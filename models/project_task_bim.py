from odoo import models, fields, api
import http.client
import base64
import io
import logging
import requests
from odoo.exceptions import Warning
_logger = logging.getLogger(__name__)  # Need for message in console.


def getAllDeserializers() :
    try:
        url = "http://119.3.41.81:8081/bimserver/json"
        payload = "{\"request\":{\"interface\":\"org.bimserver.PluginInterface\",\"method\":\"getAllDeserializers\",\"parameters\":{\"onlyEnabled\":\"true\"}},\"token\":\"b6121d0067146650c2d193207b3931679bf6631df5f70e66c4b73b2ec107e388f5f328b3eab8a1144849c258858e692a\"}"
        headers = {
            'content-type': "application/json; charset=UTF-8"
            }
        response = requests.request("POST", url, data=payload, headers=headers)
        relist = response.json()['response']['result']
        return relist
    except:
        raise Warning('模型转换异常')
        return None

def addProject(projectName:str,deslist:list,uuid:str) :
    try:
        ifcDownloadUrl = 'http://172.16.0.129:8087/SmartCity/model/ifc/download/'
        for index in range(len(deslist)):
            obj =  deslist[index]
            if obj['name'] == 'Ifc2x3tc1 (Streaming)' :
                deserializerOid = obj['oid']
                url = "http://119.3.41.81:8081/bimserver/json"
                payload = "{\"request\":{\"interface\":\"org.bimserver.ServiceInterface\",\"method\":\"addProject\",\"parameters\":{\"projectName\":\""+projectName+"\",\"schema\":\"ifc2x3tc1\"}},\"token\":\"b6121d0067146650c2d193207b3931679bf6631df5f70e66c4b73b2ec107e388f5f328b3eab8a1144849c258858e692a\"}"
                headers = {
                    'content-type': "application/json; charset=UTF-8"
                }
                response = requests.request("POST", url, data=payload.encode(encoding='UTF-8',errors='strict'), headers=headers)
                js = response.json()
                _logger.info(js)
                checkinFromUrl(str(js["response"]["result"]['oid']),str(deserializerOid),uuid+'.ifc',ifcDownloadUrl + uuid)
    except:
        raise Warning('模型转换异常')

def checkinFromUrl(poid :str, deserializerOid :str, fileName :str, fileUrl :str) :
    try:
        url = "http://119.3.41.81:8081/bimserver/json"
        payload = "{\"request\":{\"interface\":\"org.bimserver.ServiceInterface\",\"method\":\"checkinFromUrl\",\"parameters\":{\"poid\":"+ poid+",\"comment\":\"\",\"deserializerOid\":"+ deserializerOid +",\"fileName\":\""+fileName+"\",\"url\":\""+ fileUrl +"\",\"merge\":false,\"sync\":true}},\"token\":\"b6121d0067146650c2d193207b3931679bf6631df5f70e66c4b73b2ec107e388f5f328b3eab8a1144849c258858e692a\"}"
        headers = {
            'content-type': "application/json; charset=UTF-8"
        }
        response = requests.request("POST", url, data=payload, headers=headers)
        js = response.json()
        _logger.info(js)
    except:
        raise  Warning('模型转换异常')

class ProjectTaskBim(models.Model):
    """docstring for ProjectTaskBim."""
    _name = 'project.task.bim'
    name = fields.Char("模型名称", required=True)
    version = fields.Char("模型版本", required=True,default='1.0')
    file = fields.Binary("模型文件")
    file_name = fields.Char("文件名")
    file_url = fields.Html("模型显示地址")
    description = fields.Char("描述")
    task_ids = fields.Many2many('project.task', string='任务')
    user_id =  fields.Many2one('res.users','Current User', default=lambda self: self.env.user)

    @api.model
    def create(self, values):

        # bim server host url
        bim_server_host = '119.3.40.108:8087'
        bim_server_url = '/SmartCity/model/ifc/upload'
        # decode file upload from odoo
        file_decode = base64.b64decode(values['file'])
        file_str = file_decode.decode()
        file_origin = io.BytesIO(file_decode)
        file_re = io.TextIOWrapper(file_origin)

        # request data init
        data = {
            "project":"27",
            "latitude":"31.24",
            "longitude":"121.47",
            "height":"0",
            "heading":"0",
            "pitch":"0",
            "roll":"0",
            "version": values['version'],
            "pname": values['name']
        }

        # create request post body
        dataList = []
        boundary = 'wL36Yn8afVp8Ag7AmP8qZ0SA4n1v9T' # Randomly generated
        for key, value in data.items():
            dataList.append('--' + boundary)
            dataList.append('Content-Disposition: form-data; name={0}'.format(key))
            dataList.append('')
            dataList.append(str(value))
        dataList.append('--' + boundary)
        dataList.append('Content-Disposition: form-data; name=\"file\"; filename={0}'.format(values["file_name"]))
        fileType = 'application/octet-stream'
        dataList.append('Content-Type: {}'.format(fileType))
        dataList.append('')
        dataList.append(file_str)
        dataList.append('--'+boundary+'--')
        dataList.append('')
        contentType = 'multipart/form-data; boundary={}'.format(boundary)

        body = '\r\n'.join(dataList)

        # request headers
        headers = {
            'Content-type': contentType,
            "rc_uid": "CxjNWQ8JjW77Gf2yG",
            "accept": "application/json, text/javascript",
            "rc_token": "glWa1YfBd2nq4B28C4Y0rotGHmMknKhlyjPGrdhchec"
        }

        responseBody = {}
        try:
            # create HTTPConnection
            conn = http.client.HTTPConnection(bim_server_host)
            # create request
            request = conn.request('POST', bim_server_url, body.encode(encoding='UTF-8',errors='strict'), headers)
            # get response
            response = conn.getresponse()

            _logger.info('upload file to Bim server')
            _logger.info(response.status)
            responseBody = eval(response.read().decode().replace('true','True').replace('false','False'))
            _logger.info(responseBody)

            # close HTTPConnection
            conn.close()
        except :
            _logger.info('HTTP connection ERROR')
            raise Warning('网络连接异常')
            return None

        if responseBody['success'] :
            _logger.info('Upload File success')
            values['file_url'] = '<a href ="http://119.3.40.108:3000/#/model-detail-show?uuid=' + responseBody['content'] + '&uid=CxjNWQ8JjW77Gf2yG&token=glWa1YfBd2nq4B28C4Y0rotGHmMknKhlyjPGrdhchec" target="_blank" >打开模型</a>'
            # convert Bim model
            try:
                uuid = responseBody['content']
                filePName = values['name'] + '-' + uuid
                descriptionList = getAllDeserializers()
                addProject(filePName,descriptionList,uuid)
            except Warning as w:
                raise w
        else :
            raise Warning('连接Bim服务错误')
            return None
        # create obj in odoo super function
        values.pop('file')
        values.pop('file_name')
        res_id = super(ProjectTaskBim, self).create(values)
        return res_id

    @api.multi
    def write(self, vals):
        result = super(ProjectTaskBim, self).write(vals)
        _logger.info(vals)
        return result


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
