.. Sphinx-Performance documentation master file, created by
   sphinx-quickstart on Tue Feb 15 11:42:18 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Sphinx-Performance
==================

**Sphinx-Performance** is a Commandline tool to analyse the performance of different Sphinx documentation
project setups.

It was created to answer questions like:

* How good does Sphinx scale?
* Which impact has an extension to the build time?
* Is there any different between two specific versions?
* How huge is the benefit of using parallel build mode?
* Which are the performance bottlenecks during a Sphinx build?

.. image:: /_static/sphinx_performance_showcase.gif
   :align: center

.. note::

   Based on the used test project, **sphinx-performance** may install specific library versions
   into the currently used Python environment.

   It is a good idea to use virtual environments for **sphinx-performance** runs.


.. toctree::
   :maxdepth: 3
   :caption: Contents:

   cli
   test_projects/index

Kudos
-----
This little tool borrows a lot of ideas from the
`performance script <https://sphinxcontrib-needs.readthedocs.io/en/latest/performance/index.html>`_
of `Sphinx-Needs <https://sphinx-needs.com>`_.
