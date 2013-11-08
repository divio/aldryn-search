# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import get_language

from haystack import routers
from haystack.constants import DEFAULT_ALIAS


class LanguageRouter(routers.BaseRouter):
    def for_read(self, **hints):
        language = get_language()
        if language not in settings.HAYSTACK_CONNECTIONS:
            return DEFAULT_ALIAS
        return language
