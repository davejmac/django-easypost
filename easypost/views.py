# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt

import json

from .tasks import process_webhook_event


@csrf_exempt
def easypost_webhook_callback(request):
    """
    Handle webhook callbacks from EasyPost
    """

    if request.method == 'POST':
        post_content = request.body
        # responses need to be 30 seconds or less, so rather than processing here, this just verifies that JSON could be decoded
        # and then pushes it off to an asynchronous task
        process_webhook_event.delay(post_content)
        return HttpResponse()

    return HttpResponseNotAllowed(['POST', ])
