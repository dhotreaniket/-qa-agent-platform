import time
import os
from google.genai.errors import ClientError, ServerError


def invoke_with_retry(chain, input_dict, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = chain.invoke(input_dict)
            return normalize_content(result.content)
        except (ClientError, ServerError) as e:
            is_retryable = "RESOURCE_EXHAUSTED" in str(e) or "UNAVAILABLE" in str(e)
            if is_retryable and attempt < max_retries - 1:
                wait_time = 30
                print(f"[API issue ({type(e).__name__}). Waiting {wait_time}s before retry {attempt + 2}/{max_retries}...]")
                time.sleep(wait_time)
            else:
                raise


def normalize_content(content):
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, str):
                text_parts.append(item)
            elif isinstance(item, dict) and "text" in item:
                text_parts.append(item["text"])
        return "\n".join(text_parts)
    return content


def load_if_exists(filepath: str) -> str | None:
    """Returns file content if it exists, else None."""
    if filepath and os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    return None