"""Pre-flight lint and syntax sanity checker for awam."""

import ast
from typing import List, Optional, Tuple

class PreflightResult:
    def __init__(self, is_valid: bool, errors: List[str], warnings: List[str]):
        self.is_valid = is_valid
        self.errors = errors
        self.warnings = warnings

def check_syntax(code: str, filename: str = "<source>") -> Tuple[bool, Optional[str], Optional[int]]:
    """Validate Python code syntax using ast.parse before making any API calls.
    
    Returns (is_valid, error_message, line_number).
    """
    try:
        ast.parse(code, filename=filename)
        return True, None, None
    except SyntaxError as e:
        msg = f"Syntax error at line {e.lineno}: {e.msg}"
        if e.text:
            msg += f"\n  --> {e.text.strip()}"
        return False, msg, e.lineno
    except Exception as e:
        return False, f"Unable to parse code: {e}", None

def check_function_signatures(tree: ast.AST) -> List[str]:
    """Scan AST to check for basic internal call signature discrepancies."""
    warnings = []
    function_defs = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Record positional argument count (excluding self/cls)
            args = [a.arg for a in node.args.args if a.arg not in ("self", "cls")]
            min_args = len(args) - len(node.args.defaults)
            max_args = len(args)
            function_defs[node.name] = (min_args, max_args)

    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            fn_name = node.func.id
            if fn_name in function_defs:
                min_args, max_args = function_defs[fn_name]
                call_args_count = len(node.args)
                if call_args_count < min_args or call_args_count > max_args:
                    warnings.append(
                        f"Line {node.lineno}: Function '{fn_name}' expects {min_args}-{max_args} arguments but called with {call_args_count}."
                    )
    return warnings

def run_preflight(code: str, filename: str) -> PreflightResult:
    """Run full pre-flight checks on source code.
    
    Returns PreflightResult with validation status, errors, and warnings.
    """
    is_valid, error, line = check_syntax(code, filename)
    if not is_valid:
        return PreflightResult(is_valid=False, errors=[error], warnings=[])

    try:
        tree = ast.parse(code, filename=filename)
        warnings = check_function_signatures(tree)
        return PreflightResult(is_valid=True, errors=[], warnings=warnings)
    except Exception:
        return PreflightResult(is_valid=True, errors=[], warnings=[])
