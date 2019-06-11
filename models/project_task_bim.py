from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)  # Need for message in console.


class ProjectTaskBim(models.Model):
    """docstring for ProjectTaskBim."""
    _name = 'project.task.bim'
    name = fields.Char("模型名称")
    description = fields.Char("描述")
    size = fields.Integer("模型大小")
    file = fields.Char("模型文件")
    task_ids = fields.Many2many('project.task', string='Tasks')

    @api.multi
    def form_button_project_task_bim_add(self,str) :
        self.ensure_one()
        return str

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
