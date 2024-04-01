from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    complaint_ids = fields.One2many('complaint.complaint', 'sale_order_id', string='Complaints')