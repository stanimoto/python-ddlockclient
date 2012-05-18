from setuptools import setup

from ddlockclient import __version__ as version

setup(
    name = 'DDLockClient',
    version = version,
    author = 'Satoshi Tanimoto',
    author_email = 'tanimoto.satoshi@gmail.com',
    description = 'Python client library for the Danga distributed lock daemon',
    long_description = open('README.rst').read(),
    url = 'http://github.com/stanimoto/python-ddlockclient',
    packages = ['ddlockclient'],
    license='Apache',
    tests_require=['coverage', 'nose', 'unittest2', 'pep8'],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'License :: OSI Approved :: Apache Software License',
        ]
)
