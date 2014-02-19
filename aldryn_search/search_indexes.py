from distutils.version import LooseVersion

from django.contrib.sites.models import Site
from django.db.models import Q
from django.db.models.query import EmptyQuerySet
from django.template import RequestContext
from django.utils.encoding import force_unicode
from django.utils import timezone

import cms
from cms.models.pluginmodel import CMSPlugin

from haystack import indexes

from .models import TitleProxy
from .conf import settings
from .utils import _get_index_base, strip_tags


# Backwards compatibility
_strip_tags = strip_tags


class TitleIndex(_get_index_base()):
    INDEX_TITLE = True

    haystack_use_for_indexing = getattr(settings, "ALDRYN_SEARCH_CMS_PAGE", True)

    def prepare_pub_date(self, obj):
        return obj.page.publication_date

    def prepare_login_required(self, obj):
        return obj.page.login_required

    def prepare_site_id(self, obj):
        return obj.page.site_id

    def get_language(self, obj):
        return obj.language

    def get_url(self, obj):
        return obj.page.get_absolute_url()

    def get_title(self, obj):
        return obj.title

    def get_description(self, obj):
        return obj.meta_description or None

    def get_search_data(self, obj, language, request):
        current_page = obj.page
        plugins = CMSPlugin.objects.filter(language=language, placeholder__in=current_page.placeholders.all())
        text = u''
        for base_plugin in plugins:
            text += self.get_plugin_search_text(base_plugin, request)
        text += current_page.get_meta_description() or u''
        text += u' '
        text += current_page.get_meta_keywords() if hasattr(current_page, 'get_meta_keywords') and current_page.get_meta_keywords() else u''
        return text

    def get_plugin_search_text(self, base_plugin, request):
        text = u''
        instance, plugin_type = base_plugin.get_plugin_instance()
        if instance is None:
            # this is an empty plugin
            return text
        if hasattr(instance, 'search_fields'):
            text += u' '.join(force_unicode(strip_tags(getattr(instance, field, ''))) for field in instance.search_fields)
        if getattr(instance, 'search_fulltext', True) and \
                getattr(plugin_type, 'search_fulltext', True):
            text += strip_tags(instance.render_plugin(context=RequestContext(request))) + u' '
        return text

    def get_model(self):
        return TitleProxy

    def get_index_queryset(self, language):
        # get the correct language and exclude pages that have a redirect
        base_qs = super(TitleIndex, self).get_index_queryset(language).select_related('page')
        result_qs = None
        for site_obj in Site.objects.all():
            qs = base_qs.filter(page__site=site_obj.id).filter(
                Q(page__publication_date__lt=timezone.now()) | Q(page__publication_date__isnull=True),
                Q(page__publication_end_date__gte=timezone.now()) | Q(page__publication_end_date__isnull=True),
                page__published=True,
            ).filter(
                Q(language=language) & (Q(redirect__exact='') | Q(redirect__isnull=True))
            )
            if 'publisher' in settings.INSTALLED_APPS or LooseVersion(cms.__version__) >= LooseVersion('2.4'):
                qs = qs.filter(page__publisher_is_draft=False)
            qs = qs.distinct()
            if result_qs is None:
                result_qs = qs
            else:
                result_qs |= qs
        return result_qs
