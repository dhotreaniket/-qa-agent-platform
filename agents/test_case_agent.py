from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
from agents.utils import invoke_with_retry

load_dotenv()


def generate_test_cases(user_story: str, model_name: str) -> str:
    llm = ChatGoogleGenerativeAI(model=model_name, google_api_key=os.getenv("GOOGLE_API_KEY"))

    prompt = ChatPromptTemplate.from_template(
        """You are a senior QA engineer. Given this user story, generate EXACTLY 8 test cases total: 
        3 positive, 3 negative, 2 edge cases. No more, no fewer.

        Format as plain text (NOT a markdown table, no pipe characters), one test case per block, like this:

        TC_001 | Priority: High
        Description: <one line>
        Steps: <numbered steps, max 4>
        Expected Result: <one line>

        Keep each test case under 60 words total. Do not add extra commentary, headers, or explanations 
        before or after the test cases.

        User Story:
        {story}
        """
    )

    chain = prompt | llm
    return invoke_with_retry(chain, {"story": user_story})
