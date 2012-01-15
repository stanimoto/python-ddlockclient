from setuptools import setup

from ddlockclient import __version__ as version

setup(
    name = 'DDLockClient',
    version = version,
    author = 'Satoshi Tanimoto',
    description = 'Python client library for the Danga distributed lock daemon',
    long_description = open('README.rst').read(),
    url = 'http://github.com/stanimoto/python-ddlockclient',
    packages = ['ddlockclient'],
    license='Apache',
)
