=================
django-cms-search
=================

This package provides multilingual search indexes for easy Haystack integration
with `django CMS <http://www.django-cms.org>`_.

Requirements
============

 * Django >= 1.4
 * django CMS >= 2.4
 * django-haystack >= 2.0

Usage
=====

After installing djangocms-search through your package manager of choice, add
:mod:`djangocms_search` to your :setting:`INSTALLED_APPS`.

Multilingual Setup
------------------

Haystack 2.0 introduced the support of multiple backends. This is a good fit
for indexing multilingual content: every language gets its own backend. This
allows for language-specific configuration of each backend, e.g. for stopwords
or stemming algorithms.

An example of such a setup could look like this::

    HAYSTACK_CONNECTIONS = {
        'en': {
            'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
            'URL': 'http://my-solr-server/solr/my-site-en/',
            'INCLUDE_SPELLING': True,
        },
        'fr': {
            'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
            'URL': 'http://my-solr-server/solr/my-site-fr/',
            'INCLUDE_SPELLING': True,
        },
    }

    HAYSTACK_CONNECTIONS['default'] = HAYSTACK_CONNECTIONS['en']

.. note::

    Haystack requires the definition of a ``default`` backend. Reusing one of
    the defined language backends seems sensible in this case.

To make sure that the correct language is used when searching, add
:class:`djangocms_search.router.LanguageRouter` to your
:setting:`HAYSTACK_ROUTERS` setting::

    HAYSTACK_ROUTERS = ['djangocms_search.router.LanguageRouter',]


If you want to index your own multilingual content, just make sure that  your
:meth:`~SearchIndex.index_queryset` implementation filters by
language. The language that is currently indexed can be found in the ``using``
argument.



For setting up Haystack, please refer to their
`documentation <http://django-haystack.readthedocs.org/en/dev/>`_.

Customizing the Index
---------------------

You can customize what parts of a :class:`~cms.models.CMSPlugin` end up in
the index with two class attributes on :class:`~cms.plugin_base.CMSPluginBase`
subclasses:

.. attribute:: search_fields

    a list of field names to index.

.. attribute:: search_fulltext

    if ``True``, the index renders the plugin and adds the result (sans HTML
    tags) to the index.


Settings
========
.. setting: DJANGOCMS_SEARCH_INDEX_BASE_CLASS

DJANGOCMS_SEARCH_INDEX_BASE_CLASS
---------------------------------
Default: :class:`djangocms_search.base.TitleIndexBase`

This setting can be used to add custom fields to the search index if the
included fields do not suffice. Make sure to provide the full path
to your :class:`haystack:SearchIndex` subclass.
