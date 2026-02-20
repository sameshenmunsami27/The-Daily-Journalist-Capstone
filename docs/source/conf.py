import os
import sys
import django

# Path setup 
# We point Sphinx to the root 'News Application' folder
sys.path.insert(0, os.path.abspath('../..'))

# Tells Sphinx where your Django settings are located
os.environ['DJANGO_SETTINGS_MODULE'] = 'news_project.settings'

# This initializes Django so Sphinx can read the models and MySQL setup
django.setup()


# Project information
project = 'The Daily Journalist'
copyright = '2026, Sameshen Munsami'
author = 'Sameshen'
release = '1.0.0'


#  General configuration 
extensions = [
    'sphinx.ext.autodoc',      # Core library to grab docstrings
    'sphinx.ext.viewcode',     # Adds links to your highlighted source code
    'sphinx.ext.napoleon',     # Support for Google/NumPy style docstrings
    'sphinx.ext.githubpages',  # Useful if you ever host on GitHub
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '.venv', 'venv']


#  Options for HTML output 
# We use the 'Read the Docs' theme for a professional look
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']