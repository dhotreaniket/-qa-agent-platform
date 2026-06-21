from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()


def get_structured_story(raw_requirement: str) -> str:
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))

    prompt = ChatPromptTemplate.from_template(
        """You are a senior business analyst. Convert this raw requirement into a 
        well-structured Jira-style user story with Title, Description (As a/I want/So that), 
        and Acceptance Criteria.

        Raw requirement:
        {requirement}
        """
    )

    chain = prompt | llm
    result = chain.invoke({"requirement": raw_requirement})
    return result.content