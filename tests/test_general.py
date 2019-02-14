from cms.api import create_page, add_plugin
from cms.models import CMSPlugin, Title
from cms.models.placeholdermodel import Placeholder
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.template import engines
from django.test import TestCase
from haystack import connections
from haystack.constants import DEFAULT_ALIAS
from haystack.query import SearchQuerySet

from aldryn_search.search_indexes import TitleIndex

from aldryn_search.helpers import get_request


def template_from_string(value):
    """Create an engine-specific template based on provided string.
    """
    return engines.all()[0].from_string(value)


class FakeTemplateLoader(object):
    is_usable = True

    def __init__(self, name, dirs):
        pass

    def __iter__(self):
        yield self.__class__
        yield "{{baz}}"


class NotIndexedPlugin(CMSPluginBase):
    model = CMSPlugin
    plugin_content = 'rendered plugin content'
    render_template = template_from_string(plugin_content)

    def render(self, context, instance, placeholder):
        return context

plugin_pool.register_plugin(NotIndexedPlugin)


class HiddenPlugin(CMSPluginBase):
    model = CMSPlugin
    plugin_content = 'never search for this content'
    render_template = template_from_string(plugin_content)

    def render(self, context, instance, placeholder):
        return context

plugin_pool.register_plugin(HiddenPlugin)


class BaseTestCase(TestCase):
    def setUp(self):
        pass

    def get_title_index(self):
        search_conn = connections[DEFAULT_ALIAS]
        unified_index = search_conn.get_unified_index()
        index = unified_index.get_index(Title)
        return index


class PluginIndexingTests(BaseTestCase):

    def setUp(self):
        self.index = TitleIndex()
        self.request = get_request(language='en')

    def get_plugin(self):
        instance = CMSPlugin(
            language='en',
            plugin_type="NotIndexedPlugin",
            placeholder=Placeholder(id=1235)
        )
        instance.cmsplugin_ptr = instance
        instance.pk = 1234  # otherwise plugin_meta_context_processor() crashes
        return instance

    def test_plugin_indexing_is_enabled_by_default(self):
        cms_plugin = self.get_plugin()
        indexed_content = self.index.get_plugin_search_text(cms_plugin, self.request)
        self.assertEqual(NotIndexedPlugin.plugin_content, indexed_content)

    def test_plugin_indexing_can_be_disabled_on_model(self):
        cms_plugin = self.get_plugin()
        cms_plugin.search_fulltext = False
        indexed_content = self.index.get_plugin_search_text(cms_plugin, self.request)
        self.assertEqual('', indexed_content)

    def test_plugin_indexing_can_be_disabled_on_plugin(self):
        NotIndexedPlugin.search_fulltext = False

        try:
            self.assertEqual('', self.index.get_plugin_search_text(self.get_plugin(), self.request))
        finally:
            del NotIndexedPlugin.search_fulltext

    def test_page_title_is_indexed_using_prepare(self):
        """This tests the indexing path way used by update_index mgmt command"""
        page = create_page(title="home", template="page.html", language="en")
        index = self.get_title_index()

        title = Title.objects.get(pk=page.title_set.all()[0].pk)
        index.index_queryset(DEFAULT_ALIAS)  # initialises index._backend_alias
        indexed = index.prepare(title)
        self.assertEqual('home', indexed['title'])
        self.assertEqual('home', indexed['text'])

    def test_page_title_is_indexed_using_update_object(self):
        """This tests the indexing path way used by the RealTimeSignalProcessor"""
        page = create_page(title="home", template="page.html", language="en")
        index = self.get_title_index()
        title = Title.objects.get(pk=page.title_set.all()[0].pk)
        index.update_object(title, using=DEFAULT_ALIAS)
        indexed = index.prepared_data
        self.assertEqual('home', indexed['title'])
        self.assertEqual('home', indexed['text'])


