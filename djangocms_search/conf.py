# -*- coding: utf-8 -*-

from django.conf import settings
from appconf import AppConf


class DjangoCMSSearchAppConf(AppConf):
    INDEX_BASE_CLASS = 'djangocms_search.base.TitleIndexBase'

    class Meta:
        prefix = 'DJANGOCMS_SEARCH'
