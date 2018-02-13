import guerilla_parser as grl_parser


def dump(node, show_plugs=True, depth=0):
    """recursive function to print node and children information

    :param node: node to dump with it's children
    :type node: `GuerillaNode`
    :param show_plugs: print attributes names and values if `True`
    :type show_plugs: `bool`
    :param depth: add four spaces * this number in the beginning of each
    :type depth: `int`
    """
    hole = "  " * depth

    print "{hole}{node.name} ({node.type})".format(**locals())

    if show_plugs:
        for plug in node.plugs:
            print "{hole}    .{plug.name} = {plug.value}".format(**locals())

    for child in node.children:
        dump(child, show_plugs, depth + 1)


def aov_node(parser, rp_name, rl_name, aov_name):
    """utility function to get an aov from it's given info

    aov nodes can't be retrieved using a simple path like
    "|RenderPass|Layer|Beauty" and the aov name ("Beauty" here) is not the
    node name but a plug value ("PlugName").

    this function try to provide an easy way to retrieve an aov node based
    on predicted render passe and render layer names. So
    "|RenderPass|Layer|Beauty" will return the aov node representing the
    "Beauty" aov.

    :param parser: guerilla parser
    :type parser: `GuerillaParser`
    :param rp_name: render pass name
    :type rp_name: str
    :param rl_name: render layer name
    :type rl_name: str
    :param aov_name: aov name
    :type aov_name: str
    :return: aov node matching given path
    :rtype: GuerillaNode
    :raise: PathError if given info doesn't match any or more than one
    aov node
    """
    # get render layer node
    rl = parser.path_to_node('|{rp_name}|{rl_name}'.format(**locals()))

    aov_nodes = []

    # and find aov based on its display name
    for aov_node in rl.children:
        if aov_node.display_name == aov_name:
            aov_nodes.append(aov_node)

    if len(aov_nodes) == 0:
        raise grl_parser.PathError(("Can't find aov '{rp_name}', '{rl_name}', "
                                    "'{aov_name}'").format(**locals()))
    elif len(aov_nodes) == 2:
        raise grl_parser.PathError(
            ("More than one aov found '{rp_name}', "
             "'{rl_name}', '{aov_name}'").format(**locals()))
    else:
        assert len(aov_nodes) == 1, aov_nodes
        return aov_nodes[0]
