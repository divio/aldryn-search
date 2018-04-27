# -*- coding: utf-8 -*-
from django.conf.urls import url

from aldryn_search.views import AldrynSearchView


urlpatterns = [
    url('^$', AldrynSearchView.as_view(), name='aldryn-search'),
]
