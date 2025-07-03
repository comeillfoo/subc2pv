#!/usr/bin/env python3
from typing import Tuple, Generator

from tests.TranslatorCommonTestCase import TranslatorCommonTestCase


class FunctionDefinitionsTestCase(TranslatorCommonTestCase):
    def _define_empty_void_nullary_function(self, name: str,
            use_void: bool = False) -> Tuple[str, str]:
        source = '_Noreturn void %s(%s) { }' % (name, 'void' if use_void else '')
        expected = f"let {name}(u'end: channel) = out(u'end, true)."
        return source, expected

    def _define_empty_nonvoid_nullary_function(self, name: str,
            use_void: bool = False) -> Generator:
        for rtype, _ in self._types_table.items():
            source = '__stdcall %s %s(%s) { }' % (rtype, name, 'void' if use_void else '')
            expected = f"let {name}(u'ret: channel, u'end: channel) = out(u'end, true)."
            yield source, expected

    def _subtest_nullary_function_definitions_no_body(self, funcname: str):
        for use_void in (False, True):
            self.check_single_function_subtest(
                self._define_empty_void_nullary_function, funcname, use_void)
            self.check_single_function_subtests(
                self._define_empty_nonvoid_nullary_function, funcname, use_void)

    def _define_empty_void_unary_function(self, name: str,
            arr_specifier: str = '') -> Tuple[str, str]:
        source = 'inline void %s(char x%s) { }' % (name, arr_specifier)
        pvtype = 'nat' if not arr_specifier else 'bitstring'
        expected = f"let {name}(x: {pvtype}, u'end: channel) = out(u'end, true)."
        return source, expected

    def _define_empty_nonvoid_unary_function(self, name: str,
            arr_specifier: str = '') -> Generator:
        for rtype, _ in self._types_table.items():
            source = '__inline__ %s %s(char x%s) { }' % (rtype, name, arr_specifier)
            pvtype = 'nat' if not arr_specifier else 'bitstring'
            expected = f"let {name}(x: {pvtype}, u'ret: channel, u'end: channel) = out(u'end, true)."
            yield source, expected

    def _subtest_unary_function_definitions_no_body(self, funcname: str):
        for arr_specifier in '', '[]', '[][]', '[6]', '[42][]', '[SIZE]':
            self.check_single_function_subtest(
                self._define_empty_void_unary_function, funcname, arr_specifier)
            self.check_single_function_subtests(
                self._define_empty_nonvoid_unary_function, funcname, arr_specifier)

    def test_no_body_function_definitions(self):
        self._subtest_nullary_function_definitions_no_body(self._stress_test_identifier)
        self._subtest_unary_function_definitions_no_body(self._stress_test_identifier)
