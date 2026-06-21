from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
from agents.html_reader import get_clean_html
from agents.utils import invoke_with_retry

load_dotenv()


def heal_failure(failure_log: str, broken_code: str, page_url: str, model_name: str) -> str:
    llm = ChatGoogleGenerativeAI(model=model_name, google_api_key=os.getenv("GOOGLE_API_KEY"))

    real_html = get_clean_html(page_url)
    real_html = real_html[:6000]

    print("=== DEBUG: FULL HTML BEING SENT ===")
    print(real_html)
    print("=== END FULL HTML DEBUG ===\n")

    prompt = ChatPromptTemplate.from_template(
        """You are a senior SDET specializing in fixing broken Playwright test automation.

        A test failed with this error log:
        {failure_log}

        Here is the relevant broken code (a locator or assertion is likely wrong):
        {broken_code}

        Here is the ACTUAL CURRENT live HTML of the page where this failure occurred:
        {html}

        IMPORTANT: If the HTML above does not contain enough information to diagnose this 
        specific failure (e.g., it's an error page, empty, or unrelated content), respond with:
        ===DIAGNOSIS===
        INSUFFICIENT_HTML: Cannot diagnose - the fetched HTML does not contain relevant content.
        ===FIXED_CODE===
        NONE

        Otherwise, your job:
        1. Identify exactly what locator or assertion is incorrect, based on the REAL HTML above.
        2. Propose the corrected line(s) of code, using ONLY elements that genuinely exist in the HTML above.
        3. Briefly explain WHY the original was wrong, citing the specific HTML element you found.

        Respond in this exact format:

        ===DIAGNOSIS===
        (one sentence, must reference a specific real element/attribute from the HTML above)

        ===FIXED_CODE===
        (the corrected line(s) of code only, no extra commentary)
        """
    )

    chain = prompt | llm
    return invoke_with_retry(chain, {
        "failure_log": failure_log,
        "broken_code": broken_code,
        "html": real_html
    })