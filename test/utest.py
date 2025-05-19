import difflib
import filecmp
import os.path
import sys
import tempfile
import unittest


def _get_parent_dir(path):
    """utility function to get parent dir
    """
    return os.path.abspath(os.path.join(os.path.abspath(path), os.pardir))


root_dir = _get_parent_dir(_get_parent_dir(__file__))

test_dir = _get_parent_dir(__file__)
gproj_dir = os.path.join(test_dir, 'gproject')

sys.path.insert(0, root_dir+'/src')

import guerilla_parser
import guerilla_parser.util as grl_util


default_gprojects = [
    gproj_dir+'/1.4.14_01_default/1.4.14_01_default.gproject',
    gproj_dir+'/2.0.0a31_02_default/2.0.0a31_02_default.gproject'
]

default_glayers = [
    gproj_dir+'/1.4.14_01_default/1.4.14_01_default.glayer',
    gproj_dir+'/2.0.0a31_02_default/2.0.0a31_02_default.glayer'
]

default_grendergraphs = [
    gproj_dir+'/1.4.14_01_default/1.4.14_01_default.grendergraph',
    gproj_dir+'/2.0.0a31_02_default/2.0.0a31_02_default.grendergraph'
]

gprojects = [
    gproj_dir+'/1.4.13_01/1.4.13_01.gproject',
    gproj_dir+'/1.4.19_01_node_name/1.4.19_01.gproject',
    gproj_dir+'/1.4.19_01_anim/1.4.19_01_anim.gproject',
    gproj_dir+'/2.0.0a31_01/2.0.0a31_01.gproject',
    gproj_dir+'/2.0.7/2.0.7.gproject',
    gproj_dir+'/2.0.7/2.0.7_ref.gproject',  # unsolvable even by Guerilla
    gproj_dir+'/2.1.0b19/2.1.0b19_archreference.gproject',
    gproj_dir+'/2.3.0b16/2.3.0b16.gproject',
    gproj_dir+'/2.3.0b16/texture_colorspace.gproject',
    gproj_dir+'/2.1.3/animmode_loop.gproject',
    gproj_dir+'/2.3.15/types_text.gproject',
    gproj_dir+'/2.4.2/types_light_categories.gproject',
    ]

all_gprojects = [f for f in default_gprojects]
all_gprojects += [f for f in gprojects]

all_gfiles = [f for f in all_gprojects]
all_gfiles += [f for f in default_glayers]
all_gfiles += [f for f in default_grendergraphs]


# dynamic test pattern inspired from:
# https://stackoverflow.com/questions/32899/how-to-generate-dynamic-parametrized-unit-tests-in-python
# test pattern:
# TestSequence: the main empty class
# test_generator_<test_name> return a function to test given path
#  '-> test_<test_name> function that run the test

def _gen_test_name(name, path):
    """Macro to properly generate test method name from given test `name` and
    file `path`

    :return: test name
    :rtype: str
    """
    return 'test_{}_{}'.format(name, path.replace(test_dir, '')
                                         .replace('.', '_'))


g_parsed = {}


def test_generator_parse(path):

    def test_func(self):

        p = guerilla_parser.parse(path)
        g_parsed[path] = p

    return test_func


def test_generator_path_to_node(path):
    """Generate a function testing given `path`.

    :param path: gproject path to test
    :return: function
    """
    def test_func(self):
        """check returned path can be used to find node back
        """
        # import cProfile, pstats, StringIO
        # pr = cProfile.Profile()
        # pr.enable()
        assert path in g_parsed
        p = g_parsed[path]

        with self.assertRaises(guerilla_parser.PathError) as _:
            p.path_to_node("BLAH")

        for node in p.nodes:
            self.assertIs(node, p.path_to_node(node.path))

        for node in p._implicit_nodes:
            self.assertIs(node, p.path_to_node(node.path))

        # pr.disable()
        # s = StringIO.StringIO()
        # sortby = 'cumulative'
        # ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        # ps.print_stats()
        # print(s.getvalue())

    return test_func


def test_generator_path_to_plug(path):
    """Generate a function testing given `path`.

    :param path: gproject path to test
    :return: function
    """
    def test_func(self):
        """check returned path can be used to find plug back
        """
        assert path in g_parsed
        p = g_parsed[path]

        with self.assertRaises(guerilla_parser.PathError) as _:
            p.path_to_plug("BLAH")

        for plug in p.plugs:
            self.assertIs(plug, p.path_to_plug(plug.path))

    return test_func


