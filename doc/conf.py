"""Guerilla parser documentation build configuration file"""

import os.path
import sys

_doc_path = os.path.split(__file__)[0]
_repo_path = os.path.split(_doc_path)[0]
sys.path.append(os.path.join(_repo_path, 'src'))

import guerilla_parser

import sphinx_rtd_theme

# Extensions
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode'
]


html_theme = "sphinx_rtd_theme"

html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'Guerilla parser'
copyright = u'2016-2018, Dorian Fevrier'

# Version
version = guerilla_parser.__version__
release = version

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['static', 'template']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of prefixes to ignore for module listings
modindex_common_prefix = ['guerilla_parser.']

# coding highlight
highlight_language = 'python'

# copy rst source files to output for reference
html_copy_source = True


# autodoc
autodoc_default_flags = ['members', 'undoc-members', 'show-inheritance']
autodoc_member_order = 'bysource'

# intersphinx
intersphinx_mapping = {'python': ('https://docs.python.org/2', None)}


def autodoc_skip(app, what, name, obj, skip, options):
    """Don't skip __init__ method for autodoc"""
    if name == '__init__':
        return False

    return skip


def setup(app):
    app.connect('autodoc-skip-member', autodoc_skip)

