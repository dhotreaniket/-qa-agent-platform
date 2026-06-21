import os
from agents.story_agent import get_structured_story
from agents.test_case_agent import generate_test_cases

def run_pipeline(raw_requirement: str):
    # Make sure output folder exists
    os.makedirs("output", exist_ok=True)

    print("=== Agent 1: Generating Structured User Story ===\n")
    story = get_structured_story(raw_requirement)
    print(story)

    with open("output/user_story.md", "w", encoding="utf-8") as f:
        f.write(story)
    print("\n[Saved to output/user_story.md]\n")

    print("\n=== Agent 2: Generating Test Cases ===\n")
    test_cases = generate_test_cases(story)
    print(test_cases)

    with open("output/test_cases.md", "w", encoding="utf-8") as f:
        f.write(test_cases)
    print("\n[Saved to output/test_cases.md]\n")

    return story, test_cases

if __name__ == "__main__":
    raw_requirement = """
    Users should be able to log into the web application using their email and password.
    If credentials are wrong, show an error. After 5 failed attempts, lock the account for 15 minutes.
    """
    run_pipeline(raw_requirement)