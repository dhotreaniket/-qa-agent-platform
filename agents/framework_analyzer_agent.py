from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
from agents.html_reader import get_clean_html
from agents.utils import invoke_with_retry

load_dotenv()


def analyze_framework(test_cases: str, target_url: str, model_name: str,
                       framework: str = "Playwright", language: str = "JavaScript") -> str:
    llm = ChatGoogleGenerativeAI(model=model_name, google_api_key=os.getenv("GOOGLE_API_KEY"))

    real_html = get_clean_html(target_url)
    real_html = real_html[:6000]

    prompt = ChatPromptTemplate.from_template(
        """You are a senior SDET architect. Below is the ACTUAL live HTML of the page to test. 
        Identify real locators (id, name, class, or text-based) by reading this HTML directly - 
        do NOT assume or invent any locator that isn't actually present in this HTML.

        Target automation stack: {framework} ({language})
        Target URL: {url}

        ACTUAL PAGE HTML:
        {html}

        Recommend a {framework} ({language}) automation strategy in this structure:
        1. Framework: (confirm {framework} / {language})
        2. Page Object / Component Classes Needed: (with locators found directly in the HTML above)
        3. Key Elements/Locators: (only elements that exist in the HTML above)
        4. Test Data Requirements
        5. Suggested File Structure

        Keep response under 400 words.

        Test Cases:
        {test_cases}
        """
    )

    chain = prompt | llm
    return invoke_with_retry(chain, {
        "url": target_url, "html": real_html, "test_cases": test_cases,
        "framework": framework, "language": language
    })