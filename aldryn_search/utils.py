import re

from django.utils.encoding import force_unicode
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module

from haystack.indexes import SearchIndex


def get_callable(string_or_callable):
    """
    If given a callable then it returns it, otherwise it resolves the path
    and returns an object.
    """
    if callable(string_or_callable):
        return string_or_callable
    else:
        module_name, object_name = string_or_callable.rsplit('.', 1)
        module = import_module(module_name)
        return getattr(module, object_name)


def _get_language_from_alias_func(path_or_callable):
    from .conf import settings

    if path_or_callable:
        try:
            func = get_callable(settings.ALDRYN_SEARCH_LANGUAGE_FROM_ALIAS)
        except AttributeError as error:
            raise ImproperlyConfigured('ALDRYN_SEARCH_LANGUAGE_FROM_ALIAS: %s' % (str(error)))
        if not callable(func):
            raise ImproperlyConfigured('ALDRYN_SEARCH_LANGUAGE_FROM_ALIAS: %s is not callable' % func)
    else:
        func = None
    return func


def _get_index_base():
    from .conf import settings

    index_string = settings.ALDRYN_SEARCH_INDEX_BASE_CLASS
    try:
        BaseClass = get_callable(index_string)
    except AttributeError as error:
        raise ImproperlyConfigured('ALDRYN_SEARCH_INDEX_BASE_CLASS: %s' % (str(error)))

    if not issubclass(BaseClass, SearchIndex):
        raise ImproperlyConfigured('ALDRYN_SEARCH_INDEX_BASE_CLASS: %s is not a subclass of haystack.indexes.SearchIndex' % index_string)

    required_fields = ['text', 'language']

    if not all(field in BaseClass.fields for field in required_fields):
        raise ImproperlyConfigured('ALDRYN_SEARCH_INDEX_BASE_CLASS: %s must contain at least these fields: %s' % (index_string, required_fields))
    return BaseClass


def language_from_alias(alias):
    """
    Returns alias if alias is a valid language.
    """
    from .conf import settings

    languages = [language[0] for language in settings.LANGUAGES]

    return alias if alias in languages else None


def strip_tags(value):
    """
    Returns the given HTML with all tags stripped.

    This is a copy of django.utils.html.strip_tags, except that it adds some
    whitespace in between replaced tags to make sure words are not erroneously
    concatenated.
    """
    return re.sub(r'<[^>]*?>', ' ', force_unicode(value))