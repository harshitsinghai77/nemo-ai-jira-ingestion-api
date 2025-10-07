import boto3
from typing import Dict, Any, Union
from pydantic import BaseModel
from boto3.dynamodb.conditions import Key

class DynamoDBClient:
    def __init__(self, table_name: str = None, region: str = "us-east-1"):
        self.table_name = table_name
        if not self.table_name:
            raise ValueError("DynamoDB table name must be provided.")
        self.resource = boto3.resource("dynamodb", region_name=region)
        self.table = self.resource.Table(self.table_name)

    def put_item(self, item: Union[BaseModel, Dict[str, Any]]) -> Dict[str, Any]:
        """Put a new item into the table."""
        if isinstance(item, BaseModel):
            item = item.model_dump()

        response = self.table.put_item(Item=item)
        return response

    def get_item(self, key: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve a single item based on primary key."""
        response = self.table.get_item(Key=key)
        return response.get("Item", {})

    def query_items(self, partition_key: str, value: Any) -> list:
        """Query by partition key only."""
        response = self.table.query(
            KeyConditionExpression=Key(partition_key).eq(value)
        )
        return response.get("Items", [])

    def delete_item(self, key: Dict[str, Any]) -> Dict[str, Any]:
        """Delete an item by key."""
        return self.table.delete_item(Key=key)
