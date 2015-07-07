#!/usr/bin/env python
# -*- coding: utf-8 -*-


HELPER_SETTINGS = {
    'ALLOWED_HOSTS': ['localhost'],
    'CMS_LANGUAGES': {1: [{'code': 'en', 'name': 'English'}]},
    'CMS_TEMPLATES': (("whee.html", "Whee Template"),),
    'LANGUAGES': (('en', 'English'),),
    'LANGUAGE_CODE': 'en',
    'TEMPLATE_LOADERS': ('aldryn_search.tests.FakeTemplateLoader',),
}


def run():
    from djangocms_helper import runner
    runner.cms('aldryn_search')

if __name__ == '__main__':
    run()
