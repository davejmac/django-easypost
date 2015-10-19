# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from django.core.validators import MinValueValidator

import easypost
easypost.api_key = settings.EASYPOST_API_KEY


class Address(models.Model):
    """
    :param ship: The name for the address
    :param street1: First line for the street in the address
    :param street2: Second line for the unit/apartment information in the address (optional)
    :param city: City for the address
    :param state: State/Province for the address
    :param zip_code: Zip/Postal Code for the address
    :param country: Country for the address
    :param phone: Phone number for the address (optional)
    :param verified_address: The boolean indicating if the address has been verified or not
    """
    ship = models.CharField(max_length=100)
    street1 = models.CharField(max_length=100)
    street2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=25)
    country = models.CharField(max_length=50, default="US")
    phone = models.CharField(max_length=100, blank=True)
    email = models.CharField(max_length=200, blank=True)
    verified_address = models.BooleanField(blank=True, default=False)

    class Meta:
        verbose_name_plural = "addresses"

    def verify(self):
        """
        verifies address against EasyPost's API. Any variations in the address are saved back to the object.
        """
        easypost_address = easypost.Address.create(
            name=self.ship,
            street1=self.street1,
            street2=self.street2,
            city=self.city,
            state=self.state,
            zip=self.zip_code,
            country=self.country,
            phone=self.phone,
            email=self.email
        )
        try:
            verified_from_address = easypost_address.verify()
            self.name = verified_from_address.name,
            self.street1 = verified_from_address.street1,
            self.street1 = verified_from_address.street2,
            self.city = verified_from_address.city,
            self.state = verified_from_address.state,
            self.zip_code = verified_from_address.zip,
            self.country = verified_from_address.country,
            self.phone = verified_from_address.phone,
            self.verified_address = True
            self.save()

        except easypost.Error as e:
            raise e