class PluginFilterIndexingTests(BaseTestCase):

    def test_page_title_is_indexed_using_prepare_with_filter_option(self):
        """This tests the indexing path way used by update_index mgmt command"""
        page = create_page(title="test_page", reverse_id='testpage', template="test.html", language="en")
        plugin = add_plugin(page.placeholders.get(slot='content'), NotIndexedPlugin, 'en')
        plugin2 = add_plugin(page.placeholders.get(slot='hidden_content'), HiddenPlugin, 'en')
        index = self.get_title_index()
        title = Title.objects.get(pk=page.title_set.all()[0].pk)
        index.index_queryset(DEFAULT_ALIAS)  # initialises index._backend_alias
        indexed = index.prepare(title)
        self.assertEqual('test_page', indexed['title'])
        self.assertEqual('test_page rendered plugin content', indexed['text'])

    def test_page_title_is_indexed_using_update_object_with_filter_option(self):
        """This tests the indexing path way used by the RealTimeSignalProcessor"""
        page = create_page(title="test_page", reverse_id='testpage', template="test.html", language="en")
        plugin = add_plugin(page.placeholders.get(slot='content'), NotIndexedPlugin, 'en')
        plugin2 = add_plugin(page.placeholders.get(slot='hidden_content'), HiddenPlugin, 'en')
        index = self.get_title_index()
        title = Title.objects.get(pk=page.title_set.all()[0].pk)
        index.update_object(title, using=DEFAULT_ALIAS)
        indexed = index.prepared_data
        self.assertEqual('test_page', indexed['title'])
        self.assertEqual('test_page rendered plugin content', indexed['text'])


class PluginExcludeAndFilterIndexingTests2(BaseTestCase):

    def test_page_title_is_indexed_using_prepare_with_excluding_filter_option2(self):
        """This tests the indexing path way used by update_index mgmt command"""
        page = create_page(title="test_page2", reverse_id='testpage2', template="test.html", language="en")
        plugin = add_plugin(page.placeholders.get(slot='content'), NotIndexedPlugin, 'en')
        plugin2 = add_plugin(page.placeholders.get(slot='hidden_content'), HiddenPlugin, 'en')
        index = self.get_title_index()
        title = Title.objects.get(pk=page.title_set.all()[0].pk)
        index.index_queryset(DEFAULT_ALIAS)  # initialises index._backend_alias
        indexed = index.prepare(title)
        self.assertEqual('test_page2', indexed['title'])
        self.assertEqual('test_page2 rendered plugin content never search for this content', indexed['text'])

    def test_page_title_is_indexed_using_update_object_with_excluding_filter_option2(self):
        """This tests the indexing path way used by the RealTimeSignalProcessor"""
        page = create_page(title="test_page2", reverse_id='testpage2', template="test.html", language="en")
        plugin = add_plugin(page.placeholders.get(slot='content'), NotIndexedPlugin, 'en')
        plugin2 = add_plugin(page.placeholders.get(slot='hidden_content'), HiddenPlugin, 'en')
        index = self.get_title_index()
        title = Title.objects.get(pk=page.title_set.all()[0].pk)
        index.update_object(title, using=DEFAULT_ALIAS)
        indexed = index.prepared_data
        self.assertEqual('test_page2', indexed['title'])
        self.assertEqual('test_page2 rendered plugin content never search for this content', indexed['text'])


class PluginExcludeAndFilterIndexingTests3(BaseTestCase):

    def test_page_title_is_indexed_using_prepare_with_excluding_filter_option3(self):
        """This tests the indexing path way used by update_index mgmt command"""
        page = create_page(title="test_page3", reverse_id='testpage3', template="test.html", language="en")
        plugin = add_plugin(page.placeholders.get(slot='content'), NotIndexedPlugin, 'en')
        plugin2 = add_plugin(page.placeholders.get(slot='hidden_content'), HiddenPlugin, 'en')
        index = self.get_title_index()
        title = Title.objects.get(pk=page.title_set.all()[0].pk)
        index.index_queryset(DEFAULT_ALIAS)  # initialises index._backend_alias
        indexed = index.prepare(title)
        self.assertEqual('test_page3', indexed['title'])
        self.assertEqual('test_page3', indexed['text'])

    def test_page_title_is_indexed_using_update_object_with_excluding_filter_option3(self):
        """This tests the indexing path way used by the RealTimeSignalProcessor"""
        page = create_page(title="test_page3", reverse_id='testpage3', template="test.html", language="en")
        plugin = add_plugin(page.placeholders.get(slot='content'), NotIndexedPlugin, 'en')
        plugin2 = add_plugin(page.placeholders.get(slot='hidden_content'), HiddenPlugin, 'en')
        index = self.get_title_index()
        title = Title.objects.get(pk=page.title_set.all()[0].pk)
        index.update_object(title, using=DEFAULT_ALIAS)
        indexed = index.prepared_data
        self.assertEqual('test_page3', indexed['title'])
        self.assertEqual('test_page3', indexed['text'])


