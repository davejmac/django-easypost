# -*- coding: utf-8 -*-
from django.conf import settings
import easypost
easypost.api_key = settings.EASYPOST_SECRET_KEY

# TODO model for Address

# TODO model for Parcel

# TODO model for Shipment

# TODO model for PostageLabel
