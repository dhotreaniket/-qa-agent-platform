import re


def patch_test_file(file_path: str, old_code: str, new_code: str) -> bool:
    """
    Replaces old_code with new_code inside the given file.
    Returns True if the replacement was made, False if old_code wasn't found.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Normalize whitespace for matching (LLM output formatting can differ slightly)
    if old_code.strip() not in content:
        return False

    new_content = content.replace(old_code.strip(), new_code.strip())

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    return True


def backup_file(file_path: str) -> str:
    """Creates a .bak copy before patching, so we can roll back if needed."""
    backup_path = file_path + ".bak"
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    with open(backup_path, "w", encoding="utf-8") as f:
        f.write(content)
    return backup_path


def restore_backup(file_path: str):
    """Rolls back to the backup if a fix attempt failed."""
    backup_path = file_path + ".bak"
    with open(backup_path, "r", encoding="utf-8") as f:
        content = f.read()
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)