import os

import boto3
from aws_lambda_powertools.logging import Logger

from src.jira_models import SqsPayload
from src.jira_models import JiraWebhookIngest

logger = Logger(service="jira_ingestor", level="INFO", json_formatter=True)
sqs = boto3.client('sqs')

def send_sqs_message(jira_information: JiraWebhookIngest, github_link: str) -> dict:
    """
    Sends a message to the SQS queue with the given payload.

    Returns:
        dict: The response from the SQS send_message API call.
    """
    queue_url = os.getenv("QUEUE_URL")
    if not queue_url:
        raise ValueError("QUEUE_URL is not set in environment variables")

    payload = SqsPayload(
        github_link=github_link,
        jira_story=jira_information.description,
        jira_story_id=jira_information.jira_id,
        is_data_analysis_task=jira_information.is_data_analysis_task
    )
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=payload.model_dump_json(),
        MessageGroupId=jira_information.jira_id,
        MessageDeduplicationId=payload.jira_story_id
    )

    return response
