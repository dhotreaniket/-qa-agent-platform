# PythiAiAgent — Multi-Agent QA Automation Platform

An AI-powered, multi-agent pipeline that automates the QA lifecycle — from raw requirements to executable test code — built using Python, LangChain, and the Gemini API.

## Why this exists

Manual QA workflows involve repetitive, time-consuming steps: writing user stories, deriving test cases, building automation scripts, and maintaining frameworks. This project explores how a chain of specialized AI agents — each responsible for one step — can accelerate this pipeline while keeping outputs structured, reviewable, and framework-ready for real test execution.

**As of this milestone, the pipeline runs end-to-end with a single command**: `python main.py` takes a requirement and a target URL, and autonomously produces a real Jira story (pushed via the Jira REST API), structured test cases, a verified automation strategy (grounded in the live page's real HTML, not guessed locators), real runnable Playwright code written directly into the execution project, automatic test execution with pass/fail reporting, an HTML report, and a generated Jenkinsfile for CI/CD — covering the full requirement-to-regression lifecycle originally envisioned for this project.

The architecture is also designed to be **automation-type agnostic**: a `runner_config` abstraction means the same Agent 3/4 pipeline can target Web (Playwright), and is structured to extend to API (RestAssured), Mobile (Appium), or Performance (k6) by adding a new config entry and prompt variant — not rewriting the pipeline.

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
| 1. Story Agent | ✅ Working | Converts raw requirements into structured Jira-style user stories, and **pushes them directly into a real Jira Cloud project** via the REST API (or reads an existing Jira story by key instead of generating one) |
| 2. Test Case Agent | ✅ Working | Generates positive, negative, and edge-case test cases from a user story |
| 3. Framework Analyzer | ✅ Working | Reads the LIVE HTML of the target app (via Playwright) and recommends a Playwright (JS) automation strategy with real, verified locators — no hardcoded or guessed selectors |
| 4. Code Generator | ✅ Working | Generates real, runnable Playwright (JS) Page Object + test spec files from the verified framework plan |
| 5. Execution Agent | ✅ Working | Automatically triggers the real test run (`npx playwright test`) via Python subprocess directly against the generated code in the runner project, captures output, reports pass/fail |
| 6. Auto-Heal Agent | 🔧 Working, with known limitations | Re-fetches live HTML + runs an instrumented diagnostic re-run to classify failures (locator / timing / assertion / wrong-interaction-method) and propose fixes. A self-heal loop (patch → re-run → verify, with retry) is built but currently limited by naive exact-string patch matching — see "Lessons learned." |
| 7. Report + CI/CD Agent | 📋 Planned | Generates execution reports and Jenkins pipeline configs |

## Key design decisions

- **Config-driven, not hardcoded**: target URL, Gemini model name, and automation type (`web`/future: `api`/`mobile`/`performance`) live in `config.json`, never hardcoded in agent code.
- **Automation-type agnostic architecture**: a `runner_config.py` registry maps an `automation_type` to its runner directory, file structure, run command, and language/framework — Agent 3 and Agent 4 accept `framework`/`language` as parameters rather than hardcoding "Playwright JavaScript," so adding API (RestAssured/Java) or Mobile (Appium) support means adding a config entry and prompt variant, not restructuring the pipeline.
- **No manual file-copying**: Agent 4 writes generated code directly into the execution project's real file structure (e.g. `playwright-runner/tests/`), and Agent 5 triggers real execution via `subprocess` immediately after — a single `python main.py` run covers requirement-to-execution with zero manual steps.
- **Real HTML inspection, not guessed locators**: Agent 3 uses a headless Playwright browser to fetch and read the actual live HTML of the target page before recommending locators.
- **Caching**: each agent's output is cached to disk; re-running the pipeline skips already-completed steps unless `force_rerun=True`, saving both time and API tokens during iteration.
- **Retry-aware API calls**: all Gemini calls go through a shared retry helper that backs off and retries on both rate-limit (429) and transient server overload (503) errors.

## Lessons learned (real debugging journey)

Building this end-to-end surfaced genuinely useful findings, documented here rather than hidden:

- **Bot detection is real**: the target practice site blocks naive HTTP requests and is sometimes flaky even with headless Playwright. Fix: prefer headed/real browser contexts, add retry-with-backoff to HTML fetches, and default test execution to a single reliable browser (Chromium) rather than all three.
- **Generated locators can still be wrong even when grounded in real HTML** — the model correctly read `h1.post-title` from live HTML, but the actual test failure (TC_003) was a race condition / wrong interaction method, not a locator problem.
- **Auto-Heal Agent — diagnosis vs. fix quality are different skills**: given only a static error log, the agent could correctly classify a failure as timing-related but initially proposed fixes that just reshuffled existing assertions rather than restructuring the interaction. Adding a genuine **instrumented re-run** (actually re-executing the test to gather fresh runtime evidence, not just analyzing a stale log) let the agent correctly diagnose a subtle real bug: pressing Enter doesn't submit this particular form because its inputs sit inside a `<div>`, not a `<form>` — and it proposed focusing the submit button before pressing Enter, which works.
- **Self-heal loop limitation (current, unresolved)**: the patch-application step uses exact string matching to locate code to replace. In practice the LLM's restated "broken code" doesn't always match the real file's exact whitespace/formatting, causing `patch_failed_old_code_not_found`. A more robust version would have the agent locate the target code by structural/semantic search (e.g., AST-based or line-range based) rather than literal string matching.
- **Config-driven design paid off**: switching Gemini models (after hitting daily free-tier limits) and pointing at a different target URL required zero code changes — only edits to `config.json`. The same is intended to hold true for switching automation types in the future.
- **Windows-specific subprocess gotcha**: `subprocess.run(["npx", ...])` fails with `FileNotFoundError` on Windows because `npx` resolves to `npx.cmd`; using a single command string with `shell=True` fixes this.

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

- [x] Agent 3: Framework Analyzer (reads live HTML via Playwright, recommends automation strategy with real locators — now framework/language agnostic)
- [x] Agent 4: Code Generator (executable code, written directly into the runner project — no manual copying)
- [x] Agent 5: Execution Agent (auto-runs the real test suite via subprocess, captures pass/fail)
- [x] Agent 6: Auto-Heal Agent v1 (diagnosis-driven, validated against real bugs including a subtle interaction-method issue)
- [x] Jira integration: push generated stories to a real Jira Cloud project, or read an existing story by key
- [ ] Agent 6 v2: robust self-heal loop (structural/semantic patch matching instead of exact string match)
- [ ] Agent 7: Reporting + Jenkins CI/CD pipeline generation
- [ ] Extend `runner_config` to support API (RestAssured/Java), Mobile (Appium), and Performance (k6) automation types
- [ ] Optional: lightweight UI/CLI for non-technical pipeline triggering (e.g. "I want to test Web/API/Mobile/Performance for this app")

## Author

Built by Aniket — Senior QA Automation Lead (BFSI/Fintech), exploring the intersection of AI and test engineering.

Follow the build journey: [add YouTube/LinkedIn links]