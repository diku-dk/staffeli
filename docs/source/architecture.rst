Architecture
============

Staffeli has a *layered* architecture, staring with a low-level API wrapper,
wrapped in an object model.

Low-level API Wrapper
---------------------

The ``Canvas`` object, defined in ``canvas.py``, implements a number of
low-level wrappers for the `Canvas LMS REST API`_. It makes few abstractions,
and is mainly a functional reflection of the REST API.

.. _Canvas LMS REST API: https://canvas.instructure.com/doc/api/index.html

Object Model
------------

There are two fundamental classes:

1. A ``ListedEntity`` has a ``name``, or ``id``, and occurs in some listing on
canvas.  For instance, both courses and assignments are "listed entities".

2. A ``CachableEntity`` may be "cached" on disk, to avoid excessive REST API
requests, which can otherwise be a drag.

Python allows multiple inheritance, so some objects are both an instance of
``ListedEntity`` and ``CachableEntity``. For instance, both ``Course`` and
``Assignment`` inherit from the two.

NB! ``ListedEntity`` and ``CachableEntity`` have conflicting constructors.  One
will reach for the containing list on Canvas, while the other will reach for
the disk. The choice between these is made at runtime. The former is chosen if
any identifying information is given. For instance, if the user is cloning a
given course, or fetching a given assignment, then we reach for Canvas
regardless of what may be on disk.

Listed Entities
~~~~~~~~~~~~~~~

.. todo::

   Coming soon.

Cachable Entities
~~~~~~~~~~~~~~~~~

Cachable entities are cached on disk. They are stored in a dedicated directory,
in a YAML file called ``.staffeli.yml``. (Note the leading ``.``: The file
remains hidden to many Unix-style utilities. You might find this useful.)

Cachable entities have a ``cachename``. This identifies a cache entry (some
``.staffeli.yml`` file) as belonging to this particular cachable entity. This
is used to distinguish different cachable entities (e.g., course and
assignment).

Cachable entities can be initialized with a path, which is optionally walked up
to find a matching cache entry:

  * If initialized with a path to a cache entry, or its containing directory,
    the file is loaded without further a due (failing if the cachename does
    not match).

  * If allowed to walk, ``staffeli`` walks up in the filesystem
    hierarchy, until a matching cache entry is found, if any. ``staffeli``
    eventually gives up at ``/``, if not earlier.

  * By default, the path is set to ``.`` i.e., the current working directory.

Cachable entities which have no backing cache should simply not call the
constructor.

The filesystem walk is useful if you would like to find some containing cache
entry while deep inside the file system hierarchy (e.g., find the course while
marking a submission).
