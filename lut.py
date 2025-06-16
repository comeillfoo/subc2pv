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
        return self.rules.get('X', set())

    def extract(self, fname: str) -> bool:
        return bool(fname in self.rules.get('X', set()))

    def substitutes(self) -> dict[str, str]:
        return self.rules.get('S', {})

    def substitute(self, fname: str) -> Optional[str]:
        return self.rules.get('S', {}).get(fname, None)

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


    class Parser:
        def __init__(self):
            self.rules = {}

        def _accept_single(self, type: str, lines: list[str],
                           maxsplit: int = -1) -> list[str]:
            if not lines:
                return []
            line = lines[0].strip()[1:]
            if not line.startswith(type):
                return []
            return line.split(maxsplit=maxsplit)

        # %F <path>
        def _accept_file(self, lines: list[str]) -> int:
            parts = self._accept_single('F', lines)
            if len(parts) < 2:
                return 0

            self.rules['F'] = pathlib.Path(parts[1].strip())
            return 1

        # %X <fname>
        def _accept_extract(self, lines: list[str]) -> int:
            parts = self._accept_single('X', lines)
            if len(parts) < 2:
                return 0

            s = self.rules.get('X', set())
            s.add(parts[1].strip())
            self.rules['X'] = s
            return 1

        # %S <fname> <substitution>
        def _accept_substitute(self, lines: list[str]) -> int:
            parts = self._accept_single('S', lines, 2)
            # TODO: solve problem with not enough parameters
            if len(parts) < 3:
                return 0

            d = self.rules.get('S', {})
            d[parts[1].strip()] = parts[2].strip()
            self.rules['S'] = d
            return 1

        # %P
        # ...
        # %%
        def _accept_paste(self, lines: list[str]) -> int:
            if not lines:
                return 0
            i = 0
            line = lines[0].strip()[1:]
            if not line.startswith('P'):
                return i
            i += 1
            paste = []
            while i < len(lines):
                line = lines[i]
                i += 1
                if line.startswith('%%'):
                    break
                paste.append(line)
            self.rules['P'] = ''.join(paste)
            return i

        def parse(self, lines: list[str]):
            i = 0
            while i < len(lines):
                while i < len(lines) and not lines[i].strip().startswith('%'):
                    i += 1
                i += self._accept_file(lines[i:])
                i += self._accept_extract(lines[i:])
                i += self._accept_substitute(lines[i:])
                i += self._accept_paste(lines[i:])


    @classmethod
    def from_lines(cls, lines: list[str]):
        lut_parser = LookUpTable.Parser()
        lut_parser.parse(lines)
        return cls(lut_parser.rules)

    @classmethod
    def from_path(cls, path: pathlib.Path):
        if not path.is_file():
            return cls.from_lines([])
        with open(path, 'r', encoding='utf-8') as lut:
            return cls.from_lines(lut.readlines())

    @classmethod
    def from_line(cls, line: str):
        return cls.from_lines(line.splitlines(keepends=True))
