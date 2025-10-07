from aws_cdk import Stack, aws_apigateway, aws_lambda, Duration, CfnOutput

from constructs import Construct

class NemoAIJiraIngestionAPILambdaStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        base_lambda = aws_lambda.Function(
            self,
            "NemoAIJiraIngestionAPILambdaFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_13,
            handler="main.lambda_handler",
            #code=aws_lambda.Code.from_asset("src")
            code = aws_lambda.Code.from_asset("lambda_function.zip"),
            memory_size=256,
            timeout=Duration.seconds(90)
        )

        function_url = base_lambda.add_function_url(
            auth_type=aws_lambda.FunctionUrlAuthType.NONE
        )

        CfnOutput(self, "LambdaFunctionUrl", value=function_url.url)

        # endpoint = aws_apigateway.LambdaRestApi(
        #     self,
        #     "ApiGwEndpoint",
        #     handler=fn,
        #     rest_api_name="HelloApi"
        # )