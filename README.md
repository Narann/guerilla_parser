# Python Guerilla file parser

[![Build Status](https://travis-ci.org/Narann/guerilla_parser.svg?branch=master)](https://travis-ci.org/Narann/guerilla_parser)
[![Documentation Status](https://readthedocs.org/projects/guerilla-parser/badge/?version=latest)](https://readthedocs.org/projects/guerilla-parser/?badge=latest)

This python module provide an easy way to parse Guerilla files and navigate into parsed nodes and plugs.

## Code snippets

Parse given file:

```python
import guerilla_parser

# parse and get object interfacing the parsed document
p = guerilla_parser.parse("/path/to/my_project.gproject")
```

Print the document revision format:

```python
print p.doc_format_rev
# 19
```

Iterate over every node of the parsed file:

```python
for node in p.nodes:
    print node.path, node.type
```

Get root node:

```python
# root node is the document node if you are parsing a gproject
doc = p.root

print doc.get_plug('FirstFrame').value
print doc.get_plug('LastFrame').value
```

Get node name, path and type:

```python
print node.name, node.path, node.type
```

Get parent node:

```python
print node.parent
```

Get node display name (useful for aov nodes):

```python
print node.display_name
```

Iterate over every children of a node:

```python
for child in node.children:

    print child.path
```

Get node children by its name:

```python
node.get_child("RenderPass")
```

Iterate over render passes, render ayers and aovs:

```python
rp_iter = (n for n in p.nodes if n.type == 'RenderPass')

for rp in rp_iter:

    rl_iter = (n for n in rp.children if n.type == 'RenderLayer')

    for rl in rl_iter:

        aov_iter = (n for n in rp.children if n.type == 'LayerOut')

        for aov in aov_iter:

            print aov.path, aov.display_name
```

Iterate over every plug of a node:

```python
for plug in node.plugs:

    print plug.path, plug.type

    if plug.input:  # does node plug have incoming plug?
        print plug.input.path, "->", plug.path
    else:  # no incoming plug? get it's value
        print plug.value

    # if this plug is connected to other plug, we print it
    for out_plug in plug.outputs:
        print plug.path, "->", out_plug.path
```

Get specified plug (from its _PlugName_ attribute):

```python
node.get_plug('NodePos')
```

Get node from it's path:

```python
rp = p.path_to_node('|RenderPass')
```

## Known limitations

* Missing lua to python conversion `'{}'`.
* Missing lua to python conversion `'types.color'`.
* Missing lua to python conversion `'types.float {min=1,max=10}'`.
* Missing lua to python conversion `'matrix.create{-1,0,0,0,0,1,0,0,0,0,-1,0,0,0,0,1}'`.
* Missing lua to python conversion `'transform.create{-1,0,0,0,0,1,0,0,0,0,-1,0,0,0,0,1}'`.
* Curve unpacking is not supported.
