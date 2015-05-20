=================
aldryn-search
=================

This package provides a search indexes for easy Haystack 2 integration with django CMS.
The package is compatible with `Aldryn <http://www.aldryn.com>`_.

Usage
=====

After installing aldryn-search through your package manager of choice, add ``aldryn_search`` to your
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

To make sure the correct backend is used during search, add ``aldryn_search.router.LanguageRouter`` to your
``HAYSTACK_ROUTERS`` setting::

    HAYSTACK_ROUTERS = ['aldryn_search.router.LanguageRouter',]



When using multiple languages, usually there's one search backend per language, when indexing it's important to know
which language is currently being used, this can be facilitated by the ``ALDRYN_SEARCH_LANGUAGE_FROM_ALIAS`` setting,
this setting could be a callable or a string path that resolves to one.

Please keep in mind that it's usually not a good idea to import things in your settings, however there are cases where
it seems overkill to create a function to handle the alias, for example::

    ALDRYN_SEARCH_LANGUAGE_FROM_ALIAS = lambda alias: alias.split('-')[-1]


the example above could be used when using multiple languages and sites, all backends could have a language suffix.

The same could be achieved using a function defined somewhere else in your code like so::

    ALDRYN_SEARCH_LANGUAGE_FROM_ALIAS = "my_app.helpers.language_from_alias"



If any of the above return None then ``settings.LANGUAGE_CODE`` will be used.

By default this setting evaluates to a function that checks if the alias is in ``settings.LANGUAGES`` and if so it
uses the alias as a language.


For a complete Haystack setup, please refer to their `documentation <http://docs.haystacksearch.org/dev/>`_.

For more docs, see the ``docs`` folder or the
`online documentation <http://django-cms-search.readthedocs.org/en/latest/>`_.

Integration with django CMS
===========================

aldryn-search comes with an App Hook for django CMS, and a search view using Django's class based views. If you
want to use this app hook, you can either subclass it and register it yourself, or set
``ALDRYN_SEARCH_REGISTER_APPHOOK`` to ``True``.

For pagination, aldryn-search uses ``aldryn_common.paginator.DiggPaginator``. If you want to use this built-in
pagination, make sure to install`django-spurl <https://github.com/j4mie/django-spurl>`_, and add then add ``spurl``
to ``INSTALLED_APPS``.

Pagination
==========

Results are paginated according to the ``ALDRYN_SEARCH_PAGINATION`` setting (default: 10).
If set to ``None`` pagination is disabled.

Extra feature
=======

This branch adds a feature planed for django-haystack-2.4.0, backported to 2.3.x branch.
It uses a custom branch of django-haystack that adds support to skip the indexing of an object
anytime in it's prepare proccess.

To use this new django-haystack feature, just raise ``haystack.exceptions.DoNotIndex`` in ``prepare`` methods.

Dependencies
------------

When installing from a requirements.txt file please add following lines to it::

    https://github.com/chronossc/django-haystack/archive/2.3.x.zip#egg=django-haystack-2.3.2.dev0
    https://github.com/aldryn/aldryn-search/archive/feature/donotindex_appconfig_without_pages.zip#egg=aldryn-search

This is required by ``pip>=1.5`` which deprecate dependency links.

AldrynAppconfigIndexBase
------------------------

Due to how django url resolution works, we can index objects with wrong url. Example:

* For aldryn-newsblog we have following ``NewsBlogConfig`` namespaces: 'foo' and 'bar'.
* We have a Page with ``application_namespace = 'bar'`` and ``application_urls = 'NewsBlogApp'``.
* We have the ``<Article 1>`` with ``app_config.namespace = 'foo'``.

When indexing we get ``<Article 1>.get_absolute_url()`` and because it's namespace is ``foo`` and we does not have a newsblog page with ``application_namespace = 'foo'`` it will return url for page with ``application_namespace = 'bar'``.

This will lead to Http 404 error because when newsblog filter the articles it will look for ``bar`` namespace instead ``foo``.

This indexer will skip from indexing objects with namespaces that are not
related to any published page to avoid index of these entries.

To use that set ``ALDRYN_SEARCH_INDEX_BASE_CLASS`` to ``aldryn_search.base.AldrynAppconfigIndexBase``
or inherit your ``BaseSearch`` from that class.
