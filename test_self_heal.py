from agents.self_heal_loop import self_heal
from agents.config_loader import load_config

config = load_config()

failure_log = """
Error: expect(page).toHaveURL(expected) failed
Expected pattern: /.*\\/logged-in-successfully\\//
Received string:  "https://practicetestautomation.com/practice-test-login/"
Test: TC_003
"""

broken_code = """await page.keyboard.press('Enter');"""

result = self_heal(
    failure_log, broken_code,
    "https://practicetestautomation.com/practice-test-login/",
    config["gemini_model"],
    test_file_path="tests/login.spec.js",
    project_dir="playwright-runner",
    max_attempts=3
)

print("\n=== FINAL RESULT ===")
print(result)