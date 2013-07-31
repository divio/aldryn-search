# -*- coding: utf-8 -*-
import logging
from django.conf import settings
from django.utils.translation import get_language

from haystack import routers

logger = logging.getLogger(__name__)

class LanguageRouter(routers.BaseRouter):
    def for_read(self, **hints):
        language = get_language()
        logger.info("Current routed language is %s" % (language))
        if language not in settings.HAYSTACK_CONNECTIONS:
            return 'default'
        return language