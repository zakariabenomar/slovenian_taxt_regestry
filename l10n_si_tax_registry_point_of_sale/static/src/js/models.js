function odoo_l10n_si_tax_registry_point_of_sale_models(instance, module) {  // module is instance.point_of_sale
    'use strict';
    var PosModelSuper = module.PosModel,
        OrderSuper = module.Order;

    module.PosModel = module.PosModel.extend({
        push_order: function (order) {
            if (!this.config.iface_print_via_proxy || !order) {
                return PosModelSuper
                    .prototype
                    .push_order
                    .call(this, order);
            }

            // FIXME: We assume we push the order before we print it.
            order.set_l10n_si_tax_reg_receipt(true);
            return PosModelSuper
                .prototype
                .push_order
                .call(this, order);
        },
        get_l10n_si_tax_reg_export_print_code_for_printing: function () {
            if (!this.config.l10n_si_tax_reg_code_type) {
                return {
                    'l10n_si_tax_reg_barcode_name': 'Code128',
                    'l10n_si_tax_reg_barcode_width': 600,
                    'l10n_si_tax_reg_barcode_height': 54,
                    'l10n_si_tax_reg_barcode_lines': 3,
                    'l10n_si_tax_reg_barcode_human_readable': true
                };
            }

            var type = {'qr': 'QR', 'code128': 'Code128'},
                print = {
                    'l10n_si_tax_reg_barcode_name':
                        type[this.config.l10n_si_tax_reg_code_type],
                    'l10n_si_tax_reg_barcode_human_readable':
                        this.config.l10n_si_tax_reg_code_human_readable
                };
            if (this.config.l10n_si_tax_reg_code_width &&
                    this.config.l10n_si_tax_reg_code_width > 0) {
                print.l10n_si_tax_reg_barcode_width =
                    this.config.l10n_si_tax_reg_code_width;
            }
            if (this.config.l10n_si_tax_reg_code_height &&
                    this.config.l10n_si_tax_reg_code_height > 0) {
                print.l10n_si_tax_reg_barcode_height =
                    this.config.l10n_si_tax_reg_code_height;
            }
            if (this.config.l10n_si_tax_reg_code_num_lines &&
                    this.config.l10n_si_tax_reg_code_num_lines > 0) {
                print.l10n_si_tax_reg_barcode_lines =
                    this.config.l10n_si_tax_reg_code_num_lines;
            }
            return print;
        },
        l10n_si_tax_reg_export_for_printing: function (order, options, def) {
            def = (def === undefined && new $.Deferred()) || def;
            options = (options === undefined &&
                this.get_l10n_si_tax_reg_export_print_code_for_printing()) ||
                    options;
            var posOrderModel = new instance.web.Model('pos.order'),
                orders = this.db.get_orders(),
                i = 0,
                len = orders.length,
                self = this,
                fun = function () {
                    self.l10n_si_tax_reg_export_for_printing(order, options,
                        def);
                };
            for (i, len; i < len; i += 1) {
                if (orders[i].data.name === order) {
                    window.setTimeout(fun, 2048);
                    return def;
                }
            }

            posOrderModel
                .query(['l10n_si_tax_reg_premise_line_id'])
                .filter([['pos_reference', '=', order]])
                .limit(1)
                .order_by('-date_order')
                .first()
                .then(function (id) {
                    if (!id.l10n_si_tax_reg_premise_line_id) {
                        def.resolve({});
                        return {};
                    }
                    posOrderModel
                        .call('l10n_si_tax_reg_export_for_printing', [id.id], {
                            context: new instance.web.CompoundContext(options)
                        })
                        .then(function (print) {
                            def.resolve(print);
                        })
                        .fail(function () {
                            def.reject(order);
                        });
                    return id;
                })
                .fail(function () {
                    def.reject(order);
                });

            return def;
        }
    });

    module.Order = module.Order.extend({
        initialize: function (attributes) {
            this.l10n_si_tax_reg_receipt = false;
            return OrderSuper
                .prototype
                .initialize
                .call(this, attributes);
        },
        export_for_printing: function () {
            var res = OrderSuper
                .prototype
                .export_for_printing
                .call(this);
            res.l10n_si_tax_reg_receipt = this.get_l10n_si_tax_reg_receipt();
            return res;
        },
        set_l10n_si_tax_reg_receipt: function (receipt) {
            this.l10n_si_tax_reg_receipt = receipt;
        },
        get_l10n_si_tax_reg_receipt: function () {
            return this.l10n_si_tax_reg_receipt;
        }
    });

}
