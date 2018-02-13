Known limitations
=================

Guerilla file format has some particularities affecting the way the parser is written.

int vs float
------------

Lua version used in Guerilla (5.1) `does not <https://www.lua.org/pil/2.3.html>`_ `support` ``int`` types. Any numeric value is a ``float`` so it's the attribute that `defines` the type. This also mean a value of ``2.0`` will always be stored as a ``2`` in Guerilla files, without the comma.

When Guerilla parse the file back, it store value depending on the attribute type.

This means you can't guess the type from the parsed file only. That's why the parser returns numerical values as Python ``float``.

TODO
----

- object id and oid
- '{}'
- 'create.Id'
- float to int so we only take float
- not tested on python 3 (because CGI is python2)
