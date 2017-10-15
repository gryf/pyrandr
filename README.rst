pyrandr
=======

``pyrandr`` is a small wrapper on ``xrandr`` to provide most common usage as
simple as possible.

Requirements
------------

``pyrandr`` doesn't require any other thing than Python (any version starting
from Python 2.7) and ``xrandr`` command line tool.

Installation
------------

Just make ``pyrandr.py`` executable and drop somewhere in your ``$PATH``.

Usage
-----

Invocation is simple, executing the script:

.. code:: shell-session

   user@localhost $ pyrandr.py

should list all mailable outputs for your display device(s).

There is a mode for turning all displays at once called panic mode:

.. code:: shell-session

   user@localhost $ pyrandr.py -a

And most interesting part is ability to turn on selected outputs side by side
in horizontal layout, for example:

.. code:: shell-session

   user@localhost $ pyrandr.py -p VGA1 VGA2 VGA1

Will switch off all other outputs, but ``VGA1`` and ``VGA2``, and place those
outputs in order ``VGA1`` on the right of ``VGA2``. The option ``-p`` will set
``VGA1`` as the primary output.

Use ``--help`` to see all the other options:

.. code:: shell-session

   (myenv)user@localhost ~/mylogs $ pyrandr.py -h

License
-------

This work is licensed on 3-clause BSD license. See LICENSE file for details.
