#!/usr/bin/env python3
from typing import Tuple, Generator
import unittest

from tests.common import *


class AssignmentsTestCase(unittest.TestCase):
    def setUp(self):
        self._strings_cases = [
            [''],
            ['', ''],
            ['A', 'B'],
            ['alsdf'],
            ['__', '---', 'lorem ipsum']
        ]
        return super().setUp()

    def _subtest_variable_no_init(self, name: str) -> Tuple[str, str]:
        source = 'void %s() { int a; }' % (name)
        expected = f'let {name}(u\'end: channel) = new a: nat; out(u\'end, true).'
        return source, expected

    def _subtest_variable_primitive_init(self, name: str) -> Generator:
        for ttype, pvtype in TESTS_TYPES.items():
            source = 'void %s(%s a) { %s b = a; }' % (name, ttype, ttype)
            expected = f'let {name}(a: {pvtype}, u\'end: channel) = new b: {pvtype}; out(u\'end, true).'
            yield (source, expected)

    def _subtest_variable_assign_constant(self, name: str) -> Tuple[str, str]:
        source = 'void %s() { int a; a = 42; }' % (name)
        expected = f'let {name}(u\'end: channel) = new a: nat;\nlet a = 42 in out(u\'end, true).'
        return source, expected

    def _subtest_variable_assign_identifier(self, name: str) -> Generator:
        for ttype, pvtype in TESTS_TYPES.items():
            source = 'void %s(%s a) { %s b; b = a; }' % (name, ttype, ttype)
            expected = f'let {name}(a: {pvtype}, u\'end: channel) = new b: {pvtype};\nlet b = a in out(u\'end, true).'
            yield source, expected

    def _subtest_variable_assign_strings(self, name: str) -> Generator:
        for strings_case in self._strings_cases:
            joined = ''.join(strings_case)
            unique = set([*strings_case, joined])
            _id = len(unique) - 1
            expr = ''.join(map(lambda s: f'"{s}"', strings_case))
            source = 'void %s() { char *a; a = %s; }' % (name, expr)
            expected = f'let {name}(u\'end: channel) = new a: bitstring;\nlet a = u\'strlit{_id} in out(u\'end, true).'
            yield source, expected

    def test_single_assignment(self):
        check_subtest_single(self, self._subtest_variable_no_init, SOME_IDENTIFIER)
        check_subtests(self, self._subtest_variable_primitive_init, SOME_IDENTIFIER)
        check_subtest_single(self, self._subtest_variable_assign_constant, SOME_IDENTIFIER)
        check_subtests(self, self._subtest_variable_assign_identifier, SOME_IDENTIFIER)
        check_subtests(self, self._subtest_variable_assign_strings, SOME_IDENTIFIER)


    def _subtest_fielded_init_with_single_field(self) -> Tuple[str, str]:
        source = '''struct A { int x; };
void main(void) { struct A a = { 42 }; }'''
        expected = 'let main(u\'end: channel) = let a: A = u\'A_init(42) in' \
                + ' out(u\'end, true).'
        return source, expected

    def _subtest_fielded_init_with_single_designator(self) -> Tuple[str, str]:
        source = '''struct A { int x; };
void main(void) { struct A a = { .x = 42 }; }'''
        expected = 'let main(u\'end: channel) = let a: A = u\'A_init(42) in' \
                + ' out(u\'end, true).'
        return source, expected

    def _subtest_fielded_init_with_fields_list(self) -> Tuple[str, str]:
        source = '''struct A { int x; int y; int z; };
void main(void) { struct A a = { 21, 42, 84 }; }'''
        expected = 'let main(u\'end: channel) = let a: A = u\'A_init(21, 42, 84) ' \
                + 'in out(u\'end, true).'
        return source, expected

    def _subtest_fielded_init_with_designators(self) -> Tuple[str, str]:
        source = '''struct A { int x; int y; int z; };
void main(void) { struct A a = { .y = 42, .z = 84, .x = 21 }; }'''
        expected = 'let main(u\'end: channel) = let a: A = u\'A_init(21, 42, 84) ' \
                + 'in out(u\'end, true).'
        return source, expected

    def _subtest_fielded_init_with_missed_fields(self) -> Tuple[str, str]:
        source = '''struct A { int x; int y; int z; };
void main(void) { struct A a = { .z = 84, .x = 21 }; }'''
        expected = 'let main(u\'end: channel) = let a: A = u\'A_init(21, 0, 84) ' \
                + 'in out(u\'end, true).'
        return source, expected

    def _subtest_fielded_init_with_missed_designators(self) -> Tuple[str, str]:
        source = '''struct A { int x; int y; int z; };
void main(void) { struct A a = { 21, 42 }; }'''
        expected = 'let main(u\'end: channel) = let a: A = u\'A_init(21, 42, 0) ' \
                + 'in out(u\'end, true).'
        return source, expected

    def _subtest_fielded_init_mixed(self) -> Tuple[str, str]:
        source = '''struct A { int x; int y; int z; };
void main(void) { struct A a = { 21, .z = 84, .y = 42 }; }'''
        expected = 'let main(u\'end: channel) = let a: A = u\'A_init(21, 42, 84) ' \
                + 'in out(u\'end, true).'
        return source, expected

    def _subtest_nested_structs_init(self) -> Tuple[str, str]:
        source = '''struct A { int x; int y; };
struct B { int z; struct A a; };
void main(void) { struct A a = {}; struct B b = { .a = a }; }
'''
        expected = 'let main(u\'end: channel) = let a: A = u\'A_init(0, 0) in\n' \
                + 'let b: B = u\'B_init(0, a) in out(u\'end, true).'
        return source, expected

    def test_struct_or_union_init(self):
        check_subtest_single(self, self._subtest_fielded_init_with_single_field)
        check_subtest_single(self, self._subtest_fielded_init_with_fields_list)
        check_subtest_single(self, self._subtest_fielded_init_with_missed_fields)
        check_subtest_single(self, self._subtest_fielded_init_with_single_designator)
        check_subtest_single(self, self._subtest_fielded_init_with_missed_designators)
        check_subtest_single(self, self._subtest_fielded_init_with_designators)
        check_subtest_single(self, self._subtest_fielded_init_mixed)
        check_subtest_single(self, self._subtest_nested_structs_init)


    def _subtest_array_declaration(self) -> Tuple[str, str]:
        source = 'void main(void) { int a[]; }'
        expected = 'let main(u\'end: channel) = new a: bitstring; out(u\'end, true).'
        return source, expected

    def _subtest_multidimensional_array_declaration(self) -> Tuple[str, str]:
        source = 'void main(void) { int a[][][][][][][][][][][][][][][][][]; }'
        expected = 'let main(u\'end: channel) = new a: bitstring; out(u\'end, true).'
        return source, expected

    def _subtest_multidimensional_array_with_sizes(self) -> Tuple[str, str]:
        source = 'void main(void) { int a[1][][3][][5]; }'
        expected = 'let main(u\'end: channel) = new a: bitstring; out(u\'end, true).'
        return source, expected

    def _subtest_array_without_size(self) -> Tuple[str, str]:
        source = 'void main(void) { int a[] = { 1, 2, 3, 4, 5 }; }'
        expected = 'let main(u\'end: channel) = new a: bitstring; out(u\'end, true).'
        return source, expected

    def _subtest_array_with_size(self) -> Tuple[str, str]:
        source = 'void main(void) { int a[8] = {}; }'
        expected = 'let main(u\'end: channel) = new a: bitstring; out(u\'end, true).'
        return source, expected

    def test_array_init(self):
        check_subtest_single(self, self._subtest_array_declaration)
        check_subtest_single(self, self._subtest_multidimensional_array_declaration)
        check_subtest_single(self, self._subtest_multidimensional_array_with_sizes)
        check_subtest_single(self, self._subtest_array_without_size)
        check_subtest_single(self, self._subtest_array_with_size)
