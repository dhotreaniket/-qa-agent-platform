from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
import os
import re
from dotenv import load_dotenv
from agents.utils import invoke_with_retry

load_dotenv()


def generate_automation_code(framework_plan: str, test_cases: str, target_url: str, model_name: str,
                              framework: str = "Playwright", language: str = "JavaScript") -> dict:
    llm = ChatGoogleGenerativeAI(model=model_name, google_api_key=os.getenv("GOOGLE_API_KEY"))

    prompt = ChatPromptTemplate.from_template(
        """You are a senior SDET. Based on this verified framework plan and test cases, generate 
        TWO complete, runnable {framework} ({language}) files for the target URL: {url}

        Framework Plan (contains REAL verified locators - use these exactly, do not invent new ones):
        {framework_plan}

        Test Cases to automate:
        {test_cases}

        Output format - respond with EXACTLY this structure, nothing else, no extra commentary:

        ===PAGE_OBJECT===
        (complete page object / component class code here)

        ===TEST_FILE===
        (complete test file code here, covering the positive and negative test cases)

        Use idiomatic {language} conventions and {framework} best practices throughout. 
        Keep code clean and production-quality, no placeholder comments like "add more tests here".
        """
    )

    chain = prompt | llm
    raw_output = invoke_with_retry(chain, {
        "url": target_url, "framework_plan": framework_plan, "test_cases": test_cases,
        "framework": framework, "language": language
    })

    return parse_code_blocks(raw_output)


def parse_code_blocks(raw_output: str) -> dict:
    page_object_match = re.search(r"===PAGE_OBJECT===(.*?)===TEST_FILE===", raw_output, re.DOTALL)
    test_file_match = re.search(r"===TEST_FILE===(.*)", raw_output, re.DOTALL)

    page_object_code = page_object_match.group(1).strip() if page_object_match else ""
    test_file_code = test_file_match.group(1).strip() if test_file_match else ""

    page_object_code = re.sub(r"^```(?:\w+)?\n|```$", "", page_object_code, flags=re.MULTILINE).strip()
    test_file_code = re.sub(r"^```(?:\w+)?\n|```$", "", test_file_code, flags=re.MULTILINE).strip()

    return {"page_object": page_object_code, "test_file": test_file_code}