# -*- coding: utf-8 -*-
from django.conf import settings

from appconf import AppConf


class AldrynSearchAppConf(AppConf):
    INDEX_BASE_CLASS = 'aldryn_search.base.AldrynIndexBase'
    LANGUAGE_FROM_ALIAS = 'aldryn_search.utils.language_from_alias'
    DEFAULT_LANGUAGE = settings.LANGUAGE_CODE
    REGISTER_APPHOOK = True

    class Meta:
        prefix = 'ALDRYN_SEARCH'
