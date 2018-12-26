"""
dj-stripe Invoice Model Tests.
"""
from copy import deepcopy
from unittest.mock import ANY, patch

from django.contrib.auth import get_user_model
from django.test.testcases import TestCase
from stripe.error import InvalidRequestError

from djstripe.models import Invoice, Plan, Subscription, UpcomingInvoice
from djstripe.settings import STRIPE_SECRET_KEY

from . import (
	FAKE_BALANCE_TRANSACTION, FAKE_CARD, FAKE_CHARGE,
	FAKE_CUSTOMER, FAKE_INVOICE, FAKE_INVOICEITEM_II, FAKE_PLAN,
	FAKE_SUBSCRIPTION, FAKE_UPCOMING_INVOICE, default_account
)


class InvoiceTest(TestCase):
	def setUp(self):
		self.account = default_account()
		self.user = get_user_model().objects.create_user(
			username="pydanny", email="pydanny@gmail.com"
		)
		self.customer = FAKE_CUSTOMER.create_for_user(self.user)

	@patch("djstripe.models.Account.get_default_account")
	@patch("stripe.Subscription.retrieve", return_value=deepcopy(FAKE_SUBSCRIPTION))
	@patch("stripe.Charge.retrieve", return_value=deepcopy(FAKE_CHARGE))
	def test_str(
		self, charge_retrieve_mock, subscription_retrive_mock, default_account_mock
	):
		default_account_mock.return_value = self.account
		invoice = Invoice.sync_from_stripe_data(deepcopy(FAKE_INVOICE))
		self.assertEqual(
			invoice.get_stripe_dashboard_url(), self.customer.get_stripe_dashboard_url()
		)
		self.assertEqual(str(invoice), "Invoice #XXXXXXX-0001")

		# check fks
		self.assertEqual(FAKE_CHARGE["id"], invoice.charge.id)
		self.assertEqual(FAKE_SUBSCRIPTION["id"], invoice.subscription.id)

		charge = invoice.charge

		# check fks on Charge
		self.assertEqual(FAKE_BALANCE_TRANSACTION["id"], charge.balance_transaction.id)
		self.assertEqual(FAKE_CUSTOMER["id"], charge.customer.id)
		# TODO
		# self.assertEqual(FAKE_INVOICE["id"], charge.invoice.id)
		self.assertEqual(FAKE_CARD["id"], charge.source.id)

		subscription = invoice.subscription

		# check fks on Subscription
		self.assertEqual(FAKE_CUSTOMER["id"], subscription.customer.id)
		self.assertEqual(FAKE_PLAN["id"], subscription.plan.id)

	@patch("stripe.Invoice.retrieve")
	@patch("djstripe.models.Account.get_default_account")
	@patch("stripe.Subscription.retrieve", return_value=deepcopy(FAKE_SUBSCRIPTION))
	@patch("stripe.Charge.retrieve", return_value=deepcopy(FAKE_CHARGE))
	def test_retry_true(
		self,
		charge_retrieve_mock,
		subscription_retrieve_mock,
		default_account_mock,
		invoice_retrieve_mock,
	):
		default_account_mock.return_value = self.account

		fake_invoice = deepcopy(FAKE_INVOICE)
		fake_invoice.update({"paid": False, "closed": False})
		invoice_retrieve_mock.return_value = fake_invoice

		invoice = Invoice.sync_from_stripe_data(fake_invoice)
		return_value = invoice.retry()

		invoice_retrieve_mock.assert_called_once_with(
			id=invoice.id, api_key=STRIPE_SECRET_KEY, expand=[]
		)
		self.assertTrue(return_value)

	@patch("stripe.Invoice.retrieve")
	@patch("djstripe.models.Account.get_default_account")
	@patch("stripe.Subscription.retrieve", return_value=deepcopy(FAKE_SUBSCRIPTION))
	@patch("stripe.Charge.retrieve", return_value=deepcopy(FAKE_CHARGE))
	def test_retry_false(
		self,
		charge_retrieve_mock,
		subscription_retrieve_mock,
		default_account_mock,
		invoice_retrieve_mock,
	):
		default_account_mock.return_value = self.account

		fake_invoice = deepcopy(FAKE_INVOICE)
		invoice_retrieve_mock.return_value = fake_invoice

		invoice = Invoice.sync_from_stripe_data(fake_invoice)
		return_value = invoice.retry()

		self.assertFalse(invoice_retrieve_mock.called)
		self.assertFalse(return_value)

	@patch("djstripe.models.Account.get_default_account")
	@patch("stripe.Subscription.retrieve", return_value=deepcopy(FAKE_SUBSCRIPTION))
	@patch("stripe.Charge.retrieve", return_value=deepcopy(FAKE_CHARGE))
	def test_status_paid(
		self, charge_retrieve_mock, subscription_retrieve_mock, default_account_mock
	):
		default_account_mock.return_value = self.account

		invoice = Invoice.sync_from_stripe_data(deepcopy(FAKE_INVOICE))

		self.assertEqual(Invoice.STATUS_PAID, invoice.status)

	@patch("djstripe.models.Account.get_default_account")
	@patch("stripe.Subscription.retrieve", return_value=deepcopy(FAKE_SUBSCRIPTION))
	@patch("stripe.Charge.retrieve", return_value=deepcopy(FAKE_CHARGE))
	def test_status_open(
		self, charge_retrieve_mock, subscription_retrieve_mock, default_account_mock
	):
		default_account_mock.return_value = self.account

		invoice_data = deepcopy(FAKE_INVOICE)
		invoice_data.update({"paid": False, "closed": False})
		invoice = Invoice.sync_from_stripe_data(invoice_data)

		self.assertEqual(Invoice.STATUS_OPEN, invoice.status)

	@patch("djstripe.models.Account.get_default_account")
	@patch("stripe.Subscription.retrieve", return_value=deepcopy(FAKE_SUBSCRIPTION))
	@patch("stripe.Charge.retrieve", return_value=deepcopy(FAKE_CHARGE))
	def test_status_forgiven(
		self, charge_retrieve_mock, subscription_retrieve_mock, default_account_mock
	):
		default_account_mock.return_value = self.account

		invoice_data = deepcopy(FAKE_INVOICE)
		invoice_data.update({"paid": False, "closed": False, "forgiven": True})
		invoice = Invoice.sync_from_stripe_data(invoice_data)

		self.assertEqual(Invoice.STATUS_FORGIVEN, invoice.status)

	@patch("djstripe.models.Account.get_default_account")
	@patch("stripe.Subscription.retrieve", return_value=deepcopy(FAKE_SUBSCRIPTION))
	@patch("stripe.Charge.retrieve", return_value=deepcopy(FAKE_CHARGE))
	def test_status_closed(
		self, charge_retrieve_mock, subscription_retrieve_mock, default_account_mock
	):
		default_account_mock.return_value = self.account

		invoice_data = deepcopy(FAKE_INVOICE)
		invoice_data.update({"paid": False})
		invoice = Invoice.sync_from_stripe_data(invoice_data)

		self.assertEqual(Invoice.STATUS_CLOSED, invoice.status)

	@patch("djstripe.models.Account.get_default_account")
	@patch("stripe.Plan.retrieve", return_value=deepcopy(FAKE_PLAN))
	@patch("stripe.Subscription.retrieve", return_value=deepcopy(FAKE_SUBSCRIPTION))
	@patch("stripe.Charge.retrieve", return_value=deepcopy(FAKE_CHARGE))
	def test_sync_no_subscription(
		self,
		charge_retrieve_mock,
		subscription_retrieve_mock,
		plan_retrieve_mock,
		default_account_mock,
	):
		default_account_mock.return_value = self.account

		invoice_data = deepcopy(FAKE_INVOICE)
		invoice_data.update({"subscription": None})
		invoice = Invoice.sync_from_stripe_data(invoice_data)

		self.assertEqual(None, invoice.subscription)

		self.assertEqual(FAKE_CHARGE["id"], invoice.charge.id)
		self.assertEqual(FAKE_PLAN["id"], invoice.plan.id)

		# charge_retrieve_mock.assert_not_called()
		plan_retrieve_mock.assert_not_called()
		subscription_retrieve_mock.assert_not_called()

	@patch("djstripe.models.Account.get_default_account")
	@patch("stripe.Subscription.retrieve", return_value=deepcopy(FAKE_SUBSCRIPTION))
	@patch("stripe.Charge.retrieve", return_value=deepcopy(FAKE_CHARGE))
	def test_invoice_with_subscription_invoice_items(
		self, charge_retrieve_mock, subscription_retrieve_mock, default_account_mock
	):
		default_account_mock.return_value = self.account

		invoice_data = deepcopy(FAKE_INVOICE)
		invoice = Invoice.sync_from_stripe_data(invoice_data)

		items = invoice.invoiceitems.all()
		self.assertEqual(1, len(items))
		item_id = "{invoice_id}-{subscription_id}".format(
			invoice_id=invoice.id, subscription_id=FAKE_SUBSCRIPTION["id"]
		)
		self.assertEqual(item_id, items[0].id)

	@patch("djstripe.models.Account.get_default_account")
	@patch("stripe.Subscription.retrieve", return_value=deepcopy(FAKE_SUBSCRIPTION))
	@patch("stripe.Charge.retrieve", return_value=deepcopy(FAKE_CHARGE))
	def test_invoice_with_no_invoice_items(
		self, charge_retrieve_mock, subscription_retrieve_mock, default_account_mock
	):
		default_account_mock.return_value = self.account

		invoice_data = deepcopy(FAKE_INVOICE)
		invoice_data["lines"] = []
		invoice = Invoice.sync_from_stripe_data(invoice_data)

		self.assertIsNotNone(invoice.plan)  # retrieved from invoice item
		self.assertEqual(FAKE_PLAN["id"], invoice.plan.id)

	@patch("djstripe.models.Account.get_default_account")
	@patch("stripe.Subscription.retrieve", return_value=deepcopy(FAKE_SUBSCRIPTION))
	@patch("stripe.Charge.retrieve", return_value=deepcopy(FAKE_CHARGE))
	def test_invoice_with_non_subscription_invoice_items(
		self, charge_retrieve_mock, subscription_retrieve_mock, default_account_mock
	):
		default_account_mock.return_value = self.account

		invoice_data = deepcopy(FAKE_INVOICE)
		invoice_data["lines"]["data"].append(deepcopy(FAKE_INVOICEITEM_II))
		invoice_data["lines"]["total_count"] += 1
		invoice = Invoice.sync_from_stripe_data(invoice_data)

		self.assertIsNotNone(invoice)
		self.assertEqual(2, len(invoice.invoiceitems.all()))

	@patch("djstripe.models.Account.get_default_account")
	@patch("stripe.Subscription.retrieve", return_value=deepcopy(FAKE_SUBSCRIPTION))
	@patch("stripe.Charge.retrieve", return_value=deepcopy(FAKE_CHARGE))
	def test_invoice_plan_from_invoice_items(
		self, charge_retrieve_mock, subscription_retrieve_mock, default_account_mock
	):
		default_account_mock.return_value = self.account

		invoice_data = deepcopy(FAKE_INVOICE)
		invoice = Invoice.sync_from_stripe_data(invoice_data)

		self.assertIsNotNone(invoice.plan)  # retrieved from invoice item
		self.assertEqual(FAKE_PLAN["id"], invoice.plan.id)

	@patch("djstripe.models.Account.get_default_account")
	@patch("stripe.Subscription.retrieve", return_value=deepcopy(FAKE_SUBSCRIPTION))
	@patch("stripe.Charge.retrieve", return_value=deepcopy(FAKE_CHARGE))
	def test_invoice_plan_from_subscription(
		self, charge_retrieve_mock, subscription_retrieve_mock, default_account_mock
	):
		default_account_mock.return_value = self.account

		invoice_data = deepcopy(FAKE_INVOICE)
		invoice_data["lines"]["data"][0]["plan"] = None
		invoice = Invoice.sync_from_stripe_data(invoice_data)
		self.assertIsNotNone(invoice.plan)  # retrieved from subscription
		self.assertEqual(FAKE_PLAN["id"], invoice.plan.id)

	@patch("djstripe.models.Account.get_default_account")
	@patch("stripe.Subscription.retrieve", return_value=deepcopy(FAKE_SUBSCRIPTION))
	@patch("stripe.Charge.retrieve", return_value=deepcopy(FAKE_CHARGE))
	def test_invoice_without_plan(
		self, charge_retrieve_mock, subscription_retrieve_mock, default_account_mock
	):
		default_account_mock.return_value = self.account

		invoice_data = deepcopy(FAKE_INVOICE)
		invoice_data["lines"]["data"][0]["plan"] = None
		invoice_data["subscription"] = None
		invoice = Invoice.sync_from_stripe_data(invoice_data)
		self.assertIsNone(invoice.plan)

	@patch("stripe.Plan.retrieve", return_value=deepcopy(FAKE_PLAN))
	@patch("stripe.Subscription.retrieve", return_value=deepcopy(FAKE_SUBSCRIPTION))
	@patch("stripe.Invoice.upcoming", return_value=deepcopy(FAKE_UPCOMING_INVOICE))
	def test_upcoming_invoice(
		self, invoice_upcoming_mock, subscription_retrieve_mock, plan_retrieve_mock
	):
		invoice = UpcomingInvoice.upcoming()
		self.assertIsNotNone(invoice)
		self.assertIsNone(invoice.id)
		self.assertIsNone(invoice.save())
		self.assertEqual(invoice.get_stripe_dashboard_url(), "")

		subscription_retrieve_mock.assert_called_once_with(
			api_key=ANY, expand=ANY, id=FAKE_SUBSCRIPTION["id"]
		)
		plan_retrieve_mock.assert_not_called()

		items = invoice.invoiceitems.all()
		self.assertEqual(1, len(items))
		self.assertEqual(FAKE_SUBSCRIPTION["id"], items[0].id)

		# delete/update should do nothing
		self.assertEqual(invoice.invoiceitems.update(), 0)
		self.assertEqual(invoice.invoiceitems.delete(), 0)

		self.assertIsNotNone(invoice.plan)
		self.assertEqual(FAKE_PLAN["id"], invoice.plan.id)

		invoice._invoiceitems = []
		items = invoice.invoiceitems.all()
		self.assertEqual(0, len(items))
		self.assertIsNotNone(invoice.plan)

	@patch("stripe.Plan.retrieve", return_value=deepcopy(FAKE_PLAN))
	@patch("stripe.Subscription.retrieve", return_value=deepcopy(FAKE_SUBSCRIPTION))
	@patch("stripe.Invoice.upcoming", return_value=deepcopy(FAKE_UPCOMING_INVOICE))
	def test_upcoming_invoice_with_subscription(
		self, invoice_upcoming_mock, subscription_retrieve_mock, plan_retrieve_mock
	):
		invoice = Invoice.upcoming(subscription=Subscription(id=FAKE_SUBSCRIPTION["id"]))
		self.assertIsNotNone(invoice)
		self.assertIsNone(invoice.id)
		self.assertIsNone(invoice.save())

		subscription_retrieve_mock.assert_called_once_with(
			api_key=ANY, expand=ANY, id=FAKE_SUBSCRIPTION["id"]
		)
		plan_retrieve_mock.assert_not_called()

		self.assertIsNotNone(invoice.plan)
		self.assertEqual(FAKE_PLAN["id"], invoice.plan.id)

	@patch("stripe.Plan.retrieve", return_value=deepcopy(FAKE_PLAN))
	@patch("stripe.Subscription.retrieve", return_value=deepcopy(FAKE_SUBSCRIPTION))
	@patch("stripe.Invoice.upcoming", return_value=deepcopy(FAKE_UPCOMING_INVOICE))
	def test_upcoming_invoice_with_subscription_plan(
		self, invoice_upcoming_mock, subscription_retrieve_mock, plan_retrieve_mock
	):
		invoice = Invoice.upcoming(subscription_plan=Plan(id=FAKE_PLAN["id"]))
		self.assertIsNotNone(invoice)
		self.assertIsNone(invoice.id)
		self.assertIsNone(invoice.save())

		subscription_retrieve_mock.assert_called_once_with(
			api_key=ANY, expand=ANY, id=FAKE_SUBSCRIPTION["id"]
		)
		plan_retrieve_mock.assert_not_called()

		self.assertIsNotNone(invoice.plan)
		self.assertEqual(FAKE_PLAN["id"], invoice.plan.id)

	@patch(
		"stripe.Invoice.upcoming",
		side_effect=InvalidRequestError("Nothing to invoice for customer", None),
	)
	def test_no_upcoming_invoices(self, invoice_upcoming_mock):
		invoice = Invoice.upcoming()
		self.assertIsNone(invoice)

	@patch(
		"stripe.Invoice.upcoming", side_effect=InvalidRequestError("Some other error", None)
	)
	def test_upcoming_invoice_error(self, invoice_upcoming_mock):
		with self.assertRaises(InvalidRequestError):
			Invoice.upcoming()