class PluginExcludeAndFilterIndexingTests4(BaseTestCase):

    def test_page_title_is_indexed_using_prepare_with_excluding_filter_option4(self):
        """This tests the indexing path way used by update_index mgmt command"""
        page = create_page(title="test_page4", reverse_id='testpage4', template="test.html", language="en")
        plugin = add_plugin(page.placeholders.get(slot='content'), NotIndexedPlugin, 'en')
        plugin2 = add_plugin(page.placeholders.get(slot='hidden_content'), HiddenPlugin, 'en')
        index = self.get_title_index()
        title = Title.objects.get(pk=page.title_set.all()[0].pk)
        index.index_queryset(DEFAULT_ALIAS)  # initialises index._backend_alias
        indexed = index.prepare(title)
        self.assertEqual('test_page4', indexed['title'])
        self.assertEqual('test_page4 rendered plugin content', indexed['text'])

    def test_page_title_is_indexed_using_update_object_with_excluding_filter_option4(self):
        """This tests the indexing path way used by the RealTimeSignalProcessor"""
        page = create_page(title="test_page4", reverse_id='testpage4', template="test.html", language="en")
        plugin = add_plugin(page.placeholders.get(slot='content'), NotIndexedPlugin, 'en')
        plugin2 = add_plugin(page.placeholders.get(slot='hidden_content'), HiddenPlugin, 'en')
        index = self.get_title_index()
        title = Title.objects.get(pk=page.title_set.all()[0].pk)
        index.update_object(title, using=DEFAULT_ALIAS)
        indexed = index.prepared_data
        self.assertEqual('test_page4', indexed['title'])
        self.assertEqual('test_page4 rendered plugin content', indexed['text'])


class PluginExcludeAndFilterIndexingTests5(BaseTestCase):

    def test_page_title_is_indexed_using_prepare_with_excluding_filter_option5(self):
        """This tests the indexing path way used by update_index mgmt command"""
        page = create_page(title="test_page5", reverse_id='testpage5', template="test.html", language="en")
        plugin = add_plugin(page.placeholders.get(slot='content'), NotIndexedPlugin, 'en')
        plugin2 = add_plugin(page.placeholders.get(slot='hidden_content'), HiddenPlugin, 'en')
        index = self.get_title_index()
        title = Title.objects.get(pk=page.title_set.all()[0].pk)
        index.index_queryset(DEFAULT_ALIAS)  # initialises index._backend_alias
        indexed = index.prepare(title)
        self.assertEqual('test_page5', indexed['title'])
        self.assertEqual('test_page5 never search for this content', indexed['text'])

    def test_page_title_is_indexed_using_update_object_with_excluding_filter_option5(self):
        """This tests the indexing path way used by the RealTimeSignalProcessor"""
        page = create_page(title="test_page5", reverse_id='testpage5', template="test.html", language="en")
        plugin = add_plugin(page.placeholders.get(slot='content'), NotIndexedPlugin, 'en')
        plugin2 = add_plugin(page.placeholders.get(slot='hidden_content'), HiddenPlugin, 'en')
        index = self.get_title_index()
        title = Title.objects.get(pk=page.title_set.all()[0].pk)
        index.update_object(title, using=DEFAULT_ALIAS)
        indexed = index.prepared_data
        self.assertEqual('test_page5', indexed['title'])
        self.assertEqual('test_page5 never search for this content', indexed['text'])


class PluginExcludeAndFilterIndexingTests6(BaseTestCase):

    def test_page_title_is_indexed_using_prepare_with_excluding_filter_option6(self):
        """This tests the indexing path way used by update_index mgmt command"""
        page = create_page(title="test_page6", reverse_id='testpage6', template="test.html", language="en")
        plugin = add_plugin(page.placeholders.get(slot='content'), NotIndexedPlugin, 'en')
        plugin2 = add_plugin(page.placeholders.get(slot='hidden_content'), HiddenPlugin, 'en')
        index = self.get_title_index()
        title = Title.objects.get(pk=page.title_set.all()[0].pk)
        index.index_queryset(DEFAULT_ALIAS)  # initialises index._backend_alias
        indexed = index.prepare(title)
        self.assertEqual('test_page6', indexed['title'])
        self.assertEqual('test_page6 rendered plugin content never search for this content', indexed['text'])

    def test_page_title_is_indexed_using_update_object_with_excluding_filter_option6(self):
        """This tests the indexing path way used by the RealTimeSignalProcessor"""
        page = create_page(title="test_page6", reverse_id='testpage6', template="test.html", language="en")
        plugin = add_plugin(page.placeholders.get(slot='content'), NotIndexedPlugin, 'en')
        plugin2 = add_plugin(page.placeholders.get(slot='hidden_content'), HiddenPlugin, 'en')
        index = self.get_title_index()
        title = Title.objects.get(pk=page.title_set.all()[0].pk)
        index.update_object(title, using=DEFAULT_ALIAS)
        indexed = index.prepared_data
        self.assertEqual('test_page6', indexed['title'])
        self.assertEqual('test_page6 rendered plugin content never search for this content', indexed['text'])


