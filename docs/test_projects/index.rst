Test Projects
=============

Integrated test project
-----------------------
This is a list of Sphinx projects, which are available to be used as test project.

.. toctree::
   :maxdepth: 1

   basic
   needs

Own test projects
-----------------
The parameter ``--project`` can also take a path to a local test project.

This test project **must** contain the following files:

::

    ├── conf.template
    ├── index.template
    ├── page.template
    ├── performance.py
    ├── requirements.template
    └── _static

.. hint::

   It is a good idea to use one of the :ref:`existing test projects <basic_files>` as template.

Additional files are allowed and get copied to the temporary source folder as well.
However the additional files get not handled by **jinja2**.


jinja support
~~~~~~~~~~~~~
All basic files ending on ``.template`` get handled by **jinja2**, so that all build and project parameters
are available and allow the creation of "dynamic rst and config files".

performance.py
~~~~~~~~~~~~~~
Gets imported by **sphinx-performance** and must provide two variables:

* parameters
* info

parameters
++++++++++
Must be a ``dict``, where each **key** represents a parameter, which can be set by the user.
Do not use any whitespace or characters, which are hard to use on a Commandline interface.

The **value** represents a default value, which is taken, if the use does use the parameter.

.. hint::

     The ``value`` does not support multiple values.
     So a test project can only have one single, fix configuration by default.

Example::

    parameters = {
        "sphinx": "4.2",
        "pages": 10,
        "dummies": 10
    }

info
++++
Must be a ``dict``, is able to give additional information to the user.
Helpful to e.g. calculate the overall amount of "dummies", which is the product of ``dummies_per_page x pages``.

Example::

    info = {
        '#dummies': "{{dummies * pages}}"
        }

conf.template
~~~~~~~~~~~~~
Standard Sphinx ``conf.py`` file, but with **jinja2** support.

index.template
~~~~~~~~~~~~~~
Main index file, which must contain ``rst`` data.

page.template
~~~~~~~~~~~~~
Template for a page file, which must contain ``rst`` data.

Multiple page files get created, based on the ``--pages`` option.
The name would be ``page_1.rst``, ``page_2.rst``, ...

requirements.template
~~~~~~~~~~~~~~~~~~~~~
A pip requirements file, which gets installed via ``pip install -r requirements.txt``.

It also has **jinja2** support, which allows to define libraries or specific versions via
commandline.

__static folder
~~~~~~~~~~~~~~~
This folder should exist to supress Sphinx warnings about a missing ``__static folder``.






