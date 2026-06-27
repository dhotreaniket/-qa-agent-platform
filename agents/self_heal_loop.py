from agents.auto_heal_agent import heal_failure, parse_diagnosis_and_fix
from agents.code_patcher import patch_test_file, backup_file, restore_backup
from agents.diagnostic_runner import run_diagnostic_test, did_test_pass


def self_heal(failure_log: str, broken_code: str, page_url: str, model_name: str,
              test_file_path: str, project_dir: str, max_attempts: int = 3) -> dict:
    """
    Full loop: diagnose -> patch -> re-run -> check -> retry if needed.
    Returns a dict with the outcome and history of attempts.
    """
    full_test_path = f"{project_dir}/{test_file_path}"
    backup_path = backup_file(full_test_path)

    attempt_history = []
    current_broken_code = broken_code
    current_failure_log = failure_log

    for attempt in range(1, max_attempts + 1):
        print(f"\n--- Self-Heal Attempt {attempt}/{max_attempts} ---")

        raw_result = heal_failure(
            current_failure_log, current_broken_code, page_url, model_name,
            test_file_path=test_file_path, project_dir=project_dir
        )

        diagnosis, fixed_code = parse_diagnosis_and_fix(raw_result)
        print(f"Diagnosis: {diagnosis}")

        if fixed_code in ("NONE", ""):
            attempt_history.append({"attempt": attempt, "diagnosis": diagnosis, "result": "no_fix_proposed"})
            break

        patched = patch_test_file(full_test_path, current_broken_code, fixed_code)
        if not patched:
            attempt_history.append({"attempt": attempt, "diagnosis": diagnosis, "result": "patch_failed_old_code_not_found"})
            break

        rerun_output = run_diagnostic_test(test_file_path, project_dir)
        passed = did_test_pass(rerun_output)

        attempt_history.append({
            "attempt": attempt,
            "diagnosis": diagnosis,
            "fixed_code": fixed_code,
            "result": "passed" if passed else "still_failing"
        })

        if passed:
            print(f"Fix succeeded on attempt {attempt}!")
            return {"success": True, "final_code": fixed_code, "history": attempt_history}

        # Prepare for next attempt: feed the NEW failure as input
        current_failure_log = rerun_output[-1500:]
        current_broken_code = fixed_code

    # If we exhausted attempts without success, roll back
    restore_backup(full_test_path)
    return {"success": False, "history": attempt_history}