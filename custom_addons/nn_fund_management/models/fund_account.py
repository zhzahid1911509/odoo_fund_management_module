# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class NnFundAccount(models.Model):
    _name = 'nn.fund.account'
    _description = 'Fund Account'

    name = fields.Char(string='Account Name', required=True)
    account_number = fields.Char(string='Account Number')
    
    total_received = fields.Float(
        string='Total Received Amount', 
        compute='_compute_balances', 
        store=True, 
        readonly=True
    )
    amount_held = fields.Float(string='Amount On Hold', compute='_compute_balances', store=True, readonly=True)
    total_assigned = fields.Float(string='Total Assigned Amount', compute='_compute_balances', store=True, readonly=True)
    available_unassigned_balance = fields.Float(
        string='Available Unassigned Balance', 
        compute='_compute_balances', 
        store=True, 
        readonly=True
    )

    allocation_ids = fields.One2many('nn.fund.allocation', 'account_id', string='Allocations')
    incoming_fund_ids = fields.One2many('nn.incoming.fund', 'account_id', string='Incoming Transaction Ledgers')

    @api.depends('incoming_fund_ids.amount', 'incoming_fund_ids.state', 'allocation_ids.amount', 'allocation_ids.state')
    def _compute_balances(self):
        for account in self:
            # Aggregate balance calculations dynamically from verified deposits
            total_rec = sum(inc.amount for inc in account.incoming_fund_ids if inc.state == 'confirmed')
            
            held = 0.0
            assigned = 0.0
            for alloc in account.allocation_ids:
                if alloc.state in ['submitted', 'gm_approval', 'md_approval']:
                    held += alloc.amount
                elif alloc.state == 'approved':
                    assigned += alloc.amount

            account.total_received = total_rec
            account.amount_held = held
            account.total_assigned = assigned
            
            # Master Formula: (Total Received) - (Funds Active on Hold + Permanent Allocations Out)
            account.available_unassigned_balance = total_rec - (held + assigned)

    @api.constrains('available_unassigned_balance')
    def _check_negative_balance(self):
        for account in self:
            if account.available_unassigned_balance < 0:
                raise ValidationError(
                    "Transaction Terminated! The requested operation forces the bank account's "
                    "unassigned fluid balance below zero. Action rolled back safely."
                )
