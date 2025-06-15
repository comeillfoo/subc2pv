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

    def at_fun_subtest(self, subtest: Callable):
        with self.subTest(subtest.__name__):
            subtest(SOME_IDENTIFIER)

    def test_single_assignment(self):
        self.at_fun_subtest(self._function_variable_no_init_subtest)
        self.at_fun_subtest(self._function_variable_primitive_init_subtest)
        self.at_fun_subtest(self._function_variable_assign_to_constant_subtest)
        self.at_fun_subtest(self._function_variable_assign_to_identifier_subtest)
        self.at_fun_subtest(self._function_variable_assign_to_strings_subtest)


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

    def at_subtest(self, subtest: Callable):
        with self.subTest(subtest.__name__):
            source, expected = subtest()
            model = Translator.from_line(source, False).translate()
            _, actual = model.functions[0]
            self.assertEqual(expected, actual)

    def test_struct_or_union_init(self):
        self.at_subtest(self._subtest_fielded_init_with_single_field)
        self.at_subtest(self._subtest_fielded_init_with_fields_list)
        self.at_subtest(self._subtest_fielded_init_with_missed_fields)
        self.at_subtest(self._subtest_fielded_init_with_single_designator)
        self.at_subtest(self._subtest_fielded_init_with_missed_designators)
        self.at_subtest(self._subtest_fielded_init_with_designators)
        self.at_subtest(self._subtest_fielded_init_mixed)
        self.at_subtest(self._subtest_nested_structs_init)


    def _subtest_array_declaration(self) -> Tuple[str, str]:
        source = 'void main(void) { int a[]; }'
        expected = 'let main(_end: channel) = new a: bitstring; out(_end, true).'
        return source, expected

    def _subtest_multidimensional_array_declaration(self) -> Tuple[str, str]:
        source = 'void main(void) { int a[][][][][][][][][][][][][][][][][]; }'
        expected = 'let main(_end: channel) = new a: bitstring; out(_end, true).'
        return source, expected

    def _subtest_multidimensional_array_with_sizes(self) -> Tuple[str, str]:
        source = 'void main(void) { int a[1][][3][][5]; }'
        expected = 'let main(_end: channel) = new a: bitstring; out(_end, true).'
        return source, expected

    def _subtest_array_without_size(self) -> Tuple[str, str]:
        source = 'void main(void) { int a[] = { 1, 2, 3, 4, 5 }; }'
        expected = 'let main(_end: channel) = new a: bitstring; out(_end, true).'
        return source, expected

    def _subtest_array_with_size(self) -> Tuple[str, str]:
        source = 'void main(void) { int a[8] = { 1, 2, 3, 4, 5 }; }'
        expected = 'let main(_end: channel) = new a: bitstring; out(_end, true).'
        return source, expected

    def test_array_init(self):
        self.at_subtest(self._subtest_array_declaration)
        self.at_subtest(self._subtest_multidimensional_array_declaration)
        self.at_subtest(self._subtest_multidimensional_array_with_sizes)
        self.at_subtest(self._subtest_array_without_size)
        self.at_subtest(self._subtest_array_with_size)
