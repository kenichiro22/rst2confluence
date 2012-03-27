#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import codecs

from docutils import nodes, writers

# sys.stdout = codecs.getwriter('shift_jis')(sys.stdout)

class Writer(writers.Writer):
    def translate(self):
        self.visitor = ConfluenceTranslator(self.document)
        self.document.walkabout(self.visitor)
        self.output = self.visitor.astext()


class ConfluenceTranslator(nodes.NodeVisitor):
    """Write output in Confluence Wiki format.

    References:
    * ReST: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html
    * Confluence Wiki: http://confluence.atlassian.com/display/DOC/Confluence+Notation+Guide+Overview
    """

    empty_methods = [
        'visit_document', 'depart_document',
        'depart_Text',
        'depart_list_item',
        'visit_target', 'depart_target',
#        'depart_field_list',
#        'visit_field', 'depart_field',
#        'depart_field_body',
        'visit_decoration', 'depart_decoration',
        'depart_footer',
        'visit_tgroup', 'depart_tgroup',
        'visit_colspec', 'depart_colspec',
        'depart_image',
    ]

    keepLineBreaks = False

    def __init__(self, document):
        nodes.NodeVisitor.__init__(self, document)
        self.settings = document.settings

        self.content = []

        self.first = True
        self.list_level = 0
        self.section_level = 1
        self.list_counter = -1

        self.list_prefix = []

        self.table = False
        self.table_header = False

        self.quote_level = 0

        # Block all output
        self.block = False

        for method in self.empty_methods:
            setattr(self, method, lambda n: None)

    def _add(self, string):
        if not self.block:
            self.content.append(string)

    def _indent(self):
        self._add(" " * self.list_level * 2)

    def _newline(self, number=1):
        self._add("\n"*number)

    def astext(self):
        return "".join(self.content)

    def unknown_visit(self, node):
        raise Exception("Unknown visit on line %s: %s." % (node.line, repr(node)))

    def unknown_departure(self, node):
        raise Exception("Unknown departure on line %s: %s." % (node.line, repr(node)))


    def visit_paragraph(self, node):
        if not self.first and not self.table:
            self._newline()

    def depart_paragraph(self, node):
        if not self.table:
            self._newline()
        self.first = False

    def visit_Text(self, node):
        string = node.astext().replace("[", "\[")
        if self.keepLineBreaks:
            self._add(string)
        else:
            # rst line break shoud be removed.
            self._add(" ".join(string.splitlines()))

    def visit_emphasis(self, node):
        self._add("_")

    def depart_emphasis(self, node):
        self._add("_")

    def visit_strong(self, node):
        self._add("*")

    def depart_strong(self, node):
        self._add("*")

    def visit_section(self, node):
        self.section_level += 1

    def depart_section(self, node):
        self.section_level -= 1

    def visit_reference(self, node):
        if 'refuri' in node:
            if node.children[0].astext() == node["refuri"]:
                self._add(node.children[0].astext())
            else:
                self._add("[")
                self._add(node.children[0].astext() + "|")
                self._add(node["refuri"] + "]")
        else:
            assert 'refid' in node, \
                   'References must have "refuri" or "refid" attribute.'
            self._add("[")
            self._add(node.children[0].astext() + "|")
            self._add("#" + node["refid"] + "]")

        raise nodes.SkipNode

    def depart_reference(self, node):
        pass

    def visit_literal_block(self, node):
        self.keepLineBreaks = True
        self._add('{code}')
        self._newline()

    def depart_literal_block(self, node):
        self.keepLineBreaks = False
        self._newline()
        self._add('{code}')
        self._newline()

    def visit_literal(self, node):
        self._add('{{')

    def depart_literal(self, node):
        self._add('}}')

    def visit_footer(self, node):
        pass

    #----------------------------------------------------

    # title
    def visit_title(self, node):
        if not self.first:
            self._newline()
        self._add("h" + str(self.section_level) + ". ")

    def depart_title(self, node):
        self._newline(2)
        self.first = True

    def visit_subtitle(self,node):
        self._add("h" + str(self.section_level) + ". ")

    def depart_subtitle(self,node):
        self._newline(2)

    # bullet list
    def visit_bullet_list(self, node):
        self.list_level += 1
        self.list_prefix.append("*")

    def depart_bullet_list(self, node):
        self.list_level -= 1
        self.list_prefix.pop()

    def visit_list_item(self, node):
        self._add("".join(self.list_prefix) + " ")
        self.first = True

    # enumerated list
    def visit_enumerated_list(self, node):
        self.list_prefix.append("#")
        self.list_counter = 1
        self.list_level += 1

    def depart_enumerated_list(self, node):
        self.list_counter = -1
        self.list_level -= 1
        self.list_prefix.pop()

    # paragraph
    def visit_note(self, node):
        self._add("{note}")
        self._newline()

    def depart_note(self, node):
        self._add("{note}")
        self._newline(2)

    def visit_warning(self, node):
        self._add("{warning}")

    def depart_warning(self, node):
        self._add("{warning}")
        self._newline(2)

    # image
    def visit_image(self, node):
        uri = node['uri']
        atts = {}
        if 'alt' in node:
            atts['alt'] = node['alt']
        if 'width' in node:
            atts['width'] = node['width']
        if 'height' in node:
            atts['height'] = node['height']
        if 'align' in node:
            atts['align'] = node['align']
        attributes = []
        for att in atts.iterkeys():
            attributes.append(att + "=" + atts[att])

        self._add("!")
        self._add(uri)
        if attributes:
            self._add("|")
            self._add(",".join(attributes))
        self._add("!")
        self._newline()

    def visit_table(self, node):
        self.table = True
#        raise nodes.SkipNode

    def depart_table(self, node):
        self.table = False
        self._newline()

    def visit_thead(self, node):
        # self._add("||")
        self.table_header = True

    def depart_thead(self, node):
        self.table_header = False

    def visit_tbody(self, node):
        pass

    def depart_tbody(self, node):
        pass

    def visit_row(self, node):
        pass

    def depart_row(self, node):
        if self.table_header:
            self._add("||")
        else:
            self._add("|")

        self._newline()

    def visit_entry(self, node):
        if self.table:
            if self.table_header:
                self._add("||")
            else:
                self._add("|")

    def depart_entry(self, node):
        pass

    """Definition list
    Confluence wiki does not support definition list
    Definition list is converted to h6 section
    """
    def visit_definition_list(self, node):
        pass

    def depart_definition_list(self, node):
        pass

    def visit_definition_list_item(self, node):
        pass

    def depart_definition_list_item(self, node):
        pass

    def visit_term(self, node):
        self._add("h6. ")

    def depart_term(self, node):
        self._newline()

    def visit_definition(self, node):
        self.first = True

    def depart_definition(self, node):
        self._newline()

    def visit_block_quote(self, nde):
        if self.quote_level == 0:
            self._add("{quote}")

        self.quote_level += 1

    def depart_block_quote(self, nde):
        if self.quote_level == 1:
            self._add("{quote}")
            self._newline()

        self.quote_level -= 1

    def invisible_visit(self, node):
        """Invisible nodes should be ignored."""
        raise nodes.SkipNode

    visit_comment = invisible_visit

    def visit_topic(self, node):
        self._add("{toc}")
        self._newline(2)
        raise nodes.SkipNode

    def depart_topic(self, node):
        pass

    def visit_system_message(self, node):
        self._add(
            "{warning:title="
            + "System Message: %s/%s" % (node['type'], node['level'])
            + "}")
        self._newline()
        self._add('{{' + node['source'] + "}}#" + str(node['line']))

    def depart_system_message(self, node):
        self._add("{warning}")
