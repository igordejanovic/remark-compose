#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import codecs
from setuptools import setup
import remarkcompose

AUTHOR = 'Igor R. Dejanovic'
AUTHOR_EMAIL = 'igor DOT dejanovic AT gmail DOT com'
GITHUB_ACCOUNT = 'igordejanovic'

NAME = 'remark-compose'
DESC = 'A tool for making slides in remarkjs'
VERSION = remarkcompose.__version__
LICENSE = 'MIT'
URL = 'https://github.com/%s/%s' % (GITHUB_ACCOUNT, NAME)
DOWNLOAD_URL = 'https://github.com/%s/%s/archive/v%s.tar.gz' % \
    (GITHUB_ACCOUNT, NAME, VERSION)
README = codecs.open(os.path.join(os.path.dirname(__file__), 'README.md'),
                     'r', encoding='utf-8').read()

if sys.argv[-1].startswith('publish'):
    if os.system("pip list | grep wheel"):
        print("wheel not installed.\nUse `pip install wheel`.\nExiting.")
        sys.exit()
    if os.system("pip list | grep twine"):
        print("twine not installed.\nUse `pip install twine`.\nExiting.")
        sys.exit()
    os.system("python setup.py sdist bdist_wheel")
    if sys.argv[-1] == 'publishtest':
        os.system("twine upload -r test dist/*")
    else:
        os.system("twine upload dist/*")
        print("You probably want to also tag the version now:")
        print("  git tag -a {0} -m 'version {0}'".format(VERSION))
        print("  git push --tags")
    sys.exit()

setup(
    name = NAME,
    version = VERSION,
    description = DESC,
    long_description = README,
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,
    maintainer = AUTHOR,
    maintainer_email = AUTHOR_EMAIL,
    license = LICENSE,
    url = URL,
    download_url = DOWNLOAD_URL,
    packages = ["remarkcompose"],
    install_requires = ["click", "glob2", "textX", "livereload", "Jinja2"],
    keywords = "markdown presentation slides",
    entry_points={
        'console_scripts': [
            'remarkc = remarkcompose.cli:remarkc'
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Topic :: Multimedia :: Graphics :: Presentation',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        ]

)
