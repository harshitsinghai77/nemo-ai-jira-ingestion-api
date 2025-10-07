from aws_cdk import Stack, aws_apigateway, aws_lambda, Duration

from constructs import Construct

class NemoAIJiraIngestionAPILambdaStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        fn = aws_lambda.Function(
            self,
            "NemoAIJiraIngestionAPILambdaFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_13,
            handler="app.lambda_handler",
            #code=aws_lambda.Code.from_asset("src")
            code = aws_lambda.Code.from_asset("lambda_function.zip"),
            memory_size=256,
            timeout=Duration.seconds(180)
        )

        # endpoint = aws_apigateway.LambdaRestApi(
        #     self,
        #     "ApiGwEndpoint",
        #     handler=fn,
        #     rest_api_name="HelloApi"
        # )