# Configuration file for the Sphinx documentation builder.

import os
import sys
sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------

project = 'DZ14'
copyright = '2024, Oleksandr Miestoivanchenko'
author = 'Oleksandr Miestoivanchenko'
release = '1.0.0'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',  # Include documentation from docstrings
    'sphinx.ext.napoleon',  # Support for NumPy and Google style docstrings
    'sphinx.ext.intersphinx',  # Link to other project's documentation
    'sphinx.ext.viewcode',  # Add links to highlighted source code
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 'venv']

# If you have your own conf.py file, uncomment the following line:
# master_doc = 'index'

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Optionally, you can add custom CSS
html_css_files = [
    'css/custom.css',
]

# Optionally, you can add custom JavaScript
html_js_files = [
    'js/custom.js',
]


