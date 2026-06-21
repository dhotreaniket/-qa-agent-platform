from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()


def generate_test_cases(user_story: str) -> str:
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))

    prompt = ChatPromptTemplate.from_template(
        """You are a senior QA engineer. Given this user story, generate detailed test cases 
        (positive, negative, edge cases) in a structured table: 
        ID | Description | Steps | Expected Result | Priority.

        User Story:
        {story}
        """
    )

    chain = prompt | llm
    result = chain.invoke({"story": user_story})
    return result.content