import time
import os
from agents.config_loader import load_config
from agents.story_agent import get_structured_story
from agents.test_case_agent import generate_test_cases
from agents.framework_analyzer_agent import analyze_framework
from agents.code_generator_agent import generate_automation_code
from agents.utils import load_if_exists


def run_pipeline(raw_requirement: str, target_url: str, model_name: str, force_rerun: bool = False):
    os.makedirs("output", exist_ok=True)
    os.makedirs("output/pages", exist_ok=True)
    os.makedirs("output/tests", exist_ok=True)

    # --- Agent 1 ---
    story = None if force_rerun else load_if_exists("output/user_story.md")
    if story:
        print("=== Agent 1: Skipped (using cached output/user_story.md) ===\n")
    else:
        print("=== Agent 1: Generating Structured User Story ===\n")
        story = get_structured_story(raw_requirement, model_name)
        with open("output/user_story.md", "w", encoding="utf-8") as f:
            f.write(story)
        print(story, "\n[Saved to output/user_story.md]\n")
        time.sleep(20)

    # --- Agent 2 ---
    test_cases = None if force_rerun else load_if_exists("output/test_cases.md")
    if test_cases:
        print("=== Agent 2: Skipped (using cached output/test_cases.md) ===\n")
    else:
        print("\n=== Agent 2: Generating Test Cases ===\n")
        test_cases = generate_test_cases(story, model_name)
        with open("output/test_cases.md", "w", encoding="utf-8") as f:
            f.write(test_cases)
        print(test_cases, "\n[Saved to output/test_cases.md]\n")
        time.sleep(20)

    # --- Agent 3 ---
    framework_plan = None if force_rerun else load_if_exists("output/framework_plan.md")
    if framework_plan:
        print("=== Agent 3: Skipped (using cached output/framework_plan.md) ===\n")
    else:
        print("\n=== Agent 3: Analyzing Automation Framework Strategy ===\n")
        framework_plan = analyze_framework(test_cases[:1500], target_url, model_name)
        with open("output/framework_plan.md", "w", encoding="utf-8") as f:
            f.write(framework_plan)
        print(framework_plan, "\n[Saved to output/framework_plan.md]\n")
        time.sleep(20)

    # --- Agent 4 ---
    existing_page = None if force_rerun else load_if_exists("output/pages/LoginPage.js")
    existing_test = None if force_rerun else load_if_exists("output/tests/login.spec.js")
    if existing_page and existing_test:
        print("=== Agent 4: Skipped (using cached LoginPage.js / login.spec.js) ===\n")
        code_files = {"page_object": existing_page, "test_file": existing_test}
    else:
        print("\n=== Agent 4: Generating Automation Code ===\n")
        code_files = generate_automation_code(framework_plan, test_cases, target_url, model_name)
        with open("output/pages/LoginPage.js", "w", encoding="utf-8") as f:
            f.write(code_files["page_object"])
        with open("output/tests/login.spec.js", "w", encoding="utf-8") as f:
            f.write(code_files["test_file"])
        print("[Saved Agent 4 outputs]\n")

    return story, test_cases, framework_plan, code_files


if __name__ == "__main__":
    config = load_config()

    raw_requirement = f"""
    Users should be able to log into the application at {config['target_url']} 
    using a username and password.
    """

    # Set force_rerun=True if you want to regenerate everything from scratch
    run_pipeline(raw_requirement, config["target_url"], config["gemini_model"], force_rerun=False)