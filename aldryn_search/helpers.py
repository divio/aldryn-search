# -*- coding: utf-8 -*-
import django
from cms.plugin_rendering import PluginContext
from django.contrib.auth.models import AnonymousUser
from django.template import RequestContext
from django.test import RequestFactory
from django.utils.text import smart_split
try:
    from django.utils.encoding import force_unicode
except ImportError:
    from django.utils.encoding import force_text as force_unicode

from .conf import settings
from .utils import get_field_value, strip_tags


def get_cleaned_bits(data):
    decoded = force_unicode(data)
    stripped = strip_tags(decoded)
    return smart_split(stripped)


def get_plugin_index_data(base_plugin, request):
    text_bits = []

    instance, plugin_type = base_plugin.get_plugin_instance()

    if instance is None:
        # this is an empty plugin
        return text_bits

    search_fields = getattr(instance, 'search_fields', [])

    if hasattr(instance, 'search_fulltext'):
        # check if the plugin instance has search enabled
        search_contents = instance.search_fulltext
    elif hasattr(base_plugin, 'search_fulltext'):
        # now check in the base plugin instance (CMSPlugin)
        search_contents = base_plugin.search_fulltext
    elif hasattr(plugin_type, 'search_fulltext'):
        # last check in the plugin class (CMSPluginBase)
        search_contents = plugin_type.search_fulltext
    else:
        # disabled if there's search fields defined,
        # otherwise it's enabled.
        search_contents = not bool(search_fields)

    if search_contents:
        if django.get_version() < '1.8':
            plugin_context = RequestContext(request)
        else:
            plugin_context = PluginContext({'request': request}, instance, instance.placeholder)
        plugin_contents = instance.render_plugin(context=plugin_context)

        if plugin_contents:
            text_bits = get_cleaned_bits(plugin_contents)
    else:
        values = (get_field_value(instance, field) for field in search_fields)

        for value in values:
            cleaned_bits = get_cleaned_bits(value or '')
            text_bits.extend(cleaned_bits)
    return text_bits


def get_request(language=None):
    """
    Returns a Request instance populated with cms specific attributes.
    """
    request_factory = RequestFactory(HTTP_HOST=settings.ALLOWED_HOSTS[0])
    request = request_factory.get("/")
    request.session = {}
    request.LANGUAGE_CODE = language or settings.LANGUAGE_CODE
    # Needed for plugin rendering.
    request.current_page = None
    request.user = AnonymousUser()
    return request
