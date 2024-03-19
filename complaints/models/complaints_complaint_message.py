from odoo import models, fields

class ComplaintMessage(models.Model):
    _name = 'complaint.message'
    _description = 'Complaint Message'

    text = fields.Text(string='Message Text', required=True)
    author_id = fields.Many2one('res.partner', string='Author', required=True)
    message_date = fields.Datetime(string='Message Date', default=fields.Datetime.now, readonly=True)
    complaint_id = fields.Many2one('complaint.complaint', string='Associated Complaint', required=True)
