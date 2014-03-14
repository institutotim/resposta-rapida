function TimedTaskModal(Container, SaveTaskURL, DeleteTaskURL, FormID) {
    /* properties */
    var that = this;
    that.container = Container;
    that.errorCtrl = new ErrorController($("#task-error"));

    /* model */
    that.mdl = {
        pk: $(".pk", that.container),
        form: $(".form", that.container),
        once: $(".once", that.container),
        run_after_min: $(".run_after_min", that.container),
        submission_status: $(".status_from", that.container),
        status_to_change: $(".status_to", that.container),
        answer: $(".answer", that.container),

        get_model: function () {
            var resp = {
                pk: that.mdl.pk.val(),
                form: that.mdl.form.val() || FormID,
                once: !!(that.mdl.once.val() == "1"),
                run_after_min: that.mdl.run_after_min.val(),
                submission_status: that.mdl.submission_status.val(),
                status_to_change: that.mdl.status_to_change.val(),
                answer: that.mdl.answer.val()
            };

            if (isNaN(parseInt(resp.pk, 10))) {
                delete resp.pk;
            }

            return resp;
        }
    };

    /* private methods */
    var create_props = function () {
        var cancel_btn = new Prop(".cancel", that.container),
            main_bnt = new Prop("#submit-task"),
            title = new Prop("h4 span", that.container);

        return {"cancel_btn": cancel_btn, "main_btn": main_bnt, "title": title};
    };

    var create_stage = function (props) {
        var stage = new Stage(props.cancel_btn, props.main_btn, props.title);

        stage.save_scene(); // save default stage

        /* edit scene */
        props.main_btn
            .set("text", "Salvar")
            .set("enabled", true);
        props.title.set("text", "Alterar Tarefa");
        props.cancel_btn.set("visible", true);

        stage.save_scene('edit');

        /* new scene */
        props.main_btn
            .set("text", "Adicionar")
            .set("enabled", true);
        props.title.set("text", "Criar nova tarefa");
        props.cancel_btn.set("visible", true);

        stage.save_scene('new');


        /* saving scene */
        props.title.set("text", "Salvando tarefa...");
        props.main_btn
            .set("enabled", false)
            .set("text", "Aguarde...");
        props.cancel_btn.set("visible", false);

        stage.save_scene('saving');


        return stage;
    };

    var save_task = function (task) {
        if (task) {
            that.stage.set_scene("saving");
            return $.ajax({url: SaveTaskURL, data: {"task": JSON.stringify(task)}, dataType: 'json', type: "POST"});
        } else {
            return undefined;
        }
    };

    /* public methods */
    that.edit = function (task) {
        that.errorCtrl.hide();

        that.mdl.pk.val(task.pk);
        that.mdl.form.val(task.form);
        that.mdl.once.val(task.once ? "1" : "0");
        that.mdl.run_after_min.val(task.run_after_min);
        that.mdl.submission_status.val(task.submission_status);
        that.mdl.status_to_change.val(task.status_to_change);
        that.mdl.answer.val(task.answer);

        that.stage.set_scene('edit');
        that.container.modal('show');
    };

    that.new = function () {
        that.errorCtrl.hide();

        $([that.mdl.submission_status[0], that.mdl.once[0], that.mdl.status_to_change[0]]).val(0);
        $([that.mdl.pk[0], that.mdl.run_after_min[0], that.mdl.answer[0]]).val('');
        that.stage.set_scene('new');
        that.container.modal('show');
    };

    that.delete = function (task) {
        var delete_item_url = DeleteTaskURL.replace("/0", "/" + task.pk);

        return $.post(delete_item_url, {"id": task.pk}, 'json');
    };

    /* init */
    that.props = create_props();
    that.stage = create_stage(that.props);

    /* handlers */
    that.props.main_btn.node.on('click', preventDefault(function () {
        var task = that.mdl.get_model();

        if (task) {
            that.stage.set_scene('saving');
            save_task(task).done(function (response) {
                if (response.success) {
                    $(that).trigger('task_saved', [response.task]);
                    that.container.modal('hide');
                } else {
                    that.stage.set_scene('edit');
                    that.errorCtrl.show(response.error);
                }

            });
        }
    }));

    /* return instance */
    return that;
}

