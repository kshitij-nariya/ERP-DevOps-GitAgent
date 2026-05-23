from __future__ import annotations

import re
from collections import Counter
from typing import Any

from lxml import etree


def _line_snippet(source: str, line_no: int) -> str:
    lines = source.splitlines()
    if 1 <= line_no <= len(lines):
        return lines[line_no - 1].strip()
    return ""


def _inside_loop(lines: list[str], index: int) -> bool:
    current_indent = len(lines[index]) - len(lines[index].lstrip())
    for previous in range(index - 1, -1, -1):
        stripped = lines[previous].strip()
        indent = len(lines[previous]) - len(lines[previous].lstrip())
        if stripped.startswith(("for ", "while ")) and indent < current_indent:
            return True
        if stripped and indent < current_indent and not stripped.startswith(("#", "@")):
            return False
    return False


def analyze_orm(file_contents: dict[str, str]) -> list[dict[str, Any]]:
    findings = []
    for path, source in file_contents.items():
        if not path.endswith(".py"):
            continue
        lines = source.splitlines()
        for index, line in enumerate(lines):
            line_no = index + 1
            stripped = line.strip()
            if re.search(r"\.search_count\s*\(", stripped) and _inside_loop(lines, index):
                findings.append({
                    "file": path,
                    "line": line_no,
                    "pattern": "search_count in loop",
                    "severity": "CRITICAL",
                    "code_snippet": stripped,
                    "explanation": "This executes one COUNT query per loop iteration.",
                    "fix": "Batch the search on all record IDs and aggregate counts in Python or with read_group().",
                    "agent": "orm",
                })
            elif re.search(r"\.search\s*\(", stripped) and _inside_loop(lines, index):
                findings.append({
                    "file": path,
                    "line": line_no,
                    "pattern": "search in loop",
                    "severity": "CRITICAL",
                    "code_snippet": stripped,
                    "explanation": "This can create an N+1 query pattern in Odoo ORM.",
                    "fix": "Move the search outside the loop and use an `in` domain over the full recordset.",
                    "agent": "orm",
                })
            elif re.search(r"\.write\s*\(", stripped) and _inside_loop(lines, index):
                findings.append({
                    "file": path,
                    "line": line_no,
                    "pattern": "write in loop",
                    "severity": "CRITICAL",
                    "code_snippet": stripped,
                    "explanation": "This performs one UPDATE per record instead of a batched write.",
                    "fix": "Call write() once on the complete recordset.",
                    "agent": "orm",
                })
            elif re.search(r"\.browse\s*\(", stripped) and _inside_loop(lines, index):
                findings.append({
                    "file": path,
                    "line": line_no,
                    "pattern": "browse in loop",
                    "severity": "WARNING",
                    "code_snippet": stripped,
                    "explanation": "Browsing IDs one at a time prevents efficient prefetching.",
                    "fix": "Browse all IDs at once, then iterate over the resulting recordset.",
                    "agent": "orm",
                })
    return findings


def analyze_security(file_contents: dict[str, str]) -> list[dict[str, Any]]:
    findings = []
    for path, source in file_contents.items():
        if not path.endswith(".py"):
            continue
        lines = source.splitlines()
        for index, line in enumerate(lines):
            line_no = index + 1
            stripped = line.strip()
            if ".sudo().search([])" in stripped:
                findings.append({
                    "file": path,
                    "line": line_no,
                    "vulnerability_type": "unrestricted sudo search",
                    "severity": "CRITICAL",
                    "code_snippet": stripped,
                    "risk_description": "This bypasses record rules and can expose every record in the model.",
                    "fix": "Add a restrictive domain, usually company, owner, or explicit business access scope.",
                    "agent": "security",
                })
            if "execute(" in stripped and re.search(r"(\+|%|f['\"])", stripped):
                findings.append({
                    "file": path,
                    "line": line_no,
                    "vulnerability_type": "SQL injection",
                    "severity": "CRITICAL",
                    "code_snippet": stripped,
                    "risk_description": "SQL is built dynamically instead of being parameterized.",
                    "fix": "Use placeholders: self.env.cr.execute(\"... WHERE name = %s\", (name,)).",
                    "agent": "security",
                })
            if re.search(r"query\s*=.*SELECT.*\+", stripped, re.IGNORECASE):
                findings.append({
                    "file": path,
                    "line": line_no,
                    "vulnerability_type": "SQL injection",
                    "severity": "CRITICAL",
                    "code_snippet": stripped,
                    "risk_description": "The query string is concatenated with runtime values.",
                    "fix": "Keep SQL static and pass user values as parameters to execute().",
                    "agent": "security",
                })
            if "auth='public'" in stripped or 'auth="public"' in stripped:
                findings.append({
                    "file": path,
                    "line": line_no,
                    "vulnerability_type": "public route",
                    "severity": "WARNING",
                    "code_snippet": stripped,
                    "risk_description": "Public routes require explicit access checks before returning ERP data.",
                    "fix": "Use auth='user' or validate authorization and rate limits inside the handler.",
                    "agent": "security",
                })
    return _dedupe(findings)


