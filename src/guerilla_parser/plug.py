
class GuerillaPlug(object):
    """class representing a parsed Guerilla plug

    :ivar name: plug name
    :type name: str
    :ivar type: plug type (often 'Plug')
    :type type: str
    :ivar parent: plug parent node
    :type parent: GuerillaNode
    :ivar value: plug value
    :type value: bool|float|str
    :ivar org_value: original parser plug value
    :type org_value: str
    :ivar input: plug input
    :type input: GuerillaPlug
    :ivar outputs: plug outputs
    :type outputs: list[GuerillaPlug]
    """
    def __init__(self, name, type_, parent, value=None, flag=None,
                 org_value=None):
        """init plug

        :param name: plug name
        :type name: str
        :param type_: plug type (often 'Plug')
        :type type_: str
        :param parent: plug node parent
        :type parent: `GuerillaNode`
        :param value: plug value
        :type value: bool|float|str
        :param org_value: original parser plug value
        :type org_value: str
        """
        assert isinstance(name, basestring), (type(name), name)
        assert isinstance(type_, basestring), (type(type_), type_)
        assert parent is not None, (type(parent), parent)

        self.name = name
        self.type = type_
        self.parent = parent
        self.value = value
        self.flag = flag
        self.org_value = org_value

        self.input = None

        self.outputs = []

        # add current node to given parent
        assert name not in self.parent.plug_dict, (name,
                                                   self.parent.plug_dict)

        self.parent.plug_dict[name] = self

    @property
    def path(self):
        """full plug path

        :return: full plug path
        :rtype: str
        """
        return '{self.parent.path}.{self.name}'.format(**locals())
