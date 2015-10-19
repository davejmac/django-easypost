import celery
from django.conf import settings

import easypost
import dateutil.parser

from .models import Shipment, Label

import logging

logger = logging.getLogger(__name__)


@celery.task(ignore_result=True, default_retry_delay=10, max_retried=20)
def process_webhook_event(easypost_data):
    """
    Take the JSON from an EasyPost webhook POST and process it.
    """
    new_event = easypost.Event()
    new_event = new_event.receive(easypost_data)
    if new_event.description == 'tracker.updated':
        # Currently only handling tracking updates.
        easypost_shipment_id = new_event.result.shipment_id
        shipment = Shipment.objects.get(easypost_id=easypost_shipment_id)
        shipment.tracking_code = new_event.result.tracking_code
        shipment.tracking_status = new_event.result.status
        shipment.save(update_fields=['tracking_code', 'tracking_status'])
        for history in new_event.result.tracking_details:
            event_date = dateutil.parser.parse(history.datetime)
            shipment.update_tracking_history(status=history.status, message=history.message, update_time=event_date)


@celery.task(ignore_result=True, default_retry_delay=10, max_retried=20)
def get_additional_label_formats(label_id):
    """
    Ensure all label formats have been generated and stored.

    By default EasyPost only generates a png label immediately and then asynchronously generates a pdf.
    If the pdf is needed immediately or the zpl is needed at all, then they must be specifically requested.
    This process can be slow, so just automatically request all of them asynchronously.
    """
    label = Label.objects.get(id=label_id)
    for format in Label.LABEL_FORMATS:
        try:
            label.request_label_file(format=format)
        except Exception, e:
            logger.exception(e)

    label.save()


@celery.task(ignore_result=True, default_retry_delay=10, max_retried=20)
def update_refund_statuses():
    """
    Poll the EasyPost API for refund statuses on shipments where a refund has been requested
    """

    shipments = Shipment.objects.filter(refund_status=Shipment.RefundStatus.SUBMITTED)
    for shipment in shipments:
        try:
            easypost_shipment = easypost.Shipment.retrieve(id=shipment.easypost_id, api_key=settings.EASYPOST_SECRET_KEY)
        except Exception, e:
            logger.exception(e)
        else:
            shipment.refund_status = easypost_shipment.refund_status
            shipment.save(update_fields=['refund_status'])
