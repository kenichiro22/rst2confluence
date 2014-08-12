#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import codecs
import urllib

from docutils import nodes, writers

# sys.stdout = codecs.getwriter('shift_jis')(sys.stdout)

class Writer(writers.Writer):

    #Prevent the filtering of the Meta directive.
    supported = ['html']

    def translate(self):
        self.visitor = ConfluenceTranslator(self.document)
        self.visitor.meta = {}
        self.document.walkabout(self.visitor)
        #Save some metadata as a comment, one per line.
        self.output = unicode()
        for key in self.visitor.meta.keys():
            self.output += "###. meta/%s:%s\n" % (key, self.visitor.meta[key])

        if len(self.visitor.meta.keys()) > 0:
            self.output += "\n"
        self.output += self.visitor.astext()


class ConfluenceTranslator(nodes.NodeVisitor):
    """Write output in Confluence Wiki format.

    References:
    * ReST: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html
    * Confluence Wiki: http://confluence.atlassian.com/display/DOC/Confluence+Notation+Guide+Overview
    """

    empty_methods = [
        'depart_Text',
        'depart_colspec',
        'depart_decoration',
        'depart_document',
        'depart_field',
        'depart_field_name',
        'depart_footer',
        'depart_image',
        'depart_line_block',
        'depart_list_item',
        'depart_meta',
        'depart_raw',
        'depart_target',
        'depart_tgroup',
        'visit_colspec',
        'visit_decoration',
        'visit_document',
        'visit_field',
        'visit_line',
        'visit_raw',
        'visit_tgroup'
    ]

    inCode = False
    keepLineBreaks = False
    lastTableEntryBar = 0
    docinfo = False
    meta = {}

    def __init__(self, document):
        nodes.NodeVisitor.__init__(self, document)
        self.settings = document.settings

        self.content = []

        self.first = True
        self.list_level = 0
        self.section_level = 0
        self.list_counter = -1

        self.list_prefix = [[]]
        self.lineBeginsWithListIndicator = False
        self.addedNewline = False

        self.table = False
        self.table_header = False

        self.quote_level = 0

        self.figure = False
        self.figureImage = False
        self.lastGalleryClass = ""

        self.inTitle = False

        self.openFootnotes = 0

        # Block all output
        self.block = False
        self.footnote = False
        self.field_body = False

        for method in self.empty_methods:
            setattr(self, method, lambda n: None)

    def _add(self, string):
        if not self.block:
            self.addedNewline = False
            self.content.append(string)

    def _indent(self):
        self._add(" " * self.list_level * 2)

    def _newline(self, number=1):
        if self.addedNewline and self.table:
            self.content[self.lastTableEntryBar] += "{div}"
            self.tableEntryDiv = True
        self._add("\n" * number)
        self.addedNewline = True
        self.lineBeginsWithListIndicator = False

    def _remove_last_newline(self):
        if self.addedNewline:
            self.content.pop(len(self.content) - 1)
            self.addedNewline = False

    def astext(self):
        return "".join(self.content)

    def unknown_visit(self, node):
        raise Exception("Unknown visit on line %s: %s." % (node.line, repr(node)))

    def unknown_departure(self, node):
        raise Exception("Unknown departure on line %s: %s." % (node.line, repr(node)))


    def visit_paragraph(self, node):
        if not self.first and not self.footnote and not self.field_body and self.list_level == 0:
            self._newline()
        if self.list_level > 0 and not self.lineBeginsWithListIndicator:
            self._add(" " * (self.list_level + (self.list_level > 0)))

    def depart_paragraph(self, node):
        if not self.footnote and not isinstance(node.parent, nodes.field_body):
            self._newline()
        self.first = False

    def visit_Text(self, node):
        string = node.astext()
        if not self.inCode:
            string = string.replace("[", "\[").replace('{', '&#123;').replace('}', '&#125;')
        if self.keepLineBreaks:
            self._add(string)
        else:
            # rst line break should be removed.
            self._add(" ".join(string.split('\n')))

    def visit_emphasis(self, node):
        self._add("_")

    def depart_emphasis(self, node):
        self._add("_")

    def visit_strong(self, node):
        self._add_space_when_needed()
        self._add("*")

    def depart_strong(self, node):
        self._add("*")

    def visit_section(self, node):
        self.section_level += 1

    def depart_section(self, node):
        self.section_level -= 1

    def cflAnchorValue(self, name):
        return name.replace("-", "").replace(" ", '').replace(u"ä", "a").replace(u"ö", "o").replace(u"ü", "u").replace(u"ß", "s")

    def visit_target(self, node):
        if not node.has_key("refid"):
            return
        self._add("{anchor:" + self.cflAnchorValue(node["refid"]) + "}")
        self._newline()

    def visit_reference(self, node):
        if 'refuri' in node:
            if node.children[0].astext() == node["refuri"] and "://" in node["refuri"]:
                if self.table and self._endswidth("|"):
                    self._add(" ")
                self._add(self.escapeUri(node.children[0].astext()))
            elif "://" in node["refuri"]:
                self._add("[")
                self._add(node.children[0].astext() + "|")
                self._add(self.escapeUri(node["refuri"]) + "]")
            else:
                self._add("[")
                self._add(node.children[0].astext() + "|")
                self._add(urllib.unquote(node["refuri"]) + "]")
        else:
            assert 'refid' in node, \
                   'References must have "refuri" or "refid" attribute.'
            self._add("[")
            self._add(node.children[0].astext() + "|")
            self._add("#" + self.cflAnchorValue(node["refid"]) + "]")

        raise nodes.SkipNode

    def escapeUri(self, uri):
        return uri.replace("[", "\[").replace("]", "\]")

    def depart_reference(self, node):
        pass

    def visit_footnote_reference(self, node):
        self.openFootnotes += 1
        self._add("^")
        self._add(node.children[0].astext())
        self._add("^")

        raise nodes.SkipNode

    def depart_footnote_reference(self, node):
        pass

    def visit_footnote(self, node):
        self.openFootnotes -= 1
        self.footnote = True
        self._newline()
        self._add("bq. ")

    def depart_footnote(self, node):
        self.footnote = False
        if self.openFootnotes == 0:
            self._newline()

    def visit_label(self, node):
        self._add("^")
        self._add(node.astext())
        self._add("^ ")

        raise nodes.SkipNode

    def depart_label(self, node):
        pass

    def visit_literal_block(self, node):
        self.keepLineBreaks = True
        self.inCode = True
        self._add('{code}')
        self._newline()

    def depart_literal_block(self, node):
        self.keepLineBreaks = False
        self.inCode = False
        self._newline()
        self._add('{code}')
        self._newline()

    def visit_literal(self, node):
        self._add_space_when_needed()
        self._add('{{')

    def depart_literal(self, node):
        self._add('}}')

    def visit_footer(self, node):
        pass

    #----------------------------------------------------

    # title
    def visit_title(self, node):
        if self.section_level == 0:
            self.section_level = 1
        if not self.first:
            self._newline()
        self._add("h" + str(self.section_level) + ". ")
        self.inTitle = True

    def depart_title(self, node):
        anchorname = self.cflAnchorValue(node.astext()).lower()
        self._add('{anchor:' + anchorname + '}');
        self._newline(2)
        self.first = True
        self.inTitle = False

    def visit_subtitle(self,node):
        self._add("h" + str(self.section_level) + ". ")

    def depart_subtitle(self,node):
        self._newline(2)

    # bullet list
    def visit_bullet_list(self, node):
        self.list_level += 1
        self.list_prefix[-1].append("*")

    def depart_bullet_list(self, node):
        self.list_level -= 1
        self.list_prefix[-1].pop()

    def visit_list_item(self, node):
        self._add("".join(self.list_prefix[-1]) + " ")
        self.first = True
        self.lineBeginsWithListIndicator = True

    # enumerated list
    def visit_enumerated_list(self, node):
        self.list_prefix[-1].append("#")
        self.list_counter = 1
        self.list_level += 1

    def depart_enumerated_list(self, node):
        self.list_counter = -1
        self.list_level -= 1
        self.list_prefix[-1].pop()

    # admonitions
    def visit_info(self, node):
        self._add("{info}")
        self.do_visit_admonition()

    def depart_info(self, node):
        self._add("{info}")
        self.do_depart_admonition()

    def visit_note(self, node):
        self._add("{note}")
        self.do_visit_admonition()

    def depart_note(self, node):
        self._add("{note}")
        self.do_depart_admonition()

    def visit_tip(self, node):
        self._add("{tip}")
        self.do_visit_admonition()

    def depart_tip(self, node):
        self._add("{tip}")
        self.do_depart_admonition()

    def visit_docinfo(self, node):
        self.table = True
        self.docinfo = True

    def visit_meta(self, node):
        name = node.get('name')
        content = node.get('content')
        self.meta[name] = content

    def depart_docinfo(self, node):
        self.table = False
        self.docinfo = False
        self._newline(2)

    def _docinfo_field(self, node):
        #non-standard docinfo field, becomes a generic field element.
        #and render as normal table fields.
        if self.docinfo:
            self._add("||%s|" % node.__class__.__name__)
            self.visit_field_body(node)

    def visit_author(self, node):
        return self._docinfo_field(node)

    def depart_author(self, node):
        if self.docinfo:
            self.depart_field_body(node)

    def visit_contact(self, node):
        return self._docinfo_field(node)

    def depart_contact(self, node):
        if self.docinfo:
            self.depart_field_body(node)

    def visit_date(self, node):
        return self._docinfo_field(node)

    def depart_date(self, node):
        if self.docinfo:
            self.depart_field_body(node)

    def visit_status(self, node):
        return self._docinfo_field(node)

    def depart_status(self, node):
        if self.docinfo:
            self.depart_field_body(node)

    def visit_version(self, node):
        return self._docinfo_field(node)

    def depart_version(self, node):
        if self.docinfo:
            self.depart_field_body(node)

    def visit_revision(self, node):
        return self._docinfo_field(node)

    def depart_revision(self, node):
        if self.docinfo:
            self.depart_field_body(node)

    def visit_inline(self, node):
        pass

    def depart_inline(self, node):
        pass

    def visit_warning(self, node):
        self._add("{warning}")
        self.do_visit_admonition()

    def depart_warning(self, node):
        self._add("{warning}")
        self.do_depart_admonition()

    #admonition helpers
    def do_visit_admonition(self):
        self.list_prefix.append([])

    def do_depart_admonition(self):
        self.list_prefix.pop()
        if self.list_level == 0:
            self._newline(2)
        else:
            self._newline()

    # image
    def visit_image(self, node):
        if 'classes' in node:
            for classval in node['classes']:
                if classval.startswith("gallery-"):
                    self._print_image_gallery(node, classval)
                    return
        if self.figure:
            self.figureImage = node
        else:
            self._print_image(node)

    def _print_image(self, node):
        uri = node['uri']
        atts = {}
        if 'alt' in node:
            atts['alt'] = node['alt']
        if 'title' in node:
            atts['title'] = node['title']
        if 'width' in node:
            atts['width'] = node['width']
        if 'height' in node:
            atts['height'] = node['height']
        if 'scale' in node:
            #confluence has no percentages, so we simply make thumbnail
            atts['thumbnail'] = True
        if 'align' in node:
            atts['align'] = node['align']
        attributes = []
        for att in atts.iterkeys():
            if atts[att] == True:
                attributes.append(att)
            else:
                attributes.append(att + "=" + atts[att])

        self._add("!")
        self._add(uri)
        if attributes:
            self._add("|")
            self._add(",".join(attributes))
        self._add("!")
        self._newline()

    def _print_image_gallery(self, node, galleryclass):
        uri = node['uri']
        if galleryclass == self.lastGalleryClass and self.content[-1].startswith("{gallery:"):
            self.content[-1] = self.content[-1][0:-2] + "," + uri + "}\n"
        else:
            self.lastGalleryClass = galleryclass
            self._add("{gallery:include=" + uri + "}\n")

    # figure
    def visit_figure(self, node):
        self.figure = True

    def depart_figure(self, node):
        if not self.figureImage:
            #happens in gallery mode
            return

        foo = vars(node)['attributes']
        for att in foo:
            self.figureImage[att] = foo[att]

        self.figure = False
        self._print_image(self.figureImage)
        self.figureImage = None

    def visit_caption(self, node):
        self.figureImage['title'] = node.children[0]
        raise nodes.SkipNode

    # table
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
        if not self.table:
            return

        self.first = True
        self.tableEntryDiv = False;

        if self.table_header:
            self._add("||")
        else:
            self._add("|")
        self.lastTableEntryBar = len(self.content) - 1

    def depart_entry(self, node):
        if not self.table:
            return

        self._remove_last_newline()
        self.first = False
        if self.tableEntryDiv:
            #work around bug in confluence
            # https://jira.atlassian.com/browse/CONF-9785
            self._add("{div}")

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


    #field lists
    def visit_field_list(self, node):
        self._newline()

    def depart_field_list(self, node):
        self._newline()

    def visit_field_name(self, node):
        self._add("||")

    def visit_field_body(self, node):
        self.field_body = True
        self._add("|")

    def depart_field_body(self, node):
        self.field_body = False
        self._add("|")
        self._newline()

    #line blocks
    def visit_line_block(self, node):
        if not self.field_body:
            self._newline()

    def depart_line(self, node):
        self._newline()


    #roles http://docutils.sourceforge.net/docs/ref/rst/roles.html
    def visit_title_reference(self, node):
        self._add("_")

    def depart_title_reference(self, node):
        self._add("_")

    def _add_space_when_needed(self):
        if len(self.content) == 0:
            return
        lastline = self.content[len(self.content) - 1]
        if not lastline.endswith(" ") and not lastline.endswith("\n"):
            self._add(" ")

    def _endswidth(self, string):
        lastline = self.content[len(self.content) - 1]
        return lastline.endswith(string)

    #substitution definitions
    def visit_substitution_definition(self, node):
        raise nodes.SkipNode
