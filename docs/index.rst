.. role:: underline
    :class: underline

.. only:: html

   .. image:: https://img.shields.io/pypi/dm/sphinx-performance.svg
       :target: https://pypi.python.org/pypi/sphinx-performance
       :alt: Downloads
   .. image:: https://img.shields.io/pypi/l/sphinx-performance.svg
       :target: https://pypi.python.org/pypi/sphinx-performance
       :alt: License
   .. image:: https://img.shields.io/pypi/pyversions/sphinx-performance.svg
       :target: https://pypi.python.org/pypi/sphinx-performance
       :alt: Supported versions
   .. image:: https://readthedocs.org/projects/sphinx-performance/badge/?version=latest
       :target: https://readthedocs.org/projects/sphinx-performance/
   .. image:: https://img.shields.io/pypi/v/sphinx-performance.svg
       :target: https://pypi.python.org/pypi/sphinx-performance
       :alt: PyPI Package latest release


Sphinx-Performance
==================

**Sphinx-Performance** is a Commandline tool to analyse the performance of different Sphinx documentation
project setups.

It was created to answer questions like:

* How well does Sphinx scale?
* What impact does a specific extension have to the build time?
* Is there any different between two specific versions?
* How huge is the benefit of using parallel build mode?
* What are the performance bottlenecks during a Sphinx build?

.. image:: /_static/sphinx_performance_showcase.gif
   :align: center

.. note::

   Based on the used test project, **sphinx-performance** may install specific library versions
   into the currently used Python environment.

   It is a good idea to use virtual environments for **sphinx-performance** runs.


.. toctree::
   :maxdepth: 3
   :caption: Contents:

   installation
   cli
   test_projects/index

Kudos
-----
This little tool borrows a lot of ideas from the
`performance script <https://sphinx-performance.readthedocs.io/en/latest/performance/index.html>`_
of `Sphinx-Needs <https://sphinx-needs.com>`_.


Changelog
---------
0.1.7
~~~~~
:Released: under development

* Improvement: ``--project`` can be used multiple times.
* Bugfix: Python bin/script calculation on windows fixed.

0.1.6
~~~~~
:Released: 21.02.2022

* Improvement: Reading and writing times get measured (ALPHA status, poor parallel build support).
* Improvement: CSV export is possible by setting ``--csv results.csv``.
* Improvement: Builder can be set, also multiple times: ``--builder json``.

0.1.5
~~~~~
:Released: 18.02.2022

* Improvement: ``--temp`` parameter support
* Improvement: Result tables highlights diffs
* Improvement: More data for result tables
* Bugfix: Unique Needs ID calculation

0.1.4
~~~~~
:Released: 17.02.2022

* Bugfix: "Need" project unique object-id calculation working with folders.
* Bugfix: "Need" project defines all needed defaults now.

0.1.3
~~~~~
:Released: 17.02.2022

* Improvement: More data (File amounts and sizes, build times, progress timer)
* Improvement: Amount of folders can be defined
* Improvement: Folder depth can be defined
* Improvement: Folder support for test projects

0.1.2
~~~~~
:Released: 16.02.2022

* Initial version

