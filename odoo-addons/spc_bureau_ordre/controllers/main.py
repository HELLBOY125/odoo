from openerp import http
from openerp.http import request
import base64
import os
from openerp.tools import topological_sort, tempfile
try:
    from tempfile import SpooledTemporaryFile
except ImportError:
    from tempfile import TemporaryFile
    SpooledTemporaryFile = None


from openerp import http, fields
from openerp.addons.web.controllers.main import Binary
from openerp.addons.web.controllers.main import serialize_exception, content_disposition

class Binary_inherit(Binary):
    file_new = fields.Binary()

    def content_disposition(filename):
        return super(Binary_inherit).content_disposition(filename)

    @http.route('/web/binary/saveas', type='http', auth="public")
    @serialize_exception
    def saveas(self, model, field, id=None, filename_field=None, *args, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        Model = request.registry[model]
        print('Model', Model)
        # if (model != 'ir.attachment'):
        print('.....not ir attachment.....',id,'.............',model)
        print('filename_field..........',filename_field)
        print('field........',field)
        node = http.request.env['ir.attachment'].search([('id','=',id)]).node_alfresco
        print('node.........',node)
        name = http.request.env['ir.attachment'].search([('id','=',id)]).datas_fname
        print('name file',name)
        print('node.....',node)
        repo = http.request.env['alfresco.configuration'].connection_alfresco_old_api()
        doc = repo.getObject(node)
        doc_content = doc.getContentStream()
        return request.make_response(doc_content,
                                     [('Content-Type', 'application/octet-stream'),
                                      ('Content-Disposition', content_disposition(name))])








class Courrier(http.Controller):

    @http.route('/api/ws/saveScannedDocument/',type='http',auth="public", website=True, methods=['POST'])
    def saveScannedDocument(self,idEntity,file,nature,typeEntity):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        env = request.env()
        # up_file_list = []
        a_file_name = file.filename

        # Build target
        full_path = '/tmp/'
        a_file_target = os.path.join(full_path,a_file_name)

        # Save file
        file.save(a_file_target)
        file_size = os.stat(a_file_target).st_size

        # up_file_list.append(a_file_name)
        r = open(a_file_target, 'rb').read().encode('base64')

        # model= env['ir.model'].sudo().browse(int(typeEntity)).model
        if str(typeEntity) == 'courrier.entrant':
            val={'name':a_file_name,
                  'datas_fname':a_file_name,
                 'file_size': file_size,
                 'type':'binary',
                 'res_id':idEntity,
                 'res_model':'courrier.entrant',
                 'datas':r,
                 }

            env['ir.attachment'].sudo().create(val)
            vals = {'auto_refresh': 'True'}
            env['courrier.entrant'].sudo().write(vals)




        if str(typeEntity) == 'courrier.sortant':
            val = {'name': a_file_name,
                   'datas_fname': a_file_name,
                   'file_size': file_size,
                   'type': 'binary',
                   'res_id': idEntity,
                   'res_model': 'courrier.sortant',
                   'datas': r,
                   }

            env['ir.attachment'].sudo().create(val)
            vals = {'auto_refresh': 'True'}
            env['courrier.sortant'].sudo().write(vals)

        # return {
        #     'type': 'ir.actions.act_window',
        #     'res_model': str(typeEntity),
        #     'view_mode': 'form',
        #     'view_type': 'form',
        #     'res_id': idEntity,
        #     'views': [(False, 'form')],
        #     'target': 'current',
        # }






