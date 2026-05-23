# Odoo ERP Anti-Patterns Reference

## ORM Performance

### N+1 Query Pattern

Bad:

```python
for partner in partners:
    orders = self.env["sale.order"].search([("partner_id", "=", partner.id)])
```

Good:

```python
orders = self.env["sale.order"].search([("partner_id", "in", partners.ids)])
```

### Write in Loop

Bad:

```python
for line in self.order_line:
    line.write({"state": "confirmed"})
```

Good:

```python
self.order_line.write({"state": "confirmed"})
```

## XML

- Avoid positional XPath such as `//div[2]`.
- Prefer field anchors such as `//field[@name='partner_id']`.
- Avoid duplicate XML IDs in a module.
- Replace QWeb `t-raw` with `t-out` unless output is sanitized.

## Security

- Avoid unrestricted `sudo().search([])`.
- Parameterize SQL queries.
- Avoid public routes for sensitive data.
