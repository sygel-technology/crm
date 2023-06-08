# Copyright 2023 Ángel García de la Chica Herrera <angel.garcia@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    previous_salesperson_id = fields.Many2one(
        comodel_name="res.users",
        readonly=True,
        string='Previous Salesperson',
    )
