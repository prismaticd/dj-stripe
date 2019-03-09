import factory
from factory.django import DjangoModelFactory
import djstripe.models


class AddressFactory(factory.Factory):

	line1 = factory.Faker("street_address")
	line2 = None
	city = factory.Faker("city")
	state = None
	postal_code = factory.Faker("postcode")
	country = factory.Faker("country")


class BusinessProfileFactory(factory.Factory):

	name = factory.Faker("company")
	url = factory.Faker("url")
	product_description = None
	support_address = None
	support_email = factory.Faker("company_email")
	support_phone = factory.Faker("phone_numer")
	support_url = factory.Faker("url")


class AccountFactory(DjangoModelFactory):

	class Meta:
		model = djstripe.models.connect.Account

