#!/usr/bin/env python3
from typing import Tuple, Generator

from tests.TranslatorCommonTestCase import TranslatorCommonTestCase


class FunctionsDeclarationsTestCase(TranslatorCommonTestCase):
    def _declare_void_nullary_function(self, name: str,
                                       use_void: bool = False) -> Tuple[str, str]:
        source = f'static _Noreturn inline void {name}({"void" if use_void else ""});'
        return source, f'let {name}(u\'end: channel) = out(u\'end, true).'

    def _declare_nonvoid_nullary_function(self, name: str,
                                          use_void: bool = False) -> Generator:
        tmplt = 'extern __stdcall __inline__ {} %s(%s);' \
            % (name, 'void' if use_void else '')
        for rtype, pvtype in self._types_table.items():
            yield tmplt.format(rtype), f'fun {name}(): {pvtype}.'

    def _subtest_nullary_function_declarations(self, name: str):
        for use_void in (False, True):
            self.check_single_function_subtest(
                self._declare_void_nullary_function, name, use_void)
            self.check_single_function_subtests(
                self._declare_nonvoid_nullary_function, name, use_void)

    def _declare_void_unary_function(self, name: str, anon: bool) -> Generator:
        tmplt = 'void {}({});'
        for ptype, pvtype in self._types_table.items():
            param_name = '_p0' if anon else f'arg_{name}'
            param = ptype + ('' if anon else f' {param_name}')
            expected = f'let {name}({param_name}: {pvtype}, u\'end: channel) = out(u\'end, true).'
            yield tmplt.format(name, param), expected

    def _declare_nonvoid_unary_function(self, name: str, anon: bool) -> Generator:
        tmplt = 'static {} %s({});' % (name)
        pname = '_p0' if anon else f'arg_{name}'
        for rtype, rpvtype in self._types_table.items():
            for ptype, ppvtype in self._types_table.items():
                param = ptype + ('' if anon else f' {pname}')
                expected = f'fun {name}({ppvtype}): {rpvtype}.'
                yield tmplt.format(rtype, param), expected

    def _subtest_unary_function_declarations(self, name: str):
        for anon in (False, True):
            self.check_single_function_subtests(
                self._declare_void_unary_function, name, anon)
            self.check_single_function_subtests(
                self._declare_nonvoid_unary_function, name, anon)

    def test_single_function_declaration(self):
        for name in self._stress_identifiers:
            self._subtest_nullary_function_declarations(name)
        self._subtest_unary_function_declarations(self._stress_test_identifier)

    def _subtest_void_unary_function_declaration(self, name: str,
            array_specifier: str) -> Generator:
        tmplt = '__declspec(dllimport) void {}({}{});'
        for ptype, pvtype in self._types_table.items():
            if not (not array_specifier):
                pvtype = 'bitstring'
            expected = f'let {name}(_p0: {pvtype}, u\'end: channel) = out(u\'end, true).'
            yield tmplt.format(name, ptype, array_specifier), expected

    def test_single_void_unary_function_declaration_arrays(self):
        for array_specifier in self._array_specifiers:
            self.check_single_function_subtests(
                self._subtest_void_unary_function_declaration,
                self._stress_test_identifier, array_specifier)
