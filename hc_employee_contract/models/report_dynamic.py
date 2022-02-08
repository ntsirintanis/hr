from odoo import fields, models


class ReportDynamic(models.Model):
    _inherit = "report.dynamic"

    contract_id = fields.Many2one("hr.contract")
