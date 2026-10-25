# Awam

> **A developer-first CLI tool for proactive edge case discovery, Socratic testing inquiry, and unit test generation.**

`awam` runs natively inside your project directory from the terminal. Built for developers who struggle with knowing what to test until something breaks, `awam` acts as an **active testing coach**: it inspects your target code and local module dependencies to uncover **"what could go wrong"**—framing edge cases as probing inquiry questions (*"What happens to Y when X fails?"*) so you learn how to think about failure modes.

When you're ready, `awam` can draft ready-to-run tests into your project's `tests/` directory and validate them live with `pytest`, giving actionable fix suggestions if an unhandled edge case fails.

---

## Features

- **Terminal Native:** Runs directly in your CLI where you code—no context switching or copy-pasting code into web chatbots.
- **Socratic Inquiry by Default:** Running `awam <file>` is non-destructive. It presents missing edge cases as thought-provoking questions to build your testing intuition rather than spoon-feeding code.
- **Pre-Flight Sanity Checker:** Scans code locally using Python AST for syntax errors and parameter mismatches in 0.02s before making any API calls—saving API quotas on broken code.
- **Multi-File Context Resolver:** Traverses immediate local module imports (up to 3 files total, e.g. `sample/helper.py` imported by `sample/calculator.py`) to understand real function contracts and helper exceptions.
- **Unified Edge Case Audit:** 
  - `[✓] Already covered`: Instant positive reinforcement confirming what your existing test suite already handles.
  - `[+] Missing gap`: Proactively flags uncovered failure modes with probing Socratic questions.
- **On-Demand Test Generation (`--generate`):** Safely appends missing test functions into `tests/test_<name>.py` while preserving existing tests without duplication.
- **Validation Runner & Fix Advisor (`--run`):** Executes `pytest` live. When a test fails due to a missing error guard, it provides a concise, 2-sentence developer fix suggestion pointing to the source file.
- **Offline / Mock Mode (`--mock`):** Built-in simulation mode allows complete end-to-end evaluation without requiring an API key or consuming quotas.
- **Zero Source Code Mutation:** `awam` writes tests and offers advice—you retain 100% control over your implementation code.
- **Powered by Gemini 3.1 Flash Lite:** Fast structured reasoning with automatic retry and high-demand fallback handling.

---

## Quick Start

### 1. Installation

Clone and install in editable mode:

```bash
git clone https://github.com/<user>/awam.git
cd awam

# Optional but recommended: use a virtual environment
python -m venv .venv
# On Windows: .venv\Scripts\activate
# On Linux/macOS: source .venv/bin/activate

pip install -e .
```

> **Note for Windows users:** If you install globally without a virtual environment and `awam` isn't found in your PATH, you can either add Python's `Scripts/` folder to PATH, or invoke the CLI directly using Python's module syntax: `python -m awam.cli <file>`.

### 2. Configure API Key (Optional)

`awam` includes a built-in `--mock` flag for offline testing. When you're ready to use live model reasoning with **Gemini 3.1 Flash Lite**, configure your free key from [Google AI Studio](https://aistudio.google.com/) or any provider of choice:

```bash
# Bash / Zsh (Git Bash, Linux, macOS)
export GEMINI_API_KEY="your-gemini-api-key"

# PowerShell
$env:GEMINI_API_KEY="your-gemini-api-key"

# Windows CMD
set GEMINI_API_KEY=your-gemini-api-key
```

*(You can also place it in a `.env` file in the project root: `GEMINI_API_KEY=your_key`)*

---

## Usage

### 1. Safe Socratic Inquiry Mode (Default)
```bash
awam sample/calculator.py
# Or offline without API key:
awam sample/calculator.py --mock
```
Non-destructive by default. Displays the **Unified Edge Case Audit** posing questions like:
- *❓ Inquiry: What should `divide(a, 0)` do? Should it raise a `ZeroDivisionError`, return a fallback, or validate upfront?*
- *❓ Inquiry: What happens to the price if `discount_percent` or `price` is negative?*
- *❓ Inquiry: What should `parse_user_scores([])` return? Does it crash on sum/max or return clean default metrics?*

### 2. Generate Missing Tests (`--generate` / `-g`)
```bash
awam sample/calculator.py --generate --mock
```
Writes or cleanly appends generated pytest functions into `tests/test_calculator.py`. Existing tests are preserved without duplicate definitions.

### 3. Run Test Validation & Get Fix Advice (`--run`)
```bash
awam sample/calculator.py --run --mock
```
Executes `pytest` on your test suite. If an edge case fails because your source code lacks an error guard, `awam` presents a **Developer Fix Suggestion** box pinpointing where and what guard to write.

### 4. Generate & Run in One Command
```bash
awam sample/calculator.py --generate --run --mock
```
Generates missing tests and immediately runs pytest to validate them.

### 5. Preview Generated Tests Without Writing (`--audit-only`)
```bash
awam sample/calculator.py --audit-only --mock
```
Displays a syntax-highlighted preview of the test code that `awam` would generate without modifying any files on disk.

### 6. Verbose Diagnostics (`--verbose`)
```bash
awam sample/calculator.py --verbose --mock
```
Displays diagnostic metadata in the footer: analyzed files, target test file destination, model name (`gemini-3.1-flash-lite`), and latency.

---

## 📂 Project Structure

```
devpost-challenge/
├── awam/                     # Core CLI package
│   ├── __init__.py           # Package version (0.1.0)
│   ├── cli.py                # Click CLI entrypoint & options (--generate, --run, --mock)
│   ├── analyzer.py           # Pre-flight syntax validation & AST checks
│   ├── resolver.py           # Local import traversal (max 3 files)
│   ├── engine.py             # Gemini 3.1 Flash Lite client, Pydantic schemas & Socratic prompts
│   ├── test_manager.py       # Smart discovery & non-duplicating test appending in tests/
│   ├── runner.py             # Subprocess pytest runner & developer fix advisor
│   └── reporter.py           # Rich terminal UI, tables, panels & UTF-8 Windows handling
├── sample/                   # Demo sample files
│   ├── calculator.py         # Primary sample source file
│   └── helper.py             # Local dependency imported by calculator.py
├── tests/                    # Project tests managed by awam
│   └── test_calculator.py
├── devpost/                  # Hackathon planning artifacts
│   ├── scope.md              # Project scope & boundary
│   ├── prd.md                # Product requirements
│   ├── spec.md               # Technical specification
│   ├── checklist.md          # Slices and verification checklist
│   └── app-map.html          # Standalone visual architecture & learning map
├── pyproject.toml            # Packaging & CLI entrypoint configuration
├── requirements.txt          # Python dependencies
└── README.md
```

---

## 🧪 Quick Walkthrough Demo

Try the complete flow in under 60 seconds:

```bash
# Step 1: Discover edge cases with Socratic inquiries (zero disk writes)
awam sample/calculator.py --mock

# Step 2: Generate the tests into tests/test_calculator.py
awam sample/calculator.py --generate --mock

# Step 3: Run pytest live and verify the results
awam sample/calculator.py --run --mock
```
