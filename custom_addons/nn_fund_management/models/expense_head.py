# -*- coding: utf-8 -*-
from odoo import models, fields, api

class NnExpenseHead(models.Model):
    _name = 'nn.expense.head'
    _description = 'Expense Head Configuration'

    name = fields.Char(string='Expense Head Name', required=True)
    description = fields.Text(string='Description Log')

    total_allocated = fields.Float(string='Total Allocated Fund', compute='_compute_balances', store=True, readonly=True)
    available_fund = fields.Float(string='Available Fund', compute='_compute_balances', store=True, readonly=True)
    requisition_hold = fields.Float(string='Requisition Hold', compute='_compute_balances', store=True, readonly=True)
    transfer_hold = fields.Float(string='Transfer Hold', compute='_compute_balances', store=True, readonly=True)
    approved_unspent = fields.Float(string='Approved but Unspent', compute='_compute_balances', store=True, readonly=True)
    total_spent = fields.Float(string='Total Spent Amount', compute='_compute_balances', store=True, readonly=True)
    incoming_transfers = fields.Float(string='Incoming Transfers', compute='_compute_balances', store=True, readonly=True)
    outgoing_transfers = fields.Float(string='Outgoing Transfers', compute='_compute_balances', store=True, readonly=True)

    allocation_ids = fields.One2many('nn.fund.allocation', 'expense_head_id', string='Allocations')
    requisition_ids = fields.One2many('nn.fund.requisition', 'expense_head_id', string='Requisitions')

    @api.depends('allocation_ids.amount', 'allocation_ids.state', 'requisition_ids.amount', 'requisition_ids.state')
    def _compute_balances(self):
        for head in self:
            approved_alloc = sum(a.amount for a in head.allocation_ids if a.state == 'approved')
            req_hold = sum(r.amount for r in head.requisition_ids if r.state == 'submitted')
            spent = sum(r.amount for r in head.requisition_ids if r.state == 'approved')
            
            trans_hold = sum(t.amount for t in self.env['nn.fund.transfer'].search([('from_expense_head_id', '=', head.id), ('state', '=', 'submitted')]))
            out_trans = sum(t.amount for t in self.env['nn.fund.transfer'].search([('from_expense_head_id', '=', head.id), ('state', '=', 'approved')]))
            in_trans = sum(t.amount for t in self.env['nn.fund.transfer'].search([('to_expense_head_id', '=', head.id), ('state', '=', 'approved')]))

            head.total_allocated = approved_alloc
            head.requisition_hold = req_hold
            head.transfer_hold = trans_hold
            head.outgoing_transfers = out_trans
            head.incoming_transfers = in_trans
            head.total_spent = spent
            head.approved_unspent = approved_alloc - spent
            head.available_fund = (approved_alloc + in_trans) - (req_hold + trans_hold + out_trans + spent)