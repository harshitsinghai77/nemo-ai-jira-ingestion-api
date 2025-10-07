import logging
import os
from dotenv import load_dotenv

import boto3
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.event_handler import LambdaFunctionUrlResolver
from aws_lambda_powertools.event_handler.api_gateway import Response
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext

from src.jira_models import JiraWebhookIngest, extract_relevant_fields, SqsPayload
from src.dynamodb_client import DynamoDBClient
from src.github_url_parser import extract_github_url

logger = logging.getLogger()
logger.setLevel(logging.INFO)

tracer = Tracer()
logger = Logger()
metrics = Metrics()

sqs = boto3.client("sqs")
app = LambdaFunctionUrlResolver()

load_dotenv()

@app.post("/ingest")
@tracer.capture_method
def ingest_jira_story():
    try:
        payload = app.current_event.json_body
        logger.debug(f"Payload received: {payload}")
        
        flatten_payload = extract_relevant_fields(payload)
        jira_information = JiraWebhookIngest.model_validate(flatten_payload)
        logger.info(f"Jira Info extracted: {jira_information}")

        table_name = os.getenv('DYNAMODB_TABLE_NAME')
        DynamoDBClient(table_name=table_name).put_item(jira_information)
        logger.info(f"Saved story {jira_information.jira_id} to DynamoDB")

        github_link = extract_github_url(jira_information.description)
        if github_link:
            sqs_payload = SqsPayload(
                github_link=github_link,
                jira_story=jira_information.description,
                jira_story_id=jira_information.jira_id
            )

            sqs.send_message(
                QueueUrl=os.getenv('QUEUE_URL'),
                MessageBody=sqs_payload.model_dump_json(),
                MessageGroupId="jira-tasks",
                # MessageDeduplicationId=story_id
            )
            logger.info(f"Sent message to SQS: {sqs_payload}")
        else:
            logger.warning(f"No GitHub URL found in Jira story: {jira_information.jira_id}")

        metrics.add_metric(name="StoriesProcessed", unit=MetricUnit.Count, value=1)
        return Response(
            status_code=200,
            content_type="application/json",
            body={"message": "Story ingested successfully"}
        )
    except Exception as e:
        logger.error(f"Request error occurred: {e}")
        metrics.add_metric(name="RequestFailed", unit=MetricUnit.Count, value=1)
        Response(
            status_code=200,
            content_type="application/json",
            body={"message": f"Request error occurred: {str(e)}"}
        )

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
