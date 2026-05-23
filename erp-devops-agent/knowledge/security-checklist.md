# Security Checklist

- Check route authentication and authorization.
- Check `sudo()` call sites for explicit domain limits and business justification.
- Check raw SQL for parameterization.
- Check sensitive logging.
- Check CORS and public endpoints.
- Check `ir.model.access.csv` for new models.
