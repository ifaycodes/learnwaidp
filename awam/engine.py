"""AI analysis and audit engine using Google Gemini Flash."""

import os
import time
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from typing_extensions import Literal

try:
    from dotenv import load_dotenv
    load_dotenv()
    # Also attempt loading from home directory ~/.env if not already set
    home_env = os.path.expanduser("~/.env")
    if os.path.exists(home_env):
        load_dotenv(home_env)
except ImportError:
    pass

class GeminiKeyMissingError(Exception):
    """Raised when GEMINI_API_KEY is not configured."""
    pass

class EdgeCaseAuditItem(BaseModel):
    scenario: str = Field(description="Description of the edge case or boundary condition")
    status: Literal["covered", "missing"] = Field(description="Whether an existing test covers this case")
    matched_test: Optional[str] = Field(default=None, description="Name of existing test function that covers this case")
    reason: str = Field(description="Why this case is a critical risk, or how existing test verifies it")

class AnalysisResponse(BaseModel):
    candidate_cases: List[EdgeCaseAuditItem] = Field(description="List of all candidate edge cases evaluated")
    generated_tests: str = Field(description="Runnable pytest test functions covering ONLY the missing edge cases")
    imports_needed: List[str] = Field(default_factory=list, description="Imports or mocks needed for generated tests")

class FixSuggestion(BaseModel):
    error_summary: str = Field(description="Summary of the failed test assertion")
    suggested_guard: str = Field(description="1-2 sentence developer guidance on what error guard or check to add")
    target_file: str = Field(description="Source file where the guard should be placed")

def get_api_key() -> Optional[str]:
    """Retrieve Gemini API key from environment."""
    return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

def _generate_mock_analysis(
    target_filename: str,
    source_code: str,
    existing_tests: str = "",
) -> AnalysisResponse:
    """Generate high-fidelity heuristic edge cases for offline verification and testing."""
    base_name = os.path.splitext(os.path.basename(target_filename))[0]
    
    # Check if existing tests cover basic happy path
    has_happy_test = "test_" in existing_tests and "happy" in existing_tests.lower()
    
    candidate_cases = [
        EdgeCaseAuditItem(
            scenario=f"Standard valid input execution for {base_name}",
            status="covered" if has_happy_test else "missing",
            matched_test="test_happy_path" if has_happy_test else None,
            reason="Basic valid input computation handled by existing tests." if has_happy_test else "Baseline happy path validation."
        ),
        EdgeCaseAuditItem(
            scenario="Division by zero or denominator boundary condition",
            status="missing",
            matched_test=None,
            reason="Unchecked zero denominator triggers unhandled ZeroDivisionError in production."
        ),
        EdgeCaseAuditItem(
            scenario="Negative numeric argument or boundary discount value",
            status="missing",
            matched_test=None,
            reason="Negative inputs may bypass business rule validations or corrupt pricing data."
        ),
        EdgeCaseAuditItem(
            scenario="Empty collection or empty list payload",
            status="missing",
            matched_test=None,
            reason="Passing an empty list triggers ZeroDivisionError or IndexError on aggregations."
        ),
    ]

    generated_tests = f'''import pytest
from {base_name} import divide, calculate_discount, parse_user_scores

def test_divide_by_zero():
    """Verify divide raises ZeroDivisionError when denominator is zero."""
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

def test_calculate_discount_negative_price():
    """Verify calculate_discount handles negative price boundary."""
    # This exposes missing validation in source code
    result = calculate_discount(-50.0, 10.0)
    assert result <= 0

def test_parse_user_scores_empty_list():
    """Verify parse_user_scores behavior with empty score collection."""
    with pytest.raises((ZeroDivisionError, ValueError)):
        parse_user_scores([])
'''
    return AnalysisResponse(
        candidate_cases=candidate_cases,
        generated_tests=generated_tests,
        imports_needed=["import pytest"],
    )

