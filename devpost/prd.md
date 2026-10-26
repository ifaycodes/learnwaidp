---
doc: prd
status: approved
---

# awam — Product Requirements

A developer-first CLI tool that inspects Python source files and their local dependencies (up to 3 related files), pinpoints "what could go wrong" edge cases through Socratic inquiry prompts before production breaks, provides real-time reinforcement of what the user already covered alongside new gaps, and offers on-demand unit test generation (`--generate`) into the project's `tests/` directory with live `pytest` validation (`--run`) and developer-led fix suggestions.

Source: `scope.md > The Unique Kernel`, `scope.md > Who It's For`

## The Core Journey

1. **Invocation:** The developer opens their terminal in their project directory and runs `awam <file>` (default safe inquiry mode), optionally including flags like `--generate`, `--run`, `--mock`, or `--verbose`.
2. **Progressive Step Feedback:** `awam` prints immediate status steps (`Looking through file...`, `Analyzing dependencies...`).
3. **Pre-Flight Sanity Check:** It scans for immediate syntax errors locally using Python AST (`ast.parse`) in 0.02s before making any external calls, reporting syntax errors with exact line numbers upfront.
4. **Context & Contract Analysis:** `awam` analyzes the target file and up to 2 directly imported local files (max 3 files total, e.g. `sample/helper.py` imported by `sample/calculator.py`) to understand real function contracts, expected inputs, and return values.
5. **Unified Edge Case Audit & Socratic Inquiries:**
   - `awam` generates a mental model of candidate edge cases (e.g. Case 1: null response, Case 2: empty payload, Case 3: boundary numbers).
   - As it inspects existing tests in `tests/test_<name>.py`, it audits each candidate case:
     - **Already handled:** Marked with a green checkmark `[✓] Already covered: <case>` — giving the developer immediate positive reinforcement that their intuition was spot-on.
     - **Missing gap:** Marked with `[+] Missing gap: <case>` with a probing Socratic question (*"❓ Inquiry: What happens to Y when X fails?"*) to prompt developer thinking.
6. **Default Safe Inquiry vs On-Demand Test Writing (`--generate`):**
   - **Default (`awam <file>`):** Inquiry mode active. Zero files modified on disk, allowing the developer to draft their own tests.
   - **`--generate` (`-g`):** Appends only missing tests to `tests/test_<name>.py` (creating the file if absent, preserving existing tests without duplication).
7. **Educational Output:**
   - Displays the complete audit log (both what the user already did right and the new inquiry prompts), reinforcing solid testing patterns over time.
8. **Optional Validation (`--run`):**
   - If `--run` is enabled, `awam` executes `pytest` against `tests/test_<name>.py`.
   - If all tests pass: displays green success summary.
   - If a test fails (revealing an unhandled error path in source code): displays the test output followed by concise, actionable suggestions for what the developer can fix in their source code. The developer performs all code edits; `awam` never alters source code.

## Interaction Surface & CLI Flags

`awam` operates exclusively as a command-line interface in the developer's terminal. 

### CLI Flags & Behavior
`awam` provides a minimal, focused set of command-line flags tailored for developer learning, safety, and rapid validation:

