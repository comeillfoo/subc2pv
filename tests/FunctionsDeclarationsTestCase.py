#!/usr/bin/env python3
import unittest


from translator import Translator
from tests.common import *


class FunctionsDeclarationsTestCase(unittest.TestCase):
    def _function_declare_void_0_arity(self, name: str, use_void: bool = False):
        source = f'static _Noreturn inline void {name}({"void" if use_void else ""});'
        model = Translator.from_line(source, False).translate()
        self.assertTrue(not model.preamble)
        self.assertEqual((name, f'let {name}(u\'end: channel) = out(u\'end, true).'), model.functions[0])

    def _function_declare_nonvoid_0_arity(self, name: str, use_void: bool = False):
        tmplt = 'extern __stdcall __inline__ {} %s(%s);' \
            % (name, 'void' if use_void else '')
        for rtype, pvtype in TESTS_TYPES.items():
            model = Translator.from_line(tmplt.format(rtype), False).translate()
            self.assertTrue(not model.preamble)
            self.assertEqual((name, f'fun {name}(): {pvtype}.'),
                             model.functions[0])

    def _function_0_arity_declarations_subtest(self, name: str):
        for use_void in (False, True):
            self._function_declare_void_0_arity(name, use_void)
            self._function_declare_nonvoid_0_arity(name, use_void)

    def _function_declare_void_1_arity(self, name: str, anon: bool):
        tmplt = 'void {}({});'
        for ptype, pvtype in TESTS_TYPES.items():
            param_name = '_p0' if anon else f'arg_{name}'
            param = ptype + ('' if anon else f' {param_name}')
            model = Translator.from_line(tmplt.format(name, param),
                                         False).translate()
            self.assertTrue(not model.preamble)
            self.assertEqual((name, f'let {name}({param_name}: {pvtype}, u\'end: channel) = out(u\'end, true).'),
                             model.functions[0])

    def _function_declare_nonvoid_1_arity(self, name: str, anon: bool):
        tmplt = 'static {} %s({});' % (name)
        pname = '_p0' if anon else f'arg_{name}'
        def _test_single(rtype: str, rpvtype: str, ptype: str, ppvtype: str):
            param = ptype + ('' if anon else f' {pname}')
            model = Translator.from_line(tmplt.format(rtype, param),
                                         False).translate()
            self.assertTrue(not model.preamble)
            self.assertEqual((name, f'fun {name}({ppvtype}): {rpvtype}.'),
                             model.functions[0])
        for rtype, rpvtype in TESTS_TYPES.items():
            for ptype, ppvtype in TESTS_TYPES.items():
                _test_single(rtype, rpvtype, ptype, ppvtype)

    def _function_1_arity_declarations_subtest(self, name: str):
        for anon in (False, True):
            self._function_declare_void_1_arity(name, anon)
            self._function_declare_nonvoid_1_arity(name, anon)

    def test_single_function_declaration(self):
        def at_subtest(subtest: str, fun, *args):
            with self.subTest(f'{subtest}'):
                fun(*args)
        for name in IDENTIFIERS:
            at_subtest('function-0_arity-declaration',
                       self._function_0_arity_declarations_subtest,
                       name)
        at_subtest('function-1_arity-declaration',
                   self._function_1_arity_declarations_subtest,
                   SOME_IDENTIFIER)
