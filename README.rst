lpais
=====  

|license| |python version| |build-status| |docs| |coverage| |pypi package|

.. |license| image:: https://img.shields.io/github/license/loicpw/lpais.svg
.. |build-status| image:: https://travis-ci.org/loicpw/lpais.svg?branch=master
    :target: https://travis-ci.org/loicpw/lpais
.. |docs| image:: https://readthedocs.org/projects/lpais/badge/?version=latest
    :target: http://lpais.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
.. |coverage| image:: https://coveralls.io/repos/github/loicpw/lpais/badge.svg?branch=master
    :target: https://coveralls.io/github/loicpw/lpais?branch=master
.. |pypi package| image:: https://badge.fury.io/py/lpais.svg
    :target: https://badge.fury.io/py/lpais
.. |python version| image:: https://img.shields.io/pypi/pyversions/lpais.svg
   :target: https://pypi.python.org/pypi/lpais

use libais to decode ais messages, 

install and test
=======================

.. warning:: user is encouraged to use `gcc`_ to compile `libais`_
    (*gcc* and *g++*), otherwise it's likely to fail. Make sure **gcc**
    will be used as default compliler or specify it when install / build

    example:

    .. code-block:: bash

        $ CC=gcc-8 CXX=g++-8 make install

production install
******************

There is a makefile in the project root directory:
    
.. code-block:: bash

    $ make install

Using pip, the above is equivalent to:

.. code-block:: bash

    $ pip install -r requirements.txt                                             
    $ pip install -e .

dev install
****************

There is a makefile in the project root directory:
    
.. code-block:: bash

    $ make dev

Using pip, the above is equivalent to:

.. code-block:: bash

    $ pip install -r requirements-dev.txt                                             
    $ pip install -e .

run the tests
******************

Use the makefile in the project root directory:

.. code-block:: bash

    $ make test

This runs the tests generating a coverage html report

build the doc
******************

The documentation is made with sphinx, you can use the makefile in the
project root directory to build html doc:

.. code-block:: bash

    $ make doc

Documentation
=======================

Documentation on `Read The Docs`_.

Meta
=======================

loicpw - peronloic.us@gmail.com

Distributed under the MIT license. See ``LICENSE.txt`` for more information.

https://github.com/loicpw


.. _Read The Docs: http://lpais.readthedocs.io/en/latest/
.. _gcc: https://gcc.gnu.org/
.. _libais: https://github.com/schwehr/libais 
