CLI
===
**sphinx-performance** is used via its command line interface.

To get a first help, type ``sphinx-performance --help``

.. command-output:: sphinx-performance --help

\-\-project
---------
``--project`` allows to select a specific test project.

This can be an integrated project or a path to a self defined project::

    sphinx-performance --project needs
    sphinx-performance --project my/sphinx/project

Default: ``basic``

\-\-parallel
----------
Defines the amount of cores (Sphinx workers) to use for the build.

Uses internally the Sphinx option ``-j``.

Parallel execution can bring huge benefits, if the documentation is based on
multiple pages.

.. command-output:: sphinx-performance --parallel 1 --parallel 4 --pages 30

Project parameters
------------------
**sphinx-performance** takes every project parameters and provides it to the test project.

Which parameters are need and how their defaults looks like are documented in the test project specific documentation.

.. command-output:: sphinx-performance --pages 2 --dummies 5

Parameter matrix
~~~~~~~~~~~~~~~~
All project parameters can be set multiple times, so that tests gets executed for each given parameter.

**sphinx-performance** creates also a configuration matrix, if multiple parameters are given multiple times.

This ``--pages 1 --pages 5 --dummies 1 --dummies 20`` would run 4 tests with:

    #. ``pages = 1`` and ``dummies = 1``
    #. ``pages = 1`` and ``dummies = 20``
    #. ``pages = 5`` and ``dummies = 1``
    #. ``pages = 5`` and ``dummies = 20``

.. command-output:: sphinx-performance --pages 1 --pages 5 --dummies 1 --dummies 20




\-\-debug
-------
Shows the out put of Sphinx build and Python dependency installation step:

.. command-output:: sphinx-performance --debug

\-\-keep
------
Does not delete the created, temporary test folders and prints their location.

.. command-output:: sphinx-performance --keep

\-\-browser
---------
Opens each generated documentation in the browser after the build::

    sphinx-performance --browser

This sets also automatically ``--keep``.