class Shipment(models.Model):
    """
    A shipment for items in a :class:`orders.models.Order`

    order: the order connected with this shipment
    :param to_address: The :class:`easypost.models.Address` related to the address to which to send the shipment
    :param from_address: The :class:`easypost.models.Address` related to the address from which the shipment is sent
    is_return: indicates if this shipment is a return or not
    """

    class Carrier:
        USPS = "USPS"
        UPS = "UPS"
        FED_EX = "FedEx"

    class RefundPeriod:
        """
        Refund period for carriers in days
        """
        USPS = 10
        USP = 90
        FED_EX = 90

    class Status:
        """
        from EasyPost statuses
        """
        UNKNOWN = 'unknown'
        PRE_TRANSIT = 'pre_transit'
        IN_TRANSIT = 'in_transit'
        FAILURE = 'failure'
        DELIVERED = 'delivered'

    class RefundStatus:
        NONE = ''
        SUBMITTED = 'submitted'
        REJECTED = 'rejected'
        REFUNDED = 'refunded'
        # others?

    class EELCode:
        """
        Standard Exemption/Exclusion License codes
        """
        US_TO_CANADA = 'NOEEL 30.36'
        VALUE_UNDER_2500_USD = 'NOEEL 30.37(a)'

    CARRIER_CHOICES = ((Carrier.USPS, 'USPS'),
                       (Carrier.UPS, Carrier.UPS),
                       (Carrier.FED_EX, Carrier.FED_EX))

    STATUS_CHOICES = ((Status.UNKNOWN, Status.UNKNOWN),
                      (Status.PRE_TRANSIT, Status.PRE_TRANSIT),
                      (Status.IN_TRANSIT, Status.IN_TRANSIT),
                      (Status.FAILURE, Status.FAILURE),
                      (Status.DELIVERED, Status.DELIVERED)
                      )

    REFUND_STATUS_CHOICES = ((RefundStatus.NONE, RefundStatus.NONE),
                             (RefundStatus.SUBMITTED, RefundStatus.SUBMITTED),
                             (RefundStatus.REJECTED, RefundStatus.REJECTED),
                             (RefundStatus.REFUNDED, RefundStatus.REFUNDED),
                             )

    to_address = models.ForeignKey('easypost.Address', related_name="shipments_to")
    from_address = models.ForeignKey('easypost.Address', related_name="shipments_from")
    is_return = models.BooleanField(blank=True, default=False)
    refund_status = models.CharField(max_length=25, blank=True, choices=REFUND_STATUS_CHOICES, default=RefundStatus.NONE)

    easypost_id = models.CharField(max_length=200, blank=True, null=True)
    tracking_code = models.CharField(max_length=75, blank=True, null=True)
    tracking_status = models.CharField(max_length=25, choices=STATUS_CHOICES, default=Status.UNKNOWN, blank=True, null=True)
    carrier = models.CharField(max_length=25, choices=CARRIER_CHOICES, default=Carrier.USPS)
    service = models.CharField(max_length=50, null=True, blank=True)
    rate = models.DecimalField(decimal_places=2, max_digits=10, help_text=_('Shipping cost'), null=True, blank=True)

    created_date = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="shipments")

    def __unicode__(self):
        return u'{0}'.format(self.easypost_id)

    def create_on_easypost(self, parcel, customs_info=None):
        """
        Create the shipment on EasyPost. Requires an EasyPost parcel object
        """
        to_address = {
            'name': self.to_address.ship,
            'street1': self.to_address.street1,
            'street2': self.to_address.street2,
            'city': self.to_address.city,
            'state': self.to_address.state,
            'zip': self.to_address.zip_code,
            'country': self.to_address.country,
            'phone': self.to_address.phone,
            'email': self.to_address.email
        }
        from_address = {
            'name': self.from_address.ship,
            'street1': self.from_address.street1,
            'street2': self.from_address.street2,
            'city': self.from_address.city,
            'state': self.from_address.state,
            'zip': self.from_address.zip_code,
            'country': self.from_address.country,
            'phone': self.from_address.phone,
            'email': self.from_address.email
        }
        shipment = easypost.Shipment.create(
            to_address=to_address,
            from_address=from_address,
            parcel=parcel,
            customs_info=customs_info,
            is_return=self.is_return,
            api_key=settings.EASYPOST_API_KEY
        )
        self.easypost_id = shipment.id
        self.save()
        return shipment

    def get_easypost_shipment(self):
        """
        Gets the easypost.Shipment object from easypost
        """
        assert(self.easypost_id)
        return easypost.Shipment.retrieve(self.easypost_id)

    def update_from_easypost(self):
        """
        Checks easypost for update to tracking code
        """
        easypost_shipment = self.get_easypost_shipment()
        self.tracking_code = easypost_shipment.tracking_code

        self.save()

    def buy_label(self, shipment=None, rate=None, carriers=None, services=None, commit=True):
        """
        But a label for the shipment if one does not exist

        By default, EasyPost returns a label in PNG format. See Label.request_label_file() for other options.

        Uses the default cheapest postage if postage choice is not provided.
        Updates the Shipment's rate, service, and carrier and then optionally saves the Shipment
        if commit is True.  Default is True.
        """

        # lowest_rate() requires carriers and services to either be iterable
        # or not passed at all.  Cannot pass None, etc.
        if services and not carriers:
            # services are specific to carrier, we need to specify a carrier to specify a service
            services = []

        if not services:
            services = []

        if not carriers:
            carriers = []

        try:
            # cannot buy a second label
            return self.label
        except Label.DoesNotExist:
            pass

        # this is a bit slow since it's two lookups
        if not shipment:
            shipment = self.get_easypost_shipment()

        if not rate:
            rate = shipment.lowest_rate(carriers=carriers, services=services)

        l = shipment.buy(rate=rate)
        label = Label(shipment=self,
                      easypost_id=l.id)

        label.label_url = shipment.postage_label.label_url
        # these three show up in the documentation but the test api never returns them
        label.label_pdf_url = getattr(l, 'label_pdf_url', '')
        label.label_epl2_url = getattr(l, 'label_epl2_url', '')
        label.label_zpl_url = getattr(l, 'label_zpl_url', '')
        label.save()

        self.rate = rate.rate
        self.service = rate.service
        self.carrier = rate.carrier
        if commit:
            self.save(update_fields=['rate', 'service', 'carrier'])

        return label

    def refund(self):
        """
        Request a refund for this shipment from EasyPost
        """
        if not self.refund_status:
            shipment = self.get_easypost_shipment()
            shipment.refund()
            self.refund_status = Shipment.RefundStatus.SUBMITTED
            self.save(update_fields=['refund_status'])
        # else raise an exception or return an error?

    def get_shipping_rates(self):
        """
        Returns all of the Rate objects available for this shipment
        """
        shipment = self.get_easypost_shipment()
        return shipment.get_rates().rates

    def get_shipping_rate(self, rate_id):
        rates = self.get_shipping_rates()
        for rate in rates:
            if rate.id == rate_id:
                return rate

        return None

    def update_tracking_history(self, status, message, update_time):
        """
        Adds a new ShipmentTrackingHistory if one does not already exist
        which matches the status, message, and update time for this shipment
        """
        ShipmentTrackingHistory.objects.get_or_create(shipment=self,
                                                      status=status,
                                                      message=message,
                                                      update_time=update_time)

    def get_latest_tracking_update(self):
        try:
            return self.shipmenttrackinghistory_set.latest('date_created')
        except ShipmentTrackingHistory.DoesNotExist:
            return None


