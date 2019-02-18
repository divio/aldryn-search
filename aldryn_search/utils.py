# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import importlib
import re

from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.encoding import force_text

from cms.utils.i18n import get_language_code

import six
from haystack import DEFAULT_ALIAS
from haystack.indexes import SearchIndex
from lxml.etree import ParseError, ParserError
from lxml.html.clean import Cleaner as LxmlCleaner

from .conf import settings


def _get_alias_from_language_func():
    path_or_callable = settings.ALDRYN_SEARCH_ALIAS_FROM_LANGUAGE

    if path_or_callable:
        try:
            func = get_callable(path_or_callable)
        except AttributeError as error:
            raise ImproperlyConfigured('ALDRYN_SEARCH_ALIAS_FROM_LANGUAGE: %s' % (str(error)))
        if not callable(func):
            raise ImproperlyConfigured('ALDRYN_SEARCH_ALIAS_FROM_LANGUAGE: %s is not callable' % func)
    else:
        func = alias_from_language
    return func


def _get_language_from_alias_func():
    path_or_callable = settings.ALDRYN_SEARCH_LANGUAGE_FROM_ALIAS

    if path_or_callable:
        try:
            func = get_callable(path_or_callable)
        except AttributeError as error:
            raise ImproperlyConfigured('ALDRYN_SEARCH_LANGUAGE_FROM_ALIAS: %s' % (str(error)))
        if not callable(func):
            raise ImproperlyConfigured('ALDRYN_SEARCH_LANGUAGE_FROM_ALIAS: %s is not callable' % func)
    else:
        func = language_from_alias
    return func


def alias_from_language(language):
    """
    Returns alias if alias is a valid language.
    """
    language = get_language_code(language)

    if language == settings.ALDRYN_SEARCH_DEFAULT_LANGUAGE:
        return DEFAULT_ALIAS
    return language


def clean_join(separator, iterable):
    """
    Filters out iterable to only join non empty items.
    """
    return separator.join(filter(None, iterable))


def get_callable(string_or_callable):
    """
    If given a callable then it returns it, otherwise it resolves the path
    and returns an object.
    """
    if callable(string_or_callable):
        return string_or_callable
    else:
        module_name, object_name = string_or_callable.rsplit('.', 1)
        module = importlib.import_module(module_name)
        return getattr(module, object_name)


def get_index_base():
    index_string = settings.ALDRYN_SEARCH_INDEX_BASE_CLASS
    try:
        BaseClass = get_callable(index_string)
    except AttributeError as error:
        raise ImproperlyConfigured('ALDRYN_SEARCH_INDEX_BASE_CLASS: %s' % (str(error)))

    if not issubclass(BaseClass, SearchIndex):
        exception_message = ('ALDRYN_SEARCH_INDEX_BASE_CLASS: %s is not a '
                             'subclass of haystack.indexes.SearchIndex')
        raise ImproperlyConfigured(exception_message % index_string)

    required_fields = ['text', 'language']

    if not all(field in BaseClass.fields for field in required_fields):
        exception_message = ('ALDRYN_SEARCH_INDEX_BASE_CLASS: %s must contain '
                             'at least these fields: %s')
        raise ImproperlyConfigured(exception_message % (index_string,
                                                        required_fields))
    return BaseClass


def language_from_alias(alias):
    """
    Returns alias if alias is a valid language.
    """
    languages = [language[0] for language in settings.LANGUAGES]

    return alias if alias in languages else None


def get_field_value(obj, name):
    """
    Given a model instance and a field name (or attribute),
    returns the value of the field or an empty string.
    """
    fields = name.split('__')

    name = fields[0]

    try:
        obj._meta.get_field(name)
    except (AttributeError, models.FieldDoesNotExist):
        # we catch attribute error because obj will not always be a model
        # specially when going through multiple relationships.
        value = getattr(obj, name, None) or ''
    else:
        value = getattr(obj, name)

    if len(fields) > 1:
        remaining = '__'.join(fields[1:])
        return get_field_value(value, remaining)
    return value


def get_model_path(model_or_string):
    if not isinstance(model_or_string, six.string_types):
        # it's a model class
        app_label = model_or_string._meta.app_label
        model_name = model_or_string._meta.object_name
        model_or_string = '{0}.{1}'.format(app_label, model_name)
    return model_or_string.lower()


def _strip_tags(value):
    """
    Returns the given HTML with all tags stripped.
    This is a copy of django.utils.html.strip_tags, except that it adds some
    whitespace in between replaced tags to make sure words are not erroneously
    concatenated.
    """
    return re.sub(r'<[^>]*?>', ' ', force_text(value))


def strip_tags(value):
    """
    Returns the given HTML with all tags stripped.
    We use lxml to strip all js tags and then hand the result to django's
    strip tags. If value isn't valid, just return value since there is
    no tags to strip.
    """
    if isinstance(value, six.string_types):
        value = value.strip()

        try:
            partial_strip = LxmlCleaner().clean_html(value)
        except (ParseError, ParserError):
            # Error could occur because of invalid html document,
            # including '' values. We don't want to return empty handed.
            partial_strip = value
        value = _strip_tags(partial_strip)
        return value.strip()  # clean cases we have <div>\n\n</div>
    return value
