#!/usr/bin/env python3
import pathlib
import antlr4

from libs.SubCLexer import SubCLexer
from libs.SubCParser import SubCParser
from listeners.SubC2PVListener import SubC2PVListener

from model import Model


class Translator:
    AUXILARY_GLOBALS = [
        'const NULL: bitstring.',               # NULL
        "fun u'addressof(any_type): bitstring.", # &a
        "fun u'deref(bitstring): bitstring\n" \
        "\treduc u'deref(NULL) = fail.",         # *a
        "fun u'sizeof(any_type): nat.",          # sizeof(a)
        "fun u'mul(nat, nat): nat.",             # a * b
        "fun u'div(nat, nat): nat.",             # a / b
        "fun u'mod(nat, nat): nat.",             # a % b
        "fun u'shl(nat, nat): nat.",             # a << b
        "fun u'shr(nat, nat): nat.",             # a >> b
        "fun u'and(nat, nat): nat.",             # a & b
        "fun u'xor(nat, nat): nat.",             # a ^ b
        "fun u'or(nat, nat): nat.",              # a | b
        "fun u'not(nat): nat.",                  # ~a
        "fun u'ternary(bool, any_type, any_type): any_type\n" \
        "\treduc forall a: any_type, b: any_type; u'ternary(true, a, b) = a\n" \
        "\t\totherwise forall a: any_type, b: any_type; u'ternary(false, a, b) = b.", # cond ? a : b
    ]

    def __init__(self, stream: antlr4.InputStream,
                 predefine_helpers: bool = True):
        self._stream = stream
        self._predefine_helpers = predefine_helpers

    def _preamble(self, listener: SubC2PVListener) -> str:
        _globals = []
        if self._predefine_helpers:
            _globals.extend(self.AUXILARY_GLOBALS)
        _globals.extend(listener._globals)
        return '\n'.join(_globals)

    def _listener2model(self, listener: SubC2PVListener) -> Model:
        return Model(self._preamble(listener),
                     list(listener._functions.items()))


    def translate(self) -> Model:
        lexer = SubCLexer(self._stream)
        token_stream = antlr4.CommonTokenStream(lexer)
        parser = SubCParser(token_stream)

        root_node = parser.compilationUnit()
        listener = SubC2PVListener()
        walker = antlr4.ParseTreeWalker()
        walker.walk(listener, root_node)
        return self._listener2model(listener)


    @classmethod
    def from_path(cls, implementation: pathlib.Path,
                  predefine_helpers: bool = True):
        return cls(antlr4.FileStream(implementation, encoding='utf-8'),
                   predefine_helpers)

    @classmethod
    def from_lines(cls, lines: list[str], predefine_helpers: bool = True):
        return cls(antlr4.InputStream('\n'.join(lines)), predefine_helpers)

    @classmethod
    def from_line(cls, line: str, predefine_helpers: bool = True):
        return cls(antlr4.InputStream(line), predefine_helpers)
