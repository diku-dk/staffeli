# Design

In the following, the keyword "SHOULD" is to be interpreted as described in
[RFC 2119](http://tools.ietf.org/html/rfc2119) (Bradner, S., "Key words for use
in RFCs to Indicate Requirement Levels", BCP 14, RFC 2119, March 1997).

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

**Outcome 1:** Python 3, is deemed[1] a popular, modern, cross-platform
language.  Python 3 is the primary choice for every part of Staffeli.
Cross-platform Python 3 code SHOULD be preferred over non-cross-platform code.
For instance, when handling file-system paths.

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
