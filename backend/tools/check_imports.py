"""Static check for broken internal imports.

Python only fails on a missing name when the line actually runs, so a typo in
an import or a call to a method that was renamed can survive a syntax check and
reach production. This walks the project's own imports and verifies every
imported name exists in the module it comes from.

Run from the backend directory:

    python tools/check_imports.py
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
PACKAGE_NAME = "app"


def collect_module_names(path: Path) -> set[str]:
    """Top-level names a module exposes to importers."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: set[str] = set()

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            names.update(
                target.id for target in node.targets if isinstance(target, ast.Name)
            )
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
        elif isinstance(node, ast.Import):
            names.update((alias.asname or alias.name.split(".")[0]) for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            names.update((alias.asname or alias.name) for alias in node.names)

    return names


def module_path(dotted_name: str) -> Path | None:
    relative = Path(*dotted_name.split("."))
    for candidate in (PACKAGE_ROOT / relative.with_suffix(".py"), PACKAGE_ROOT / relative / "__init__.py"):
        if candidate.exists():
            return candidate
    return None


def is_subpackage(dotted_name: str, imported: str) -> bool:
    return module_path(f"{dotted_name}.{imported}") is not None


def check_file(path: Path, exports: dict[str, set[str]]) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    problems: list[str] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom) or not node.module:
            continue
        if not node.module.startswith(f"{PACKAGE_NAME}.") and node.module != PACKAGE_NAME:
            continue

        available = exports.get(node.module)
        if available is None:
            problems.append(f"{path.relative_to(PACKAGE_ROOT)}: unknown module '{node.module}'")
            continue

        for alias in node.names:
            if alias.name == "*" or alias.name in available:
                continue
            if is_subpackage(node.module, alias.name):
                continue
            problems.append(
                f"{path.relative_to(PACKAGE_ROOT)}:{node.lineno} "
                f"'{alias.name}' is not defined in {node.module}"
            )

    return problems


def main() -> int:
    package_dir = PACKAGE_ROOT / PACKAGE_NAME
    source_files = sorted(package_dir.rglob("*.py"))

    exports: dict[str, set[str]] = {}
    for path in source_files:
        relative = path.relative_to(PACKAGE_ROOT)
        parts = list(relative.with_suffix("").parts)
        if parts[-1] == "__init__":
            parts.pop()
        exports[".".join(parts)] = collect_module_names(path)

    problems: list[str] = []
    for path in [*source_files, *sorted((PACKAGE_ROOT / "tests").rglob("*.py"))]:
        problems.extend(check_file(path, exports))

    if problems:
        print(f"Broken internal imports ({len(problems)}):")
        for problem in problems:
            print(f"  {problem}")
        return 1

    print(f"Internal imports OK across {len(source_files)} modules.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
