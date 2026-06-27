import requests
import os
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()


def create_jira_story(story_text: str, summary: str) -> dict:
    """
    Pushes a generated user story into Jira as a new Story issue.
    Returns dict with issue key and URL.
    """
    base_url = os.getenv('JIRA_URL').rstrip('/')
    url = f"{base_url}/rest/api/2/issue"

    payload = {
        "fields": {
            "project": {"key": os.getenv("JIRA_PROJECT_KEY")},
            "summary": summary,
            "description": story_text,
            "issuetype": {"name": "Story"}
        }
    }

    response = requests.post(
        url,
        json=payload,
        auth=HTTPBasicAuth(os.getenv("JIRA_EMAIL"), os.getenv("JIRA_API_TOKEN")),
        headers={"Content-Type": "application/json"}
    )

    if response.status_code != 201:
        raise Exception(f"Jira issue creation failed: {response.status_code} - {response.text}")

    result = response.json()
    issue_key = result["key"]
    issue_url = f"{base_url}/browse/{issue_key}"

    return {"key": issue_key, "url": issue_url}


def get_jira_story(issue_key: str) -> str:
    """
    Reads an EXISTING Jira story by its key (e.g. 'AUT-5') and returns its description.
    """
    base_url = os.getenv('JIRA_URL').rstrip('/')
    url = f"{base_url}/rest/api/2/issue/{issue_key}"

    response = requests.get(
        url,
        auth=HTTPBasicAuth(os.getenv("JIRA_EMAIL"), os.getenv("JIRA_API_TOKEN")),
        headers={"Content-Type": "application/json"}
    )

    if response.status_code != 200:
        raise Exception(f"Failed to fetch Jira issue: {response.status_code} - {response.text}")

    issue = response.json()
    summary = issue["fields"]["summary"]
    description = issue["fields"].get("description", "")

    return f"Summary: {summary}\n\nDescription:\n{description}"