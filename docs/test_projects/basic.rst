Basic
=====
A basic test project, with no extensions or specific themes.

Parameters
----------
:pages: Amount of pages to generate
:dummies: Amount of "dummy data" to add (Some standard sphinx directives)
:sphinx: Sphinx version to use

For the default values of the above parameters, please take a look into the ``performance.py`` file.

Information
-----------
:#dummies: Overall amount of dummies created

Run
---

.. command-output:: sphinx-performance --project basic

.. _basic_files:

Files
-----

performance.py
~~~~~~~~~~~~~~

.. literalinclude:: ../../sphinx_performance/projects/basic/performance.py


requirements.template
~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../sphinx_performance/projects/basic/requirements.template

conf.template
~~~~~~~~~~~~~

.. literalinclude:: ../../sphinx_performance/projects/basic/conf.template

index.template
~~~~~~~~~~~~~~

.. literalinclude:: ../../sphinx_performance/projects/basic/index.template

page.template
~~~~~~~~~~~~~

.. literalinclude:: ../../sphinx_performance/projects/basic/page.template