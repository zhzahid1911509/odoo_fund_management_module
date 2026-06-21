# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class NnFundAllocation(models.Model):
    _name = 'nn.fund.allocation'
    _description = 'Fund Allocation Request'
    _inherit = ['mail.thread', 'mail.activity.mixin'] # Adds the chatter system fields

    name = fields.Char(string='Request Number', required=True, copy=False, readonly=True, default=lambda self: 'New')
    # ... leave the rest of your model code exactly as it is ...
    account_id = fields.Many2one('nn.fund.account', string='Fund Account', required=True)
    project_id = fields.Many2one('nn.project', string='Target Project')
    expense_head_id = fields.Many2one('nn.expense.head', string='Target Expense Head')
    amount = fields.Float(string='Allocation Amount', required=True)
    purpose = fields.Text(string='Allocation Purpose', required=True)
    request_date = fields.Date(string='Request Date', default=fields.Date.context_today, required=True)
    requested_by = fields.Many2one('res.users', string='Requested By', default=lambda self: self.env.user, required=True, readonly=True)
    attachment = fields.Binary(string='Supporting Document Attachment')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('gm_approval', 'GM Approval'),
        ('md_approval', 'MD Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', readonly=True, index=True)

    @api.constrains('project_id', 'expense_head_id')
    def _check_exclusive_or_destination(self):
        for record in self:
            if not record.project_id and not record.expense_head_id:
                raise ValidationError("Operational Error! You must select either a Project or an Expense Head.")
            if record.project_id and record.expense_head_id:
                raise ValidationError("Business Logic Fault! A transaction must use either a project or an expense head, not both.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('nn.fund.allocation') or 'ALLOC-GENERIC'
        return super(NnFundAllocation, self).create(vals_list)

    def action_submit(self):
        for record in self:
            if record.amount <= 0:
                raise ValidationError("The requested capital allocation value must be positive.")
            if record.amount > record.account_id.available_unassigned_balance:
                raise ValidationError("Insufficient Liquidity! The requested allocation amount is greater than the available unassigned balance.")
            record.state = 'submitted'
            record.account_id._compute_balances()

    def action_gm_approve(self):
        for record in self:
            record.state = 'gm_approval'

    def action_md_approve(self):
        for record in self:
            record.state = 'approved'
            record.account_id._compute_balances()
            if record.project_id:
                record.project_id._compute_balances()
            if record.expense_head_id:
                record.expense_head_id._compute_balances()

    def action_reject(self):
        for record in self:
            record.state = 'rejected'
            record.account_id._compute_balances()

    def action_cancel(self):
        for record in self:
            if record.state == 'approved':
                raise ValidationError("Approved financial ledger entries cannot be arbitrarily cancelled.")
            record.state = 'cancelled'
            record.account_id._compute_balances()