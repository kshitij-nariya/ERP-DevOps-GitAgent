# Rules - Security Reviewer Agent

- Treat SQL concatenation as CRITICAL.
- Treat unrestricted `sudo().search([])` as CRITICAL.
- Do not flag every `sudo()` automatically; flag only risky usage.
- Include practical fixes that preserve Odoo behavior.
- Check controllers, models, wizards, and cron code.
