import time
from google.genai.errors import ClientError


def invoke_with_retry(chain, input_dict, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = chain.invoke(input_dict)
            return normalize_content(result.content)
        except ClientError as e:
            if "RESOURCE_EXHAUSTED" in str(e) and attempt < max_retries - 1:
                wait_time = 45
                print(f"[Rate limit hit. Waiting {wait_time}s before retry {attempt + 2}/{max_retries}...]")
                time.sleep(wait_time)
            else:
                raise


def normalize_content(content):
    """Some Gemini model versions return content as a list of parts instead of a plain string."""
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, str):
                text_parts.append(item)
            elif isinstance(item, dict) and "text" in item:
                text_parts.append(item["text"])
        return "\n".join(text_parts)
    return content