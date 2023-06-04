# -*- coding: utf-8 -*-


from odoo import api, fields, models

class ResConfigSettingsleaves(models.TransientModel):
    _inherit = 'res.config.settings'

    nb_hours_authorization_month = fields.Float(string="Exit authorization threshold per day",required=True)
    #nb_days_rtt = fields.Float(string="Maximum Number Of Days", readonly=False)
    
    
   
    
    
    
    
    
    
    
#     def set_values(self): 
#         res = super(ResConfigSettingsleaves, self).set_values() 
#         params = self.env["ir.config_parameter"].sudo() 
#         if self.nb_hours_authorization_month: 
#             params.set_param("spc_leaves.nb_hours_authorization_month", self.nb_hours_authorization_month) 
#         return res 
    def set_values(self): 
        res = super(ResConfigSettingsleaves, self).set_values() 
        params = self.env["ir.config_parameter"].sudo()  
        params.set_param("spc_leaves.nb_hours_authorization_month", self.nb_hours_authorization_month) 
        return res         
    @api.model 
    def get_values(self): 
        res = super(ResConfigSettingsleaves, self).get_values() 
        
        ICPSudo = self.env['ir.config_parameter'].sudo()
        nb_hours_authorization_month_value = float(ICPSudo.get_param('spc_leaves.nb_hours_authorization_month'))
        res.update(nb_hours_authorization_month=nb_hours_authorization_month_value) 
        return res        
    
#     @api.model
#     def get_values(self):
#         res = super(ResConfigSettingsleaves, self).get_values()
#         params = self.env["ir.config_parameter"].sudo()
#         nb_hours_authorization_month_value = params.get_param("spc_leaves.nb_hours_authorization_month")
#         res.update(nb_hours_authorization_month =nb_hours_authorization_month_value)
#         return res
    