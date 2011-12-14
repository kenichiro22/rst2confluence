#!/usr/bin/env python
import os, shutil
from distutils.core import setup

if not os.path.exists('scripts'):
    os.makedirs('scripts')

shutil.copyfile('rst2confluence.py', 'scripts/rst2confluence')

setup(name='rst2confluence',
      version='0.2',
      description='reStructuredText-to-Confluence markup converter',
      author='Kenichiro TANAKA',
      author_email='tanaka.kenichiro@gmail.com',
      url='https://github.com/kenichiro22/rst2confluence',
      py_modules=['rst2confluence.confluence'],
      #package_dir={'rst2confluence': 'src/rst2confluence'},
      scripts=['scripts/rst2confluence']
     )