function TimedTasksController(Container, Modal, Tasks, StatusLookup, SaveTaskURL, DeleteTaskURL, FormID) {
    /* properties */
    var that = this;
    that.answer_length = 35;

    that.modal = new TimedTaskModal(Modal, SaveTaskURL, DeleteTaskURL, FormID);

    that.container = Container;
    that.task_list = $("tbody", that.container);
    that.header = $("thead", that.container);
    that.no_items = $("#no-items", that.container);

    /* model */
    that.tasks = Tasks || {};

    /* private methods */
    var update_row = function (row, task) {
        var phrase = (task.once ? "Após" : "A cada") + " " + task.run_after_min + " minutos...";
        var answer = task.answer.length > that.answer_length
            ? task.answer.slice(0, that.answer_length) + "..."
            : task.answer;

        row.find(".when").html(phrase);
        row.find(".status_from").html(StatusLookup[task.submission_status]);
        row.find(".status_to").html(StatusLookup[task.status_to_change] || "Manter Atual");
        row.find(".answer").html(answer);
        row.attr('data-id', task.pk);

        return row;
    };

    var create_row = function (task) {
        var row = $($("#task-template").html());

        return update_row(row, task);
    };


    /* public methods */
    that.add_item = function (task) {
        var item = create_row(task);
        that.task_list.append(item);
        that.tasks[task.pk] = task;

        if (!that.header.is(":visible")) {
            that.header.show();
        }

        if(that.no_items.is(":visible")) {
            that.no_items.hide();
        }
    };

    that.update_item = function (task) {
        if (task.pk in that.tasks) {
            that.tasks[task.pk] = task;
            var row = $("tr[data-id='" + task.pk + "']", that.container);
            update_row(row, task);

            return true;
        }

        return false;
    };

    that.delete_item = function (task) {
        if (task.pk in that.tasks) {
            delete that.tasks[task.pk];
            var row = $("tr[data-id='" + task.pk + "']", that.task_list);
            row.fadeTo('fast', 0.4, function () {
                row.slideUp();
                row.remove();

                if(window.size(that.tasks) < 1) {
                    that.header.hide();
                    that.no_items.show();
                }
            });
        }
    }

    /* init */
    for (var pk in that.tasks) {
        var mdl_objects = ['pk', 'form', 'once', 'submission_status', 'run_after_min', 'status_to_change', 'answer'];
        var task = {};

        for (var i = 0; i < mdl_objects.length; i++) {
            task[mdl_objects[i]] = that.tasks[pk][mdl_objects[i]] || that.tasks[pk]['fields'][mdl_objects[i]];
        }

        that.add_item(task);
    }

    if (that.tasks.length < 1) {
        that.header.hide();
    } else {
        that.no_items.hide();
    }

    /* handlers */
    $(that.container).on('click', '.add-task-button', preventDefault(function () {
        that.modal.new();
    }));

    $(that.container).on('click', '.edit-btn', preventDefault(function () {
        var id = $(this).parents("tr").data('id');
        that.modal.edit(that.tasks[id]);
    }));

    $(that.container).on('confirmed', '.del-btn', preventDefault(function () {
        var id = $(this).parents("tr").data('id');
        that.modal.delete(that.tasks[id]).done(function (resp) {
            if (resp.success) {
                that.delete_item(that.tasks[id]);
            } else {
                alert(resp.error);
                window.location.reload();
            }
        });
    }));

    $(that.modal).on('task_saved', function (e, task) {
        if (!that.update_item(task)) {
            that.add_item(task);
        }
    });

    /* return instance */
    return that;
}