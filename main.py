import time
import os
from agents.config_loader import load_config
from agents.story_agent import get_structured_story
from agents.test_case_agent import generate_test_cases
from agents.framework_analyzer_agent import analyze_framework


def run_pipeline(raw_requirement: str, target_url: str, model_name: str):
    os.makedirs("output", exist_ok=True)

    print("=== Agent 1: Generating Structured User Story ===\n")
    story = get_structured_story(raw_requirement, model_name)
    with open("output/user_story.md", "w", encoding="utf-8") as f:
        f.write(story)
    print(story, "\n[Saved to output/user_story.md]\n")

    time.sleep(20)

    print("\n=== Agent 2: Generating Test Cases ===\n")
    test_cases = generate_test_cases(story, model_name)
    with open("output/test_cases.md", "w", encoding="utf-8") as f:
        f.write(test_cases)
    print(test_cases, "\n[Saved to output/test_cases.md]\n")

    time.sleep(20)

    print("\n=== Agent 3: Analyzing Automation Framework Strategy ===\n")
    framework_plan = analyze_framework(test_cases[:1500], target_url, model_name)
    with open("output/framework_plan.md", "w", encoding="utf-8") as f:
        f.write(framework_plan)
    print(framework_plan, "\n[Saved to output/framework_plan.md]\n")

    return story, test_cases, framework_plan


if __name__ == "__main__":
    config = load_config()

    raw_requirement = f"""
    Users should be able to log into the application at {config['target_url']} 
    using a username and password.
    """

    run_pipeline(raw_requirement, config["target_url"], config["gemini_model"])