def test_generator_nodes(path):
    """Generate a function testing given `path`.

    :param path: gproject path to test
    :return: function
    """
    def test_func(self):
        """check each node path is unique
        """
        assert path in g_parsed
        p = g_parsed[path]

        # implicit nodes
        paths = set()

        for node in p._implicit_nodes:
            self.assertIsInstance(node, guerilla_parser.GuerillaNode)
            self.assertNotIn(node.path, paths)
            paths.add(node.path)

        # nodes
        paths = set()

        for node in p.nodes:
            self.assertIsInstance(node, guerilla_parser.GuerillaNode)
            self.assertNotIn(node.path, paths)
            paths.add(node.path)

    return test_func


def test_generator_plugs(path):
    """Generate a function testing given `path`.

    :param path: gproject path to test
    :return: function
    """
    def test_func(self):
        """check each plug path is unique
        """
        assert path in g_parsed
        p = g_parsed[path]

        # plugs
        paths = set()

        for plug in p.plugs:
            self.assertIsInstance(plug, guerilla_parser.GuerillaPlug)
            self.assertNotIn(plug.path, paths)
            paths.add(plug.path)

    return test_func


def test_generator_raises(path):
    """Generate a function testing given `path`.

    :param path: gproject path to test
    :return: function
    """
    def test_func(self):

        assert path in g_parsed
        p = g_parsed[path]

        root_node = p.root

        with self.assertRaises(guerilla_parser.PathError):
            root_node.path

        with self.assertRaises(guerilla_parser.ChildError):
            root_node.get_child('TAGADAPOUETPOUET')

        with self.assertRaises(guerilla_parser.PathError):
            p.path_to_node('TAGADAPOUETPOUET')

        with self.assertRaises(guerilla_parser.PathError):
            grl_util.aov_node(p, 'RenderPass', 'Layer', 'TAGADAPOUETPOUET')

    return test_func


def test_generator_child_unique(path):
    """Generate a function testing given `path`.

    :param path: gproject path to test
    :return: function
    """
    def test_func(self):

        assert path in g_parsed
        p = g_parsed[path]

        for node in p.nodes:

            child_names = set()

            for child in node.children:

                self.assertNotIn(child.name, child_names)

                child_names.add(child.name)

    return test_func


def test_generator_arch_ref(path):
    """Generate a function testing given `path`.

    :param path: gproject path to test
    :return: function
    """
    def test_func(self):

        assert path in g_parsed
        p = g_parsed[path]

        for node in p.nodes:

            if node.type == 'ArchReference':

                # this plug must exists
                node.get_plug('ReferenceFileName')

            else:
                with self.assertRaises(KeyError):
                    node.get_plug('ReferenceFileName')

    return test_func


def test_generator_default_gprojects(path):
    """Generate a function testing given `path`.

    :param path: gproject path to test
    :return: function
    """
    def test_func(self):

        assert path in g_parsed
        p = g_parsed[path]

        self.assertIsInstance(p, guerilla_parser.GuerillaParser)

        self.assertEqual(p.doc_format_rev, 19)

        doc = p.root

        self.assertEqual(doc.id, 1)
        self.assertEqual(doc.name, 'LUIDocument')
        self.assertEqual(doc.type, 'GADocument')
        self.assertEqual(doc.get_plug('AutoKey').value, True)
        self.assertEqual(doc.get_plug('InvertT').value, False)
        self.assertEqual(doc.get_plug('LastFrame').value, 50)
        self.assertEqual(doc.get_plug('Membership').value, "All")
        self.assertEqual(doc.get_plug('CurveWidthShape').value, 1.5)

        pref = doc.get_child('Preferences')

        self.assertEqual(pref.id, 2)
        self.assertEqual(pref.name, 'Preferences')
        self.assertEqual(pref.type, 'Preferences')

        self.assertEqual(pref.get_plug('LightAmbient').value, [0, 0, 0, 1])
        self.assertEqual(pref.get_plug('LightSpecular').value,
                         [0.5, 0.5, 0.5, 1])
        self.assertEqual(pref.get_plug('SearchPathTexture').value, "")

        for node in p.nodes:
            for child in node.children:
                self.assertIs(node.get_child(child.name), child)

            for plug in node.plugs:
                self.assertIs(node.get_plug(plug.name), plug)

        # aov
        aov = grl_util.aov_node(p, 'RenderPass', 'Layer', 'Beauty')

        self.assertIsInstance(aov, guerilla_parser.GuerillaNode)
        self.assertEqual(aov.path, "|RenderPass|Layer|Input1")

        rp_iter = (n for n in p.nodes if n.type == 'RenderPass')

        for rp in rp_iter:

            rl_iter = (n for n in rp.children if n.type == 'RenderLayer')

            for rl in rl_iter:

                for aov in rl.children:
                    self.assertEqual(aov.type, "LayerOut")

                    aov_2 = grl_util.aov_node(p, rp.name, rl.name,
                                              aov.display_name)

                    self.assertIs(aov, aov_2)

        # path to node
        for node in p.nodes:
            self.assertEqual(node, p.path_to_node(node.path))

    return test_func


