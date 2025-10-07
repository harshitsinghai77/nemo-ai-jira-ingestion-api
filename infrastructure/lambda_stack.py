from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_dynamodb as _dynamodb,
    aws_sqs as _sqs,
    aws_iam as iam,
    CfnOutput,
)

from constructs import Construct

class NemoAIJiraIngestionAPILambdaStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        table = _dynamodb.Table.from_table_name(self, "ImportedTable", "JiraWebhookEvents")
        queue = _sqs.Queue.from_queue_arn(
            self,
            "NemoAIQueue",
            "arn:aws:sqs:us-east-1:976193265367:nemo-ai-tasks.fifo" 
        )

        base_lambda = _lambda.Function(
            self,
            "NemoAIJiraIngestionAPILambdaFunction",
            runtime=_lambda.Runtime.PYTHON_3_13,
            handler="main.lambda_handler",
            #code=aws_lambda.Code.from_asset("src")
            code = _lambda.Code.from_asset("lambda_function.zip"),
            memory_size=128,
            timeout=Duration.seconds(60),
            tracing=_lambda.Tracing.ACTIVE,
            environment={
                "DYNAMODB_TABLE_NAME": table.table_name,
                "POWERTOOLS_METRICS_NAMESPACE": "JiraIngestor",
                "POWERTOOLS_METRICS_FUNCTION_NAME": "jira-ingestor",
                "POWERTOOLS_SERVICE_NAME": "jira_ingestor",
                "QUEUE_URL": "https://sqs.us-east-1.amazonaws.com/976193265367/nemo-ai-tasks.fifo"
            },
        )

        table.grant_read_write_data(base_lambda)
        queue.grant_send_messages(base_lambda)

        base_lambda.add_to_role_policy(iam.PolicyStatement(
            actions=["cloudwatch:PutMetricData", "logs:CreateLogStream", "logs:PutLogEvents", "xray:PutTraceSegments", "xray:PutTelemetryRecords"],
            resources=["*"]
        ))

        function_url = base_lambda.add_function_url(
            auth_type=_lambda.FunctionUrlAuthType.NONE,
            cors=_lambda.FunctionUrlCorsOptions(
                allowed_origins=["*"],
                allowed_methods=[_lambda.HttpMethod.GET, _lambda.HttpMethod.POST],
                allowed_headers=["*"],
            )
        )

        CfnOutput(self, "LambdaFunctionUrl", value=function_url.url)

        # endpoint = aws_apigateway.LambdaRestApi(
        #     self,
        #     "ApiGwEndpoint",
        #     handler=fn,
        #     rest_api_name="HelloApi"
        # )