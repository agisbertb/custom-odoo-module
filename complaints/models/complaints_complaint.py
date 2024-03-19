from odoo import models, fields, api

class Complaint(models.Model):
    _name = 'complaint.complaint'
    _description = 'Complaint Management'

    title = fields.Char(string='Title', required=True)
    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    user_id = fields.Many2one('res.users', string='User Creator', default=lambda self: self.env.user)
    creation_date = fields.Datetime(string='Creation Date', default=fields.Datetime.now, readonly=True)
    modification_date = fields.Datetime(string='Modification Date', readonly=True)
    closing_date = fields.Datetime(string='Closing Date')
    initial_description = fields.Text(string='Initial Description')
    messages_ids = fields.One2many('complaint.message', 'complaint_id', string='Messages')
    invoice_count = fields.Integer(string='Number of Invoices', compute='_compute_invoice_count')
    shipment_count = fields.Integer(string='Number of Shipments', compute='_compute_shipment_count')
    state = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled')
    ], string='State', default='new')
    sale_order_id = fields.Many2one('sale.order', string='Associated Sale Order')
    resolution_description = fields.Text(string='Resolution Description')
    closing_reason_id = fields.Many2one('complaint.closing_reason', string='Closing Reason')


    @api.depends('sale_order_id.invoice_ids')
    def _compute_invoice_count(self):
        for complaint in self:
            complaint.invoice_count = len(complaint.sale_order_id.invoice_ids)

    @api.depends('sale_order_id.picking_ids')
    def _compute_shipment_count(self):
        for complaint in self:
            complaint.shipment_count = len(complaint.sale_order_id.picking_ids)