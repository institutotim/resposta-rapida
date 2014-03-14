function FormController(FieldUpdateURL, IsFormNew, SaveFormURL) {
    var that = this;

    /* Public methods */
    that.get_form_data = function () {
        var data = {}, i, field;

        var text_fields = $("input.editable");

        for (i = 0; i < text_fields.length; i++) {
            field = $(text_fields[i]);
            data[field.attr("id")] = field.val();
        }

        var bool_fields = $(".bool");

        for (i = 0; i < bool_fields.length; i++) {
            field = $(bool_fields[i]);
            data[field.attr("id")] = $.trim(field.text()) == "Sim" ? 1 : 0;
        }

        return data;

    };

    that.submit_form = function (data) {
        $("#submit-button").html("Aguarde...").addClass("disabled");

        return $.post(SaveFormURL, data, function (response) {
            if (response.success) {
                window.location = response.view_form_url;
            } else {
                $(that).trigger('error', response.error);

                if (response.params) {
                    for (var i = 0; i < response.params.length; i++) {
                        var field = $("#" + response.params[i]);
                        field.addClass("lazy-error");

                        if (i == 0) {
                            field.focus();
                        }
                    }
                }

                $("#submit-button").html("Continuar").removeClass("disabled");
            }
        });
    };

    /* init */
    if (IsFormNew) {
        $("#submit-button").on('click', function () {
            var data = that.get_form_data();
            that.submit_form(data);
        });
    } else {
        var data = that.get_form_data();
        if(data["requires_confirmation"]) {
            $("#ans_default").parent().hide();
        }
    }

    $(".editable").editable({ // TODO: Break up into handler section
        "url": FieldUpdateURL,

        "new": IsFormNew,

        "bool_values": {
            true: "Sim",
            false: "Não",
            "Sim": true,
            "Não": false
        },

        "onError": function (response) {
            $(that).trigger('error', response.error);
        },

        "onBeforeChange": function (old_val) {
            var $el = $(this);

            if ($el.attr('id') == 'main') {
                if (!old_val) {
                    return confirm("Se você ativar o modo principal em um formulário, os outros formulários serão desconsiderados para processamento de submissões. Tem certeza que deseja ativar o modo principal?");
                }
            }

            return true;
        },

        "onAfterChange": function (new_val) {
            var $el = $(this);

            if ($el.attr('id') == "requires_confirmation") {
                if (new_val == "Sim") {
                    $(".req_con").slideDown('fast');
                    $(".req_heading").addClass("open");
                    $("#ans_default").parent().slideUp('fast');
                    $("#confirmation-link").fadeIn('fast');
                } else {
                    $(".req_con").slideUp('fast', function () {
                        $(".req_heading").removeClass("open");
                    });
                    $("#ans_default").parent().slideDown('fast');
                    $("#confirmation-link").fadeOut('fast');
                }
            }

            if ($el.attr('id') == "separator") {
                $(".separator", "#fields").html(new_val);
            }
        }
    });

    return that;
};