# -*- coding: utf-8 -*-
from django.contrib.auth.models import AnonymousUser
from django.template import RequestContext
from django.test import RequestFactory
from django.utils.encoding import force_unicode

from .conf import settings
from .utils import strip_tags


def get_plugin_index_data(base_plugin, request):
    text_bits = []
    instance, plugin_type = base_plugin.get_plugin_instance()

    if instance is None:
        # this is an empty plugin
        return ''

    search_contents = getattr(instance, 'search_fulltext', True) or getattr(plugin_type, 'search_fulltext', True)

    for field in getattr(instance, 'search_fields', []):
        field_content = strip_tags(getattr(instance, field, ''))

        if field_content:
            field_content = force_unicode(field_content)
            text_bits.extend(field_content.split())

    if search_contents:
        plugin_contents = instance.render_plugin(context=RequestContext(request))

        if plugin_contents:
            plugin_contents = strip_tags(plugin_contents)
            text_bits.extend(plugin_contents.split())

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
