# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

urlpatterns = patterns('easypost.views',
                       url(r'^webhook/$', 'easypost_webhook_callback', name='easypost_webhook_callback'),
)
