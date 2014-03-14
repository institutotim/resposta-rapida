function FieldsController(AddFieldURL, EditFieldConditionURL, FormID, FieldModal) {
    /* properties */
    var that = this;

    that.fields_holder = $("#fields");
    that.fields_panel = $("#fields-panel")
    that.no_fields_phrase = $(".center-table", that.fields_panel);
    that.add_field_button = $(".add-field-button");

    /* public methods */
    that.update_fields = function (e, separator, fields) {
        that.fields_holder.html('');

        if (fields.length > 0) {
            for (var i = 0; i < fields.length; i++) {
                var field = fields[i];
                that.fields_holder.append(that.item_tmpl(field.id, field.field_type, field.name));

                if (i != (fields.length - 1)) {
                    that.fields_holder.append(that.separator_tmpl(separator));
                }
            }

            that.no_fields_phrase.hide();
        } else {
            that.no_fields_phrase.show();
        }
    };

    that.submit_field = function () {
        var name = $("#field-name"), type = $("#field-type").val();

        if (name.val().length < 1) {
            name.addClass("lazy-error").focus();
            return;
        }

        name = name.val();

        that.set_state('loading');

        $.post(AddFieldURL, {"name": name, "type": type, "form_id": FormID}, function (response) {
            if (response.error) {
                $(that).trigger('error', response.error);
            } else {
                that.update_fields(response.separator, response.fields);

                FieldModal.hide();
            }

            that.set_state('default');
        });
    };

    that.item_tmpl = function (id, type, name) {
        return '<li>' +
            '<a href="#" class="field" data-id="' + id + '" data-type="' + type + '" data-name="' + name + '">' + name + '' +
            '<a href="'+ EditFieldConditionURL + id +'"><i class="icon-sitemap"></i> </a>'+
            '</a></li>';
    };

    that.separator_tmpl = function (separator) {
        return '<li><span class="separator">' + separator + '</span></li>';
    };

    /* init */
    if(that.fields_holder.find("li").length > 0) {
        that.no_fields_phrase.hide();
    }


    /* handlers */
    $(that.fields_holder).sortable({
        placeholder: "sortable-highlight",
        axis: "x",
        cancel: "li.separator",
        containment: "parent"
    });

    that.add_field_button.on('click', function(e){
        e.preventDefault();
        FieldModal.open_new();
    });

    that.fields_holder.on('click', '.field', function(e){
        e.preventDefault();

        var $this = $(this);
        var id = $this.attr('data-id'), name_internal = $this.attr('data-name-internal'), name_public = $this.attr('data-name-public'), type = $this.attr('data-type');

        FieldModal.open_editable(id, name_internal, name_public, type);
    });

    /* return instance */
    return that;
};