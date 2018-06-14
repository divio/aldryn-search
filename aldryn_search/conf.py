# -*- coding: utf-8 -*-
from django.conf import settings

from appconf import AppConf


class AldrynSearchAppConf(AppConf):

    CMS_PAGE = True
    DEFAULT_LANGUAGE = settings.LANGUAGE_CODE
    INDEX_BASE_CLASS = 'aldryn_search.base.AldrynIndexBase'
    ALIAS_FROM_LANGUAGE = 'aldryn_search.utils.alias_from_language'
    LANGUAGE_FROM_ALIAS = 'aldryn_search.utils.language_from_alias'
    PAGINATION = 10
    REGISTER_APPHOOK = True

    class Meta:
        prefix = 'ALDRYN_SEARCH'
