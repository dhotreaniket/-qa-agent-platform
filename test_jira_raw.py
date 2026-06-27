import requests
import os
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()

url = f"{os.getenv('JIRA_URL')}/rest/api/2/issue"

payload = {
    "fields": {
        "project": {"key": os.getenv("JIRA_PROJECT_KEY")},
        "summary": "Test Story - Raw API Call",
        "description": "Testing direct REST API call, bypassing the jira Python library.",
        "issuetype": {"name": "Story"}
    }
}

response = requests.post(
    url,
    json=payload,
    auth=HTTPBasicAuth(os.getenv("JIRA_EMAIL"), os.getenv("JIRA_API_TOKEN")),
    headers={"Content-Type": "application/json"}
)

print("Status code:", response.status_code)
print("Response:", response.text)