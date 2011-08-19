#!/usr/bin/env python
import os
from smk import __version__

f = open(os.path.join(os.path.dirname(__file__), 'README.md'))
long_description = f.read()
f.close()

sdict = {
    'name' : 'smk',
    'version' : __version__,
    'description' : 'Python client for Smarkets streaming API',
    'long_description' : long_description,
    'url': 'https://github.com/smarkets/smk_python_sdk',
    'download_url' : 'https://github.com/smarkets/smk_python_sdk/downloads/smk_python_sdk-%s.tar.gz' % __version__,
    'author' : 'Smarkets Limited',
    'author_email' : 'support@smarkets.com',
    'maintainer' : 'Smarkets Limited',
    'maintainer_email' : 'support@smarkets.com',
    'keywords' : ['Smarkets', 'betting exchange'],
    'license' : 'MIT',
    'packages' : ['smk'],
    'test_suite' : 'tests.all_tests',
    'classifiers' : [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python'],
    }

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(**sdict)
