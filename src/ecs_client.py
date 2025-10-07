import logging
import boto3

from src.jira_models import JiraWebhookIngest

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ecs = boto3.client("ecs")

class ECSTaskError(Exception):
    """Custom exception for ECS task invocation errors"""
    def __init__(self, message, details=None):
        self.message = message
        self.details = details
        super().__init__(f'{self.message} - {self.details}')

def invoke_ecs_fargate_task(jira_information: JiraWebhookIngest, github_link: str):
    """Invoke ECS Fargate task for long running operations"""
    try:
        cluster_name = 'NemoAIECSFargateStack-NemoAIECSCluster1F1DBE26-qAE5J3iQY5BA'
        task_definition = 'NemoAIECSFargateStackNemoAIECSTaskDefinitionF86D8E2D'
        # subnet_id = 'subnet-0da0c795e10622438'
        
        container_overrides = [{
            'name': 'NemoAIECSContainer', 
            'environment': [
                {'name': 'GITHUB_LINK', 'value': github_link},
                {'name': 'JIRA_STORY', 'value': jira_information.description},
                {'name': 'JIRA_STORY_ID', 'value': jira_information.jira_id},
                {'name': 'TASK_TYPE', 'value': 'long_running_task'}
            ]
        }]
        
        response = ecs.run_task(
            cluster=cluster_name,
            taskDefinition=task_definition,
            launchType='FARGATE',
            networkConfiguration={
                'awsvpcConfiguration': {
                    'subnets': ['subnet-0b9056109302ba49a'],
                    'assignPublicIp': 'DISABLED'
                }
            },
            overrides={
                'containerOverrides': container_overrides
            },
            tags=[
                {'key': 'JiraStoryId', 'value': jira_information.jira_id},
                {'key': 'TaskType', 'value': 'long_running_task'}
            ]
        )
        
        logger.info(f"ECS Fargate task started successfully.")
        return response
        
    except Exception as e:
        logger.error(f"Failed to start ECS Fargate task: {e}")
        raise ECSTaskError(f"Failed to start ECS Fargate task", str(e))
