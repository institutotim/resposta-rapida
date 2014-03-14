var listItem = function (name, value, status, list, id) {
    var that = this;
    status = status || "disabled";

    that.new = name === null && value === null;
    that.id = id;
    that.list = list;
    that.dom = $($("#tmpl-extra-vars-field").html());
    that.dom.data('listItem', that);
    that.name = that.dom.find(".var-name");
    that.value = that.dom.find(".var-value");
    that.save_button = that.dom.find(".var-add-button");
    that.edit_button = that.dom.find('.var-edit-button');
    that.delete_button = that.dom.find(".var-delete-button");

    that.toggle_fields = function (enable) {
        if (enable) {
            $([that.name[0], that.value[0]]).removeAttr('disabled').removeClass('disabled');
        } else {
            $([that.name[0], that.value[0]]).addClass('disabled').attr('disabled', 'disabled');
        }
    };

    that.set_value = function (value) {
        that.value.val(value);
    };

    that.set_name = function (name) {
        that.name.val(name);
    };

    that.get_value = function () {
        return that.value.val();
    }

    that.get_name = function () {
        return that.name.val();
    }

    that.get = function () {
        return {name: that.name.val(), value: that.value.val()};
    };


    that.set = function (name, value) {
        that.set_name(name);
        that.set_value(value);
    };


    that.switch_status = function (status) {
        switch (status) {
            case "enabled":
                that.toggle_fields(true);
                that.save_button.show();
                $([that.edit_button[0], that.delete_button[0]]).hide();
                that.dom.attr('class', 'enabled');
                break;
            case "disabled":
                that.toggle_fields(false);
                that.save_button.hide();
                $([that.edit_button[0], that.delete_button[0]]).show();
                that.dom.attr('class', 'disabled');
                break;
        }
    };

    that.delete_dom = function () {
        that.dom.remove();
    };

    that.validate_fields = function () {
        if (that.name.val().length < 1) {
            that.name.focus();
            return false;
        } else if (that.value.val().length < 1) {
            that.value.focus();
            return false;
        }

        return true;
    };

    that.switch_status(status);
    that.set(name, value);

    that.edit_button.on('click', preventDefault(function () {
        that.switch_status('enabled');
    }));

    that.save_button.on('click', preventDefault(function () {
        if (that.validate_fields()) {
            if (that.new) {
                that.dom.trigger('create', [that.id]);
            } else {
                that.dom.trigger('update', [that.id]);
            }
        }
    }));

    that.delete_button.on('confirmed', function (e) {
        that.dom.trigger('delete', [that.id]);
    });

    that.list.append(that.dom);

    return that;
};

function ExtraVarsCtrl(extra_vars) {
    extra_vars = extra_vars || [];

    var that = this;

    that.list = $("#extra-vars");
    that.extra_vars = [];

    for (var i = 0; i < extra_vars.length; i++) {
        that.extra_vars[i] = new listItem(extra_vars[i].name, extra_vars[i].value, 'disabled', that.list, i);
    }

    that.create_new_field = function () {
        var index = that.extra_vars.length;
        return that.extra_vars[index] = new listItem(null, null, 'enabled', that.list, index);
    };

    that.validate_unique = function (item) {
        if (that.key_count(item.get().name) > 1) {
            item.name.focus();
            alert("Esse nome já está sendo usado em outra variável.");
            return false;
        }

        return true;
    };

    that.list.on('update', function (e, id) {
        var item = that.extra_vars[id];

        if (that.validate_unique(item)) {
            item.switch_status('disabled');
        }
    });

    that.list.on('delete', function (e, id) {
        var item = that.extra_vars[id];
        item.delete_dom();
        delete that.extra_vars[id];
    });

    that.create_new_field();

    that.list.on('create', function (e, id) {
        var item = that.extra_vars[id];
        if (that.validate_unique(item)) {
            item.switch_status('disabled');
            that.create_new_field();
            item.new = false;
        }
    });

    that.key_count = function (key) {
        var vars = that.get();
        var count = 0;

        for (var i = 0; i < vars.length; i++) {
            if (vars[i].name == key) {
                count++;
            }
        }

        return count;
    };

    that.get = function () {
        var extra_vars = [];

        for (var idx in that.extra_vars) {
            if (that.extra_vars.hasOwnProperty(idx)) {
                var data = that.extra_vars[idx].get();
                if (data.name.length > 0 && data.value.length > 0) {
                    extra_vars.push(data);
                }
            }
        }
        return extra_vars;
    }

    return that;
}