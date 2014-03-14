function Prop(selector, container) {
    var that = this;

    Prop.instances = Prop.instances || 0;

    that.node = typeof container != 'undefined' ? $(selector, container) : $(selector);

    if (!that.node[0]) {
        throw new Error("Cannot find node element with selector: " + selector);
    }

    that.tag = that.node.prop('tagName').toLowerCase();

    that.uniqid = "Prop<" + (Prop.instances++) + ">";

    return that;
}

Prop.prototype.toString = function () {
    return this.uniqid;
}

Prop.prototype.set = function (what, val) {
    switch (what) {
        case "enabled":
            if (!val) {
                this.node.attr('disabled', 'disabled');
                if (!this.node.hasClass('disabled'))
                    this.node.addClass('disabled');
            } else {
                this.node.removeAttr('disabled');
                this.node.removeClass('disabled');
            }

            break;

        case "text":
            if (this.tag == 'input') {
                this.node.val(val);
            } else {
                this.node.html(val);
            }

            break;

        case "visible":
            if (val) {
                this.node.show();
            } else {
                this.node.hide();
            }
            break;
    }

    return this;
};

Prop.prototype.get = function (what) {
    switch (what) {
        case "enabled":
            return this.node.attr('disabled') != 'disabled' && !this.node.hasClass('disabled');
        case "text":
            return this.tag == "input" ? this.node.val() : this.node.html();
        case "visible":
            return this.node.css("display") != "none" && this.node.css("visibility") != "hidden";
    }

    return undefined;
};


function Stage(/** props */) {
    var that = this,
        args = Array.prototype.slice.call(arguments, 0);

    that.scenes = {};
    that.props = args;
    that.attrs = ['enabled', 'visible', 'text'];
    that.current_scene = 'default';

    return that;
}

Stage.prototype.save_scene = function (title) {
    title = title || this.current_scene;
    this.scenes[title] = this.get_scene();
};

Stage.prototype.get_scene = function () {
    var scene = {};

    for (var prop in this.props) {
        if (this.props.hasOwnProperty(prop)) {
            scene[prop] = {};
            for (var attr in this.attrs) {
                if (this.attrs.hasOwnProperty(attr)) {
                    attr = this.attrs[attr];
                    scene[prop][attr] = this.props[prop].get(attr);
                }
            }
        }
    }

    return scene;
};

Stage.prototype.set_scene = function (scene) {
    scene = scene || 'default';
    this.current_scene = scene;
    this.execute_scene(this.scenes[scene]);
    return this;
};

Stage.prototype.execute_scene = function (scene) {
    for (var prop in scene) {
        if (scene.hasOwnProperty(prop)) {
            for (var attr in this.attrs) {
                if (this.attrs.hasOwnProperty(attr)) {
                    attr = this.attrs[attr];
                    this.props[prop].set(attr, scene[prop][attr]);
                }
            }
        }
    }
};
