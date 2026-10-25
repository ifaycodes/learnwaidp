"""Smart test file manager for awam: discovery, creation, and appending in tests/."""

import os
import ast
import re
from typing import List, Optional, Tuple

def resolve_test_file(primary_file: str, custom_output: Optional[str] = None) -> str:
    """Determine destination test file path.
    
    Defaults to tests/test_<basename>.py or honors custom_output.
    """
    if custom_output:
        return custom_output

    base_name = os.path.splitext(os.path.basename(primary_file))[0]
    
    # Check if primary file has a sibling tests/ directory (e.g. sample/tests/)
    parent_dir = os.path.dirname(primary_file)
    sibling_tests = os.path.join(parent_dir, "tests", f"test_{base_name}.py")
    if os.path.exists(sibling_tests):
        return sibling_tests

    # Standard top-level tests/ directory
    return os.path.join("tests", f"test_{base_name}.py")

def read_existing_tests(test_file_path: str) -> str:
    """Read existing test file content if present."""
    if os.path.exists(test_file_path):
        try:
            with open(test_file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return ""
    return ""

def extract_test_names(test_code: str) -> List[str]:
    """Parse test code AST to extract function names starting with 'test_'."""
    if not test_code.strip():
        return []
    try:
        tree = ast.parse(test_code)
        names = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                names.append(node.name)
        return names
    except Exception:
        # Fallback to regex
        return re.findall(r"def\s+(test_\w+)\s*\(", test_code)

def split_test_functions(generated_tests: str) -> Tuple[List[str], List[Tuple[str, str]]]:
    """Split generated test code into import lines and individual test function blocks.
    
    Returns (import_lines, [(func_name, func_code), ...]).
    """
    imports = []
    tests = []
    
    try:
        tree = ast.parse(generated_tests)
        lines = generated_tests.splitlines()
        
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imp_str = ast.get_source_segment(generated_tests, node)
                if imp_str:
                    imports.append(imp_str.strip())
            elif isinstance(node, ast.FunctionDef):
                fn_str = ast.get_source_segment(generated_tests, node)
                if fn_str:
                    tests.append((node.name, fn_str.strip()))
        return imports, tests
    except Exception:
        # Regex-based fallback
        current_fn = None
        current_lines = []
        for line in generated_tests.splitlines():
            if line.startswith("import ") or line.startswith("from "):
                imports.append(line.strip())
            elif line.startswith("def test_"):
                if current_fn:
                    tests.append((current_fn, "\n".join(current_lines).strip()))
                    current_lines = []
                match = re.match(r"def\s+(test_\w+)", line)
                current_fn = match.group(1) if match else "test_unnamed"
                current_lines.append(line)
            elif current_fn:
                current_lines.append(line)
        if current_fn and current_lines:
            tests.append((current_fn, "\n".join(current_lines).strip()))
        return imports, tests

def write_or_append_tests(
    test_file_path: str,
    generated_tests: str,
    source_file: Optional[str] = None,
) -> Tuple[int, bool]:
    """Write new test file or append tests cleanly to existing test file.
    
    Returns (count_of_tests_written, was_created).
    """
    if not generated_tests.strip():
        return 0, False

    imports, test_blocks = split_test_functions(generated_tests)
    if not test_blocks:
        return 0, False

    os.makedirs(os.path.dirname(test_file_path) or ".", exist_ok=True)

    if not os.path.exists(test_file_path):
        # Create new test file
        header = f'"""Unit tests generated and audited by awam for {source_file or "source code"}."""\n\n'
        content = header + generated_tests.strip() + "\n"
        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return len(test_blocks), True

    # Existing file: append only new tests
    existing_content = read_existing_tests(test_file_path)
    existing_names = set(extract_test_names(existing_content))

    new_blocks = [block for name, block in test_blocks if name not in existing_names]
    if not new_blocks:
        return 0, False

    # Check for missing imports
    needed_imports = []
    for imp in imports:
        if imp not in existing_content:
            needed_imports.append(imp)

    append_parts = []
    if needed_imports:
        append_parts.append("\n".join(needed_imports))

    append_parts.append("\n# --- Edge cases identified by awam ---")
    append_parts.extend(new_blocks)

    separator = "\n\n" if not existing_content.endswith("\n\n") else ""
    updated_content = existing_content.rstrip() + separator + "\n\n" + "\n\n".join(append_parts) + "\n"

    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write(updated_content)

    return len(new_blocks), False
