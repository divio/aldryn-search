#!/usr/bin/env python
# -*- coding: utf-8 -*-

gettext = lambda s: s

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://localhost:9001/solr/default',
        'TIMEOUT': 60 * 5,
        'INCLUDE_SPELLING': True,
        'BATCH_SIZE': 100,
        'EXCLUDED_INDEXES': ['thirdpartyapp.search_indexes.BarIndex'],
    },
    'en': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://my-solr-server/solr/my-site-en/',
        'TIMEOUT': 60 * 5,
        'INCLUDE_SPELLING': True,
        'BATCH_SIZE': 100,
    },
}

HELPER_SETTINGS = {
    'TEMPLATE_DIRS': ('aldryn_search/tests_data/templates/',),
    'CMS_TEMPLATES': (
        ('fullwidth.html', 'Fullwidth'),
        ('page.html', 'Normal page'),
        ('test.html', 'Normal page2'),
    ),
    'ALLOWED_HOSTS': ['localhost'],
    'CMS_LANGUAGES': {1: [{'code': 'en', 'name': 'English'}]},
    'LANGUAGES': (('en', 'English'),),
    'LANGUAGE_CODE': 'en',
    # 'TEMPLATE_LOADERS': ('aldryn_search.tests.FakeTemplateLoader',),
    'HAYSTACK_CONNECTIONS': HAYSTACK_CONNECTIONS,
    'HAYSTACK_SIGNAL_PROCESSOR': 'aldryn_search.signal_processor.RealtimeSignalProcessor',
    'CMS_PERMISSION': True,
    'CMS_PLACEHOLDER_CONF': {
        'content': {},
    },
    'PLACEHOLDERS_SEARCH_LIST': {
        '*': {},
        'testpage': {
            'include': ['content'],
        },
        'testpage2': {},
        'testpage3': {
            'exclude': ['content', 'hidden_content']
        },
        'testpage4': {
            'include': ['content'],
            'exclude': ['hidden_content']
        },
        'testpage5': {
            'include': ['hidden_content'],
            'exclude': ['content']
        },
        'testpage6': {
            'include': ['hidden_content', 'content'],
        },
        'testpage7': {
            'include': ['hidden_content'],
        }
    },
}


def run():
    from djangocms_helper import runner
    runner.cms('aldryn_search')

if __name__ == '__main__':
    run()
