(function ($) {
    var options = {};

    var updateValue = function (el, val) {
        var orig = window._editableStore[$(el)].originalElement;

        var $orig = $(orig);

        if ((val != $.trim($orig.text()) || $orig.data('type') != "text") && !options.new) {
            var data = {"name": $orig.attr('id'), "pk": $orig.data('pk'), "value": val};

            $(el).attr('disabled', 'disabled');

            return $.post(options.url, data, function (response) {
                if (response.error) {
                    options.onError.call(this, response);
                } else {
                    $orig.html(response.current_value);

                    if (options["onAfterChange"]) {
                        options["onAfterChange"].call(el, val);
                    }
                }
            });
        } else {
            $orig.html(val);

            if (options["onAfterChange"]) {
                options["onAfterChange"].call(el, val);
            }
        }

        return undefined;
    };

    var toggleBool = function (el) {
        var $this = $(el);

        var current_value = options.bool_values[$.trim($this.text())];

        if (options["onBeforeChange"]) {
            if (!options["onBeforeChange"].call(el, current_value)) {
                return;
            }
        }

        var new_value = options.bool_values[!current_value];

        updateValue(el, new_value);
    };

    var displayOriginal = function (el, new_value) {
        var $orig = $(window._editableStore[$(el)].originalElement);

        $orig.on('click', openEdit);
        $(el).replaceWith($orig);
    };

    var processStroke = function (e) {
        var $this = $(this);
        var val = $this.val();

        switch (e.which) {
            case 13:
            case 27:
                var that = this;

                $.when(updateValue(this, val)).then(function () {
                    displayOriginal(that, val)
                });

                break;
        }
    };

    var openEdit = function () {
        var $this = $(this);
        var type = $this.data('type');

        if (!window._editableStore[$this]) {
            window._editableStore[$this] = {};
        }

        window._editableStore[$this].originalElement = this;
        var input;

        switch (type) {
            case 'text':
                var max_len = $this.data('maxlength');
                input = $("<input type='text'>");

                if (max_len) {
                    input.attr('maxlength', max_len);
                }

                input.val($.trim($this.text()));

                if (!options.new) {
                    input.css('width', $this.innerWidth() - 7);
                    input.on('keyup', processStroke);
                    input.on('blur', function () {
                        $.when(updateValue(input, input.val())).then(function () {
                            displayOriginal(input, input.val());
                        });
                    });
                }

                $this.replaceWith(input);
                break;
            case 'bool':
                toggleBool(this);
                return;
        }

        var classes = $this.attr("class").split(' ');
        classes.push('x-editable');
        classes = classes.join(" ");
        input.attr('id', $this.attr('id'));
        input.attr('class', classes);

        if (!options.new) {
            input.focus();
        }
    };

    $.fn.editable = function (settings) {
        options = settings;

        window._editableStore = {};

        for (var i = 0; i < this.length; i++) {
            var $this = $(this[i]);

            if (!options.new || $this.data('type') != "text") {
                $this.on('click', openEdit);
            } else {
                openEdit.call(this[i]);
            }
        }

    };
})(jQuery);