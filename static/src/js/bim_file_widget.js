function bimFileLoad(field, bimfile){
    var name = $("input[name='name']").val();
    var version = $("input[name='version']").val();
    if (name === "" | version === "" ) {
        $("#bim_file_tmp_name").html("选择文件");
        $("#bim_model_file_input").value = '';
        $("#fileerrorTip").html("请先填写模型名称或版本！").show();
        return;
    }

    // console.log('size',version);
    // console.log('name',name);
    // console.log('input',bimfile);

    var form = new FormData();
    form.append("project", "27");
    form.append("latitude", "31.24");
    form.append("longitude", "121.47");
    form.append("height", "0");
    form.append("heading", "0");
    form.append("pitch", "0");
    form.append("roll", "0");
    form.append("version", version);
    form.append("file", bimfile);//模型文件 form表单中的FileUpload类型
    form.append("pname", name); //模型名
    form.append("dir","");
    $("button[accesskey='s']").attr('disabled',true);
    $("button[accesskey='j']").attr('disabled',true);
    $("#fileTransformInfo").html("正在上传模型，请勿关闭窗口！ 进度：\t0%").show();

    $.ajax({
        "async": true,
        "crossDomain": true,
        "url": "http://119.3.40.108:8087/SmartCity/model/ifc/upload",
        "method": "POST",
        "headers": {
            "rc_uid": "CxjNWQ8JjW77Gf2yG",
            "accept": "application/json, text/javascript",
            "rc_token": "glWa1YfBd2nq4B28C4Y0rotGHmMknKhlyjPGrdhchec"
        },
        "processData": false,
        "contentType": false,
        "mimeType": "multipart/form-data",
        "data": form,
        "xhr": function(){
            myXhr = $.ajaxSettings.xhr();
            if (myXhr.upload) {
                myXhr.upload.addEventListener('progress', progressHandlingFunction, false);
            }
            return myXhr;
        },
        "success": function(result){
            const response = JSON.parse(result);
            console.log("response",response);
            // console.log("content",response.content);
            field._setValue(response.content);
            $("#fileTransformInfo").html("模型上传成功，正在转换模型，请勿关闭窗口！（这可能需要几分钟）").show();
            transformIfcFile(name, response.content)
        },
    });
}

function transformIfcFile(name, uuid){
    $.ajax({
        "async": true,
        "crossDomain": true,
        "url": "http://119.3.41.81:8081/bimserver/json",
        "method": "POST",
        "headers": {
            "content-type": "application/json; charset=UTF-8"
        },
        "data": "{\"request\":{\"interface\":\"org.bimserver.PluginInterface\",\"method\":\"getAllDeserializers\",\"parameters\":{\"onlyEnabled\":\"true\"}},\"token\":\"b6121d0067146650c2d193207b3931679bf6631df5f70e66c4b73b2ec107e388f5f328b3eab8a1144849c258858e692a\"}",
        "success": function (response) {
            console.log("transformIfcFile",response);
            const dList = response.response.result;
            console.log("dlist",dList);
            var filePName = name + '-' + uuid;
            console.log("filePName",filePName);
            addProject(filePName, dList, uuid);
        }
    });
}
function addProject(filePName, dList, uuid) {
    for(var i=0;i<dList.length;i++) {
        var obj = dList[i];
        if (obj.name === "Ifc2x3tc1 (Streaming)") {
            const deserializerOid = obj.oid;
            $.ajax({
                "async": true,
                "crossDomain": true,
                "url": "http://119.3.41.81:8081/bimserver/json",
                "method": "POST",
                "headers": {
                    "content-type": "application/json; charset=UTF-8"
                },
                "data": "{\"request\":{\"interface\":\"org.bimserver.ServiceInterface\",\"method\":\"addProject\",\"parameters\":{\"projectName\":\""+ filePName +"\",\"schema\":\"ifc2x3tc1\"}},\"token\":\"b6121d0067146650c2d193207b3931679bf6631df5f70e66c4b73b2ec107e388f5f328b3eab8a1144849c258858e692a\"}",
                "success": function (response) {
                    console.log("addProject", response);
                    const oid = response.response.result.oid;
                    checkinFromUrl(oid, deserializerOid, uuid+'.ifc',  'http://172.16.0.129:8087/SmartCity/model/ifc/download/' + uuid);
                }
            });
        }
    }

}

