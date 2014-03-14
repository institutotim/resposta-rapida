window.preventDefault = function (fn) {
    return function (e) {
        e.preventDefault();
        fn.call(this);
    }
};

window.size = function(obj) {
    var size = 0, key;
    for (key in obj) {
        if (obj.hasOwnProperty(key)) size++;
    }
    return size;
};