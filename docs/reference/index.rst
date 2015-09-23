#########
Reference
#########

********
Settings
********

In ``settings.py``, you can configure:


ALDRYN_SEARCH_CMS_PAGE
======================

Tells aldryn-search to register CMS pages with Haystack. Setting this to ``False`` would mean CMS
pages are *not* going to be searchable.

Default: ``True``


ALDRYN_SEARCH_DEFAULT_LANGUAGE
==============================

aldryn-search will try to match a backend alias to a valid language, when it can't find one
it will default to this setting.

This applies mostly to the ``default`` alias which does not match a language and so aldryn-search
needs to know which language should be used when indexing to this connection.

Default: ``settings.LANGUAGE_CODE``


ALDRYN_SEARCH_INDEX_BASE_CLASS
==============================

aldryn-search comes with an index class that provides some pre-configured fields;
sometimes it's useful to override this class or extend it in order to add project specific
fields to your index, like permission related fields and so on.

Default: ``'aldryn_search.base.AldrynIndexBase'``.


ALDRYN_SEARCH_LANGUAGE_FROM_ALIAS
=================================

By design, aldryn-search will do a one to one match from a haystack connection alias
to a valid django language code.

Sometimes you need to prefix your aliases, for example in a solr set-up where you serve public
content and private content, and you choose to create multilingual cores prefixed by ``public`` or
``private``. So this setting allows you to define a callable or a path to one, that takes a
connection alias as the one and only parameter and returns a valid language.

Given the scenario above, you can set this to ``lambda alias: alias.split('-'][-1]``

Default: ``'aldryn_search.utils.language_from_alias'``.


ALDRYN_SEARCH_PAGINATION
========================
The number of items to include per page when paginating search results.

Default: ``10``.


ALDRYN_SEARCH_REGISTER_APPHOOK
==============================

Depending on your project requirements, you'll either use aldryn search view directly
or connect it to a django-cms page using apphooks.

This setting tells aldryn-search to register its apphook with the CMS.

Default: ``True``.
