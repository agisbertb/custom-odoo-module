from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Complaint(models.Model):
    _name = 'complaint.complaint'
    _description = 'Complaint Management'

    title = fields.Char(string='Title', required=True)
    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    user_id = fields.Many2one('res.users', string='User Creator', default=lambda self: self.env.user)
    creation_date = fields.Datetime(string='Creation Date', default=fields.Datetime.now, readonly=True)
    modification_date = fields.Datetime(string='Modification Date', readonly=True, compute='_compute_dates')
    closing_date = fields.Datetime(string='Closing Date')
    sale_order_id = fields.Many2one('sale.order', string='Associated Sale Order', required=True)
    initial_description = fields.Text(string='Initial Description')
    messages_ids = fields.One2many('complaint.message', 'complaint_id', string='Messages')
    invoice_count = fields.Integer(string='Number of Invoices')
    shipment_count = fields.Integer(string='Number of Shipments')
    state = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled')
    ], string='State', default='new')
    resolution_description = fields.Text(string='Resolution Description')
    closing_reason_id = fields.Many2one('complaint.closing_reason', string='Closing Reason')
