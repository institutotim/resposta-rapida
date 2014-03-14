function LogicCtrl(Select, Params, LogicParams, Value) {
    var that = this;
    Value = Value || [];
    that.initial_value = Value;

    that.update_params = function () {
        var logic_id = Select.val();
        var last_params = that.get_params();
        var new_params = [];

        for (var key in last_params) {
            if (last_params.hasOwnProperty(key)) {
                if (last_params[key] != "") {
                    new_params.push(last_params[key]);
                }
            }
        }

        if (new_params.length) {
            that.initial_value = new_params;
        }

        if (logic_id in LogicParams) {
            Params.html('');

            var params_config = LogicParams[logic_id];

            for (var i = 0; i < params_config.length; i++) {
                var param_config = params_config[i];

                if (typeof param_config === 'string') {
                    Params.append(param_template(param_config, "text"));
                } else if (typeof param_config === 'object') {
                    Params.append(param_template(param_config.cap, param_config.type));
                }
            }

            that.set_params(new_params.length ? new_params : that.initial_value);
        } else {
            Params.html('');
        }
    };

    that.get_params = function () {
        var params = [];

        $("input.param").each(function (i, el) {
            params.push($(this).val());
        });

        return params;
    };

    that.get_logic = function(){
        return Select.val();
    };

    that.set_params = function (params) {
        for (var i = 0; i < params.length; i++) {
            $(Params.find("input")[i]).val(params[i]);
        }
    };

    var param_template = function (caption, type) {
        var size_cls = "input";
        var cell_cls = "cell";

        if (type == "list") {
            type = "text";
            size_cls = "input-xxlarge";
        } else if (type == "number") {
            size_cls = "input-small";
            cell_cls = "cell p30";
        }

        return '<div class="' + cell_cls + '"><p>' + caption + '</p>'
            + '<input type="' + type + '" class="param ' + size_cls + '" data-type="' + type + '"></div>';
    };


    Select.on('change', that.update_params);
    that.update_params();
    that.set_params(Value);

    return that;
}