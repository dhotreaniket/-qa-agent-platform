RUNNER_CONFIGS = {
    "web": {
        "runner_dir": "playwright-runner",
        "pages_subdir": "pages",
        "tests_subdir": "tests",
        "page_object_filename": "LoginPage.js",
        "test_filename": "login.spec.js",
        "run_command": "npx playwright test {test_file} --headed --reporter=list",
        "language": "JavaScript",
        "framework": "Playwright"
    },
    # Future: "api", "mobile", "performance" — same shape, different values
}


def get_runner_config(automation_type: str) -> dict:
    if automation_type not in RUNNER_CONFIGS:
        supported = list(RUNNER_CONFIGS.keys())
        raise ValueError(f"automation_type '{automation_type}' not yet supported. Supported: {supported}")
    return RUNNER_CONFIGS[automation_type]