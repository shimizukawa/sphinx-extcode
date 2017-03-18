#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
sys.path.insert(0, os.path.abspath('.'))


# -- General configuration ------------------------------------------------
sys.path.insert(0, os.path.abspath('..'))

extensions = [
    'sphinx.ext.githubpages',
    'extcode',
]

extcode = {
    #'rendered-block': 'vertical',
}

source_suffix = '.rst'
master_doc = 'index'
project = 'sphinx-extcode'
copyright = '2017, shimizukawa'
author = 'shimizukawa'
version = release = '0.1'
language = 'ja'
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
pygments_style = 'sphinx'

html_theme = 'alabaster'

