---
doc: scope
status: approved
---

# awam

A developer-first CLI tool that analyzes code directly in your project directory, spots "what could go wrong" coverage gaps before things break, poses Socratic inquiry questions to build testing intuition, and writes ready-to-run unit tests straight into your test files.

## The Unique Kernel
Unlike browser-based AI chatbots that require developers to manually copy and paste code back and forth, `awam` runs natively inside your project directory from the terminal. It inspects your target code and traverses its local imports (e.g. reading `helper.py` when analyzing `calculator.py`) to understand what the code actually depends on. 

It looks at the system through the proactive lens of *"what could go wrong before something breaks in production?"*—flagging missing error guards, unhandled exceptions, boundary conditions, and mock needs. By default, it presents these risks as probing Socratic inquiries (*"What happens to Y when X fails?"*) so developers learn how to anticipate failure modes. When desired, `--generate` writes or appends these tests into the project's standard `tests/` directory with an optional `--run` flag to validate them immediately with `pytest`.

## Who It's For
A software developer (like the learner) who writes Python code, struggles with knowing what edge cases to write tests for until bugs appear in production, and wants a fast, friction-free tool that works right where they code without leaving the terminal.

## The Core Loop
1. Developer writes or updates a Python code file in their repository.
2. In the terminal, they run `awam <file>` (safe inquiry mode) to explore candidate edge cases.
3. `awam` runs local AST pre-flight checks, traverses local module imports to understand dependencies and contracts, and inspects existing tests in the `tests/` directory.
4. It displays the **Unified Edge Case Audit** featuring probing questions on unhandled edge cases alongside green checkmarks for already covered behavior.
5. If the developer runs `awam <file> --generate`, it writes or appends ready-to-run tests into `tests/test_<filename>`, preserving existing tests without duplication.
6. If `--run` is passed, `awam` executes `pytest` and displays pass/fail status in the terminal with developer fix advice on failure.

## Inspiration & Identity
- **Vibe:** Pragmatic, snappy developer tool and active testing coach. Clean terminal feedback that highlights edge cases clearly without noisy clutter.
- **Context:** Built to be highly intentional with AI calls and designed to run directly in the developer's local workflow.

## Why This Matters to the Learner
*"Most times I don't know what to test till something breaks."* It directly solves a real, daily struggle by serving as a proactive safety net right in the terminal, while also giving the learner practice with agentic workflows in a project they will use immediately.

## What "Working" Looks Like
In a demo terminal, the user runs `awam sample/calculator.py` on a file that imports a local `helper.py`. `awam` runs local pre-flight checks, resolves the local dependency, lists specific edge cases with Socratic inquiry questions (e.g. unhandled ZeroDivisionError or negative prices), allows generating tests via `--generate`, executes `pytest` via `--run`, and shows actionable fix guidance if an unhandled edge case fails. The whole flow demonstrates complete end-to-end utility in under 60 seconds.

## The POC Boundary
- **Terminal CLI:** Single command `awam` executed in the project directory (no copy-pasting code).
- **Focused Python (`pytest`) Support:** Native Python AST pre-flight checks, local dependency resolution, and `pytest` execution. Node.js (`jest`/`node:test`) is deferred to `## Later`.
- **Local Dependency Traversal:** Traverses immediate local module imports (e.g. `import helper`) up to 3 files total to understand function contracts and mock needs.
- **Safe Socratic Inquiry by Default:** Running `awam <file>` poses "what happens when..." questions without modifying disk.
- **On-Demand Test Generation (`--generate`):** Locates and manages tests under a standard `tests/` directory (creates `tests/test_<name>.py` if absent, or appends if present without duplicating).
- **Validation Runner & Fix Advisor (`--run`):** Executes `pytest` live and provides 2-sentence developer-led fix suggestions on failure.
- **Offline Simulation (`--mock`):** Enables offline testing without burning Gemini API limits or requiring environment variables.

### CLI Flags in the POC
| Flag / Tag | Default | Purpose & What It Does |
|---|---|---|
| `awam <file>` | *(Required)* | **Default Socratic Inquiry Mode:** Runs AST pre-flight checks, resolves local imports, and displays the Unified Edge Case Audit with probing questions (*"What happens to Y when X fails?"*). Modifies zero files on disk. |
| `--generate` / `-g` | `False` | **On-Demand Test Writer:** Appends runnable pytest test functions covering identified missing edge cases into `tests/test_<name>.py` without touching existing tests. |
| `--run` | `False` | **Validation Test Runner:** Executes `pytest` via subprocess. If tests fail, captures traceback and generates a concise 2-sentence developer fix suggestion without mutating source code. |
| `--mock` / `--demo` | `False` | **Offline Simulation Mode:** Bypasses Gemini API calls entirely, using fast local heuristic analysis for zero-quota testing, instant demos, and environments without an API key. |
| `--audit-only` | `False` | **Syntax Preview Mode:** Displays a syntax-highlighted preview of the generated test code in the terminal without writing anything to disk. |
| `--verbose` | `False` | **Telemetry & Diagnostics:** Prints diagnostic metadata (files resolved, external packages mocked, test target file, LLM model, token counts, latency) in a clean footer. |
| `--output <path>` | `tests/test_<name>.py` | **Custom Destination:** Specifies a custom output file path for generated tests instead of standard `tests/test_<name>.py`. |

## Later
- Node.js (`jest` / `node:test`) and multi-language support.
- Deep multi-level dependency graph resolution across entire packages.
- Additional language modules (Java / JUnit, Go, Rust).
- Whole-repository scan mode (`awam scan --all`).
- Git integration (`awam --diff` to scan only git staged files before commit).
- Interactive mode to pick and choose specific proposed test cases.

## Explicitly Cut
- **Web UI / Browser Interface:** Cut because developers don't want to copy-paste code or context-switch away from their editor and terminal.
- **Automatic Code Refactoring / Auto-Patching Source Code:** Cut for the PoC. `awam` writes tests and offers advice; fixing the implementation code remains in the developer's hands.
- **Automatic Git Commits / PR Creation:** Cut to keep the developer in full control of what code enters version control.
