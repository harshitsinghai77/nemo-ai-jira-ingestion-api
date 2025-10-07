import logging
import os
from dotenv import load_dotenv
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.event_handler import LambdaFunctionUrlResolver
from aws_lambda_powertools.event_handler.api_gateway import Response
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import ValidationError

from src.jira_models import JiraWebhookIngest, extract_relevant_fields
from src.dynamodb_client import DynamoDBClient

logger = logging.getLogger()
logger.setLevel(logging.INFO)

tracer = Tracer()
logger = Logger()
metrics = Metrics()
app = LambdaFunctionUrlResolver()

load_dotenv()

@app.post("/ingest")
@tracer.capture_method
def ingest_jira_story():
    try:
        payload = app.current_event.json_body
        logger.info(f"Payload received: {payload}")
        
        flatten_payload = extract_relevant_fields(payload)
        story = JiraWebhookIngest.model_validate(flatten_payload)
        resp = DynamoDBClient(table_name=os.getenv('DYNAMODB_TABLE_NAME')).put_item(story)
        logger.info(f"Dynamodb resp: {resp}")

        logger.info("StoriesProcessed")
        metrics.add_metric(name="StoriesProcessed", unit=MetricUnit.Count, value=1)
        return Response(
            status_code=200,
            content_type="application/json",
            body={"message": "Story ingested successfully"}
        )
    except ValidationError:
        metrics.add_metric(name="ValidationFailed", unit=MetricUnit.Count, value=1)
        raise
    except Exception as e:
        logger.error(f"Request error occurred: {e}")
        metrics.add_metric(name="RequestFailed", unit=MetricUnit.Count, value=1)
        raise

@app.get('/hello')
def hello():
    return Response(
        status_code=200,
        content_type="application/json",
        body={"message": "Hello, World!"}
    )

@logger.inject_lambda_context(correlation_id_path=correlation_paths.LAMBDA_FUNCTION_URL)
@tracer.capture_lambda_handler
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
