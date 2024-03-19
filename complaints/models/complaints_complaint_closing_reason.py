from odoo import models, fields

class ComplaintClosingReason(models.Model):
    _name = 'complaint.closing_reason'
    _description = 'Complaint Closing Reason'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')