import metadata as m

from setuptools import setup, find_packages

INSTALL_REQUIRES = [
    'lxml',
    'setuptools',
    'Django>=1.4,<1.7',
    'django-appconf',
    'django-cms>=2.4',
    'django-classy-tags>=0.3.2',
    'django-haystack>=2.3.2.dev0,<2.4.0',
    'django-spurl',
    'django-standard-form',
    'aldryn-common',
]

DEPENDENCY_LINKS = [
    'https://github.com/chronossc/django-haystack/archive/2.3.x.zip#egg=django-haystack-2.3.2.dev0'  # NOQA
]

setup(
    name=m.name,
    version=m.version,
    url=m.project_url,
    license=m.license,
    platforms=['OS Independent'],
    description=m.description,
    author=m.author,
    author_email=m.author_email,
    packages=find_packages(),
    install_requires=INSTALL_REQUIRES,
    dependency_links=DEPENDENCY_LINKS,
    # Accept all data files and directories matched by MANIFEST.in or
    # found in source control.workon
    include_package_data=True,
    package_dir={
        m.package_name: m.package_name,
    },
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
