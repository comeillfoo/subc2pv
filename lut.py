#!/usr/bin/env python3
import pathlib
from typing import Optional

from model import Model


class LookUpTable:
    def __init__(self, rules: dict):
        self.rules = rules

    def file(self) -> Optional[pathlib.Path]:
        return self.rules.get('F', None)

    def extracts(self) -> set[str]:
        return self.rules.get('X', {})

    def substitutes(self) -> dict[str, str]:
        return self.rules.get('S', {})

    def paste(self) -> str:
        return self.rules.get('P', '')

    def apply_rules(self, model: Model) -> str:
        spec = [model.preamble, '']
        funcs = self.extracts()
        substitutions = self.substitutes()
        for fname, fbody in model.functions:
            if fname in funcs:
                spec.extend([fbody, ''])
            elif fname in substitutions:
                spec.extend([substitutions.get(fname), ''])
        spec.append(self.paste())
        return '\n'.join(spec)


    @classmethod
    def from_lines(cls, lines: list[str]):
        # TODO: implement
        return cls({})

    @classmethod
    def from_path(cls, path: pathlib.Path):
        if not path.is_file():
            return cls.from_lines([])
        with open(path, 'r', encoding='utf-8') as lut:
            return cls.from_lines(lut.readlines())

    @classmethod
    def from_line(cls, line: str):
        return cls.from_lines(line.split('\n'))