def test_generator_aovs(path):
    """Generate a function testing given `path`.

    :param path: gproject path to test
    :return: function
    """
    def test_func(self):
        """test render pass render layer and AOV particularities
        """

        assert path in g_parsed
        p = g_parsed[path]

        aov = grl_util.aov_node(p, 'RenderPass', 'Layer', 'Beauty')

        self.assertIsInstance(aov, guerilla_parser.GuerillaNode)
        self.assertEqual(aov.path, "|RenderPass|Layer|Input1")

        rp_iter = (n for n in p.nodes if n.type == 'RenderPass')

        for rp in rp_iter:

            rl_iter = (n for n in rp.children if n.type == 'RenderLayer')

            for rl in rl_iter:

                for aov in rl.children:

                    self.assertEqual(aov.type, "LayerOut")

                    aov_2 = grl_util.aov_node(p, rp.name, rl.name,
                                              aov.display_name)

                    self.assertIs(aov, aov_2)

    return test_func


def test_generator_default_glayers(path):
    """Generate a function testing given `path`.

    :param path: gproject path to test
    :return: function
    """
    def test_func(self):

        assert path in g_parsed
        p = g_parsed[path]

        root = p.root

        self.assertEqual(root.id, 1)
        self.assertEqual(root.name, 'RenderPass')
        self.assertEqual(root.type, 'RenderPass')
        self.assertEqual(root.get_plug('AutoBuildTextures').value, True)
        self.assertEqual(root.get_plug('BalanceReyesDistribution').value, False)
        self.assertEqual(root.get_plug('BrdfSamples').value, 16)
        self.assertEqual(root.get_plug('ColorMode').value, "multiply")
        self.assertEqual(root.get_plug('DeepCompression').value, 0.1)
        self.assertEqual(root.get_plug('DefaultSurfaceColor').value,
                         [0.0, 0.0, 0.0])

    return test_func


class TestSequence(unittest.TestCase):
    pass


for path in all_gfiles:
    test_name = _gen_test_name('001_parse', path)
    test = test_generator_parse(path)
    assert not hasattr(TestSequence, test_name), test_name
    setattr(TestSequence, test_name, test)

    test_name = _gen_test_name('path_to_node', path)
    test = test_generator_path_to_node(path)
    assert not hasattr(TestSequence, test_name), test_name
    setattr(TestSequence, test_name, test)

    test_name = _gen_test_name('path_to_plug', path)
    test = test_generator_path_to_plug(path)
    assert not hasattr(TestSequence, test_name), test_name
    setattr(TestSequence, test_name, test)

    test_name = _gen_test_name('nodes', path)
    test = test_generator_nodes(path)
    setattr(TestSequence, test_name, test)

    test_name = _gen_test_name('plugs', path)
    test = test_generator_plugs(path)
    setattr(TestSequence, test_name, test)

    test_name = _gen_test_name('raises', path)
    test = test_generator_raises(path)
    setattr(TestSequence, test_name, test)

    test_name = _gen_test_name('child_unique', path)
    test = test_generator_child_unique(path)
    setattr(TestSequence, test_name, test)

    test_name = _gen_test_name('arch_ref', path)
    test = test_generator_arch_ref(path)
    setattr(TestSequence, test_name, test)

for path in default_gprojects:

    test_name = _gen_test_name('default_gproject', path)
    test = test_generator_default_gprojects(path)
    assert not hasattr(TestSequence, test_name)
    setattr(TestSequence, test_name, test)

    test_name = _gen_test_name('aovs', path)
    test = test_generator_aovs(path)
    assert not hasattr(TestSequence, test_name)
    setattr(TestSequence, test_name, test)

for path in default_glayers:
    test_name = _gen_test_name('default_glayers', path)
    test = test_generator_default_glayers(path)
    assert not hasattr(TestSequence, test_name)
    setattr(TestSequence, test_name, test)


