import metadata as m

from setuptools import setup, find_packages

install_requires = [
    'lxml',
    'setuptools',
    'Django>=1.8',
    'django-appconf',
    'django-cms>=3.5',
    'django-haystack>=2.0.0',
    'django-spurl',
    'django-standard-form',
    'aldryn-common>=1.0.2',
]

setup(
    name = m.name,
    version = m.version,
    url = m.project_url,
    license = m.license,
    platforms=['OS Independent'],
    description = m.description,
    author = m.author,
    author_email = m.author_email,
    packages=find_packages(),
    install_requires = install_requires,
    # Accept all data files and directories matched by MANIFEST.in
    # or found in source control.
    include_package_data = True,
    package_dir = {
        m.package_name: m.package_name,
    },
    zip_safe=False,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
