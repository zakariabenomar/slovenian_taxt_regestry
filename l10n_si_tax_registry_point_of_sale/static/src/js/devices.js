function odoo_l10n_si_tax_registry_point_of_sale_devices(instance, module) {  // module is instance.point_of_sale
    'use strict';
    var QWeb = instance.web.qweb;

    module.ProxyDevice.include({
        print_receipt: function (receipt) {
            if (!receipt) {
                return this._super(receipt);
            }

            var rec = this.get_l10n_si_tax_reg_receipt(receipt),
                _super = this._super.bind(this),
                def = new $.Deferred();
            if (!rec.length) {
                return this._super(receipt);
            }
            window.posmodel.l10n_si_tax_reg_export_for_printing(rec.html()).done(function (print) {
                if ($.isEmptyObject(print)) {
                    _super(receipt);
                    def.resolve();
                    return print;
                }
                var img = new Image(),
                    new_print = JSON.parse(JSON.stringify(print));
                new_print.date_order = new Date(print.date_order)
                    .toLocaleString();
                img.onload = function () {
                    var c = document.createElement('canvas'),
                        ctx = c.getContext('2d');
                    c.width = img.width;
                    c.height = img.height;
                    ctx.drawImage(img, 0, 0, img.width, img.height);
                    new_print.l10n_si_tax_reg_barcode_base64 = c.toDataURL();
                    receipt = receipt.replace(rec.appendTo(document.createElement('t')).parent().html(), QWeb.render('L10nSiTaxRegistryPointOfSaleReceipt', {
                        model: window.posmodel,
                        order: new_print
                    }));
                    _super(receipt);
                    def.resolve();
                };
                img.onerror = function () {
                    def.reject();
                };
                img.src = 'data:image/png;base64,' +
                    print.l10n_si_tax_reg_barcode_base64;
                return print;
            }.bind(this)).fail(function (order) {
                // TODO: Error handler.
                window.console.error('err: ' + order);
                def.reject();
            });

            return def;
        },
        get_l10n_si_tax_reg_receipt: function (receipt) {
            return $('span.l10n_si_tax_reg_receipt', receipt);
        }
    });

}
