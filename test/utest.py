import unittest

import sys

import os.path


def get_parent_dir(path):
    return os.path.abspath(os.path.join(os.path.abspath(path), os.pardir))

toto = os.path.abspath(os.path.join(
        os.path.abspath(os.path.join(
            os.path.abspath(os.path.join(
                os.path.abspath(__file__), os.pardir)), os.pardir)), os.pardir))

test_dir = get_parent_dir(__file__)

sys.path.append(get_parent_dir(test_dir)+'/src')

from guerilla_parser import GuerillaParser, GuerillaNode
import guerilla_parser.util as grl_util


gprojects = [test_dir+'/gproject/1.4.13_01/1.4.13_01.gproject',
             test_dir+'/gproject/2.0.0a31_01/2.0.0a31_01.gproject']


class TestStringMethods(unittest.TestCase):

    def test_read(self):

        p = GuerillaParser.from_file(gprojects[1])

        self.assertEqual(p.doc_format_rev, 19)
        self.assertEqual(p.document.name, 'LUIDocument')
        self.assertEqual(p.document.get_plug('InternalDirectLighting').value, True)
        self.assertEqual(p.document.get_plug('InvertT').value, False)
        self.assertEqual(p.document.get_plug('LastFrame').value, 50)
        self.assertEqual(p.document.get_plug('Membership').value, "All")
        self.assertEqual(p.document.get_plug('CurveWidthShape').value, 1.5)
        self.assertEqual(p.pref.get_plug('LightAmbient').value, [0, 0, 0, 1])
        self.assertEqual(p.pref.get_plug('LightSpecular').value, [0.5, 0.5, 0.5, 1])
        self.assertEqual(p.pref.get_plug('SearchPathTexture').value, "")

        for node in p.nodes:
            for child in node.children:
                self.assertIs(node.get_child(child.name), child)

            for plug in node.plugs:
                self.assertIs(node.get_plug(plug.name), plug)

        aov = grl_util.aov_node(p, 'RenderPass', 'Layer', 'Beauty')

        self.assertIsInstance(aov, GuerillaNode)
        self.assertEqual(aov.path, "LUIDocument|RenderPass|Layer|Input1")

        rp_iter = (n for n in p.nodes if n.type == 'RenderPass')

        for rp in rp_iter:

            rl_iter = (n for n in rp.children if n.type == 'RenderLayer')

            for rl in rl_iter:

                for aov in rl.children:

                    self.assertEqual(aov.type, "LayerOut")

                    aov_2 = grl_util.aov_node(p, rp.name, rl.name, aov.display_name)

                    self.assertIs(aov, aov_2)

    def test_toto(self):

        p = GuerillaParser.from_file(
            gprojects[0],
            diagnose=False)

        print p.doc_format_rev
        d = p.document

        '''for node in p.nodes:
            print node.path'''

        for node in p.nodes:

            print node.path

            for plug in node.plugs:

                if plug.input:
                    print "{plug.input.path} -> {plug.path}".format(**locals())

                # node.out_attr -> [(in_node.in_attr), ...]
                for out_plug in plug.outputs:
                    print "{plug.path} -> {out_plug.path}".format(**locals())

        ###########################################################################
        # iterate over render pass/layer/aov
        ###########################################################################
        # build an iterator over render pass nodes
        rp_iter = (n for n in p.nodes if n.type == 'RenderPass')

        # iter over render passes
        for rp in rp_iter:

            # iter over render layers
            for rl in rp.children:

                # iter over aovs
                for aov in rl.children:
                    print aov.path, aov.display_name

        '''def print_children(node):
            for child in node.children:
                print child.path
                print_children(child)

        for node in p.document.children:
            print node.path
            print_children(node)'''

        # p.dump(True)
        print p.objs.keys()
        node = p.objs[33]
        p.set_plug_value([(node.get_plug("ColorMode"), 'divide')])


if __name__ == '__main__':
    unittest.main()