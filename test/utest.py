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

sys.path.append(root_dir+'/src')

import guerilla_parser
import guerilla_parser.util as grl_util


default_gprojects = [test_dir+'/gproject/1.4.14_01_default/1.4.14_01_default.gproject',
                     test_dir+'/gproject/2.0.0a31_02_default/2.0.0a31_02_default.gproject']

default_glayers = [test_dir+'/gproject/1.4.14_01_default/1.4.14_01_default.glayer',
                   test_dir+'/gproject/2.0.0a31_02_default/2.0.0a31_02_default.glayer']

default_grendergraphs = [test_dir+'/gproject/1.4.14_01_default/1.4.14_01_default.grendergraph',
                         test_dir+'/gproject/2.0.0a31_02_default/2.0.0a31_02_default.grendergraph']

gprojects = [test_dir+'/gproject/1.4.13_01/1.4.13_01.gproject',
             test_dir+'/gproject/2.0.0a31_01/2.0.0a31_01.gproject']

all_gfiles = [f for f in default_gprojects]
all_gfiles += [f for f in default_glayers]
all_gfiles += [f for f in default_grendergraphs]


class TestDefaultGProjects(unittest.TestCase):

    def test_default_gprojects(self):

        for gproject in default_gprojects:

            p = guerilla_parser.parse(gproject)

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

    def test_default_glayers(self):

        for gproject in default_glayers:

            p = guerilla_parser.parse(gproject)

            root = p.root

            self.assertEqual(root.id, 1)
            self.assertEqual(root.name, 'RenderPass')
            self.assertEqual(root.type, 'RenderPass')
            self.assertEqual(root.get_plug('AutoBuildTextures').value, True)
            self.assertEqual(root.get_plug('BalanceReyesDistribution').value, False)
            self.assertEqual(root.get_plug('BrdfSamples').value, 16)
            self.assertEqual(root.get_plug('ColorMode').value, "multiply")
            self.assertEqual(root.get_plug('DeepCompression').value, 0.1)
            self.assertEqual(root.get_plug('DefaultSurfaceColor').value, [0.0, 0.0, 0])


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

    def test_aov(self):
        """test render pass render layer and aov particularities"""

        for gproject in default_gprojects:

            p = guerilla_parser.parse(gproject)

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

    def test_path_to_node(self):
        """check returned path can be used to find node back"""
        for gproject in all_gfiles:
            p = guerilla_parser.parse(
                gproject,
                diagnose=False)

            for node in p.nodes:
                self.assertEqual(node, p.path_to_node(node.path))

    def test_raises(self):
        """"""
        for gproject in default_gprojects:

            p = guerilla_parser.parse(gproject)

            root_node = p.root

            with self.assertRaises(guerilla_parser.PathError):
                root_node.path()

            with self.assertRaises(guerilla_parser.ChildError):
                root_node.get_child('TAGADAPOUETPOUET')

            with self.assertRaises(guerilla_parser.PathError):
                p.path_to_node('TAGADAPOUETPOUET')

            with self.assertRaises(guerilla_parser.PathError):
                grl_util.aov_node(p, 'RenderPass', 'Layer', 'TAGADAPOUETPOUET')

    def test_set_plug_value(self):

        for gproject in default_gprojects:

            p = guerilla_parser.parse(gproject)

            node = p.path_to_node("|Preferences|RenderViewport")

            plug = node.get_plug("ColorMode")
            self.assertEqual(plug.value, 'multiply')
            p.set_plug_value([(plug, 'divide')])
            self.assertEqual(plug.value, 'divide')

    def test_write_file(self):

        for gproject in default_gprojects:

            _, tmp_file = tempfile.mkstemp()

            p = guerilla_parser.parse(
                gproject,
                diagnose=False)

            p.write(tmp_file)

            # no change
            self.assertFalse(p.has_changed)
            self.assertTrue(filecmp.cmp(gproject, tmp_file))

            node = p.path_to_node("|Preferences|RenderViewport")

            plug = node.get_plug("ColorMode")
            p.set_plug_value([(plug, 'divide')])

            p.write(tmp_file)

            # has changed
            self.assertTrue(p.has_changed)
            self.assertFalse(filecmp.cmp(gproject, tmp_file))

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


if __name__ == '__main__':
    unittest.main()
