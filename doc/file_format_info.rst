Guerilla file format info
=========================

Gathered notes about guerilla file format.

Get every class of type Plug
----------------------------

As we are outside Guerilla when parsing, we have to know the classes inherited
of ``Plug``. To do this, we execute and get the returned list of class from
this code snippet:

.. code-block:: python

    import inspect
    import guerilla

    for att in dir(guerilla):
        cl = getattr(guerilla, att)
        if not inspect.isclass(cl):
            continue
        if issubclass(cl, guerilla.Plug):
            print cl.__name__

This list of class is then put inside global variable
``plug_class_names``.

On Guerilla 1.4.17 it list:

* ``BakePlug``
* ``DynAttrPlug``
* ``ExpressionInput``
* ``ExpressionOutput``
* ``HostPlug``
* ``MeshPlug``
* ``Plug``
* ``UserPlug``

Introspecting Guerilla project files, I found few other, undocumented plug
types:

* ``HSetPlug``
* ``HVisiblePlug``
* ``HMattePlug``
* ``SceneGraphNodePropsPlug``
* ``SceneGraphNodeRenderPropsPlug``
* ``AttributePlug``
* ``AttributeShaderPlug``

Those types are `local overrides`. Overrides you apply directly on local
hierarchy nodes. Those plugs return ``guerilla.Plug`` when ``type()`` is called
on them.


What are implicit nodes?
------------------------

When Guerilla need to do a relation/modification to a node which is inside a
reference (alembic file for example), he can not do a simple
``set("$20.Plug",true)`` as the node having the plug (here ``$20``) is not
inside the gproject but inside the reference.

That's why, Guerilla has to do ``set("$19|Foo|Bar.Plug",true)``.

When we parse the file, we have no direct way to know what ``Foo`` and ``Bar``
are so we have a special node type ``UNKNOWN`` to still have nodes without
breaking the hierarchy.

Inside the parser code, those are called `implicit nodes`.
