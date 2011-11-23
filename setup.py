#!/usr/bin/env python

from distutils.core import setup

setup(name='rst2confluence',
      version='0.2',
      description='reStructuredText-to-Confluence markup converter',
      author='Kenichiro TANAKA',
      author_email='tanaka.kenichiro@gmail.com',
      url='https://github.com/kenichiro22/rst2confluence',
      py_modules=['rst2confluence.confluence'],
      #package_dir={'rst2confluence': 'src/rst2confluence'},
      scripts=['rst2confluence.py']
     )
