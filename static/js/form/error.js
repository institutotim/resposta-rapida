function ErrorController(Panel) {
    var that = this;
    that.show_time = 15 * 1000;
    that.error_panel = Panel;
    that.error_message = $("span", Panel);

    if(that.error_panel.length < 1 || that.error_message.length < 1) {
        throw new Error("ErrorCtrl: Selectors couldn't match the containers");
    }

    that.error_panel.hide();

    that.show = function (message) {
        that.error_panel.fadeIn("fast");

        if(typeof message != "string") {
            message = message.join("<br>");
        }

        that.error_message.html(message);

        clearTimeout(window.errorMessageTimeout);

        window.errorMessageTimeout = setTimeout(that.hide, that.show_time);
    };

    that.hide = function () {
        if (that.error_panel.is(":visible")) {
            that.error_panel.fadeOut();
        }
    };

    that.error_panel.on('click', function () {
        that.error_panel.fadeOut();
    });

    return that;
}