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

    models.load_models({
        model: 'reservation',
        fields: ['name'],
        domain: [

        ],
        loaded: function(self, reservation) {
            self.reservation = reservation
        }
     });


    models.Order = models.Order.extend({
        initialize: function(sessions, attributes) {

            this.practitioner = false;
            this.reservation = false;


            return SuperOrder.initialize.call(this, sessions, attributes);
        },

        export_as_JSON: function() {
            var orders = SuperOrder.export_as_JSON.call(this);
            var vals = {
                'practitioner': this.practitioner,
                'reservation': this.reservation,
            };
            $.extend(orders, vals);
            return orders;

        }
    })






    var Practitioner = screens.ActionButtonWidget.extend({
        template: 'Practitioner',
        button_click: function() {
            var self = this;
            var employees_list = []
            _.each(self.pos.employees, function(e) {
                employees_list.push({ 'label': e.name, 'item': e.id })
            });


            self.gui.show_popup('selection', {
                title: _t('Select Practitioner'),
                list: employees_list,
                confirm: function(practitioner) {
                    var order = self.pos.get_order();
                    order.practitioner = practitioner;
                    models.practitioner = practitioner;
                },
                is_selected: function(practitioner) {
                    return practitioner === self.pos.get_order().practitioner;
                }
            });
        },
    });

    var Reservation = screens.ActionButtonWidget.extend({
        template: 'ReservationSource',
        button_click: function() {
            var self = this;
            var reservation_list =[]
            _.each(self.pos.reservation, function(e) {
                 reservation_list.push({ 'label': e.name, 'item': e.id})
            });


            self.gui.show_popup('selection', {
                title: _t('Select Reservation'),
                list: reservation_list,
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
        'name': 'practitioner',
        'widget': Practitioner,
    });

    screens.define_action_button({
        'name': 'reservation',
        'widget': Reservation,

    });


});