def test_generator_set_plug_value(path):
    """Generate a function testing given `path`.

    :param path: gproject path to test
    :return: function
    """
    def test_func(self):

        p = guerilla_parser.parse(path)

        node = p.path_to_node("|Preferences|RenderViewport")

        plug = node.get_plug("ColorMode")
        self.assertEqual(plug.value, 'multiply')
        p.set_plug_value([(plug, 'divide')])
        self.assertEqual(plug.value, 'divide')

    return test_func


class SetPlugValueTestCase(unittest.TestCase):
    pass


for gproject in default_gprojects:
    test_name = _gen_test_name('set_plug_value', gproject)
    test = test_generator_set_plug_value(gproject)
    setattr(SetPlugValueTestCase, test_name, test)


def test_generator_write_file(path):
    """Generate a function testing given `path`.

    :param path: gproject path to test
    :return: function
    """
    def test_func(self):

        _, tmp_file = tempfile.mkstemp()
        os.close(_)

        p = guerilla_parser.parse(
            path,
            diagnose=False)

        p.write(tmp_file)

        # no change
        self.assertFalse(p.has_changed)
        self.assertTrue(filecmp.cmp(path, tmp_file))

        node = p.path_to_node("|Preferences|RenderViewport")

        # get value
        plug = node.get_plug("ColorMode")
        self.assertEqual(plug.value, 'multiply')

        # set value
        p.set_plug_value([(plug, 'divide')])
        self.assertEqual(plug.value, 'divide')

        p.write(tmp_file)

        # has changed
        self.assertTrue(p.has_changed)
        self.assertFalse(filecmp.cmp(path, tmp_file))

        # get diff
        old = []
        new = []
        for c in difflib.ndiff(p.original_content, p.modified_content):
            if c.startswith("- "):
                old.append(c[2:])
                continue
            if c.startswith("+ "):
                new.append(c[2:])
                continue

        old = "".join(old)
        new = "".join(new)

        # no typo here! "i" is just considered has haven't been moved
        self.assertEqual(old, 'multply')
        self.assertEqual(new, 'dvide')

        os.remove(tmp_file)

    return test_func


class WriteFileTestCase(unittest.TestCase):
    pass


for gproject in default_gprojects:
    test_name = _gen_test_name('write_file', gproject)
    test = test_generator_write_file(gproject)
    setattr(WriteFileTestCase, test_name, test)


class TestStringMethods(unittest.TestCase):

    def test_read(self):

        p = guerilla_parser.parse(default_gprojects[1])

        self.assertIsInstance(p, guerilla_parser.GuerillaParser)

        self.assertEqual(p.doc_format_rev, 19)

        doc = p.root

        self.assertEqual(doc.id, 1)
        self.assertEqual(doc.name, 'LUIDocument')
        self.assertEqual(doc.type, 'GADocument')
        self.assertEqual(doc.get_plug('InternalDirectLighting').value, True)
        self.assertEqual(doc.get_plug('InvertT').value, False)
        self.assertEqual(doc.get_plug('LastFrame').value, 50)
        self.assertEqual(doc.get_plug('Membership').value, "All")
        self.assertEqual(doc.get_plug('CurveWidthShape').value, 1.5)

        pref = doc.get_child('Preferences')

        self.assertEqual(pref.id, 2)
        self.assertEqual(pref.name, 'Preferences')
        self.assertEqual(pref.type, 'Preferences')

        self.assertEqual(pref.get_plug('LightAmbient').value, [0, 0, 0, 1])
        self.assertEqual(pref.get_plug('LightSpecular').value, [0.5, 0.5, 0.5, 1])
        self.assertEqual(pref.get_plug('SearchPathTexture').value, "")

        for node in p.nodes:
            for child in node.children:
                self.assertIs(node.get_child(child.name), child)

            for plug in node.plugs:
                self.assertIs(node.get_plug(plug.name), plug)


class TestArchReferenceMethods(unittest.TestCase):

    def test_read(self):

        p = guerilla_parser.parse(gprojects[6])

        self.assertIsInstance(p, guerilla_parser.GuerillaParser)

        self.assertEqual(p.doc_format_rev, 19)

        doc = p.root

        self.assertEqual(doc.id, 1)
        self.assertEqual(doc.name, 'LUIDocument')
        self.assertEqual(doc.type, 'GADocument')

        foo_node = doc.get_child('foo')

        self.assertEqual(foo_node.type, 'ArchReference')

        self.assertEqual(foo_node.get_plug('ReferenceFileName').value,
                         '/path/to/file.abc')


