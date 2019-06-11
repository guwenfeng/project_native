odoo.define('project_task_bim.file', function (require) {
    "use strict";

    var Widget = require('web.Widget');
    var widgetRegistry = require('web.widget_registry');
    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;

    Var bimFileUpload = AbstractAction.extend({
       template: 'bimFileField',
       events: { 'click .demo-submit': '_onSubmitClick' },

       _onSubmitClick: function (e) {
           e.stopPropagation();
           alert('Submit clicked!');
       }
    });

    core.action_registry.add('project_task_bim.file', bimFileUpload);


 });
