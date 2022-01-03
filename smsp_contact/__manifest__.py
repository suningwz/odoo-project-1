# -*- coding: utf-8 -*-
{
    'name': "SMSP Setup",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        This is used to:
        - Add Lifecycle Stage in contact
        - Become certain Lifecycle date
        - Automatic update Lifecycle Stage and also become Lifecycle date
        - Add UTM Source, UTM Medium, UTM Campaign, UTM Term, and Chatwoot ID (readonly)
        - Add Leads (Contact) menu in CRM with its default filter
        - Add company group field
        - Add constrain unique together between email and phone
        - Move analyze data (UTM, LC, and become LC date) to a separate tab
        - Add Business Entity
        - Add Industry
        - Add Accurate ID
        - Add customer_rank and supplier_rank in Contact Form View
        - Add expected tonnage in CRM Form View
        - Add Group as m2o relationship in Contact Form View
        - Add validation email and phone
        - Add validation in create and update for duplicating email and phone
        - Make button validate invisible when there is a stock minus, over credit limit, and overdue invoice.
        - Add boolean variable in PO to check if all products in that PO is fully received or not
        - Add validation for non-negative stock in manufacture order (prevent mark as done when it's happened).
        - Add posted_cost and posted_total_cost to record cost for each invoice line at that time when the invoice has been posted.
        - Add Accurate ID in product variant and product form.
        - Add Total Weight in sale order.
        - Add Total Weight in purchase order.
        - Add Total Weight in account move (INV/BILL).
        - Override Sale Order Portal Content with our layout.
        - Add our own css for odoo print report.
        - Add Purchase Analysis and Invoice list in Purchase module.
        - Add SKU number in product.template
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'contacts', 'crm', 'sale', 'stock', 'purchase'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/override_crm.xml',
        'views/override_crm_lead.xml',
        'views/override_stock_picking.xml',
        'views/override_purchase_order.xml',
        'views/override_manufacture.xml',
        'views/override_product.xml',
        'views/override_sale_order.xml',
        'views/override_sale_order_portal_content.xml',
        'views/override_invoice_bill.xml',
        'views/override_web_report_layout.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
