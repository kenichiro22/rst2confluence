*********************************************
Convert reStructuredText to Confluence markup
*********************************************

====================
Supported directives
====================

- bullet list
- enumerated list
- image, figure, confluence image galleries
- definition list
- simple and grid tables
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
- field lists
- line blocks (except nested ones)
- meta directives
- substitutions


Additional features
===================

Image galleries
---------------
Images and figures with class names that begin with
``gallery-`` form a gallery::

   .. image:: cat.jpg
       :class: gallery-1
   .. image:: dog.jpg
       :class: gallery-1
   .. figure:: horse.jpg
       :class: gallery-2
       :scale: 50%

This creates two galleries: One with cat and dog, the other one with
the horse picture only.
All attributes are ignored on gallery images.

Gallery-classed images are converted to ``{gallery:include=a.jpg,b.jpg}``
Confluence markup.

=====
Usage
=====
::

    ./rst2confluence.py /path/to/file.rst


============
Installation
============
From git checkout::

    $ sudo ./setup.py install

Without a git checkout::

    $ pip install rst2confluence


============
Dependencies
============
- ``python-docutils``


=====
Tests
=====
We have some examples how ``rst2confluence`` should behave.

Check if it does what it should::

    ./run-tests.sh

Run a single test::

    ./run-test.sh test/figure.rst


===========
Other tools
===========
Use deploy-rst__ to automatically deploy rST documents into confluence.


__ https://github.com/netresearch/deploy-rst


=======================
Releasing a new version
=======================

1. Fill ``ChangeLog``
2. Update version in ``setup.py``
3. Create release tag
4. Upload to pip::

     $ ./setup.py sdist upload