| Flag / Tag | Alias | Default | Behavior & What It Does |
|---|---|---|---|
| `awam <file>` | *(None)* | *(Required)* | **Default Socratic Inquiry Mode:** Parses and analyzes the target Python file and its local dependencies. Runs local pre-flight syntax checks, audits existing tests, and displays the Unified Edge Case Audit with probing questions (*"❓ Inquiry: What happens to Y when X fails?"*). Safe and non-destructive: zero files are written or modified on disk, encouraging developers to formulate their own tests. |
| `--generate` | `-g` | `False` | **On-Demand Test Generation:** Writes or cleanly appends newly generated test functions covering missing edge cases into `tests/test_<name>.py` (or `--output`). Preserves existing tests without modification or duplication. |
| `--run` | *(None)* | `False` | **Validation Test Runner:** Executes `pytest` against the test file via subprocess. If all tests pass, shows a green success banner. If a test fails, extracts the traceback and queries Gemini for a targeted 2-sentence developer fix suggestion. Never mutates source code. |
| `--mock` | `--demo` | `False` | **Offline Simulation Mode:** Runs the entire pipeline locally without making calls to the Gemini API. Uses realistic heuristic edge case generation for zero-quota testing, instant demos, and environments where `GEMINI_API_KEY` is not set. Cross-shell compatible (works seamlessly in Git Bash, PowerShell, and Command Prompt). |
| `--audit-only` | *(None)* | `False` | **Syntax Preview Mode:** Displays a syntax-highlighted preview of the test code that `awam` would generate directly in the terminal, without writing to disk. |
| `--verbose` | `-v` | `False` | **Diagnostic Telemetry:** Prints detailed diagnostic metadata in a cleanly separated footer at the bottom of terminal output (files analyzed, external mocks, target test file, LLM model, token counts, and execution latency). |
| `--output <path>` | `-o` | `tests/test_<name>.py` | **Custom Test File Destination:** Directs generated tests to a custom file path rather than the default `tests/test_<filename>.py`. |

### Output Structure
1. **Header & Context:** Tool name, analyzed target file, and resolved dependencies.
2. **Pre-flight Notices:** Any syntax errors or call parameter mismatches caught locally.
3. **Unified Edge Case Audit:**
   - `[✓]` Green checkmarks for edge cases already tested by the developer (positive reinforcement).
   - `[+]` Yellow badges for missing edge cases with probing Socratic inquiry questions.
4. **Action Hints / Test File Update Summary:** Number of tests appended (when `--generate` is used) or next-step hints.
5. **Validation Block (when `--run` is passed):** Live stream of pytest output + developer fix suggestions if tests fail.

## Look and Feel

- **Formatting:** Clean, structured CLI typography with minimal visual noise.
- **Color Coding:**
  - `Cyan`: Informational status and file paths (e.g. `[awam] Analyzing src/app.py...`)
  - `Yellow`: Warnings, pre-flight notices, and missing edge cases being generated (`[+]`).
  - `Green`: Edge cases already covered by the developer (`[✓]`), successful file writes, and passing tests.
  - `Red`: Failing test runner results.
- **Tone:** Professional, encouraging developer peer tone. Celebrates what the developer already covered while clearly flagging gaps.

## Features and Behavior

### 1. Pre-Flight Lint & Syntax Sanity Check
- Source: `scope.md > The Unique Kernel`
- **Behavior:** Scans the target file for immediate syntax errors, typos, or obvious argument mismatches before running full analysis.
- **Acceptance Criteria:**
  - [ ] If syntax error exists in the target file, `awam` flags line number and description without crashing.
  - [ ] If an imported function is invoked with incorrect parameter counts, flags the discrepancy in terminal feedback.

### 2. Multi-File Context Analysis (Max 3 Files)
- Source: `scope.md > The Unique Kernel`, `scope.md > The POC Boundary`
- **Behavior:** Accepts a target Python file and traverses its immediate local imports (or accepts up to 3 explicitly specified related files). Capped at 3 files to ensure high context quality and token efficiency.
- **Acceptance Criteria:**
  - [ ] Automatically detects local imports (e.g. `import helper` or `from helper import calc_tax`) and loads them into analysis context.
  - [ ] Never traverses deeper than 3 related files total.
  - [ ] Non-local third-party packages (e.g. `os`, `sys`, `requests`, `numpy`) are treated as external and mocked where needed rather than read from disk.

### 3. Unified Edge Case Audit & Developer Reinforcement
- Source: `scope.md > The Unique Kernel`, `scope.md > Why This Matters to the Learner`
- **Behavior:** Explicitly checks candidate failure modes (nulls, boundary inputs, exceptions) against existing test files and reports an itemized audit on every run.
- **Acceptance Criteria:**
  - [ ] Lists edge cases already covered by existing tests with a green `[✓] Already covered: <scenario>`.
  - [ ] Lists missing edge cases with a yellow `[+] Missing gap: <scenario>`.
  - [ ] Provides instant confirmation to the developer that their testing intuition was correct on covered cases.