class TestUniqueAttr(unittest.TestCase):

    def test_types_multistrings(self):

        path = gproj_dir + '/2.3.0b16/texture_switch.gproject'

        p = guerilla_parser.parse(path)

        node = p.objs[53]

        plug = node.get_plug('Files')

        self.assertEqual(plug.name, 'Files')
        self.assertEqual(plug.flag, 4)
        self.assertEqual(plug.type, 'AttributeShaderPlug')
        self.assertEqual(plug.value, ['$(SAMPLES)/sprite.1.png',
                                      '$(SAMPLES)/sprite.2.png',
                                      '$(SAMPLES)/sprite.3.png',
                                      '$(SAMPLES)/sprite.4.png'])

    def test_types_bool(self):

        path = gproj_dir + '/2.0.0a31_01/2.0.0a31_01.gproject'

        p = guerilla_parser.parse(path)

        node = p.objs[85]

        plug = node.get_plug('DoubleSided')

        self.assertEqual(plug.name, 'DoubleSided')
        self.assertEqual(plug.flag, 4)
        self.assertEqual(plug.type, 'SceneGraphNodePropsPlug')
        self.assertEqual(plug.value, False)

    def test_types_light_categories(self):

        path = gproj_dir + '/2.4.2/types_light_categories.gproject'

        p = guerilla_parser.parse(path)

        node = p.objs[40]

        plug = node.get_plug('Category')

        self.assertEqual(plug.name, 'Category')
        self.assertEqual(plug.flag, 4)
        self.assertEqual(plug.type, 'SceneGraphNodeRenderPropsPlug')
        self.assertEqual(plug.value, 'FillLightTest')

        plug = node.get_plug('HSet')

        self.assertEqual(plug.name, 'HSet')
        self.assertEqual(plug.flag, 4)
        self.assertEqual(plug.type, 'HSetPlug')
        self.assertEqual(plug.value, {'-PointLight',
                                      'Diffuse',
                                      'Reflection',
                                      'Refraction',
                                      'Shadows'})

        plug = node.get_plug('ShadowSet')

        self.assertEqual(plug.name, 'ShadowSet')
        self.assertEqual(plug.flag, 4)
        self.assertEqual(plug.type, 'HSetPlug')
        self.assertEqual(plug.value, {'-PointLight', 'Shadows'})

        plug = node.get_plug('HVisible')

        self.assertEqual(plug.name, 'HVisible')
        self.assertEqual(plug.flag, 4)
        self.assertEqual(plug.type, 'HVisiblePlug')
        self.assertEqual(plug.value, {"-visible:VisTest2", "visible:VisTest1"})

        plug = node.get_plug('HMatte')

        self.assertEqual(plug.name, 'HMatte')
        self.assertEqual(plug.flag, 4)
        self.assertEqual(plug.type, 'HMattePlug')
        self.assertEqual(plug.value, {"matte:MatteTest1", "matte:MatteTest2"})

        plug = node.get_plug('DistantMode')

        self.assertEqual(plug.name, 'DistantMode')
        self.assertEqual(plug.flag, 4)
        self.assertEqual(plug.type, 'SceneGraphNodeRenderPropsPlug')
        self.assertEqual(plug.value, "distant")


###############################################################################
# Unique string test
###############################################################################
class TestUniqueStringRegexes(unittest.TestCase):

    def test_read(self):

        cls = guerilla_parser.GuerillaParser

        for raw_str in ('"AttributePlug","$799","MetalProfile",4,types.metal,"$(LIBRARY)/ior/Gold/McPeak.yml"',
                        ):

            match_arg = cls._CMD_CREATE_ARG_PARSE.match(raw_str)

            self.assertIsNotNone(match_arg)

            self.assertEqual(match_arg.group('type'), 'AttributePlug')
            self.assertEqual(match_arg.group('parent'), '$799')
            self.assertEqual(match_arg.group('name'), 'MetalProfile')

            rest = match_arg.group('rest')

            self.assertIsNotNone(match_arg)

            match_rest = cls._CREATE_PLUG_REST_PARSE.match(rest)

            self.assertIsNotNone(match_rest)

            self.assertEqual(match_rest.group('flag'), '4')
            self.assertEqual(match_rest.group('type'), 'types.metal')
            self.assertIsNone(match_rest.group('param'))
            self.assertEqual(match_rest.group('value'),
                             '"$(LIBRARY)/ior/Gold/McPeak.yml"')
            #value = match_rest.group('value')


if __name__ == '__main__':
    unittest.main()
