Example
=======

.. module:: guerilla_parser

This page give some examples and code snippets to use Guerilla parser.

Parse given file
----------------

Use the :py:meth:`parse() <guerilla_parser.GuerillaParser.from_file>` method to parse and get :py:class:`~guerilla_parser.GuerillaParser` object interfacing the parsed document:

    >>> import guerilla_parser
    >>> p = guerilla_parser.parse("/home/user/my_project.gproject")

Iterate over every node
-----------------------

This snippet use :py:meth:`GuerillaParser.nodes <guerilla_parser.GuerillaParser.nodes>` property to iterate over every parsed node.

    >>> for node in p.nodes:
    >>>     print node.path, node.type

Get every reference files
-------------------------

This snippet list every reference file.

This can be usefull to list Alembic files from a gproject.

    >>> for node in p.nodes:
    >>>     if node.type == 'ArchReference':
    >>>         print node.get_plug('ReferenceFileName')

Get root node
-------------

For a gproject file, root node is the document node.

    >>> doc = p.root
    >>> print doc.get_plug('FirstFrame').value
    101
    >>> print doc.get_plug('LastFrame').value
    150


Get node name, path and type
----------------------------

    >>> print node.name
    'RenderGraph'
    >>> print node.path
    '|RenderGraph'
    >>> print node.type
    'RenderGraph'

Get parent node
---------------

    >>> print node.parent
    GuerillaNode(44, 'RenderGraph', 'RenderGraph')

Get node display name
---------------------

This is useful for aov nodes.

    >>> print node.display_name
    'Beauty'

Iterate over every children of a node
-------------------------------------

    >>> for child in node.children:
    >>>     print child.path

Get node children by its name
-----------------------------

    >>> node.get_child("RenderPass")

Get node from its path
----------------------

    >>> p.path_to_node('|RenderPass|Layer|Input1')


Iterate over render passes, render ayers and aovs
-------------------------------------------------

    >>> rp_iter = (n for n in p.nodes if n.type == 'RenderPass')
    >>> for rp in rp_iter:
    >>>     rl_iter = (n for n in rp.children if n.type == 'RenderLayer')
    >>>     for rl in rl_iter:
    >>>         aov_iter = (n for n in rp.children if n.type == 'LayerOut')
    >>>         for aov in aov_iter:
    >>>             print aov.path, aov.display_name

Iterate over every plug of a node
---------------------------------

    >>> for plug in node.plugs:
    >>>     print plug.path, plug.type
    >>>     if plug.input:  # does node plug have incoming plug?
    >>>         print plug.input.path, "->", plug.path
    >>>     else:  # no incoming plug? get it's value
    >>>         print plug.value
    >>>     # if this plug is connected to other plug, we print it
    >>>     for out_plug in plug.outputs:
    >>>         print plug.path, "->", out_plug.path

Get specified plug (from its `PlugName` attribute)
--------------------------------------------------

    >>> node.get_plug('NodePos')

Get node from it's path
-----------------------

    >>> rp = p.path_to_node('|RenderPass')
