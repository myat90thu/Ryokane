odoo.define('ryokane_pos_buttons.buttons', function(require) {
    "use strict";

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var utils = require('web.utils');


    var QWeb = core.qweb;

    var _t = core._t;

    var SuperOrder = models.Order.prototype;

    models.load_models({
        model: 'hr.employee',
        fields: ['name'],
        domain: [

        ],
        loaded: function(self, employees) {
            self.employees = employees
        }
    });

    models.Order = models.Order.extend({
        initialize: function(sessions, attributes) {

            this.pratitioner = false;
            this.reservation = false;


            return SuperOrder.initialize.call(this, sessions, attributes);
        },

        export_as_JSON: function() {
            var orders = SuperOrder.export_as_JSON.call(this);
            var vals = {
                'pratitioner': this.pratitioner,
                'reservation': this.reservation,
            };
            $.extend(orders, vals);
            return orders;

        }
    })






    var Pratitioner = screens.ActionButtonWidget.extend({
        template: 'Pratitioner',
        button_click: function() {
            var self = this;
            var employees_list = []
            _.each(self.pos.employees, function(e) {
                employees_list.push({ 'label': e.name, 'item': e.id })
            });


            self.gui.show_popup('selection', {
                title: _t('Select Pratitioner'),
                list: employees_list,
                confirm: function(pratitioner) {
                    var order = self.pos.get_order();
                    order.pratitioner = pratitioner;
                    models.pratitioner = pratitioner;
                },
                is_selected: function(pratitioner) {
                    return pratitioner === self.pos.get_order().pratitioner;
                }
            });
        },
    });

    var ReservationSource = screens.ActionButtonWidget.extend({
        template: 'ReservationSource',
        button_click: function() {
            var self = this;

            self.gui.show_popup('selection', {
                title: _t('Select Reservation Source'),
                list: [
                    { "label": "Walk In", "item": "walk_in" },
                    { "label": "Phone", "item": "phone" },
                    { "label": "Internet", "item": "internet" }
                ],
                confirm: function(reservation) {
                    var order = self.pos.get_order();
                    order.reservation = reservation;
                    models.reservation = reservation;
                },
                is_selected: function(reservation) {
                    return reservation === self.pos.get_order().reservation;
                }
            });
        },
    });

    screens.define_action_button({
        'name': 'pratitioner',
        'widget': Pratitioner,
    });

    screens.define_action_button({
        'name': 'reservation',
        'widget': ReservationSource,

    });


});
