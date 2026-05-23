from odoo import models


class SaleOrderBad(models.Model):
    _inherit = "sale.order"

    def confirm_all_lines(self):
        for line in self.order_line:
            line.write({"state": "sale"})

    def get_partner_orders(self):
        results = []
        for partner in self.env["res.partner"].search([]):
            orders = self.env["sale.order"].search([
                ("partner_id", "=", partner.id),
            ])
            results.extend(orders)
        return results

    def get_all_invoices(self):
        return self.env["account.move"].sudo().search([])

    def search_by_name(self, name):
        query = "SELECT id FROM sale_order WHERE name = '" + name + "'"
        self.env.cr.execute(query)
        return self.env.cr.fetchall()
