from distutils.version import LooseVersion
import re

from django.core.exceptions import ImproperlyConfigured
from django.contrib.sites.models import Site
from django.db.models import Q
from django.db.models.query import EmptyQuerySet
from django.template import RequestContext
from django.test.client import RequestFactory
from django.utils import importlib
from django.utils.encoding import force_unicode
from django.utils.translation import override
from django.utils import timezone

import cms
from cms.models.pluginmodel import CMSPlugin

from haystack import indexes

from .models import TitleProxy
from .conf import settings

def _strip_tags(value):
    """
    Returns the given HTML with all tags stripped.

    This is a copy of django.utils.html.strip_tags, except that it adds some
    whitespace in between replaced tags to make sure words are not erroneously
    concatenated.
    """
    return re.sub(r'<[^>]*?>', ' ', force_unicode(value))


def _get_index_base():
    index_string = settings.DJANGOCMS_SEARCH_INDEX_BASE_CLASS
    module, class_name = index_string.rsplit('.', 1)
    mod = importlib.import_module(module)
    base_class = getattr(mod, class_name, None)
    if not base_class:
        raise ImproperlyConfigured('DJANGOCMS_SEARCH_INDEX_BASE_CLASS: module %s has no class %s' % (module, class_name))
    if not issubclass(base_class, indexes.SearchIndex):
        raise ImproperlyConfigured('DJANGOCMS_SEARCH_INDEX_BASE_CLASS: %s is not a subclass of haystack.indexes.SearchIndex' % index_string)
    required_fields = ['text', 'language']
    if not all(field in base_class.fields for field in required_fields):
        raise ImproperlyConfigured('DJANGOCMS_SEARCH_INDEX_BASE_CLASS: %s must contain at least these fields: %s' % (index_string, required_fields))
    return base_class

rf = RequestFactory()


class TitleIndex(_get_index_base(), indexes.Indexable):

    def prepare_url(self, obj):
        with override(obj.language):
            return obj.page.get_absolute_url()

    def prepare(self, obj):
        current_language = obj.language
        with override(current_language):
            request = rf.get("/")
            request.session = {}
            request.LANGUAGE_CODE = current_language
            self.prepared_data = super(TitleIndex, self).prepare(obj)
            plugins = CMSPlugin.objects.filter(language=current_language, placeholder__in=obj.page.placeholders.all())
            text = u''
            for base_plugin in plugins:
                instance, plugin_type = base_plugin.get_plugin_instance()
                if instance is None:
                    # this is an empty plugin
                    continue
                if hasattr(instance, 'search_fields'):
                    text += u' '.join(force_unicode(_strip_tags(getattr(instance, field, ''))) for field in instance.search_fields)
                if getattr(instance, 'search_fulltext', False) or getattr(plugin_type, 'search_fulltext', False):
                    text += _strip_tags(instance.render_plugin(context=RequestContext(request))) + u' '
            text += obj.page.get_meta_description() or u''
            text += u' '
            text += obj.page.get_meta_keywords() if hasattr(obj.page, 'get_meta_keywords') else u''
            self.prepared_data['text'] = text
            self.prepared_data['language'] = current_language
            return self.prepared_data

    def get_model(self):
        return TitleProxy

    def index_queryset(self, using=None):
        # get the correct language and exclude pages that have a redirect
        base_qs = super(TitleIndex, self).index_queryset().select_related('page')
        result_qs = EmptyQuerySet()
        for site_obj in Site.objects.all():
            qs = base_qs.filter(page__site=site_obj.id).filter(
                Q(page__publication_date__lt=timezone.now()) | Q(page__publication_date__isnull=True),
                Q(page__publication_end_date__gte=timezone.now()) | Q(page__publication_end_date__isnull=True),
                page__published=True,
            ).filter(
                Q(language=using) & (Q(redirect__exact='') | Q(redirect__isnull=True))
            )
            if 'publisher' in settings.INSTALLED_APPS or LooseVersion(cms.__version__) >= LooseVersion('2.4'):
                qs = qs.filter(page__publisher_is_draft=False)
            qs = qs.distinct()
            result_qs |= qs
        return result_qs
