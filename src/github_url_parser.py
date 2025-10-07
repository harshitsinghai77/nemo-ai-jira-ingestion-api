import re

def extract_github_url(jira_story: str) -> str:

    if not jira_story:
        return None

    pattern = r"https?://(?:www\.)?github\.com/[^\s|)\]\"'<]+"
    matches = re.findall(pattern, jira_story)

    if matches:
        return matches[0]
