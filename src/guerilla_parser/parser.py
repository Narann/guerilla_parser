# -*- coding: utf-8 -*-
from __future__ import print_function

import math
import re

from .exception import PathError
from .node import GuerillaNode
from .plug import GuerillaPlug

from .util import iteritems
from .util import open_


# use to print missing implementation of python to lua value conversion
_print_missing_implementation = False
_print_unknown_command = False
_print_expression_node_connection = False


# guerilla class names inheriting from guerilla.Plug
plug_class_names = {'BakePlug',
                    'DynAttrPlug',
                    'ExpressionInput',
                    'ExpressionOutput',
                    'HostPlug',
                    'MeshPlug',
                    'Plug',
                    'UserPlug',
                    'HSetPlug',
                    'HVisiblePlug',
                    'HMattePlug',
                    'SceneGraphNodePropsPlug',
                    'SceneGraphNodeRenderPropsPlug',
                    'AttributePlug',
                    'AttributeShaderPlug'}

# floating value regex "4.64"
_FLOAT_PARSE = re.compile('^[0-9.-]+$')

# float table {127.5,-80, ...}
_FLOAT_TABLE_PARSE = re.compile('^{[0-9.,-]+}$')


class GuerillaParser(object):
    """Guerilla .gproject file parser.

    :ivar objs: Guerilla "object" per id (parsed in ``oid[<id>]``).
    :vartype objs: dict[int, GuerillaNode|GuerillaPlug]
    :ivar diagnose: Diagnose mode.
    :vartype diagnose: bool
    """
    _PY_TO_LUA_BOOL = {True: 'true',
                       False: 'false'}

    _LUA_TO_PY_BOOL = {v: k for (k, v) in iteritems(_PY_TO_LUA_BOOL)}

    # main line regex
    _LINE_PARSE = re.compile(
        r'\s*(oid\[(?P<oid>\d+)\]=)?'
        r'(?P<cmd>\w+)'
        r'\((?P<args>.*)\)\n')

    # per command argument regex
    _CMD_CREATE_ARG_PARSE = re.compile(
        r'"(?P<type>[a-zA-Z0-9]+)",'
        r'"(?P<parent>(\\"|[^"])*)",'
        r'(("(?P<name>(\\"|[^"])*)")|(?P<name_number>-?\d+))'
        r'(?P<rest>.*)')

    _CREATE_REF_REST_PARSE = re.compile(
        r'^,"(?P<path>(\\"|[^"])+)",(true|false),(true|false),'
        r'(?P<param>({.*}|nil)),(true|false)$')

    _CREATE_PLUG_REST_PARSE = re.compile(
        r'^,(?P<flag>\d+),'
        r'(?P<type>[a-zA-Z0-9.]+)( (?P<param>{.*}))?,'
        r'(?P<value>.*)$')

    _CMD_SET_ARG_PARSE = re.compile(
        r'"\$(?P<id>\d+)(?P<path>(\\"|[^"])+)?\.(?P<plug>\w+)",'
        r'(?P<value>.+)', re.UNICODE)

    _CMD_CONNECT_ARG_PARSE = re.compile(
        r'"\$(?P<in_id>\d+)((?P<in_path>(\\"|[^"])+)?\.(?P<in_plug>\w+))?",'
        r'"\$(?P<out_id>\d+)((?P<out_path>(\\"|[^"])+)?\.(?P<out_plug>\w+))?"')

    _CMD_DEPEND_ARG_PARSE = re.compile(
        r'"\$(?P<in_id>\d+)((?P<in_path>(\\"|[^"])+)?\.(?P<in_plug>\w+))?",'
        r'"\$(?P<out_id>\d+)((?P<out_path>(\\"|[^"])+)?\.(?P<out_plug>\w+))?"')

    _PARENT_PARSE = re.compile(r'\$(?P<id>\d+)(?P<path>(\\"|[^"])+)?')

    def __init__(self, content, diagnose=False):
        """Init the parser.

        :param content: Raw Guerilla file content to parse.
        :type content: str
        :param diagnose: Will print some diagnostic information if True.
        :type diagnose: bool
        """
        super(GuerillaParser, self).__init__()

        # original content of the gproject, never modified
        self.__org_content = content  # :type: str

        # modified content of the gproject (modified by set_plug_value())
        self.__mod_content = None  # :type: str

        self.__doc_format_rev = None

        self.objs = {}

        self._implicit_nodes = []  # :type: list[GuerillaNode]

        self.diagnose = diagnose

        # __create_and_get_implicit_node() do a huge amount of calls to
        # GuerillaNode.path property, we have to cache its result for
        # performance purpose.
        # implicit nodes are "$44|foo|bar"
        # key is (source node, path) where source node is the GuerillaNode
        # representing $44 and path is "|foo|bar".
        self.__implicit_node_cache = {}

        self.__parse_nodes()

    def __eq__(self, other):
        """Compare the content of this instance with the content of an other
        parser.

        :param other: Other parser instance to compare content from.
        :type other: GuerillaParser
        :return: True if both parser instance have same modified content.
        :rtype: bool
        """
        if self is other:
            return True

        return self.__mod_content == other.__mod_content

    @classmethod
    def from_file(cls, path, *args, **kwords):
        """Construct parser reading given file `path` content.

        This is the main method to use if you want to use the parser.

        :param path: Path of the Guerilla file to parse.
        :type path: str
        :return: Parser filled with content of given `path`.
        :rtype: GuerillaParser
        """
        with open_(path) as f:
            content = f.read()

        return cls(content, *args, **kwords)

    @property
    def has_changed(self):
        """Return if current parsed file has changed.

        A parsed file can be changed using :meth:`set_plug_value()` method.

        :return: True if both parser instance have same modified content.
        :rtype: bool
        """
        # no modified content mean we didn't tried to modified it
        if self.__mod_content is None:
            return False
        else:
            return self.__org_content != self.__mod_content

    @property
    def modified_content(self):
        """Modified parsed Guerilla file content.

        A parsed file can be changed using :meth:`set_plug_value()` method.

        :return: Modified parsed Guerilla file content.
        :rtype: str
        """
        if self.__mod_content is None:
            return self.__org_content

        else:
            return self.__mod_content

    @property
    def original_content(self):
        """Original (unmodified) parsed Guerilla file content.

        :return: Original (unmodified) parsed Guerilla file content.
        :rtype: str
        """
        return self.__org_content

    def write(self, path):
        """Write modified content to given file `path`.

        :param path: File path to write modified content in.
        :type path: str
        """
        with open(path, 'w') as f:
            f.write(self.modified_content)

    @property
    def root(self):
        """Root node (top node of the parsed file).

        On standard .gproject files, root node is the `Document`.

        :return: Root node.
        :rtype: GuerillaNode
        """
        return self.objs[1]

    @property
    def doc_format_rev(self):
        """Document format revision.

        :return: Document format revision.
        :rtype: int
        :raises AttributeError: If no document format revision is present in
            file.
        """
        if self.__doc_format_rev is None:
            raise AttributeError("Missing doc format revision")

        return self.__doc_format_rev

    @classmethod
    def __recursive_node(cls, node):
        """Macro to recursively iterate over children of given `node`

        :param node: Node to iterate into children.
        :type node: GuerillaNode
        :rtype: collections.iterator[GuerillaNode]
        """
        for child in node.children:

            yield child

            for sub_child in cls.__recursive_node(child):

                yield sub_child

    @property
    def nodes(self):
        """Recursively iterate over nodes of the gproject file (except root
        node).

        :return: Generator of nodes of the parsed Guerilla file.
        :rtype: collections.iterator[GuerillaNode]
        """
        for node in self.__recursive_node(self.root):

            yield node

    @property
    def plugs(self):
        """Iterate over plugs of the gproject file.

        :return: Generator of plugs of the parsed Guerilla file.
        :rtype: collections.iterator[GuerillaPlug]
        """
        for node in self.nodes:
            for plug in node.plugs:
                yield plug

    @staticmethod
    def __clean_path(path):
        """Clean node path.

        "|foo|sphereShape\\\\$" -> "|foo|sphereShape$"
        "|bar|clous\\\\[1\\\\]" -> "|foo|clous[1]"
        """
        return re.sub(r'\\\\(.)', r'\g<1>', path)

    def __parse_nodes(self):
        """Parse commands in Guerilla file.
        """
        self.objs = {}

        for match in self._LINE_PARSE.finditer(self.original_content):

            cmd = match.group('cmd')
            args = match.group('args')

            if cmd in 'docformatrevision':

                self.__doc_format_rev = int(args)

            elif cmd in ('create', 'createnotref'):
                ###############################################################
                # create
                ###############################################################
                oid = int(match.group('oid'))

                match_arg = self._CMD_CREATE_ARG_PARSE.match(args)

                type_ = match_arg.group('type')
                parent = match_arg.group('parent')
                name = match_arg.group('name')

                if name is None:
                    name = match_arg.group('name_number')
                    if name is not None:  # we have something !
                        name = int(name)  # let's convert it to int

                if name is None:
                    name = ""

                # unescaped node names
                if isinstance(name, str):
                    name = re.sub(r'\\(.)', r'\g<1>', name)

                if parent in (r'\"\"', ''):  # GADocument or root
                    parent = None
                else:
                    parent_match_grp = self._PARENT_PARSE.match(parent)
                    parent_id = int(parent_match_grp.group('id'))
                    parent_path = parent_match_grp.group('path')

                    parent = self.objs[parent_id]

                    if parent_path:
                        parent_path = self.__clean_path(parent_path)
                        parent = self.__create_and_get_implicit_node(
                            parent, parent_path)

                if type_ in plug_class_names:
                    assert not isinstance(name, int), (type(name), name)
                    ###########################################################
                    # Plugs
                    ###########################################################
                    rest = match_arg.group('rest')

                    match_rest = self._CREATE_PLUG_REST_PARSE.match(rest)

                    flag = int(match_rest.group('flag'))
                    plug_type = match_rest.group('type')
                    param = match_rest.group('param')
                    value = match_rest.group('value')

                    # convert value to python type
                    if plug_type == 'types.string':
                        value = str(value)
                    elif plug_type in {'types.float',
                                       'types.angle',
                                       'types.radians',
                                       'LUIPSTypeNumber'}:
                        value = float(value)
                        if param is not None:
                            param = self.__lua_dict_to_python(param)
                    elif plug_type == 'types.bool':
                        value = bool(value)
                    elif plug_type == 'types.int':
                        value = int(value)
                        if param is not None:
                            param = self.__lua_dict_to_python(param)
                    elif plug_type in {'types.color',
                                       'types.vector',
                                       'types.vector2',
                                       'LUIPSTypeColor',
                                       'LUIPSTypeVector',
                                       'LUIPSTypePoint'}:
                        # "{1,0.5,0.5}" to (1,0.5,0.5)
                        value = eval(value.replace('{', '(').replace('}', ')'))
                    elif plug_type == 'types.enum':
                        value = str(value)
                        # '{{"Enabled","enable"},{"Disabled","disable"}}'
                        # TODO
                        param = {}
                    elif plug_type == 'types.hset':
                        # "Diffuse,-Reflection,-Refraction,Shadows"
                        value = set((s.replace(' ', '')
                                     for s in value.split(',')))
                    elif plug_type == 'LUIPSTypeInt':
                        if value == 'nil':
                            # Tested in Guerilla 2.1, a 'nil' int value return
                            # None. So we reproduce this behavior here
                            value = None
                        else:
                            value = int(value)
                    elif plug_type == 'LUIPSTypeAngle0Pi2':
                        value = float(value)
                    elif plug_type == 'LUIPSTypeFloat':
                        value = float(value)
                    elif plug_type == 'types.typeboxmode':
                        value = str(value)
                    elif plug_type == 'types.set':
                        value = str(value)
                    elif plug_type == 'types.texture':
                        value = value[1:-1]
                        value = str(value)
                    elif plug_type == 'types.projectors':
                        value = value[1:-1]
                    elif plug_type == 'types.combo':
                        # {"color","coordinates","density","fallof","fuel","pressure","temperature","velocity"},"density"
                        # TODO
                        param = {}
                    elif plug_type == 'LUIPSTypeString':
                        value = value[1:-1]
                    elif plug_type == 'types.metal':
                        value = value[1:-1]
                    elif plug_type == 'LUIPSTypeFloat01Open':
                        value = float(value)
                    elif plug_type == 'types.materials':
                        value = value[1:-1]
                    elif plug_type == 'types.radians0pi4':
                        value = float(value)
                    elif plug_type == 'types.animationmode':
                        value = value[1:-1]
                    else:
                        assert False, args

                    # convert param to python dict
                    if any((param == '{}',
                            param is None)):
                        param = {}

                    assert isinstance(param, dict), param

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

                    if type_ == 'ArchReference':
                        #######################################################
                        # ArchReference
                        #######################################################
                        rest = match_arg.group('rest')

                        match_rest = self._CREATE_REF_REST_PARSE.match(rest)

                        path = match_rest.group('path')
                        param = match_rest.group('param')

                        GuerillaPlug('ReferenceFileName', 'Plug', node, path)

                if self.diagnose:
                    if node.id == 1:
                        node_path = ""
                    else:
                        node_path = node.path
                    print(("Create '{node_path}' "
                           "'{node.type}'").format(**locals()))

            elif cmd == 'set':
                ###############################################################
                # set
                ###############################################################
                match_arg = self._CMD_SET_ARG_PARSE.match(args)

                oid = int(match_arg.group('id'))
                path = match_arg.group('path')
                plug_name = match_arg.group('plug')
                org_value = match_arg.group('value')

                value = self._lua_to_py_value(org_value)

                node = self.objs[oid]

                if path:
                    path = self.__clean_path(path)
                    node = self.__create_and_get_implicit_node(node, path)

                GuerillaPlug(plug_name, 'Plug', node, value,
                             org_value=org_value)

                if self.diagnose:
                    if node.id == 1:
                        node_path = ""
                    else:
                        node_path = node.path
                    print(('Set: {node_path}.{plug_name} -> '
                           '{value}').format(**locals()))

            elif cmd == 'connect':
                ###############################################################
                # connect
                ###############################################################
                match_arg = self._CMD_CONNECT_ARG_PARSE.match(args)

                in_oid = int(match_arg.group('in_id'))
                in_path = match_arg.group('in_path')
                in_plug_name = match_arg.group('in_plug')

                out_oid = int(match_arg.group('out_id'))
                out_path = match_arg.group('out_path')
                out_plug_name = match_arg.group('out_plug')

                in_node = self.objs[in_oid]

                if out_oid is 0 and 0 not in self.objs:
                    # 0 is a special value referencing root document, we have a
                    # glayer trying to connect to document root attribute, we
                    # don't support this.
                    print(("Trying to connect to document reference "
                           "'{args}'").format(**locals()))
                    continue

                out_node = self.objs[out_oid]

                if in_path:
                    in_path = self.__clean_path(in_path)
                    in_node = self.__create_and_get_implicit_node(in_node,
                                                                  in_path)

                if out_path:
                    out_path = self.__clean_path(out_path)
                    out_node = self.__create_and_get_implicit_node(out_node,
                                                                   out_path)

                if not out_path and not out_plug_name:
                    # output is in the form "$64", an expression node
                    if _print_expression_node_connection:
                        print(out_node.type, out_node.path, '->',
                              in_node.type, in_node.path, in_plug_name)
                    # TODO: support when output is $64-like
                    continue

                if not in_path and not in_plug_name:
                    # same here for inputs
                    if _print_expression_node_connection:
                        print(in_node.type, in_node.path, '->',
                              in_node.type, in_node.path, in_plug_name)
                    # TODO: support when input is $64-like
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

                assert in_plug.input is None, in_plug_name

                # p1.out -> p2.in
                out_plug.outputs.append(in_plug)
                in_plug.input = out_plug

                if self.diagnose:
                    if out_node.id == 1:
                        out_node_path = ""
                    else:
                        out_node_path = out_node.path
                    if in_node.id == 1:
                        in_node_path = ""
                    else:
                        in_node_path = in_node.path
                    print(('Connect: {out_node_path}.{out_plug_name} -> '
                           '{in_node_path}.{in_plug_name}').format(**locals()))

            elif cmd == 'depend':
                ###############################################################
                # depend
                ###############################################################
                match_arg = self._CMD_DEPEND_ARG_PARSE.match(args)

                in_oid = int(match_arg.group('in_id'))
                in_path = match_arg.group('in_path')
                in_plug_name = match_arg.group('in_plug')

                out_oid = int(match_arg.group('out_id'))
                out_path = match_arg.group('out_path')
                out_plug_name = match_arg.group('out_plug')

                # Some .grendergraph/.glayer files attempts to connect to
                # Guerilla root node. This node doesn't exists in the context
                # of parsing:
                # depend("$17.Out","$0|Preferences.ShutterClose")
                if out_oid is 0 and 0 not in self.objs:
                    print(("Trying to depends on document reference "
                           "'{args}'").format(**locals()))
                    continue

                in_node = self.objs[in_oid]
                out_node = self.objs[out_oid]

                if in_path:
                    in_path = self.__clean_path(in_path)
                    in_node = self.__create_and_get_implicit_node(in_node,
                                                                  in_path)

                if out_path:
                    out_path = self.__clean_path(out_path)
                    out_node = self.__create_and_get_implicit_node(out_node,
                                                                   out_path)

                if self.diagnose:
                    if out_node.id == 1:
                        out_node_path = ""
                    else:
                        out_node_path = out_node.path
                    if in_node.id == 1:
                        in_node_path = ""
                    else:
                        in_node_path = in_node.path
                    print(('Depend: {out_node_path}.{out_plug_name} -> '
                           '{in_node_path}.{in_plug_name}').format(**locals()))

                # TODO: For now, dependencies are not supported

            elif _print_unknown_command:
                print("Unknown command '{cmd}'".format(**locals()))

    def __create_and_get_implicit_node(self, start_node, path):
        """Macro to recursively create implicit nodes from given `path`
        starting from given `start_node`.

        if a direct path is present (instead of a direct node id)
        this mean we have an "implicit" node (aka: not created by
        the gproject itself).

        $36|Frustum -> $36 is `start_node` and "|Fustum" is `path`, will create
        a node from "UNKNOWN" type named "Frustrum" with node with id 36 as
        parent.

        :param start_node:
        :type start_node: GuerillaNode
        :param path:
        :type path: str
        :return:
        :rtype: GuerillaNode
        """
        # get in the cache for full path first
        try:
            return self.__implicit_node_cache[(start_node, path)]
        except KeyError:
            pass

        # no implicit node found? create it along its path!
        cur_parent = start_node

        # use to store path along iteration
        cur_path = ""

        # for  |foo|bar|toto, get-or-create 'foo', then 'bar', then 'toto'
        for name in path.split('|')[1:]:

            # aggregate current path ('|foo', then '|foo|bar', then
            # '|foo|bar|toto')
            cur_path = '|'.join((cur_path, name))

            # get-or-create implicit node
            try:
                implicit_node = self.__implicit_node_cache[(start_node,
                                                            cur_path)]
            except KeyError:

                implicit_node = GuerillaNode(-1, name, 'UNKNOWN', cur_parent)

                self._implicit_nodes.append(implicit_node)

                # store it in the cache
                self.__implicit_node_cache[(start_node, cur_path)] = \
                    implicit_node

            # prepare next iteration
            cur_parent = implicit_node

        # we now have our implicit node
        return cur_parent

    @staticmethod
    def __lua_dict_to_python(lua_dict_str):
        """Convert given lua table representation to python dict.

        "{foo=1,bar=2}" -> {'foo': 1, 'bar': 2}
        {min=0,max=16} to {'min': 0, max': 16}
        {slidermax=4,min=0} to {'slidermax': 4, 'min': 0}

        :param lua_dict_str: Lua table representation to convert in python.
        :type lua_dict_str: str
        :return: Lua table representation converted to python dict.
        :rtype: dict
        """
        # reformat
        lua_dict_str = re.sub(r'([a-zA-Z0-9_-]+)=([a-zA-Z0-9_-]+)',
                              r"'\g<1>':\g<2>",
                              lua_dict_str)
        # and eval as python expression
        return eval(lua_dict_str.replace('=', ':'))

    @staticmethod
    def _lua_to_py_value(raw_str):
        """Convert given guerilla lua `raw_str` value expression to python.

        :param raw_str: Raw string representing lua value to convert to python.
        :type raw_str: str
        :return: Value converted from lua to python.
        :rtype: bool|float|list[float]|str
        """
        if raw_str == 'true':

            return True

        elif raw_str == 'false':

            return False

        elif raw_str[0] == raw_str[-1] == '"':  # surrounded by '"'?

            # lua string
            return str(raw_str[1:-1].replace(r'\010', '\n')
                                    .replace(r'\009', '\t')
                                    .replace(r'\"', '"')
                                    .replace('\\\\', '\\'))

        elif _FLOAT_PARSE.match(raw_str):

            # we don't support int as "1" can be a float but lua hide
            # fractional part
            return float(raw_str)

        elif _FLOAT_TABLE_PARSE.match(raw_str):

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
            print(("Missing lua to python conversion "
                   "'{raw_str}'").format(**locals()))

        return raw_str

    @staticmethod
    def __is_float_intable(value):
        """Return if given float `value` is possible to convert to int without
        lost.

        4.2 returns False, 4.0 return True

        :param value:
        :return: True if given `value` is convertible in `int` without.
        precision loss.
        """
        return (value - math.floor(value)) == 0.0

    @classmethod
    def _py_to_lua_value(cls, value):
        """Convert given python `value` to guerilla lua string representation.

        :param value: Python value to convert in lua string representation.
        :type value: bool|int|float|string|list[float]|dict
        :return: Value converted from python to lua representation.
        :rtype: str
        """
        if type(value) is bool:

            return cls._PY_TO_LUA_BOOL[value]

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
            print(("Missing python to lua conversion "
                   "'{value}'").format(**locals()))

        return value

    def path_to_node(self, path):
        """Find and return node at given `path`.

        :Example:

        >>> p.path_to_node('|foo|bar|bee')
        GuerillaNode('bee', 10, 'primitive')
        >>> p.path_to_node('$65|bar|bee')
        GuerillaNode('bee', 10, 'primitive')

        :param path: Path to get node from.
        :type path: str
        :return: Node found from given `path`.
        :rtype: GuerillaNode
        :raises PathError: If root node can't be found.
        :raises PathError: If path contain unreachable nodes.
        """
        assert path is not None
        assert isinstance(path, str), (type(path), path)

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
        for path_node_name in re.split(r'(?<!\\)\|', path)[1:]:

            for node in cur_node.children:
                if node._name_for_path == path_node_name:
                    cur_node = node
                    break  # we've found it! let's move to the next node

            else:  # no break?
                raise PathError("Can't find node '{path}'".format(**locals()))

        return cur_node

    def path_to_plug(self, path):
        """Find and return plug at given `path`.

        :Example:

        >>> p.path_to_plug('|foo|bar.DiffuseColor')
        GuerillaPlug('DiffuseColor', 'Plug', '|foo|bar|bee')

        :param path: Path to get plug from.
        :type path: str
        :return: Plug found from given `path`.
        :rtype: GuerillaPlug
        :raises PathError: If path doen't point to a plugs.
        """
        # ('|foo|bar', 'DiffuseColor')
        try:
            node_path, plug_name = path.rsplit('.', 1)
        except ValueError:
            raise PathError("No plug in path '{path}'".format(
                **locals()))

        if node_path:
            node = self.path_to_node(node_path)
        else:
            node = self.root  # plug is connected to root document

        try:
            return node.get_plug(plug_name)
        except KeyError:
            raise PathError("Can't find plug '{}' in node '{}'".format(
                plug_name, node.path))

    @staticmethod
    def node_to_id_path(node):
        """Return the shortest `id path` for given `node`.

        Node id paths are paths relative to the first parent node with an id.

        This methode is mostly for internal use to find plug value in
        ``set_plug_value()`` but is exposed to the user for his own
        convinience; debugging, file compare, etc.

        :Example:

        >>> p.node_to_id_path(my_node)
        '$60'
        >>> p.node_to_id_path(my_other_node)
        '$37|Frustum'

        In the second line above, ``my_other_node`` is an implicit node. See
        :doc:`file format information <../file_format_info>` page for more
        information.

        :param node: Implicit node to get `id path` from.
        :type node: GuerillaNode
        :return:
        :rtype: str
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
        """Escape given string `value` to make it parsed in regex.

        :param value: String to escape for regex.
        :type value: str
        :return: Escaped string.
        :rtype: str
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
        """While exposed, this method is not stable yet and could potentially
        change in the future.

        :param plug_values:
        :type plug_values: list[(GuerillaPlug, str)]
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

            old_lua_value = self._py_to_lua_value(plug.value)
            new_lua_value = self._py_to_lua_value(value)

            path = self.node_to_id_path(plug.parent)

            plug_path = "{path}.{plug.name}".format(**locals())

            plug_value_list[plug_path] = new_lua_value

            # regex is separated in three groups:
            # set(" | $3.AxisColor | ",{0,0,0,1})
            # we need the second
            # the job of the replace function (outside the loop) is to
            # recreated the latest group
            regex_str = [r'(\s*set\(")(',
                         plug_path.replace('$', '\\$').replace('.', '\\.'),
                         ')(",',
                         self.__escape_str_for_regex(old_lua_value),
                         '\\)\n)']

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
