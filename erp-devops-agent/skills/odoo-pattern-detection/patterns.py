from __future__ import annotations

import ast
from dataclasses import dataclass


@dataclass
class Finding:
    file: str
    line: int
    severity: str
    code_snippet: str
    fix: str


def classify_files(paths: list[str]) -> dict[str, list[str]]:
    return {
        "python_files": [path for path in paths if path.endswith(".py")],
        "xml_files": [path for path in paths if path.endswith(".xml")],
        "other_files": [path for path in paths if not path.endswith((".py", ".xml"))],
    }


def parse_python(source: str) -> ast.AST | None:
    try:
        return ast.parse(source)
    except SyntaxError:
        return None
