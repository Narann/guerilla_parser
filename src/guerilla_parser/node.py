from exception import ChildError, PathError


class GuerillaNode(object):
    """class representing a parsed Guerilla node"""

    def __init__(self, id_, name, type_, parent=None):
        """init node

        :param id_: value in "oid[<id>]="
        :type id_: `int`
        :param name: node name
        :type name: `str`
        :param type_: node type
        :type type_: `str`
        :param parent: node parent
        :type parent: `GuerillaNode`
        """
        self.id = id_
        self.name = name
        self.type = type_
        self.parent = parent

        self.children = []
        """:type: list[GuerillaNode]"""

        self.plug_dict = {}
        """:type: dict[str, GuerillaPlug]"""

        # add current node to given parent
        if self.parent is not None:
            self.parent.children.append(self)

    @property
    def path(self):
        """full node path

        :return: full node path
        :rtype: `str`
        """
        if self.id == 1:
            raise PathError("No path for root node")

        # we recursively move from current node to parent node storing node
        # name
        path = []
        node = self
        while node is not None:
            path.append(node.name)
            node = node.parent

        # the root should never appear in the path (but we replace it to an
        # empty string to keep the "|" at the beginning of the returned path
        path[-1] = ""

        return '|'.join(reversed(path))

    @property
    def display_name(self):
        """node name shown in UI

        Some nodes (render graph plugs, aovs, etc.) have a distinction between
        internal name and UI display name. This property return UI name (aka
        PlugName attribute) if available.

        :return: node name shown in UI
        :rtype: `str`
        """
        try:
            return self.plug_dict['PlugName'].value
        except KeyError:
            return self.name

    @property
    def plugs(self):
        """iterator over node plugs

        :return: iterator over node plugs
        :rtype: `collection.iterator[GuerillaPlug]`
        """
        for plug in self.plug_dict.itervalues():
            yield plug

    def get_child(self, name):
        """return child node with given `name`

        :param name: name of the child node to return
        :return: child node with given `name`
        :rtype: `GuerillaNode`
        :raise: `KeyError` if no child node with given `name` is found
        """
        for n in self.children:
            if n.name == name:
                return n

        raise ChildError("Can't find child node '{name}'".format(**locals()))

    def get_plug(self, name):
        """return plug with given `name`

        :param name: name of the plug to return
        :return: plug with given `name`
        :rtype: `GuerillaPlug`
        :raise: `KeyError` if no plug with given name is found
        """
        return self.plug_dict[name]