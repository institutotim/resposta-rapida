$(function(){
    var toggle_target = function(target) {
        var target = $("#" + $(this).attr('enable-for'));

        if($(this).attr('checked')) {
            target.removeAttr('disabled').removeClass('disabled');
        } else {
            target.attr('disabled', 'disabled').addClass('disabled');
        }
    };

    $(document).on('change', "*[enable-for]", toggle_target);

    $("*[enable-for]").each(toggle_target);
});