import attr

# Model-like classes for entities
# This is useful both for generating data in structures
# that don't match our models (eg objects that only appear as hashes in the Stripe API)


@attr.s
class Address:
	line1 = attr.ib()
	line2 = attr.ib()
	city = attr.ib()
	state = attr.ib()
	postal_code = attr.ib()
	country = attr.ib()


@attr.s
class BusinessProfile:
	mcc = attr.ib()
	name = attr.ib()
	url = attr.ib()
	product_description = attr.ib()
	support_address = attr.ib()
	support_email = attr.ib()
	support_phone = attr.ib()
	support_url = attr.ib()


@attr.s
class Account:
	id = attr.ib()
	business_profile = attr.ib()
	business_type = attr.ib()
	capabilities = attr.ib()
	# TODO etc

	object = attr.ib(default="account")
