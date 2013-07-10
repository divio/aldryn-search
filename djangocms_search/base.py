# -*- coding: utf-8 -*-
from haystack import indexes


class TitleIndexBase(indexes.SearchIndex):
    language = indexes.CharField()
    text = indexes.CharField(document=True, use_template=False)
    pub_date = indexes.DateTimeField(model_attr='page__publication_date', null=True)
    login_required = indexes.BooleanField(model_attr='page__login_required')
    url = indexes.CharField(stored=True, indexed=False)
    title = indexes.CharField(stored=True, indexed=False, model_attr='title')
    site_id = indexes.IntegerField(stored=True, indexed=True, model_attr='page__site_id')
