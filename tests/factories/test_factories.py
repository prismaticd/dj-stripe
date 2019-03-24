import factory
from django.test import TestCase

from . import connect


class TestConnectFactories(TestCase):
	def test_build_dict(self):
		for factory_class in (
			connect.AddressFactory,
			connect.BusinessProfileFactory,
			connect.AccountFactory,
		):
			# simple sanity check that build succeeds
			d = factory.build(dict, FACTORY_CLASS=factory_class)

	def test_build(self):
		for factory_class in (
			connect.AddressFactory,
			connect.BusinessProfileFactory,
			connect.AccountFactory,
		):
			# simple sanity check that build succeeds
			factory_class.build()

	def test_build_account_factory(self):
		account = connect.AccountFactory.build()
		business_profile = account.business_profile
		support_address_dict = business_profile.support_address

