---
doc: scope
status: approved
---

# awam

A developer-first CLI tool that analyzes code directly in your project directory, spots "what could go wrong" coverage gaps before things break, and writes ready-to-run unit tests straight into your test files.

## The Unique Kernel
Unlike browser-based AI chatbots that require developers to manually copy and paste code back and forth, `awam` runs natively inside your project directory from the terminal. It inspects your target code and traverses its local imports (e.g. reading `grow.py` when analyzing `app.py`) to understand what the code actually depends on. 

It looks at the system through the proactive lens of *"what could go wrong before something breaks in production?"*—flagging missing error guards, unhandled exceptions, boundary conditions, and mock needs. By generating tests for these missing paths, it acts as a test-driven reality check: if an error path isn't implemented yet, the generated test highlights the exact fix needed. `awam` writes or appends these tests into the project's standard `tests/` directory with an optional `--run` flag to validate them immediately.

## Who It's For
A software developer (like the learner) who writes code across languages (such as Python and Node), struggles with knowing what edge cases to write tests for until bugs appear in production, and wants a fast, friction-free tool that works right where they code without leaving the terminal.

## The Core Loop
1. Developer writes or updates a code file in their repository.
2. In the terminal, they run `awam <file>` (or `awam <file> --run`).
3. `awam` detects the language, traverses local module imports to understand dependencies and contracts, and inspects existing tests in the `tests/` directory.
4. It identifies unhandled edge cases and missing error paths, generating unit tests that test both happy paths and failure guards.
5. It writes or appends these tests into `tests/test_<filename>`, creating the file if it doesn't already exist.
6. If `--run` is passed, `awam` immediately executes the test suite and displays pass/fail status in the terminal.
7. The developer sees passing tests for existing behavior and failing/exposed edge cases to fix in their source code.

## Inspiration & Identity
- **Vibe:** Pragmatic, snappy developer tool. Clean terminal feedback that highlights edge cases clearly without noisy clutter.
- **Context:** Aligned with the IBM Bob 2.0 Hackathon automated testing hub track, built to be highly intentional with AI calls (conserving the 40-Bobcoin budget) and designed to run directly in the developer's local workflow.

## Why This Matters to the Learner
*"Most times I don't know what to test till something breaks."* It directly solves a real, daily struggle by serving as a proactive safety net right in the terminal, while also giving the learner practice with agentic workflows in a project they will use immediately.

## What "Working" Looks Like
In a demo terminal, the user runs `awam src/app.py --run` on a file that imports a local `grow.py`. `awam` outputs the detected language, shows that it resolved the local dependency, lists 3 specific edge cases spotted (e.g. unhandled error path when `grow.py` returns null/raises an exception), appends the tests into `tests/test_app.py`, executes the test runner (`pytest` or `jest`), and shows the test output. The whole flow demonstrates complete end-to-end utility in under 60 seconds.

## The POC Boundary
- **Terminal CLI:** Single command `awam` executed in the project directory (no copy-pasting code).
- **Configurable Multi-Language Support:** Architected to detect file type/config, with out-of-the-box support for Python (`pytest`) and Node.js (`jest`/native test runner).
- **Local Dependency Traversal:** Traverses immediate local module imports (e.g. `import grow`) to understand function contracts and mock needs.
- **Standard `tests/` Management:** Locates and manages tests under a standard `tests/` directory (creates `tests/test_<name>` if absent, or appends if present).
- **"What Could Go Wrong" Edge Case & Error Path Detection:** Highlights missing error guards and boundary cases through runnable test specifications.
- **Validation Flag (`--run`):** Optional flag allowing the user to decide whether to automatically execute the test runner immediately.

## Later
- Deep multi-level dependency graph resolution across entire packages.
- Additional language modules (Java / JUnit, Go, Rust).
- Whole-repository scan mode (`awam scan --all`).
- Git integration (`awam --diff` to scan only git staged files before commit).
- Interactive mode to pick and choose specific proposed test cases.

## Explicitly Cut
- **Web UI / Browser Interface:** Cut because developers don't want to copy-paste code or context-switch away from their editor and terminal.
- **Automatic Code Refactoring / Auto-Patching Source Code:** Cut for the PoC. `awam` writes the tests to expose gaps; fixing the implementation code remains in the developer's hands.
- **Automatic Git Commits / PR Creation:** Cut to keep the developer in full control of what code enters version control.
