#!/usr/bin/env python3
import unittest

from translator import Translator
from tests.common import *


class FunctionDefinitionsTestCase(unittest.TestCase):
    def _function_define_empty_void_0_arity(self, name: str, use_void: bool = False):
        source = '_Noreturn void %s(%s) { }' % (name, 'void' if use_void else '')
        model = Translator.from_line(source, False).translate()
        self.assertTrue(not model.preamble)
        self.assertEqual((name, f'let {name}() = 0.'), model.functions[0])

    def _function_define_empty_nonvoid_0_arity(self, name: str, use_void: bool = False):
        for rtype, _ in TESTS_TYPES.items():
            tmplt = '__stdcall %s %s(%s) { }' % (rtype, name,
                                                 'void' if use_void else '')
            model = Translator.from_line(tmplt, False).translate()
            self.assertTrue(not model.preamble)
            self.assertEqual((name, f'let {name}(_ret_ch: channel) = 0.'),
                             model.functions[0])

    def _function_0_arity_definitions_empty_subtest(self, name: str):
        for use_void in (False, True):
            self._function_define_empty_void_0_arity(name, use_void)
            self._function_define_empty_nonvoid_0_arity(name, use_void)

    def test_no_body_function_definition(self):
        def at_subtest(subtest: str, fun):
            with self.subTest(f'{subtest}'):
                fun(SOME_IDENTIFIER)
        at_subtest('function-0_arity_definitions-empty',
                   self._function_0_arity_definitions_empty_subtest)
