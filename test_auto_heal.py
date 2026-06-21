from agents.auto_heal_agent import heal_failure
from agents.config_loader import load_config

config = load_config()

failure_log = """
Error: expect(page).toHaveURL(expected) failed
Expected pattern: /.*\\/logged-in-successfully\\//
Received string:  "https://practicetestautomation.com/practice-test-login/"

Test: TC_003 | Verify keyboard navigation and submission on login form
"""

broken_code = """
const successHeader = page.locator('h1.post-title');
await expect(successHeader).toBeVisible();
await expect(successHeader).toHaveText('Logged In Successfully');
"""

result = heal_failure(failure_log, broken_code, "https://practicetestautomation.com/logged-in-successfully/", config["gemini_model"])
print(result)