# Staffeli — DIKU Support Tools for Canvas LMS

"Staffeli" is Danish for "easel" — a support frame for holding up a canvas.

![An Easel](logo.jpg
  "Image license: CC0; Source: https://pixabay.com/en/art-painting-modern-art-mural-1027828/")

These tools leverage the [Canvas LMS REST
API](https://canvas.instructure.com/doc/api/index.html) to create a more
pleasant environment for working with [Absalon](https://absalon.ku.dk/).

[![Documentation Status](https://readthedocs.org/projects/staffeli/badge/?version=latest)](http://staffeli.readthedocs.io/en/latest/?badge=latest)

## Installation

1. `pip3 install --user pyyaml`
1. Add `Staffeli/src/` to your PYTHONPATH environment variable.
1. Add `Staffeli/src/` to your PATH environment variable.
1. Generate a token at https://absalon.instructure.com/profile/settings, save
   it in a file named `token` in your course directory. This is your personal
   token, so best to ignore it in git.

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
   programming language SHOULD be the one deemed most familiar to
   perspective teaching assistants in that period.

3. Staffeli SHOULD be fast and easy to extend. It is unlikely that Staffeli
   meets everyone's needs, and so it should have a clear, modular design,
   allowing for quick and dirty extensions, which over time can grow into
   stable parts of Staffeli proper.

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

**Outcome 2:** YAML is a human-readable data serialization language. It is
similar to JSON, but is deemed[1] slightly more readable. Staffeli generates local
YAML dumps of Canvas course data that is not likely to change. These SHOULD be
decorated with an expiration timestamp.

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

We use a tab-width of 4 spaces, with tabs expanded to spaces.

### `vim`

Add this to your `~/.vimrc`:

```
au BufNewFile,BufRead /path/to/Staffeli/* set expandtab tabstop=4
```
