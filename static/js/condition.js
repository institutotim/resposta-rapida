$(function () {
    /* properties */
    var that = this;

    that.logic_select = $("#logic");
    that.new_val = $("#change-value-to");
    that.status = $("#change-status-to");
    that.answer = $("#answer");
    that.id = window.$id || undefined;

    /* private properties */
    var logicCtrl = new LogicCtrl(that.logic_select, $(".params"), window.$logic_params, window.$param),
        extraCtrl = new ExtraVarsCtrl(window.$extra_vars),
        errorCtrl = new ErrorController($("#condition_form_error"));

    /* globals */
    window.$param = window.$param || [];
    window.$extra_vars = window.$extra_vars || [];
    window.logicCtrl = logicCtrl;
    window.extraCtrl = extraCtrl;

    /* private methods */

    var get_form_field = function (field) {
        var field_id = field.attr('id'),
            enabler = $("[enable-for='" + field_id + "']");

        // Has Enabler
        if (enabler[0]) {
            if (enabler.is(":checked")) {
                return field.val();
            } else {
                return undefined;
            }
        } else {
            return field.val();
        }
    };

    var create_stage = function () {
        var save_button = new Prop("#save-btn"), title = new Prop(".widget-title h5");
        var stage = new Stage(save_button, title);

        stage.save_scene();

        save_button.set('enabled', false)
            .set('text', 'Aguarde...');
        title.set('text', 'Salvando a condição...');

        stage.save_scene('saving');

        return stage;
    };

    that.get_form_data = function () {
        return {
            id: that.id,
            cond_type: window.$cond_type,
            related_id: window.$related_id,
            logic: logicCtrl.get_logic(),
            param: logicCtrl.get_params(),
            action: get_form_field($("#change-status-to")) || null,
            new_value: get_form_field($("#change-value-to")) || "",
            answer: get_form_field($("#answer")) || "",
            extra_vars: extraCtrl.get()
        };
    };

    that.save_condition = function () {
        var form_data = that.get_form_data();
        var cond_type = form_data.cond_type,
            related_id = form_data.related_id;

        delete form_data.cond_type;
        delete form_data.related_id;

        var data = {"data": JSON.stringify(form_data), "cond_type": cond_type, "related_id": related_id};

        $.post(window.$save_condition_url, data, function (response) {
            if (response.success) {
                window.location = response.return_url;
            } else {
                errorCtrl.show(response.message);
                stage.set_scene('default');
            }
        }, 'json');
    };

    /* init */
    if ("$status" in window) {
        if (window.$status || window.$status == 0) {
            $("#enable-status").click();
            that.status.val(window.$status);
        }
    }

    if ("$new_value" in window) {
        $("#enable-new-val").click();
        that.new_val.val(window.$new_value);
    }

    if ("$answer" in window) {
        $("#enable-answer").click();
        that.answer.val(window.$answer);
    }

    var stage = create_stage();

    stage.set_scene('default');

    /* handlers */
    $("#save-btn").on('click', function (e) {
        e.preventDefault();
        stage.set_scene('saving');
        that.save_condition();
    });
});