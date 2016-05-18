# -*- coding: utf-8 -*-
from django.contrib.auth.models import AnonymousUser
from django.template import RequestContext
from django.test import RequestFactory
from django.utils.text import smart_split
try:
    from django.utils.encoding import force_unicode
except ImportError:
    from django.utils.encoding import force_text as force_unicode

from cms.toolbar.toolbar import CMSToolbar

from aldryn_common.compat import DJANGO_1_7

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
        context = RequestContext(request)

        if not DJANGO_1_7:
            from django.template import Engine
            # On Django <= 1.7, the RequestContext class would call
            # all context processors and update the context on initialization.
            # On Django >= 1.8 the logic to update the context
            # from context processors is now tied to the bind_template
            # context manager.
            updates = {}
            engine = Engine.get_default()

            for processor in engine.template_context_processors:
                updates.update(processor(context.request))
            context.dicts[context._processors_index] = updates

        plugin_contents = instance.render_plugin(context=context)

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
    request.toolbar = CMSToolbar(request)
    return request
