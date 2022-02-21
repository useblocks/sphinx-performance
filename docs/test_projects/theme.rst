Theme
=====
A  test project to test specific themes.

Supported themes are:

* **rtd**: sphinx-rtd-theme
* **furo**: furo
* **book**: sphinx-book-theme
* **pydata**: pydata-sphinx-theme
* **press**: sphinx-press-theme

Parameters
----------
:theme: A predefined theme name. See above list for valid values
:sidebar: If `true`, sidebar is shown. If `false` not
:pages: Amount of pages to generate
:dummies: Amount of "dummy data" to add (Some standard sphinx directives)
:sphinx: Sphinx version to use

For the default values of the above parameters, please take a look into the ``performance.py`` file.

Information
-----------
:#dummies: Overall amount of dummies created

Run
---

.. command-output:: sphinx-performance --project theme

.. _theme_files:

Files
-----

performance.py
~~~~~~~~~~~~~~

.. literalinclude:: ../../sphinx_performance/projects/theme/performance.py


requirements.template
~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../sphinx_performance/projects/theme/requirements.template

conf.template
~~~~~~~~~~~~~

.. literalinclude:: ../../sphinx_performance/projects/theme/conf.template

index.template
~~~~~~~~~~~~~~

.. literalinclude:: ../../sphinx_performance/projects/theme/index.template

page.template
~~~~~~~~~~~~~

.. literalinclude:: ../../sphinx_performance/projects/theme/page.template