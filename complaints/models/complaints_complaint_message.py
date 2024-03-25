from odoo import models, fields, api, exceptions

class ComplaintMessage(models.Model):
    _name = 'complaint.message'
    _description = 'Complaint Message'

    text = fields.Text(string='Message Text', required=True)
    author_id = fields.Many2one('res.partner', string='Author', required=True)
    message_date = fields.Datetime(string='Message Date', default=fields.Datetime.now, readonly=True)
    complaint_id = fields.Many2one('complaint.complaint', string='Associated Complaint', required=True)

    @api.model
    def create(self, vals):
        new_record = super(ComplaintMessage, self).create(vals)
        if new_record.complaint_id and new_record.complaint_id.state == 'new':
            new_record.complaint_id.state = 'in_progress'
        return new_record

    @api.model
    def create(self, vals):
        return super(ComplaintMessage, self).create(vals)

    def write(self):
        raise exceptions.UserError("Sorry, messages cannot be modified.")