from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
from agents.html_reader import get_clean_html
from agents.utils import invoke_with_retry
from agents.diagnostic_runner import run_diagnostic_test

load_dotenv()


def heal_failure(failure_log: str, broken_code: str, page_url: str, model_name: str,
                  test_file_path: str = None, project_dir: str = None) -> str:
    llm = ChatGoogleGenerativeAI(model=model_name, google_api_key=os.getenv("GOOGLE_API_KEY"))

    real_html = get_clean_html(page_url)
    real_html = real_html[:6000]

    # PASS 1: if we have access to actually re-run the test, get fresh runtime evidence
    diagnostic_output = ""
    if test_file_path and project_dir:
        try:
            diagnostic_output = run_diagnostic_test(test_file_path, project_dir)
            diagnostic_output = diagnostic_output[:3000]  # trim
        except Exception as e:
            diagnostic_output = f"[Diagnostic re-run failed: {e}]"

    prompt = ChatPromptTemplate.from_template(
        """You are a senior SDET specializing in fixing broken Playwright test automation.

        ORIGINAL failure log:
        {failure_log}

        Broken code:
        {broken_code}

        ACTUAL CURRENT live HTML of the relevant page:
        {html}

        FRESH DIAGNOSTIC RE-RUN output (this is real, current runtime evidence - trust this 
        MORE than the original failure log, since it reflects the test's actual current behavior):
        {diagnostic_output}

        First, classify the failure into ONE category:
        - LOCATOR_WRONG: element/selector doesn't exist or doesn't match real HTML
        - TIMING_RACE_CONDITION: action and assertion aren't properly sequenced - use the 
          diagnostic re-run output to confirm whether the expected end-state (e.g. URL, element) 
          is EVER reached, or never reached at all (these need different fixes)
        - ASSERTION_WRONG: expected value doesn't match reality
        - INTERACTION_METHOD_WRONG: the way the action is triggered (e.g. keyboard Enter) doesn't 
          actually work on this real app - use a different interaction method (e.g. click instead)

        Then apply the fix:
        - LOCATOR_WRONG: correct locator from real HTML.
        - TIMING_RACE_CONDITION: restructure with Promise.all() wrapping action + wait together.
        - ASSERTION_WRONG: correct expected value to match real HTML/content.
        - INTERACTION_METHOD_WRONG: replace the triggering interaction with one confirmed to work 
          (e.g., if diagnostic shows Enter never changes the URL, use a button click instead).

        If HTML/diagnostic data is insufficient, respond:
        ===DIAGNOSIS===
        INSUFFICIENT_DATA
        ===FIXED_CODE===
        NONE

        Respond in this exact format:

        ===DIAGNOSIS===
        Category: <category>
        Reason: <one sentence, cite specific evidence from HTML or diagnostic output>

        ===FIXED_CODE===
        <corrected, properly restructured code>
        """
    )

    chain = prompt | llm
    return invoke_with_retry(chain, {
        "failure_log": failure_log,
        "broken_code": broken_code,
        "html": real_html,
        "diagnostic_output": diagnostic_output or "[No diagnostic re-run available]"
    })


import re


def parse_diagnosis_and_fix(raw_output: str) -> tuple[str, str]:
    diagnosis_match = re.search(r"===DIAGNOSIS===(.*?)===FIXED_CODE===", raw_output, re.DOTALL)
    fix_match = re.search(r"===FIXED_CODE===(.*)", raw_output, re.DOTALL)

    diagnosis = diagnosis_match.group(1).strip() if diagnosis_match else "UNKNOWN"
    fixed_code = fix_match.group(1).strip() if fix_match else "NONE"

    fixed_code = re.sub(r"^```(?:javascript|js)?\n|```$", "", fixed_code, flags=re.MULTILINE).strip()

    return diagnosis, fixed_code