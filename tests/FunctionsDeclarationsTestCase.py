#!/usr/bin/env python3
from typing import Tuple, Generator
import unittest

from tests.common import *


class FunctionsDeclarationsTestCase(unittest.TestCase):
    def _declare_void_nullary_function(self, name: str,
                                       use_void: bool = False) -> Tuple[str, str]:
        source = f'static _Noreturn inline void {name}({"void" if use_void else ""});'
        return source, f'let {name}(u\'end: channel) = out(u\'end, true).'

    def _declare_nonvoid_nullary_function(self, name: str,
                                          use_void: bool = False) -> Generator:
        tmplt = 'extern __stdcall __inline__ {} %s(%s);' \
            % (name, 'void' if use_void else '')
        for rtype, pvtype in TESTS_TYPES.items():
            yield tmplt.format(rtype), f'fun {name}(): {pvtype}.'

    def _subtest_nullary_function_declarations(self, name: str):
        for use_void in (False, True):
            check_subtest_single(self, self._declare_void_nullary_function, name, use_void)
            check_subtests(self, self._declare_nonvoid_nullary_function, name, use_void)

    def _declare_void_unary_function(self, name: str, anon: bool) -> Generator:
        tmplt = 'void {}({});'
        for ptype, pvtype in TESTS_TYPES.items():
            param_name = '_p0' if anon else f'arg_{name}'
            param = ptype + ('' if anon else f' {param_name}')
            expected = f'let {name}({param_name}: {pvtype}, u\'end: channel) = out(u\'end, true).'
            yield tmplt.format(name, param), expected

    def _declare_nonvoid_unary_function(self, name: str, anon: bool) -> Generator:
        tmplt = 'static {} %s({});' % (name)
        pname = '_p0' if anon else f'arg_{name}'
        for rtype, rpvtype in TESTS_TYPES.items():
            for ptype, ppvtype in TESTS_TYPES.items():
                param = ptype + ('' if anon else f' {pname}')
                expected = f'fun {name}({ppvtype}): {rpvtype}.'
                yield tmplt.format(rtype, param), expected

    def _subtest_unary_function_declarations(self, name: str):
        for anon in (False, True):
            check_subtests(self, self._declare_void_unary_function, name, anon)
            check_subtests(self, self._declare_nonvoid_unary_function, name, anon)

    def test_single_function_declaration(self):
        for name in IDENTIFIERS:
            self._subtest_nullary_function_declarations(name)
        self._subtest_unary_function_declarations(SOME_IDENTIFIER)
