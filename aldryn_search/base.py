# -*- coding: utf-8 -*-
import warnings
from django.utils.translation import override

from haystack import indexes

from .conf import settings
from .helpers import get_request
from .utils import clean_join, _get_language_from_alias_func


language_from_alias = _get_language_from_alias_func()


class AbstractIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=False)
    
    def _get_backend(self, using):
        return self.get_backend(using)

    def get_backend(self, using):
        """
        We set the backend to allow easy access for things like document search.
        """
        if hasattr(super(AbstractIndex, self), 'get_backend'):
            self._backend = super(AbstractIndex, self).get_backend(using)
        else:
            self._backend = super(AbstractIndex, self)._get_backend(using)
            
        self._backend_alias = using
        return self._backend

    def index_queryset(self, using=None):
        self._get_backend(using)
        language = self.get_current_language(using)
        filter_kwargs = self.get_index_kwargs(language)
        qs = self.get_index_queryset(language)
        return (qs.filter(**filter_kwargs))

    def get_index_queryset(self, language):
        return self.get_model().objects.all()

    def prepare(self, obj):
        current_language = self.get_current_language(using=self._backend_alias, obj=obj)

        with override(current_language):
            request = self.get_request_instance(obj, current_language)
            self.prepared_data = super(AbstractIndex, self).prepare(obj)
            self.prepared_data['text'] = self.get_search_data(obj, current_language, request)
            self.prepare_fields(obj, current_language, request)
            return self.prepared_data

    def get_request_instance(self, obj, language):
        return get_request(language)

    def get_language(self, obj):
        """
        Equivalent to self.prepare_language.
        """
        return None

    def get_current_language(self, using=None, obj=None):
        """
        Helper method bound to ALWAYS return a language.

        When obj is not None, this calls self.get_language to try and get a
        language from obj, this is useful when the object itself defines it's
        language in a "language" field.

        If no language was found or obj is None, then we call
        self.get_default_language to try and get a fallback language.
        """
        language = self.get_language(obj) if obj else None
        return language or self.get_default_language(using)

    def get_default_language(self, using):
        """
        When using multiple languages, this allows us to specify a fallback based on the
        backend being used.
        """
        language = None

        if using and language_from_alias:
            language = language_from_alias(using)
        return language or settings.ALDRYN_SEARCH_DEFAULT_LANGUAGE

    def get_index_kwargs(self, language):
        """
        This is called to filter the index queryset.
        """
        return {}

    def get_search_data(self, obj, language, request):
        """
        Returns a string that will be used to populate the text field (primary field).
        """
        return ''

    def prepare_fields(self, obj, language, request):
        """
        This is called to prepare any extra fields.
        """
        pass


class AldrynIndexBase(AbstractIndex):
    # For some apps it makes sense to turn on the title indexing.
    index_title = False

    language = indexes.CharField()
    description = indexes.CharField(indexed=False, stored=True, null=True)
    pub_date = indexes.DateTimeField(null=True)
    login_required = indexes.BooleanField(default=False)
    url = indexes.CharField(stored=True, indexed=False)
    title = indexes.CharField(stored=True, indexed=False)
    site_id = indexes.IntegerField(stored=True, indexed=True, null=True)

    def __init__(self):
        if hasattr(self, 'INDEX_TITLE'):
            warning_message = ('AldrynIndexBase.INDEX_TITLE is deprecated; '
                               'use AldrynIndexBase.index_title instead')
            warnings.warn(warning_message, PendingDeprecationWarning)
        super(AldrynIndexBase, self).__init__()

    def get_url(self, obj):
        """
        Equivalent to self.prepare_url.
        """
        return obj.get_absolute_url()

    def get_title(self, obj):
        """
        Equivalent to self.prepare_title.
        """
        return None

    def get_description(self, obj):
        """
        Equivalent to self.prepare_description.
        """
        return None

    def prepare_fields(self, obj, language, request):
        self.prepared_data['language'] = language
        # We set the following fields here because on some models,
        # the value of these fields is dependent on the active language
        # this being the case we extrapolate the language hacks.
        self.prepared_data['url'] = self.get_url(obj)
        self.prepared_data['title'] = self.get_title(obj)
        self.prepared_data['description'] = self.get_description(obj)

        if self.index_title or getattr(self, 'INDEX_TITLE', False):
            prepared_text = self.prepared_data['text']
            prepared_title = self.prepared_data['title']
            self.prepared_data['text'] = clean_join(
                ' ', [prepared_title, prepared_text]
            )
