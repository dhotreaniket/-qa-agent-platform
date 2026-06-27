import subprocess


def run_diagnostic_test(test_file_path: str, project_dir: str) -> str:
    try:
        result = subprocess.run(
            f"npx playwright test {test_file_path} --headed --reporter=list --project=chromium",
            cwd=project_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=120,
            shell=True
        )
        return result.stdout + "\n" + result.stderr
    except subprocess.TimeoutExpired as e:
        partial_output = (e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
        return f"[TIMEOUT after 120s]\n{partial_output}"


def did_test_pass(diagnostic_output: str) -> bool:
    return "passed" in diagnostic_output and "failed" not in diagnostic_output.lower()