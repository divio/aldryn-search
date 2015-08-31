############
Installation
############


Example content:

    *******************
    Installing packages
    *******************

    We'll assume you have a django CMS (version 3.x) project up and running.

    If you need to set up a new django CMS project, follow the instructions in the `django CMS
    tutorial <http://docs.django-cms.org/en/develop/introduction/install.html>`_.

    Then run either::

        pip install aldryn-jobs

    or to install from the latest source tree::

        pip install -e git+https://github.com/aldryn/aldryn-jobs.git#egg=aldryn-jobs


    ***********
    settings.py
    ***********

    In your project's ``settings.py`` make sure you have all of::

        'absolute',
        'aldryn_common',
        'aldryn_boilerplates',
        'aldryn_apphooks_config',
        'aldryn_reversion',
        'aldryn_categories',
        'aldryn_jobs',
        'emailit',
        'parler',
        'standard_form',
        'sortedm2m',

    listed in ``INSTALLED_APPS``, *after* ``'cms'``.

    .. note::
       If you are using Django 1.6, add ``south`` to  ``INSTALLED_APPS``.


    Now set the name of the boilerplate you want to use in your project::

        ALDRYN_BOILERPLATE_NAME = 'bootstrap3'

    .. note::
       Note that Aldryn Jobs doesn't use the the traditional Django ``/templates`` and ``/static
       directories``. Instead, it employs `Aldryn Boilerplates
       <https://github.com/aldryn/aldryn-boilerplates>`_, which makes it possible to to support
       multiple different frontend schemes ('Boilerplates')and switch between them without the need
       for project-by-project file overwriting.

       Aldryn Jobs's templates and staticfiles will be found in named directories inside the
       ``/boilerplates`` directory.


    ****************************
    Prepare the database and run
    ****************************

    Now run ``python manage.py migrate`` to prepare the database for the new application, then
    ``python manage.py runserver``.


    ****************
    For Aldryn users
    ****************

    On the Aldryn platform, the Addon is available from the `Marketplace
    <http://www.aldryn.com/en/marketplace>`_.

    You can also `install Aldryn Jobs into any existing Aldryn project
    <https://control.aldryn.com/control/?select_project_for_addon=aldryn-jobs>`_.
