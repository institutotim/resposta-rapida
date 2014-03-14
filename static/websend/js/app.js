(function ($) {
    var listUpdater = {
        loading: false,
        last_id: null,
        pending_items: 0,

        tick: function () {
            var that = this;

            if (!this.loading) {
                this.loading = true;

                $.get(app.get_messages_url, {"identity": formController.identity(), "offset": this.last_id}, function (response) {
                    if (response.success) {
                        if (response.messages.length > 0) {
                            for (var i = 0; i < response.messages.length; i++) {
                                var entry = response.messages[i];

                                $("#message-list .no-data").remove();
                                $("#message-list").prepend(that.template(entry));

                                if (i + 1 == response.messages.length) {
                                    that.last_id = entry.pk;
                                }
                            }

                            that.pending_items -= response.messages.length;

                            if (that.pending_items < 1) {
                                that.pending_items = 0;
                                formController.reset_form();
                            }
                        }
                    }

                    that.loading = false;
                });
            }
        },

        template: function (entry) {
            var tmpl = '<tr class="' + entry.direction + '-message">';
            tmpl += '<td>' + entry.pk + '</td>';
            tmpl += '<td>' + entry.identity;

            if (entry.direction == 'I') {
                tmpl += '<span title="Do sistema (entrada)">&raquo;</span>';
            } else {
                tmpl += '<span title="Sua (saída)">&laquo;</span>';
            }

            tmpl += '</td><td>' + (entry.direction == 'I' ? 'Usuário' : 'Sistema') + '</td>';
            tmpl += '<td class="text">' + entry.text + '</td></tr>';

            return tmpl;
        }
    };

    var formController = {
        identity: function () {
            return $("#id_identity").val();
        },

        text: function () {
            return $("#id_text").val();
        },

        reset_form: function () {
            $("#id_text").removeAttr('disabled');
            $("#id_submit").removeClass("disabled").attr("value", "Enviar");
            $("#id_text").val('');
            $("#id_text").focus();
        },

        send: function () {
            if($("#id_text").attr('disabled') == 'disabled') {
                if(!confirm("Você já está enviando uma mensagem, deseja enviar outro após o término desta?")) {
                    return;
                }
            }

            $("#id_text").attr('disabled', 'disabled');
            listUpdater.pending_items += 2;
            $.post(app.send_message_url, {identity: this.identity(), text: this.text()});
            $("#id_submit").addClass("disabled").attr("value", "Enviando...");
        }
    };

    $(function () {
        $("#id_submit").on('click', $.proxy(formController.send, formController))
        window.setInterval($.proxy(listUpdater.tick, listUpdater), 3000);
    });
})(jQuery);