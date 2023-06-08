# Copyright 2023 Ángel García de la Chica Herrera <angel.garcia@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, _
from datetime import datetime
from odoo.exceptions import ValidationError


class TransferPorfolioWizard(models.TransientModel):
    _name = "transfer.portfolio.wizard"
    _description = "Transfer Portfolio Wizard"

    current_salesperson = fields.Many2one(
        comodel_name="res.users",
        required=True,
        string="Current Salesperson"
    )
    new_salesperson = fields.Many2one(        
        comodel_name="res.users",
        string="New Salesperson"
    )
    review_state = fields.Boolean(
        default=False,
        string="Review State"
    )
    contact_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Contacts",
        domain="[('user_id', '=', current_salesperson)]"
    )
    opportunity_ids = fields.Many2many(
        comodel_name="crm.lead",
        string="Opportunities",
        domain="[('user_id', '=', current_salesperson), ('stage_id.allow_transfer_opportunity', '=', True)]"
    )

    def review_transfer(self):
        self.ensure_one()
        self.contact_ids = self.env['res.partner'].search([
            ('user_id', '=', self.current_salesperson.id),
        ])
        self.opportunity_ids = self.env['crm.lead'].search([
            ('user_id', '=', self.current_salesperson.id),
            ('stage_id.allow_transfer_opportunity', '=', True)
        ])
        self.review_state = True
        return {
            'name': 'Transfer Portfolio',
            'view_mode': 'form',
            'view_id': False,
            'res_model': self._name,
            'domain': [],
            'context': dict(self._context, active_ids=self.ids),
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.id,
        }

    def transfer_portfolio(self):
        if not self.new_salesperson:
            raise ValidationError(_(
                "You must select a new salesperson."
            ))
        transfer_ids = self.filtered(
            lambda x: x.contact_ids or x.opportunity_ids
        )
        if not transfer_ids:
            raise ValidationError(_(
                "There are no records to transfer."
            ))
        contact_child_ids = self.env['res.partner'].search(
            [('parent_id', 'in', self.contact_ids.ids)]
        )
        self.contact_ids += contact_child_ids
        for sel in transfer_ids:
            vals = sel._get_vals_transfer_registry()
            sel.env['portfolio.transfer.registry'].create(vals)
            self.env['res.partner'].browse(sel.contact_ids.ids).write({
                "previous_salesperson_id": sel.current_salesperson.id,
                "user_id": sel.new_salesperson.id
                })
            self.env['crm.lead'].browse(sel.opportunity_ids.ids).write({
                "previous_salesperson_id": sel.current_salesperson.id,
                "user_id": sel.new_salesperson.id
                })

    def clear_records(self):
        self.write({
            'contact_ids': False,
            'opportunity_ids': False
        })
        return {
            'name': 'Transfer Portfolio',
            'view_mode': 'form',
            'view_id': False,
            'res_model': self._name,
            'domain': [],
            'context': dict(self._context, active_ids=self.ids),
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.id,
        }

    def _get_vals_transfer_registry(self):
        return {
            "user_made_transfer_id": self.env.user.id,
            "date_transfer": datetime.now(),
            "previous_salesperson_id": self.current_salesperson.id,
            "new_salesperson_id": self.new_salesperson.id,
            "list_contacts_ids": "{}".format(self.contact_ids.ids),
            "list_opportunity_ids": "{}".format(self.opportunity_ids.ids),
        }
