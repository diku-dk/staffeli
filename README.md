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
