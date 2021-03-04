from .exception import ChildError, PathError

from .util import itervalues
from .util import name_to_path_name


class GuerillaNode(object):
    """Class representing a parsed Guerilla node.

    :ivar id: Node id (value in parsed expression ``oid[<id>]=``).
    :vartype id: int
    :ivar type: Node type.
    :vartype type: str
    :ivar parent: Node parent.
    :vartype parent: GuerillaNode
    :ivar children: Node children.
    :vartype children: list[GuerillaNode]
    :ivar plug_dict: Node plug by name.
    :vartype plug_dict: dict[str, GuerillaPlug]
    """
    def __init__(self, id_, name, type_, parent=None):
        """Init node.

        :param id_: Value in parsed expression ``oid[<id>]=``.
        :type id_: int
        :param name: Node name.
        :type name: (str or int)
        :param type_: Node type.
        :type type_: str
        :param parent: Node parent.
        :type parent: GuerillaNode
        """
        assert isinstance(id_, int), (type(id_), id_)
        assert isinstance(name, (str, int)), (type(name), name)
        assert isinstance(type_, str), (type(type_), type_)
        assert len(type_), (len(type_), type_)

        self.id = id_
        self.__name = name
        self.type = type_
        self.parent = parent

        self.children = []

        self.plug_dict = {}

        # add current node to given parent
        if self.parent is not None:
            self.parent.children.append(self)

        # cache path for performance purpose. __create_and_get_implicit_node()
        # do intensive GuerillaNode.path property call so we cache path once
        # we have generated once
        self.__path_cache = None

        # for path, name with number are exposed with bracket:
        # 0 -> '[0]'
        # as we use this value a lot in path property, we cache it here.
        if isinstance(self.name, int):
            self._name_for_path = '[{}]'.format(self.name)
        else:
            self._name_for_path = name_to_path_name(self.name)

    def __repr__(self):
        """

        :return:
        :rtype: str
        """
        name = "'{}'".format(self.name) if isinstance(self.name, str)\
            else self.name

        return "{}({}, {}, '{}')".format(type(self).__name__, self.id, name,
                                         self.type)

    @property
    def name(self):
        """Node name.

        :return: Node name.
        :rtype: (str, int)
        """
        return self.__name

    @name.setter
    def name(self, value):
        """Set node name.

        :param value: New node name.
        """
        self.__name = value
        self.__path_cache = None  # clean path cache as we just renamed node

    @property
    def path(self):
        """Full node path.

        :return: Full node path.
        :rtype: str
        :raise PathError: When node is root.
        """
        if self.id == 1:
            raise PathError("No path for root node")

        if self.__path_cache is None:

            # we recursively move from current node to parent node storing node
            # name
            path = []
            node = self
            while node is not None:

                # some nodes can be named "foo|bar" so we have to escape "|"
                # from their names.
                path.append(node._name_for_path)
                node = node.parent

            # the root should never appear in the path (but we replace it to an
            # empty string to keep the "|" at the beginning of the returned path
            path[-1] = ""

            self.__path_cache = '|'.join(reversed(path))

        return self.__path_cache

    @property
    def display_name(self):
        """Node name shown in UI.

        Some nodes (render graph plugs, AOVs, etc.) have a distinction between
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
        :rtype: collection.iterator[GuerillaPlug]
        """
        for plug in itervalues(self.plug_dict):
            yield plug

    def get_child(self, name):
        """Return child node with given `name`.

        :param name: Name of the child node to return.
        :return: Child node with given `name`.
        :rtype: GuerillaNode
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
        :rtype: GuerillaPlug
        :raise KeyError: When no plug with given name is found
        """
        return self.plug_dict[name]
