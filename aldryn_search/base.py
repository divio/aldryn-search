# -*- coding: utf-8 -*-
from haystack import indexes


class AldrynIndexBase(indexes.SearchIndex):
    language = indexes.CharField()
    text = indexes.CharField(document=True, use_template=False)
    description = indexes.CharField(indexed=False, stored=True, null=True)
    pub_date = indexes.DateTimeField(null=True)
    login_required = indexes.BooleanField(default=False)
    url = indexes.CharField(stored=True, indexed=False)
    title = indexes.CharField(stored=True, indexed=False)
    site_id = indexes.IntegerField(stored=True, indexed=True, null=True)
