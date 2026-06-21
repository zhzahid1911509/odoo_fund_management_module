from odoo import models, fields, api
from odoo.exceptions import ValidationError

class NnIncomingFund(models.Model):
    _name = 'nn.incoming.fund'
    _description = 'Incoming Fund Deposit Record'
    _order = 'date desc, id desc'

    name = fields.Char(string='Reference ID', required=True, copy=False, readonly=True, default=lambda self: 'New')
    account_id = fields.Many2one('nn.fund.account', string='Fund Account', required=True)
    date = fields.Date(string='Deposit Date', default=fields.Date.context_today, required=True)
    amount = fields.Float(string='Received Amount', required=True)
    transaction_ref = fields.Char(string='Transaction Reference', required=True)
    sender_source = fields.Char(string='Sender / Source', required=True)
    description = fields.Text(string='Transaction Description')
    
    # Attachment configuration fields
    attachment = fields.Binary(string='Supporting Attachment')
    attachment_name = fields.Char(string='Attachment Filename')
    
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed')
    ], string='Status', default='draft', readonly=True, index=True)

    # Server-Side SQL Constraint: Double check matching criteria for section 2 rules
    _sql_constraints = [
        ('unique_tx_ref_per_account', 
         'unique(account_id, transaction_ref)', 
         'Data Integrity Violation! The same transaction reference must not be used twice within the same fund account!')
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('nn.incoming.fund') or 'INC-GENERIC'
        return super(NnIncomingFund, self).create(vals_list)

    def action_confirm(self):
        """Confirm the incoming fund and automatically add it to the unassigned balance"""
        for record in self:
            if record.amount <= 0:
                raise ValidationError("The deposited transaction amount must be strictly positive.")
            record.state = 'confirmed'
            # Trigger immediate background re-calculation on the target bank account node
            record.account_id._compute_balances()

    def action_draft(self):
        """Allows authorized rollback changes to draft status"""
        for record in self:
            record.state = 'draft'
            record.account_id._compute_balances()