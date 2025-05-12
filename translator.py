#!/usr/bin/env python3
import pathlib
import antlr4

from libs.SubCLexer import SubCLexer
from libs.SubCParser import SubCParser
from SubC2PVListener import SubC2PVListener

from model import Model



class Translator:
    def __init__(self, stream: antlr4.InputStream):
        self._stream = stream


    def translate(self) -> Model:
        lexer = SubCLexer(self._stream)
        token_stream = antlr4.CommonTokenStream(lexer)
        parser = SubCParser(token_stream)

        root_node = parser.compilationUnit()
        listener = SubC2PVListener()
        walker = antlr4.ParseTreeWalker()
        walker.walk(listener, root_node)
        return listener.model()


    @classmethod
    def from_path(cls, implementation: pathlib.Path):
        return cls(antlr4.FileStream(implementation, encoding='utf-8'))

    @classmethod
    def from_lines(cls, lines: list[str]):
        return cls(antlr4.InputStream('\n'.join(lines)))

    @classmethod
    def from_line(cls, line: str):
        return cls(antlr4.InputStream(line))
