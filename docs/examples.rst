Examples
========

These are some command line examples to show how to measure and analyse Sphinx builds.


Runtime analysis with a local package
-------------------------------------

Loads the project **needs** and uses the reference configuration named **small**.

Uses pyinstrument tree view to show the needed runtime of important functions.

It also installs a local version of sphinx-needs, so that local code changes (performance bug fixes) can be easily
tested.

.. code-block:: bash

   sphinx-analysis --project needs --ref small \
   --local /home/daniel/workspace/sphinx/sphinx-needs \
   --pyinstrument --tree




