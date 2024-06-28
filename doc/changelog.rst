Changelog
=========

This changelog keep track of modifications. Keep an eye on it when changing
versions. Some advices are often provided.

0.8.4 (2024 06 28)
------------------

* Fix wrong bool value retrieved when ``type.bool`` is ``"false"`` (Reported and fixed by Baptiste Fraboul).
* Add support for ``ExpressionOutput`` plug type with ``LUIPSTypeAngle`` of type ``float``.
* Add support for ``types.text`` plug type.


0.8.3 (2022 03 10)
------------------

* Add support for ``types.multistrings`` plug type.
* Leave the a ``types.float`` value to string if float parsing fail.
* Support spaces in plug names (``"$1.Min Trace Depth"``).


0.8.2 (2021 04 01)
------------------

* Add support for ``types.colorspaces`` plug type as ``str``.


0.8.1 (2021 03 07)
------------------

* Add support for ``types.animationmode`` plug type as ``str``.


0.8.0 (2021 03 06)
------------------

Officially support Python 3.7 and 3.8.

Add method ``GuerillaParser.path_to_plug(path)``` to find plug from its path.

Fix ``GuerillaParser.plugs`` property didn't return all plugs properly.

Fix crash when nodes are created with a negative zero ``-0`` as name.

Limit parser crash in some specific cases on corrupted file values enclosing
regex: ``0,5`` (comma) no more match float regex.

* Uppercase "aov" in docstrings, documentation and exceptions.
* Cleanup .gitignore, add building folders.
* Update copyright date.
* Docstring and documentation cleanup.
* Add support for ``types.radians0pi4`` plug type as ``float``.

0.7.0 (2020 06 09)
------------------

Fix ``LUIPSTypeInt`` with ``'nil'`` value now return ``None``.

Fix new plug type parsing:

* ``LUIPSTypeFloat01Open`` as ``float``.
* ``types.materials`` as ``str``.
* ``LUIPSTypeVector`` as ``tuple``.
* ``LUIPSTypePoint`` as ``tuple``.
* ``LUIPSTypeNumber`` as ``float``.
* ``types.radians`` as ``float``.

Fix doc to add instance variable type.

Improve ``ArchReference`` node type support adding a ``ReferenceFileName`` plug
to such node.

Fix some deprecation warning on Python 3.8.

``connect()`` and ``depend()`` commands referencing document root attributes
on ``.glayer`` and ``.grendergraph`` are skipped:

    connect("$1.AspectRatio","$0.ProjectAspectRatio")
    depend("$17.Out","$0|Preferences.ShutterClose")

0.6.0 (2018 02 27)
------------------

Add Python 3.5 and 3.6 CI test. Now officially support 2.7, 3.4, 3.5 and 3.6.

``connect()`` and ``depend()`` call with nodes having dots ``.`` is now
supported.

Support ``^`` character in ``set()`` command.

New iterator: ``GuerillaParser.plugs`` iterate over every parsed
``GuerillaPlug``.

New plug types found and supported:

* ``HSetPlug``
* ``HVisiblePlug``
* ``HMattePlug``
* ``SceneGraphNodePropsPlug``
* ``SceneGraphNodeRenderPropsPlug``
* ``AttributePlug``
* ``AttributeShaderPlug``

See :doc:`this page <file_format_info>` for more information.

Fix node with number as name (``Cube``, ``Sphere``, ``Plane``, etc. with type
``SubPrimitive``). Guerilla return their name as number (``0`` for default
``Cube`` sub primitive) but they are bracketed in paths ``Cube|[0]``. Now, this
behavior is properly emulated.

Fix ``GuerillaPlug.path`` could raise an exception if plug's parent is the root
node.

Fix ``GuerillaParser()`` ``diagnose`` argument would crash when trying to print
root node paths.

Fix no more printing of various unknown commands.

Fix ``GuerillaParser.nodes`` property wasn't iterating in every nodes.

Still improve documentation.

Rewrite most regex.

Handle Guerilla paths for numeric node names (``SubPrimitive`` typed nodes).

0.5.0 (2018 02 24)
------------------

Add Python 3 support (and CI). Now officially support 2.7 and 3.4.

Support new characters for node names:

* brackets (``[]``).

Fix:

* Implicit node paths were not properly parsed.
* Guerilla file encoding is ``iso-8859-1`` (was broken in Python 3)

Unit tests: Improve performance parsing once and use later.

Documentation:

* Uppercase first letter of every docstring.
* Remove useless quotes from class names.
* Rewrite most of the documentation.

0.4.0 (2018 02 13)
------------------

Support new characters:

* slash (``/``) in path of ``set()`` commands.
* comma (``,``), dollar (``$``) and minus (``-``) in path of ``connect()`` commands.

Improve documentation formating.

Fix unit test in environment with default guerilla_parser module.

Reorganize unit tests.

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
* space.

Support nodes with empty names (``GraphFrame`` can have empty string as name).

Fix bad implicit node handling (rewrite implementation).

Write a ``__repr__()`` implementation for ``GuerillaNode`` and ``GuerillaPlug``
for debugging purpose.

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
