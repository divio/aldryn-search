# -*- coding: utf-8 -*-
from django.contrib.auth.models import AnonymousUser
from django.template import RequestContext
from django.test import RequestFactory
from django.utils.encoding import force_unicode

from .conf import settings
from .utils import strip_tags


def get_plugin_index_data(base_plugin, request):
    text = u''
    instance, plugin_type = base_plugin.get_plugin_instance()
    if instance is None:
        # this is an empty plugin
        return text
    if hasattr(instance, 'search_fields'):
        text += u' '.join(force_unicode(strip_tags(getattr(instance, field, ''))) for field in instance.search_fields)
    if getattr(instance, 'search_fulltext', True) and getattr(plugin_type, 'search_fulltext', True):
        text += strip_tags(instance.render_plugin(context=RequestContext(request))) + u' '
    return text


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
