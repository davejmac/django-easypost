# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Address, Shipment, ShipmentItem, Parcel, ShipmentTrackingHistory


admin.site.register(Address)
admin.site.register(Shipment)
admin.site.register(ShipmentItem)
admin.site.register(Parcel)
admin.site.register(ShipmentTrackingHistory)
