# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class NnFundTransfer(models.Model):
    _name = 'nn.fund.transfer'
    _description = 'Inter-Budget Fund Transfer'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Transfer ID', required=True, copy=False, readonly=True, default=lambda self: 'New')
    
    # Polymorphic Sources (Exclusive-OR)
    from_project_id = fields.Many2one('nn.project', string='Source Project', tracking=True)
    from_expense_head_id = fields.Many2one('nn.expense.head', string='Source Expense Head', tracking=True)
    
    # Polymorphic Destinations (Exclusive-OR)
    to_project_id = fields.Many2one('nn.project', string='Destination Project', tracking=True)
    to_expense_head_id = fields.Many2one('nn.expense.head', string='Destination Expense Head', tracking=True)
    
    amount = fields.Float(string='Transfer Amount', required=True, tracking=True)
    reason = fields.Char(string='Transfer Reason', required=True, tracking=True)
    date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    requested_by = fields.Many2one('res.users', string='Requested By', default=lambda self: self.env.user, required=True, readonly=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Hold/Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft', readonly=True, index=True, tracking=True)

    @api.constrains('from_project_id', 'from_expense_head_id', 'to_project_id', 'to_expense_head_id')
    def _check_transfer_integrity(self):
        for record in self:
            # Validate Source XOR
            if not record.from_project_id and not record.from_expense_head_id:
                raise ValidationError("Configuration Error! Select either a Source Project or Source Expense Head.")
            if record.from_project_id and record.from_expense_head_id:
                raise ValidationError("Validation Error! A transfer can only source from one budget line.")
            
            # Validate Destination XOR
            if not record.to_project_id and not record.to_expense_head_id:
                raise ValidationError("Configuration Error! Select either a Destination Project or Destination Expense Head.")
            if record.to_project_id and record.to_expense_head_id:
                raise ValidationError("Validation Error! A transfer can only target one destination budget line.")
            
            # Prevent self-loop transfers
            if record.from_project_id and record.from_project_id == record.to_project_id:
                raise ValidationError("Loop Detected! Source and Destination projects cannot be identical.")
            if record.from_expense_head_id and record.from_expense_head_id == record.to_expense_head_id:
                raise ValidationError("Loop Detected! Source and Destination expense heads cannot be identical.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('nn.fund.transfer') or 'XFER-GENERIC'
        return super(NnFundTransfer, self).create(vals_list)

    def action_submit(self):
        for record in self:
            if record.amount <= 0:
                raise ValidationError("Transfer amounts must be positive values.")
            
            source = record.from_project_id or record.from_expense_head_id
            if record.amount > source.available_fund:
                raise ValidationError("Transfer Denied! The requested source budget lacks sufficient available unassigned funds.")
            
            record.state = 'submitted'
            source._compute_balances()

    def action_approve(self):
        for record in self:
            record.state = 'approved'
            if record.from_project_id: record.from_project_id._compute_balances()
            if record.from_expense_head_id: record.from_expense_head_id._compute_balances()
            if record.to_project_id: record.to_project_id._compute_balances()
            if record.to_expense_head_id: record.to_expense_head_id._compute_balances()

    def action_reject(self):
        for record in self:
            record.state = 'rejected'
            if record.from_project_id: record.from_project_id._compute_balances()
            if record.from_expense_head_id: record.from_expense_head_id._compute_balances()