import time
import os
import shutil
from agents.config_loader import load_config
from agents.story_agent import get_structured_story
from agents.test_case_agent import generate_test_cases
from agents.framework_analyzer_agent import analyze_framework
from agents.code_generator_agent import generate_automation_code
from agents.runner_config import get_runner_config
from agents.diagnostic_runner import run_diagnostic_test, did_test_pass
from agents.utils import load_if_exists


def run_pipeline(raw_requirement: str, target_url: str, model_name: str,
                  automation_type: str = "web", force_rerun: bool = False):
    runner = get_runner_config(automation_type)
    os.makedirs("output", exist_ok=True)

    # --- Agent 1 ---
    story = None if force_rerun else load_if_exists("output/user_story.md")
    if story:
        print("=== Agent 1: Skipped (cached) ===")
    else:
        print("=== Agent 1: Generating User Story ===")
        story = get_structured_story(raw_requirement, model_name)
        with open("output/user_story.md", "w", encoding="utf-8") as f:
            f.write(story)
        time.sleep(15)

    # --- Agent 2 ---
    test_cases = None if force_rerun else load_if_exists("output/test_cases.md")
    if test_cases:
        print("=== Agent 2: Skipped (cached) ===")
    else:
        print("=== Agent 2: Generating Test Cases ===")
        test_cases = generate_test_cases(story, model_name)
        with open("output/test_cases.md", "w", encoding="utf-8") as f:
            f.write(test_cases)
        time.sleep(15)

    # --- Agent 3 ---
    framework_plan = None if force_rerun else load_if_exists("output/framework_plan.md")
    if framework_plan:
        print("=== Agent 3: Skipped (cached) ===")
    else:
        print(f"=== Agent 3: Analyzing {runner['framework']} Strategy ===")
        framework_plan = analyze_framework(
            test_cases[:1500], target_url, model_name,
            framework=runner["framework"], language=runner["language"]
        )
        with open("output/framework_plan.md", "w", encoding="utf-8") as f:
            f.write(framework_plan)
        time.sleep(15)

    # --- Agent 4: write DIRECTLY into the runner project, no manual copy ---
    runner_dir = runner["runner_dir"]
    pages_dir = os.path.join(runner_dir, runner["pages_subdir"]) if runner["pages_subdir"] else None
    tests_dir = os.path.join(runner_dir, runner["tests_subdir"])

    if pages_dir:
        os.makedirs(pages_dir, exist_ok=True)
    os.makedirs(tests_dir, exist_ok=True)

    test_file_full_path = os.path.join(tests_dir, runner["test_filename"])
    page_file_full_path = os.path.join(pages_dir, runner["page_object_filename"]) if pages_dir else None

    existing_test = None if force_rerun else load_if_exists(test_file_full_path)
    if existing_test:
        print("=== Agent 4: Skipped (code already exists in runner project) ===")
        code_files = {"test_file": existing_test,
                      "page_object": load_if_exists(page_file_full_path) if page_file_full_path else ""}
    else:
        print(f"=== Agent 4: Generating {runner['framework']} Code ===")
        code_files = generate_automation_code(
            framework_plan, test_cases, target_url, model_name,
            framework=runner["framework"], language=runner["language"]
        )
        if page_file_full_path:
            with open(page_file_full_path, "w", encoding="utf-8") as f:
                f.write(code_files["page_object"])
            print(f"[Written directly to {page_file_full_path}]")

        with open(test_file_full_path, "w", encoding="utf-8") as f:
            f.write(code_files["test_file"])
        print(f"[Written directly to {test_file_full_path}]")

    # --- Agent 5 (basic, inline for now): auto-execute ---
    print(f"=== Agent 5: Executing {runner['framework']} Tests ===")
    relative_test_path = f"{runner['tests_subdir']}/{runner['test_filename']}"
    test_output = run_diagnostic_test(relative_test_path, runner_dir)
    passed = did_test_pass(test_output)

    print(test_output[-2000:])  # show tail of output
    print(f"\n=== RESULT: {'PASSED' if passed else 'FAILED'} ===")

    with open("output/execution_report.txt", "w", encoding="utf-8") as f:
        f.write(test_output)

    return {
        "story": story, "test_cases": test_cases, "framework_plan": framework_plan,
        "code_files": code_files, "execution_passed": passed, "execution_output": test_output
    }


if __name__ == "__main__":
    config = load_config()

    raw_requirement = f"""
    Users should be able to log into the application at {config['target_url']} 
    using a username and password.
    """

    result = run_pipeline(
        raw_requirement,
        config["target_url"],
        config["gemini_model"],
        automation_type=config.get("automation_type", "web"),
        force_rerun=False
    )