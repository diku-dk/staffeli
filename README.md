# Staffeli — DIKU Support Tools for Canvas LMS

"Staffeli" is Danish for "easel" — a support frame for holding up a canvas.

![An Easel](logo.jpg
  "Image license: CC0; Source: https://pixabay.com/en/art-painting-modern-art-mural-1027828/")

These tools leverage the [Canvas LMS REST
API](https://canvas.instructure.com/doc/api/index.html) to create a more
pleasant environment for working with [Absalon](https://absalon.ku.dk/).

[![Documentation Status](https://readthedocs.org/projects/staffeli/badge/?version=latest)](http://staffeli.readthedocs.io/en/latest/?badge=latest)
[![License](https://img.shields.io/badge/license-EUPL%20v1.1-blue.svg)](https://github.com/DIKU-EDU/Staffeli/blob/master/LICENSE.md)

## Purpose

The purpose of Staffeli is two-fold:

1. Leverage the [Canvas LMS REST
API](https://canvas.instructure.com/doc/api/index.html) to get things done
better, faster, stronger.
1. Quick prototyping of new features for [Canvas
LMS](https://www.canvaslms.com/).

Initially, Staffeli is _not_ intended for managing course content, merely to
let teachers and teaching assistants get an overview of the course (students,
submissions, etc.), _and_ to get grading done efficiently.

## Status

This is a somewhat coherent summoning of scripts developed during courses using
Canvas. Brace yourself. Lend a hand.

## Installation

1. `pip3 install --user pyyaml`
1. Add `Staffeli/lib/` to your PYTHONPATH environment variable.
1. Add `Staffeli/bin/` to your PATH environment variable.

## Getting Started

With Staffeli, we work with local course clones. We aim to keep these clones
compatible with git.

We recommend that you create a local directory `canvas`, `absalon`, or similar,
for all of you Canvas-related local course clones. Staffeli needs some initial
help to be able to login with your credentials. You need to [generate a
token](https://guides.instructure.com/m/4214/l/40399-how-do-i-obtain-an-api-access-token-for-an-account)
for Staffeli to use, and save it as `.token`, `token`, or `token.txt` in this
high-level directory.

**NB!** This is your personal token so **do not** share it with others, else
they can easily impersonate you using a tool like Staffeli. Unfortunately, to
the best of our knowledge, Canvas has no means to segregate or specialize
tokens, so this is really "all or nothing".

## Cloning a Course

To clone a course:

```
$ staffeli clone <course name>
```

The `<course name>` may be a substring of the course name as it appears on your
dashboard. Casing is not important. If there are multiple conflicting names, or
no matching course names, Staffeli will complain and let you try again.

## Design

In the following, the keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL
NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" are to be
interpreted as described in [RFC 2119](http://tools.ietf.org/html/rfc2119)
(Bradner, S., "Key words for use in RFCs to Indicate Requirement Levels", BCP
14, RFC 2119, March 1997).

In the following, the "foreseeable future" is roughly 5 years.

1. Staffeli SHOULD be "cross-platform", working across all the *desktop*
   platforms that teachers and teaching assistants might use for the foreseeable
   future.

2. Staffeli SHOULD be easy to maintain for the foreseeable future. The primary
   programming language SHOULD be the one deemed most familiar to present and
   perspective teaching assistants.

3. Staffeli SHOULD be easy to extend. It is unlikely that Staffeli
   meets everyone's needs, and so it should have a clear, modular design,
   allowing for quick and dirty extensions, which can grow into stable parts
   of Staffeli proper over time.

4. Staffeli SHOULD be *fast*, not reloading information that is known (i.e.,
   known to Staffeli users) to not have changed. This is to combat Canvas
   page-loading time issues, and possible Canvas down-times.

**Outcome 1:** Python 3, is deemed[1] a popular, modern, cross-platform language.
Python 3 is the primary choice for every part of Staffeli. When relevant,
cross-platform Python 3 code SHOULD be preferred over non-cross-platform code.
For instance, when handling file system paths.

**Exceptions to outcome 1:** When everyone involved is known to use a
particular set of desktop platforms, and a part of Staffeli would be faster to
write in a platform-specific way.

**Outcome 2:** [YAML](http://yaml.org/) is a human-readable data serialization
language. It is similar to JSON, but is deemed[1] slightly more readable.
Staffeli generates local YAML dumps of Canvas course data that is not likely to
change. These SHOULD be decorated with an expiration timestamp.

**Outcome 3:** First and foremost, Staffeli provides a [Python 3 library
interface](src/canvas.py), which hides low-level mechanics of the REST API. To
make Staffeli accessible further, a [command-line interface](src/CanvasTA)
hides the low-level mechanics of the Python 3 library interface. We are open to
adding a web, mobile, or desktop UI, but no one has done any work on this yet.

[1]: By @oleks, @nqpz. (Your name here?)

## Giving Feedback via Script

Navigate to the student directory containing a `canvas_group.json`, or a
file with a name matching the pattern

```
<name>_(late_)?_<studentid>_<submissionid>_.*
```

For instance, a file named something like

```
kenfriislarsen_12321_1414214_src-1.zip
```

From here, you can use `feedback.py` to give feedback:

```
feedback.py <grade> <file> [<more-files>]
```

For instance,

```
feedback.py 3 feedback.html
```

or

```
feedback.py incomplete feedback.html onlineta.txt
```

`feedback.py` accepts `complete`, `incomplete`, `pass`, `fail`, or an integer
grade. `feedback.py` does not (yet) validate whether the grade you provide is
compatible with the assignment: beware if your assignment is marked as
pass/fail or on a point-scale. `feedback.py` also does not (yet) verify that
the points you give fall within the assignment point scale (neither does
Canvas!).

NB! For `feedback.py` to work you also need to have a hierarchy of
`canvas.json` files, specifying the course and assignment ids. There is no
automatic script for setting this up (yet).

## Contributing

Contact us at dikunix at dikumail dot dk.

Take a look at our on-going [issues](https://github.com/DIKU-EDU/Staffeli/issues).

## Style Guide

We use a tab-width of 4 spaces, with tabs expanded to spaces.

### `vim`

Add this to your `~/.vimrc`:

```
au BufNewFile,BufRead /path/to/Staffeli/* set expandtab tabstop=4
```
