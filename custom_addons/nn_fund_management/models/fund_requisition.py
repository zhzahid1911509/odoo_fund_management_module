# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class NnFundRequisition(models.Model):
    _name = 'nn.fund.requisition'
    _description = 'Fund Requisition'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Requisition Number', required=True, copy=False, readonly=True, default=lambda self: 'New')
    project_id = fields.Many2one('nn.project', string='Source Project', tracking=True)
    expense_head_id = fields.Many2one('nn.expense.head', string='Source Expense Head', tracking=True)
    amount = fields.Float(string='Requisition Amount', required=True, tracking=True)
    purpose = fields.Char(string='Purpose / Vendor Info', required=True, tracking=True)
    date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    requested_by = fields.Many2one('res.users', string='Requested By', default=lambda self: self.env.user, required=True, readonly=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Hold/Review'),
        ('approved', 'Approved/Paid'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft', readonly=True, index=True, tracking=True)

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
                vals['name'] = self.env['ir.sequence'].next_by_code('nn.fund.requisition') or 'REQ-EXP-GENERIC'
        return super(NnFundRequisition, self).create(vals_list)

    def action_submit(self):
        for record in self:
            if record.amount <= 0:
                raise ValidationError("The requested expense requisition amount must be strictly greater than zero.")
            
            target = record.project_id or record.expense_head_id
            if record.amount > target.available_fund:
                raise ValidationError("Budget Violation! Action Aborted. The requested expense exceeds the remaining Available Fund balance.")
            
            record.state = 'submitted'
            target._compute_balances()

    def action_approve(self):
        for record in self:
            record.state = 'approved'
            target = record.project_id or record.expense_head_id
            target._compute_balances()

    def action_reject(self):
        for record in self:
            record.state = 'rejected'
            target = record.project_id or record.expense_head_id
            target._compute_balances()