from odoo import http

class BimController(http.Controller) :
    @http.route('/bim/create', auth='public')
    def createbim(self, **kw):
        return "ok"
