from django.template import Template
from django.test import TestCase
from django.test.utils import override_settings

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.models.placeholdermodel import Placeholder
from cms.models import CMSPlugin

from aldryn_search.search_indexes import TitleIndex
from .helpers import get_plugin_index_data, get_request


test_settings = {
    'ALLOWED_HOSTS': ['localhost'],
    'CMS_LANGUAGES': {1: [{'code': 'en', 'name': 'English'}]},
    'CMS_TEMPLATES': (("whee.html", "Whee Template"),),
    'LANGUAGES': (('en', 'English'),),
    'LANGUAGE_CODE': 'en',
    'TEMPLATE_LOADERS': ('aldryn_search.tests.FakeTemplateLoader',),
}


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
    render_template = Template(plugin_content)

    def render(self, context, instance, placeholder):
        return context

plugin_pool.register_plugin(NotIndexedPlugin)


@override_settings(**test_settings)
class PluginIndexingTests(TestCase):

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
        instance.pk = 1234 # otherwise plugin_meta_context_processor() crashes
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
        from cms.api import create_page
        page = create_page(title="Whoopee", template="whee.html", language="en")

        from haystack import connections
        from haystack.constants import DEFAULT_ALIAS
        search_conn = connections[DEFAULT_ALIAS]
        unified_index = search_conn.get_unified_index()

        from cms.models import Title
        index = unified_index.get_index(Title)

        title = Title.objects.get(pk=page.title_set.all()[0].pk)
        index.index_queryset(DEFAULT_ALIAS) # initialises index._backend_alias
        indexed = index.prepare(title)
        self.assertEqual('Whoopee', indexed['title'])
        self.assertEqual('Whoopee', indexed['text'])

    def test_page_title_is_indexed_using_update_object(self):
        """This tests the indexing path way used by the RealTimeSignalProcessor"""
        from cms.api import create_page
        page = create_page(title="Whoopee", template="whee.html", language="en")

        from haystack import connections
        from haystack.constants import DEFAULT_ALIAS
        search_conn = connections[DEFAULT_ALIAS]
        unified_index = search_conn.get_unified_index()

        from cms.models import Title
        index = unified_index.get_index(Title)

        title = Title.objects.get(pk=page.title_set.all()[0].pk)
        index.update_object(title, using=DEFAULT_ALIAS)
        indexed = index.prepared_data
        self.assertEqual('Whoopee', indexed['title'])
        self.assertEqual('Whoopee', indexed['text'])
