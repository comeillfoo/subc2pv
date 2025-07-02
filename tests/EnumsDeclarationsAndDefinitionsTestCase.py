#!/usr/bin/env python3
import unittest
from typing import Tuple

from translator import Translator
from tests.common import *


class EnumsDeclarationsAndDefinitionsTestCase(unittest.TestCase):
    def setUp(self):
        self._enums_consts = [
            [ ('A', ''), ('b', ''), ('C', '') ],
            [ ('adsff', '42'), ('aslkdnf', '')],
            [ ('__', '0xDEADBEEF') ],
            [ ('SEND', ''), ('RECV', '0b101'), ('ACK', ''), ('NACK', '0777') ]
        ]
        return super().setUp()

    def _subtest_enum_declaration(self, name: str):
        model = Translator.from_line(f'enum {name};', False).translate()
        self.assertTrue(not model.functions, 'No functions should be parsed')
        self.assertEqual(model.preamble, f'type {name}.')

    def test_enum_declaration(self):
        for name in IDENTIFIERS:
            at_subtest(self, self._subtest_enum_declaration, name)

    def _subtest_enum_definition(self, name: str, consts: list[Tuple[str, str]]):
        lines = [f'enum {name}', '{']
        expected = [f'type {name}.']
        for ec_name, ec_value in consts:
            if ec_value != '':
                ec_value = f' = {ec_value}'
            lines.append(f'\t{ec_name}{ec_value},')
            expected.append(f'const {ec_name}: {name}.')
        lines.append('};')

        model = Translator.from_lines(lines, False).translate()
        self.assertTrue(not model.functions)
        self.assertEqual(model.preamble, '\n'.join(expected))

    def test_enum_definition(self):
        for name in IDENTIFIERS:
            for consts in self._enums_consts:
                at_subtest(self, self._subtest_enum_definition, name, consts)
