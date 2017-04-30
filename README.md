# `staffeli` — DIKU Support Tools for Canvas LMS

"Staffeli" is Danish for "easel" — a support frame for holding up a canvas.

<p align="center"><img src ="logo.jpg" width="300" alt="An Easel"
title="Image license: CC0; Source:
https://pixabay.com/en/art-painting-modern-art-mural-1027828/"/></p>

These tools leverage the [Canvas LMS REST
API](https://canvas.instructure.com/doc/api/index.html) to create a more
pleasant environment for working with [Absalon](https://absalon.ku.dk/).

[![Documentation Status](https://readthedocs.org/projects/staffeli/badge/)](http://staffeli.readthedocs.io/en/latest/)
[![Travis CI (Linux + macOS) Status](https://travis-ci.org/DIKU-EDU/staffeli.svg)](https://travis-ci.org/DIKU-EDU/staffeli)
[![License: EUPL v1.1](https://img.shields.io/badge/license-EUPL%20v1.1-blue.svg)](https://github.com/DIKU-EDU/Staffeli/blob/master/LICENSE.md)

## Purpose

The purpose of Staffeli is two-fold:

1. Leverage the [Canvas LMS REST
API](https://canvas.instructure.com/doc/api/index.html) to get things done
better, faster, stronger.
1. Quick prototyping of new features for [Canvas
LMS](https://www.canvaslms.com/).

Initially, Staffeli is _not_ intended for managing course content, merely to
snapshot course data (e.g. enrolled students, groups, sections, submissions),
_and_ to get grading done efficiently.

## Status

This is a somewhat coherent summoning of scripts developed during courses using
Canvas. Brace yourself. Lend a hand.

## Installation

1. Clone, or
   [download](https://github.com/DIKU-EDU/staffeli/archive/master.zip) this
   repository.
2. `pip3 install .`

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

### Cloning a Course

To clone a course:

```
$ staffeli clone <course name>
```

The `<course name>` may be a substring of the course name as it appears on your
dashboard. Casing is not important. If there are multiple conflicting names, or
no matching course names, Staffeli will complain and let you try again.

### Fetch Submissions for a New Assignment

Use `staffeli fetch`. For instance, to fetch all submissions for "A3":

```
$ staffeli fetch subs/A3
```

To fetch just the metadata for all submissions, but not the submissions
themselves:

```
$ staffeli fetch subs
```

### Fetch Groups

This is a good idea to make sure you are up-to-date with canvas.

```
$ staffeli fetch groups
```

### Split According to Some Group Category

Assuming you already fetched groups and submissions,

```
$ staffeli groupsplit subs/A3 groups/Team.yml
```

### NB

If you are using git to share course internals, remember to push both changes
to [`groups`](groups), [`subs`](subs), and [`splits`](splits), when making
splits for some new assignment.

### Grade a Submission

Assuming you are in the submission directory, you can use `staffeli grade` to
grade the submission:

```
staffeli grade GRADE [-m COMMENT] [FILEPATH]...

Where
    GRADE           pass, fail, or an int.
    [-m COMMENT]    An optional comment to write.
    [FILEPATH]...   Optional files to upload alongside.
```

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

[1]: By @oleks, @nqpz, @orkeren. (Your name here?)

## Contributing

Please follow our [style guide](STYLE.md)

Contact us at dikunix at dikumail dot dk.

Take a look at our on-going [issues](https://github.com/DIKU-EDU/Staffeli/issues).

## Related Work

In terms of Python-wrapper design, Staffeli is in many ways to
[Canvas](https://www.canvaslms.com/) as
[`python-gitlab`](http://python-gitlab.readthedocs.io/en/stable/) is to
[GitLab](https://about.gitlab.com/).

Closer to Canvas, however, we can mention these projects:

* [`lumenlearning/python3-canvaslms-api`](https://github.com/lumenlearning/python3-canvaslms-api)
  * 1 contributor
  * Last commit was made on June 25, 2013.
* [`dkloz/canvas-api-python`](https://github.com/dkloz/canvas-api-python)
  * 1 contributor
  * Last commit was made on May 13, 2016.
