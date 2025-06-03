#!/usr/bin/env python3
import unittest

from translator import Translator
from tests.common import *


class IfStatementTestCase(unittest.TestCase):
    def test_without_else_branch(self):
        source = 'void main() { if (false) { int a = 8; } }'
        expected = '''let main() = new if_cond0: channel;
new if_end0: channel;
((
out(if_cond0, false))
| (in(if_cond0, _cond0: bool); if _cond0 then new a: nat; out(if_end0, true) else out(if_end0, true))
| (in(if_end0, _tvar0: bool);
)).'''
        model = Translator.from_line(source, False).translate()
        self.assertEqual(('main', expected), model.functions[0])

    def test_with_else_branch(self):
        source = 'void main() { if (false) { int a = 8; } else { short b; } }'
        expected = '''let main() = new if_cond0: channel;
new if_end0: channel;
((
out(if_cond0, false))
| (in(if_cond0, _cond0: bool); if _cond0 then new a: nat; out(if_end0, true) else new b: nat; out(if_end0, true))
| (in(if_end0, _tvar0: bool);
)).'''
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
        expected = '''let main() = new a: nat;
new if_cond1: channel;
new if_end1: channel;
((
let _tvar0: bool = a < 6 in
out(if_cond1, _tvar0))
| (in(if_cond1, _cond1: bool); if _cond1 then let _tvar1 = _mul(a, 4) in 
let a = _tvar1 in  out(if_end1, true) else let _tvar2 = a + 28 in 
let a = _tvar2 in  out(if_end1, true))
| (in(if_end1, _tvar9: bool);
new b: nat;
new if_cond0: channel;
new if_end0: channel;
((
let _tvar4: nat = _mul(a, 2) in 
let _tvar3: nat = a + b in 
let _tvar5: bool = _tvar3 > _tvar4 in
out(if_cond0, _tvar5))
| (in(if_cond0, _cond0: bool); if _cond0 then let _tvar6 = b - 50 in 
let b = _tvar6 in  out(if_end0, true) else out(if_end0, true))
| (in(if_end0, _tvar8: bool);
let _tvar7: nat = a + b in 
let a = _tvar7 in 
))
)).'''
        model = Translator.from_line(source, False).translate()
        self.maxDiff = None
        self.assertEqual(('main', expected), model.functions[0])
