Needs
=====
A `Sphinx-Needs <https://sphinx-needs.com>`_ specific project to test the performance with different
amounts of needs and needtables.

Parameters
----------
:needs: Number of maximum needs
:needtables: Number of maximum needtables
:dummies: Number of standard rst dummies
:pages: Number of additional pages with needs
:parallel: Number of parallel processes to use. Same as -j for sphinx-build
:sphinx: Sphinx version to use

For the default values of the above parameters, please take a look into the ``performance.py`` file.

Information
-----------
:#needs: Overall amount of needs
:#needtables: Overall amount of needtables
:#dummies: Overall amount of dummies

Run
---
.. command-output:: sphinx-performance --project needs

Files
-----

.. _needs_performance:

performance.py
~~~~~~~~~~~~~~

.. literalinclude:: ../../sphinx_performance/projects/needs/performance.py


requirements.template
~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../sphinx_performance/projects/needs/requirements.template

conf.template
~~~~~~~~~~~~~

.. literalinclude:: ../../sphinx_performance/projects/needs/conf.template

index.template
~~~~~~~~~~~~~~

.. literalinclude:: ../../sphinx_performance/projects/needs/index.template

page.template
~~~~~~~~~~~~~

.. literalinclude:: ../../sphinx_performance/projects/needs/page.template

