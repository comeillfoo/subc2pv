#!/usr/bin/env python3
from typing import Callable, Tuple
import unittest


from translator import Translator
from tests.common import *


class AssignmentsTestCase(unittest.TestCase):
    def _function_variable_no_init_subtest(self, name: str):
        source = 'void %s() { int a; }' % (name)
        model = Translator.from_line(source, False).translate()
        self.assertTrue(not model.preamble)
        _, actual = model.functions[0]
        self.assertEqual(
            f'let {name}(_end: channel) = new a: nat; out(_end, true).', actual)

    def _function_variable_primitive_init_subtest(self, name: str):
        for ttype, pvtype in TESTS_TYPES.items():
            source = 'void %s(%s a) { %s b = a; }' % (name, ttype, ttype)
            model = Translator.from_line(source, False).translate()
            self.assertTrue(not model.preamble)
            _, actual = model.functions[0]
            expected = f'let {name}(a: {pvtype}, _end: channel) = new b: {pvtype}; out(_end, true).'
            self.assertEqual(expected, actual)

    def _function_variable_assign_to_constant_subtest(self, name: str):
        source = 'void %s() { int a; a = 42; }' % (name)
        model = Translator.from_line(source, False).translate()
        self.assertTrue(not model.preamble)
        _, actual = model.functions[0]
        expected = f'let {name}(_end: channel) = new a: nat;\nlet a = 42 in out(_end, true).'
        self.assertEqual(expected, actual)

    def _function_variable_assign_to_identifier_subtest(self, name: str):
        for ttype, pvtype in TESTS_TYPES.items():
            source = 'void %s(%s a) { %s b; b = a; }' % (name, ttype, ttype)
            model = Translator.from_line(source, False).translate()
            self.assertTrue(not model.preamble)
            _, actual = model.functions[0]
            expected = f'let {name}(a: {pvtype}, _end: channel) = new b: {pvtype};\nlet b = a in out(_end, true).'
            self.assertEqual(expected, actual)

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
            _, actual = model.functions[0]
            expected = f'let {name}(_end: channel) = new a: bitstring;\nlet a = _strlit{_id} in out(_end, true).'
            self.assertEqual(expected, actual,
                             f'functions differs with {strings_case}')

    def test_single_assignment(self):
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

    def _subtest_fielded_init_with_single_field(self) -> Tuple[str, str]:
        source = '''struct A { int x; };
void main(void) { struct A a = { 42 }; }'''
        expected = 'let main(_end: channel) = let a: A = _A_init(42) in' \
                + ' out(_end, true).'
        return source, expected


    def _subtest_fielded_init_with_single_designator(self) -> Tuple[str, str]:
        source = '''struct A { int x; };
void main(void) { struct A a = { .x = 42 }; }'''
        expected = 'let main(_end: channel) = let a: A = _A_init(42) in' \
                + ' out(_end, true).'
        return source, expected


    def _subtest_fielded_init_with_fields_list(self) -> Tuple[str, str]:
        source = '''struct A { int x; int y; int z; };
void main(void) { struct A a = { 21, 42, 84 }; }'''
        expected = 'let main(_end: channel) = let a: A = _A_init(21, 42, 84) ' \
                + 'in out(_end, true).'
        return source, expected


    def _subtest_fielded_init_with_designators(self) -> Tuple[str, str]:
        source = '''struct A { int x; int y; int z; };
void main(void) { struct A a = { .y = 42, .z = 84, .x = 21 }; }'''
        expected = 'let main(_end: channel) = let a: A = _A_init(21, 42, 84) ' \
                + 'in out(_end, true).'
        return source, expected


    def _subtest_fielded_init_with_missed_fields(self) -> Tuple[str, str]:
        source = '''struct A { int x; int y; int z; };
void main(void) { struct A a = { .z = 84, .x = 21 }; }'''
        expected = 'let main(_end: channel) = let a: A = _A_init(21, 0, 84) ' \
                + 'in out(_end, true).'
        return source, expected


    def _subtest_fielded_init_with_missed_designators(self) -> Tuple[str, str]:
        source = '''struct A { int x; int y; int z; };
void main(void) { struct A a = { 21, 42 }; }'''
        expected = 'let main(_end: channel) = let a: A = _A_init(21, 42, 0) ' \
                + 'in out(_end, true).'
        return source, expected


    def _subtest_fielded_init_mixed(self) -> Tuple[str, str]:
        source = '''struct A { int x; int y; int z; };
void main(void) { struct A a = { 21, .z = 84, .y = 42 }; }'''
        expected = 'let main(_end: channel) = let a: A = _A_init(21, 42, 84) ' \
                + 'in out(_end, true).'
        return source, expected


    def _subtest_nested_structs_init(self) -> Tuple[str, str]:
        source = '''struct A { int x; int y; };
struct B { int z; struct A a; };
void main(void) { struct A a = {}; struct B b = { .a = a }; }
'''
        expected = 'let main(_end: channel) = let a: A = _A_init(0, 0) in\n' \
                + 'let b: B = _B_init(0, a) in out(_end, true).'
        return source, expected


    def test_struct_or_union_init(self):
        def at_subtest(subtest: Callable):
            with self.subTest(subtest.__name__):
                source, expected = subtest()
                model = Translator.from_line(source, False).translate()
                _, actual = model.functions[0]
                self.assertEqual(expected, actual)
        at_subtest(self._subtest_fielded_init_with_single_field)
        at_subtest(self._subtest_fielded_init_with_fields_list)
        at_subtest(self._subtest_fielded_init_with_missed_fields)
        at_subtest(self._subtest_fielded_init_with_single_designator)
        at_subtest(self._subtest_fielded_init_with_missed_designators)
        at_subtest(self._subtest_fielded_init_with_designators)
        at_subtest(self._subtest_fielded_init_mixed)
        at_subtest(self._subtest_nested_structs_init)
