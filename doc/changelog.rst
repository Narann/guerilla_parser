Changelog
=========

0.3.0 (2018 01 10)
------------------

Support new characters for node names:

* parentheses (``()``).
* spaces, dot (``.``).
* backslash (``\\``).
* dollar (``$``).
* pipe (``|``).
* plus (``+``).
* minus (``-``).
* space (`` ``).

Support nodes with empty names (``GraphFrame`` can have empty string as name).

Fix bad implicit node handling (rewrite implementation).

Write a `__repr__()` implementation for `GuerillaNode` and `GuerillaPlug` for debugging purpose.

Rewrite unit test implementation to dynamically create them.

0.2.0 (2017 11 4)
------------------

Better performance on big gproject files.

Support nodes with `,` and `|` in names.

Fix bad assertion in plug name.

Skip unsupported (yet) inputs in `$0` formatting.

Update documentation (still far from perfect).


0.1.0 (2017 06 11)
------------------

Initial release
