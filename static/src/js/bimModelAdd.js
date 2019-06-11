
this.$('.o_select_file_button').click(function () {

    var $input = $('#bim_model_file_input');
    var files = $input.prop('files');
    console.log(files[0])
    var size = $('.bim_model_version_input').val()
    var description = $('.bim_model_description_input').val()
    var name = $('.bim_model_name_input').val()
    console.log(size)
    console.log(description)
    console.log(name)

    if (!files.length) {
        alert("请选择要上传的文件");
        return;
    }

        var data = new FormData();
        /*browse base方式，上传格式有严格的POST Policy限制，不能随意添加字段*/
        // data.append('key', files[0].name);
        // data.append('acl', "public-read");
        // data.append('success_action_status', '201');
        // data.append('policy', res['fields']['policy']);
        // data.append('x-amz-algorithm', res['fields']['x-amz-algorithm']);
        // data.append('x-amz-credential', res['fields']['x-amz-credential']);
        // data.append('x-amz-date', res['fields']['x-amz-date']);
        // data.append('x-amz-signature', res['fields']['x-amz-signature']);
        // data.append('file', files[0]);

        /*上传到S3服务器*/
        // var rpc = require('web.rpc');
        // rpc.query({
        //     model: 'project.task.bim',
        //     method: 'form_button_project_task_bim_add',
        //     args: [{
        //         'str':'ok',
        //     }]
        // }).then(function(result) {
        //     console.log(result);
        // });

        $.ajax({
            type: 'GET',
            url: '/bim/create',
            success: function (resx) {
                console.log(resx)
                alert("上传成功！")
            }
        });
});


$(".bim-file-a-upload").on("change","input[type='file']",function(){
    var filePath=$(this).val();
    if(filePath.indexOf("ifc")!=-1){
        $("#fileerrorTip").html("").hide();
        var arr=filePath.split('\\');
        var fileName=arr[arr.length-1];
        $("#bim_file_tmp_name").html(fileName);
    }else{
        $("#showFileName").html("");
        $("#fileerrorTip").html("您未上传模型，或者您上传模型文件类型有误！").show();
        return false
    }
})
