$(function () {
    var confirm_before_execute = function (e) {
        if (confirm($(this).attr("data-confirm"))) {
            return true;
        } else {
            e.preventDefault();
            return false;
        }
    };

    var confirm_before_trigger = function (e) {
        e.preventDefault();

        if (confirm($(this).attr("data-confirm-ev"))) {
            $(this).trigger('confirmed');
        } else {
            $(this).trigger('canceled');
        }
    };

    $(document).on('click', "*[data-confirm]", confirm_before_execute);
    $(document).on('click', "*[data-confirm-ev]", confirm_before_trigger);
});