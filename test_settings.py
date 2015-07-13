#!/usr/bin/env python
# -*- coding: utf-8 -*-

gettext = lambda s: s

import os

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
    'ALLOWED_HOSTS': ['localhost'],
    'CMS_LANGUAGES': {1: [{'code': 'en', 'name': 'English'}]},
    'LANGUAGES': (('en', 'English'),),
    'LANGUAGE_CODE': 'en',
    #'TEMPLATE_LOADERS': ('aldryn_search.tests.FakeTemplateLoader',),
    'HAYSTACK_CONNECTIONS': HAYSTACK_CONNECTIONS,
    'CMS_PERMISSION': True,
    'CMS_PLACEHOLDER_CONF': {
        'content': {},
    },
    'PLACEHOLDERS_SEARCH_LIST': {
        '*': [],
        'testpage': ['content',],
        'testpage2': [],
        'testpage3': ['-content'],
    },
}


def run():
    from djangocms_helper import runner
    runner.cms('aldryn_search')

if __name__ == '__main__':
    run()
