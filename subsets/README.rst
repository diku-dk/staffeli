Self-Contained Subsets of Staffeli
==================================

Some teachers might wish to get a simplified, self-contained subset of
Staffeli. This way, they reap the benefits of Staffeli, without inheriting it
as a software dependency: The features that they don't need can be carved out,
allowing to simplify the code-base, perhaps so much that it can fit on a
human-readable Python file, which can be distributed, and backed up, by
*copying the file*.

Examples:

* `LinAlgDat 2017 <linalg17>`__

This is noble, but silly work because:

* Upstream changes don't make it downstream.
* Downstream changes don't make it upstream.

It would be great for someone to do a BSc project to formalize the process:

1. To get a simplified, self-contained subset, start by writing a thin wrapper
   using the Staffeli API. Then, use call-graph analysis to extract just the
   parts of Staffeli needed to support the wrapper. Package it all up into a
   neat little Python file.
2. Next, it would be great to record the point at which the subset was
   constructed, and enable one to *compare* that, or the current version
   Staffeli to the subset, such that the differences between upstream and
   downstream can be identified and dealt with.
