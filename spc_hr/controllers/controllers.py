# -*- coding: utf-8 -*-
from odoo import http

# class SpcHr(http.Controller):
#     @http.route('/spc_hr/spc_hr/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/spc_hr/spc_hr/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('spc_hr.listing', {
#             'root': '/spc_hr/spc_hr',
#             'objects': http.request.env['spc_hr.spc_hr'].search([]),
#         })

#     @http.route('/spc_hr/spc_hr/objects/<model("spc_hr.spc_hr"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('spc_hr.object', {
#             'object': obj
#         })