#!/usr/bin/env python3
from typing import Tuple
import unittest

from translator import Translator
from tests.common import *


class LoopsTestCase(unittest.TestCase):
    def _subtest_simplest_while(self) -> Tuple[str, str, str]:
        source = 'void main() { while (true) { int a = 7; } }'
        expected = '''let main(u'end: channel) = new u'while_begin0: channel;
new u'while_end0: channel;
new u'while_cond0: channel;
((
out(u'while_cond0, true)
)
| !(in(u'while_cond0, u'while_var0: bool); if u'while_var0 then out(u'while_begin0, true) else out(u'while_end0, true))
| !(in(u'while_begin0, u'tvar0: bool);
new a: nat;
out(u'while_cond0, true)
)
| (in(u'while_end0, u'tvar1: bool);
)); out(u'end, true).'''
        return 'simplest-while', source, expected

    def _subtest_simplest_dowhile(self) -> Tuple[str, str, str]:
        source = 'void main() { do { int b = 0x54; } while (true); }'
        expected = '''let main(u'end: channel) = new u'dowhile_begin0: channel;
new u'dowhile_end0: channel;
new u'dowhile_cond0: channel;
((
out(u'dowhile_cond0, true))
| !(in(u'dowhile_cond0, u'dowhile_var0: bool); if u'dowhile_var0 then out(u'dowhile_begin0, true) else out(u'dowhile_end0, true))
| !(in(u'dowhile_begin0, u'tvar0: bool);
new b: nat;
out(u'dowhile_cond0, true)
)
| (in(u'dowhile_end0, u'tvar1: bool);
)); out(u'end, true).'''
        return 'simplest-do-while', source, expected

    def _subtest_simplest_for(self) -> Tuple[str, str, str]:
        source = 'void main() { int a = 0; for (int i = 0; i < 10; i = i + 1) a = 2 * i; }'
        expected = '''let main(u'end: channel) = new a: nat;
new u'for_begin0: channel;
new u'for_end0: channel;
new u'for_cond0: channel;
((
new i: nat;
let u'tvar0: bool = i < 10 in
out(u'for_cond0, u'tvar0)
)
| !(in(u'for_cond0, u'for_var0: bool); if u'for_var0 then out(u'for_begin0, true) else out(u'for_end0, true))
| !(in(u'for_begin0, u'tvar3: bool);
let u'tvar2: nat = u'mul(2, i) in
let a = u'tvar2 in
let u'tvar1: nat = i + 1 in
let i = u'tvar1 in
let u'tvar0: bool = i < 10 in
out(u'for_cond0, u'tvar0)
)
| (in(u'for_end0, u'tvar4: bool);
)); out(u'end, true).'''
        return 'simplest-for', source, expected

    def test_simplest_loops(self):
        subtests = [
            self._subtest_simplest_while,
            self._subtest_simplest_dowhile,
            self._subtest_simplest_for
        ]
        self.maxDiff = None
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
        expected = '''let main(u'end: channel) = new foo: bitstring;
new u'while_begin1: channel;
new u'while_end1: channel;
new u'while_cond1: channel;
((
out(u'while_cond1, true)
)
| !(in(u'while_cond1, u'while_var1: bool); if u'while_var1 then out(u'while_begin1, true) else out(u'while_end1, true))
| !(in(u'while_begin1, u'tvar2: bool);
new u'while_begin0: channel;
new u'while_end0: channel;
new u'while_cond0: channel;
((
out(u'while_cond0, false)
)
| !(in(u'while_cond0, u'while_var0: bool); if u'while_var0 then out(u'while_begin0, true) else out(u'while_end0, true))
| !(in(u'while_begin0, u'tvar0: bool);
let foo = u'strlit0 in
out(u'while_cond0, false)
)
| (in(u'while_end0, u'tvar1: bool);
))
out(u'while_cond1, true)
)
| (in(u'while_end1, u'tvar3: bool);
)); out(u'end, true).'''
        model = Translator.from_line(source, False).translate()
        _, actual = model.functions[0]
        self.maxDiff = None
        self.assertEqual(expected, actual)

    def _subtest_no_cond_for(self):
        source = '''void main()
{
    int a = 0;
    for (int i = 0;;i = i + 1)
        a += i;
}'''
        expected = '''let main(u'end: channel) = new a: nat;
new u'for_begin0: channel;
new u'for_end0: channel;
new u'for_cond0: channel;
((
new i: nat;
out(u'for_cond0, true)
)
| !(in(u'for_cond0, u'for_var0: bool); if u'for_var0 then out(u'for_begin0, true) else out(u'for_end0, true))
| !(in(u'for_begin0, u'tvar2: bool);
let u'tvar1 = a + i in
let a = u'tvar1 in
let u'tvar0: nat = i + 1 in
let i = u'tvar0 in
out(u'for_cond0, true)
)
| (in(u'for_end0, u'tvar3: bool);
)); out(u'end, true).'''
        return 'no-condition-for', source, expected

    def _subtest_no_iter_for(self):
        source = '''void main()
{
    int a;
    for (a = 1;a != 4;)
        a = a << 1;
}'''
        expected = '''let main(u'end: channel) = new a: nat;
new u'for_begin0: channel;
new u'for_end0: channel;
new u'for_cond0: channel;
((
let a = 1 in
let u'tvar0: bool = a <> 4 in
out(u'for_cond0, u'tvar0)
)
| !(in(u'for_cond0, u'for_var0: bool); if u'for_var0 then out(u'for_begin0, true) else out(u'for_end0, true))
| !(in(u'for_begin0, u'tvar2: bool);
let u'tvar1: nat = u'shl(a, 1) in
let a = u'tvar1 in
let u'tvar0: bool = a <> 4 in
out(u'for_cond0, u'tvar0)
)
| (in(u'for_end0, u'tvar3: bool);
)); out(u'end, true).'''
        return 'no-iteration-for', source, expected

    def _subtest_infinite_for(self):
        source = 'void main() { int a = 1; for (;;) a *= 2; }'
        expected = '''let main(u'end: channel) = new a: nat;
new u'for_begin0: channel;
new u'for_end0: channel;
new u'for_cond0: channel;
((
out(u'for_cond0, true)
)
| !(in(u'for_cond0, u'for_var0: bool); if u'for_var0 then out(u'for_begin0, true) else out(u'for_end0, true))
| !(in(u'for_begin0, u'tvar1: bool);
let u'tvar0 = u'mul(a, 2) in
let a = u'tvar0 in
out(u'for_cond0, true)
)
| (in(u'for_end0, u'tvar2: bool);
)); out(u'end, true).'''
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
