# PythiAiAgent — Multi-Agent QA Automation Platform

An AI-powered, multi-agent pipeline that automates the QA lifecycle — from raw requirements to executable test code — built using Python, LangChain, and the Gemini API.

## Why this exists

Manual QA workflows involve repetitive, time-consuming steps: writing user stories, deriving test cases, building automation scripts, and maintaining frameworks. This project explores how a chain of specialized AI agents — each responsible for one step — can accelerate this pipeline while keeping outputs structured, reviewable, and framework-ready for real test execution.

This is a **build-in-public** project. Progress, design decisions, and learnings are documented on [YouTube/LinkedIn — add your links].

## Architecture

The platform is designed as a sequential multi-agent pipeline, where each agent has a single responsibility and passes its output to the next:

```
Raw Requirement
      │
      ▼
[Agent 1: Story Agent] ──► Structured Jira-style User Story
      │
      ▼
[Agent 2: Test Case Agent] ──► Test Cases (Positive / Negative / Edge)
      │
      ▼
[Agent 3: Framework Analyzer] (in progress) ──► Framework + Strategy Decision
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
```

## Current status

| Agent | Status | Description |
|---|---|---|
| 1. Story Agent | ✅ Working | Converts raw requirements into structured Jira-style user stories |
| 2. Test Case Agent | ✅ Working | Generates positive, negative, and edge-case test cases from a user story |
| 3. Framework Analyzer | ✅ Working | Reads the LIVE HTML of the target app (via Playwright) and recommends a Playwright (JS) automation strategy with real, verified locators — no hardcoded or guessed selectors |
| 4. Code Generator | ✅ Working | Generates real, runnable Playwright (JS) Page Object + test spec files from the verified framework plan |
| 5. Execution Agent | 📋 Planned | Will trigger `npx playwright test` via Python subprocess and capture results |
| 6. Auto-Heal Agent | 🔧 Working, with known limitations | Re-fetches live HTML and classifies failures (locator / timing / assertion). Reliably diagnoses locator mismatches grounded in real HTML; struggles to produce correct *structural* fixes for timing/race-condition failures from static logs alone — see "Lessons learned" below. |
| 7. Report + CI/CD Agent | 📋 Planned | Generates execution reports and Jenkins pipeline configs |

## Key design decisions

- **Config-driven, not hardcoded**: target URL and Gemini model name live in `config.json`, never hardcoded in agent code. Switching target apps or models requires zero code changes.
- **Real HTML inspection, not guessed locators**: Agent 3 uses a headless Playwright browser to fetch and read the actual live HTML of the target page before recommending locators — avoiding hallucinated selectors that wouldn't work in practice. This is the same engine planned for the future Execution Agent, so it's reused rather than duplicated.
- **Retry-aware API calls**: all Gemini calls go through a shared retry helper (`agents/utils.py`) that automatically backs off and retries on rate-limit errors.

## Lessons learned (real debugging journey)

Building this end-to-end surfaced genuinely useful findings, documented here rather than hidden:

- **Bot detection is real**: the target practice site blocks naive HTTP requests and sometimes headless browsers. Fix: use a real Playwright browser context (headed mode more reliable than headless for this specific site) rather than a simple HTTP client.
- **Generated locators can still be wrong even when grounded in real HTML** — the model correctly read `h1.post-title` from live HTML, but the actual *test logic* failure (TC_003) was a race condition, not a locator problem. Diagnosing the right failure category matters as much as having accurate data.
- **Auto-Heal Agent limitation**: given only a static error log, the agent could correctly *classify* a failure as a timing issue but could not always generate the correct *structural* fix (e.g., wrapping a trigger action in `Promise.all()` with `waitForURL`) — it tended to anchor on the previously-broken code and reshuffle assertions instead. Confirming the real fix required adding diagnostic logging and re-running to observe actual behavior (e.g., discovering that pressing `Enter` never submitted the form — only a real button click did). This suggests a more effective Auto-Heal design needs **two passes**: an instrumented diagnostic run, then a fix proposal informed by runtime evidence, not log text alone.
- **Config-driven design paid off**: switching Gemini models (after hitting daily free-tier limits) and pointing at a different target URL required zero code changes — only edits to `config.json`.

## Tech stack



- **Python 3.14**
- **LangChain** (`langchain`, `langchain-google-genai`) — prompt orchestration
- **Google Gemini API** (`gemini-2.5-flash`) — LLM backend
- **python-dotenv** — environment/secret management

## Project structure

```
PythiAiAgent/
├── agents/
│   ├── __init__.py
│   ├── story_agent.py        # Agent 1: Requirement -> User Story
│   └── test_case_agent.py    # Agent 2: User Story -> Test Cases
├── output/                    # Generated artifacts (gitignored)
├── .env                       # API keys (gitignored, not committed)
├── main.py                     # Pipeline orchestrator
└── requirements.txt
```

## Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/YOUR_USERNAME/PythiAiAgent.git
   cd PythiAiAgent
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   pip install -r requirements.txt
   ```

3. Add your Gemini API key:
   Create a `.env` file in the project root:
   ```
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

4. Run the pipeline:
   ```bash
   python main.py
   ```

Outputs are saved to `output/user_story.md` and `output/test_cases.md`.

## Sample output

**Input (raw requirement):**
> Users should be able to log into the web application using their email and password. If credentials are wrong, show an error. After 5 failed attempts, lock the account for 15 minutes.

**Agent 1 output:** A structured user story with Title, Description (As a/I want/So that), and Acceptance Criteria.

**Agent 2 output:** A full test case table covering valid login, invalid password, account lockout after 5 attempts, lockout expiry after 15 minutes, and related edge cases — each with ID, Steps, Expected Result, and Priority.

## Roadmap

- [x] Agent 3: Framework Analyzer (reads live HTML via Playwright, recommends Playwright POM strategy with real locators)
- [x] Agent 4: Code Generator (executable Playwright JS code — Page Object + test spec)
- [x] Agent 6: Auto-Heal Agent (first version — diagnoses from live HTML, documented limitations on timing/race-condition fixes)
- [ ] Agent 5: Execution Agent (run generated tests via Python subprocess, capture pass/fail)
- [ ] Agent 6 v2: two-pass auto-heal (instrumented diagnostic run + evidence-based fix)
- [ ] Agent 7: Reporting + Jenkins CI/CD pipeline generation
- [ ] Optional: lightweight UI/CLI for non-technical pipeline triggering

## Author

Built by Aniket — Senior QA Automation Lead (BFSI/Fintech), exploring the intersection of AI and test engineering.

Follow the build journey: [add YouTube/LinkedIn links]