---
doc: checklist
status: approved
---

# Build Checklist

Build mode: learn

## Slices

- [ ] **1. CLI scaffold and core AI edge case audit engine (`awam <file> --audit-only`)**
  Becomes usable: Running `awam <file> --audit-only` inspects a Python file, calls Gemini Flash to uncover "what could go wrong" edge cases, and prints a color-coded audit table directly in the terminal without touching files on disk.
  Why now: Proves the whole stack and the unique AI kernel on day one—project structure, CLI invocation, Gemini API integration, and Rich terminal output—before dealing with file mutation, dependency resolution, or subprocess test runners.
  PRD ref: `prd.md > The Core Journey` (steps 1, 5, 7), `prd.md > 3. Unified Edge Case Audit & Developer Reinforcement`
  Spec ref: `spec.md > Components > CLI Entrypoint (awam.cli)`, `spec.md > Components > AI Analysis & Audit Engine (awam.engine)`, `spec.md > Components > Terminal UI & Reporter (awam.reporter)`
  Build: Scaffold the package (`pyproject.toml`, `requirements.txt`, `awam/__init__.py`), create `awam/cli.py` with Click, `awam/engine.py` using `google-genai` for structured JSON edge case audit and test code generation, `awam/reporter.py` with `rich` for colored terminal tables and banners, and create a `sample/calculator.py` file with sample logic and edge cases.
  Verify (mechanical): Run `python -m awam.cli sample/calculator.py --audit-only` and confirm exit code 0, formatted Rich edge case audit output (`[✓]` vs `[+]`), and generated test code preview in stdout.
  Learner check: Run `awam sample/calculator.py --audit-only` in your terminal and see if the color-coded edge case audit output clearly highlights what could go wrong.
  Commit: `Scaffold CLI and build core AI edge case audit engine`

- [ ] **2. Smart test file discovery and appending in `tests/`**
  Becomes usable: Running `awam <file>` writes or appends the missing unit tests into `tests/test_<name>.py` (creating `tests/` and test file if absent, or preserving existing tests and appending if present), respecting `--output`.
  Why now: Connects the audit engine to actual filesystem persistence, enabling the test-driven reality check where generated tests become real test files in the project.
  PRD ref: `prd.md > The Core Journey` (step 6), `prd.md > 4. Smart Test File Management in tests/`
  Spec ref: `spec.md > Components > Smart Test File Manager (awam.test_manager)`
  Build: Implement `awam/test_manager.py` to discover existing test files in `tests/`, parse existing test functions so existing tests are fed into the Gemini audit prompt, and safely append only new tests without overwriting existing tests.
  Verify (mechanical): Run `python -m awam.cli sample/calculator.py`, verify `tests/test_calculator.py` is created with valid Python syntax, run again with an existing test and confirm new tests append without duplicating or overwriting.
  Learner check: Run `awam sample/calculator.py` and inspect `tests/test_calculator.py` to see the generated test cases ready to run.
  Commit: `Add smart test file discovery and appending in tests directory`

- [ ] **3. Pre-flight syntax checker and local import resolver**
  Becomes usable: `awam` catches syntax errors locally before calling the API, and automatically inspects up to 2 local imported files (e.g. `sample/helper.py` imported by `sample/calculator.py`) so edge cases across contracts and helper exceptions are caught.
  Why now: Prevents wasted API calls on broken syntax and expands context from single-file isolation to real-world multi-file local dependencies without blowing token budgets.
  PRD ref: `prd.md > 1. Pre-Flight Lint & Syntax Sanity Check`, `prd.md > 2. Multi-File Context Analysis (Max 3 Files)`
  Spec ref: `spec.md > Components > Pre-Flight Lint & Syntax Checker (awam.analyzer)`, `spec.md > Components > Multi-File Context Resolver (awam.resolver)`
  Build: Implement `awam/analyzer.py` using Python `ast.parse` for instant syntax/argument checks; implement `awam/resolver.py` to scan AST `Import` and `ImportFrom` nodes, resolve relative/local `.py` files in the same directory tree (up to 3 files total), and feed combined context into `engine.py`.
  Verify (mechanical): Run pre-flight check on a syntax-broken file to verify clean local error reporting with line number; run `awam sample/calculator.py` where `calculator.py` imports `sample/helper.py` and verify both files appear in analysis and test mocks/contract edge cases are generated.
  Learner check: Check that `awam` catches a deliberate syntax typo instantly, then resolves `helper.py` when analyzing `calculator.py`.
  Commit: `Add pre-flight syntax checker and local import resolver`

- [ ] **4. Test runner execution and developer fix advisor (`--run`)**
  Becomes usable: Passing `--run` invokes `pytest` on the generated test file; if tests pass, prints a green success banner; if an unhandled edge case test fails, captures the error and displays a 2-sentence developer fix suggestion pointing to the source file.
  Why now: Completes the full feedback loop of the core journey—validating the tests immediately and giving developer-led guidance to fix the source code.
  PRD ref: `prd.md > The Core Journey` (step 8), `prd.md > 5. Validation Runner & Developer-Led Fix Suggestions (--run)`
  Spec ref: `spec.md > Components > Validation Runner & Fix Advisor (awam.runner)`, `spec.md > Important Failure Modes`
  Build: Implement `awam/runner.py` to execute `pytest` via `subprocess.run`, capture stdout/stderr, and call Gemini Flash for targeted fix suggestions when a test fails; wire up `--verbose` diagnostics footer (`reporter.py`).
  Verify (mechanical): Run `python -m awam.cli sample/calculator.py --run`, verify `pytest` executes via subprocess, and test failure triggers the fix advisor output without mutating source code.
  Learner check: Run `awam sample/calculator.py --run` to see your tests run live, exposing any unhandled edge case with an actionable fix suggestion.
  Commit: `Add test runner execution and developer fix advisor on test failure`

## Hands-on Checkpoints

- [ ] Early usable behavior explored — Slice 1 (`awam sample/calculator.py --audit-only`)
- [ ] Final kick-the-tires exploration and feedback completed — Slice 4 (`awam sample/calculator.py --run`)

## Final Review

- [ ] Final review complete — feedback resolved and learner confirms ready to ship

## Code Tour and App Map

- [ ] Learning activity complete — guided route, focused alternative, prior practice connected, or brief recap
- [ ] Optional edit and transfer reflection addressed — offered/declined/already covered/not applicable as appropriate
- [ ] `devpost/app-map.html` generated from finished code, checked, and shown, including a project-grounded practice to reuse

Activity and evidence: [what actually happened; real document/test/code references; unfinished work if interrupted]
Route and stops: [actual paths and symbols; guided stops completed, or reference-only route]
Edit outcome: [tried/kept/reverted/declined/not applicable; verification if changed]
Reflection: [offered/answered/declined/already covered — personal answer belongs only in the ignored profile]
Activity mode: [live app and editor, explicit static fallback, focused alternative, prior practice, or recap]

## Revisions

- Updated default Gemini model to `gemini-3.8-flash` — upgraded from deprecated model references across engine, reporter, and spec.
