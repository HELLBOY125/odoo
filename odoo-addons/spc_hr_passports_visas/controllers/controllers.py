# -*- coding: utf-8 -*-
from odoo import http

# class SpcHrPassportsVisas(http.Controller):
#     @http.route('/spc_hr_passports_visas/spc_hr_passports_visas/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/spc_hr_passports_visas/spc_hr_passports_visas/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('spc_hr_passports_visas.listing', {
#             'root': '/spc_hr_passports_visas/spc_hr_passports_visas',
#             'objects': http.request.env['spc_hr_passports_visas.spc_hr_passports_visas'].search([]),
#         })

#     @http.route('/spc_hr_passports_visas/spc_hr_passports_visas/objects/<model("spc_hr_passports_visas.spc_hr_passports_visas"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('spc_hr_passports_visas.object', {
#             'object': obj
#         })