class PluginExcludeAndFilterIndexingTests7(BaseTestCase):

    def test_page_title_is_indexed_using_prepare_with_excluding_filter_option7(self):
        """This tests the indexing path way used by update_index mgmt command"""
        page = create_page(title="test_page7", reverse_id='testpage7', template="test.html", language="en")
        plugin = add_plugin(page.placeholders.get(slot='content'), NotIndexedPlugin, 'en')
        plugin2 = add_plugin(page.placeholders.get(slot='hidden_content'), HiddenPlugin, 'en')
        index = self.get_title_index()
        title = Title.objects.get(pk=page.title_set.all()[0].pk)
        index.index_queryset(DEFAULT_ALIAS)  # initialises index._backend_alias
        indexed = index.prepare(title)
        self.assertEqual('test_page7', indexed['title'])
        self.assertEqual('test_page7 never search for this content', indexed['text'])

    def test_page_title_is_indexed_using_update_object_with_excluding_filter_option7(self):
        """This tests the indexing path way used by the RealTimeSignalProcessor"""
        page = create_page(title="test_page7", reverse_id='testpage7', template="test.html", language="en")
        plugin = add_plugin(page.placeholders.get(slot='content'), NotIndexedPlugin, 'en')
        plugin2 = add_plugin(page.placeholders.get(slot='hidden_content'), HiddenPlugin, 'en')
        index = self.get_title_index()
        title = Title.objects.get(pk=page.title_set.all()[0].pk)
        index.update_object(title, using=DEFAULT_ALIAS)
        indexed = index.prepared_data
        self.assertEqual('test_page7', indexed['title'])
        self.assertEqual('test_page7 never search for this content', indexed['text'])

class PluginExcludeAndFilterIndexingTests8(BaseTestCase):

    def test_page_title_is_indexed_using_prepare_with_excluding_filter_option8(self):
        """This tests the indexing path way used by update_index mgmt command"""
        page = create_page(title="test_page8", reverse_id='testpage8', template="test.html", language="en")
        plugin = add_plugin(page.placeholders.get(slot='content'), NotIndexedPlugin, 'en')
        plugin2 = add_plugin(page.placeholders.get(slot='hidden_content'), HiddenPlugin, 'en')
        index = self.get_title_index()
        title = Title.objects.get(pk=page.title_set.all()[0].pk)
        index.index_queryset(DEFAULT_ALIAS)  # initialises index._backend_alias
        indexed = index.prepare(title)
        self.assertEqual('test_page8', indexed['title'])
        self.assertEqual('test_page8 rendered plugin content never search for this content', indexed['text'])

    def test_page_title_is_indexed_using_update_object_with_excluding_filter_option8(self):
        """This tests the indexing path way used by the RealTimeSignalProcessor"""
        page = create_page(title="test_page8", reverse_id='testpage8', template="test.html", language="en")
        plugin = add_plugin(page.placeholders.get(slot='content'), NotIndexedPlugin, 'en')
        plugin2 = add_plugin(page.placeholders.get(slot='hidden_content'), HiddenPlugin, 'en')
        index = self.get_title_index()
        title = Title.objects.get(pk=page.title_set.all()[0].pk)
        index.update_object(title, using=DEFAULT_ALIAS)
        indexed = index.prepared_data
        self.assertEqual('test_page8', indexed['title'])
        self.assertEqual('test_page8 rendered plugin content never search for this content', indexed['text'])

# This test case is suitable only if you have a running solr, so if you do
# please uncomment it and ensure that aldryn-search works as expected.
# class UnpublishTest(BaseTestCase):
#
#     def test_unpublish_page(self):
#         page = create_page('test page', 'test.html', 'en', published=True)
#         title = page.publisher_public.get_title_obj('en')
#         self.assertEqual(1, SearchQuerySet().models(Title).filter(id=title.pk).count())
#         page.unpublish('en')
#         self.assertEqual(0, SearchQuerySet().models(Title).filter(id=title.pk).count())
