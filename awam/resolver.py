"""Multi-file context and local dependency resolver for awam (max 3 files total)."""

import os
import ast
from typing import Dict, List, Optional, Set

def extract_imported_names(code: str) -> Set[str]:
    """Parse AST to extract names of imported modules."""
    imported = set()
    try:
        tree = ast.parse(code)
    except Exception:
        return imported

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported.add(node.module.split(".")[0])
            elif node.level and node.level > 0:
                # Relative import
                for alias in node.names:
                    imported.add(alias.name)
    return imported

def find_local_dependency(module_name: str, search_dirs: List[str]) -> Optional[str]:
    """Locate local .py file for a module name in search directories."""
    candidates = [
        f"{module_name}.py",
        os.path.join(module_name, "__init__.py"),
    ]

    for d in search_dirs:
        for candidate in candidates:
            path = os.path.join(d, candidate)
            if os.path.isfile(path):
                return os.path.normpath(path)
    return None

def resolve_dependencies(primary_file: str, max_helper_files: int = 2) -> Dict[str, str]:
    """Scan primary file for local module imports and return their paths and contents.
    
    Capped at max_helper_files (default 2, ensuring max 3 files total analyzed).
    Ignores external third-party and standard library packages.
    """
    if not os.path.isfile(primary_file):
        return {}

    try:
        with open(primary_file, "r", encoding="utf-8") as f:
            primary_code = f.read()
    except Exception:
        return {}

    imported_modules = extract_imported_names(primary_code)
    
    primary_dir = os.path.dirname(primary_file) or "."
    search_dirs = [primary_dir, "."]

    resolved_files: Dict[str, str] = {}
    norm_primary = os.path.normpath(primary_file)

    for mod in imported_modules:
        if len(resolved_files) >= max_helper_files:
            break

        dep_path = find_local_dependency(mod, search_dirs)
        if dep_path and dep_path != norm_primary and dep_path not in resolved_files:
            try:
                with open(dep_path, "r", encoding="utf-8") as f:
                    resolved_files[dep_path] = f.read()
            except Exception:
                continue

    return resolved_files
