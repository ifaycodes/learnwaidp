---
doc: prd
status: approved
---

# awam — Product Requirements

A developer-first CLI tool that inspects source files and their local dependencies (up to 3 related files), pinpoints "what could go wrong" edge cases and error paths before production breaks, provides real-time reinforcement of what the user already covered alongside new gaps, and writes runnable unit tests into the project's `tests/` directory with optional test execution and developer-led fix suggestions.

Source: `scope.md > The Unique Kernel`, `scope.md > Who It's For`

## The Core Journey

1. **Invocation:** The developer opens their terminal in their project directory and runs `awam <file>` (or passes up to 3 related files/dependencies, e.g. `awam src/app.py src/grow.py`), optionally including `--run`.
2. **Progressive Step Feedback:** `awam` prints immediate status steps (`Looking through file...`, `Analyzing dependencies...`).
3. **Pre-Flight Sanity Check:** It scans for immediate syntax errors, typos, or parameter mismatches between calls and imported functions, reporting them upfront.
4. **Context & Contract Analysis:** `awam` analyzes the target file and up to 2 directly imported local files (max 3 files total) to understand real function contracts, expected inputs, and return values.
5. **Unified Edge Case Audit & Reinforcement:**
   - `awam` generates a mental model of candidate edge cases (e.g. Case 1: null response, Case 2: empty payload, Case 3: boundary numbers).
   - As it inspects existing tests in `tests/test_<name>`, it audits each candidate case:
     - **Already handled:** Marked with a green checkmark `[✓] Already covered: <case>` — giving the developer immediate positive reinforcement that their intuition was spot-on.
     - **Missing gap:** Marked with `[+] Missing edge case: <case>` — flagged for test generation.
6. **Test Writing & Preservation:**
   - Appends only the missing tests to `tests/test_<name>` (creating the file if absent, or preserving existing tests if present).
   - Never generates redundant duplicates for cases already covered.
7. **Educational Output:**
   - Displays the complete audit log (both what the user already did right and the new tests generated), reinforcing solid testing patterns over time.
8. **Optional Validation (`--run`):**
   - If `--run` is enabled, `awam` executes the local test runner (`pytest` or `jest`).
   - If all tests pass: displays green success summary.
   - If a test fails (revealing an unhandled error path in source code): displays the test output followed by concise, actionable suggestions for what the developer can fix in their source code. The developer performs all code edits; `awam` never alters source code.

## Interaction Surface & Terminal Output

`awam` operates exclusively as a command-line interface in the developer's terminal. 

### Output Structure
1. **Header & Context:** Tool name, detected language/framework, and files analyzed.
2. **Pre-flight Notices:** Any syntax/call mismatches noticed between files.
3. **Unified Edge Case Audit:**
   - `[✓]` Green checkmarks for edge cases already tested by the developer (positive reinforcement).
   - `[+]` Yellow badges for edge cases missing from tests.
4. **Test File Update Summary:** Number of tests appended to `tests/test_<name>`.
5. **Validation Block (when `--run` is passed):** Live stream of runner output + developer fix suggestions if tests fail.

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
- **Behavior:** Accepts a target file and traverses its immediate local imports (or accepts up to 3 explicitly specified related files). Capped at 3 files to ensure high context quality and token efficiency.
- **Acceptance Criteria:**
  - [ ] Automatically detects local imports (e.g. `import grow` or `const grow = require('./grow')`) and loads them into analysis context.
  - [ ] Never traverses deeper than 3 related files total.
  - [ ] Non-local third-party packages (e.g. `os`, `express`, `requests`) are treated as external and mocked where needed rather than read from disk.

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
- **Behavior:** Executes the project's native test runner (`pytest` for Python, `jest`/node test for Node) when `--run` is supplied. If tests fail, provides actionable guidance for the developer to fix the code themselves.
- **Acceptance Criteria:**
  - [ ] When `--run` is omitted, `awam` writes tests and exits cleanly without running test commands.
  - [ ] When `--run` is provided, invokes `pytest` or `npm test` and displays results.
  - [ ] If a newly added test fails because the source code lacks an error guard, prints a "Suggested Fix" section pinpointing where the developer can add the guard.
  - [ ] `awam` NEVER modifies the source code file automatically.

## States and Boundaries

- **First Run (No `tests/` directory):** Creates `tests/`, writes `tests/test_<filename>`, and prints audit showing all candidate cases marked `[+] Missing gap (generating)`.
- **Incremental Run (Existing tests present):** Shows mixed audit with `[✓] Already covered` for existing test cases and `[+] Missing gap` for new ones; appends only the missing tests.
- **Fully Covered State:** Shows all considered edge cases with `[✓] Already covered`; leaves test file untouched.
- **Test Failure State (`--run` enabled):** Displays failure trace + suggested source code fixes.
- **Missing / Invalid File Argument:** Displays friendly error explaining file path was not found and prints usage command syntax.

## Product Decisions

- **Unified Reinforcement Audit:** Displays both covered and missing edge cases on every run. Reinforces the developer's confidence that they are thinking in the right direction.
- **Developer Owns Code Edits:** The tool suggests fixes when tests fail, but never auto-patches source code. Developer agency and learning are preserved.
- **Max 3 Related Files:** Limits traversal to 3 files to balance deep context with token efficiency (conserving IBM Bob 40-coin budget).
- **CLI Terminal Native:** Developer never has to leave their terminal or copy-paste code into a web browser.
- **Standard `tests/` Directory:** Standardized test location simplifies project structure across Python and Node.

## What We're Building

- CLI command `awam <file...> [--run]`
- Python support (`pytest`) and Node.js support (`jest`)
- Local dependency traversal up to 3 files
- Pre-flight syntax & parameter check
- Unified edge case audit (`[✓]` covered vs `[+]` missing)
- Smart test creation/append in `tests/`
- Test execution and developer fix suggestions with `--run`

## Deferred From the POC

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
