from functools import partial

import factory.fuzzy
from factory.django import DjangoModelFactory

import djstripe.models

from . import fake_models

fake_stripe_id = partial(factory.fuzzy.FuzzyText, length=12)


class AddressFactory(factory.Factory):
	class Meta:
		model = fake_models.Address

	line1 = factory.Faker("street_address")
	line2 = None
	city = factory.Faker("city")
	state = None
	postal_code = factory.Faker("postcode")
	country = factory.Faker("country_code")


class BusinessProfileFactory(factory.Factory):
	class Meta:
		model = fake_models.BusinessProfile

	name = factory.Faker("company")
	url = factory.Faker("url")
	product_description = None
	support_address = factory.SubFactory(AddressFactory)
	support_email = factory.Faker("company_email")
	support_phone = factory.Faker("phone_number")
	support_url = factory.Faker("url")


class AccountFactory(DjangoModelFactory):
	class Meta:
		model = fake_models.Account

	id = fake_stripe_id(prefix="acct_")
	business_profile = factory.SubFactory(BusinessProfileFactory)
