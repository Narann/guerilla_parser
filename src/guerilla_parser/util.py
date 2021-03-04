import sys

from .exception import PathError


def dump(node, show_plugs=True, depth=0):
    """Recursive function to print node and children information.

    :param node: Node to dump with it's children.
    :type node: GuerillaNode
    :param show_plugs: Print attributes names and values if `True`.
    :type show_plugs: `bool`
    :param depth: Add four spaces * this number in the beginning of each.
    :type depth: `int`
    """
    hole = "  " * depth

    print("{hole}{node.name} ({node.type})".format(**locals()))

    if show_plugs:
        for plug in node.plugs:
            print("{hole}    .{plug.name} = {plug.value}".format(**locals()))

    for child in node.children:
        dump(child, show_plugs, depth + 1)


def path_name_to_name(path_name):
    """

    :param path_name:
    :return:
    """
    return path_name.replace("\\\\", "\\") \
                    .replace(r"\.", ".", ) \
                    .replace(r"\$", "$") \
                    .replace(r"\|", "|") \
                    .replace(r"\[", "[") \
                    .replace(r"\]", "]")


def name_to_path_name(name):
    """

    :param name:
    :return:
    """
    return name.replace("\\", "\\\\")\
               .replace(".", r"\.")\
               .replace("$", r"\$")\
               .replace("|", r"\|")\
               .replace("[", r"\[")\
               .replace("]", r"\]")


def aov_node(parser, rp_name, rl_name, aov_name):
    """Utility function to get an AOV from it's given info.

    AOV nodes can't be retrieved using a simple path like
    "|RenderPass|Layer|Beauty" and the AOV name ("Beauty" here) is not the
    node name but a plug value ("PlugName").

    This function try to provide an easy way to retrieve an AOV node based
    on predicted render passe and render layer names. So
    "|RenderPass|Layer|Beauty" will return the AOV node representing the
    "Beauty" AOV.

    :param parser: Guerilla parser.
    :type parser: GuerillaParser
    :param rp_name: Render pass name.
    :type rp_name: str
    :param rl_name: Render layer name.
    :type rl_name: str
    :param aov_name: AOV name.
    :type aov_name: str
    :return: AOV node matching given path.
    :rtype: GuerillaNode
    :raises PathError: If given info doesn't match any or more than one
    aov node.
    """
    # get render layer node
    rl = parser.path_to_node('|{rp_name}|{rl_name}'.format(**locals()))

    aov_nodes = []

    # and find aov based on its display name
    for aov_node in rl.children:
        if aov_node.display_name == aov_name:
            aov_nodes.append(aov_node)

    if len(aov_nodes) == 0:
        raise PathError(("Can't find AOV '{rp_name}', '{rl_name}', "
                         "'{aov_name}'").format(**locals()))
    elif len(aov_nodes) == 2:
        raise PathError(("More than one AOV found '{rp_name}', "
                         "'{rl_name}', '{aov_name}'").format(**locals()))
    else:
        assert len(aov_nodes) == 1, aov_nodes
        return aov_nodes[0]


if sys.version_info[0] == 3:
    def iteritems(d, **kw):
        return iter(d.items(**kw))

    def itervalues(d, **kw):
        return iter(d.values(**kw))

    def open_(path):
        import io
        return io.open(path, 'rt', encoding='iso-8859-1')
else:
    def iteritems(d, **kw):
        return d.iteritems(**kw)

    def itervalues(d, **kw):
        return d.itervalues(**kw)

    def open_(path):
        return open(path, 'rU')
