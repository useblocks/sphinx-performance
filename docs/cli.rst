CLI
===
.. contents::
   :local:
   :depth: 1



.. _sphinx-performance:

sphinx-performance
------------------
**sphinx-performance** is used via its command line interface.

To get a first help, type ``sphinx-performance --help``

.. command-output:: sphinx-performance --help

Use **sphinx-command** to compare different Sphinx project setups.

For deeper analysis, use :ref:`sphinx-analysis`.

\-\-project
~~~~~~~~~~~
``--project`` allows to select a specific test project.

This can be an integrated project or a path to a self defined project::

    sphinx-performance --project needs
    sphinx-performance --project my/sphinx/project

Can be used multiple times, so that for each project a specific test run gets executed::

    sphinx-performance --project basic --project needs

Default: ``basic``

\-\-parallel
~~~~~~~~~~~~
Defines the amount of cores (Sphinx workers) to use for the build.

Uses internally the Sphinx option ``-j``.

Parallel execution can bring huge benefits, if the documentation is based on
multiple pages.

.. command-output:: sphinx-performance --parallel 1 --parallel 4 --pages 30

\-\-builder
~~~~~~~~~~~
Defines the builder to use, for instance ``html``, ``text``, ``json``, ``xml``.

Type ``make`` in a sphinx project folder so see all available builders.

Can be used multiple times, so that for each builder a specific test run gets executed.

.. command-output:: sphinx-performance --pages 2 --builder html --builder text


Project parameters
~~~~~~~~~~~~~~~~~~
**sphinx-performance** takes every project parameters and provides it to the test project.

Which parameters are need and how their defaults looks like are documented in the test project specific documentation.

.. command-output:: sphinx-performance --pages 2 --dummies 5

Commonly used parameters
++++++++++++++++++++++++
This is a list of parameters, which are supported by most test projects.

\-\-pages
*********
Amount of pages per folder::

    sphinx-performance --pages 20


\-\-folders
***********
Amount of folders per folder depth::

    sphinx-performance --folders 10 --pages 10

This will create 10 sub-folders, each containing 10 pages.

\-\-depth
*********
Folder depth.

1 = Create folders once on root level

2 = Create also folder again in folders of root level

And so one.

This means the amount of folders and files raises exponential::

    sphinx-performance --pages 10 --folders 10 --depth 0  # 10 pages, 0 folders
    sphinx-performance --pages 10 --folders 10 --depth 1  # 110 pages, 10 folders
    sphinx-performance --pages 10 --folders 10 --depth 2  # 1110 pages, 100 folders


\-\-ref
*******
Allows to select a preconfigured testproject setup by its reference name.

Each test project can provide its own set of configurations.

There is no common naming rule, how such references shall be named in Sphinx-Performance.
For details take a look at the variable ``references`` of ``performance.py`` file of each test
project. For embedded projects:

* :ref:`Basic config file <basic_performance>`
* :ref:`Needs config file <needs_performance>`
* :ref:`Theme config file <theme_performance>`

Example::

   sphinx-performance --project theme --ref alabaster --ref rtd --ref pydata --ref furo --browser --depth 2

Config parameters set by a reference configuration can be easily overwritten by just using the parameter in the
command line call::

   sphinx-performance --ref small --folders 50


Parameter matrix
++++++++++++++++
All project parameters can be set multiple times, so that tests gets executed for each given parameter.

**sphinx-performance** creates also a configuration matrix, if multiple parameters are given multiple times.

This ``--pages 1 --pages 5 --dummies 1 --dummies 20`` would run 4 tests with:

    #. ``pages = 1`` and ``dummies = 1``
    #. ``pages = 1`` and ``dummies = 20``
    #. ``pages = 5`` and ``dummies = 1``
    #. ``pages = 5`` and ``dummies = 20``

.. command-output:: sphinx-performance --pages 1 --pages 5 --dummies 1 --dummies 20


\-\-temp
~~~~~~~~
Defines the location of the folder to use for creating the temporary test project folders.

By default a operating system specific is chosen, on Linux this is ``/tmp``.

``--temp`` can also be a relative path.

So a ``sphinx-performance --temp .`` will create a test-folder like ``tmp0zmq3js2`` in the current working directory.

Use ``--temp`` together with ``--keep``, to keep the test-folder at an easy accessible location.


