#!/usr/bin/env python3
import unittest

from translator import Translator
from tests.common import *


class BranchingTestCase(unittest.TestCase):
    def test_if_without_else_branch(self):
        source = 'void main() { if (false) { int a = 8; } }'
        expected = '''let main(_end: channel) = new _if_end0: channel;
((
if false then new a: nat; out(_if_end0, true) else out(_if_end0, true))
| (in(_if_end0, _tvar0: bool);
)); out(_end, true).'''
        model = Translator.from_line(source, False).translate()
        self.assertEqual(('main', expected), model.functions[0])

    def test_if_with_else_branch(self):
        source = 'void main() { if (false) { int a = 8; } else { short b; } }'
        expected = '''let main(_end: channel) = new _if_end0: channel;
((
if false then new a: nat; out(_if_end0, true) else new b: nat; out(_if_end0, true))
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
new _if_end0: channel;
((
let _tvar0: bool = a < 6 in
if _tvar0 then let _tvar1 = _mul(a, 4) in
let a = _tvar1 in out(_if_end0, true) else let _tvar2 = a + 28 in
let a = _tvar2 in out(_if_end0, true))
| (in(_if_end0, _tvar3: bool);
))
new b: nat;
new _if_end1: channel;
((
let _tvar5: nat = _mul(a, 2) in
let _tvar4: nat = a + b in
let _tvar6: bool = _tvar4 > _tvar5 in
if _tvar6 then let _tvar7 = b - 50 in
let b = _tvar7 in out(_if_end1, true) else out(_if_end1, true))
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
new _if_end1: channel;
((
if true then new _if_end0: channel;
((
if false then let _tvar0 = _mod(a, 4) in
let a = _tvar0 in out(_if_end0, true) else out(_if_end0, true))
| (in(_if_end0, _tvar1: bool);
)) out(_if_end1, true) else out(_if_end1, true))
| (in(_if_end1, _tvar2: bool);
)); out(_end, true).'''
        model = Translator.from_line(source, False).translate()
        _, actual = model.functions[0]
        self.assertEqual(expected, actual)

    def test_switch_single_default(self):
        source = '''void main()
{
    int selector;
    switch (selector) default: selector = 42;
}'''
        expected = '''let main(_end: channel) = new selector: nat;
new _sw0_end: channel;
new _sw0_default: channel;
((
out(_sw0_default, true))
| (in(_sw0_default, _tvar0: bool); let selector = 42 in out(_sw0_end, true))
| (in(_sw0_end, _tvar1: bool);
)); out(_end, true).'''
        model = Translator.from_line(source, False).translate()
        _, actual = model.functions[0]
        self.assertEqual(expected, actual)

    def test_switch_single_case(self):
        source = '''void main()
{
    int selector;
    switch (selector) case 42: selector = 42;
}'''
        expected = '''let main(_end: channel) = new selector: nat;
new _sw0_end: channel;
new _sw0_case0: channel;
((
if selector = 42 then out(_sw0_case0, true) else out(_sw0_end, true))
| (in(_sw0_case0, _tvar0: bool); let selector = 42 in out(_sw0_end, true))
| (in(_sw0_end, _tvar1: bool);
)); out(_end, true).'''
        model = Translator.from_line(source, False).translate()
        _, actual = model.functions[0]
        self.assertEqual(expected, actual)

    def test_multiple_cases_and_default(self):
        source = '''void main()
{
    int selector;
    switch (selector) {
        case 0: selector = 1;
        case 1: selector = 2;
        case 2: selector = 4;
        case 3: selector = 8;
        default: selector = 16;
    }
}'''
        expected = '''let main(_end: channel) = new selector: nat;
new _sw0_end: channel;
new _sw0_default: channel;
new _sw0_case0: channel;
new _sw0_case1: channel;
new _sw0_case2: channel;
new _sw0_case3: channel;
((
if selector = 0 then out(_sw0_case3, true)
else if selector = 1 then out(_sw0_case2, true)
else if selector = 2 then out(_sw0_case1, true)
else if selector = 3 then out(_sw0_case0, true)
else out(_sw0_default, true))
| (in(_sw0_case3, _tvar3: bool); let selector = 1 in out(_sw0_case2, true))
| (in(_sw0_case2, _tvar2: bool); let selector = 2 in out(_sw0_case1, true))
| (in(_sw0_case1, _tvar1: bool); let selector = 4 in out(_sw0_case0, true))
| (in(_sw0_case0, _tvar0: bool); let selector = 8 in out(_sw0_default, true))
| (in(_sw0_default, _tvar4: bool); let selector = 0 in out(_sw0_end, true))
| (in(_sw0_end, _tvar4: bool);
)); out(_end, true).'''
        model = Translator.from_line(source, False).translate()
        _, actual = model.functions[0]
        self.maxDiff = None
        self.assertEqual(expected, actual)
