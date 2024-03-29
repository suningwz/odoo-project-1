# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
from odoo.exceptions import UserError, ValidationError
from ..settings import CONTACT_CONNECTOR_API

import datetime
import phonenumbers
import re
import requests
import uuid


class IndustrySMSP(models.Model):
    _name = 'industry.smsp'
    _description = 'Contact Industry'
    name = fields.Char(
        'Name', index=True, readonly=False, store=True)


class GroupContactSMSP(models.Model):
    _name = 'group.contact.smsp'
    _description = 'Group Contact'
    name = fields.Char(
        'Name', index=True, readonly=False, store=True)


class ContactSMSP(models.Model):
    _inherit = 'res.partner'

    kelurahan = fields.Char('Kelurahan', index=False, readonly=False, store=True)
    kecamatan = fields.Char('Kecamatan', index=False, readonly=False, store=True)

    business_entity = fields.Selection([
        ('Perorangan', 'Perorangan'),
        ('Toko', 'Toko'),
        ('CV.', 'CV.'),
        ('PT.', 'PT.'),
        ('UD.', 'UD.'),
        ('FA.', 'FA.')], string='Business Entity',
        default='Perorangan', store=True)
    industry_smsp = fields.Many2many(comodel_name='industry.smsp', string='Industry')
    accurate_id = fields.Char(
        'Accurate ID', index=True, readonly=False, store=True)

    company_group = fields.Many2one(comodel_name='res.partner', string='Company Group')
    lifecycle_stage = fields.Selection([
        ('visitor', 'Visitor'),
        ('lead', 'Lead'),
        ('prospect', 'Prospect'),
        ('customer', 'Customer')], string='lifecycle Stage',
        default='lead', store=True)
    become_visitor_date = fields.Datetime(
        'Become Visitor Date', index=True, store=True, readonly=False,
        compute='_compute_visitor_date')
    become_lead_date = fields.Datetime(
        'Become Lead Date', index=True, store=True, readonly=False,
        compute='_compute_lead_date')
    become_prospect_date = fields.Datetime(
        'Become Prospect Date', index=True, store=True, readonly=False,
        compute='_compute_prospect_date')
    become_customer_date = fields.Datetime(
        'Become Customer Date', index=True, store=True, readonly=False,
        compute='_compute_customer_date')

    utm_source = fields.Selection([
        ('google', 'Google'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('twitter', 'Twitter'),
        ('pinterest', 'Pinterest'),
        ('linkedin', 'LinkedIn'),
        ('tokopedia', 'Tokopedia'),
        ('newsletter', 'Newsletter'),
        ('outbound', 'Outbound'),
        ('referral', 'Referral'),
        ('direct', 'Direct')],
        string='UTM Source', index=True, readonly=False, store=True)
    utm_medium = fields.Selection([
        ('cpc', 'CPC'),
        ('display', 'Display'),
        ('search', 'Search'),
        ('email', 'E-mail'),
        ('social', 'Social'),
        ('blog', 'Blog'),
        ('canvasing', 'Canvasing'),
        ('phone', 'Phone')],
        string='UTM Medium', index=True, readonly=False, store=True)
    utm_campaign = fields.Char(
        'UTM Campaign', index=True, readonly=False, store=True)
    utm_term = fields.Char(
        'UTM Term', index=True, readonly=False, store=True)
    chatwoot_id = fields.Char(
        'Chatwoot ID', index=True, readonly=False, store=True)
    group = fields.Many2one('group.contact.smsp', string='Group', ondelete='set null', index=True, copy=False)
    # teddy = fields.Char(
    #     'TEDDY', index=True, readonly=False, store=True)

    # _sql_constraints = [
    #     ('email_phone_uniq', 'unique (email,phone)', 'The email and phone must be unique for each customer !'),
    # ]

    _sql_constraints = [
        ('email_phone_uniq', 'Check(1=1)', 'The email and phone must be unique for each customer !'),
    ]

    @api.model
    def create(self, vals_list):
        """Phone Validation."""
        phone = vals_list.get('phone')
        if phone:
            try:
                if not self.check_phonenumber(phone):
                    raise ValidationError('Not a valid Phone')
            except Exception as e:
                raise ValidationError(str(e))

        """Email Validation."""
        email = vals_list.get('email')
        if email:
            match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email)
            if match is None:
                raise ValidationError('Not a valid E-mail')

        """Duplicate Email and Phone Validation."""
        if phone is None:
            phone = False
        if email is None:
            email = False
        dup = self.env['res.partner'].search(
            [('phone', '=', phone),
             ('email', '=', email),
             ('is_company', '=', False)])
        if len(dup) > 0 and not vals_list.get('is_company'):
            raise ValidationError("Email and phone must be unique!")
        else:
            partner = super().create(vals_list)
            data = self.env['res.partner'].search_read(
                [('id', '=', partner.id)],
                [
                    'id', 'name', 'email', 'phone', 'lifecycle_stage',
                    'become_visitor_date', 'become_lead_date',
                    'become_prospect_date', 'become_customer_date',
                    'utm_source', 'utm_term', 'utm_medium', 'utm_campaign'
                ]
            )
            result = data[0]
            result['method'] = 'create'
            if result.get('become_visitor_date'):
                result['become_visitor_date'] = str(result['become_visitor_date'])
            if result.get('become_lead_date'):
                result['become_lead_date'] = str(result['become_lead_date'])
            if result.get('become_prospect_date'):
                result['become_prospect_date'] = str(result['become_prospect_date'])
            if result.get('become_customer_date'):
                result['become_customer_date'] = str(result['become_customer_date'])

            # Send to contact connector service API
            try:
                url = CONTACT_CONNECTOR_API
                requests.post(url, json=result[0])
            except Exception:
                pass

            return partner

    def write(self, vals):
        """Phone Validation."""
        phone = vals.get('phone')
        if phone:
            try:
                if not self.check_phonenumber(phone):
                    raise ValidationError('Not a valid Phone')
            except Exception as e:
                raise ValidationError(str(e))

        """Email Validation."""
        email = vals.get('email')
        if email:
            match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email)
            if match is None:
                raise ValidationError('Not a valid E-mail')

        """Duplicate Email and Phone Validation."""
        is_email_phone_change = True
        if phone is None:
            phone = False
        if email is None:
            email = False
        if not (vals.get('phone') or vals.get('email')):
            is_email_phone_change = False
        is_company = vals.get('is_company')
        if not is_company:
            is_company = self.is_company
        dup = self.env['res.partner'].search(
            [('phone', '=', phone),
             ('email', '=', email),
             ('is_company', '=', False)])
        if len(dup) > 0 and not is_company and is_email_phone_change:
            raise ValidationError("Email and phone must be unique!")
        else:
            partner = super().write(vals)
            data = self.env['res.partner'].search_read(
                [('id', '=', self.id)],
                [
                    'id', 'name', 'email', 'phone', 'lifecycle_stage',
                    'become_visitor_date', 'become_lead_date',
                    'become_prospect_date', 'become_customer_date',
                    'utm_source', 'utm_term', 'utm_medium', 'utm_campaign'
                ]
            )
            if len(data) > 0:
                result = data[0]
                result['method'] = 'update'

                if result.get('become_visitor_date'):
                    result['become_visitor_date'] = str(result['become_visitor_date'])
                if result.get('become_lead_date'):
                    result['become_lead_date'] = str(result['become_lead_date'])
                if result.get('become_prospect_date'):
                    result['become_prospect_date'] = str(result['become_prospect_date'])
                if result.get('become_customer_date'):
                    result['become_customer_date'] = str(result['become_customer_date'])

                print(result)
                # Send to contact connector service API
                try:
                    url = CONTACT_CONNECTOR_API
                    resp = requests.post(url, json=result)
                    print(resp)
                except Exception as e:
                    print(e)
            return partner

    def convert_phonenumber(self, phonenumber):
        if phonenumber[0] == '0':
            phonenumber = '+62' + phonenumber[1:]
        x = phonenumbers.parse(phonenumber, 'ID')
        return phonenumbers.format_number(
            x,
            phonenumbers.PhoneNumberFormat.INTERNATIONAL
        )

    def check_phonenumber(self, phonenumber):
        pn = self.convert_phonenumber(phonenumber)
        x = phonenumbers.parse(pn, 'ID')
        is_possible = phonenumbers.is_possible_number(x)
        is_valid = phonenumbers.is_valid_number(x)
        if is_possible and is_valid:
            return True
        else:
            return False

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

    expected_tonnage = fields.Float(string='Expected Tonnage', default=0.0)
    utm_source = fields.Selection([
        ('google', 'Google'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('twitter', 'Twitter'),
        ('pinterest', 'Pinterest'),
        ('linkedin', 'LinkedIn'),
        ('tokopedia', 'Tokopedia'),
        ('newsletter', 'Newsletter'),
        ('outbound', 'Outbound'),
        ('referral', 'Referral'),
        ('direct', 'Direct')],
        string='UTM Source', index=True, readonly=False, store=True)
    utm_medium = fields.Selection([
        ('cpc', 'CPC'),
        ('display', 'Display'),
        ('search', 'Search'),
        ('email', 'E-mail'),
        ('social', 'Social'),
        ('blog', 'Blog'),
        ('canvasing', 'Canvasing'),
        ('phone', 'Phone')],
        string='UTM Medium', index=True, readonly=False, store=True)
    utm_campaign = fields.Char(
        'UTM Campaign', index=True, readonly=False, store=True)
    utm_term = fields.Char(
        'UTM Term', index=True, readonly=False, store=True)

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

    # def unlink(self):
    #     old_partner = self.partner_id
    #     if old_partner.opportunity_count <= 1 and old_partner.lifecycle_stage != 'customer':
    #         old_partner.write({'become_prospect_date': None,
    #                            'lifecycle_stage': 'lead'})
    #     return super().unlink()

    def _prepare_customer_values(self, partner_name, is_company=False, parent_id=False):
        """ Extract data from lead to create a partner.

        :param name : furtur name of the partner
        :param is_company : True if the partner is a company
        :param parent_id : id of the parent partner (False if no parent)

        :return: dictionary of values to give at res_partner.create()
        """
        email_split = tools.email_split(self.email_from)
        res = {
            'name': partner_name,
            'user_id': self.env.context.get('default_user_id') or self.user_id.id,
            'comment': self.description,
            'team_id': self.team_id.id,
            'parent_id': parent_id,
            'phone': self.phone,
            'mobile': self.mobile,
            'email': email_split[0] if email_split else False,
            'title': self.title.id,
            'function': self.function,
            'street': self.street,
            'street2': self.street2,
            'zip': self.zip,
            'city': self.city,
            'country_id': self.country_id.id,
            'state_id': self.state_id.id,
            'website': self.website,
            'utm_source': self.utm_source,
            'utm_medium': self.utm_medium,
            'utm_term': self.utm_term,
            'utm_campaign': self.utm_campaign,
            'is_company': is_company,
            'type': 'contact'
        }
        if self.lang_id:
            res['lang'] = self.lang_id.code

        res = super()._prepare_customer_values(partner_name, is_company=is_company, parent_id=parent_id)
        return res


class SaleOrderSMSP(models.Model):
    _inherit = 'sale.order'

    is_complete_delivered = fields.Boolean(string='Complete Received?', compute='_compute_is_complete_delivered', help='It indicates all of the products in SO has been fully delivered or not.', readonly=True, store=False)
    total_weight = fields.Float(string='Total Weight', compute='_compute_total_weight', default=0.0)

    @api.depends('order_line')
    def _compute_total_weight(self):
        for record in self:
            all_lines = record.order_line
            total = 0
            for l in all_lines:
                total =  total + (l.product_id.weight * l.product_uom_qty)
            record.total_weight = total

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

    def _compute_is_complete_delivered(self):
        for record in self:
            all_lines = record.order_line
            delivered = True
            for l in all_lines:
                if l.product_uom_qty != l.qty_delivered:
                    delivered = False
                    record.is_complete_delivered = False
                    break

            if delivered:
                record.is_complete_delivered = True


class StockMoveLineSMSP(models.Model):
    _inherit = 'stock.move.line'

    over_quantity = fields.Boolean(string='Over Quantity?', compute='_compute_over_quantity', help='It indicates this line of product is about to move out while the quantity in source location is not enough.')

    @api.depends('product_id.stock_quant_ids', 'qty_done')
    def _compute_over_quantity(self):
        for record in self:
            all_quants = record.product_id.stock_quant_ids
            record.over_quantity = False
            found = False
            for q in all_quants:
                if q.location_id == record.location_id and q.lot_id == record.lot_id:
                    found = True
                    record.over_quantity = record.qty_done > q.quantity
            if found == False:
                record.over_quantity = record.qty_done > 0


class StockPickingSMSP(models.Model):
    _inherit = 'stock.picking'

    over_quantity = fields.Boolean(string='Over Quantity?', compute='_compute_over_quantity', help='It indicates there is at least 1 moving out product which more than the stock in source location.', readonly=False)
    over_credit = fields.Boolean(string='Over Credit?', compute='_compute_over_credit', help='It indicates this contact has more credit limit that it should be.', readonly=False)
    has_overdue = fields.Boolean(string='Has Overdue?', compute='_compute_has_overdue', help='It indicates this contact has 1 or more overdue invoices.', readonly=False)

    @api.depends('move_line_ids_without_package')
    def _compute_over_quantity(self):
        for record in self:
            all_quants = record.move_line_ids_without_package
            record.over_quantity = False
            for q in all_quants:
                if q.over_quantity:
                    record.over_quantity = q.over_quantity
                    break

            if record.picking_type_id.name == 'Receipts':
                record.over_quantity = False

    @api.depends('partner_id')
    def _compute_over_credit(self):
        for record in self:
            limit = 0
            used_credit = 0

            if record.partner_id.parent_id:
                company = record.partner_id.parent_id
                limit = company.credit_limit
                used_credit = company.credit
                if company.company_group:
                    limit = company.company_group.credit_limit
                    companies = self.env['res.partner'].search([('company_group', '=', company.company_group.id)])
                    used_credit = 0
                    for c in companies:
                        used_credit = used_credit + c.credit
            else:
                limit = record.partner_id.credit_limit
                used_credit = record.partner_id.credit

            for ol in record.sale_id.order_line:
                if ol.product_uom_qty != 0:
                    used_credit += (ol.price_subtotal/ol.product_uom_qty)*(ol.product_uom_qty-ol.qty_invoiced)+0.1*(ol.price_subtotal/ol.product_uom_qty)*(ol.product_uom_qty-ol.qty_invoiced)
            for inv in record.sale_id.invoice_ids:
                if inv.state == 'draft':
                    used_credit += inv.amount_total
            record.over_credit = used_credit > limit

    @api.depends('partner_id')
    def _compute_has_overdue(self):
        for record in self:
            record.has_overdue = record.partner_id.total_overdue > 0
            # record.has_overdue = 1 == 0

    def button_validate(self):
        self._compute_over_quantity()
        # self._compute_over_credit()
        # self._compute_has_overdue()

        # if self.over_quantity or self.over_credit or self.has_overdue:
        if self.over_quantity:
            raise ValidationError("Check the quantity or credit or overdue!")
        else:
            res = super().button_validate()
            return res


class PurchaseOrderSMSP(models.Model):
    _inherit = 'purchase.order'

    is_complete_received = fields.Boolean(string='Complete Received?', compute='_compute_is_complete_received', help='It indicates all of the products in PO has been fully delivered or not.', readonly=True, store=False)
    total_weight = fields.Float(string='Total Weight', compute='_compute_total_weight', default=0.0)

    @api.depends('order_line')
    def _compute_total_weight(self):
        for record in self:
            all_lines = record.order_line
            total = 0
            for l in all_lines:
                total =  total + (l.product_id.weight * l.product_qty)
            record.total_weight = total

    def _compute_is_complete_received(self):
        for record in self:
            all_lines = record.order_line
            received = True
            for l in all_lines:
                if l.product_qty != l.qty_received:
                    received = False
                    record.is_complete_received = False
                    break

            if received:
                record.is_complete_received = True


class AccountMoveLineSMSP(models.Model):
    _inherit = 'account.move.line'

    posted_cost = fields.Float(string='Posted Cost', digits='Product Price', default=0.0)
    posted_total_cost = fields.Float(string='Posted Total Cost', digits='Product Price', default=0.0)


class AccountMoveSMSP(models.Model):
    _inherit = 'account.move'

    total_weight = fields.Float(string='Total Weight', compute='_compute_total_weight', default=0.0)

    @api.depends('invoice_line_ids')
    def _compute_total_weight(self):
        for record in self:
            all_lines = record.invoice_line_ids
            total = 0
            for l in all_lines:
                total =  total + (l.product_id.weight * l.quantity)
            record.total_weight = total

    def action_post(self):
        for record in self:
            all_lines = record.invoice_line_ids
            for l in all_lines:
                l.posted_cost = l.product_id.standard_price
                l.posted_total_cost = l.posted_cost * l.quantity
        res = super().action_post()
        return res


class ProductSMSP(models.Model):
    _inherit = 'product.template'

    accurate_id = fields.Char(
        'Accurate ID', index=True, readonly=False, store=True)
    sku_number = fields.Char(
        'SKU Number', index=True, readonly=False, store=True)
    weight_theoretical = fields.Float(compute='_compute_weight_theoretical', string='Weight Theoretical', store=True, readonly=False, default=0.0)
    classification = fields.Selection([
        ('S', 'S'),
        ('A', 'A'),
        ('B', 'B')],
        compute='_compute_classification',
        string='Classification',
        default=None, store=True, readonly=False)

    @api.depends('product_variant_id.weight_theoretical')
    def _compute_weight_theoretical(self):
        for record in self:
            if record.weight_theoretical != record.product_variant_id.weight_theoretical and record.product_variant_count <= 1 and record.product_variant_id.weight_theoretical > 0:
                record.weight_theoretical = record.product_variant_id.weight_theoretical

    @api.depends('product_variant_id.classification')
    def _compute_classification(self):
        for record in self:
            if record.classification != record.product_variant_id.classification and record.product_variant_count <= 1 and record.product_variant_id.classification is not None:
                record.classification = record.product_variant_id.classification


class ProductVariantSMSP(models.Model):
    _inherit = 'product.product'

    accurate_id = fields.Char(
        'Accurate ID', index=True, readonly=False, store=True)
    weight_theoretical = fields.Float(compute='_compute_weight_theoretical', string='Weight Theoretical', store=True, readonly=False, default=0.0)
    classification = fields.Selection([
        ('S', 'S'),
        ('A', 'A'),
        ('B', 'B')],
        compute='_compute_classification',
        string='Classification',
        default=None, store=True, readonly=False)

    @api.depends('product_tmpl_id.weight_theoretical')
    def _compute_weight_theoretical(self):
        for record in self:
            if record.weight_theoretical != record.product_tmpl_id.weight_theoretical and record.product_tmpl_id.product_variant_count <= 1:
                record.weight_theoretical = record.product_tmpl_id.weight_theoretical

    @api.depends('product_tmpl_id.classification')
    def _compute_classification(self):
        for record in self:
            if record.classification != record.product_tmpl_id.classification and record.product_tmpl_id.product_variant_count <= 1:
                record.classification = record.product_tmpl_id.classification

    @api.model
    def create(self, vals_list):
        # The vals_list value is different depending on the model is created.
        # Create automatically from product.template
        if vals_list.get('product_tmpl_id'):
            product = self.env['product.template'].search_read(
                [('id', '=', vals_list.get('product_tmpl_id'))]
            )[0]
            cat_id = product.get('categ_id')[0]  # get the id in index 0
            weight_t = product.get('weight_theoretical')
            classi = product.get('classification')
            default_code = ''
            cat_prefix = ''
            list_cat_code = []

            # Generate category prefix based on its category.
            while True:
                category = self.env['product.category'].search_read(
                    [('id', '=', cat_id)],
                    ['id', 'code', 'parent_id']
                )
                if not category[0]['code']:
                    raise Exception(
                        'The category must be have a code. Category "{}" '
                        'does not have a code'.format(category[0]['name'])
                    )
                if not category[0].get('parent_id'):
                    list_cat_code.append(category[0]['code'])
                    break
                else:
                    list_cat_code.append(category[0]['code'])
                    cat_id = category[0]['parent_id'][0]

            # Reverse the list, so we get from root of the category.
            desc_list = sorted(list_cat_code, reverse=True)
            taken_code = 3
            for i in range(0, taken_code):
                if i > len(desc_list)-1:
                    cat_prefix += '00'
                else:
                    cat_prefix += desc_list[i]

            # Generate 4 digit hash.
            str_hash = str(uuid.uuid4())[:4]
            default_code = cat_prefix + str_hash

            # Check existing default code
            while True:
                existing_default_code = self.env['product.product'].search(
                    [('default_code', '=', default_code)]
                )
                if not existing_default_code:
                    break
                else:
                    str_hash = str(uuid.uuid4())[:4]
                    default_code = cat_prefix + str_hash

            vals_list['default_code'] = default_code.upper()
            vals_list['weight_theoretical'] = weight_t
            vals_list['classification'] = classi

        # Update from product.product
        if not vals_list.get('default_code'):
            # VIDN / default code is contain:
            # category prefix 6 digit + hash 4 digit
            default_code = ''
            cat_prefix = ''
            list_cat_code = []
            cat_id = vals_list.get('categ_id')

            # Generate category prefix based on its category.
            while True:
                category = self.env['product.category'].search_read(
                    [('id', '=', cat_id)],
                    ['id', 'code', 'parent_id']
                )
                if not category[0]['code']:
                    raise Exception(
                        'The category must be have a code. Category "{}" '
                        'does not have a code'.format(category[0]['name'])
                    )
                if not category[0].get('parent_id'):
                    list_cat_code.append(category[0]['code'])
                    break
                else:
                    list_cat_code.append(category[0]['code'])
                    cat_id = category[0]['parent_id'][0]

            # Reverse the list, so we get from root of the category.
            desc_list = sorted(list_cat_code, reverse=True)
            taken_code = 3
            for i in range(0, taken_code):
                if i > len(desc_list)-1:
                    cat_prefix += '00'
                else:
                    cat_prefix += desc_list[i]

            # Generate 4 digit hash.
            str_hash = str(uuid.uuid4())[:4]
            default_code = cat_prefix + str_hash

            # Check existing default code
            while True:
                existing_default_code = self.env['product.product'].search(
                    [('default_code', '=', default_code)]
                )
                if not existing_default_code:
                    break
                else:
                    str_hash = str(uuid.uuid4())[:4]
                    default_code = cat_prefix + str_hash

            vals_list['default_code'] = default_code.upper()

        res = super().create(vals_list)
        return res

    def write(self, vals):
        if len(self) <= 1:
            if not self.default_code:
                # VIDN / default code is contain:
                # category prefix 6 digit + hash 4 digit
                default_code = ''
                cat_prefix = ''
                list_cat_code = []
                cat_id = self.categ_id.id

                # Generate category prefix based on its category.
                while True:
                    category = self.env['product.category'].search_read(
                        [('id', '=', cat_id)],
                        ['id', 'name', 'code', 'parent_id']
                    )
                    if not category[0]['code']:
                        raise Exception(
                            'The category must be have a code. Category "{}" '
                            'does not have a code'.format(category[0]['name'])
                        )
                    if not category[0].get('parent_id'):
                        list_cat_code.append(category[0]['code'])
                        break
                    else:
                        list_cat_code.append(category[0]['code'])
                        cat_id = category[0]['parent_id'][0]

                # Reverse the list, so we get from root of the category.
                desc_list = sorted(list_cat_code, reverse=True)
                taken_code = 3
                for i in range(0, taken_code):
                    if i > len(desc_list)-1:
                        cat_prefix += '00'
                    else:
                        cat_prefix += desc_list[i]

                # Generate 4 digit hash.
                str_hash = str(uuid.uuid4())[:4]
                default_code = cat_prefix + str_hash

                # Check existing default code
                while True:
                    existing_default_code = self.env['product.product'].search(
                        [('default_code', '=', default_code)]
                    )
                    if not existing_default_code:
                        break
                    else:
                        str_hash = str(uuid.uuid4())[:4]
                        default_code = cat_prefix + str_hash

                vals['default_code'] = default_code.upper()

        res = super().write(vals)
        return res


class ManufactureSMSP(models.Model):
    _inherit = 'mrp.production'

    over_quantity = fields.Boolean(string='Over Quantity?', compute='_compute_over_quantity', help='It indicates this line of product is about to be consumed while the quantity in source location is not enough.', readonly=False)

    @api.depends('move_raw_ids')
    def _compute_over_quantity(self):
        for record in self:
            all_quants = record.move_raw_ids.move_line_ids
            record.over_quantity = False
            for q in all_quants:
                if q.over_quantity:
                    record.over_quantity = q.over_quantity
                    break


class ProductCategorySMSP(models.Model):
    _inherit = 'product.category'

    code = fields.Char(
        'Code', index=True, readonly=False, store=True)

    @api.model
    def create(self, vals_list):
        if vals_list.get('code') is False:
            if vals_list.get('parent_id'):
                # Code will be filled in with sequence of number
                code = 1
                while True:
                    existing_code = self.env['product.category'].search(
                        [('parent_id', '=', vals_list.get('parent_id')),
                         ('code', '=', str(code).zfill(2))])
                    if len(existing_code) == 0:
                        break
                    else:
                        if code == 1:
                            total = len(self.env['product.category'].search(
                                [
                                    (
                                        'parent_id',
                                        '=',
                                        vals_list.get('parent_id')
                                    )
                                ]
                            ))
                            code = total + 1
                        else:
                            code += 1

                # Set code to string and convert to '0(code)' with zfill.
                code = str(code).zfill(2)
                vals_list['code'] = code
            else:
                code = vals_list.get('name')[:2].upper()
                vals_list['code'] = code
        else:
            vals_list['code'] = vals_list['code'].upper()

        res = super().create(vals_list)
        return res

    def write(self, vals):
        if self.code is False and not vals.get('code'):
            if self.parent_id:
                # Code will be filled in with sequence of number
                code = 1
                while True:
                    existing_code = self.env['product.category'].search(
                        [('parent_id', '=', self.parent_id.id),
                         ('code', '=', str(code).zfill(2))])
                    if len(existing_code) == 0:
                        break
                    else:
                        if code == 1:
                            total = len(self.env['product.category'].search(
                                [
                                    (
                                        'parent_id',
                                        '=',
                                        self.parent_id.id
                                    )
                                ]
                            ))
                            code = total + 1
                        else:
                            code += 1

                # Set code to string and convert to '0(code)' with zfill.
                code = str(code).zfill(2)
                vals['code'] = code
            else:
                code = self.name[:2].upper()
                vals['code'] = code
        if vals.get('code'):
            vals['code'] = vals['code'].upper()
        write_result = super().write(vals)
        return write_result


class EmployeeSMSP(models.Model):
    _inherit = 'hr.employee'

    taxpayer_number = fields.Char(string='Taxpayer Identification Number', help='NPWP')
    stratum = fields.Selection([
        ('S1L1', 'Stratum 1 - Low - 1'),
        ('S1L2', 'Stratum 1 - Low - 2'),
        ('S1L3', 'Stratum 1 - Low - 3'),
        ('S1L4', 'Stratum 1 - Low - 4'),
        ('S1L5', 'Stratum 1 - Low - 5'),
        ('S1L6', 'Stratum 1 - Low - 6'),
        ('S1M1', 'Stratum 1 - Medium - 1'),
        ('S1M2', 'Stratum 1 - Medium - 2'),
        ('S1M3', 'Stratum 1 - Medium - 3'),
        ('S1M4', 'Stratum 1 - Medium - 4'),
        ('S1M5', 'Stratum 1 - Medium - 5'),
        ('S1M6', 'Stratum 1 - Medium - 6'),
        ('S1H1', 'Stratum 1 - High - 1'),
        ('S1H2', 'Stratum 1 - High - 2'),
        ('S1H3', 'Stratum 1 - High - 3'),
        ('S1H4', 'Stratum 1 - High - 4'),
        ('S1H5', 'Stratum 1 - High - 5'),
        ('S1H6', 'Stratum 1 - High - 6'),
        ('S2L1', 'Stratum 2 - Low - 1'),
        ('S2L2', 'Stratum 2 - Low - 2'),
        ('S2L3', 'Stratum 2 - Low - 3'),
        ('S2L4', 'Stratum 2 - Low - 4'),
        ('S2L5', 'Stratum 2 - Low - 5'),
        ('S2L6', 'Stratum 2 - Low - 6'),
        ('S2M1', 'Stratum 2 - Medium - 1'),
        ('S2M2', 'Stratum 2 - Medium - 2'),
        ('S2M3', 'Stratum 2 - Medium - 3'),
        ('S2M4', 'Stratum 2 - Medium - 4'),
        ('S2M5', 'Stratum 2 - Medium - 5'),
        ('S2M6', 'Stratum 2 - Medium - 6'),
        ('S2H1', 'Stratum 2 - High - 1'),
        ('S2H2', 'Stratum 2 - High - 2'),
        ('S2H3', 'Stratum 2 - High - 3'),
        ('S2H4', 'Stratum 2 - High - 4'),
        ('S2H5', 'Stratum 2 - High - 5'),
        ('S2H6', 'Stratum 2 - High - 6'),
        ('S3L1', 'Stratum 3 - Low - 1'),
        ('S3L2', 'Stratum 3 - Low - 2'),
        ('S3L3', 'Stratum 3 - Low - 3'),
        ('S3L4', 'Stratum 3 - Low - 4'),
        ('S3L5', 'Stratum 3 - Low - 5'),
        ('S3L6', 'Stratum 3 - Low - 6'),
        ('S3M1', 'Stratum 3 - Medium - 1'),
        ('S3M2', 'Stratum 3 - Medium - 2'),
        ('S3M3', 'Stratum 3 - Medium - 3'),
        ('S3M4', 'Stratum 3 - Medium - 4'),
        ('S3M5', 'Stratum 3 - Medium - 5'),
        ('S3M6', 'Stratum 3 - Medium - 6'),
        ('S3H1', 'Stratum 3 - High - 1'),
        ('S3H2', 'Stratum 3 - High - 2'),
        ('S3H3', 'Stratum 3 - High - 3'),
        ('S3H4', 'Stratum 3 - High - 4'),
        ('S3H5', 'Stratum 3 - High - 5'),
        ('S3H6', 'Stratum 3 - High - 6'),
        ('S4L1', 'Stratum 4 - Low - 1'),
        ('S4L2', 'Stratum 4 - Low - 2'),
        ('S4L3', 'Stratum 4 - Low - 3'),
        ('S4L4', 'Stratum 4 - Low - 4'),
        ('S4L5', 'Stratum 4 - Low - 5'),
        ('S4L6', 'Stratum 4 - Low - 6'),
        ('S4M1', 'Stratum 4 - Medium - 1'),
        ('S4M2', 'Stratum 4 - Medium - 2'),
        ('S4M3', 'Stratum 4 - Medium - 3'),
        ('S4M4', 'Stratum 4 - Medium - 4'),
        ('S4M5', 'Stratum 4 - Medium - 5'),
        ('S4M6', 'Stratum 4 - Medium - 6'),
        ('S4H1', 'Stratum 4 - High - 1'),
        ('S4H2', 'Stratum 4 - High - 2'),
        ('S4H3', 'Stratum 4 - High - 3'),
        ('S4H4', 'Stratum 4 - High - 4'),
        ('S4H5', 'Stratum 4 - High - 5'),
        ('S4H6', 'Stratum 4 - High - 6')], string='Stratum',
        default='S1L1', store=True)
