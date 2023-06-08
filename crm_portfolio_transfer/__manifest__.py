# Copyright 2023 Ángel García de la Chica <angel.garcia@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "CRM Portfolio Transfer",
    "summary": "Transfer Client Portfolio Between Salespersons.",
    "version": "15.0.1.0.0",
    "category": "crm",
    "website": "https://github.com/OCA/crm",
    "author": "Sygel Technology," "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        'base',
        'crm',
        'sales_team',
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner_views.xml",
        "views/crm_lead_views.xml",
        "views/portfolio_transfer_registry_views.xml",
        "views/crm_stage_views.xml",
        "wizard/transfer_portfolio_wizard_views.xml",
    ],
}
