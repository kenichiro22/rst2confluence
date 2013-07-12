*********************************************
Convert reStructuredText to Confluence markup
*********************************************

====================
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
- field lists
- line blocks (except nested ones)


Additional features
===================

Image galleries
---------------
Class names beginning with ``gallery-`` form a gallery::

   .. image:: cat.jpg
       :class: gallery-1
   .. image:: dog.jpg
       :class: gallery-1
   .. image:: horse.jpg
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
::

    sudo ./setup.py install


=====
Tests
=====
We have some examples how ``rst2confluence`` should behave.

Check if it does what it should::

    ./run-tests.sh

Run a single test::

    ./run-test.sh test/figure.rst
