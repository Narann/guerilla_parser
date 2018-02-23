import difflib
import filecmp
import os.path
import sys
import tempfile
import unittest


def _get_parent_dir(path):
    """utility function to get parent dir"""
    return os.path.abspath(os.path.join(os.path.abspath(path), os.pardir))


root_dir = _get_parent_dir(_get_parent_dir(__file__))

test_dir = _get_parent_dir(__file__)
gproj_dir = os.path.join(test_dir, 'gproject')

sys.path.insert(0, root_dir+'/src')

import guerilla_parser
import guerilla_parser.util as grl_util


default_gprojects = [gproj_dir+'/1.4.14_01_default/1.4.14_01_default.gproject',
                     gproj_dir+'/2.0.0a31_02_default/2.0.0a31_02_default.gproject']

default_glayers = [gproj_dir+'/1.4.14_01_default/1.4.14_01_default.glayer',
                   gproj_dir+'/2.0.0a31_02_default/2.0.0a31_02_default.glayer']

default_grendergraphs = [gproj_dir+'/1.4.14_01_default/1.4.14_01_default.grendergraph',
                         gproj_dir+'/2.0.0a31_02_default/2.0.0a31_02_default.grendergraph']

gprojects = [
    gproj_dir+'/1.4.13_01/1.4.13_01.gproject',
    gproj_dir+'/1.4.19_01_node_name/1.4.19_01.gproject',
    gproj_dir+'/1.4.19_01_anim/1.4.19_01_anim.gproject',
    gproj_dir+'/2.0.0a31_01/2.0.0a31_01.gproject',
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

    def test_parse(self):

        p = guerilla_parser.parse(path)
        g_parsed[path] = p

    return test_parse


def test_generator_path_to_node(path):
    """Generate a function testing given `path`.

    :param path: gproject path to test
    :return: function
    """
    def test_path_to_node(self):
        """check returned path can be used to find node back"""
        # import cProfile, pstats, StringIO
        # pr = cProfile.Profile()
        # pr.enable()
        assert path in g_parsed
        p = g_parsed[path]

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

    return test_path_to_node


def test_generator_nodes(path):
    """Generate a function testing given `path`.

    :param path: gproject path to test
    :return: function
    """
    def test_nodes(self):
        """check each node path is unique"""
        assert path in g_parsed
        p = g_parsed[path]

        # implicit nodes
        paths = set()

        for node in p._implicit_nodes:
            self.assertNotIn(node.path, paths)
            paths.add(node.path)

        # nodes
        paths = set()

        for node in p.nodes:
            self.assertNotIn(node.path, paths)
            paths.add(node.path)

    return test_nodes


def test_generator_raises(path):
    """Generate a function testing given `path`.

    :param path: gproject path to test
    :return: function
    """
    def test_raises(self):

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

    return test_raises


def test_generator_child_unique(path):
    """Generate a function testing given `path`.

    :param path: gproject path to test
    :return: function
    """
    def test_child_unique(self):

        assert path in g_parsed
        p = g_parsed[path]

        for node in p.nodes:

            child_names = set()

            for child in node.children:

                self.assertNotIn(child.name, child_names)

                child_names.add(child.name)

    return test_child_unique


def test_generator_default_gprojects(path):
    """Generate a function testing given `path`.

    :param path: gproject path to test
    :return: function
    """
    def test_default_gprojects(self):

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

    return test_default_gprojects


def test_generator_aovs(path):
    """Generate a function testing given `path`.

    :param path: gproject path to test
    :return: function
    """
    def test_aovs(self):
        """test render pass render layer and aov particularities"""

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

    return test_aovs


def test_generator_default_glayers(path):
    """Generate a function testing given `path`.

    :param path: gproject path to test
    :return: function
    """
    def test_default_glayers(self):

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

    return test_default_glayers


class TestSequence(unittest.TestCase):
    pass


for path in all_gfiles:
    test_name = _gen_test_name('001_parse', path)
    test = test_generator_parse(path)
    assert not hasattr(TestSequence, test_name)
    setattr(TestSequence, test_name, test)

    test_name = _gen_test_name('path_to_node', path)
    test = test_generator_path_to_node(path)
    assert not hasattr(TestSequence, test_name)
    setattr(TestSequence, test_name, test)

    test_name = _gen_test_name('nodes', path)
    test = test_generator_nodes(path)
    setattr(TestSequence, test_name, test)

    test_name = _gen_test_name('raises', path)
    test = test_generator_raises(path)
    setattr(TestSequence, test_name, test)

    test_name = _gen_test_name('child_unique', path)
    test = test_generator_child_unique(path)
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
    def test_set_plug_value(self):

        p = guerilla_parser.parse(path)

        node = p.path_to_node("|Preferences|RenderViewport")

        plug = node.get_plug("ColorMode")
        self.assertEqual(plug.value, 'multiply')
        p.set_plug_value([(plug, 'divide')])
        self.assertEqual(plug.value, 'divide')

    return test_set_plug_value


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
    def test_write_file(self):

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

    return test_write_file


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


if __name__ == '__main__':
    unittest.main()
