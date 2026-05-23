from odoo import models


class BadOrmExample(models.Model):
    _inherit = "sale.order"

    def confirm_all_lines(self):
        for line in self.order_line:
            line.write({"state": "sale"})

    def get_partner_orders(self):
        orders = []
        for partner in self.env["res.partner"].search([]):
            orders.extend(self.env["sale.order"].search([("partner_id", "=", partner.id)]))
        return orders
