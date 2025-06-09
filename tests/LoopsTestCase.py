#!/usr/bin/env python3
from typing import Tuple
import unittest

from translator import Translator
from tests.common import *


class LoopsTestCase(unittest.TestCase):
    def _subtest_simplest_while(self) -> Tuple[str, str, str]:
        source = 'void main() { while (true) { int a = 7; } }'
        expected = '''let main() = new _while_begin0: channel;
new _while_end0: channel;
new _while_cond0: channel;
((
out(_while_cond0, true))
| !(in(_while_cond0, _while_var0: bool); if _while_var0 then out(_while_begin0, true) else out(_while_end0, true))
| !(in(_while_begin0, _tvar0: bool); new a: nat; out(_while_cond0, true))
| (in(_while_end0, _tvar1: bool);
)).'''
        return 'simplest-while', source, expected

    def _subtest_simplest_dowhile(self) -> Tuple[str, str, str]:
        source = 'void main() { do { int b = 0x54; } while (true); }'
        expected = '''let main() = new _dowhile_begin0: channel;
new _dowhile_end0: channel;
new _dowhile_cond0: channel;
((
out(_dowhile_cond0, true))
| !(in(_dowhile_cond0, _dowhile_var0: bool); if _dowhile_var0 then out(_dowhile_begin0, true) else out(_dowhile_end0, true))
| !(in(_dowhile_begin0, _tvar0: bool); new b: nat; out(_dowhile_cond0, true))
| (in(_dowhile_end0, _tvar1: bool);
)).'''
        return 'simplest-do-while', source, expected

    def _subtest_simplest_for(self) -> Tuple[str, str, str]:
        source = 'void main() { int a = 0; for (int i = 0; i < 10; i = i + 1) a = 2 * i; }'
        expected = '''let main() = new a: nat;
new _for_begin0: channel;
new _for_end0: channel;
new _for_cond0: channel;
new i: nat;
((
let _tvar0: bool = i < 10 in  out(_for_cond0, _tvar0))
| !(in(_for_cond0, _for_var0: bool); if _for_var0 then out(_for_begin0, true) else out(_for_end0, true))
| !(in(_for_begin0, _tvar3: bool); let _tvar2: nat = _mul(2, i) in 
let a = _tvar2 in  let _tvar1: nat = i + 1 in 
let i = _tvar1 in  let _tvar0: bool = i < 10 in  out(_for_cond0, _tvar0))
| (in(_for_end0, _tvar4: bool);
)).'''
        return 'simplest-for', source, expected

    def test_simplest_loops(self):
        subtests = [
            self._subtest_simplest_while,
            self._subtest_simplest_dowhile,
            self._subtest_simplest_for
        ]
        for subtest in subtests:
            name, source, expected = subtest()
            with self.subTest(name):
                model = Translator.from_line(source, False).translate()
                _, actual = model.functions[0]
                self.assertEqual(expected, actual)

    def test_nested_whiles(self):
        source = '''void main()
{
    char const* foo = "Hello, World!\\n";
    while (true)
        while (false) foo = "Hello, World!\\n";
}'''
        expected = '''let main() = new foo: bitstring;
new _while_begin1: channel;
new _while_end1: channel;
new _while_cond1: channel;
((
out(_while_cond1, true))
| !(in(_while_cond1, _while_var1: bool); if _while_var1 then out(_while_begin1, true) else out(_while_end1, true))
| !(in(_while_begin1, _tvar2: bool); new _while_begin0: channel;
new _while_end0: channel;
new _while_cond0: channel;
((
out(_while_cond0, false))
| !(in(_while_cond0, _while_var0: bool); if _while_var0 then out(_while_begin0, true) else out(_while_end0, true))
| !(in(_while_begin0, _tvar0: bool); let foo = _strlit0 in  out(_while_cond0, false))
| (in(_while_end0, _tvar1: bool);
)) out(_while_cond1, true))
| (in(_while_end1, _tvar3: bool);
)).'''
        model = Translator.from_line(source, False).translate()
        _, actual = model.functions[0]
        self.assertEqual(expected, actual)

    def _subtest_no_cond_for(self):
        source = '''void main()
{
    int a = 0;
    for (int i = 0;;i = i + 1)
        a += i;
}'''
        expected = '''let main() = new a: nat;
new _for_begin0: channel;
new _for_end0: channel;
new _for_cond0: channel;
new i: nat;
((
out(_for_cond0, true))
| !(in(_for_cond0, _for_var0: bool); if _for_var0 then out(_for_begin0, true) else out(_for_end0, true))
| !(in(_for_begin0, _tvar2: bool); let _tvar1 = a + i in 
let a = _tvar1 in  let _tvar0: nat = i + 1 in 
let i = _tvar0 in  out(_for_cond0, true))
| (in(_for_end0, _tvar3: bool);
)).'''
        return 'no-condition-for', source, expected

    def _subtest_no_iter_for(self):
        source = '''void main()
{
    int a;
    for (a = 1;a != 4;)
        a = a << 1;
}'''
        expected = '''let main() = new a: nat;
new _for_begin0: channel;
new _for_end0: channel;
new _for_cond0: channel;
let a = 1 in 
((
let _tvar0: bool = a <> 4 in  out(_for_cond0, _tvar0))
| !(in(_for_cond0, _for_var0: bool); if _for_var0 then out(_for_begin0, true) else out(_for_end0, true))
| !(in(_for_begin0, _tvar2: bool); let _tvar1: nat = _shl(a, 1) in 
let a = _tvar1 in  let _tvar0: bool = a <> 4 in  out(_for_cond0, _tvar0))
| (in(_for_end0, _tvar3: bool);
)).'''
        return 'no-iteration-for', source, expected

    def _subtest_infinite_for(self):
        source = 'void main() { int a = 1; for (;;) a *= 2; }'
        expected = '''let main() = new a: nat;
new _for_begin0: channel;
new _for_end0: channel;
new _for_cond0: channel;
((
out(_for_cond0, true))
| !(in(_for_cond0, _for_var0: bool); if _for_var0 then out(_for_begin0, true) else out(_for_end0, true))
| !(in(_for_begin0, _tvar1: bool); let _tvar0 = _mul(a, 2) in 
let a = _tvar0 in  out(_for_cond0, true))
| (in(_for_end0, _tvar2: bool);
)).'''
        return 'infinite-for', source, expected

    def test_for_loop_variants(self):
        subtests = [
            self._subtest_no_cond_for,
            self._subtest_no_iter_for,
            self._subtest_infinite_for
        ]
        for subtest in subtests:
            name, source, expected = subtest()
            with self.subTest(name):
                model = Translator.from_line(source, False).translate()
                _, actual = model.functions[0]
                self.maxDiff = None
                self.assertEqual(expected, actual)
