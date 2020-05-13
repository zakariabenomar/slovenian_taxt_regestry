openerp.l10n_si_tax_registry_point_of_sale = function (instance) {
    'use strict';

    instance.l10n_si_tax_registry_point_of_sale = {};

    var module = instance.point_of_sale;

    odoo_l10n_si_tax_registry_point_of_sale_models(instance, module);  // import l10n_si_tax_registry_point_of_sale_models.js

    odoo_l10n_si_tax_registry_point_of_sale_screens(instance, module);  // import l10n_si_tax_registry_point_of_sale_screens.js

    odoo_l10n_si_tax_registry_point_of_sale_devices(instance, module);  // import l10n_si_tax_registry_point_of_sale_devices.js
};
