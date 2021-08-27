# -*- coding: utf-8 -*-
# from odoo import http


# class SmspContactService(http.Controller):
#     @http.route('/smsp_contact_service/smsp_contact_service/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/smsp_contact_service/smsp_contact_service/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('smsp_contact_service.listing', {
#             'root': '/smsp_contact_service/smsp_contact_service',
#             'objects': http.request.env['smsp_contact_service.smsp_contact_service'].search([]),
#         })

#     @http.route('/smsp_contact_service/smsp_contact_service/objects/<model("smsp_contact_service.smsp_contact_service"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('smsp_contact_service.object', {
#             'object': obj
#         })
