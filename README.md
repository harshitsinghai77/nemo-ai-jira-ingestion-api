# Nemo AI Jira Ingestion API

A serverless AWS Lambda application that processes Jira webhook events and routes tasks to processing workflows based on task type mentioned in the Jira Story.

## Architecture Overview

The application receives Jira webhook events, extracts GitHub URLs from task descriptions, and routes tasks to either SQS queues for standard processing or ECS Fargate tasks for long-running operations.

```
Jira Webhook → Lambda Function → DynamoDB Storage
                     ↓
              Task Classification
                     ↓
        ┌─────────────────────────┐
        ↓                         ↓
   SQS Queue                ECS Fargate
(Standard Tasks)         (Long Running Tasks)
        ↓
Core Lambda Engine
(Consumes from SQS)
```

## Directory Structure

```
├── .github/workflows/          # GitHub Actions CI/CD
│   └── deploy.yml             # Automated deployment pipeline
├── infrastructure/            # AWS CDK infrastructure code
│   └── lambda_stack.py       # Lambda, DynamoDB, SQS stack definition
├── src/                      # Application source code
│   ├── dynamodb_client.py    # DynamoDB operations
│   ├── ecs_client.py         # ECS Fargate task invocation
│   ├── jira_models.py        # Pydantic models for Jira data
│   ├── send_sqs_message.py   # SQS message handling
│   └── task_metadata_parser.py # Task classification logic
├── cdk_app.py               # CDK application entry point
├── main.py                  # Lambda function handler
└── requirements.txt         # Python dependencies
```

## Key Features

### Intelligent Task Routing
- **Standard Tasks**: Routed to SQS queue, consumed by core Lambda engine for batch processing
- **Long Running Tasks**: Executed on ECS Fargate for long-running processing
- **Data Analysis Tasks**: Different handling for analytics workloads

### Task Classification
The system automatically classifies tasks based on description content:
- Extracts GitHub URLs from Jira descriptions
- Identifies long-running tasks via `Long Running Task: True` flag
- Detects data analysis tasks via `Data Analysis Task: True` flag

### AWS Services Integration
- **Lambda**: Serverless webhook processing with Function URLs
- **DynamoDB**: Persistent storage for Jira events
- **SQS**: Message queuing for standard task processing
- **ECS Fargate**: Container execution for complex tasks
- **CloudWatch**: Comprehensive logging and metrics

### Observability
- AWS Lambda Powertools integration
- Structured JSON logging
- X-Ray distributed tracing
- Custom CloudWatch metrics
- Error handling and monitoring

## Infrastructure (CDK)

The infrastructure is defined using AWS CDK in Python:

- **Lambda Function**: Python 3.13 runtime with 128MB memory
- **DynamoDB Table**: `JiraWebhookEvents` for event storage
- **SQS Queue**: FIFO queue `nemo-ai-tasks.fifo` for task processing
- **IAM Roles**: Least-privilege permissions for AWS service access
- **Function URL**: Direct HTTP access without API Gateway

## GitHub Actions CI/CD

Automated deployment pipeline triggered on main branch pushes:

1. **Environment Setup**: Python 3.13 + Node.js 22 + AWS CDK
2. **Dependency Installation**: Python packages and CDK CLI
3. **Lambda Packaging**: Creates deployment zip with dependencies
4. **AWS Deployment**: Deploys infrastructure using CDK

## API Endpoints

### POST /ingest
Processes Jira webhook events and routes tasks appropriately.

**Request**: Jira webhook payload
**Response**: Success/error status with processing details

### GET /hello
Health check endpoint for monitoring.

## Environment Variables

- `DYNAMODB_TABLE_NAME`: DynamoDB table for event storage
- `QUEUE_URL`: SQS queue URL for standard tasks
- `POWERTOOLS_*`: AWS Lambda Powertools configuration

## Dependencies

- **aws-lambda-powertools**: Observability and utilities
- **pydantic**: Data validation and serialization
- **boto3**: AWS SDK (included in Lambda runtime)
- **python-dotenv**: Environment variable management

## Deployment

1. Configure AWS credentials
2. Set `AWS_DEFAULT_ACCOUNT` environment variable
3. Deploy using CDK: `cdk deploy`

Or use GitHub Actions by pushing to main branch.

## Error Handling

- Custom `ECSTaskError` for Fargate task failures
- Graceful degradation for missing GitHub URLs
- Comprehensive error logging and metrics
- HTTP 200 responses with error details for webhook compatibility