import json

from src.constants.constants import MESSAGE


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    # Example processing
    # Return a response
    return {
        "statusCode": 200,
        "body": json.dumps({
        "message": MESSAGE
    })
}