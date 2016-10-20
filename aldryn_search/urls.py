# -*- coding: utf-8 -*-
from django.conf.urls import url

from aldryn_common.compat import DJANGO_1_6

from aldryn_search.views import AldrynSearchView


urlpatterns = [
    url('^$', AldrynSearchView.as_view(), name='aldryn-search'),
]

if DJANGO_1_6:
    from django.conf.urls import patterns

    urlpatterns = patterns('', urlpatterns[0])
