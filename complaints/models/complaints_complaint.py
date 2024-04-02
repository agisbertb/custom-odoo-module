from odoo import models, fields, api, _
from odoo.exceptions import UserError


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
    has_posted_invoices = fields.Boolean(compute='_compute_has_posted_invoices', string='Has Posted Invoices')
    has_linked_sale_order = fields.Boolean(compute='_compute_has_linked_sale_order', string='Has Linked Sale Order')
    sale_order_id = fields.Many2one('sale.order', string='Associated Sale Order')
    resolution_description = fields.Text(string='Resolution Description')
    closing_reason_id = fields.Many2one('complaint.closing_reason', string='Closing Reason')

    @api.depends('title')
    def name_get(self):
        result = []
        for record in self:
            name = record.title
            result.append((record.id, name))
        return result

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

    @api.depends('sale_order_id')
    def _compute_has_posted_invoices(self):
        for record in self:
            if record.sale_order_id:
                invoices = record.sale_order_id.invoice_ids.filtered(lambda inv: inv.state == 'posted')
                if invoices:
                    record.has_posted_invoices = len(invoices)
                else:
                    record.has_posted_invoices = 0
            else:
                record.has_posted_invoices = False
    
    @api.depends('sale_order_id')
    def _compute_has_linked_sale_order(self):
        for record in self:
            record.has_linked_sale_order = bool(record.sale_order_id)

    def close_ticket(self):
        for record in self:
            if record.state == 'in_progress':
                record.state = 'closed'
                record.closing_date = fields.Datetime.now()

    def cancel_ticket(self):
        for record in self:
            if record.state in ['new', 'in_progress']:
                record.state = 'cancelled'

    def reopen_ticket(self):
        for record in self:
            if record.state == 'closed':
                record.state = 'in_progress'

    def cancel_associated_sale_order(self):
        for record in self:
            print(record.sale_order_id)
            if record.sale_order_id:
                sale_order = record.sale_order_id
                if sale_order.state != 'cancel':
                    if sale_order.invoice_ids.filtered(lambda inv: inv.state == 'posted'):
                        # Mostrar advertencia si conté factures ja públicades
                        warning_msg = _('There are posted invoices associated with the sale order. Please cancel them first!')

                    # Enviar correu al client informant de la cancel·lació
                    mail_template = self.env.ref('complaints.email_template_cancel_order')
                    if mail_template:
                        mail_template.send_mail(sale_order.id, force_send=True)
                    # Registrar el correu a l'historial de la comanda
                    mail_values = {
                        'subject': _('Order Cancellation Notification'),
                        'email_from': self.env.user.partner_id.email,
                        'email_to': sale_order.partner_id.email,
                        'body_html': _('The order %s has been cancelled.') % sale_order.name,
                        'model': 'sale.order',
                        'res_id': sale_order.id,
                    }
                    self.env['mail.mail'].create(mail_values)

                    # Cancel·lar factures associades no publicades
                    for invoice in sale_order.invoice_ids.filtered(lambda inv: inv.state != 'posted'):
                        invoice.state = 'cancel'

                    # Cancel·lar enviaments no fets
                    for picking in sale_order.picking_ids.filtered(lambda pick: pick.state not in ['done', 'cancel']):
                        picking.state = 'cancel'

                    # Cancel the status of the assosicated sale order
                    sale_order.state = 'cancel'

                    # Redirect to the sale order
                    return {
                        'name': _('Sale Order'),
                        'view_mode': 'form',
                        'res_model': 'sale.order',
                        'type': 'ir.actions.act_window',
                        'res_id': sale_order.id,
                        'context': self.env.context,
                    }
            
    _sql_constraints = [
        ('unique_title', 'UNIQUE(title)', _('A complaint with this title already exists!')),
        ('unique_open_complaint', 'CHECK((state != \'in_progress\' OR state IS NULL) OR (state = \'in_progress\' AND (SELECT COUNT(*) FROM complaint_complaint WHERE sale_order_id = complaint_complaint.sale_order_id AND state = \'in_progress\') = 1))', _('There can only be one open complaint associated with the same sale order at a time!'))
    ]