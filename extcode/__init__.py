# -*- coding: utf-8 -*-
"""
    sphinxcontrib.extcode
    ~~~~~~~~~~~~~~~~~~~~~~

    This package is a namespace package that contains all extensions
    distributed in the ``sphinx-contrib`` distribution.

    :copyright: Copyright 2007-2013 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import os
from os import path
import re

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.io import DocTreeInput, StringOutput
from docutils.readers.doctree import Reader as DoctreeReader
from docutils.core import Publisher, publish_doctree
from sphinx import addnodes
from sphinx.util.nodes import set_source_info
from sphinx.util.osutil import ensuredir, copyfile
from sphinx.directives.code import CodeBlock
from sphinx.environment import SphinxStandaloneReader
from sphinx.writers.html import HTMLWriter as BaseWriter  #FIXME: need latex version or epub or...

RENDERED_BLOCK_CHOICES = ('horizontal', 'vertical', 'tab', 'toggle')

BASEDIR = path.dirname(path.abspath(__file__))
STATICDIR = path.join(BASEDIR, 'static')

#FIXME: `#:` is special comment for source, but it is batting with Sphinx document comment
# I need another special comment syntax. (as like as `#<label>` )
annotation_matcher = re.compile(r'^(.*[^\s])\s*#:([^:]+):$').match


class extcode(nodes.Element):
    """Extended code-block element"""


def sandbox_rst_parser(source, source_path=None, settings_overrides=None):
    """
    :param unicode source: reSTコンテンツ
    :param unicode source_path: Warning等で表示するためのソースファイルパス
    :param dict settings_orverrides: docutils settings
    :return: doctree
    :rtype: doctree
    """
    try:  #FIXME: htmlビルダー以外の場合にraiseする
        return publish_doctree(
                source=source,
                source_path=source_path,
                settings_overrides=settings_overrides)
    except:
        return None


class SandboxDoctreeReader(DoctreeReader):
    transforms = SphinxStandaloneReader.transforms

    def get_transforms(self):
        return DoctreeReader.get_transforms(self) + self.transforms


class Writer(BaseWriter):

    def translate(self):
        env = self.builder.env
        # transformでpending_xrefが発生するので、resolve_referenceが必要
        # ただし、この処理はsandboxの外にあるグローバルなenvに依存する
        env.resolve_references(self.document, env.docname, self.builder)
        super(Writer, self).translate()


def sandbox_partial_builder(doctree, env):
    env.process_downloads(env.docname, doctree)
    for domain in env.domains.values():
        domain.process_doc(env, env.docname, doctree)
    env.resolve_references(doctree, env.docname, env.app.builder)
    if not hasattr(env.app.builder, 'dlpath'):
        # FIXME: builders.html.StandaloneHTMLBuilder.write_doc で設定される属性のため、この時点では存在しない
        env.app.builder.dlpath = '_downloads'
        env.app.builder.fignumbers = env.toc_secnumbers.get(env.docname, {})
        env.app.builder.secnumbers = env.toc_secnumbers.get(env.docname, {})
    pub = Publisher(
            reader=SandboxDoctreeReader(),
            writer=Writer(env.app.builder),
            source=DocTreeInput(doctree),
            destination_class=StringOutput,
            )
    pub.set_components(None, 'restructuredtext', None)
    defaults = env.settings.copy()
    defaults['output_encoding'] = 'unicode'
    pub.process_programmatic_settings(None, defaults, None)
    pub.set_destination(None, None)
    out = pub.publish(enable_exit_status=False)
    return pub.writer.parts['fragment']


def annotation_parser(argument):
    if argument:
        doc = sandbox_rst_parser(argument)
        if doc is not None:
            docinfo = doc[0]
            annotations = nodes.field_list()
            annotations.source, annotations.line = docinfo.source, docinfo.line
            annotations.extend(docinfo.children)
            return annotations
    return []


def rendered_block_choice(argument):
    return directives.choice(
            argument,
            RENDERED_BLOCK_CHOICES)

def rendered_image_parser(argument):
    return directives.uri(argument)


def build_table(elements, colwidths, head_rows=0, stub_columns=0, attrs={}):
    """build_table bulid table node from elements list of list.

    :param elements:
       [[col11, col12, col13], [col21, col22, col23], ...]: col is node.
    :type elements: list of list of node
    :param heads: header line nodes
    :type heads: list of node
    :param attrs: all entry node aim attrs
    """
    cols = len(colwidths)
    table = nodes.table()
    tgroup = nodes.tgroup(cols=cols)
    table += tgroup

    #colspec
    for colwidth in colwidths:
        colspec = nodes.colspec(colwidth=colwidth)
        if stub_columns:
            colspec['stub'] = 1
            stub_columns -= 1
        tgroup += colspec

    #head
    if head_rows:
        thead = nodes.thead()
        tgroup += thead
        head_elements, elements = elements[:head_rows], elements[head_rows:]
        for heads in head_elements:
            row = nodes.row()
            for cell in heads:
                entry = nodes.entry(**attrs)
                entry += cell
                row += entry
            thead += row

    #body
    tbody = nodes.tbody()
    tgroup += tbody
    for row_cells in elements:
        row = nodes.row()
        for cell in row_cells:
            entry = nodes.entry(**attrs)
            entry += cell
            row += entry
        tbody += row

    return table


class ExtCode(CodeBlock):

    option_spec = {}
    option_spec.update(CodeBlock.option_spec)
    extra_option_spec = {
        #: display rendered reST by 'horizontal', 'vertical' or 'tab'
        'rendered-block': rendered_block_choice,
        #: display rendered reST by specified image file
        'rendered-image': rendered_image_parser,
        #: annotation definitions used by field-list
        'annotations': annotation_parser,
        #: display inline annotation label
        'annotate-inline': directives.flag,
        #: display annotation ndescription table
        'annotate-block': directives.flag,
    }
    option_spec.update(extra_option_spec)

    def run(self):
        env = self.state.document.settings.env
        extcode_config = env.app.config.extcode

        if not extcode_config:
            if all(opt not in self.options for opt in self.extra_option_spec):
                return super(ExtCode, self).run()  # nothing to do special

        rendered_block = self.options.get('rendered-block',
                                          extcode_config.get('rendered-block'))

        line_annotations = {}
        annotations = self.options.get('annotations', [])
        annotationsmap = dict((k.astext(), v) for k, v in annotations)
        for i,c in enumerate(self.content):
            match = annotation_matcher(c)
            if match:
                self.content[i], label = match.groups()
                if label in annotationsmap:
                    line_annotations[i] = (label, annotationsmap[label])
                else:
                    #TODO: warning
                    line_annotations[i] = (label, None)

        # get literal from modified self.content
        literal = super(ExtCode, self).run()[0]
        # line_annotations attribute will be used for writer (not yet)
        literal['line_annotations'] = line_annotations

        wrapper = extcode(classes=['extcode'])
        set_source_info(self, wrapper)

        #check: can parse rst? and partial build?
        try:
            partial_doc = sandbox_rst_parser(
                    u'\n'.join(self.content),
                    env.doc2path(env.docname),
                    env.settings)
            partial_out = sandbox_partial_builder(partial_doc, env)
        except Exception as e:
            env.warn(
                    env.docname,
                    u'extcode: partial build failed: %s' % str(e),
                    lineno=self.lineno)
            partial_doc = None
            partial_out = None

        if literal['language'] == 'rst' and rendered_block:
            wrapper['classes'].append(
                    'extcode-layout-' + rendered_block)

            rendered = nodes.container()
            set_source_info(self, rendered)

            only_html = addnodes.only(expr='html')
            set_source_info(self, only_html)
            only_html += nodes.raw(
                    partial_out,
                    partial_out,
                    format='html',
                    classes=['extcode-rendered'])
            rendered += only_html

            if 'rendered-image' in self.options:
                only_xml = addnodes.only(expr='xml')
                set_source_info(self, only_xml)
                only_xml += nodes.image(self.options['rendered-image'], uri=self.options['rendered-image'])
                rendered += only_xml


            #FIXME: need translation support
            make_text = lambda t: nodes.inline(t, t)

            if rendered_block == 'horizontal':
                table = build_table(
                        [[make_text('literal'), make_text('rendered')],
                         [literal, rendered]],
                        [1, 1],
                        head_rows=1,
                        attrs={'classes': ['extcode-layout']})
                table.setdefault('classes', []).append('extcode-layout')
                wrapper.append(table)

            elif rendered_block == 'vertical':
                table = build_table(
                        [[make_text('literal'), literal],
                         [make_text('rendered'), rendered]],
                        [2, 8],
                        stub_columns=1,
                        attrs={'classes': ['extcode-layout']})
                table.setdefault('classes', []).append('extcode-layout')
                wrapper.append(table)

            else:  # toggle, tab
                wrapper.append(literal)
                wrapper.append(rendered)
        else:
            wrapper.append(literal)

        if line_annotations and 'annotate-inline' in self.options:
            prefix = '... '  #TODO prefixi customization
            contents = []
            for i in range(0, len(self.content)):
                label, value = line_annotations.get(i, ('', None))
                line = nodes.line()
                if label and value:
                    #FIXME: label and explanation need translation support
                    abbr = nodes.abbreviation(label, label)  #TODO: label customization (i.e. render with number)
                    abbr['explanation'] = value.astext()
                    line.append(nodes.inline(prefix, prefix))
                    line.append(abbr)
                elif label:
                    line.append(nodes.inline(prefix, prefix))
                    line.append(nodes.Text(label, label))
                contents.append(line)
            overlay = nodes.line_block(classes=['extcode-overlay'])
            set_source_info(self, overlay)
            overlay.extend(contents)
            wrapper.append(overlay)

        if annotations and 'annotate-block' in self.options:
            annotations['classes'] = ['extcode-annotations']
            set_source_info(self, annotations)
            wrapper.append(annotations)

        return [wrapper]


def visit_extcode_node_html(self, node):
    self.body.append(self.starttag(node, 'div'))


def depart_extcode_node_html(self, node=None):
    self.body.append('</div>\n')


def visit_extcode_node_xml(self, node):
    import pdb;pdb.set_trace()
    self.body.append(self.starttag(node, 'div'))


def depart_extcode_node_xml(self, node=None):
    import pdb;pdb.set_trace()
    self.body.append('</div>\n')


def on_doctree_resolved(self, doctree, docname):
    if self.builder.name in ('singlehtml', 'html', 'epub'):
        return

    #FIXME: remove extcode nodes if not html output

    def find_extcode_removable_subnode(node):
        if (isinstance(node, nodes.compound) and
            'extcode-rendered' in node['classes']):
            return True
        if (isinstance(node, nodes.line_block) and
            'extcode-overlay' in node['classes']):
            return True
        return False

    for node in doctree.traverse(find_extcode_removable_subnode):
        node.parent.remove(node)


def on_html_coolect_pages(app):
    """on copy static files"""
    app.info(' extcode', nonl=1)
    ensuredir(path.join(app.outdir, '_static'))
    for f in os.listdir(STATICDIR):
        copyfile(
                path.join(STATICDIR, f),
                path.join(app.outdir, '_static', f))

    return []  #no pages


def setup(app):
    dummy_func = lambda *args, **kw: None
    app.add_node(extcode,
            html=(visit_extcode_node_html, depart_extcode_node_html),
            xml=(visit_extcode_node_xml, depart_extcode_node_xml),
            latex=(dummy_func, dummy_func),
            text=(dummy_func, dummy_func),
            man=(dummy_func, dummy_func),
            texinfo=(dummy_func, dummy_func),
            )
    app.add_directive('code-block', ExtCode)
    app.add_stylesheet('extcode.css')
    app.add_javascript('extcode.js')
    app.add_config_value('extcode', {}, 'env')
    app.connect("html-collect-pages", on_html_coolect_pages)
    app.connect("doctree-resolved", on_doctree_resolved)
