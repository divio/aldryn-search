# -*- coding: utf-8 -*-
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from django.utils.translation import override

from haystack import indexes
from haystack.constants import DEFAULT_ALIAS

from cms.utils.i18n import get_current_language

from .conf import settings


class AldrynIndexBase(indexes.SearchIndex):
    # For some apps it makes sense to turn on the title indexing.
    INDEX_TITLE = False

    language = indexes.CharField()
    text = indexes.CharField(document=True, use_template=False)
    description = indexes.CharField(indexed=False, stored=True, null=True)
    pub_date = indexes.DateTimeField(null=True)
    login_required = indexes.BooleanField(default=False)
    url = indexes.CharField(stored=True, indexed=False)
    title = indexes.CharField(stored=True, indexed=False)
    site_id = indexes.IntegerField(stored=True, indexed=True, null=True)

    def index_queryset(self, using=None):
        self._backend_alias = using
        language = self.get_current_language(using)
        filter_kwargs = self.get_index_kwargs(language)
        qs = self.get_index_queryset(language)
        return (qs.filter(**filter_kwargs))

    def get_index_queryset(self, language):
        return self.get_model().objects.all()

    def prepare(self, obj):
        current_language = self.get_current_language(using=self._backend_alias, obj=obj)

        with override(current_language):
            self.prepared_data = super(AldrynIndexBase, self).prepare(obj)

            request_factory = RequestFactory(HTTP_HOST=settings.ALLOWED_HOSTS[0])
            request = request_factory.get("/")
            request.session = {}
            request.LANGUAGE_CODE = current_language
            # Needed for plugin rendering.
            request.current_page = None
            request.user = AnonymousUser()

            self.prepared_data['text'] = self.get_search_data(obj, current_language, request)
            self.prepared_data['language'] = current_language
            # We set the following fields here because on some models,
            # the value of these fields is dependent on the active language
            # this being the case we extrapolate the language hacks.
            self.prepared_data['url'] = self.get_url(obj)
            self.prepared_data['title'] = self.get_title(obj)
            self.prepared_data['description'] = self.get_description(obj)

            if self.INDEX_TITLE:
                self.prepared_data['text'] = self.prepared_data['title'] + " " + self.prepared_data['text']

            return self.prepared_data

    def get_current_language(self, using=None, obj=None):
        language = self.get_language(obj) if obj else None
        return language or self.get_default_language(using)

    def get_language(self, obj):
        return None

    def get_url(self, obj):
        return obj.get_absolute_url()

    def get_title(self, obj):
        return None

    def get_description(self, obj):
        return None

    def get_default_language(self, using):
        """
        When using multiple languages, this allows us to specify a fallback based on the
        backend being used.
        """
        func = settings.ALDRYN_SEARCH_LANGUAGE_FROM_ALIAS

        if using and not using == DEFAULT_ALIAS and func:
            return func(using)
        else:
            return get_current_language() or settings.LANGUAGE_CODE

    def get_index_kwargs(self, language):
        """
        This is called to filter the index queryset.
        """
        return {}

    def get_model(self):
        raise NotImplementedError()

    def get_search_data(self, obj, language, request):
        raise NotImplementedError()
