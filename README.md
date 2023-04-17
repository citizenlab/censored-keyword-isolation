# censored-keyword-isolation

Algorithms for using repeated sample tests to isolate which combination of
keywords is triggering automatic filtering of a censored string of text.

The files prefixed with `algorithms-*` versus `coroutines-*` implement the
same underlying algorithm, but they have different interfaces for determining
whether a collection of strings is censored.  The former require the
implementation and passing of a callback function `is_censored` which must be
designed such that it returns `True` or `False` depending on whether a passed
collection of strings is censored.  The latter will `yield` a string to test
for censorship, after which `True` or `False` must be returned to the coroutine
via its `send()` method.

The files suffixed with `*-ordered` are variants of the algorithm in which the
order of the appearance of keyword combinations components is relevant for
triggering censorship.  In these, keyword combinations are modeled as tuples as
opposed to sets.

The files containing the `*left*` infix may return a different keyword
combination in the case that multiple censored keyword combinations are
present in the censored string.  Namely, if more than one censored keyword
combination is present, these variants isolate the one whose rightmost
component is leftmost in the provided string, whereas the algorithms without
the `*left*` infix isolate the one whose leftmost component is rightmost.

This code originally accompanied the paper "[An Efficient Method to Determine
which Combination of Keywords Triggered Automatic Filtering of a Message](
https://www.usenix.org/system/files/foci19-paper_xiong.pdf)" by Ruohan Xiong
and Jeffrey Knockel (2019). For the original version with all of the algorithms
evaluated in the paper, see
[this commit](https://github.com/citizenlab/censored-keyword-isolation/tree/37f9cc44).
