#!/usr/bin/env python3
import pathlib
import antlr4

from libs.SubCLexer import SubCLexer
from libs.SubCParser import SubCParser
from SubC2PVListener import SubC2PVListener

from model import Model, FunctionModel


class Translator:
    AUXILARY_GLOBALS = [
        'fun _addressof(any_type): bitstring.', # &a
        'fun _deref(any_type): bitstring.',     # *a
        'fun _sizeof(any_type): nat.',          # sizeof(a)
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
