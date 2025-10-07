import os
import aws_cdk as cdk
from infrastructure.lambda_stack import NemoAIJiraIngestionAPILambdaStack

app = cdk.App()

NemoAIJiraIngestionAPILambdaStack(
    app,
    "NemoAIJiraIngestionAPILambdaStack",
    env=cdk.Environment(account=os.getenv("AWS_DEFAULT_ACCOUNT"), region="us-east-1"),
)

app.synth()
print("CDK app synthesized successfully")