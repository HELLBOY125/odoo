# -*- coding: utf-8 -*-
from odoo import http

# class SpcHrContract(http.Controller):
#     @http.route('/spc_hr_contract/spc_hr_contract/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/spc_hr_contract/spc_hr_contract/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('spc_hr_contract.listing', {
#             'root': '/spc_hr_contract/spc_hr_contract',
#             'objects': http.request.env['spc_hr_contract.spc_hr_contract'].search([]),
#         })

#     @http.route('/spc_hr_contract/spc_hr_contract/objects/<model("spc_hr_contract.spc_hr_contract"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('spc_hr_contract.object', {
#             'object': obj
#         })