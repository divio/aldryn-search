# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

from aldryn_search import __version__


REQUIREMENTS = [
    'lxml',
    'setuptools',
    'django-appconf',
    'django-cms>=3.4.5',
    'django-haystack>=2.0.0',
    'django-spurl',
    'django-standard-form',
    'aldryn-common>=1.0.2',
]


CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Framework :: Django',
    'Framework :: Django :: 1.11',
    'Framework :: Django :: 2.0',
    'Framework :: Django :: 2.1',
    'Framework :: Django :: 2.2',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries',
]


setup(
    name='aldryn-search',
    version=__version__,
    author='Benjamin Wohlwend',
    author_email='piquadrat@gmail.com',
    url='https://github.com/divio/aldryn-search',
    license='BSD',
    description='An extension to django CMS to provide multilingual Haystack indexes',
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIREMENTS,
    classifiers=CLASSIFIERS,
    test_suite='tests.settings.run',
)
