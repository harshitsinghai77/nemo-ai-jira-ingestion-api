import re

def remove_html_formatting(jira_story: str) -> str: 
    "Clean Jira formatting like bold, italic, and HTML-like tags from the input text."
    if not jira_story:
        return ""

    # Remove markdown and HTML-like formatting
    cleaned = re.sub(r"[*_`~]+", "", jira_story)
    cleaned = re.sub(r"<[^>]+>", "", cleaned)
    return cleaned.strip()

def extract_github_url(jira_story: str) -> str:
    "Extract the first GitHub URL found in the Jira story."
    if not jira_story:
        return None

    cleaned_text = remove_html_formatting(jira_story)
    pattern = r"https?://(?:www\.)?github\.com/[^\s|)\]\"'<]+"
    matches = re.findall(pattern, cleaned_text)

    if matches:
        return matches[0]

def is_long_running_task(jira_story: str) -> bool:
    """Looks for 'Long Running Task: True' in the Jira story."""
    if not jira_story:
        return False
        
    # Look for "Long Running Task: True" pattern (case insensitive)
    cleaned_text = remove_html_formatting(jira_story)
    pattern = r"Long\s+Running\s+Task\s*:\s*(True|False)"
    match = re.search(pattern, cleaned_text, re.IGNORECASE)
    
    if match and match.group(1).lower() == "true":
        return True
        
    return False

def is_data_analysis_task(jira_story: str) -> bool:
    """Looks for 'Data Analysis Task: True' in the Jira story."""
    if not jira_story:
        return False
        
    # Look for "Data Analysis Task: True" pattern (case insensitive)
    cleaned_text = remove_html_formatting(jira_story)
    pattern = r"Data\s+Analysis\s+Task\s*:\s*(True|False)"
    match = re.search(pattern, cleaned_text, re.IGNORECASE)
    
    if match and match.group(1).lower() == "true":
        return True
        
    return False