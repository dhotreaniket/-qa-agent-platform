from agents.jira_agent import create_jira_story

result = create_jira_story(
    story_text="As a user, I want to log in with valid credentials so that I can access the application.",
    summary="Test Story - PythiAiAgent Integration"
)

print("Created issue:", result)