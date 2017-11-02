from .exception import ChildError, PathError


class GuerillaNode(object):
    """Class representing a parsed Guerilla node.

    :ivar id: Node id (value in parsed expression ``oid[<id>]=``).
    :type id: int
    :ivar name: Node name.
    :type name: str
    :ivar type: Node type.
    :type type: str
    :ivar parent: Node parent.
    :type parent: :class:`GuerillaNode`
    :ivar children: Node children.
    :type children: list[:class:`GuerillaNode`]
    :ivar plug_dict: Node plug by name.
    :type plug_dict: dict[str, :class:`GuerillaPlug`]
    """
    def __init__(self, id_, name, type_, parent=None):
        """Init node.

        :param id_: Value in parsed expression ``oid[<id>]=``.
        :type id_: int
        :param name: Node name.
        :type name: str
        :param type_: Node type.
        :type type_: str
        :param parent: Node parent.
        :type parent: :class:`GuerillaNode`
        """
        self.id = id_
        self.name = name
        self.type = type_
        self.parent = parent

        self.children = []

        self.plug_dict = {}

        # add current node to given parent
        if self.parent is not None:
            self.parent.children.append(self)

    @property
    def path(self):
        """Full node path.

        :return: Full node path.
        :rtype: str
        :raise PathError: When node is root.
        """
        if self.id == 1:
            raise PathError("No path for root node")

        # we recursively move from current node to parent node storing node
        # name
        path = []
        node = self
        while node is not None:
            # some nodes can be named "foo|bar" so we have to escape "|" from
            # their names.
            path.append(node.name.replace("|", "\\|"))
            node = node.parent

        # the root should never appear in the path (but we replace it to an
        # empty string to keep the "|" at the beginning of the returned path
        path[-1] = ""

        return '|'.join(reversed(path))

    @property
    def display_name(self):
        """Node name shown in UI.

        Some nodes (render graph plugs, aovs, etc.) have a distinction between
        internal name and UI display name. This property return UI name (aka
        PlugName attribute) if available.

        :return: Node name shown in UI.
        :rtype: str
        """
        try:
            return self.plug_dict['PlugName'].value
        except KeyError:
            return self.name

    @property
    def plugs(self):
        """Iterator over node plugs.

        :return: Iterator over node plugs.
        :rtype: collection.iterator[:class:`GuerillaPlug`]
        """
        for plug in self.plug_dict.itervalues():
            yield plug

    def get_child(self, name):
        """Return child node with given `name`.

        :param name: Name of the child node to return.
        :return: Child node with given `name`.
        :rtype: :class:`GuerillaNode`
        :raise KeyError: When no child node with given `name` is found.
        """
        for n in self.children:
            if n.name == name:
                return n

        raise ChildError("Can't find child node '{name}'".format(**locals()))

    def get_plug(self, name):
        """Return plug with given `name`.

        :param name: Name of the plug to return.
        :return: Plug with given `name`.
        :rtype: :class:`GuerillaPlug`
        :raise KeyError: When no plug with given name is found
        """
        return self.plug_dict[name]