class ShipmentItem(models.Model):
    """
    A single item in a :class:`shipments.models.Shipment` relating to an :class:`orders.models.OrderItem`

    shipment: the shipment connected with this shipmentitem
    order_item: the order_item connected with this shipmentitem
    count: how many in this shipment item
    """

    shipment = models.ForeignKey(Shipment)
    count = models.PositiveIntegerField()


class Label(models.Model):
    """
    A shipping label
    """

    class LabelFormats:
        PNG = 'png'
        PDF = 'pdf'
        EPL2 = 'epl2'
        ZPL = 'zpl'

    LABEL_FORMATS = [LabelFormats.ZPL, LabelFormats.PDF, LabelFormats.EPL2, LabelFormats.PNG]

    shipment = models.OneToOneField('Shipment')
    easypost_id = models.CharField(max_length=75, null=True, blank=True)  # should match the shipment id
    label_url = models.CharField(max_length=200, blank=True)
    label_pdf_url = models.CharField(max_length=200, blank=True)
    label_epl2_url = models.CharField(max_length=200, blank=True)
    label_zpl_url = models.CharField(max_length=200, blank=True)

    created_date = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)

    def request_label_file(self, format='pdf', commit=False):
        """
        Request the label in a specific format from EasyPost and saves the url
        """
        # EasyPost only creates a png initially and then asynchronously a pdf by default
        # if pdf is needed right away or epl2 or zpl are needed at all, then separate rquests
        # must be made to EasyPost
        shipment = self.shipment.get_easypost_shipment()
        shipment.label(file_format=format)  # this will raise an exception if no label has been bought yet

        # update all of them
        self.label_url = shipment.postage_label.label_url
        self.label_pdf_url = getattr(shipment.postage_label, 'label_pdf_url', '')
        self.label_epl2_url = getattr(shipment.postage_label, 'label_epl2_url', '')
        self.label_zpl_url = getattr(shipment.postage_label, 'label_zpl_url', '')

        if commit:
            self.save(update_fields=['label_url', 'label_pdf_url', 'label_epl2_url', 'label_zpl_url'])


