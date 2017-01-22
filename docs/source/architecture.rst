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
