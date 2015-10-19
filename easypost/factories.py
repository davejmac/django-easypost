from django.conf import settings
import factory
import factory.fuzzy
from factory.django import DjangoModelFactory
from django.utils import timezone

import easypost
easypost.api_key = settings.EASYPOST_API_KEY


class UserFactory(DjangoModelFactory):

    class Meta:
        model = settings.AUTH_USER_MODEL

    first_name = factory.Sequence(lambda n: 'User%d' % n)
    last_name = 'LastName'
    email = factory.LazyAttribute(lambda obj: '%s@example.com' % obj.first_name)

    @factory.post_generation
    def setuser_password(obj, create, extracted, **kwargs):
        obj.set_password('password')
        obj.save()


class AddressFactory(DjangoModelFactory):

    class Meta:
        model = 'easypost.Address'

    ship = factory.Faker('name')
    street1 = factory.Faker('street_address')
    city = factory.Faker('city')
    state = factory.Faker('state_abbr')
    zip_code = factory.Faker('zipcode')
    country = 'US'
    phone = factory.Faker('phone_number')
    email = factory.Faker('free_email')


class ShipmentFactory(DjangoModelFactory):

    class Meta:
        model = 'easypost.Shipment'

    order = factory.SubFactory('orders.factories.OrderFactory')
    to_address = factory.SubFactory('easypost.factories.AddressFactory')
    from_address = factory.SubFactory('easypost.factories.AddressFactory')

    created_by = factory.SubFactory('easypost.factories.UserFactory')


class ShipmentItemFactory(DjangoModelFactory):

    class Meta:
        model = 'easypost.ShipmentItem'

    shipment = factory.SubFactory('easypost.factories.ShipmentFactory')
    order_item = factory.SubFactory('orders.factories.OrderItemFactory')
    count = factory.fuzzy.FuzzyInteger(0, 10)


class LabelFactory(DjangoModelFactory):

    class Meta:
        model = 'easypost.Label'

    shipment = factory.SubFactory('easypost.factories.ShipmentFactory')
    label_url = factory.Faker('url')
    label_pdf_url = factory.Faker('url')
    label_epl2_url = factory.Faker('url')
    label_zpl_url = factory.Faker('url')

    created_by = factory.SubFactory('accounts.factories.UserFactory')

    @factory.lazy_attribute
    def easypost_id(self):
        return self.shipment.easypost_id


class ParcelFactory(DjangoModelFactory):

    class Meta:
        model = 'easypost.Parcel'

    shipment = factory.SubFactory('easypost.factories.ShipmentFactory')
    predefined_package = 'FlatRateEnvelope'
    weight = factory.fuzzy.FuzzyFloat(1.0, 20.0)

    created_by = factory.SubFactory('easypost.factories.UserFactory')

    @factory.lazy_attribute
    def easypost_id(self):
        return self.shipment.easypost_id


class ShipmentTrackingHistoryFactory(DjangoModelFactory):

    class Meta:
        model = 'easypost.ShipmentTrackingHistory'

    shipment = factory.SubFactory('easypost.factories.ShipmentFactory')
    status = factory.fuzzy.FuzzyText(length=20)
    message = factory.Faker('sentence', nb_words=20)
    update_time = factory.fuzzy.FuzzyDateTime(timezone.now())

    created_by = factory.SubFactory('easypost.factories.UserFactory')
