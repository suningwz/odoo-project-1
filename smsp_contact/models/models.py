# -*- coding: utf-8 -*-

from odoo import models, fields, api

import datetime


class ContactSMSP(models.Model):
    _inherit = 'res.partner'

    lifecycle_stage = fields.Selection([
        ('visitor', 'Visitor'),
        ('lead', 'Lead'),
        ('prospect', 'Prospect'),
        ('customer', 'Customer')], string='lifecycle Stage',
        default='lead', store=True)
    become_visitor_date = fields.Datetime(
        'Become Visitor Date', index=True, readonly=True, store=True,
        compute='_compute_visitor_date')
    become_lead_date = fields.Datetime(
        'Become Lead Date', index=True, readonly=True, store=True,
        compute='_compute_lead_date')
    become_prospect_date = fields.Datetime(
        'Become Prospect Date', index=True, readonly=True, store=True,
        compute='_compute_prospect_date')
    become_customer_date = fields.Datetime(
        'Become Customer Date', index=True, readonly=True, store=True,
        compute='_compute_customer_date')

    utm_source = fields.Char(
        'UTM Source', index=True, readonly=False, store=True)
    utm_medium = fields.Char(
        'UTM Medium', index=True, readonly=False, store=True)
    utm_campaign = fields.Char(
        'UTM Campaign', index=True, readonly=False, store=True)
    chatwoot_id = fields.Char(
        'Chatwoot ID', index=True, readonly=False, store=True)
    # teddy = fields.Char(
    #     'TEDDY', index=True, readonly=False, store=True)

    @api.depends('lifecycle_stage')
    def _compute_visitor_date(self):
        for partner in self:
            if partner.lifecycle_stage == 'visitor' and not partner.become_visitor_date:
                partner.become_visitor_date = datetime.datetime.now()

    @api.depends('lifecycle_stage')
    def _compute_lead_date(self):
        for partner in self:
            if partner.lifecycle_stage == 'lead' and not partner.become_lead_date:
                partner.become_lead_date = datetime.datetime.now()
                if not partner.become_visitor_date:
                    partner.become_visitor_date = datetime.datetime.now()

    @api.depends('lifecycle_stage')
    def _compute_prospect_date(self):
        for partner in self:
            if partner.lifecycle_stage == 'prospect' and not partner.become_prospect_date:
                partner.become_prospect_date = datetime.datetime.now()
                if not partner.become_visitor_date:
                    partner.become_visitor_date = datetime.datetime.now()
                if not partner.become_lead_date:
                    partner.become_lead_date = datetime.datetime.now()

    @api.depends('lifecycle_stage')
    def _compute_customer_date(self):
        for partner in self:
            if partner.lifecycle_stage == 'customer' and not partner.become_customer_date:
                partner.become_customer_date = datetime.datetime.now()
                if not partner.become_visitor_date:
                    partner.become_visitor_date = datetime.datetime.now()
                if not partner.become_lead_date:
                    partner.become_lead_date = datetime.datetime.now()
                if not partner.become_prospect_date:
                    partner.become_prospect_date = datetime.datetime.now()


class LeadSMSP(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)
        if res.partner_id and res.partner_id.become_prospect_date == False:
            partner = res.partner_id
            partner.write({'become_prospect_date': res.create_date,
                           'lifecycle_stage': 'prospect'})
            if partner.become_lead_date == False:
                partner.write({'become_lead_date': res.create_date})
        return res

    def write(self, vals):
        # write_result = super(Lead, self).write(vals)
        if vals.get('partner_id'):
            old_partner = self.partner_id
            if old_partner.opportunity_count <= 1 and old_partner.lifecycle_stage != 'customer':
                old_partner.write({'become_prospect_date': None,
                                   'lifecycle_stage': 'lead'})

        write_result = super().write(vals)

        if self.partner_id and self.partner_id.become_prospect_date == False:
            partner = self.partner_id
            partner.write({'become_prospect_date': self.create_date,
                           'lifecycle_stage': 'prospect'})
            if partner.become_lead_date == False:
                partner.write({'become_lead_date': self.create_date})

        return write_result

    def unlink(self):
        old_partner = self.partner_id
        if old_partner.opportunity_count <= 1 and old_partner.lifecycle_stage != 'customer':
            old_partner.write({'become_prospect_date': None,
                               'lifecycle_stage': 'lead'})
        return super().unlink()


class SaleOrderSMSP(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super().action_confirm()
        if self.partner_id.become_customer_date == False:
            partner = self.partner_id
            become_lc_date = self.date_order
            partner.write({'become_customer_date': become_lc_date,
                           'lifecycle_stage': 'customer'})
            if partner.become_prospect_date == False:
                partner.write({'become_prospect_date': become_lc_date})
            if partner.become_lead_date == False:
                partner.write({'become_lead_date': become_lc_date})
        return res

    def action_cancel(self):
        old_partner = self.partner_id
        so_count = self.env['sale.order'].search_count(
            [('partner_id', '=', self.partner_id.id),
             ('state', '=', 'sale')])

        if so_count <= 1 and old_partner.become_customer_date.strftime("%Y-%m-%d %H:%M:%S") == self.date_order.strftime("%Y-%m-%d %H:%M:%S"):
            old_partner.write({'become_customer_date': None,
                               'lifecycle_stage': 'prospect'})
        elif so_count > 1 and old_partner.become_customer_date.strftime("%Y-%m-%d %H:%M:%S") == self.date_order.strftime("%Y-%m-%d %H:%M:%S"):
            so = self.env['sale.order'].search(
                [('partner_id', '=', self.partner_id.id),
                 ('state', '=', 'sale')], order="date_order asc")
            old_partner.write({'become_customer_date': so[1].date_order})
            if old_partner.become_prospect_date.strftime("%Y-%m-%d %H:%M:%S") == self.date_order.strftime("%Y-%m-%d %H:%M:%S"):
                old_partner.write({'become_prospect_date': so[1].date_order})
        if old_partner.opportunity_count < 1 and old_partner.become_prospect_date.strftime("%Y-%m-%d %H:%M:%S") == self.date_order.strftime("%Y-%m-%d %H:%M:%S") and old_partner.lifecycle_stage == 'prospect':
            old_partner.write({'become_prospect_date': None,
                               'lifecycle_stage': 'lead'})

        res = super().action_cancel()
        return res
