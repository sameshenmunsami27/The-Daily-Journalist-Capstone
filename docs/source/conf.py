import os
import sys
import django
from django.conf import settings
from django.core.management import call_command
from unittest.mock import MagicMock

# Path setup 
sys.path.insert(0, os.path.abspath('../..'))

# --- THE "STRICT" BYPASS START ---
if not settings.configured:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'news_project.settings'
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:', # Temporary database in RAM
            }
        },
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'django.contrib.admin',
            'django.contrib.sessions',
            'django.contrib.messages',
            'news', 
        ],
        SECRET_KEY='docs-build-key',
    )
    django.setup()
    
    # THIS IS THE KEY: Create the tables in the dummy database
    try:
        call_command('migrate', verbosity=0, interactive=False)
    except Exception:
        pass

# Mocking migrations to prevent further DB issues
class MockMigrator:
    def __getattr__(self, name): return MagicMock()
sys.modules['django.db.migrations'] = MockMigrator()
# --- THE "STRICT" BYPASS END ---

# Project information
project = 'The Daily Journalist'
copyright = '2026, Sameshen Munsami'
author = 'Sameshen'
release = '1.0.0'

# General configuration 
extensions = [
    'sphinx.ext.autodoc',      # Core library to grab docstrings
    'sphinx.ext.viewcode',     # Adds links to your highlighted source code
    'sphinx.ext.napoleon',     # Support for Google/NumPy style docstrings
    'sphinx.ext.githubpages',  # Useful if you ever host on GitHub
]

templates_path = ['_templates']
exclude_patterns = [
    '_build', 'Thumbs.db', '.DS_Store', 
    '.venv', 'venv', '**/migrations/*', 'lib'
]

# Options for HTML output 
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Fix for Python 3.13 / Sphinx ValueError
def setup(app):
    from sphinx.util import inspect
    
    orig_object_description = inspect.object_description
    
    def patched_object_description(obj, *args, **kwargs):
        try:
            return orig_object_description(obj, *args, **kwargs)
        except (ValueError, TypeError):
            return repr(obj)
            
    inspect.object_description = patched_object_description