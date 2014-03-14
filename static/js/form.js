$(function () {
    var FormErrorCtrl = new ErrorController($("#form-error"));

    var form = new FormController($field_update_url, $new_form, $save_form_url);

    $(form).on('error', function(e, message){
        FormErrorCtrl.show(message);
    });

    if(!$new_form) {
        var FieldErrorCtrl = new ErrorController($("#field-error"));
        var field_modal = new FieldModalController(FieldErrorCtrl, $form_id, $add_field_url, $update_field_url, $remove_field_url);
        var fields = new FieldsController($add_field_url, $edit_field_condition, $form_id, field_modal);

        var tasks = [];

        for(var task in $tasks) {
            tasks[$tasks[task].pk] = $tasks[task];
        }

        var tasks_list = new TimedTasksController($("#timed-tasks-panel"), $("#timed-task-modal"), tasks, $status_lookup, $save_task_url, $delete_task_url, $form_id);

        $(field_modal).on('fields_changed', fields.update_fields)
            .on('error', function(e, message){
                FieldErrorCtrl.show(message);
            });

        $(fields).on('error', function(e, message){
            FieldErrorCtrl.show(message);
        });
    }
});