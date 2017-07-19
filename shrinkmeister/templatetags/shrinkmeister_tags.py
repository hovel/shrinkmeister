# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from django.template import Library, Node, NodeList, TemplateSyntaxError
from django.utils.encoding import smart_str
from django.utils.six import text_type

from shrinkmeister.shortcuts import get_thumbnail

register = Library()
kw_pat = re.compile(r'^(?P<key>[\w]+)=(?P<value>.+)$')


class ThumbnailNode(Node):
    nodelist_empty = NodeList()
    child_nodelists = ('nodelist_file', 'nodelist_empty')
    error_msg = ('Syntax error. Expected: ``thumbnail source geometry '
                 '[key1=val1 key2=val2...] as var``')

    def __init__(self, parser, token):
        bits = token.split_contents()
        self.file_ = parser.compile_filter(bits[1])
        self.geometry = parser.compile_filter(bits[2])
        self.options = []
        self.as_var = None
        self.nodelist_file = None

        if bits[-2] == 'as':
            options_bits = bits[3:-2]
        else:
            options_bits = bits[3:]

        for bit in options_bits:
            m = kw_pat.match(bit)
            if not m:
                raise TemplateSyntaxError(self.error_msg)
            key = smart_str(m.group('key'))
            expr = parser.compile_filter(m.group('value'))
            self.options.append((key, expr))

        if bits[-2] == 'as':
            self.as_var = bits[-1]
            self.nodelist_file = parser.parse(('empty', 'endthumbnail',))
            if parser.next_token().contents == 'empty':
                self.nodelist_empty = parser.parse(('endthumbnail',))
                parser.delete_first_token()

    def render(self, context):
        try:
            self._render(context)
        except Exception:
            return self.nodelist_empty.render(context)

    def _render(self, context):
        file_ = self.file_.resolve(context)
        geometry = self.geometry.resolve(context)
        options = {}
        for key, expr in self.options:
            noresolve = {'True': True, 'False': False, 'None': None}
            value = noresolve.get(text_type(expr), expr.resolve(context))
            if key == 'options':
                options.update(value)
            else:
                options[key] = value

        thumbnail = get_thumbnail(file_, geometry, **options)

        if not thumbnail:
            if self.nodelist_empty:
                return self.nodelist_empty.render(context)
            else:
                return ''

        if self.as_var:
            context.push()
            context[self.as_var] = thumbnail
            output = self.nodelist_file.render(context)
            context.pop()
        else:
            output = thumbnail.url

        return output

    def __repr__(self):
        return "<ThumbnailNode>"

    def __iter__(self):
        for node in self.nodelist_file:
            yield node
        for node in self.nodelist_empty:
            yield node


@register.tag
def thumbnail(parser, token):
    return ThumbnailNode(parser, token)


@register.filter
def is_portrait(file_):
    try:
        return file_.height > file_.width
    except Exception as e:
        return False
