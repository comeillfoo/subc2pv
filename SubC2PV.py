#!/usr/bin/env python3
import pathlib

from translator import Translator
from lut import LookUpTable


class SubC2PV:
    def __init__(self, translator: Translator, lut: LookUpTable):
        self.translator = translator
        self.lut = lut

    def extract(self) -> str:
        return self.lut.apply_rules(self.translator.translate())

    @classmethod
    def from_path(cls, implementation: pathlib.Path, table: pathlib.Path):
        lut = LookUpTable.from_path(table)
        path = implementation if lut.file() is None else lut.file()
        return cls(Translator.from_path(path), lut)

    def extract_to_path(self, path: pathlib.Path):
        with open(path, 'w', encoding='utf-8') as out:
            out.write(self.extract())
