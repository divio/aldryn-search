# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import get_language

from haystack import routers
from haystack.constants import DEFAULT_ALIAS
from haystack.exceptions import NotHandled

from .utils import alias_from_language


class LanguageRouter(routers.BaseRouter):

    def get_alias_from_active_language(self):
        language = get_language()
        alias = alias_from_language(language)

        if alias not in settings.HAYSTACK_CONNECTIONS:
            return DEFAULT_ALIAS
        return alias

    def for_read(self, **hints):
        return self.get_alias_from_active_language()

    def for_write(self, **hints):
        alias = self.get_alias_from_active_language()
        instance = hints.get('instance')

        if instance:
            from haystack import connections

            unified_index = connections[alias].get_unified_index()

            try:
                index = unified_index.get_index(instance.__class__)
            except NotHandled:
                return alias

            # language can be None if the object is not language aware.
            # if it does return None then we fallback to the old behavior
            # of relying on the thread language.
            language = index.get_language(obj=instance)

            if language:
                # Override alias with one matching the object language.
                alias = alias_from_language(language)
        return alias
