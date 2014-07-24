from django.db.models import Q
from django.utils import timezone

from cms.models import CMSPlugin, Title

from .conf import settings
from .helpers import get_plugin_index_data
from .utils import clean_join, get_index_base, strip_tags


# Backwards compatibility
_strip_tags = strip_tags


class TitleIndex(get_index_base()):
    index_title = True

    haystack_use_for_indexing = settings.ALDRYN_SEARCH_CMS_PAGE

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

    def get_plugin_queryset(self, language):
        queryset = CMSPlugin.objects.filter(language=language)
        return queryset

    def get_search_data(self, obj, language, request):
        current_page = obj.page
        placeholders = current_page.placeholders.all()
        plugins = self.get_plugin_queryset(language).filter(placeholder__in=placeholders)
        text_bits = []

        for base_plugin in plugins:
            plugin_text_content = self.get_plugin_search_text(base_plugin, request)
            text_bits.append(plugin_text_content)

        page_meta_description = current_page.get_meta_description(fallback=False, language=language)

        if page_meta_description:
            text_bits.append(page_meta_description)

        page_meta_keywords = getattr(current_page, 'get_meta_keywords', None)

        if page_meta_keywords:
            text_bits.append(page_meta_keywords)

        return clean_join(' ', text_bits)

    def get_plugin_search_text(self, base_plugin, request):
        plugin_content_bits = get_plugin_index_data(base_plugin, request)
        return clean_join(' ', plugin_content_bits)

    def get_model(self):
        return Title

    def get_index_queryset(self, language):
        queryset = Title.objects.public().filter(
            Q(page__publication_date__lt=timezone.now()) | Q(page__publication_date__isnull=True),
            Q(page__publication_end_date__gte=timezone.now()) | Q(page__publication_end_date__isnull=True),
            Q(redirect__exact='') | Q(redirect__isnull=True),
            language=language
        ).select_related('page').distinct()
        return queryset
