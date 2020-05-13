function odoo_l10n_si_tax_registry_point_of_sale_screens(instance, module) {  // module is instance.point_of_sale
    'use strict';
    var QWeb = instance.web.qweb;

    module.ReceiptScreenWidget.include({
        refresh: function () {
            this._super();

            // FIXME: display this data along with the original receipt.
            var self = this;
            this.pos.l10n_si_tax_reg_export_for_printing(this.pos.get('selectedOrder').attributes.name).done(function (print) {
                if ($.isEmptyObject(print)) {
                    return print;
                }
                var new_print = JSON.parse(JSON.stringify(print));
                new_print.date_order = new Date(print.date_order)
                    .toString(Date.CultureInfo.formatPatterns.shortDate + ' ' +
                        Date.CultureInfo.formatPatterns.longTime);
                new_print.l10n_si_tax_reg_barcode_base64 =
                    'data:image/png;base64,' +
                        print.l10n_si_tax_reg_barcode_base64;
                $(self.$('div.pos-sale-ticket span.l10n_si_tax_reg_ticket'))
                    .replaceWith(QWeb.render('L10nSiTaxRegistryPointOfSaleTicketDateOrder', {
                        widget: self,
                        order: new_print
                    }));
                $(self.$('div.pos-sale-ticket > table:last'))
                    .after(QWeb.render('L10nSiTaxRegistryPointOfSaleTicket', {
                        widget: self,
                        order: new_print
                    }));
                return print;
            });
        }
    });

}
