#!/usr/bin/env python3
from typing import Tuple, Generator

from helpers import Parameter
from translator import Translator
from tests.TranslatorCommonTestCase import TranslatorCommonTestCase


class UnionsOrStructsDeclarationsAndDefinitionsTestCase(TranslatorCommonTestCase):
    def setUp(self):
        self._inttypes = ['char', 'short', 'int', 'long', '__m128', '__m128d',
                          '__m128i']
        return super().setUp()

    def _subtest_fielded_declaration(self, name: str,
                                     ttype: str) -> Tuple[str, str]:
        return f'{ttype} {name};', f'type {name}.'

    def _dict2fielded_def(self, name: str, fields: list[Parameter] = [],
                          ttype: str = 'struct') -> str:
        lines = [f'{ttype} {name}', '{']
        for ftype, fname in fields:
            lines.append(f'{ftype} {fname};')
        lines.append('};')
        return '\n'.join(lines)

    def _subtest_fielded_empty_definition(self, name: str,
                                          ttype: str) -> Tuple[str, str]:
        source = self._dict2fielded_def(name, ttype=ttype)
        expected = '\n'.join([f'type {name}.', f"fun u'{name}_init(): {name}."])
        return source, expected

    def _subtest_single_enum_field(self, name: str,
                                   ttype: str) -> Tuple[str, str]:
        source = self._dict2fielded_def(name, [('enum A', 'x')], ttype)
        expected = '\n'.join([
            f'type {name}.', f"fun u'{name}_get_x({name}): A.",
            f"fun u'{name}_set_x({name}, A): {name}.",
            f"fun u'{name}_init(A): {name}."])
        return source, expected

    def _define_fielded_with_single_integer(self, name: str, ttype: str,
            fname: str, ftype: str) -> Tuple[str, str]:
        source = self._dict2fielded_def(name, [(ftype, fname)], ttype)
        expected = '\n'.join([
            f'type {name}.', f"fun u'{name}_get_{fname}({name}): nat.",
            f"fun u'{name}_set_{fname}({name}, nat): {name}.",
            f"fun u'{name}_init(nat): {name}."])
        return source, expected

    def _subtest_single_integer_field(self, name: str,
                                      ttype: str) -> Generator:
        for fname in self._stress_identifiers:
            for ftype in self._inttypes:
                yield self._define_fielded_with_single_integer(name, ttype,
                                                               fname, ftype)

    def _subtest_single_bool_field(self, name: str, ttype: str) -> Generator:
        for fname in self._stress_identifiers:
            source = self._dict2fielded_def(name, [('_Bool', fname)], ttype)
            expected = '\n'.join([
                f'type {name}.', f"fun u'{name}_get_{fname}({name}): bool.",
                f"fun u'{name}_set_{fname}({name}, bool): {name}.",
                f"fun u'{name}_init(bool): {name}."])
            yield source, expected

    def test_unions(self):
        self.check_preamble_subtest(self._subtest_fielded_declaration,
                                    self._stress_test_identifier, 'union')
        self.check_preamble_subtest(self._subtest_fielded_empty_definition,
                                    self._stress_test_identifier, 'union')
        self.check_preamble_subtest(self._subtest_single_enum_field,
                                    self._stress_test_identifier, 'union')
        self.check_preamble_subtests(self._subtest_single_integer_field,
                                     self._stress_test_identifier, 'union')
        self.check_preamble_subtests(self._subtest_single_bool_field,
                                     self._stress_test_identifier, 'union')

    def test_structs(self):
        self.check_preamble_subtest(self._subtest_fielded_declaration,
                                    self._stress_test_identifier, 'struct')
        self.check_preamble_subtest(self._subtest_fielded_empty_definition,
                                    self._stress_test_identifier, 'struct')
        self.check_preamble_subtest(self._subtest_single_enum_field,
                                    self._stress_test_identifier, 'struct')
        self.check_preamble_subtests(self._subtest_single_integer_field,
                                     self._stress_test_identifier, 'struct')
        self.check_preamble_subtests(self._subtest_single_bool_field,
                                     self._stress_test_identifier, 'struct')
