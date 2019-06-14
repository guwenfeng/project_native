from odoo import http

class BimController(http.Controller) :
    @http.route('/bim/create', auth='public')
    def createbim(self, **kw):
        # model = http.request.env['project.task.bim']
        text = '成功添加BIM模型'
        # try :
        #     model.sudo().create(kw)
        # except Exception:
        #     text = '创建BIM模型出现错误'
        return text
