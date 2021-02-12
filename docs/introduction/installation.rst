############
Installation
############

****************
Install packages
****************

We'll assume you have a django CMS (version 3.x) project up and running.

If you need to set up a new django CMS project, follow the instructions in the `django CMS
tutorial <http://docs.django-cms.org/en/develop/introduction/install.html>`_.

Then run either::

    pip install aldryn-search

or to install from the latest source tree::

    pip install -e git+https://github.com/aldryn/aldryn-search.git#egg=aldryn-search


********************
Edit ``settings.py``
********************

In your project's ``settings.py`` make sure you have all of::

    'haystack',
    'aldryn_search',
    'standard_form',
    'spurl',

listed in ``INSTALLED_APPS``, *after* ``'cms'``.


***************
Set up Haystack
***************

You'll need to set up django-haystack according to its `installation instructions
<http://django-haystack.readthedocs.org/en/master/tutorial.html#installation>`_.

.. note::

	Regardless of the search backend you picked, you need to have a ``default`` connection
	in your ``HAYSTACK_CONNECTIONS`` setting.

So if you have multiple languages, your configuration could look something like::

    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
            'URL': 'http://my-solr-server/solr/my-site-de/',
        },
        'en': {
            'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
            'URL': 'http://my-solr-server/solr/my-site-en/',
        },
        'fr': {
            'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
            'URL': 'http://my-solr-server/solr/my-site-fr/',
        },
    }


With these settings, we can have Aldryn Search map a connection alias to a language
and then we can use the ``ALDRYN_SEARCH_DEFAULT_LANGUAGE`` setting to tell Aldryn Search
which language should it fall back to if it can't map an alias to a language.

So for our example, we would set ``ALDRYN_SEARCH_DEFAULT_LANGUAGE`` to ``'de'``, then the default
alias will always map to the ``'de'`` language.


*************
Rebuild index
*************

Now run ``python manage.py rebuild_index`` to push all your data from the database to your
configured search backend.
