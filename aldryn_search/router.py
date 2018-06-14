# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import get_language

from haystack import routers
from haystack.constants import DEFAULT_ALIAS

from .helpers import get_alias_from_language


class LanguageRouter(routers.BaseRouter):

    def for_read(self, **hints):
        language = get_language()
        alias = get_alias_from_language(language)

        if alias not in settings.HAYSTACK_CONNECTIONS:
            return DEFAULT_ALIAS
        return alias

    def for_write(self, **hints):
        language = get_language()
        alias = get_alias_from_language(language)

        if alias not in settings.HAYSTACK_CONNECTIONS:
            return DEFAULT_ALIAS
        return alias
