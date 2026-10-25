"""Test validation runner and developer fix advisor for awam."""

import sys
import subprocess
import os
import re
from typing import Tuple, Optional
from pydantic import BaseModel, Field

class FixSuggestion(BaseModel):
    error_summary: str = Field(description="Summary of the failing test condition")
    suggested_guard: str = Field(description="1-2 sentence actionable suggestion on what guard to add in source code")
    target_file: str = Field(description="Source file path where the fix belongs")

def execute_pytest(test_file_path: str) -> Tuple[int, str]:
    """Execute pytest against the target test file via subprocess.
    
    Returns (returncode, runner_output).
    """
    if not os.path.isfile(test_file_path):
        return 1, f"Test file not found: {test_file_path}"

    cmd = [sys.executable, "-m", "pytest", test_file_path, "-v", "--no-header"]
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
        return proc.returncode, proc.stdout
    except FileNotFoundError:
        return 127, "pytest not found in the current Python environment. Install with 'pip install pytest' or omit --run."
    except subprocess.TimeoutExpired:
        return 124, "pytest execution timed out after 30 seconds."
    except Exception as e:
        return 1, f"Failed to execute pytest: {e}"

def generate_heuristic_fix(test_output: str, source_file: str) -> FixSuggestion:
    """Generate a clean developer fix suggestion offline."""
    # Look for failed test name in output
    failed_match = re.search(r"FAILED\s+[^\s:]+::(\w+)", test_output)
    failed_test = failed_match.group(1) if failed_match else "unhandled edge case"

    if "negative_price" in failed_test:
        guard = f"In {source_file}, add `if price < 0: raise ValueError('Price cannot be negative')` at the beginning of `calculate_discount`."
        summary = "Assertion failed: calculate_discount allowed negative price without validation."
    elif "negative_discount" in failed_test:
        guard = f"In {source_file}, add `if discount_percent < 0: raise ValueError('Discount cannot be negative')`."
        summary = "Assertion failed: calculate_discount accepted negative discount percent."
    elif "zero" in failed_test:
        guard = f"In {source_file}, check `if b == 0: raise ZeroDivisionError('Denominator cannot be zero')` or add defensive input handling."
        summary = "ZeroDivisionError encountered during execution."
    elif "tax" in failed_test or "region" in failed_test:
        guard = f"In {source_file}, wrap `helper.get_tax_multiplier(region)` in a `try...except KeyError:` block or validate region codes upfront."
        summary = "KeyError exposed when helper function received unexpected region code."
    else:
        guard = f"In {source_file}, add defensive error guards or input validation checks before calculating results."
        summary = f"Failing condition in `{failed_test}`: unhandled boundary case in source code."

    return FixSuggestion(
        error_summary=summary,
        suggested_guard=guard,
        target_file=source_file,
    )

def suggest_fix(
    test_output: str,
    source_file: str,
    model_name: str = "gemini-3.1-flash-lite",
) -> FixSuggestion:
    """Ask Gemini Flash for a concise 2-sentence developer fix suggestion, or use heuristic."""
    allow_mock = os.getenv("AWAM_MOCK", "").lower() in ("1", "true", "yes")
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    if allow_mock or not api_key:
        return generate_heuristic_fix(test_output, source_file)

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        prompt = f"""You are `awam` developer assistant.
A newly generated edge case test failed when executed against `{source_file}`.
The test exposed an unhandled error path or missing input guard in the developer's source code.

Test Runner Output:
```
{test_output[-1500:]}
```

Instructions:
1. Identify the exact failing condition.
2. In `suggested_guard`, provide a concise 1-2 sentence suggestion telling the developer where and what guard to write in `{source_file}` (e.g. `In src/app.py:12, add if price < 0: raise ValueError(...)`).
3. awam NEVER modifies source code automatically; the developer will implement your advice.
"""
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=FixSuggestion,
                temperature=0.2,
            ),
        )
        if hasattr(response, "parsed") and response.parsed:
            return response.parsed
        import json
        return FixSuggestion.model_validate(json.loads(response.text))
    except Exception:
        return generate_heuristic_fix(test_output, source_file)
