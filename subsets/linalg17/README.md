# `staffeli.py`

This is a selective, self-contained subset of
[staffeli](https://github.com/DIKU-EDU/staffeli) — DIKU Support Tools for
Canvas LMS. All it can do is download the submissions for a given assignment,
and split them up according to sections. As such, [`staffeli.py`](staffeli.py)
contains everything you need. The other files contain fluffy software
development stuff.

## Getting Started

First off, make sure you have Python 3 installed. This is the only requirement
to run [`staffeli.py`](staffeli.py).

To run [`staffeli.py`](staffeli.py) you need to provide a Canvas token and a
course ID. The script will look for the file `.staffelirc` in your home
directory structured as follows:

```
[linalg]
course_id = 19..
token = 7500~...
```

Follow [this
guide](https://guides.instructure.com/m/4214/l/40399-how-do-i-obtain-an-api-access-token-for-an-account)
to generate a token for your Canvas account.

**NB!** This is your personal token so **do not** share it with others, else
they can easily impersonate you using a tool like Staffeli. Unfortunately, to
the best of our knowledge, Canvas has no means to segregate or specialize
tokens, so this is really "all or nothing".

The course ID is a decimal number which is part of your course URL. That is, if
you go to your course page on Canvas, it will end in something like
`courses/<couse ID>`, where `<course ID>` is a decimal number.

Then, you should be able to just do this:

```
$ ./staffeli.py "Projekt ..."
```

Where `Projekt ...` is a substring of the assignment name on Canvas. This
will also be the name of the directory where `staffeli.py` will place the
submissions.

## Debugging

Python comes with [a debugger](https://docs.python.org/3.6/library/pdb.html)
out of the box. It seems quite practical to set breakpoints explicitly by
modifying the code:

```
# Line to break after
import pdb      # This is allowed in Python
pdb.set_trace() # .. and this is the breakpoint!
# Line to break before
```

# `.static_tests.py`

This is part of the software development fluff.
[`.static_tests.py`](static_tests.py) runs
[`flake8`](http://flake8.pycqa.org/en/latest/) to ensure a proper Python style,
and [`mypy`](http://mypy.readthedocs.io/en/latest/) to do some _static type
checking_.

As such, the Python code (e.g., in [`staffeli.py`](staffeli.py)) might look odd
to folks not familiar with [Python type hints (PEP
484)](https://www.python.org/dev/peps/pep-0484/).
