groups
======

This is for group assignments.

If you are a TA who just wants to grade submissions, you can jump to step 5.


Step 0: Assignment creation on Absalon
--------------------------------------

When creating a new assignment on Absalon, we make sure to tick the box that
makes it a group assignment, and create a new group category 'Assignment N
Groups'.


Step 1: Handing uploading
-------------------------

A student uploads a submission, possibly containing a `group.txt` file.


Step 2: Downloading
-------------------

We fetch all handins::

  staffeli fetch subs/N

where N is likely just a number.  For example, if the assignment name on Absalon
is 'Assignment 3: Rabbit drawing', then N is 3.  You can also use longer
patterns if necessary.


Step 3: Groups
--------------

We split them into groups.

First we find all groups::

  find-groups.sh subs/N > subs/N/groups.txt

Then we check if the groups make sense::

  check-groups.py subs/N/groups.txt

If this script doesn't print any errors, then the groups are probably fine.

We then need to create the groups on Absalon, so that all group members will be
registered as having submitted, and so that all group members can see our
feedback when it comes up.  We also need to have the groups available locally.
We run::

  create-groups.py 'Assignment N Groups' subs/N/groups.txt

where the first argument is the group category name creating in step 0.

This will create groups on Absalon and symlink locally in the ``groupsubs``
directory.


Step 4: Sections
----------------

(Optional.)

We distribute the group submissions into TA sections.  We do this to decide
which TA gets to correct which submissions.  We run::

  split-into-sections.py groupsubs/N subs/N/groups.txt SECTION...

This will symlink submissions in the ``sections`` directory.


Step 5: Grading
---------------

``cd`` to a submission directory, write some feedback, and run::

  staffeli grade GRADE -f feedback.txt

where ``GRADE`` is either ``pass``, ``incomplete`` (resubmit) or ``fail``.
Staffeli knows where to send the feedback based on a hidden file
``.staffeli.yml`` in the directory.

This will upload your feedback as comment.  It is also possible to upload
attachments, but this does not fly after a while, at least not on the KU
instance of Canvas: There appears to be some kind of cumulative limit on the
file sizes one can upload through the API.

When uploading the feedback as a comment, note that the line length is not
fixed.


Step 6: Late submissions and resubmissions
----------------------------------------------

Late submissions are handled outside the group.txt staffeli system for now.  You
can still fetch the new subs, but running the group-related scripts anew is not
guaranteed to be safe.  If necessary, you can always create late groups with
the ``staffeli group`` commands, or using Absalon's web interface.

For now it is probably best to handle resubmissions partially from within the
SpeedGrader web interface, at least for downloading the resubmissions.  Staffeli
can be a bit confused about that.


Helper tools
------------

It can be useful to find out the KU id of a student based on their name.  Run::

  staffeli user find NAME

To find out which group a student is a member of, run::

  groups-search subs/N/groups.txt abc123
