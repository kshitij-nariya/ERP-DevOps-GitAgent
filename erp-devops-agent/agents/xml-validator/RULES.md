# Rules - XML Validation Agent

- Parse XML before deeper analysis.
- Flag malformed XML as CRITICAL.
- Flag `t-raw` as WARNING unless it is clearly sanitized.
- Prefer field-based XPath selectors over positional selectors.
- Cite exact element line numbers when available.
