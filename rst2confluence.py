#!/usr/bin/env python

"""
Confluence Wiki output generator for the Docutils Publisher.
"""

try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

from docutils.core import publish_cmdline, default_description

from rst2confluence import confluence


description = ('Generates documents in Confluence Wiki format from standalone '
               'reStructuredText sources.  ' + default_description)

publish_cmdline(writer=confluence.Writer(), description=description)
