#!/usr/bin/env python
import glob
import os
import subprocess
import sys

sys.path.insert(0, os.path.abspath("."))

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from distutils.spawn import find_executable
from distutils.command import clean, build


class SmarketsProtocolBuild(build.build):
    "Class to build the protobuf output"

    description = "build the protocol buffer output with protobuf-compiler"

    def run(self):
        "Run the 'protoc' compiler command"
        protoc = find_executable("protoc")
        if protoc is None:
            sys.stderr.write("*** Cannot find protoc; is the protobuf compiler"
                             " installed?\n")
            sys.exit(-1)

        for source in glob.glob('*.proto'):
            if sys.platform == 'win32':
                source = source.replace('/', '\\')
            args = (protoc, '--python_out=.', source)
            if subprocess.call(args) != 0:
                sys.exit(-1)

        for pkg_dir in ('eto', 'seto'):
            init_file = os.path.join(
                os.path.dirname(__file__), pkg_dir, '__init__.py')
            open(init_file, 'w').close()

        build.build.run(self)


class SmarketsProtocolClean(clean.clean):
    """Class to clean up the built protobuf files."""

    description = "clean up files generated by protobuf-compiler"

    def run(self):
        """Do the clean up"""
        for source in glob.glob("eto/*.py"):
            os.unlink(source)
        for source in glob.glob("seto/*.py"):
            os.unlink(source)
        os.unlink('eto')
        os.unlink('seto')

        # Call the parent class clean command
        clean.clean.run(self)


f = open(os.path.join(os.path.dirname(__file__), 'README.rst'))
long_description = f.read()
f.close()


__version__ = '0.1.0'

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
    'packages' : ['smk', 'eto', 'seto'],
    'test_suite' : 'tests.all_tests',
    'classifiers' : [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python'],
    'cmdclass' : {
        'build': SmarketsProtocolBuild,
        'clean': SmarketsProtocolClean},
    }

setup(**sdict)
