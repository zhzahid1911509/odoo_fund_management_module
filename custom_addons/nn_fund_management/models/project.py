# -*- coding: utf-8 -*-
from odoo import models, fields, api

class NnProject(models.Model):
    _name = 'nn.project'
    _description = 'Project Profile'

    name = fields.Char(string='Project Name', required=True)
    description = fields.Text(string='Project Details')
    
    total_allocated = fields.Float(string='Total Allocated Fund', compute='_compute_balances', store=True, readonly=True)
    available_fund = fields.Float(string='Available Fund', compute='_compute_balances', store=True, readonly=True)
    requisition_hold = fields.Float(string='Requisition Hold', compute='_compute_balances', store=True, readonly=True)
    transfer_hold = fields.Float(string='Transfer Hold', compute='_compute_balances', store=True, readonly=True)
    approved_unspent = fields.Float(string='Approved but Unspent', compute='_compute_balances', store=True, readonly=True)
    total_spent = fields.Float(string='Total Spent Amount', compute='_compute_balances', store=True, readonly=True)
    incoming_transfers = fields.Float(string='Incoming Transfers', compute='_compute_balances', store=True, readonly=True)
    outgoing_transfers = fields.Float(string='Outgoing Transfers', compute='_compute_balances', store=True, readonly=True)

    allocation_ids = fields.One2many('nn.fund.allocation', 'project_id', string='Allocations')
    requisition_ids = fields.One2many('nn.fund.requisition', 'project_id', string='Requisitions')

    @api.depends('allocation_ids.amount', 'allocation_ids.state', 'requisition_ids.amount', 'requisition_ids.state')
    def _compute_balances(self):
        for proj in self:
            approved_alloc = sum(a.amount for a in proj.allocation_ids if a.state == 'approved')
            req_hold = sum(r.amount for r in proj.requisition_ids if r.state == 'submitted')
            spent = sum(r.amount for r in proj.requisition_ids if r.state == 'approved')
            
            # Fetch relational transfers from environment registry to bypass circular dependencies
            trans_hold = sum(t.amount for t in self.env['nn.fund.transfer'].search([('from_project_id', '=', proj.id), ('state', '=', 'submitted')]))
            out_trans = sum(t.amount for t in self.env['nn.fund.transfer'].search([('from_project_id', '=', proj.id), ('state', '=', 'approved')]))
            in_trans = sum(t.amount for t in self.env['nn.fund.transfer'].search([('to_project_id', '=', proj.id), ('state', '=', 'approved')]))

            proj.total_allocated = approved_alloc
            proj.requisition_hold = req_hold
            proj.transfer_hold = trans_hold
            proj.outgoing_transfers = out_trans
            proj.incoming_transfers = in_trans
            proj.total_spent = spent
            proj.approved_unspent = approved_alloc - spent
            
            # Balance Equation: (Allocated + Incoming) - (Req Hold + Transfer Hold + Outgoing + Spent)
            proj.available_fund = (approved_alloc + in_trans) - (req_hold + trans_hold + out_trans + spent)