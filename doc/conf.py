"""Guerilla parser documentation build configuration file"""

import os

import sphinx_rtd_theme

# Extensions
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.extlinks',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    #'lowdown'
]


html_theme = "sphinx_rtd_theme"

html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'Guerilla parser'
copyright = u'2016, Dorian Fevrier'

# Version
import guerilla_parser

version = guerilla_parser.__version__
release = version

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['static', 'template']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of prefixes to ignore for module listings
modindex_common_prefix = ['guerilla_parser.']


# -- HTML output --------------------------------------------------------------

# If True, copy source rst files to output for reference
html_copy_source = True


# -- Autodoc ------------------------------------------------------------------

autodoc_default_flags = ['members', 'undoc-members', 'show-inheritance']
autodoc_member_order = 'bysource'


def autodoc_skip(app, what, name, obj, skip, options):
    """Don't skip __init__ method for autodoc"""
    if name == '__init__':
        return False

    return skip


# -- Intersphinx --------------------------------------------------------------

intersphinx_mapping = {'python':('http://docs.python.org/', None)}


# -- Setup --------------------------------------------------------------------

def setup(app):
    app.connect('autodoc-skip-member', autodoc_skip)

