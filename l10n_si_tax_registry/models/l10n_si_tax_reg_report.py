# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models

class L10nSiTaxRegReport(models.AbstractModel):
    _name = 'l10n_si_tax_reg.report'

    def render_html(self, data=None):
        """overridden to increase print counter"""

        report_name, doc_args = self._l10n_si_tax_reg_render_html(data=data)
        return self.env['report'].render(report_name, doc_args)

    def _l10n_si_tax_reg_render_html(self, data=None):
        report_name = self._name.split('.', 1)[1]
        report = self.env['report']._get_report_from_name(report_name)

        doc_args = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self.env[report.model].browse(self._ids),
        }

        for doc in doc_args['docs']:
            if doc.l10n_si_tax_reg_premise_line_id:
                doc.l10n_si_tax_reg_num_copy += 1

        return (report_name, doc_args)
