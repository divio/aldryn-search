# -*- coding: utf-8 -*-
from django.template import RequestContext
from django.utils.encoding import force_unicode

from .utils import strip_tags


def get_plugin_index_data(self, base_plugin, request):
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
