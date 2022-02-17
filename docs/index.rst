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

   Based on the test project used, **sphinx-performance** may install specific library versions
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
