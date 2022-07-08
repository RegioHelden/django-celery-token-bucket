# -*- coding: UTF-8 -*-
import os
import re
from os.path import join, dirname
from setuptools import setup, find_packages


def get_version(*file_paths):
    """Retrieves the version from the given path"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def long_description():
    """Return long description from README.rst if it's present
    because it doesn't get installed."""
    try:
        return open(join(dirname(__file__), 'README.md')).read()
    except IOError:
        return ''


setup(
    name='django-celery-token-bucket',
    packages=find_packages(),
    version=get_version("django_celery_token_bucket", "__init__.py"),
    description='A token bucket implementation for celery rate limiting in Django',
    author='Jens Nistler <opensource@jensnistler.de>, Richard Ackon <richard.ackon@stroeer-online-marketing.de>',
    author_email='opensource@regiohelden.de',
    long_description=long_description(),
    long_description_content_type='text/markdown',
    install_requires=[
        'celery>=5.0.0',
        'Django>=3.2',
        'django-celery-beat>=2.3.0',
        'kombu>=5.2.4',
    ],
    license='MIT',
    url='https://github.com/RegioHelden/django-celery-token-bucket',
    project_urls={
        "Documentation": "https://github.com/RegioHelden/django-celery-token-bucket/blob/master/README.md",
        "Source": "https://github.com/RegioHelden/django-celery-token-bucket",
        "Tracker": "https://github.com/RegioHelden/django-celery-token-bucket/issues",
        "Changelog": "https://github.com/RegioHelden/django-celery-token-bucket/blob/master/CHANGELOG.md",
    },
    keywords=['django', 'celery', 'token', 'bucket', 'rate limiting'],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)
