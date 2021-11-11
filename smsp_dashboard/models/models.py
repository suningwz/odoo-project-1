# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

import datetime
import time


class FunnelDashboard(models.Model):
    _name = 'funnel.dashboard'
    _description = 'funnel dashboard'

    date = fields.Datetime('Become Lifecycle Date', index=True)
    lifecycle_stage = fields.Char('Lifecycle Stage', index=True)
    total = fields.Integer('Total')
    utm_source = fields.Char('UTM Source', index=True)
    utm_medium = fields.Char('UTM Campaign', index=True)
    utm_source_medium = fields.Char('UTM Source/Medium', index=True)


class ContactDashboard(models.Model):
    _inherit = 'funnel.dashboard'

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
                   orderby=False, lazy=True):
        """
            Override read_group to calculate the sum of the lifecycle stage.
        """

        # start = time.perf_counter()
        # Delete all records first.
        funnel_data = self.env['funnel.dashboard'].search([])
        for funnel in funnel_data:
            funnel.unlink()

        # Get all source/medium
        self.env.cr.execute(
            """SELECT DISTINCT utm_source, utm_medium FROM res_partner"""
        )
        result = self.env.cr.fetchall()

        utm_source_medium_list = []
        for r in result:
            usm = ""
            # print(r)
            for x in r:
                if x is not None:
                    usm += x + "/"
                else:
                    usm += "" + "/"
            usm = usm[:len(usm)-1]
            utm_source_medium_list.append(usm)

        # Convert date to become_lc_date as a filter.
        visitor_dom = self.convert_to_contact_domain(
            domain, 'become_visitor_date')
        lead_dom = self.convert_to_contact_domain(domain, 'become_lead_date')
        prospect_dom = self.convert_to_contact_domain(
            domain, 'become_prospect_date')
        customer_dom = self.convert_to_contact_domain(
            domain, 'become_customer_date')

        # Remove date in domain to prevent date included in filter process.
        # domain result example:
        # ['&', ['date', '>=', '2021-09-30 17:00:00'], ['date', '<=',
        # '2021-10-31 16:59:59']]
        domain_copy = domain
        counter = 0
        while counter < len(domain_copy):
            if type(domain_copy[counter]) == list:
                for x in domain_copy[counter]:
                    if x == 'date':
                        del domain[counter-1:counter+2]
                        counter += 1
            counter += 1

        for utm in utm_source_medium_list:
            # print(utm)
            data = utm.split('/')

            # Append in lifecycle domain list (used as data filter)
            source, medium = None, None
            if data[0]:
                source = data[0]
            if data[1]:
                medium = data[1]
            visitor_dom.append(('utm_source', '=', source))
            visitor_dom.append(('utm_medium', '=', medium))
            lead_dom.append(('utm_source', '=', source))
            lead_dom.append(('utm_medium', '=', medium))
            prospect_dom.append(('utm_source', '=', source))
            prospect_dom.append(('utm_medium', '=', medium))
            customer_dom.append(('utm_source', '=', source))
            customer_dom.append(('utm_medium', '=', medium))

            # Create visitor
            # print(visitor_dom)
            visitor_res = self.env['res.partner'].search_read(visitor_dom)
            self.env['funnel.dashboard'].create({
                'lifecycle_stage': '1: visitor',
                'total': len(visitor_res),
                'utm_source': data[0],
                'utm_medium': data[1],
                'utm_source_medium': utm
            })
            # print('visitor:', utm, ': ', len(visitor_res))

            # Create lead
            # print(lead_dom)
            lead_res = self.env['res.partner'].search(lead_dom)
            # print('lead res', lead_res)
            self.env['funnel.dashboard'].create({
                'lifecycle_stage': '2: lead',
                'total': len(lead_res),
                'utm_source': data[0],
                'utm_medium': data[1],
                'utm_source_medium': utm
            })

            # Create prospect
            prospect_res = self.env['res.partner'].search(prospect_dom)
            self.env['funnel.dashboard'].create({
                'lifecycle_stage': '3: prospect',
                'total': len(prospect_res),
                'utm_source': data[0],
                'utm_medium': data[1],
                'utm_source_medium': utm
            })

            # Create customer
            customer_res = self.env['res.partner'].search(customer_dom)
            self.env['funnel.dashboard'].create({
                'lifecycle_stage': '4: customer',
                'total': len(customer_res),
                'utm_source': data[0],
                'utm_medium': data[1],
                'utm_source_medium': utm
            })

            # Remove 2 last data from each ls domain list.
            visitor_dom.pop()
            visitor_dom.pop()
            lead_dom.pop()
            lead_dom.pop()
            prospect_dom.pop()
            prospect_dom.pop()
            customer_dom.pop()
            customer_dom.pop()

        res = super().read_group(
            domain, fields, groupby, offset=offset, limit=limit,
            orderby=orderby, lazy=lazy
        )
        # end = time.perf_counter()
        # print('Time: ', end-start)
        return res

    def convert_to_contact_domain(self, domain, to_domain):
        if len(domain) == 0:
            # set default date value (avoid null value)
            domain = [
                (to_domain, '>=', '1999-01-31 00:00:00')
            ]

        new_domain = []
        for x in domain:
            if type(x) == list:
                new_term = []
                for y in x:
                    if y == 'date':
                        # replace "date" variable with to_domain
                        y = to_domain
                    new_term.append(y)
                x = new_term
            new_domain.append(x)
        new_domain.append(('is_company', '=', False))
        return new_domain