class Parcel(models.Model):
    class USPSPredefinedPackage:
        CARD = 'Card'
        LETTER = 'Letter'
        FLAT = 'Flat'
        PARCEL = 'Parcel'
        LARGE_PARCEL = 'LargeParcel'
        IRREGULAR_PARCEL = 'IrregularParcel'
        FLAT_RATE_ENVELOPE = 'FlatRateEnvelope'
        FLAT_RATE_LEGAL_ENVELOPE = 'FlatRateLegalEnvelope'
        FLAT_RATE_PADDED_ENVELOPE = 'FlatRatePaddedEnvelope'
        FLAT_RATE_GIFT_CARD_ENVELOPE = 'FlatRateGiveCardEnvelope'
        FLAT_RATE_WINDOW_ENVELOPE = 'FlatRateWindowEnvelope'
        FLAT_RATE_CARDBOARD_ENVELOPE = 'FlatRateCardboardEnvelope'
        SMALL_FLAT_RATE_ENVELOPE = 'SmallFlatRateEnvelope'
        SMALL_FLAT_RATE_BOX = 'SmallFlatRateBox'
        MEDIUM_FLAT_RATE_BOX = 'MediumFlatRateBox'
        LARGE_FLAT_RATE_BOX = 'LargeFlatRateBox'
        REGIONAL_RATE_BOX_A = 'RegionalRateBoxA'
        REGIONAL_RATE_BOX_B = 'RegionalRateBoxB'
        REGIONAL_RATE_BOX_C = 'RegionalRateBoxC'
        LARGE_FLAT_RATE_BOARD_GAME_BOX = 'LargeFlatRateBoardGameBox'

    class UPSPredefinedPackage:
        UPS_LETTER = 'UPSLetter'
        UPS_EXPRESS_BOX = 'UPSExpressBox'
        UPS_25KG_BOX = 'UPS25kgBox'
        UPS_10KG_BOX = 'UPS10kgBox'
        TUBE = 'Tube'
        PAK = 'Pak'
        PALLET = 'Pallet'
        SMALL_EXPRESS_BOX = 'SmallExpressBox'
        MEDIUM_EXPRESS_BOX = 'MediumExpressBox'
        LARGE_EXPRESS_BOX = 'LargeExpressBox'

    class FedExPredefinedPackage:
        FEDEX_ENVELOPE = 'FedExEnvelope'
        FEDEX_BOX = 'FedExBox'
        FEDEX_PAK = 'FedExPak'
        FEDEX_TUBE = 'FedExTube'
        FEDEX_10KG_BOX = 'FedEx10kgBox'
        FEDEX_25KG_BOX = 'FedEx25kgBox'

    _USPS_PREDEFINED_PACKAGE_CHOICES = (
        (USPSPredefinedPackage.CARD, _('USPS Card')),
        (USPSPredefinedPackage.LETTER, _('USPS Letter')),
        (USPSPredefinedPackage.FLAT, _('USPS Flat')),
        (USPSPredefinedPackage.PARCEL, _('USPS Parcel')),
        (USPSPredefinedPackage.LARGE_PARCEL, _('USPS Large Parcel')),
        (USPSPredefinedPackage.IRREGULAR_PARCEL, _('USPS Irregular Parcel')),
        (USPSPredefinedPackage.FLAT_RATE_ENVELOPE, _('USPS Flat Rate Envelope')),
        (USPSPredefinedPackage.FLAT_RATE_LEGAL_ENVELOPE, _('USPS Flat Rate Legal Envelope')),
        (USPSPredefinedPackage.FLAT_RATE_PADDED_ENVELOPE, _('USPS Flat Rate Padded Envelope')),
        (USPSPredefinedPackage.FLAT_RATE_GIFT_CARD_ENVELOPE, _('USPS Flat Rate Gift Card Envelope')),
        (USPSPredefinedPackage.FLAT_RATE_WINDOW_ENVELOPE, _('USPS Flat Rate Window Envelope')),
        (USPSPredefinedPackage.FLAT_RATE_CARDBOARD_ENVELOPE, _('USPS Flat Rate Cardboard Envelope')),
        (USPSPredefinedPackage.SMALL_FLAT_RATE_ENVELOPE, _('USPS Small Flat Rate Envelope')),
        (USPSPredefinedPackage.SMALL_FLAT_RATE_BOX, _('USPS Small Flat Rate Box')),
        (USPSPredefinedPackage.MEDIUM_FLAT_RATE_BOX, _('USPS Medium Flat Rate Box')),
        (USPSPredefinedPackage.LARGE_FLAT_RATE_BOX, _('USPS Large Flat Rate Box')),
        (USPSPredefinedPackage.REGIONAL_RATE_BOX_A, _('USPS Regional Rate Box A')),
        (USPSPredefinedPackage.REGIONAL_RATE_BOX_B, _('USPS Regional Rate Box B')),
        (USPSPredefinedPackage.REGIONAL_RATE_BOX_C, _('USPS Regional Rate Box C')),
        (USPSPredefinedPackage.LARGE_FLAT_RATE_BOARD_GAME_BOX, _('USPS Large Flat Rate Board Game Box')),
    )

    _UPS_PREDEFINED_PACKAGE_CHOICES = (
        (UPSPredefinedPackage.UPS_LETTER, _('UPS Letter')),
        (UPSPredefinedPackage.UPS_EXPRESS_BOX, _('UPS Express Box')),
        (UPSPredefinedPackage.UPS_25KG_BOX, _('UPS 25kg Box')),
        (UPSPredefinedPackage.UPS_10KG_BOX, _('UPS 10kg Box')),
        (UPSPredefinedPackage.TUBE, _('UPS Tube')),
        (UPSPredefinedPackage.PAK, _('UPS Pak')),
        (UPSPredefinedPackage.PALLET, _('UPS Pallet')),
        (UPSPredefinedPackage.SMALL_EXPRESS_BOX, _('UPS Small Express Box')),
        (UPSPredefinedPackage.MEDIUM_EXPRESS_BOX, _('UPS Medium Express Box')),
        (UPSPredefinedPackage.LARGE_EXPRESS_BOX, _('UPS Large Express Box')),
    )

    _FEDEX_PREDEFINED_PACKAGE_CHOICES = (
        (FedExPredefinedPackage.FEDEX_ENVELOPE, _('FedEx Envelope')),
        (FedExPredefinedPackage.FEDEX_BOX, _('FedEx Box')),
        (FedExPredefinedPackage.FEDEX_PAK, _('FedEx Pak')),
        (FedExPredefinedPackage.FEDEX_TUBE, _('FedEx Tube')),
        (FedExPredefinedPackage.FEDEX_10KG_BOX, _('FedEx 10kg Box')),
        (FedExPredefinedPackage.FEDEX_25KG_BOX, _('FedEx 25kg Box')),
    )

    _PREDEFINED_PACKAGE_CHOICES = _USPS_PREDEFINED_PACKAGE_CHOICES + _UPS_PREDEFINED_PACKAGE_CHOICES + _FEDEX_PREDEFINED_PACKAGE_CHOICES

    shipment = models.OneToOneField('Shipment')
    easypost_id = models.CharField(max_length=75, null=True, blank=True)
    length = models.FloatField(blank=True, null=True, help_text=_('Length in inches'))
    height = models.FloatField(blank=True, null=True, help_text=_('Height in inches'))
    width = models.FloatField(blank=True, null=True, help_text=_('Width in inches'))
    weight = models.FloatField(help_text=_("Weight in ounces"), validators=[MinValueValidator(0.1), ],
                               error_messages={'min_value': 'Weight must be at least 0.1 oz.'})  # to ONE decimal place
    predefined_package = models.CharField(max_length=50, blank=True, help_text=_("Predefined package type"), choices=_PREDEFINED_PACKAGE_CHOICES)

    created_date = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)

    def __unicode__(self):
        if self.predefined_package:
            dimensions = u'{0}'.format(self.predefined_package)
        else:
            dimensions = u'{0}x{0}x{0}'.format(self.length, self.width, self.height)

        return "Parcel for shipment id {0} with dimensions [{1}]".format(self.shipment_id, dimensions)

    def create_on_easypost(self):
        try:
            easypost_parcel = easypost.Parcel.create(
                predefined_package=self.predefined_package,
                length=self.length,
                width=self.width,
                height=self.height,
                weight=self.weight
            )
            self.easypost_id = easypost_parcel.id
            self.save()
            return easypost_parcel

        except easypost.Error as e:
            raise e

    @classmethod
    def create_from_easypost_object(cls, easypost_parcel, shipment):
        """
        Create a new Parcel from an easypost Parcel object and an easypost_labels.models.Shipment
        """
        parcel = Parcel(shipment=shipment, easypost_id=easypost_parcel.id, weight=easypost_parcel.weight)
        if getattr(easypost_parcel, 'predefined_package'):
            parcel.predefined_package = easypost_parcel.predefined_package
        else:
            parcel.height = easypost_parcel.height
            parcel.length = easypost_parcel.length
            parcel.width = easypost_parcel.width

        parcel.save()
        return parcel


class ShipmentTrackingHistory(models.Model):
    shipment = models.ForeignKey('Shipment')
    status = models.CharField(max_length=25)
    message = models.TextField()
    update_time = models.DateTimeField(help_text="The datetime given on the tracking update from EasyPost")

    created_date = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)

    def __unicode__(self):
        return u'{0}'.format(self.message)
