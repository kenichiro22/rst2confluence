=============================================
Convert reStructuredText to Confluence markup
=============================================

Supported directives
====================

- bullet list
- enumerated list
- image, figure
- definition list
- simple table
- block quote
- text effect

  - strong
  - emphasis
  - monospace
- code blocks
- links
- admonitions

  - info
  - note
  - tip
  - warning


Usage
=====
::

    ./rst2confluence.py /path/to/file.rst


Installation
============
::

    sudo ./setup.py install


Tests
=====
We have some examples how rst2confluence should behave.

Check if it does what it should::

    ./run-tests.sh

Run a single test::

    ./run-test.sh test/figure.rst
