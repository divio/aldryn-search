from django.template import Template
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.models.pagemodel import Page
from cms.models.placeholdermodel import Placeholder
from cms.models import CMSPlugin
import cms.api

from aldryn_search.search_indexes import TitleIndex


class NotIndexedPluginModel(CMSPlugin):
    pass

class NotIndexedPlugin(CMSPluginBase):
    model = NotIndexedPluginModel
    render_template = Template("i am rendered: {{whee}}")
    INDEXED_MESSAGE = "This plugin should not be rendered for indexing!"

    def render(self, context, instance, placeholder):
        context['whee'] = self.INDEXED_MESSAGE
        return context

plugin_pool.register_plugin(NotIndexedPlugin)

class FakeTemplateLoader(object):
    is_usable = True
    def __init__(self, name, dirs):
        pass
    def __iter__(self):
        yield self.__class__
        yield "{{baz}}"


@override_settings(
    CMS_TEMPLATES=(("whee.html", "Whee Template"),),
    LANGUAGES=(('en', 'English'),),
    TEMPLATE_LOADERS=('aldryn_search.tests.FakeTemplateLoader',),
    HAYSTACK_SIGNAL_PROCESSOR='haystack.signals.BaseSignalProcessor',
    )
class PluginIndexingTests(TestCase):

    def setUp(self):
        self.plugin = NotIndexedPlugin()
        placeholder = Placeholder(id=1235)
        instance = NotIndexedPluginModel(plugin_type="NotIndexedPlugin",
            placeholder=placeholder)
        instance.cmsplugin_ptr = instance
        instance.pk = 1234 # otherwise plugin_meta_context_processor() crashes
        self.instance = instance
        self.index = TitleIndex()

        factory = RequestFactory()
        handler = getattr(factory, 'get')
        self.request = handler('/fake')

    def test_plugin_indexing_is_enabled_by_default(self):
        self.assertEqual("i am rendered: %s " % NotIndexedPlugin.INDEXED_MESSAGE,
            self.index.get_text_for_plugin(self.instance, self.request))

    def test_plugin_indexing_can_be_disabled_on_model(self):
        self.instance.search_fulltext = False
        self.assertEqual('', self.index.get_text_for_plugin(self.instance, self.request))

    def test_plugin_indexing_can_be_disabled_on_plugin(self):
        NotIndexedPlugin.search_fulltext = False
        try:
            self.assertEqual('', self.index.get_text_for_plugin(self.instance, self.request))
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

