from .exception import ChildError, PathError
from .parser import GuerillaParser
from .node import GuerillaNode
from .plug import GuerillaPlug

__version__ = "0.8.0"


# move the most useful function on top
parse = GuerillaParser.from_file
