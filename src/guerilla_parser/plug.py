
class GuerillaPlug(object):
    """class representing a parsed Guerilla plug"""

    def __init__(self, name, type_, parent, value=None, flag=None,
                 org_value=None):
        """init plug

        :param name: plug name
        :type name: `str`
        :param type_: plug type (often 'Plug')
        :type type_: `str`
        :param parent: plug node parent
        :type parent: `GuerillaNode`
        :param value: plug value
        :type value: `bool`|`float`|`str`
        :param org_value: original parser plug value
        :type org_value: `str`
        """
        self.name = name
        self.type = type_
        self.parent = parent
        self.value = value
        self.flag = flag
        self.org_value = org_value

        self.input = None
        """:type: GuerillaPlug"""

        self.outputs = []
        """:type: list[GuerillaPlug]"""

        # add current node to given parent
        if self.parent is not None:
            self.parent.plug_dict[name] = self

    @property
    def path(self):
        """full plug path

        :return: full plug path
        :rtype: `str`
        """
        return '{self.parent.path}.{self.name}'.format(**locals())
