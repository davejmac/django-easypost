from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from django.conf import settings

import json

from accounts.factories import UserFactory
from easypost.models import Shipment
from .factories import AddressFactory, ParcelFactory, ShipmentFactory, LabelFactory


class AddressTest(TestCase):

    def setUp(self):
        self.address = AddressFactory.create(
            ship='Four Seasons Hotel Austin',
            street1='98 San Jacinto Blvd',
            city='Austin',
            state='TX',
            zip_code='78701',
            country='US',
            phone='8005551234',
            email='contact@customer.com'
        )

    def test_verify_address(self):
        self.address.verify()
        self.assertTrue(self.address.verified_address)


class ParcelTest(TestCase):

    def setUp(self):
        self.parcel = ParcelFactory.create()

    def test_create_on_easypost(self):
        self.parcel.create_on_easypost()
        self.assertTrue(self.parcel.easypost_id is not None)


class ShipmentTest(TestCase):

    def setUp(self):
        self.user = UserFactory.create()
        self.to_address = AddressFactory.create(
            ship='Four Seasons Hotel Austin',
            street1='98 San Jacinto Blvd',
            city='Austin',
            state='TX',
            zip_code='78701',
            country='US',
            phone='8005551234',
            email='contact@customer.com'
        )
        self.from_address = AddressFactory.create(
            ship='Company Deluxe',
            street1='9321 Pocahontas Trail',
            city='Providence Forge',
            state='VA',
            zip_code='23140',
            country='US',
            phone='8005559304',
            email='support@company.com'
        )
        self.shipment = ShipmentFactory.create(
            to_address=self.to_address,
            from_address=self.from_address,
            created_by=self.user
        )
        self.parcel = ParcelFactory.create(
            shipment=self.shipment
        )
        self.easypost_parcel = self.parcel.create_on_easypost()
        self.easypost_shipment = self.shipment.create_on_easypost(self.easypost_parcel)

    def test_create_on_easypost(self):
        self.assertTrue(self.shipment.easypost_id is not None)

    def test_get_easypost_shipment(self):
        self.assertEqual(self.easypost_shipment.id, self.shipment.get_easypost_shipment().id)

    def test_update_from_easypost(self):
        self.shipment.update_from_easypost()
        self.assertEqual(self.shipment.tracking_code, self.easypost_shipment.tracking_code)

    def test_buy_label(self):
        easypost_label = self.shipment.buy_label(shipment=self.easypost_shipment)

        self.assertEqual(easypost_label.label_url, self.easypost_shipment.postage_label.label_url)

        self.assertTrue(self.shipment.rate is not None)
        self.assertTrue(self.shipment.service is not None)
        self.assertTrue(self.shipment.carrier is not None)

    def test_refund(self):
        self.shipment.buy_label(shipment=self.easypost_shipment)
        self.shipment.refund()
        self.assertEqual(self.shipment.refund_status, Shipment.RefundStatus.SUBMITTED)


class LabelTest(TestCase):

    def setUp(self):
        to_address = AddressFactory.create(
            ship='Four Seasons Hotel Austin',
            street1='98 San Jacinto Blvd',
            city='Austin',
            state='TX',
            zip_code='78701',
            country='US',
            phone='8005551234',
            email='contact@customer.com'
        )
        from_address = AddressFactory.create(
            ship='Company Deluxe',
            street1='9321 Pocahontas Trail',
            city='Providence Forge',
            state='VA',
            zip_code='23140',
            country='US',
            phone='8005559304',
            email='support@company.com'
        )
        shipment = ShipmentFactory.create(to_address=to_address, from_address=from_address)
        parcel = ParcelFactory.create(shipment=shipment)
        easypost_parcel = parcel.create_on_easypost()
        self.easypost_shipment = shipment.create_on_easypost(easypost_parcel)
        self.label = LabelFactory(shipment=shipment)

        # buy label first or else request_label_file() will raise an exception
        rate = self.easypost_shipment.lowest_rate(carriers=[], services=[])
        self.easypost_shipment.buy(rate=rate)

    def test_request_label_file(self):
        self.label.request_label_file()
        self.assertEqual(self.label.label_url, self.easypost_shipment.postage_label.label_url)


class EasypostWebhookCallbackTest(TestCase):
    url_name = 'easypost_webhook_callback'

    def setUp(self):
        self.user = UserFactory.create()
        self.to_address = AddressFactory.create(
            ship='Four Seasons Hotel Austin',
            street1='98 San Jacinto Blvd',
            city='Austin',
            state='TX',
            zip_code='78701',
            country='US',
            phone='8005551234',
            email='contact@customer.com'
        )
        self.from_address = AddressFactory.create(
            ship='Company Deluxe',
            street1='9321 Pocahontas Trail',
            city='Providence Forge',
            state='VA',
            zip_code='23140',
            country='US',
            phone='8005559304',
            email='support@company.com'
        )
        self.shipment = ShipmentFactory.create(
            to_address=self.to_address,
            from_address=self.from_address,
            created_by=self.user
        )
        self.parcel = ParcelFactory.create(
            shipment=self.shipment
        )
        self.easypost_parcel = self.parcel.create_on_easypost()
        self.easypost_shipment = self.shipment.create_on_easypost(self.easypost_parcel)

    @override_settings(CELERY_ALWAYS_EAGER=True)
    def test_post(self):
        pre_transit_data = {
            "id": "evt_qatAiJDM",
            "object": "Event",
            "created_at": "2015-10-13T09:33:35Z",
            "updated_at": "2015-10-15T13:01:22Z",
            "description": "tracker.updated",
            "mode": "test",
            "previous_attributes": {
                "status": "unknown"
            },
            "pending_urls": [],
            "completed_urls": [],
            "result": {
                "id": "trk_EttFFJ5J",
                "object": "Tracker",
                "mode": "test",
                "tracking_code": "9499907123456123456781",
                "status": "pre_transit",
                "tracking_details": [
                    {"object": "TrackingDetail",
                     "datetime": "2013-05-31T00:00:00Z",
                     "message": "Electronic Shipping Info Received Oct 31 2015",
                     "status": "pre_transit"
                     }],
                "shipment_id": self.shipment.easypost_id,
                "created_at": "2015-10-13T09:33:35Z",
                "updated_at": "2015-10-15T13:01:22Z"
            }
        }

        self.assertEqual(self.shipment.shipmenttrackinghistory_set.all().count(), 0)
        self.assertEqual(self.shipment.tracking_status, 'unknown')
        response = self.client.post(reverse(self.url_name), data=json.dumps(pre_transit_data), content_type='application/json')
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.shipment.shipmenttrackinghistory_set.all().count(), 1)
        updated_shipment = Shipment.objects.get(id=self.shipment.id)
        self.assertEqual(updated_shipment.tracking_status, 'pre_transit')
        self.assertEqual(updated_shipment.tracking_code, '9499907123456123456781')
