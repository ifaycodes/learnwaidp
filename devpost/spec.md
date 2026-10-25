---
doc: spec
status: approved
---

# awam — Technical Spec

## How This Works, In Plain Language

`awam` is a command-line tool written in Python that helps developers discover hidden bugs and edge cases before their code hits production, generating ready-to-run unit tests directly in their repository.

Here is how the system fits together in plain terms:
1. **The Entrypoint:** You run `awam src/app.py` in your terminal. `awam` parses your CLI flags and verifies the file exists.
2. **Pre-Flight Checker:** Before making any network or AI calls, `awam` checks the file locally using Python's built-in syntax engine (`ast.parse`). If there is a syntax error or a broken parameter call, it catches it immediately and warns you, saving API calls.
3. **Local Import Resolver:** `awam` inspects your file's imports to find local modules (like `import grow` or `./grow.js`). It loads up to 2 local helper files (maximum 3 files total) so it understands what external functions return and what errors they might throw.
4. **Existing Test Inspection:** `awam` looks into your `tests/` directory to see if you already have existing tests (e.g. `tests/test_app.py`).
5. **AI Audit Engine:** It sends your source code, local dependencies, and existing tests to Google Gemini Flash with a strict JSON format request. Gemini returns:
   - Candidate edge cases (null inputs, empty lists, boundary values, network failures).
   - An audit status for each case: `covered` (if an existing test handles it) or `missing` (if it's an untested gap).
   - Clean, runnable test code for only the missing cases.
6. **Smart Test Writer:** `awam` writes or appends the new test cases to `tests/test_app.py` without touching your existing tests. (If `--audit-only` was passed, it skips writing to disk).
7. **Validation Runner & Fix Advisor:** If you passed `--run`, `awam` runs `pytest` or `npm test` automatically. If any tests fail, it captures the failure traceback and asks Gemini for a 2-sentence fix suggestion explaining what error guard to add in your source code. You fix the code; `awam` never alters your source files.

We chose this lightweight, stateless architecture because it requires zero server infrastructure, runs in under 3 seconds, costs $0 to test, and fits directly into standard developer terminal habits.

---

## The Core Journey Through the System

Traced step-by-step from `prd.md > The Core Journey`:

1. **Invocation:** Developer runs `awam src/app.py --run` in their project terminal.
2. **Flag & Path Parsing:** `cli.py` extracts arguments (`file=src/app.py`, `run=True`, `audit_only=False`, `verbose=False`, `output=None`).
3. **Pre-flight Check:** `analyzer.py` runs Python `ast.parse` (or Node regex check). If valid, emits step: `[awam] Pre-flight syntax check passed.`
4. **Dependency Traversal:** `resolver.py` finds `import grow` in `src/app.py`, confirms `src/grow.py` exists on disk, reads both files, and caps total files to 3.
5. **Test Discovery:** `test_manager.py` checks for `tests/test_app.py`, reads its content (or notes it as absent).
6. **Gemini Audit Call:** `engine.py` builds the prompt with source code + existing test content and calls Gemini Flash with a structured JSON schema.
7. **Audit Display:** `reporter.py` prints the color-coded audit table using `rich`:
   - `[✓] Already covered: Valid input calculation` (Green)
   - `[+] Missing gap: Null payload handling` (Yellow)
   - `[+] Missing gap: Negative price boundary` (Yellow)
8. **File Write (unless `--audit-only`):** `test_manager.py` appends the generated test functions into `tests/test_app.py`.
9. **Validation (`--run`):** `runner.py` executes `pytest tests/test_app.py` via `subprocess.run`.
   - If tests pass: Green banner displayed.
   - If a test fails: Displays failure traceback + targeted Gemini suggestion: *"In src/app.py:12, add `if price < 0: raise ValueError(...)` before computing discounts."*
10. **Diagnostics (if `--verbose`):** Prints timing, tokens, and resolved dependencies at the bottom.

---

## Stack

| Technology | Role | Version / Docs | Rationale & Tradeoffs |
|---|---|---|---|
| **Python** | CLI Core Runtime | `>= 3.10` / [docs.python.org](https://docs.python.org/3/) | Native AST parsing, rapid subprocess handling, cross-platform compatibility across Windows/macOS/Linux. |
| **`google-genai`** | AI Client SDK | `>= 0.8.0` / [ai.google.dev/gemini-api/docs](https://ai.google.dev/gemini-api/docs) | Official Google GenAI SDK. Supports Gemini 2.0 / 1.5 Flash structured JSON outputs, ultra-fast latency, and a generous free tier ($0 cost). |
| **`rich`** | Terminal UI & Formatting | `>= 13.7.0` / [rich.readthedocs.io](https://rich.readthedocs.io/) | Beautiful, colored terminal output, spinners, tables, and tracebacks without clunky terminal escape sequences. |
| **`click`** | CLI Argument Parser | `>= 8.1.0` / [click.palletsprojects.com](https://click.palletsprojects.com/) | Clean, declarative command line interface definition with built-in help and flag handling. |
| **`pytest`** | Target Test Runner (Python) | `>= 8.0.0` / [docs.pytest.org](https://docs.pytest.org/) | Standard Python test execution invoked via subprocess when `--run` is supplied. |
| **`npm` / `jest`** | Target Test Runner (Node) | Native / [jestjs.io](https://jestjs.io/) | Standard Node test execution invoked via subprocess when testing JavaScript/TypeScript files. |

---

## Where It Runs and How Someone Tries It

### Runtime & Environment
* **Runtime:** Local terminal / command prompt.
* **Environment:** Python 3.10+ installed.
* **API Key:** Requires `GEMINI_API_KEY` set as an environment variable (free from Google AI Studio).

### Installation (Local Editable Mode)
```bash
git clone https://github.com/<user>/awam.git
cd awam
pip install -e .
```
This registers the global `awam` command directly in the user's terminal.

### Starting and Trying It
```bash
# Basic run: analyze code and generate missing tests
awam sample/calculator.py

# Run and immediately execute pytest/jest with fix tips on failure
awam sample/calculator.py --run

# Preview edge cases and tests without writing to disk
awam sample/calculator.py --audit-only

# View verbose diagnostics (files resolved, tokens, latency)
awam sample/calculator.py --verbose
```

### Devpost Submission Note
Submission requires a **short demo video** (showing `awam` analyzing a file with a missing edge case, appending the test, and running `--run`) and a **public GitHub repository**. Live cloud deployment is not required for a developer CLI tool.

---

## Look and Feel

Implements `prd.md > Look and Feel`:

* **CLI Palette:**
  * `Cyan / Bold Cyan`: Status headers, stage announcements (e.g. `[awam] Analyzing sample/app.py...`).
  * `Green`: Positive reinforcement for already handled tests (`[✓] Already covered: <case>`), successful test writes, and passing test runs.
  * `Yellow`: Warning notices, pre-flight discrepancies, and missing edge cases being added (`[+] Missing gap: <case>`).
  * `Red`: Failing test runner results and syntax errors.
  * `Dim / Gray`: File paths, line numbers, and diagnostic footer details.
* **Tone:** Pragmatic, supportive, educational developer peer. Reinforces good practices while making edge cases obvious.
* **Footer (when `--verbose` is passed):** Appears cleanly separated at the bottom of the output:
  ```text
  ──────────────── Diagnostics ────────────────
  • Files analyzed: sample/app.py, sample/helper.py (local)
  • External packages mocked: requests
  • Target test file: tests/test_app.py (appended 2 tests)
  • Model: gemini-3.8-flash | Latency: 1.1s | Tokens: 480 in / 190 out
  ```

---

## Components

### CLI Entrypoint (`awam.cli`)
* **What it does:** Defines command options, flags (`--run`, `--audit-only`, `--verbose`, `--output`), and coordinates the pipeline.
* **What it talks to:** `analyzer.py`, `resolver.py`, `engine.py`, `test_manager.py`, `runner.py`, and `reporter.py`.
* **PRD Ref:** Implements `prd.md > Interaction Surface & Terminal Output`.

### Pre-Flight Lint & Syntax Checker (`awam.analyzer`)
* **What it does:** Scans target source files using Python's `ast.parse` (or basic syntax validation for JS) before any external API calls are made. If syntax errors exist, reports line numbers immediately.
* **What it talks to:** Local filesystem, `reporter.py`.
* **PRD Ref:** Implements `prd.md > 1. Pre-Flight Lint & Syntax Sanity Check`.

### Multi-File Context Resolver (`awam.resolver`)
* **What it does:** Inspects `import` / `require` statements in the primary file, identifies relative local files on disk (ignoring third-party and standard library packages), and loads up to 2 local helper files (maximum 3 files total).
* **What it talks to:** Local filesystem.
* **PRD Ref:** Implements `prd.md > 2. Multi-File Context Analysis (Max 3 Files)`.

### AI Analysis & Audit Engine (`awam.engine`)
* **What it does:** Constructs the prompt with source code, local dependencies, and existing test contents. Calls Gemini Flash with structured schema to return:
  1. Candidate edge cases.
  2. Status (`covered` vs `missing`).
  3. Generated test code for missing cases.
* **What it talks to:** `google.genai.Client`, `GEMINI_API_KEY`.
* **PRD Ref:** Implements `prd.md > 3. Unified Edge Case Audit & Developer Reinforcement`.

### Smart Test File Manager (`awam.test_manager`)
* **What it does:** Locates standard `tests/test_<name>.py` (or specified `--output`), creates the directory and file if missing, or cleanly appends new test functions to the end of the existing file without modifying existing tests.
* **What it talks to:** Local filesystem.
* **PRD Ref:** Implements `prd.md > 4. Smart Test File Management in tests/`.

### Validation Runner & Fix Advisor (`awam.runner`)
* **What it does:** When `--run` is supplied, invokes the native test runner (`pytest` or `npm test`). If a test fails, extracts the error traceback and prompts Gemini Flash for a concise 2-sentence developer fix suggestion.
* **What it talks to:** Python `subprocess`, `engine.py`, `reporter.py`.
* **PRD Ref:** Implements `prd.md > 5. Validation Runner & Developer-Led Fix Suggestions (--run)`.

### Terminal UI & Reporter (`awam.reporter`)
* **What it does:** Manages all user-facing terminal output using `rich.console.Console`. Handles colors, progress spinners, edge case audit tables, test runner summaries, and the verbose diagnostics footer.
* **What it talks to:** Terminal stdout.
* **PRD Ref:** Implements `prd.md > Interaction Surface & Terminal Output` and `prd.md > Look and Feel`.

---

## Data Model

`awam` is stateless and does not require an external database. All transient analysis and audit data are modeled as typed Python dictionaries / Pydantic models:

### Edge Case Audit Item Schema
```python
class EdgeCaseAuditItem(BaseModel):
    scenario: str          # Description of the edge case (e.g. "Null input parameter")
    status: Literal["covered", "missing"] # Audit status
    matched_test: str | None # Existing test function name if covered
    reason: str            # Brief explanation why it is covered or why it is a risk
```

### Complete Audit & Generation Response Schema
```python
class AnalysisResponse(BaseModel):
    candidate_cases: list[EdgeCaseAuditItem]
    generated_tests: str   # Clean, runnable test code for missing cases only
    imports_needed: list[str] # Any mock or framework imports needed
```

### Fix Suggestion Response Schema (for `--run` failure)
```python
class FixSuggestion(BaseModel):
    error_summary: str     # Concise summary of what assertion failed
    suggested_guard: str   # 1-2 sentence developer guidance on what guard to add in source
    target_file: str       # File where the fix belongs
```

---

## File Structure

Annotated tree of the `awam` project repository:

```
devpost-challenge/
├── awam/                     # Core Python package
│   ├── __init__.py           # Package version and metadata
│   ├── cli.py                # Command-line entrypoint and Click flag definitions
│   ├── analyzer.py           # Pre-flight syntax validation and argument check
│   ├── resolver.py           # Local import and dependency scanner (max 3 files)
│   ├── engine.py             # Gemini Flash API client and prompt orchestration
│   ├── test_manager.py       # Test file discovery, creation, and appending in tests/
│   ├── runner.py             # Subprocess pytest/jest execution and failure capture
│   └── reporter.py           # Rich terminal console formatting, tables, and colors
├── sample/                   # Demo sample files for testing and video recording
│   ├── calculator.py         # Sample source file with edge cases
│   ├── helper.py             # Local dependency imported by calculator.py
│   └── tests/                # Sample tests showing covered vs missing behavior
│       └── test_calculator.py
├── devpost/                  # Devpost hackathon documentation workspace
│   ├── learner-profile.md
│   ├── scope.md
│   ├── prd.md
│   ├── spec.md               # This technical blueprint
│   └── spec.html             # Interactive visual companion
├── pyproject.toml            # Build configuration and global CLI entrypoint
├── requirements.txt          # Python dependencies (google-genai, rich, click, pytest)
└── README.md                 # Project documentation and demo instructions
```

---

## External Services and Dependencies

| Service / Dependency | Endpoint / SDK | Credentials | Rate Limits / Free Tier | Cost |
|---|---|---|---|---|
| **Google Gemini Flash** | `google-genai` SDK (`gemini-3.8-flash`) | `GEMINI_API_KEY` in environment | Free tier: 15 Requests Per Minute (RPM), 1500 Requests Per Day | **$0.00** on free tier |

---

## Important Failure Modes

1. **Missing or Invalid `GEMINI_API_KEY`:**
   * *What breaks:* Call to Gemini API fails with authentication error.
   * *Fallback:* `awam` catches the exception and prints a clear red box: `[Error] GEMINI_API_KEY environment variable is not set. Get a free key at https://aistudio.google.com/ and run 'export GEMINI_API_KEY=your_key'.`
2. **Pre-Flight Syntax Error in Source Code:**
   * *What breaks:* The developer's source file has broken syntax (e.g. unclosed parenthesis).
   * *Fallback:* `awam.analyzer` catches `SyntaxError` locally before calling Gemini. Prints exact line number and problem: `[Pre-Flight Error] Syntax error in sample/app.py at line 14: invalid syntax. Fix syntax before running awam.`
3. **Test Runner Not Installed during `--run`:**
   * *What breaks:* Developer runs `awam --run` on a Python file, but `pytest` is not installed in their environment.
   * *Fallback:* `awam.runner` catches `FileNotFoundError` and explains: `[Runner Error] pytest not found in current environment. Install pytest with 'pip install pytest' or omit --run.`
4. **API Rate Limiting (429):**
   * *What breaks:* Free tier RPM limit exceeded.
   * *Fallback:* `awam` retries once with exponential backoff (2 seconds); if still throttled, outputs a friendly message advising the user to wait a moment.

---

## What Was Simplified and Why

* **Single Structured API Call** instead of multi-pass AST-to-LLM conversation — Sends source code, dependencies, and existing tests in a single structured prompt. Cuts token latency and cost in half.
* **Local Dependency Cap (Max 3 Files)** instead of whole-repo graph parsing — Inspects immediate imports only. Prevents context bloating, avoids circular dependency traps, and keeps API latency under 2 seconds.
* **Developer-Led Fix Suggestions** instead of auto-patching source code — When a test fails, `awam` guides the developer on where and what guard to write. The developer maintains complete ownership of their codebase.
* **`--audit-only` Flag** instead of interactive terminal prompts — Avoids complex interactive TUI state, giving users a simple non-destructive preview flag.
* **Standard `tests/` Directory Convention** instead of multi-directory configuration files — Keeps project setup zero-config for standard Python and Node projects while still allowing `--output` if needed.

---

## Decisions and Open Issues

### Decisions Made in `4-spec`:
* **CLI Implementation Language:** Python (chosen by learner for native AST support and rapid CLI prototyping with `rich` and `click`).
* **AI Model:** Google Gemini Flash (chosen by learner for low cost / free tier, fast inference, and reliable structured JSON outputs).
* **Audit Architecture:** Single-call prompt returning candidate edge cases with status (`covered` vs `missing`) alongside generated tests for missing cases only.
* **Validation & Fix Workflow (`--run`):** On test failure, `awam` captures the traceback and calls Gemini Flash to return a 2-sentence developer fix suggestion.
* **Read-Only Inspection Flag:** Named `--audit-only` (learner preference over `--dry-run`) to clearly describe inspecting edge cases without writing to disk.
* **Diagnostics Placement:** `--verbose` outputs diagnostic metadata (files, tokens, latency) in a clean footer at the bottom of the output.
* **Custom Output Flag:** `--output <path>` supported for non-standard test file locations.

### Learned Unknown & Uncertainty Clarified:
* **CLI Statefulness vs Non-destructive Preview:** Learner explored how `--dry-run` / `--audit-only` connects to saving files if the developer approves the output. Clarified that standard CLI architecture is stateless: `--audit-only` performs the read-only preview, and running `awam <file>` directly executes the write.

### Open Issues:
* *(None blocking build approval. All dependencies, CLI commands, component boundaries, and failure fallbacks are fully specified.)*
