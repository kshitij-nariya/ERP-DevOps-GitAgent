# Rules - ORM Performance Agent

- Cite exact line numbers.
- Include the actual bad code snippet.
- Provide a concrete code fix.
- Check all Python files, not only `models.py`.
- Do not flag standard Odoo framework patterns such as `_inherit` or `super()`.
- Raw SQL built with concatenation is CRITICAL.
- `search_count()` in a loop is always CRITICAL.