### 4. Smart Test File Management in `tests/`
- Source: `scope.md > The POC Boundary`
- **Behavior:** Reads and manages test files inside a standardized `tests/` directory.
- **Acceptance Criteria:**
  - [ ] If `tests/` directory does not exist, creates it.
  - [ ] If `tests/test_<name>` does not exist, generates a complete valid test file with imports and runner setup.
  - [ ] If `tests/test_<name>` exists, parses existing test names and appends only the new tests at the bottom without overwriting or deleting existing tests.

### 5. Validation Runner & Developer-Led Fix Suggestions (`--run`)
- Source: `scope.md > The Unique Kernel`, `scope.md > What "Working" Looks Like`
- **Behavior:** Executes the project's native test runner (`pytest`) when `--run` is supplied. If tests fail, provides actionable guidance for the developer to fix the code themselves.
- **Acceptance Criteria:**
  - [ ] When `--run` is omitted, `awam` displays inquiries/audits without running test commands.
  - [ ] When `--run` is provided, invokes `pytest` against `tests/test_<name>.py` and displays results.
  - [ ] If a test fails because the source code lacks an error guard, prints a "Developer Fix Suggestion" panel pinpointing where the developer can add the guard.
  - [ ] `awam` NEVER modifies the source code file automatically.

## States and Boundaries

- **Inquiry Run (Default `awam <file>`):** Evaluates code, presents inquiries and audit table, and leaves disk completely untouched.
- **Generation Run (`--generate`):** Creates `tests/`, writes/appends `tests/test_<filename>.py` preserving existing tests.
- **Validation Run (`--run`):** Executes `pytest` live and streams results.
- **Fully Covered State:** Shows all considered edge cases with `[✓] Already covered`.
- **Test Failure State (`--run` enabled):** Displays failure trace + suggested source code fixes.
- **Missing / Invalid File Argument:** Displays friendly error explaining file path was not found and prints usage command syntax.

## Product Decisions

- **Socratic Inquiries by Default:** Prompts the developer with "What happens when..." questions to cultivate testing intuition rather than spoon-feeding code.
- **Developer Owns Code Edits:** The tool suggests fixes when tests fail, but never auto-patches source code. Developer agency and learning are preserved.
- **Max 3 Related Files:** Limits traversal to 3 files to balance deep context with token efficiency (conserving IBM Bob 40-coin budget).
- **CLI Terminal Native:** Developer never has to leave their terminal or copy-paste code into a web browser.
- **Standard `tests/` Directory:** Standardized test location simplifies project structure across Python projects.

## What We're Building

- CLI command `awam <file...> [--generate] [--run] [--mock] [--audit-only] [--verbose]`
- Focused Python support (`pytest`)
- Pre-flight syntax & parameter check via Python AST
- Local dependency traversal up to 3 files
- Unified edge case audit with Socratic inquiries (`[✓]` covered vs `[+]` missing)
- On-demand smart test creation/append in `tests/` (`--generate`)
- Test execution and developer fix suggestions with `--run`
- Offline evaluation mode with `--mock`

## Deferred From the POC

- Node.js (`jest` / `node:test`) and multi-language support.
- Deep recursive dependency graphs (> 3 files).
- Additional languages (Java, Go, Rust).
- Git staged diff scanning (`awam --diff`).
- Interactive TUI checkboxes for accepting individual tests.

## Non-Goals

- **No Source Code Mutation:** `awam` will not rewrite or edit implementation files.
- **No Web Interface:** No browser app, GUI, or copy-paste portals.
- **No Auto-Committing:** `awam` will not make git commits or push branches.

## Open Questions

*(None blocking spec approval. Technical details such as prompt templates, test runner invocation commands, and file AST parsing will be defined in `4-spec`.)*
