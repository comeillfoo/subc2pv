#!/usr/bin/env python3
import unittest

from translator import Translator
from tests.common import *


class BranchingTestCase(unittest.TestCase):
    def test_without_else_branch(self):
        source = 'void main() { if (false) { int a = 8; } }'
        expected = '''let main(_end: channel) = new _if_cond0: channel;
new _if_end0: channel;
((
out(_if_cond0, false))
| (in(_if_cond0, _if_var0: bool); if _if_var0 then new a: nat; out(_if_end0, true) else out(_if_end0, true))
| (in(_if_end0, _tvar0: bool);
)); out(_end, true).'''
        model = Translator.from_line(source, False).translate()
        self.assertEqual(('main', expected), model.functions[0])

    def test_with_else_branch(self):
        source = 'void main() { if (false) { int a = 8; } else { short b; } }'
        expected = '''let main(_end: channel) = new _if_cond0: channel;
new _if_end0: channel;
((
out(_if_cond0, false))
| (in(_if_cond0, _if_var0: bool); if _if_var0 then new a: nat; out(_if_end0, true) else new b: nat; out(_if_end0, true))
| (in(_if_end0, _tvar0: bool);
)); out(_end, true).'''
        model = Translator.from_line(source, False).translate()
        self.assertEqual(('main', expected), model.functions[0])

    def test_two_ifs(self):
        source = '''void main()
{
    int a = 42;
    if (a < 6)
        a *= 4;
    else
        a += 28;

    int b = 4;
    if (a + b > a * 2)
        b -= 50;
    a = a + b;
}'''
        expected = '''let main(_end: channel) = new a: nat;
new _if_cond0: channel;
new _if_end0: channel;
((
let _tvar0: bool = a < 6 in
out(_if_cond0, _tvar0))
| (in(_if_cond0, _if_var0: bool); if _if_var0 then let _tvar1 = _mul(a, 4) in
let a = _tvar1 in out(_if_end0, true) else let _tvar2 = a + 28 in
let a = _tvar2 in out(_if_end0, true))
| (in(_if_end0, _tvar3: bool);
))
new b: nat;
new _if_cond1: channel;
new _if_end1: channel;
((
let _tvar5: nat = _mul(a, 2) in
let _tvar4: nat = a + b in
let _tvar6: bool = _tvar4 > _tvar5 in
out(_if_cond1, _tvar6))
| (in(_if_cond1, _if_var1: bool); if _if_var1 then let _tvar7 = b - 50 in
let b = _tvar6 in out(_if_end1, true) else out(_if_end1, true))
| (in(_if_end1, _tvar8: bool);
))
let _tvar9: nat = a + b in
let a = _tvar9 in out(_end, true).'''
        model = Translator.from_line(source, False).translate()
        self.maxDiff = None
        self.assertEqual(('main', expected), model.functions[0])

    def test_nested_ifs(self):
        source = '''void main()
{
    int a = 7;
    if (true)
        if (false) a %= 4;
}'''
        expected = '''let main(_end: channel) = new a: nat;
new _if_cond1: channel;
new _if_end1: channel;
((
out(_if_cond1, true))
| (in(_if_cond1, _if_var1: bool); if _if_var1 then new _if_cond0: channel;
new _if_end0: channel;
((
out(_if_cond0, false))
| (in(_if_cond0, _if_var0: bool); if _if_var0 then let _tvar0 = _mod(a, 4) in
let a = _tvar0 in out(_if_end0, true) else out(_if_end0, true))
| (in(_if_end0, _tvar1: bool);
)) out(_if_end1, true) else out(_if_end1, true))
| (in(_if_end1, _tvar2: bool);
)); out(_end, true).'''
        model = Translator.from_line(source, False).translate()
        _, actual = model.functions[0]
        self.assertEqual(expected, actual)
