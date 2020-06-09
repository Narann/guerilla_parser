Known limitations
=================

Guerilla file format imply some parsing limitations.

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
- add delete command support (optional?).
- improve and expose set_plug_value().
- utest to execute inside Guerilla (Guerilla Docker image?).

Conversions
-----------

* Missing lua to python conversion `'{}'`.
* Missing lua to python conversion `'types.color'`.
* Missing lua to python conversion `'types.float {min=1,max=10}'`.
* Missing lua to python conversion `'matrix.create{-1,0,0,0,0,1,0,0,0,0,-1,0,0,0,0,1}'`.
* Missing lua to python conversion `'transform.create{-1,0,0,0,0,1,0,0,0,0,-1,0,0,0,0,1}'`.
* Curve unpacking is not supported.

Glayer connection to document
-----------------------------

Some ``.glayer``/``.grendergraph`` documents have a connection or depend command to root document:

    connect("$1.AspectRatio","$0.ProjectAspectRatio")
    depend("$17.Out","$0|Preferences.ShutterClose")

Such connections are skipped when those files are parsed because document structure doesn't exists.
