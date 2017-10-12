pyrandr
=======

``pyrandr`` is a small wrapper on ``xrandr`` to provide most common usage as
simple as possible.

Requirements
------------

``pyrandr`` doesn't require any other thing than python and ``xrandr`` command
line tool. Currently it is tested only on Python2.7, support for Python3 is
coming.

Installation
------------

Just make ``pyrandr.py`` executable and drop somewhere in your ``$PATH``.

Usage
-----

Invocation is simple, executing the script:

.. code:: shell-session

   user@localhost $ pyrandr.py

should list all mailable outputs for your display device(s)

Use ``--help`` to see all the other options:

.. code:: shell-session

   (myenv)user@localhost ~/mylogs $ pyrandr.py -h

License
-------

This work is licensed on 3-clause BSD license. See LICENSE file for details.
