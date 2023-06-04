# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class AssetDepreciationConfirmationWizard(models.TransientModel):
    _name = "asset.depreciation.confirmation.wizard"
    _description = "asset.depreciation.confirmation.wizard"

    date = fields.Date('Account Date', required=True, help="Choose the period for which you want to automatically post the depreciation lines of running assets", default=fields.Date.context_today)

    
    def asset_compute(self):
        self.ensure_one()
        context = self._context
        created_move_ids = self.env['account.asset.asset'].compute_generated_entries(self.date, asset_type=context.get('asset_type'))

        return {
            'name': _('Created Asset Moves') if context.get('asset_type') == 'purchase' else _('Created Revenue Moves'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'domain': "[('id','in',[" + ','.join(str(id) for id in created_move_ids) + "])]",
            'type': 'ir.actions.act_window',
        }




class AssetAddConfirmationWizard(models.TransientModel):
    _name = "asset.add.confirmation.wizard"
    _description = "validation des ajouts des immobilisation wizard"

    def _get_date(self): 
        date= fields.date.today()
        print ('date_________',date)
        return "%s-12-31" %date.year

    date = fields.Date("Date de mise en service", required=True, default=fields.Date.context_today)
    first_depreciation_manual_date = fields.Date("Première date de dépréciation", required=True, default=_get_date)
    
    def add_asset(self):
        self.ensure_one()
        asset_ids=[]
        context = self._context
        print ('context__________',context)
        line =self.env['stock.immobilisation'].browse(context.get('active_id'))
        print ('stock_immo_____',line)
        if line.product_id.asset_category_id.multiple_assets_per_line:
            for line_qty in range(int(line.out_qty)):
                asset_id=self.asset_create(line)
                if asset_id :
                    self.create_affectation_asset(line,asset_id.id)
                    asset_id.is_generate=True
                    asset_ids.append(asset_id.id)
        else:
            asset_id= self.asset_create(line)
            if asset_id :
                self.create_affectation_asset(line,asset_id.id)
                asset_id.is_generate=True
                asset_ids.append(asset_id.id)
    
        line.asset_ids=[(6,0,asset_ids)] if asset_ids else False
        line.state='done' 
        self.create_allocation_asset(line,asset_ids)   
            
        return {
            'name': _('Génerer les Immobilisations'), 
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.asset.asset',
            'domain': [('id','in',asset_ids)],
            'type': 'ir.actions.act_window',
        }
        
    def asset_create(self,line):
        value=0
        asset=False
        print ('line______',line)
        if line.product_id.asset_category_id:
            if line.product_id.asset_category_id.multiple_assets_per_line:
                value= line.purchase_price
            else:
                value= line.purchase_price *line.out_qty
            vals = {
                'name': line.product_id.display_name,
                'code': line.product_id.display_name,
                'category_id': line.product_id.asset_category_id.id,
                'value': value,
                'partner_id': False,
                'company_id': self.env.company.id,
                'currency_id': self.env.ref('base.TND').id,
                'date': self.date,
                'date_acquisition':line.picking_in_id.date_done,
                'invoice_id': line.move_id.id,
                'invoice_line_id':line.move_line_id.id,
                'first_depreciation_manual_date':self.first_depreciation_manual_date,
            }
            changed_vals = self.env['account.asset.asset'].onchange_category_id_values(vals['category_id'])
            vals.update(changed_vals['value'])
            asset = self.env['account.asset.asset'].create(vals)
#             if line.product_id.asset_category_id.open_asset:
#                 asset.validate()
        return asset
    
    def create_affectation_asset(self,line,asset_id):
        vals={ 
               'direction_id':line.direction_id.id if line.direction_id else False,
                'name' :'%s-%s' %(line.out_id.name,line.picking_id.name),
                'asset_id':asset_id,  
                'date':fields.date.today(),
                
            }
        self.env['account.asset.affectation'].create(vals)
    
    def create_allocation_asset(self,line,asset_ids):
        vals={ 'department_id':line.department_id.id if line.department_id else False,
               'direction_id':line.direction_id.id if line.direction_id else False,
               'unite_id':line.unite_id.id if line.unite_id else False,
               'service_id':line.service_id.id if line.service_id else False,
                'origin' :'%s-%s' %(line.out_id.name,line.picking_id.name),
                'product_id':line.product_id.id,
                'product_uom_id':line.product_uom_id.id,
                'product_qty':line.out_qty,
                'state':'open',
                'asset_ids':[(6,0,asset_ids)],  
            }
        self.env['account.asset.allocation'].create(vals)
