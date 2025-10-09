import os
from dotenv import load_dotenv

from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.event_handler import LambdaFunctionUrlResolver
from aws_lambda_powertools.event_handler.api_gateway import Response
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.logging import Logger

from src.jira_models import JiraWebhookIngest, extract_relevant_fields
from src.dynamodb_client import DynamoDBClient
from src.task_metadata_parser import extract_github_url, is_long_running_task
from src.ecs_client import invoke_ecs_fargate_task, ECSTaskError
from src.send_sqs_message import send_sqs_message

tracer = Tracer()
logger = Logger(service="jira_ingestor", level="INFO", json_formatter=True)
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
        jira_information = JiraWebhookIngest.model_validate(flatten_payload)
        logger.info(f"Jira Info extracted: {jira_information}")

        table_name = os.getenv('DYNAMODB_TABLE_NAME')
        DynamoDBClient(table_name=table_name).put_item(jira_information)
        logger.info(f"Saved story {jira_information.jira_id} to DynamoDB")

        github_link = extract_github_url(jira_information.description)

        if not github_link:
            logger.warning(f"No GitHub URL found in Jira story: {jira_information.jira_id}")
            metrics.add_metric(name="StoriesProcessed", unit=MetricUnit.Count, value=1)
            return Response(
                status_code=200,
                content_type="application/json",
                body={"message": "Story ingested successfully but no GitHub URL found"}
            )

        if is_long_running_task(jira_information.description):
            logger.info(f"Long running task detected for story {jira_information.jira_id}")
            ecs_response = invoke_ecs_fargate_task(jira_information, github_link)
            logger.info(f"ECS task started successfully: {ecs_response}")
            metrics.add_metric(name="ECSTasksStarted", unit=MetricUnit.Count, value=1)
        else:
            logger.info(f"Sending message to SQS...")
            sqs_response = send_sqs_message(jira_information, github_link)
            logger.info(f"Sent message to SQS: {sqs_response}")
            metrics.add_metric(name="SQSMessagesSent", unit=MetricUnit.Count, value=1)

        metrics.add_metric(name="StoriesProcessed", unit=MetricUnit.Count, value=1)
        return Response(
            status_code=200,
            content_type="application/json",
            body={"message": "Story ingested successfully"}
        )
    except ECSTaskError as ecs_error:
        logger.error(f"ECS task error occurred: {ecs_error.message} - {ecs_error.details}", exc_info=True)
        metrics.add_metric(name="ECSTaskErrors", unit=MetricUnit.Count, value=1)
        return Response(
            status_code=500,
            content_type="application/json",
            body={"message": f"ECS task error occurred: {ecs_error.message}"}
        )
    except Exception as e:
        logger.error(f"Request error occurred: {e}", exc_info=True)
        metrics.add_metric(name="RequestFailed", unit=MetricUnit.Count, value=1)
        return Response(
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
