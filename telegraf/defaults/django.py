from __future__ import absolute_import

from django.conf import settings
from telegraf import defaults
from telegraf.client import TelegrafClient

telegraf = None

if telegraf is None:
    host = getattr(settings, 'TELEGRAF_HOST', defaults.HOST)
    port = getattr(settings, 'TELEGRAF_PORT', defaults.PORT)
    tags = getattr(settings, 'TELEGRAF_TAGS', defaults.TAGS)
    telegraf = TelegrafClient(host=host, port=port, tags=tags)
