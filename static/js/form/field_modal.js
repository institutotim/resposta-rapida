function FieldModalController(FieldErrorCtrl, FormID, AddFieldURL, UpdateFieldURL, RemoveFieldURL) {
    var that = this;

    var DELETING = 4,
        SAVING = 3,
        EDITING = 2,
        LOADING = 1,
        DEFAULT = 0;

    that.modal = $("#field-modal");
    that.delete_button = $("#delete-field", that.modal);
    that.cancel_button = $(".cancel", that.modal);
    that.submit_button = $("#submit-field", that.modal);

    that.mdl_field_type = $("#field-type", that.modal);
    that.mdl_field_name_public = $("#field-name-public", that.modal);
    that.mdl_field_name_internal = $("#field-name-internal", that.modal);
    that.modal_title = $("h4 span", that.modal);
    that.modal_icon = $("h4 i", that.modal);

    that.current_data = {};
    that.state = DEFAULT;

    that.open_editable = function (id, nome_internal, nome_public, tipo) {
        that.set_state(EDITING);

        that.mdl_field_name_internal.val(nome_internal);
        that.mdl_field_name_public.val(nome_public);
        that.mdl_field_type.val(tipo);

        that.current_data = {"id": id, "name_internal": nome_internal, "name_public": nome_public, "type": tipo};

        that.show();
    };

    that.open_new = function () {
        that.set_state(DEFAULT);

        that.mdl_field_name_public.val('');
        that.mdl_field_name_internal.val('');
        that.mdl_field_type.val(1);

        that.show();
    };

    that.set_title = function (title, icon) {
        if (!icon) {
            icon = "icon-plus";
        }

        that.modal_title.html(title);
        that.modal_icon.removeClass().addClass(icon);
    };

    that.set_state = function (state) {
        switch (state) {
            case LOADING:
                that.cancel_button.hide();
                that.submit_button.html("Aguarde...").addClass("disabled");
                that.set_title('Criando...');
                break;
            case EDITING:
                $([that.delete_button[0], that.cancel_button[0], that.submit_button[0]]).show();
                $([that.mdl_field_name_public[0], that.mdl_field_name_internal[0], that.mdl_field_type[0], that.delete_button[0], that.submit_button[0]])
                    .removeClass('disabled lazy-error').removeAttr('disabled');

                that.delete_button.html('Excluir campo');

                that.mdl_field_name_internal.focus();
                that.mdl_field_name_public.focus();

                that.submit_button.html("Salvar").removeClass("disabled");
                that.set_title('Editando campo', 'icon-edit');
                break;
            case DELETING:
                $([that.delete_button[0]]).show();
                $([that.cancel_button[0], that.submit_button[0]]).hide();
                $([that.mdl_field_name_public[0], that.mdl_field_name_internal[0], that.mdl_field_type[0]]).addClass('disabled').attr('disabled', 'disabled');

                that.delete_button.html('Aguarde...').addClass('disabled');
                that.set_title('Excluindo...', 'icon-remove');

                break;
            case SAVING:
                $([that.delete_button[0], that.cancel_button[0]]).hide();
                $([that.mdl_field_name_public[0], that.mdl_field_name_internal[0], that.mdl_field_type[0]]).addClass('disabled').attr('disabled', 'disabled');
                that.set_title('Salvando...', 'icon-spin');
                that.submit_button.html('Aguarde...').addClass("disabled");
                break;
            default:
                $([that.cancel_button[0], that.submit_button[0], that.mdl_field_name_public[0], that.mdl_field_name_internal[0], that.mdl_field_type[0]]).show();
                $([that.mdl_field_name_public[0], that.mdl_field_name_internal[0], that.mdl_field_type[0]]).removeClass('disabled lazy-error').removeAttr('disabled');

                that.delete_button.hide();
                that.submit_button.html("Adicionar").removeClass("disabled");
                that.set_title('Adicionar campo');
                break;
        }

        that.state = state;
    };

    that.hide = function () {
        that.modal.modal('hide');
        that.current_data = {};
    };

    that.show = function () {
        FieldErrorCtrl.hide();
        that.modal.modal('show');
    };

    that.submit_field = function () {
        if (that.mdl_field_name_internal.val().length < 1) {
            that.mdl_field_name_internal.addClass("lazy-error").focus();
            return;
        }

        var name_internal = that.mdl_field_name_internal.val();
        var name_public = that.mdl_field_name_public.val();

        that.set_state(LOADING);

        $.post(AddFieldURL, {"name_internal": name_internal, "name_public": name_public, "type": that.mdl_field_type.val(), "form_id": FormID}, function (response) {
            if (response.error) {
                $(that).trigger('error', response.error);
            } else {
                $(that).trigger('fields_changed', [response.separator, response.fields]);
                that.hide();
            }

            that.set_state(DEFAULT);
        });
    };

    that.update_field = function () {
        that.set_state(SAVING);

        that.current_data["name_public"] = that.mdl_field_name_public.val();
        that.current_data["name_internal"] = that.mdl_field_name_internal.val();
        that.current_data["type"] = that.mdl_field_type.val();

        $.post(UpdateFieldURL, that.current_data, function (response) {
            if (response.error) {
                $(that).trigger('error', response.error);
                that.set_state(EDITING);
            } else {
                $(that).trigger('fields_changed', [response.separator, response.fields]);
                that.hide();
            }
        });
    };

    that.remove_field = function () {
        that.set_state(DELETING);

        $.post(RemoveFieldURL, that.current_data, function (response) {
            if (response.error) {
                $(that).trigger('error', response.error);
            } else {
                $(that).trigger('fields_changed', [response.separator, response.fields]);
                that.hide();
            }
        });
    };

    that.submit_button.on('click', function (e) {
        e.preventDefault();

        switch (that.state) {
            case DEFAULT:
                that.submit_field();
                break;
            case EDITING:
                that.update_field();
                break;
        }
    });

    var update_slug = function () {
        var slug = that.mdl_field_name_public.val().toLowerCase().replace(/[ -]/gi, "_").replace(/[^a-z0-9_]/g, "");
        that.mdl_field_name_internal.val(slug);
    };

    $([that.mdl_field_name_internal[0], that.mdl_field_name_public[0], that.mdl_field_type[0]]).on('keydown', function (e) {
        if (e.which == 13) {
            that.submit_button.trigger('click');
        }
    });

    $([that.mdl_field_name_public[0]]).on('keyup', function(e){
        update_slug();
    });

    that.delete_button.on('confirmed', function () {
        that.remove_field();
    });

    return that;
};