def analyze_code(
    target_filename: str,
    source_code: str,
    dependency_files: Optional[Dict[str, str]] = None,
    existing_tests: str = "",
    model_name: str = "gemini-3.8-flash",
) -> tuple[AnalysisResponse, float]:
    """Run proactive edge case audit and test generation via Gemini Flash.
    
    Returns (AnalysisResponse, latency_seconds).
    """
    model_name = os.getenv("GEMINI_MODEL", model_name)
    api_key = get_api_key()
    allow_mock = os.getenv("AWAM_MOCK", "").lower() in ("1", "true", "yes")
    if allow_mock:
        start_time = time.time()
        res = _generate_mock_analysis(target_filename, source_code, existing_tests)
        return res, time.time() - start_time, f"simulation/{model_name}"

    api_key = get_api_key()
    if not api_key:
        raise GeminiKeyMissingError(
            "GEMINI_API_KEY environment variable is not set.\n"
            "Get a free API key at https://aistudio.google.com/ and set it with:\n"
            "  set GEMINI_API_KEY=your_key  (Windows CMD)\n"
            "  $env:GEMINI_API_KEY='your_key'  (PowerShell)\n"
            "  export GEMINI_API_KEY=your_key  (Bash)\n"
            "or add it to your .env file."
        )

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    # Build prompt with source code, dependencies, and existing tests
    dep_context = ""
    if dependency_files:
        dep_context = "\n\n### Local Imported Files:\n"
        for fname, fcontent in dependency_files.items():
            dep_context += f"--- File: {fname} ---\n{fcontent}\n\n"

    existing_context = existing_tests.strip() if existing_tests else "(No existing test file found)"

    prompt = f"""You are `awam`, an expert automated test strategist and developer peer.
Your mission is proactive edge case detection: identifying "what could go wrong" before code breaks in production.

Analyze the target file and any local dependencies below.

### Target Source File: {target_filename}
```python
{source_code}
```
{dep_context}

### Existing Test Suite:
```python
{existing_context}
```

Instructions:
1. Identify 3 to 6 critical candidate edge cases (e.g. unhandled exceptions, None/null inputs, empty collections, zero values, negative values, boundary conditions, or helper exceptions).
2. For each candidate case, evaluate if it is ALREADY covered by the existing test suite:
   - If covered: set `status="covered"`, specify `matched_test` (the test function name), and provide a positive reinforcement note in `reason`.
   - If not covered: set `status="missing"`, set `matched_test=None`, and describe why it is a critical production risk in `reason`.
3. In `generated_tests`, generate CLEAN, READY-TO-RUN pytest test functions covering ONLY the missing edge cases.
   - Do NOT duplicate tests for cases that are already covered.
   - Include clear docstrings explaining what edge case is tested.
   - Use standard pytest idioms (e.g. `with pytest.raises(...)`).
   - Import the target functions properly.
"""

    start_time = time.time()
    models_to_try = [model_name]
    if model_name == "gemini-3.8-flash":
        models_to_try.append("gemini-3.1-flash-lite")

    response = None
    used_model = model_name
    last_error = None

    for m in models_to_try:
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model=m,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=AnalysisResponse,
                        temperature=0.2,
                    ),
                )
                used_model = m
                break
            except Exception as e:
                last_error = e
                err_msg = str(e)
                if ("503" in err_msg or "429" in err_msg or "UNAVAILABLE" in err_msg) and attempt < max_retries - 1:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                if m != models_to_try[-1] and ("503" in err_msg or "UNAVAILABLE" in err_msg):
                    # Fallback to secondary model if primary experiences high demand
                    break
                if m == models_to_try[-1]:
                    raise

        if response:
            break

    if not response and last_error:
        raise last_error

    latency = time.time() - start_time

    if hasattr(response, "parsed") and response.parsed:
        return response.parsed, latency, used_model

    # Fallback to direct json validation
    import json
    data = json.loads(response.text)
    return AnalysisResponse.model_validate(data), latency, used_model
