import math
import re

from .exception import PathError
from .node import GuerillaNode
from .plug import GuerillaPlug


# use to print missing implementation of python to lua value conversion
_print_missing_implementation = True


# guerilla class names inheriting from guerilla.Plug
plug_class_names = {'BakePlug',
                    'DynAttrPlug',
                    'ExpressionInput',
                    'ExpressionOutput',
                    'HostPlug',
                    'MeshPlug',
                    'Plug',
                    'UserPlug'}


class GuerillaParser(object):
    """Guerilla .gproject file parser

    :ivar objs: Guerilla "object" per id (parsed in "oid[<id>]")
    :type objs: dict[int, GuerillaNode|GuerillaPlug]
    :ivar diagnose: diagnose mode
    :type diagnose: bool
    """
    PY_TO_LUA_BOOL = {True: 'true',
                      False: 'false'}

    LUA_TO_PY_BOOL = {v: k for (k, v) in PY_TO_LUA_BOOL.iteritems()}

    # main line regex
    LINE_PARSE = re.compile(
        '\s*(oid\[(?P<oid>\d+)\]=)?'
        '(?P<cmd>\w+)'
        '\((?P<args>.*)\)\n')

    # per command argument regex
    CMD_CREATE_ARG_PARSE = re.compile(
        '"(?P<type>[a-zA-Z0-9]+)",'
        '"(?P<parent>[^,\n]*)",'
        '(("(?P<name>.+?)")|(?P<name_number>\d+?))?'
        '(?P<rest>.*)')

    CREATE_PLUG_REST_PARSE = re.compile(
        '^,(?P<flag>\d+),'
        '(?P<type>[a-zA-Z0-9.]+)( (?P<param>{.*}))?,'
        '(?P<value>.*)$')

    CMD_SET_ARG_PARSE = re.compile(
        '"\$(?P<id>\d+)(?P<path>[|:\w]+)?\.(?P<plug>\w+)",'
        '(?P<value>.+)')

    CMD_CONNECT_ARG_PARSE = re.compile(
        '"\$(?P<in_id>\d+)((?P<in_path>[|:\w]+)?\.(?P<in_plug>\w+))?",'
        '"\$(?P<out_id>\d+)((?P<out_path>[|:\w]+)?\.(?P<out_plug>\w+))?"')

    CMD_DEPEND_ARG_PARSE = re.compile(
        '"\$(?P<in_id>\d+)((?P<in_path>[|:\w]+)?\.(?P<in_plug>\w+))?",'
        '"\$(?P<out_id>\d+)((?P<out_path>[|:\w]+)?\.(?P<out_plug>\w+))?"')

    PARENT_PARSE = re.compile("\$(?P<id>\d+)(?P<path>[|:\w]+)?")

    def __init__(self, content, diagnose=False):

        super(GuerillaParser, self).__init__()

        self.__org_content = content
        """original content of the gproject, never modified
        :type: str"""

        self.__mod_content = None
        """modified content of the gproject (modified by set_plug_value())
        :type: str"""

        self.__doc_format_rev = None

        self.objs = {}

        self.__implicit_nodes = set()
        """:type: set[GuerillaNode]"""

        self.diagnose = diagnose

        self.__parse_nodes()

    def __eq__(self, other):
        """compare the content of this instance with the content of an other
        parser.

        :param other: other parser instance to compare content of
        :type other: `Base`
        :return: True if both parser instance have same modified content
        :rtype: `bool`
        """
        if self is other:
            return True

        return self.__mod_content == other.__mod_content

    @classmethod
    def from_file(cls, path, *args, **kwords):
        """construct parser reading given file `path` content

        :param path: .gproject file path
        :type path: str
        :return: parser filled with content of given `path`
        :rtype: `GuerillaParser`
        """
        with open(path, 'r') as f:
            content = f.read()

        return cls(content, *args, **kwords)

    @property
    def has_changed(self):
        """return if current parsed file has changed

        :return: True if both parser instance have same modified content
        :rtype: `bool`
        """
        # no modified content mean we didn't tried to modified it
        if self.__mod_content is None:
            return False
        else:
            return self.__org_content != self.__mod_content

    @property
    def modified_content(self):
        """modified parsed gproject content

        :return: modified parsed gproject content
        :rtype: str
        """
        if self.__mod_content is None:
            return self.__org_content

        else:
            return self.__mod_content

    @property
    def original_content(self):
        """original (unmodified) parsed gproject content

        :return: original (unmodified) parsed gproject content
        :rtype: str
        """
        return self.__org_content

    def write(self, path):
        """write modified content to given file `path`

        :param path: .gproject file path
        :type path: str
        """
        with open(path, 'w') as f:
            f.write(self.modified_content)

    @property
    def root(self):
        """root node (top node of the parsed file)

        :return: root node
        :rtype: `GuerillaNode`
        """
        return self.objs[1]

    @property
    def doc_format_rev(self):
        """document format revision

        :return: document format revision
        :rtype: `int`
        :raise: `AttributeError` if no document format revision is present in
        file
        """
        if self.__doc_format_rev is None:
            raise AttributeError("Missing doc format revision")

        return self.__doc_format_rev

    @property
    def nodes(self):
        """iterate over nodes of the gproject file (except root node)

        :return: generator of nodes of the gproject file
        :rtype: collections.iterator[GuerillaNode]
        """
        for obj in self.objs.itervalues():

            if obj.type in plug_class_names:  # plug node detected
                continue

            if obj.id == 1:  # root node detected
                continue

            yield obj

    def __parse_nodes(self):
        """parse commands in Guerilla file
        """
        self.objs = {}

        for match in self.LINE_PARSE.finditer(self.original_content):

            cmd = match.group('cmd')
            args = match.group('args')

            if cmd in 'docformatrevision':

                self.__doc_format_rev = int(args)

            elif cmd in ('create', 'createnotref'):
                ###############################################################
                # create
                ###############################################################
                oid = int(match.group('oid'))

                match_arg = self.CMD_CREATE_ARG_PARSE.match(args)

                type_ = match_arg.group('type')
                parent = match_arg.group('parent')
                name = match_arg.group('name')

                if name is None:
                    name = match_arg.group('name_number')

                if parent in (r'\"\"', ''):  # GADocument or root
                    parent = None
                else:
                    parent_match_grp = self.PARENT_PARSE.match(parent)
                    parent_id = int(parent_match_grp.group('id'))
                    parent_path = parent_match_grp.group('path')

                    parent = self.objs[parent_id]

                    if parent_path:
                        node = self.__create_and_get_implicit_node(parent,
                                                                   parent_path)

                if type_ in plug_class_names:
                    ###########################################################
                    # Plugs
                    ###########################################################
                    rest = match_arg.group('rest')

                    match_rest = self.CREATE_PLUG_REST_PARSE.match(rest)

                    flag = int(match_rest.group('flag'))
                    plug_type = match_rest.group('type')
                    param = match_rest.group('param')
                    value = match_rest.group('value')

                    # convert value to python type
                    if plug_type == 'types.string':
                        value = str(value)
                    elif plug_type == 'types.int':
                        value = int(value)
                    elif plug_type in {'types.float', 'types.angle'}:
                        value = float(value)
                    elif plug_type in 'types.color':
                        # "{1,0.5,0.5}" to [1,0.5,0.5]
                        value = eval(value.replace('{', '[').replace('}', ']'))

                    assert value is not None

                    # convert param to python dict
                    # {slidermax=4,min=0} to {'slidermax': 4, 'min': 0}
                    if param == '{}' or param is None:
                        param = {}
                    else:
                        param = self.__lua_dict_to_python(param)

                    plug = GuerillaPlug(name, type_, parent, value, flag)

                    assert oid not in self.objs, oid

                    self.objs[oid] = plug

                else:
                    ###########################################################
                    # Nodes
                    ###########################################################
                    node = GuerillaNode(oid, name, type_, parent)

                    assert oid not in self.objs, oid

                    self.objs[oid] = node

            elif cmd == 'set':
                ###############################################################
                # set
                ###############################################################
                match_arg = self.CMD_SET_ARG_PARSE.match(args)

                oid = int(match_arg.group('id'))
                path = match_arg.group('path')
                plug_name = match_arg.group('plug')
                org_value = match_arg.group('value')

                value = self.lua_to_py_value(org_value)

                node = self.objs[oid]

                if path:
                    node = self.__create_and_get_implicit_node(node, path)

                GuerillaPlug(plug_name, 'Plug', node, value,
                             org_value=org_value)

                if self.diagnose:
                    print ('Set: {node.path}.{plug_name} -> '
                           '{value}').format(**locals())

            elif cmd == 'connect':
                ###############################################################
                # connect
                ###############################################################
                match_arg = self.CMD_CONNECT_ARG_PARSE.match(args)

                in_oid = int(match_arg.group('in_id'))
                in_path = match_arg.group('in_path')
                in_plug_name = match_arg.group('in_plug')

                out_oid = int(match_arg.group('out_id'))
                out_path = match_arg.group('out_path')
                out_plug_name = match_arg.group('out_plug')

                in_node = self.objs[in_oid]
                out_node = self.objs[out_oid]

                if in_path:
                    in_node = self.__create_and_get_implicit_node(in_node,
                                                                  in_path)

                if out_path:
                    out_node = self.__create_and_get_implicit_node(out_node,
                                                                   out_path)

                if not out_path and not out_plug_name:
                    # output is in the form "$64", an expression node
                    print (out_node.type, out_node.path, '->',
                           in_node.type, in_node.path, in_plug_name)
                    # TODO: support when output is $64-like
                    continue

                # document is referencing a plug by its id, this mean a plug
                # node has been created in the gproject so we "offset" the
                # hierarchy to be consistent with the rest.
                if in_plug_name is None:
                    in_plug_name = in_node.name
                    in_node = in_node.parent

                if out_plug_name is None:
                    out_plug_name = out_node.name
                    out_node = out_node.parent

                assert in_plug_name is not None
                assert out_plug_name is not None

                try:
                    in_plug = in_node.plug_dict[in_plug_name]
                except KeyError:
                    in_plug = GuerillaPlug(in_plug_name, 'Plug', in_node)

                try:
                    out_plug = out_node.plug_dict[out_plug_name]
                except KeyError:
                    out_plug = GuerillaPlug(out_plug_name, 'Plug', out_node)

                assert out_plug.name not in [p.name for p in out_plug.outputs]
                assert in_plug.input is None, in_plug_name

                # p1.out -> p2.in
                out_plug.outputs.append(in_plug)
                in_plug.input = out_plug

                if self.diagnose:
                    print ('Connect: {out_node.path}.{out_plug_name} -> '
                           '{in_node.path}.{in_plug_name}').format(**locals())

            elif cmd == 'depend':
                ###############################################################
                # depend
                ###############################################################
                match_arg = self.CMD_DEPEND_ARG_PARSE.match(args)

                in_oid = int(match_arg.group('in_id'))
                in_path = match_arg.group('in_path')
                in_plug_name = match_arg.group('in_plug')

                out_oid = int(match_arg.group('out_id'))
                out_path = match_arg.group('out_path')
                out_plug_name = match_arg.group('out_plug')

                in_node = self.objs[in_oid]
                out_node = self.objs[out_oid]

                if in_path:
                    in_node = self.__create_and_get_implicit_node(in_node,
                                                                  in_path)

                if out_path:
                    out_node = self.__create_and_get_implicit_node(out_node,
                                                                   out_path)

                if self.diagnose:
                    print ('Depend: {out_node.path}.{out_plug_name} -> '
                           '{in_node.path}.{in_plug_name}').format(**locals())

                # TODO: For now, dependencies are not supported

            else:
                print "Unknown command '{cmd}'".format(**locals())

    def __create_and_get_implicit_node(self, start_node, path):
        """macro to recursively create implicit nodes from given `path`
        starting from given `start_node`.

        if a direct path is present (instead of a direct node id)
        this mean we have an "implicit" node (aka: not created by
        the gproject itself).

        $36|Frustum -> $36 is `start_node` and "|Fustum" is `path`, will create
        a node from "UNKNOWN" type named "Frustrum" with node with id 36 as
        parent.

        :param start_node:
        :param path:
        :return:
        """
        # generate the whole path of the implicit node
        implicit_node_path = start_node.path + path

        # search if implicit node already exists
        for implicit_node in self.__implicit_nodes:

            if implicit_node.path == implicit_node_path:

                return implicit_node

        # no implicit node found? create it!
        cur_parent = start_node

        for implicit_node_name in path.split('|')[1:]:

            implicit_node = GuerillaNode(-1, implicit_node_name, 'UNKNOWN',
                                         cur_parent)

            self.__implicit_nodes.add(implicit_node)

            cur_parent = implicit_node

        return cur_parent

    @staticmethod
    def __lua_dict_to_python(lua_dict_str):
        """convert given lua table representation to python dict

        "{foo=1,bar=2}" -> {'foo': 1, 'bar': 2}

        :param lua_dict_str: lua table representation to convert in python
        :type lua_dict_str: str
        :return: lua table representation converted to python dict
        :rtype: `dict`
        """
        # reformat
        lua_dict_str = re.sub('([a-zA-Z0-9_-]+)=([a-zA-Z0-9_-]+)',
                              '\'\g<1>\':\g<2>',
                              lua_dict_str)
        # and eval as python expression
        return eval(lua_dict_str.replace('=', ':'))

    @staticmethod
    def lua_to_py_value(raw_str):
        """convert given guerilla lua `raw_str` value expression to python

        :param raw_str: raw string representing lua value to convert to python
        :type raw_str: str
        :return: value converted from lua to python
        :rtype: bool|float|list[float]|str
        """
        if raw_str == 'true':

            return True

        elif raw_str == 'false':

            return False

        elif raw_str.startswith('"') and raw_str.endswith('"'):

            # lua string
            return str(raw_str[1:-1].replace(r'\010', '\n')
                                    .replace(r'\009', '\t')
                                    .replace(r'\"', '"')
                                    .replace('\\\\', '\\'))

        elif re.match('[0-9.-]+', raw_str):

            # we don't support int as "1" can be a float but lua hide
            # fractional part
            return float(raw_str)

        elif re.match('{[0-9.,-]+}', raw_str):

            # float table: {127.5,-80, ...}
            # eg. NodePos, PreClamp, PostClamp, Value, etc.
            return [float(v) for v in raw_str[1:-1].split(',')]

            # TODO: "matrix.create" and "transform.create" are not supported yet
            # because we loose the matrix.create and transform.create
            # information when setting plug values
            '''elif raw_str.startswith('matrix.create{'):
    
                content = raw_str[len('matrix.create{'):-1]
                return [float(v) for v in content.split(',')]
    
            elif raw_str.startswith('transform.create{'):
    
                content = raw_str[len('transform.create{'):-1]
                return [float(v) for v in content.split(',')]'''

        elif raw_str in ('transform.Id', 'matrix.Id'):

            # those are Guerilla shortcut to identity matrix
            return raw_str

        if _print_missing_implementation:
            print ("Missing lua to python conversion "
                   "'{raw_str}'").format(**locals())

        return raw_str

    @staticmethod
    def __is_float_intable(value):
        """return if given float `value` is possible to convert to int without
        lost

        4.2 returns False, 4.0 return True

        :param value:
        :return: true if given `value` is convertible in `int` without
        precision loss.
        """
        return (value - math.floor(value)) == 0.0

    @classmethod
    def py_to_lua_value(cls, value):
        """convert given python `value` to guerilla lua string representation

        :param value: python value to convert in lua string representation
        :type value: bool|int|float|string|list[float]|dict
        :return: value converted from python to lua representation
        :rtype: str
        """
        if type(value) is bool:

            return cls.PY_TO_LUA_BOOL[value]

        elif type(value) is int:

            return str(value)

        elif type(value) is float:

            # transform 1000.0 to "1000"
            if cls.__is_float_intable(value):
                return str(int(value))
            else:
                return str(value)

        elif type(value) is str:

            if value in ('transform.Id', 'matrix.Id'):
                return value
            else:
                value = value.replace('\\', '\\\\')\
                             .replace('"', '\\"')\
                             .replace('\n', '\\010')\
                             .replace('\t', '\\009')
                return "\"{value}\"".format(**locals())

        elif type(value) is list:

            res = ['{']

            for v in value:

                if cls.__is_float_intable(v):
                    v = int(v)

                res += [str(v), ',']

            res.pop()  # remove latest ","

            res.append('}')

            return "".join(res)

        else:
            print ("Missing python to lua conversion "
                   "'{value}'").format(**locals())

        return value

    def path_to_node(self, path):
        """find and return node at given `path`

        "|foo|bar|bee" will return "bee" node.
        "$65|bar|bee" will return "bee" node.

        :param path: path to get node of
        :type path: str
        :return: node found from given `path`
        :rtype: `GuerillaNode`
        :raise: `PathError` if root node can't be found
        :raise: `PathError` if path contain unreachable nodes
        """
        # find first node of the path
        if path.startswith('|'):  # "|foo|bar|bee" like
            cur_node = self.root  # absolute path

        elif path.startswith('$'):  # "$65|bar|bee"
            oid = int(path[1:path.find('|')])  # id "$65|" -> 65
            cur_node = self.objs[oid]

        else:
            raise PathError("Can't find root '{path}'".format(**locals()))

        # find node for each name in path:
        # "|foo|bar|bee" -> look for "foo" in document children, then "bar" in
        # "foo" children, etc.
        for node_name in re.split(r'(?<!\\)\|', path)[1:]:

            # and we replace "\|" by "|" to find the node
            node_name = node_name.replace('\\|', '|')

            if not node_name:
                raise PathError("Empty name '{path}'".format(**locals()))

            for node in cur_node.children:

                if node.name == node_name:
                    cur_node = node
                    break  # we've found it! let's move to the next node

            else:  # no break?
                raise PathError("Can't find node '{path}'".format(**locals()))

        return cur_node

    @staticmethod
    def node_to_id_path(node):
        """return the shortest id path for given node:

        "$60", "$37|Frustum", etc.

        :param node:
        :return:
        """
        path = []

        cur_node = node

        # move to parent until we find a node with a valid id
        while cur_node.id == -1:

            path.append(cur_node.name)

            cur_node = cur_node.parent

        path.append("${cur_node.id}".format(**locals()))

        return '|'.join(reversed(path))

    @staticmethod
    def __escape_str_for_regex(value):
        """escape given string `value` to make it parsed in regex

        :param value: string to espace for regex
        :type value: str
        :return: escaped string
        """
        return value.replace('\\', '\\\\')\
                    .replace('^', '\\^')\
                    .replace('$', '\\$')\
                    .replace('{', '\\{')\
                    .replace('}', '\\}')\
                    .replace('[', '\\[')\
                    .replace(']', '\\]')\
                    .replace('(', '\\(')\
                    .replace(')', '\\)')\
                    .replace('.', '\\.')\
                    .replace('*', '\\*')\
                    .replace('+', '\\+')\
                    .replace('?', '\\?')\
                    .replace('|', '\\|')\
                    .replace('<', '\\<')\
                    .replace('>', '\\>')\
                    .replace('-', '\\-')\
                    .replace('&', '\\&')

    def set_plug_value(self, plug_values):
        """

        :param plug_values:
        :return:
        """
        # this list will be filled with "set(attr, value)" regex so we can
        # create a "set(attr1, value1)|set(attr2, value2)|set(attr3, value3)"
        # string that will be used to apply regex and set values only once
        regex_list = []

        # plug path (eg. "$60.Color"): value to set (eg. "{1,0,0}")
        # this variable is used in the replace_func() function to find the
        # value to set based on plug path
        plug_value_list = {}

        for plug, value in plug_values:

            old_lua_value = self.py_to_lua_value(plug.value)
            new_lua_value = self.py_to_lua_value(value)

            path = self.node_to_id_path(plug.parent)

            plug_path = "{path}.{plug.name}".format(**locals())

            plug_value_list[plug_path] = new_lua_value

            # regex is separated in three groups:
            # set(" | $3.AxisColor | ",{0,0,0,1})
            # we need the second
            # the job of the replace function (outside the loop) is to
            # recreated the latest group
            regex_str = ['(\s*set\(")(',
                         plug_path.replace('$', '\$').replace('.', '\.'),
                         ')(",',
                         self.__escape_str_for_regex(old_lua_value),
                         '\)\n)']

            regex_list.append(''.join(regex_str))

            # and of course, don't forget to set the value on the plug object
            plug.value = value

        # the "set(attr1, value1)|set(attr2, value2)|set(attr3, value3)" string
        set_plug_regex = re.compile('|'.join(regex_list))

        # the replace function point is to recreated the parsed line
        def replace_func(match_grp):

            set_prefix = match_grp.group(1)  # 'set("'
            plug_path = match_grp.group(2)  # '$60.Color'

            new_lua_value = plug_value_list[plug_path]  # "{1,1,1}"

            return '{0}{1}",{2})\n'.format(set_prefix,
                                           plug_path,
                                           new_lua_value)

        if not self.__mod_content:
            self.__mod_content = self.__org_content

        self.__mod_content = set_plug_regex.sub(replace_func,
                                                self.__mod_content)
