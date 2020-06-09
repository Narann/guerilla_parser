
class GuerillaPlug(object):
    """Class representing a parsed Guerilla plug.

    :ivar name: Plug name.
    :vartype name: str
    :ivar type: Plug type (often 'Plug').
    :vartype type: str
    :ivar parent: Parent plug's node.
    :vartype parent: GuerillaNode
    :ivar value: Plug value.
    :vartype value: bool|float|str
    :ivar org_value: Original parser plug value.
    :vartype org_value: str
    :ivar input: Plug input.
    :vartype input: GuerillaPlug
    :ivar outputs: Plug outputs.
    :vartype outputs: list[GuerillaPlug]
    """
    def __init__(self, name, type_, parent, value=None, flag=None,
                 org_value=None):
        """init plug

        :param name: Plug name.
        :type name: str
        :param type_: Plug type (often 'Plug').
        :type type_: str
        :param parent: Plug node parent.
        :type parent: GuerillaNode
        :param value: Plug value.
        :type value: bool|float|str
        :param org_value: Original parser plug value.
        :type org_value: str
        """
        assert isinstance(name, str), (type(name), name)
        assert isinstance(type_, str), (type(type_), type_)
        assert parent is not None, (type(parent), parent)

        self.name = name
        self.type = type_
        self.parent = parent
        self.value = value
        self.flag = flag
        self.org_value = org_value

        self.input = None

        self.outputs = []

        # add current plug to given parent plugs
        assert name not in self.parent.plug_dict, (name,
                                                   self.parent.plug_dict)

        self.parent.plug_dict[name] = self

    def __repr__(self):
        """

        :return:
        :rtype: str
        """
        return "{}('{name}', '{type}', '{parent.path}')".format(
            type(self).__name__, **vars(self))

    @property
    def path(self):
        """Full plug path.

        :return: Full plug path.
        :rtype: str
        """
        if self.parent.id == 1:
            parent_path = ""
        else:
            parent_path = self.parent.path
        return '{parent_path}.{self.name}'.format(**locals())
