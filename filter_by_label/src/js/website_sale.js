odoo.define('website_sale.website_sale', function(require) {
    'use strict';

    var utils = require('web.utils');
    var ProductConfiguratorMixin = require('sale.ProductConfiguratorMixin');
    var core = require('web.core');
    var config = require('web.config');
    var sAnimations = require('website.content.snippets.animation');
    require("website.content.zoomodoo");

    var _t = core._t;

    sAnimations.registry.WebsiteSale = sAnimations.Class.extend(ProductConfiguratorMixin, {
        selector: '.oe_website_sale',
        read_events: {
            'change form .js_product:first input[name="add_qty"]': '_onChangeAddQuantity',
            'mouseup .js_publish': '_onMouseupPublish',
            'touchend .js_publish': '_onMouseupPublish',
            'change .oe_cart input.js_quantity[data-product-id]': '_onChangeCartQuantity',
            'click .oe_cart a.js_add_suggested_products': '_onClickSuggestedProduct',
            'click a.js_add_cart_json': '_onClickAddCartJSON',
            'click .a-submit': '_onClickSubmit',
            'change form.js_attributes input, form.js_attributes select': '_onChangeAttribute',
            'mouseup form.js_add_cart_json label': '_onMouseupAddCartLabel',
            'touchend form.js_add_cart_json label': '_onMouseupAddCartLabel',
            'change .css_attribute_color input': '_onChangeColorAttribute',
            'click .show_coupon': '_onClickShowCoupon',
            'submit .o_website_sale_search': '_onSubmitSaleSearch',
            'change select[name="country_id"]': '_onChangeCountry',
            'change #shipping_use_same': '_onChangeShippingUseSame',
            'click .toggle_summary': '_onToggleSummary',
            'click input.js_product_change': 'onChangeVariant',
        },
        /**
         * @private
         * @param {Event} ev
         */
        _onSubmitSaleSearch: function(ev) {
            if (!this.$('.dropdown_sorty_by').length) {
                return;
            }
            var $this = $(ev.currentTarget);
            if (!ev.isDefaultPrevented() && !$this.is(".disabled")) {
                ev.preventDefault();
                var oldurl = $this.attr('action');
                oldurl += (oldurl.indexOf("?") === -1) ? "?" : "";
                var search = $this.find('input.search-query');
                window.location = oldurl + '&' + search.attr('x_studio_website_label') + '=' + encodeURIComponent(search.val());
            }
        },
    });
});