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

sys.path.insert(0, root_dir+'/src')

import guerilla_parser
import guerilla_parser.util as grl_util


default_gprojects = [test_dir+'/gproject/1.4.14_01_default/1.4.14_01_default.gproject',
                     test_dir+'/gproject/2.0.0a31_02_default/2.0.0a31_02_default.gproject']

default_glayers = [test_dir+'/gproject/1.4.14_01_default/1.4.14_01_default.glayer',
                   test_dir+'/gproject/2.0.0a31_02_default/2.0.0a31_02_default.glayer']

default_grendergraphs = [test_dir+'/gproject/1.4.14_01_default/1.4.14_01_default.grendergraph',
                         test_dir+'/gproject/2.0.0a31_02_default/2.0.0a31_02_default.grendergraph']

gprojects = [test_dir+'/gproject/1.4.13_01/1.4.13_01.gproject',
             test_dir+'/gproject/1.4.19_01_node_name/1.4.19_01.gproject',
             test_dir+'/gproject/1.4.19_01_anim/1.4.19_01_anim.gproject',
             test_dir+'/gproject/2.0.0a31_01/2.0.0a31_01.gproject',
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
    return 'test_{}_{}'.format(name, path.replace('.', '_'))


class TestSequence(unittest.TestCase):
    pass


def test_generator_default_gprojects(path):
    """Generate a function testing given `path`.

    :param path: gproject path to test
    :return: function
    """
    def test_default_gprojects(self):

        p = guerilla_parser.parse(path)

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


for gproject in default_gprojects:
    test_name = _gen_test_name('default_gproject', gproject)
    test = test_generator_default_gprojects(gproject)
    setattr(TestSequence, test_name, test)


def test_generator_default_glayers(path):
    """Generate a function testing given `path`.

    :param path: gproject path to test
    :return: function
    """
    def test_default_glayers(self):

        p = guerilla_parser.parse(path)

        root = p.root

        self.assertEqual(root.id, 1)
        self.assertEqual(root.name, 'RenderPass')
        self.assertEqual(root.type, 'RenderPass')
        self.assertEqual(root.get_plug('AutoBuildTextures').value, True)
        self.assertEqual(root.get_plug('BalanceReyesDistribution').value, False)
        self.assertEqual(root.get_plug('BrdfSamples').value, 16)
        self.assertEqual(root.get_plug('ColorMode').value, "multiply")
        self.assertEqual(root.get_plug('DeepCompression').value, 0.1)
        self.assertEqual(root.get_plug('DefaultSurfaceColor').value, [0.0, 0.0, 0.0])

    return test_default_glayers


for gproject in default_glayers:
    test_name = _gen_test_name('default_glayers', gproject)
    test = test_generator_default_glayers(gproject)
    setattr(TestSequence, test_name, test)


def test_generator_aovs(path):
    """Generate a function testing given `path`.

    :param path: gproject path to test
    :return: function
    """
    def test_aovs(self):
        """test render pass render layer and aov particularities"""

        p = guerilla_parser.parse(path)

        aov = grl_util.aov_node(p, 'RenderPass', 'Layer', 'Beauty')

        self.assertIsInstance(aov, guerilla_parser.GuerillaNode)
        self.assertEqual(aov.path, "|RenderPass|Layer|Input1")

        rp_iter = (n for n in p.nodes if n.type == 'RenderPass')

        for rp in rp_iter:

            rl_iter = (n for n in rp.children if n.type == 'RenderLayer')

            for rl in rl_iter:

                for aov in rl.children:

                    self.assertEqual(aov.type, "LayerOut")

                    aov_2 = grl_util.aov_node(p, rp.name, rl.name, aov.display_name)

                    self.assertIs(aov, aov_2)

    return test_aovs


for gproject in default_gprojects:
    test_name = _gen_test_name('aovs', gproject)
    test = test_generator_aovs(gproject)
    setattr(TestSequence, test_name, test)


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
        p = guerilla_parser.parse(path, diagnose=False)

        for node in p.nodes:
            self.assertEqual(node, p.path_to_node(node.path))

        # pr.disable()
        # s = StringIO.StringIO()
        # sortby = 'cumulative'
        # ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        # ps.print_stats()
        # print s.getvalue()

    return test_path_to_node


for gproject in all_gfiles:
    test_name = _gen_test_name('path_to_node', gproject)
    test = test_generator_path_to_node(gproject)
    setattr(TestSequence, test_name, test)


def test_generator_nodes(path):
    """Generate a function testing given `path`.

    :param path: gproject path to test
    :return: function
    """
    def test_nodes(self):
        """check each node path is unique"""
        p = guerilla_parser.parse(path, diagnose=False)

        # implicit nodes
        paths = set()

        for node in p._implicit_nodes:
            self.assertNotIn(node.path, paths)
            paths.add(node.path)

        # nodes
        paths = set()

        for node in p.nodes:
            print node.path
            self.assertNotIn(node.path, paths)
            paths.add(node.path)

    return test_nodes


for gproject in all_gfiles:
    test_name = _gen_test_name('nodes', gproject)
    test = test_generator_nodes(gproject)
    setattr(TestSequence, test_name, test)


def test_generator_raises(path):
    """Generate a function testing given `path`.

    :param path: gproject path to test
    :return: function
    """
    def test_raises(self):

        p = guerilla_parser.parse(path)

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


for gproject in all_gfiles:
    test_name = _gen_test_name('raises', gproject)
    test = test_generator_raises(gproject)
    setattr(TestSequence, test_name, test)


def test_generator_child_unique(path):
    """Generate a function testing given `path`.

    :param path: gproject path to test
    :return: function
    """
    def test_child_unique(self):

        p = guerilla_parser.parse(path)

        for node in p.nodes:

            child_names = set()

            for child in node.children:

                self.assertNotIn(child.name, child_names)

                child_names.add(child.name)

    return test_child_unique


for gproject in all_gfiles:
    test_name = _gen_test_name('child_unique', gproject)
    test = test_generator_child_unique(gproject)
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


for gproject in default_gprojects:
    test_name = _gen_test_name('set_plug_value', gproject)
    test = test_generator_set_plug_value(gproject)
    setattr(TestSequence, test_name, test)


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

        plug = node.get_plug("ColorMode")
        p.set_plug_value([(plug, 'divide')])

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


for gproject in default_gprojects:
    test_name = _gen_test_name('write_file', gproject)
    test = test_generator_write_file(gproject)
    setattr(TestSequence, test_name, test)


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
