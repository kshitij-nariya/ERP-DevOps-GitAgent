# Rules - ERP DevOps Orchestrator

## Must Always

- Route all Python changed files through `orm-performance` and `security-reviewer`.
- Route all XML changed files through `xml-validator`.
- Include exact file path and line number for every finding.
- Assign `CRITICAL`, `WARNING`, or `SUGGESTION` for every finding.
- Write review summary to `memory/runtime/reviews.md`.
- Return valid JSON ReviewReport from automated runs.
- Include a recommended fix for every CRITICAL finding.

## Must Never

- Fabricate line numbers or snippets not present in the diff.
- Mark a finding as CRITICAL without an actionable fix.
- Skip the security agent for small Python changes.
- Post a zero-context review when Python or XML changed.

## Severity Definitions

- CRITICAL: blocks merge. Production risk such as SQL injection, unrestricted `sudo()`, N+1 in a loop, or broken XML.
- WARNING: should fix before merge. Technical debt or likely future risk.
- SUGGESTION: optional improvement.

## Review Scope

Only review changed files in the diff unless explicitly asked for a full-repo audit.