\-\-debug
~~~~~~~~~
Shows the out put of Sphinx build and Python dependency installation step:

.. command-output:: sphinx-performance --debug

\-\-keep
~~~~~~~~
Does not delete the created, temporary test folders and prints their location.

.. command-output:: sphinx-performance --keep

\-\-browser
~~~~~~~~~~~
Opens each generated documentation in the browser after the build::

    sphinx-performance --browser

This sets also automatically ``--keep``.

\-\-csv
~~~~~~~
Stores the result table in a given CSV-file

If the file exists, it gets overwritten:

   sphinx-performance --csv results.csv


.. _sphinx-analysis:

sphinx-analysis
---------------
**sphinx-analysis** builds a **single** project, but is able to create runtime and memory profiles
of the Sphinx build. It also allows to present the profiled data in different views, like
tables, flamegraphs and summaries.

For **runtime profiling**,
`cProfile <https://docs.python.org/3/library/profile.html#module-cProfile>`__
is used. `memray <https://bloomberg.github.io/memray/index.html>`__
is the used **memory profiler**, which also supports a live viewer.

.. warning::

   Don't use more than one profiler at the same time, as they would influence each other.
   It's better to reuse the same project config and just replace the profiler.

The options for setting up the project are the same as for :ref:`sphinx-performance`, except
``csv``, which is not supported, and ``snakeviz``, which was renamed to ``flamegraph``.

Example calls::

   sphinx-analysis --project --pages 10 --folders 3 --depth 2 --memray --flamegraph
   sphinx-analysis --project --pages 10 --folders 3 --depth 2 --runtime --stats
   sphinx-analysis --project needs --needs 40 --needtables 2 --pages 5 --folders 2 --depth 1 --pyinstrument --tree
   sphinx-analysis --ref medium --runtime --summary

.. _option_runtime:

\-\-runtime
~~~~~~~~~~~
Starts the runtime profiling of the Sphinx build.
Results are stored inside the file ``runtime_all.prof``.

.. _option_memray:

\-\-memray
~~~~~~~~~~
Profiles the memory consumption of the Sphinx build.
Results are stored in the file ``memray_all.prof``.

.. _option_memray_live:

\-\-memray-live
~~~~~~~~~~~~~~~
Nearly same as :ref:`option_memray`, but waits with the profiling till a memray viewer is connected.
Creates no result file.

A memray viewer can be opened in another terminal by executing ``memray live 13167``.

.. image:: /_static/sphinx_analysis_live.gif
   :width: 99%

.. _option_pyinstrument:

\-\-pyinstrument
~~~~~~~~~~~~~~~~
Uses the pyinstrument profiler and saves the profile in a file called ``pyinstrument_profile.json``.


\-\-stats
~~~~~~~~~
Prints some statistics at the end of the build.

Supported by: :ref:`option_runtime` and :ref:`option_memray`.

.. figure:: /_static/runtime_stats.png
   :width: 49%

   runtime stats

.. figure:: /_static/memray_stats.png
   :width: 49%

   memray stats

\-\-summary
~~~~~~~~~~~
Prints the memray summary at the end of the build.

Supported by: :ref:`option_memray`.

.. figure:: /_static/memray_summary.png
   :width: 49%

   memray summary

\-\-flamegraph
~~~~~~~~~~~~~~
Opens a browser to show a flamegraph view of the captured profile.

For ``runtime`` snakeviz is used, and for ``memray`` the memray flamegraph.

Supported by: :ref:`option_runtime` and :ref:`option_memray`.


.. figure:: /_static/runtime_flamegraph.png
   :width: 49%

   runtime flamegraph

.. figure:: /_static/memray_flamegraph.png
   :width: 49%

   memray flamegraph

\-\-silent
~~~~~~~~~~
Can be used to answer questions to the user automatically with ``yes``.

This may happen, if e.g. multiple projects are configured to be used, and ``sphinx-analysis`` asks the user to confirm
this.


\-\- tree
~~~~~~~~~
Creates a ``pyinstrument_profile.html`` file, which shows a runtime tree, profiled by ``--pyinstrument``.

Supported by: :ref:`option_pyinstrument`.


.. figure:: /_static/pyinstrument_tree.png
   :width: 49%

   pyinstrument tree in HTML file