function checkinFromUrl(poid, deserializerOid, fileName, fileUrl) {
    $.ajax({
        "async": true,
        "crossDomain": true,
        "url": "http://119.3.41.81:8081/bimserver/json",
        "method": "POST",
        "headers": {
            "content-type": "application/json; charset=UTF-8"
        },
        "data": "{\"request\":{\"interface\":\"org.bimserver.ServiceInterface\",\"method\":\"checkinFromUrl\",\"parameters\":{\"poid\":"+ poid+",\"comment\":\"\",\"deserializerOid\":"+ deserializerOid +",\"fileName\":\""+fileName+"\",\"url\":\""+ fileUrl +"\",\"merge\":false,\"sync\":true}},\"token\":\"b6121d0067146650c2d193207b3931679bf6631df5f70e66c4b73b2ec107e388f5f328b3eab8a1144849c258858e692a\"}",
        "success": function (response) {
            console.log("checkinFromUrl",response);
            $("#fileTransformInfo").html("模型转换成功，请保存！").show();
            $("button[accesskey='s']").attr('disabled',false);
            $("button[accesskey='j']").attr('disabled',false);
        }
    });
}

function progressHandlingFunction(e) {
    if (e.lengthComputable) {
        var vulue = Math.floor(e.loaded/e.total * 100);
        $("#fileTransformInfo").html("正在上传模型，请勿关闭窗口！ 进度：\t" + vulue + "%").show();
        $('#bim_file_progress').attr({value: e.loaded, max: e.total}); //更新数据到进度条
    }
}

odoo.define('bim_file_widget', function(require){
    "use strict";
    var AbstractField = require('web.AbstractField');
    var fieldRegistry = require('web.field_registry');

    var bimFileField = AbstractField.extend({
        className: 'o_char_bimfileupload',
        tagName: 'div',
        supportedFieldTypes: ['char'],
        events: {
            'change .bim_model_file_input': 'inputChange',
        },
        init: function () {
            this._super.apply(this, arguments);
        },
        _renderEdit: function () {
            if (this.value === false){
                this.$el.empty();
                this.$el.append("<div class='bim_field_div'>" +
                                        "<progress id='bim_file_progress' class='bim_file_progress'>100%</progress>" +
                                        "<a href='javascript:;' class='bim-file-a-upload'>" +
                                            "<span id='bim_file_tmp_name'>选择文件</span>" +
                                            "<input type='file' name='file' class='bim_model_file_input' id='bim_model_file_input'/>" +
                                        "</a>" +
                                        "<span id='fileerrorTip' class='bim_file_upLoad_info' style='color:#F00'></span>" +
                                        "<span id='fileTransformInfo' class='bim_file_upLoad_info' ></span>" +
                                "</div>");
            }
        },
        _renderReadonly: function () {
            if (this.value !== false) {
                var link = "<a href ='http://119.3.40.108:3000/#/model-detail-show?uuid=" +this.value + "&uid=CxjNWQ8JjW77Gf2yG&token=glWa1YfBd2nq4B28C4Y0rotGHmMknKhlyjPGrdhchec' target='_blank' >打开模型</a>";
                this.$el.empty();
                this.$el.append(link);
            } else {
                this.$el.empty();
            }

        },
        inputChange: function (ev) {
            var file = ev.target.files[0];
            if (file) {
                var fileName= file.name;
                if(fileName.indexOf(".ifc")!=-1){
                    $("#fileerrorTip").html("").hide();
                    $("#bim_file_tmp_name").html(fileName);
                    bimFileLoad(this,file)
                }else{
                    $("#fileerrorTip").html("您未上传模型，或者您上传模型文件类型有误！").show();
                    return false
                }
            }else{
                $("#fileerrorTip").html("您未上传模型，或者您上传模型文件类型有误！").show();
                return false
            }

        }

    });

    fieldRegistry.add('bim_file', bimFileField);

    return {
        bimFileField: bimFileField,
    };
})
