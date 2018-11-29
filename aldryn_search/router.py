# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import get_language

from haystack import routers
from haystack.constants import DEFAULT_ALIAS

from .utils import alias_from_language


class LanguageRouter(routers.BaseRouter):

    def for_read(self, **hints):
        language = get_language()
        alias = alias_from_language(language)

        if alias not in settings.HAYSTACK_CONNECTIONS:
            return DEFAULT_ALIAS
        return alias

    def for_write(self, **hints):
        language = None
        try:
            # Use this for Aldryn Events/FAQ etc 
            #   as 'get_language()' can fail to get the instance language.
            if hints and 'instance' in hints:
                if hasattr(hints['instance'],'language_code'):
                    language = hints['instance'].language_code
        except:
            pass

        if not language:
            language = get_language()

        alias = alias_from_language(language)

        if alias not in settings.HAYSTACK_CONNECTIONS:
            return DEFAULT_ALIAS
        return alias
