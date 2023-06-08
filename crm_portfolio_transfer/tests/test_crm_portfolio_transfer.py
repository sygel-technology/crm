# Copyright 2023 Ángel García de la Chica Herrera <angel.garcia@sygel.es>
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0

from odoo.tests import common
from odoo import exceptions


class TestCrmPortfolioTransfer(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestCrmPortfolioTransfer, cls).setUpClass()
        # cls.current_salesperson = cls.env.ref('base.user_admin')
        # cls.new_salesperson = cls.env.ref('base.user_demo')
        cls.current_salesperson = cls.env['res.users'].create({
            'login': 'current_salesperson',
            'partner_id': cls.env['res.partner'].create({
                'name': "Current Salesperson"
             }).id
        })
        cls.new_salesperson = cls.env['res.users'].create({
            'login': 'new_salesperson',
            'partner_id': cls.env['res.partner'].create({
                'name': "New Salesperson"
            }).id
        })
        cls.partner_contact = cls.env["res.partner"].create(
            {
                "name": "Test partner",
                "user_id": cls.current_salesperson.id
            }
        )
        cls.lead = cls.env["crm.lead"].create({
            "name": "Test lead",
            "user_id": cls.current_salesperson.id
        })
        cls.stage_id = cls.env['crm.stage'].create({
            'name': "Stage Test",
            'allow_transfer_opportunity': False
        })

    def test_review_portfolio(self):
        wizard = self.env["transfer.portfolio.wizard"].create({
            "current_salesperson": self.current_salesperson.id,
            "new_salesperson": self.new_salesperson.id,
        })
        wizard.review_transfer()
        self.assertEqual(
            self.lead.user_id,
            self.current_salesperson
        )
        self.assertEqual(
            self.lead.previous_salesperson_id.id,
            False,
            )
        self.assertEqual(
            self.partner_contact.user_id,
            self.current_salesperson
        )
        self.assertEqual(
            self.partner_contact.previous_salesperson_id.id, 
            False
        )
        contact_id = wizard.contact_ids.filtered(
            lambda x: x.id == self.partner_contact.id
        )
        lead_id = wizard.opportunity_ids.filtered(
            lambda x: x.id == self.lead.id
        )
        self.assertNotEqual(contact_id.id, False)
        self.assertNotEqual(lead_id.id, False)

    def test_transfer_all_portfolio(self):
        wizard = self.env["transfer.portfolio.wizard"].create({
            "current_salesperson": self.current_salesperson.id,
            "new_salesperson": self.new_salesperson.id,
        })
        wizard.review_transfer()
        wizard.transfer_portfolio()
        self.assertEqual(
            self.lead.user_id,
            self.new_salesperson
        )
        self.assertEqual(
            self.lead.previous_salesperson_id,
            self.current_salesperson
        )
        self.assertEqual(
            self.partner_contact.user_id,
            self.new_salesperson
        )
        self.assertEqual(
            self.partner_contact.previous_salesperson_id, 
            self.current_salesperson
        )

    def test_transfer_several_portfolio(self):
        wizard = self.env["transfer.portfolio.wizard"].create({
            "current_salesperson": self.current_salesperson.id,
            "new_salesperson": self.new_salesperson.id,
        })
        wizard.review_transfer()
        wizard.write({
            'opportunity_ids': [(3, self.lead.id)]
        })
        wizard.transfer_portfolio()
        self.assertEqual(
            self.lead.user_id,
            self.current_salesperson
        )
        self.assertEqual(
            self.lead.previous_salesperson_id.id,
            False
        )
        self.assertEqual(
            self.partner_contact.user_id,
            self.new_salesperson
        )
        self.assertEqual(
            self.partner_contact.previous_salesperson_id, 
            self.current_salesperson
        )

    def test_transfer_contact_children(self):
        partner_child_contact = self.env["res.partner"].create(
            {
                "name": "Test children",
                "parent_id": self.partner_contact.id
            }
        )
        wizard = self.env["transfer.portfolio.wizard"].create({
            "current_salesperson": self.current_salesperson.id,
            "new_salesperson": self.new_salesperson.id
        })
        wizard.review_transfer()
        wizard.transfer_portfolio()
        self.assertEqual(
            partner_child_contact.user_id,
            self.new_salesperson
        )
        self.assertEqual(
            partner_child_contact.previous_salesperson_id, 
            self.current_salesperson
        )

    def test_create_registry(self):
        wizard = self.env["transfer.portfolio.wizard"].create({
            "current_salesperson": self.current_salesperson.id,
            "new_salesperson": self.new_salesperson.id,
        })
        wizard.review_transfer()
        wizard.transfer_portfolio()
        registry_id = self.env['portfolio.transfer.registry'].search([
            ("user_made_transfer_id", "=", self.env.user.id),
            ("previous_salesperson_id", "=", self.current_salesperson.id),
            ("new_salesperson_id", "=", self.new_salesperson.id),
            ("list_contacts_ids", "=", "[{}]".format(self.partner_contact.id)),
            ("list_opportunity_ids", "=", "[{}]".format(self.lead.id)),
        ])
        self.assertNotEqual(registry_id.id, False)

    def test_not_new_salesperson_(self):
        wizard = self.env["transfer.portfolio.wizard"].create({
            "current_salesperson": self.current_salesperson.id,
        })
        wizard.review_transfer()
        with self.assertRaises(exceptions.ValidationError): 
            wizard.transfer_portfolio()

    def test_not_portfolio_to_transfer(self):
        wizard = self.env["transfer.portfolio.wizard"].create({
            "current_salesperson": self.current_salesperson.id,
            "new_salesperson": self.new_salesperson.id
        })
        wizard.review_transfer()
        wizard.write({
            'opportunity_ids': [(3, self.lead.id)]
        })
        wizard.write({
            'contact_ids': [(3, self.partner_contact.id)]
        })
        with self.assertRaises(exceptions.ValidationError): 
            wizard.transfer_portfolio()

    def test_review_portfolio_stage_not_allow(self):
        self.lead.write({
            'stage_id': self.stage_id.id 
        })
        wizard = self.env["transfer.portfolio.wizard"].create({
            "current_salesperson": self.current_salesperson.id,
            "new_salesperson": self.new_salesperson.id,
        })
        wizard.review_transfer()
        self.assertNotIn(self.lead.id, wizard.opportunity_ids.ids)

    def test_transfer_count(self):
        current_salesperson = self.env.ref('base.user_admin')
        new_salesperson = self.env.ref('base.user_demo')
        wizard = self.env["transfer.portfolio.wizard"].create({
            "current_salesperson": current_salesperson.id,
            "new_salesperson": new_salesperson.id,
        })
        wizard.review_transfer()
        current_salesperson_contacts_count = len(wizard.contact_ids)
        current_salesperson_leads_count = len(wizard.opportunity_ids)
        new_salesperson_contacts_count = self.env['res.partner'].search_count([
            ('user_id', '=', new_salesperson.id)
        ])
        new_salesperson_leads_count = self.env['crm.lead'].search_count([
            ('user_id', '=', new_salesperson.id)
        ])
        wizard.transfer_portfolio()
        self.assertEqual(self.env['res.partner'].search_count([
            ('user_id', '=', current_salesperson.id)
        ]), 0)
        self.assertEqual(self.env['crm.lead'].search_count([
            ('user_id', '=', current_salesperson.id)
        ]), 0)
        self.assertEqual(self.env['res.partner'].search_count([
            ('user_id', '=', new_salesperson.id)
        ]), 0)
        self.assertEqual(self.env['res.partner'].search_count([
                ('user_id', '=', new_salesperson.id)
            ]), 
            current_salesperson_contacts_count + new_salesperson_contacts_count
        )
        self.assertEqual(self.env['crm.lead'].search_count([
                ('user_id', '=', new_salesperson.id)
            ]), 
            current_salesperson_leads_count + new_salesperson_leads_count
        )
