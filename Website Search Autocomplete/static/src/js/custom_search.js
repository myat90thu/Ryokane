odoo.define("web_search.custom_search", function (require) {
    "use strict";
    require('web.dom_ready');
    $('input[name="search"]').devbridgeAutocomplete({
        serviceUrl: '/shop/get_suggest',
        onSelect: function (suggestion) {
            window.location.replace(window.location.origin +
                '/shop/product/' + suggestion.data.id + '?search=' + suggestion.value);
        }
    });
});
