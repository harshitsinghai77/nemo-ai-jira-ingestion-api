from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from src.task_metadata_parser import is_data_analysis_task

def extract_relevant_fields(payload: dict) -> dict:
    issue = payload.get("issue", {})
    fields = issue.get("fields", {})
    status = fields.get("status", {})
    status_category = status.get("statusCategory", {})
    issue_type = fields.get("issuetype", {})
    project = fields.get("project", {})
    assignee = fields.get("assignee") or {}
    reporter = fields.get("reporter") or {}
    changelog_items = payload.get("changelog", {}).get("items", [{}])

    return {
        "issue_id": issue.get("id"),
        "jira_id": issue.get("id"),
        "issue_key": issue.get("key"),
        "summary": fields.get("summary"),
        "description": fields.get("description"),
        "status": status.get("name"),
        "status_category": status_category.get("name"),
        "issue_type": issue_type.get("name"),
        "project_key": project.get("key"),
        "assignee_name": assignee.get("displayName"),
        "reporter_name": reporter.get("displayName"),
        "created": fields.get("created"),
        "updated": fields.get("updated"),
        "priority": fields.get("priority", {}).get("name"),
        "labels": fields.get("labels", []),
        "sprint_name": fields.get("customfield_10020", [{}])[0].get("name"),
        "timestamp": payload.get("timestamp"),
        "status_from": changelog_items[0].get("fromString"),
        "status_to": changelog_items[0].get("toString"),
        "additional_kwargs": {
            "assignee_id": assignee.get("accountId"),
            "reporter_id": reporter.get("accountId"),
        } 
    }

class JiraWebhookIngest(BaseModel):
    timestamp: int
    issue_id: str
    jira_id: str
    issue_key: str
    summary: str
    description: Optional[str]
    status: str
    status_category: str
    issue_type: str
    project_key: str
    assignee_name: Optional[str]
    reporter_name: Optional[str]
    created: Optional[str]
    updated: Optional[str]
    priority: Optional[str]
    labels: List[str]
    sprint_name: Optional[str]
    status_from: Optional[str]
    status_to: Optional[str]
    is_data_analysis_task: bool = Field(default=False)
    additional_kwargs: Dict[str, Any]

    def model_post_init(self, __context: Any) -> None:
        self.is_data_analysis_task = is_data_analysis_task(self.description)

class SqsPayload(BaseModel):
    github_link: str
    jira_story: str
    jira_story_id: str
    is_data_analysis_task: bool = False
    