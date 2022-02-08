from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.tools import safe_eval


class Contract(models.Model):
    _inherit = "hr.contract"

    report_ids = fields.One2many("report.dynamic", "contract_id")

    def action_create_report(self):
        self.ensure_one()
        # search for agreement templates
        templates = self.env["report.dynamic"].search(
            [("model_id.model", "=", self._name), ("is_template", "=", True)]
        )
        eligible_template = self.env["report.dynamic"]
        for template in templates:
            # Check the template global domain
            if not self._check_template(template):
                continue
            eligible_template += template
        if not eligible_template:
            raise UserError(_("No matching templates found"))
        if len(eligible_template) > 1:
            raise UserError(_("More templates than one found"))
        report = eligible_template.copy()
        # Transform this into an agreement,
        # tailor made for this contract
        report.write(
            {
                "is_template": False,
                "res_id": self.id,
                "contract_id": self.id,
                "resource_ref": self,
                "template_id": eligible_template.id,
                "name": "Report for {}".format(self.employee_id.name),
            }
        )
        return {
            "name": _("Report"),
            "view_mode": "form",
            "res_model": "report.dynamic",
            "type": "ir.actions.act_window",
            # new, because we want to save the form
            "target": "new",
            "res_id": report.id,
        }

    def _check_template(self, template):
        return self in self.search(safe_eval(template.condition_domain_global))
