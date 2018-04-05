# -*- coding: utf-8 -*-
from django.db.models import Q
from django.utils import timezone

from cms.models import CMSPlugin, Title

from .compat import GTE_CMS_35
from .conf import settings
from .helpers import get_plugin_index_data
from .utils import clean_join, get_index_base, strip_tags


# Backwards compatibility
_strip_tags = strip_tags


class TitleIndex(get_index_base()):
    index_title = True

    object_actions = ('publish', 'unpublish')
    haystack_use_for_indexing = settings.ALDRYN_SEARCH_CMS_PAGE

    def prepare_pub_date(self, obj):
        return obj.page.publication_date

    def prepare_login_required(self, obj):
        return obj.page.login_required

    def prepare_site_id(self, obj):
        if not GTE_CMS_35:
            return obj.page.site_id
        return obj.page.node.site_id

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

    def get_page_placeholders(self, page):
        """
        In the project settings set up the variable

        PLACEHOLDERS_SEARCH_LIST = {
            # '*' is mandatory if you define at least one slot rule
            '*': {
                'include': [ 'slot1', 'slot2', etc. ],
                'exclude': [ 'slot3', 'slot4', etc. ],
            }
            'reverse_id_alpha': {
                'include': [ 'slot1', 'slot2', etc. ],
                'exclude': [ 'slot3', 'slot4', etc. ],
            },
            'reverse_id_beta': {
                'include': [ 'slot1', 'slot2', etc. ],
                'exclude': [ 'slot3', 'slot4', etc. ],
            },
            'reverse_id_only_include': {
                'include': [ 'slot1', 'slot2', etc. ],
            },
            'reverse_id_only_exclude': {
                'exclude': [ 'slot3', 'slot4', etc. ],
            },
            # exclude it from the placehoders search list
            # (however better to remove at all to exclude it)
            'reverse_id_empty': []
            etc.
        }

        or leave it empty

        PLACEHOLDERS_SEARCH_LIST = {}
        """
        reverse_id = page.reverse_id
        args = []
        kwargs = {}

        placeholders_by_page = getattr(settings, 'PLACEHOLDERS_SEARCH_LIST', {})

        if placeholders_by_page:
            filter_target = None
            excluded = []
            slots = []
            if '*' in placeholders_by_page:
                filter_target = '*'
            if reverse_id and reverse_id in placeholders_by_page:
                filter_target = reverse_id
            if not filter_target:
                raise AttributeError('Leave PLACEHOLDERS_SEARCH_LIST empty or set up at least the generic handling')
            if 'include' in placeholders_by_page[filter_target]:
                slots = placeholders_by_page[filter_target]['include']
            if 'exclude' in placeholders_by_page[filter_target]:
                excluded = placeholders_by_page[filter_target]['exclude']
            diff = set(slots) - set(excluded)
            if diff:
                kwargs['slot__in'] = diff
            else:
                args.append(~Q(slot__in=excluded))
        return page.placeholders.filter(*args, **kwargs)

    def get_search_data(self, obj, language, request):
        current_page = obj.page
        placeholders = self.get_page_placeholders(current_page)
        plugins = self.get_plugin_queryset(language).filter(placeholder__in=placeholders)
        text_bits = []

        for base_plugin in plugins:
            plugin_text_content = self.get_plugin_search_text(base_plugin, request)
            text_bits.append(plugin_text_content)

        page_meta_description = current_page.get_meta_description(fallback=False, language=language)

        if page_meta_description:
            text_bits.append(page_meta_description)

        page_meta_keywords = getattr(current_page, 'get_meta_keywords', None)

        if callable(page_meta_keywords):
            text_bits.append(page_meta_keywords())

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
        ).select_related('page')
        if GTE_CMS_35:
            queryset = queryset.select_related('page__node')
        return queryset.distinct()

    def should_update(self, instance, **kwargs):
        # We use the action flag to prevent
        # updating the cms page on save.
        return kwargs.get('object_action') in self.object_actions
