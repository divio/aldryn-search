# -*- coding: utf-8 -*-
from django.contrib.auth.models import AnonymousUser
from django.template import RequestContext
from django.test import RequestFactory
from django.utils.text import smart_split
from django.utils.encoding import force_unicode

from .conf import settings
from .utils import strip_tags


def get_plugin_index_data(base_plugin, request):
    text_bits = []
    instance, plugin_type = base_plugin.get_plugin_instance()

    if instance is None:
        # this is an empty plugin
        return text_bits

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
        # enable by default
        search_contents = True

    for field in getattr(instance, 'search_fields', []):
        field_content = strip_tags(getattr(instance, field, ''))

        if field_content:
            field_content = force_unicode(field_content)
            text_bits.extend(smart_split(field_content))

    if search_contents:
        plugin_contents = instance.render_plugin(context=RequestContext(request))

        if plugin_contents:
            plugin_contents = strip_tags(plugin_contents)
            text_bits.extend(smart_split(plugin_contents))

    return  text_bits


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
