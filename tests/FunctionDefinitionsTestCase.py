#!/usr/bin/env python3
from typing import Callable
import unittest

from translator import Translator
from tests.common import *


class FunctionDefinitionsTestCase(unittest.TestCase):
    def _define_empty_void_nullary_function(self, name: str, use_void: bool = False):
        source = '_Noreturn void %s(%s) { }' % (name, 'void' if use_void else '')
        model = Translator.from_line(source, False).translate()
        self.assertTrue(not model.preamble)
        _, actual = model.functions[0]
        expected = f"let {name}(u'end: channel) = out(u'end, true)."
        self.assertEqual(actual, expected)

    def _define_empty_nonvoid_nullary_function(self, name: str, use_void: bool = False):
        for rtype, _ in TESTS_TYPES.items():
            tmplt = '__stdcall %s %s(%s) { }' % (rtype, name,
                                                 'void' if use_void else '')
            model = Translator.from_line(tmplt, False).translate()
            self.assertTrue(not model.preamble)
            _, actual = model.functions[0]
            expected = f"let {name}(u'ret: channel, u'end: channel) = out(u'end, true)."
            self.assertEqual(actual, expected)

    def _subtest_nullary_function_definitions_no_body(self, funcname: str):
        for use_void in (False, True):
            self._define_empty_void_nullary_function(funcname, use_void)
            self._define_empty_nonvoid_nullary_function(funcname, use_void)

    def _define_empty_void_unary_function(self, name: str,
                                          arr_specifier: str = ''):
        source = 'inline void %s(char x%s) { }' % (name, arr_specifier)
        model = Translator.from_line(source, False).translate()
        _, actual = model.functions[0]
        pvtype = 'nat' if not arr_specifier else 'bitstring'
        expected = f"let {name}(x: {pvtype}, u'end: channel) = out(u'end, true)."
        self.assertEqual(actual, expected)

    def _define_empty_nonvoid_unary_function(self, name: str,
                                             arr_specifier: str = ''):
        for rtype, _ in TESTS_TYPES.items():
            source = '__inline__ %s %s(char x%s) { }' % (rtype, name, arr_specifier)
            model = Translator.from_line(source, False).translate()
            _, actual = model.functions[0]
            pvtype = 'nat' if not arr_specifier else 'bitstring'
            expected = f"let {name}(x: {pvtype}, u'ret: channel, u'end: channel) = out(u'end, true)."
            self.assertEqual(actual, expected)

    def _subtest_unary_function_definitions_no_body(self, funcname: str):
        for arr_specifier in '', '[]', '[][]', '[6]', '[42][]', '[SIZE]':
            self._define_empty_void_unary_function(funcname, arr_specifier)
            self._define_empty_nonvoid_unary_function(funcname, arr_specifier)

    def test_no_body_function_definitions(self):
        def at_subtest(fun: Callable):
            with self.subTest(fun.__name__):
                fun(SOME_IDENTIFIER)
        at_subtest(self._subtest_nullary_function_definitions_no_body)
        at_subtest(self._subtest_unary_function_definitions_no_body)
