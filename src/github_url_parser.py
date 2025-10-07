import re

def extract_github_url(jira_story: str) -> str:

    if not jira_story:
        return None

    pattern = r"https?://(?:www\.)?github\.com/[^\s|)\]\"'<]+"
    matches = re.findall(pattern, jira_story)

    if matches:
        return matches[0]

def extract_long_running_task(jira_story: str) -> bool:
    if not jira_story:
        return False
        
    # Look for "Long Running Task: True" pattern (case insensitive)
    pattern = r"Long\s+Running\s+Task\s*:\s*(True|False)"
    match = re.search(pattern, jira_story, re.IGNORECASE)
    
    if match and match.group(1).lower() == "true":
        return True
        
    return False