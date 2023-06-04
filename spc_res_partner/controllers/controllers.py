# -*- coding: utf-8 -*-
# from odoo import http


# class SpcResPartner(http.Controller):
#     @http.route('/spc_res_partner/spc_res_partner/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/spc_res_partner/spc_res_partner/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('spc_res_partner.listing', {
#             'root': '/spc_res_partner/spc_res_partner',
#             'objects': http.request.env['spc_res_partner.spc_res_partner'].search([]),
#         })

#     @http.route('/spc_res_partner/spc_res_partner/objects/<model("spc_res_partner.spc_res_partner"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('spc_res_partner.object', {
#             'object': obj
#         })
