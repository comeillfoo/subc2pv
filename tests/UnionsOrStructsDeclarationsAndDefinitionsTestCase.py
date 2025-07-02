#!/usr/bin/env python3
from typing import Tuple
import unittest

from helpers import Parameter
from translator import Translator
from tests.common import *


class UnionsOrStructsDeclarationsAndDefinitionsTestCase(unittest.TestCase):
    def _subtest_fielded_declaration(self, name: str, ttype: str):
        model = Translator.from_line(f'{ttype} {name};', False).translate()
        self.assertTrue(not model.functions)
        self.assertEqual(model.preamble, f'type {name}.')

    def _dict2fielded_def(self, name: str, fields: list[Parameter] = [],
                          ttype: str = 'struct') -> str:
        lines = [f'{ttype} {name}', '{']
        for ftype, fname in fields:
            lines.append(f'{ftype} {fname};')
        lines.append('};')
        return '\n'.join(lines)

    def _subtest_fielded_empty_definition(self, name: str, ttype: str):
        model = Translator.from_line(
            self._dict2fielded_def(name, ttype=ttype), False).translate()
        self.assertTrue(not model.functions)
        expected = '\n'.join([f'type {name}.', f"fun u'{name}_init(): {name}."])
        self.assertEqual(model.preamble, expected)

    def _subtest_single_enum_field(self, name: str, ttype: str):
        model = Translator.from_line(
            self._dict2fielded_def(name, [('enum A', 'x')], ttype),
            False).translate()
        self.assertTrue(not model.functions)
        expected = '\n'.join([
            f'type {name}.', f"fun u'{name}_get_x({name}): A.",
            f"fun u'{name}_set_x({name}, A): {name}.",
            f"fun u'{name}_init(A): {name}."])
        self.assertEqual(model.preamble, expected)

    def _define_fielded_with_single_integer(self, name: str, ttype: str,
            fname: str, ftype: str) -> Tuple[str, str]:
        source = self._dict2fielded_def(name, [(ftype, fname)], ttype)
        expected = '\n'.join([
            f'type {name}.', f"fun u'{name}_get_{fname}({name}): nat.",
            f"fun u'{name}_set_{fname}({name}, nat): {name}.",
            f"fun u'{name}_init(nat): {name}."])
        return source, expected

    def _subtest_single_integer_field(self, name: str, ttype: str):
        ftypes = ['char', 'short', 'int', 'long', '__m128', '__m128d', '__m128i']
        for fname in IDENTIFIERS:
            for ftype in ftypes:
                source, expected = self._define_fielded_with_single_integer(
                    name, ttype, fname, ftype)
                model = Translator.from_line(source, False).translate()
                self.assertTrue(not model.functions)
                self.assertEqual(model.preamble, expected)

    def _subtest_single_bool_field(self, name: str, ttype: str):
        for fname in IDENTIFIERS:
            source = self._dict2fielded_def(name, [('_Bool', fname)], ttype)
            model = Translator.from_line(source, False).translate()
            self.assertTrue(not model.functions)
            expected = '\n'.join([
                f'type {name}.', f"fun u'{name}_get_{fname}({name}): bool.",
                f"fun u'{name}_set_{fname}({name}, bool): {name}.",
                f"fun u'{name}_init(bool): {name}."])
            self.assertEqual(model.preamble, expected)

    def test_unions(self):
        at_subtest(self, self._subtest_fielded_declaration, SOME_IDENTIFIER, 'union')
        at_subtest(self, self._subtest_fielded_empty_definition, SOME_IDENTIFIER, 'union')
        at_subtest(self, self._subtest_single_enum_field, SOME_IDENTIFIER, 'union')
        at_subtest(self, self._subtest_single_integer_field, SOME_IDENTIFIER, 'union')
        at_subtest(self, self._subtest_single_bool_field, SOME_IDENTIFIER, 'union')

    def test_structs(self):
        at_subtest(self, self._subtest_fielded_declaration, SOME_IDENTIFIER, 'struct')
        at_subtest(self, self._subtest_fielded_empty_definition, SOME_IDENTIFIER, 'struct')
        at_subtest(self, self._subtest_single_enum_field, SOME_IDENTIFIER, 'struct')
        at_subtest(self, self._subtest_single_integer_field, SOME_IDENTIFIER, 'struct')
        at_subtest(self, self._subtest_single_bool_field, SOME_IDENTIFIER, 'struct')
