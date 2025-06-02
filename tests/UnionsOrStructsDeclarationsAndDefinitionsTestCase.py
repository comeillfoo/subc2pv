#!/usr/bin/env python3
import unittest
from typing import Tuple


from translator import Translator
from tests.common import *


class UnionsOrStructsDeclarationsAndDefinitionsTestCase(unittest.TestCase):
    def _fielded_declaration_subtest(self, name: str, ttype: str):
        model = Translator.from_line(f'{ttype} {name};', False).translate()
        self.assertTrue(not model.functions)
        self.assertEqual(model.preamble, f'type {name}.')

    def _dict2fielded_def(self, name: str, fields: Tuple[str, str] = [],
                          ttype: str = 'struct') -> str:
        lines = [f'{ttype} {name}', '{']
        for fname, ftype in fields:
            lines.append(f'{ftype} {fname};')
        lines.append('};')
        return '\n'.join(lines)

    def _fielded_empty_definition_subtest(self, name: str, ttype: str):
        model = Translator.from_line(
            self._dict2fielded_def(name, ttype=ttype), False).translate()
        self.assertTrue(not model.functions)
        expected = '\n'.join([f'type {name}.', f'fun _{name}_init(): {name}.'])
        self.assertEqual(model.preamble, expected)

    def _fielded_with_single_enum_subtest(self, name: str, ttype: str):
        model = Translator.from_line(
            self._dict2fielded_def(name, [('x', 'enum A')], ttype),
            False).translate()
        self.assertTrue(not model.functions)
        expected = '\n'.join([
            f'type {name}.', f'fun _{name}_get_x({name}): A.',
            f'fun _{name}_set_x({name}, A): {name}.',
            f'fun _{name}_init(A): {name}.'])
        self.assertEqual(model.preamble, expected)

    def _fielded_single_integer_helper(self, name: str, ttype: str, fname: str,
                                       ftype: str):
        fielded_definition = self._dict2fielded_def(name, [(fname, ftype)], ttype)
        translator = Translator.from_line(fielded_definition, False)
        model = translator.translate()
        self.assertTrue(not model.functions)
        expected = '\n'.join([
            f'type {name}.', f'fun _{name}_get_{fname}({name}): nat.',
            f'fun _{name}_set_{fname}({name}, nat): {name}.',
            f'fun _{name}_init(nat): {name}.'])
        self.assertEqual(model.preamble, expected)

    def _fielded_single_integer_subtest(self, name: str, ttype: str):
        ftypes = ['char', 'short', 'int', 'long', '__m128', '__m128d', '__m128i']
        for fname in IDENTIFIERS:
            for ftype in ftypes:
                self._fielded_single_integer_helper(name, ttype, fname, ftype)

    def _fielded_single_bool_subtest(self, name: str, ttype: str):
        for fname in IDENTIFIERS:
            fielded_definition = self._dict2fielded_def(name, [(fname, '_Bool')],
                                                        ttype)
            model = Translator.from_line(fielded_definition, False).translate()
            self.assertTrue(not model.functions)
            expected = '\n'.join([
                f'type {name}.', f'fun _{name}_get_{fname}({name}): bool.',
                f'fun _{name}_set_{fname}({name}, bool): {name}.',
                f'fun _{name}_init(bool): {name}.'])
            self.assertEqual(model.preamble, expected)

    def test_fielded(self):
        def at_subtest(ttype: str, subtest: str, fun):
            with self.subTest(f'{subtest}:{ttype}'):
                fun(SOME_IDENTIFIER, ttype)
        for ttype in ('struct', 'union'):
            at_subtest(ttype, 'declaration', self._fielded_declaration_subtest)
            at_subtest(ttype, 'empty-definition',
                       self._fielded_empty_definition_subtest)
            at_subtest(ttype, 'single-enum-definition',
                       self._fielded_with_single_enum_subtest)
            at_subtest(ttype, 'single-integer-definition',
                       self._fielded_single_integer_subtest)
            at_subtest(ttype, 'single-bool-definition',
                       self._fielded_single_bool_subtest)
