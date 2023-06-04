odoo.define('spc_utils.bg_color_field', function (require) {
"use strict";

    var AbstractField = require('web.AbstractField');
    var registry = require('web.field_registry');
    var core = require('web.core');
    var _t = core._t;

    var ColoredState = AbstractField.extend({
        className: 'colored_state',
        states: {
            'valide': {class: 'badge-success', name: _t('Valide')},
            'expired': {class: 'badge-danger', name: _t('Expiré')},
        },
        /**
         * @override
         */
        init: function () {
            this._super.apply(this, arguments);
        },
        /**
         * Display widget
         * @override
         * @private
         */
        _render: function () {
            if (this.value) {
                var output = this.states[this.value] ? '<h2><i class="badge badge-pill ' + this.states[this.value].class + '">' + this.states[this.value].name + '</i></h2>' : this.value;
                this.$el.html(output);
            }
        }
    });

    registry.add('colored_state', ColoredState);
    return ColoredState
});