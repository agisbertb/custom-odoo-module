from odoo import models, fields, api, _


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

    @api.depends('sale_order_id')
    def _compute_invoice_count(self):
        for record in self:
            if record.sale_order_id:
                invoices = self.env['account.move'].search([
                    ('invoice_origin', '=', record.sale_order_id.name),
                    ('move_type', '=', 'out_invoice'),
                    ('state', '!=', 'cancel')
                ])
                record.invoice_count = len(invoices)
            else:
                record.invoice_count = 0

    @api.depends('sale_order_id')
    def _compute_shipment_count(self):
        for complaint in self:
            if complaint.sale_order_id:
                pickings = self.env['stock.picking'].search([('sale_id', '=', complaint.sale_order_id.id)])
                complaint.shipment_count = len(pickings)
            else:
                complaint.shipment_count = 0

    def set_to_closed(self):
        for record in self:
            if record.state in ['new', 'in_progress']:
                record.state = 'closed'
                record.closing_date = fields.Datetime.now()

    def set_to_cancelled(self):
        for record in self:
            if record.state in ['new', 'in_progress']:
                record.state = 'cancelled'

    _sql_constraints = [
        ('unique_title', 'UNIQUE(title)', _('A complaint with this title already exists!')),
        ('unique_customer_complaint', 'UNIQUE(customer_id)', _('A customer can only be associated with one complaint at a time!')),
        ('unique_sale_order_complaint', 'UNIQUE(sale_order_id)', _('A sale order can only be associated with one complaint at a time!')),
    ]