def analyze_xml(file_contents: dict[str, str]) -> list[dict[str, Any]]:
    findings = []
    xml_ids_by_file: dict[str, list[tuple[str, int]]] = {}
    for path, source in file_contents.items():
        if not path.endswith(".xml"):
            continue
        try:
            parser = etree.XMLParser(recover=False, huge_tree=False)
            root = etree.fromstring(source.encode("utf-8"), parser=parser)
        except etree.XMLSyntaxError as exc:
            findings.append({
                "file": path,
                "line": exc.lineno or 1,
                "issue_type": "malformed XML",
                "severity": "CRITICAL",
                "element": "",
                "code_snippet": _line_snippet(source, exc.lineno or 1),
                "explanation": str(exc),
                "fix": "Fix the XML syntax and validate before committing.",
                "agent": "xml",
            })
            continue

        for elem in root.iter():
            line = elem.sourceline or 1
            if elem.tag == "xpath":
                expr = elem.attrib.get("expr", "")
                if re.search(r"\[\d+\]", expr):
                    findings.append({
                        "file": path,
                        "line": line,
                        "issue_type": "fragile positional xpath",
                        "severity": "WARNING",
                        "element": etree.tostring(elem, encoding="unicode").strip(),
                        "code_snippet": _line_snippet(source, line),
                        "explanation": "Positional XPath breaks when upstream view layout changes.",
                        "fix": "Anchor XPath to a stable field, group, or named element.",
                        "agent": "xml",
                    })
            if "t-raw" in elem.attrib:
                findings.append({
                    "file": path,
                    "line": line,
                    "issue_type": "unsafe qweb raw output",
                    "severity": "WARNING",
                    "element": etree.tostring(elem, encoding="unicode").strip(),
                    "code_snippet": _line_snippet(source, line),
                    "explanation": "t-raw renders unescaped HTML and can introduce XSS.",
                    "fix": "Use t-out unless the value is explicitly sanitized.",
                    "agent": "xml",
                })
            if elem.tag == "record" and elem.attrib.get("id"):
                xml_ids_by_file.setdefault(path, []).append((elem.attrib["id"], line))

    for path, ids in xml_ids_by_file.items():
        counts = Counter(xml_id for xml_id, _line in ids)
        for xml_id, line in ids:
            if counts[xml_id] > 1:
                findings.append({
                    "file": path,
                    "line": line,
                    "issue_type": "duplicate XML id",
                    "severity": "CRITICAL",
                    "element": f'<record id="{xml_id}">',
                    "code_snippet": f'<record id="{xml_id}">',
                    "explanation": "Duplicate XML IDs in a module can override or break data loading.",
                    "fix": "Use a unique module-prefixed XML ID.",
                    "agent": "xml",
                })
    return findings


def generate_documentation(repo: str, pr_number: int, repo_data: dict[str, Any]) -> dict[str, Any]:
    changed = repo_data["changed_files"]
    py_files = repo_data["python_files"]
    xml_files = repo_data["xml_files"]
    return {
        "pr_summary": f"Review for {repo} PR #{pr_number} covers {len(changed)} changed file(s), including {len(py_files)} Python and {len(xml_files)} XML file(s).",
        "files_changed": [{"file": path, "change_description": _describe_file(path)} for path in changed],
        "models_affected": [path for path in py_files if "/models/" in f"/{path}"],
        "views_affected": xml_files,
        "new_dependencies": [],
        "migration_required": any("__manifest__.py" in path or "/models/" in f"/{path}" for path in changed),
        "migration_notes": "Check database migration impact for new or changed Odoo fields." if py_files else None,
        "readme_draft": None,
    }


def _describe_file(path: str) -> str:
    if path.endswith(".py"):
        return "Python/Odoo business logic changed."
    if path.endswith(".xml"):
        return "Odoo XML view or data definition changed."
    if path.endswith(".csv"):
        return "CSV security or data file changed."
    return "Supporting file changed."


def _dedupe(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    result = []
    for finding in findings:
        key = (finding["file"], finding["line"], finding.get("vulnerability_type"), finding["code_snippet"])
        if key in seen:
            continue
        seen.add(key)
        result.append(finding)
    return result
