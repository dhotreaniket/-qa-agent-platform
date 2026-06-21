PythiAiAgent — Multi-Agent QA Automation Platform

An AI-powered, multi-agent pipeline that automates the QA lifecycle — from raw requirements to executable test code — built using Python, LangChain, and the Gemini API.

Why this exists

Manual QA workflows involve repetitive, time-consuming steps: writing user stories, deriving test cases, building automation scripts, and maintaining frameworks. This project explores how a chain of specialized AI agents — each responsible for one step — can accelerate this pipeline while keeping outputs structured, reviewable, and framework-ready for real test execution.

This is a build-in-public project. Progress, design decisions, and learnings are documented on [YouTube/LinkedIn — add your links].

Architecture

The platform is designed as a sequential multi-agent pipeline, where each agent has a single responsibility and passes its output to the next:

Raw Requirement
      │
      ▼
[Agent 1: Story Agent] ──► Structured Jira-style User Story
      │
      ▼
[Agent 2: Test Case Agent] ──► Test Cases (Positive / Negative / Edge)
      │
      ▼
[Agent 3: Framework Analyzer]  ──► Framework + Strategy Decision
      │
      ▼
[Agent 4: Code Generator] (planned) ──► Executable Automation Code
      │
      ▼
[Agent 5: Execution Agent] (planned) ──► Test Run Results
      │
      ▼
[Agent 6: Auto-Heal Agent] (planned) ──► Failure Diagnosis + Fix Suggestions
      │
      ▼
[Agent 7: Report + CI/CD Agent] (planned) ──► HTML Report + Jenkins Pipeline

Current status

AgentStatusDescription1. Story Agent✅ WorkingConverts raw requirements into structured Jira-style user stories2. Test Case Agent✅ WorkingGenerates positive, negative, and edge-case test cases from a user story3. Framework Analyzer🔧 In progressAnalyzes test cases to decide automation framework/strategy (Playwright for Web)4. Code Generator📋 PlannedGenerates Page Object Model-based Playwright code5. Execution Agent📋 PlannedExecutes generated automation and captures results6. Auto-Heal Agent📋 PlannedDiagnoses failures and suggests fixes7. Report + CI/CD Agent📋 PlannedGenerates execution reports and Jenkins pipeline configs

Tech stack


Python 3.14
LangChain (langchain, langchain-google-genai) — prompt orchestration
Google Gemini API (gemini-2.5-flash) — LLM backend
python-dotenv — environment/secret management


Project structure

PythiAiAgent/
├── agents/
│   ├── __init__.py
│   ├── story_agent.py        # Agent 1: Requirement -> User Story
│   └── test_case_agent.py    # Agent 2: User Story -> Test Cases
├── output/                    # Generated artifacts (gitignored)
├── .env                       # API keys (gitignored, not committed)
├── main.py                     # Pipeline orchestrator
└── requirements.txt

Setup


Clone the repo:


bash   git clone https://github.com/dhotreaniket/PythiAiAgent.git
   cd PythiAiAgent


Create a virtual environment and install dependencies:


bash   python -m venv venv
   venv\Scripts\activate      # Windows
   pip install -r requirements.txt


Add your Gemini API key:
Create a .env file in the project root:


   GOOGLE_API_KEY=your_gemini_api_key_here


Run the pipeline:


bash   python main.py

Outputs are saved to output/user_story.md and output/test_cases.md.

Sample output

Input (raw requirement):


Users should be able to log into the web application using their email and password. If credentials are wrong, show an error. After 5 failed attempts, lock the account for 15 minutes.



Agent 1 output: A structured user story with Title, Description (As a/I want/So that), and Acceptance Criteria.

Agent 2 output: A full test case table covering valid login, invalid password, account lockout after 5 attempts, lockout expiry after 15 minutes, and related edge cases — each with ID, Steps, Expected Result, and Priority.

Roadmap


 Agent 3: Framework Analyzer (decide Playwright POM structure based on app type)
 Agent 4: Code Generator (executable Playwright/RestAssured code)
 Agent 5: Execution Agent (run generated tests, capture pass/fail)
 Agent 6: Auto-Heal Agent (diagnose and suggest fixes for failing tests)
 Agent 7: Reporting + Jenkins CI/CD pipeline generation
 Optional: lightweight UI/CLI for non-technical pipeline triggering


Author

Built by Aniket — Senior QA Automation Lead (BFSI/Fintech), exploring the intersection of AI and test engineering.

Follow the build journey: [add YouTube/LinkedIn links]