#!/usr/bin/env python3
import unittest


from translator import Translator
from tests.common import *


class AssignmentsTestCase(unittest.TestCase):
    def _function_variable_no_init_subtest(self, name: str):
        source = 'void %s() { int a; }' % (name)
        model = Translator.from_line(source, False).translate()
        self.assertTrue(not model.preamble)
        self.assertEqual((name, f'let {name}(_end: channel) = new a: nat; out(_end, true).'),
                         model.functions[0])

    def _function_variable_primitive_init_subtest(self, name: str):
        for ttype, pvtype in TESTS_TYPES.items():
            source = 'void %s(%s a) { %s b = a; }' % (name, ttype, ttype)
            model = Translator.from_line(source, False).translate()
            self.assertTrue(not model.preamble)
            expected = f'let {name}(a: {pvtype}, _end: channel) = new b: {pvtype}; out(_end, true).'
            self.assertEqual((name, expected), model.functions[0])

    def _function_variable_assign_to_constant_subtest(self, name: str):
        source = 'void %s() { int a; a = 42; }' % (name)
        model = Translator.from_line(source, False).translate()
        self.assertTrue(not model.preamble)
        expected = f'let {name}(_end: channel) = new a: nat;\nlet a = 42 in out(_end, true).'
        self.assertEqual((name, expected), model.functions[0])

    def _function_variable_assign_to_identifier_subtest(self, name: str):
        for ttype, pvtype in TESTS_TYPES.items():
            source = 'void %s(%s a) { %s b; b = a; }' % (name, ttype, ttype)
            model = Translator.from_line(source, False).translate()
            self.assertTrue(not model.preamble)
            expected = f'let {name}(a: {pvtype}, _end: channel) = new b: {pvtype};\nlet b = a in out(_end, true).'
            self.assertEqual((name, expected), model.functions[0])

    def _function_variable_assign_to_strings_subtest(self, name: str):
        strings_cases = [
            [''],
            ['', ''],
            ['A', 'B'],
            ['alsdf'],
            ['__', '---', 'lorem ipsum']
        ]
        for strings_case in strings_cases:
            joined = ''.join(strings_case)
            unique = set([*strings_case, joined])
            _id = len(unique) - 1
            expr = ''.join(map(lambda s: f'"{s}"', strings_case))
            source = 'void %s() { char *a; a = %s; }' % (name, expr)
            model = Translator.from_line(source, False).translate()
            expected = f'let {name}(_end: channel) = new a: bitstring;\nlet a = _strlit{_id} in out(_end, true).'
            self.assertEqual((name, expected), model.functions[0],
                             f'functions differs with {strings_case}')

    def test_single_function_definition(self):
        def at_subtest(subtest: str, fun):
            with self.subTest(f'{subtest}'):
                fun(SOME_IDENTIFIER)
        at_subtest('function-variable-declaration-no-init-value',
                    self._function_variable_no_init_subtest)
        at_subtest('function-variable-primitive-init-value',
                    self._function_variable_primitive_init_subtest)
        at_subtest('function-variable-assign-to-constant',
                    self._function_variable_assign_to_constant_subtest)
        at_subtest('function-variable-assign-to-identifier',
                    self._function_variable_assign_to_identifier_subtest)
        at_subtest('function-variable-assign-to-strings',
                    self._function_variable_assign_to_strings_subtest)
