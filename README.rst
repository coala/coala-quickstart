.. image:: https://cloud.githubusercontent.com/assets/7521600/19196124/e6ea06dc-8cd1-11e6-84a8-c51c899a1f36.png

coala-quickstart: personalized coala setup for your project
-----------------------------------------------------------
coala-quickstart is a tool that helps users to quickly get started
with coala. It can generate a ``.coafile`` (
`coala <https://github.com/coala/coala>`__'s configuration
file) that is tailored to your project. This supports projects in
several languages, including popular languages such as C/C++, Python,
JavaScript, CSS, Java.

Please note that you will want do manually adapt the configuration to
your needs!

-----

.. contents::
    :local:
    :depth: 1
    :backlinks: none

-----

========
Features
========

* Out-of-the-box support for projects using various
  `popular languages <https://github.com/coala/bear-docs/blob/master/README.rst>`__,
  such as **C/C++**, **Python**, **Javascript**, **CSS**, **Java** and many
  others with built-in check routines.
* Automatic identification of relevant bears for your project
  based on the languages used.
* A clean and simple interface with a well defined flow.

-----

============
Installation
============

To install the **latest stable version** run:

.. code-block:: bash

    $ pip3 install coala-quickstart

|Stable|

To install the latest development version run:

.. code-block:: bash

    $ pip3 install coala-quickstart --pre

The latest code from the master branch is automatically deployed as the
development version in PyPI.

|PyPI| |Windows| |Linux|

-----

=====
Usage
=====

coala-quickstart is designed with ease of use and simplicity in mind. To get
started, simply run:

.. code-block:: bash

    $ coala-quickstart

This should prompt you for the project directory. If you want to use the current
directory, just press the return key and we'll be on our way!

At the end, you should have a file named ``.coafile`` generated at the root of your
project directory. This contains all the settings needed by coala to lint and
fix your code.

When this is done, simply fire up coala from your project's root directory:

.. code-block:: bash

    $ coala

You can also open the ``.coafile`` in your favorite editor and edit
the settings to suit your needs. Check out our `coafile specification <http://coala.readthedocs.io/en/latest/Users/coafile.html>`__
to learn more.

-----

=======
Support
=======

Feel free to contact us at our `Gitter channel <https://gitter.im/coala/coala>`__, we'd be happy to help!

You can also drop an email at our
`mailing list <https://github.com/coala/coala/wiki/Mailing-Lists>`__.

-----

=======
Authors
=======

coala-quickstart is maintained by a growing community. Please take a look at the
meta information in `setup.py <setup.py>`__ for the current maintainers.

-----

=======
License
=======

|AGPL|

.. |Windows| image:: https://img.shields.io/badge/platform-Windows-brightgreen.svg
.. |Linux| image:: https://img.shields.io/badge/platform-Linux-brightgreen.svg
.. |Stable| image:: https://img.shields.io/badge/latest%20stable-0.3.0-green.svg
.. |PyPI| image:: https://img.shields.io/pypi/pyversions/coala-quickstart.svg
   :target: https://pypi.python.org/pypi/coala-quickstart
.. |Linux Build Status| image:: https://img.shields.io/circleci/project/coala/coala-quickstart/master.svg?label=linux%20build
   :target: https://circleci.com/gh/coala/coala
.. |Windows Build status| image:: https://img.shields.io/appveyor/ci/coala/coala/master.svg?label=windows%20build
   :target: https://ci.appveyor.com/project/coala/coala/branch/master
.. |Scrutinizer Code Quality| image:: https://img.shields.io/scrutinizer/g/coala-analyzer/coala.svg?label=scrutinizer%20quality
   :target: https://scrutinizer-ci.com/g/coala-analyzer/coala/?branch=master
.. |codecov.io| image:: https://img.shields.io/codecov/c/github/coala/coala/master.svg?label=branch%20coverage
   :target: https://codecov.io/github/coala/coala?branch=master
.. |Documentation Status| image:: https://readthedocs.org/projects/coala/badge/?version=latest
   :target: http://coala.rtfd.org/
.. |AGPL| image:: https://img.shields.io/github/license/coala/coala.svg
   :target: https://www.gnu.org/licenses/agpl-3.0.html
.. |Gitmate| image:: https://img.shields.io/badge/Gitmate-0%20issues-brightgreen.svg
   :target: http://gitmate.com/
.. |gitter| image:: https://badges.gitter.im/coala/coala.svg
    :target: https://gitter.im/coala/coala
    :alt: Chat on Gitter
