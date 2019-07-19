from odoo import models, fields, api
import http.client
import base64
import io
import logging
import requests
from odoo.exceptions import Warning
_logger = logging.getLogger(__name__)  # Need for message in console.

class ProjectTaskBim(models.Model):
    """docstring for ProjectTaskBim."""
    _name = 'project.task.bim'
    name = fields.Char("模型名称", required=True)
    version = fields.Char("模型版本", required=True,default='1.0')
    description = fields.Char("描述")
    task_ids = fields.Many2many('project.task', string='任务')
    user_id =  fields.Many2one('res.users','Current User', default=lambda self: self.env.user)
    bim = fields.Char("BIM模型文件")

    @api.model
    def create(self, values):
        _logger.info(values)
        res_id = super(ProjectTaskBim, self).create(values)
        return res_id


class ProjectTask(models.Model):
    _name = 'project.task'
    _inherit = 'project.task'

    bim = fields.Integer(string='Bim', default=False)
    bim_ids = fields.Many2many('project.task.bim', string='Bims')


    def _task_bim_add(self, task, vals, bim_name):

        if "bim_vals" in task.keys() and task["bim_vals"]:
            bim_data = task["bim_vals"]
            bim_data["name"] = bim_name
            task_bim_lines = [(0, 0, bim_data)]
            vals["bim_ids"] = task_bim_lines
        return vals

    def _task_bim_remove(self, bim_name):
        domain = [('name', '=', bim_name)]
        result = self.env['project.task.bim'].sudo().search(domain)
        if result:
            result.unlink()
