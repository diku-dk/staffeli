Examples
========

List students who did not submit
--------------------------------

First, clone a course::

    $ staffeli clone <course>

This will create a course directory. The first thing you should do is navigate
to this directory::

    $ cd <course>

This contains a ``students`` subdirectory, containing a file ``.staffeli.yml``
with metadata about the students signed up for the course, in YAML format. You
can always update this metadata by issuing the following command from the
course directory::

    $ staffeli fetch students

Next, fetch or update assignment metadata::

    $ staffeli fetch subs

This does not give you information about who has submitted. To get this, you
must explicitly fetch a given assignment. To avoid actually downloading the
attachments, use the ``--metadata`` flag::

    $ staffeli --metadata fetch subs/<assignment>

This creates a directory ``subs/<assignment>/<kuid>-.../`` for each submission.

Time to apply the pipes.

To get a sorted list of the KUIDs of the students on the course::

    $ cat students/.staffeli.yml | grep sis_login_id | cut -d' ' -f4 | cut -d'@' -f1 | sort | uniq > all.txt

To get a sorted list of the KUIDs of the students that have submitted::

    $  ls subs/<assignment>/ | cut -d'_' -f1 | sort | uniq > submitted.txt

Now, we can use ``comm`` to list the KUIDs that did not submit::

    $ comm -2 -3 all.txt submitted.txt

NB! This only works for individual assignments. Group assignments will require
you to dig into the individual submissions.
