#!/usr/bin/env python3
from typing import Callable
import unittest


from translator import Translator
from tests.common import *


class FunctionsDeclarationsTestCase(unittest.TestCase):
    def _declare_void_nullary_function(self, name: str, use_void: bool = False):
        source = f'static _Noreturn inline void {name}({"void" if use_void else ""});'
        model = Translator.from_line(source, False).translate()
        self.assertTrue(not model.preamble)
        self.assertEqual((name, f'let {name}(u\'end: channel) = out(u\'end, true).'), model.functions[0])

    def _declare_nonvoid_nullary_function(self, name: str, use_void: bool = False):
        tmplt = 'extern __stdcall __inline__ {} %s(%s);' \
            % (name, 'void' if use_void else '')
        for rtype, pvtype in TESTS_TYPES.items():
            model = Translator.from_line(tmplt.format(rtype), False).translate()
            self.assertTrue(not model.preamble)
            self.assertEqual((name, f'fun {name}(): {pvtype}.'),
                             model.functions[0])

    def _subtest_nullary_function_declarations(self, name: str):
        for use_void in (False, True):
            self._declare_void_nullary_function(name, use_void)
            self._declare_nonvoid_nullary_function(name, use_void)

    def _declare_void_unary_function(self, name: str, anon: bool):
        tmplt = 'void {}({});'
        for ptype, pvtype in TESTS_TYPES.items():
            param_name = '_p0' if anon else f'arg_{name}'
            param = ptype + ('' if anon else f' {param_name}')
            model = Translator.from_line(tmplt.format(name, param),
                                         False).translate()
            _, actual = model.functions[0]
            expected = f'let {name}({param_name}: {pvtype}, u\'end: channel) = out(u\'end, true).'
            self.assertEqual(actual, expected)

    def _declare_nonvoid_unary_function(self, name: str, anon: bool):
        tmplt = 'static {} %s({});' % (name)
        pname = '_p0' if anon else f'arg_{name}'
        for rtype, rpvtype in TESTS_TYPES.items():
            for ptype, ppvtype in TESTS_TYPES.items():
                param = ptype + ('' if anon else f' {pname}')
                _, actual = Translator.from_line(tmplt.format(rtype, param),
                                                False).translate().functions[0]
                expected = f'fun {name}({ppvtype}): {rpvtype}.'
                self.assertEqual(actual, expected)

    def _subtest_unary_function_declarations(self, name: str):
        for anon in (False, True):
            self._declare_void_unary_function(name, anon)
            self._declare_nonvoid_unary_function(name, anon)

    def test_single_function_declaration(self):
        def at_subtest(fun: Callable, *args):
            with self.subTest(fun.__name__):
                fun(*args)
        for name in IDENTIFIERS:
            at_subtest(self._subtest_nullary_function_declarations, name)
        at_subtest(self._subtest_unary_function_declarations, SOME_IDENTIFIER)
