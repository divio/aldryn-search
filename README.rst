=================
djangocms-search
=================

This package provides a search indexes for easy Haystack 2 integration with django CMS.

Usage
=====

After installing djangocms-search through your package manager of choice, add ``djangocms_search`` to your
``INSTALLED_APPS``. If you run a multilingual CMS setup, you have to define a haystack backend for every language
in use::

    HAYSTACK_CONNECTIONS = {
        'en': {
            'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
            'URL': 'http://my-solr-server/solr/my-site-en/',
            'TIMEOUT': 60 * 5,
            'INCLUDE_SPELLING': True,
            'BATCH_SIZE': 100,
        },
        'fr': {
            'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
            'URL': 'http://my-solr-server/solr/my-site-fr/',
            'TIMEOUT': 60 * 5,
            'INCLUDE_SPELLING': True,
            'BATCH_SIZE': 100,
        },
    }

To make sure the correct backend is used during search, add ``djangocms_search.router.LanguageRouter`` to your
``HAYSTACK_ROUTERS`` setting::

    HAYSTACK_ROUTERS = ['djangocms_search.router.LanguageRouter',]


For a complete Haystack setup, please refer to their `documentation <http://docs.haystacksearch.org/dev/>`_.

For more docs, see the ``docs`` folder or the
`online documentation <http://django-cms-search.readthedocs.org/en/latest/>`_.

