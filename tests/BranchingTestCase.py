#!/usr/bin/env python3
import unittest

from translator import Translator
from tests.common import *


class BranchingTestCase(unittest.TestCase):
    def test_if_without_else_branch(self):
        source = 'void main() { if (false) { int a = 8; } }'
        expected = '''let main(u'end: channel) = new u'if_end0: channel;
((
if false then
new a: nat;
out(u'if_end0, true)
else
out(u'if_end0, true)
)
| (in(u'if_end0, u'tvar0: bool);
)); out(u'end, true).'''
        model = Translator.from_line(source, False).translate()
        self.assertEqual(('main', expected), model.functions[0])

    def test_if_with_else_branch(self):
        source = 'void main() { if (false) { int a = 8; } else { short b; } }'
        expected = '''let main(u'end: channel) = new u'if_end0: channel;
((
if false then
new a: nat;
out(u'if_end0, true)
else
new b: nat;
out(u'if_end0, true)
)
| (in(u'if_end0, u'tvar0: bool);
)); out(u'end, true).'''
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
        expected = '''let main(u'end: channel) = new a: nat;
new u'if_end0: channel;
((
let u'tvar0: bool = a < 6 in
if u'tvar0 then
let u'tvar1 = u'mul(a, 4) in
let a = u'tvar1 in
out(u'if_end0, true)
else
let u'tvar2 = a + 28 in
let a = u'tvar2 in
out(u'if_end0, true)
)
| (in(u'if_end0, u'tvar3: bool);
))
new b: nat;
new u'if_end1: channel;
((
let u'tvar5: nat = u'mul(a, 2) in
let u'tvar4: nat = a + b in
let u'tvar6: bool = u'tvar4 > u'tvar5 in
if u'tvar6 then
let u'tvar7 = b - 50 in
let b = u'tvar7 in
out(u'if_end1, true)
else
out(u'if_end1, true)
)
| (in(u'if_end1, u'tvar8: bool);
))
let u'tvar9: nat = a + b in
let a = u'tvar9 in out(u'end, true).'''
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
        expected = '''let main(u'end: channel) = new a: nat;
new u'if_end1: channel;
((
if true then
new u'if_end0: channel;
((
if false then
let u'tvar0 = u'mod(a, 4) in
let a = u'tvar0 in
out(u'if_end0, true)
else
out(u'if_end0, true)
)
| (in(u'if_end0, u'tvar1: bool);
))
out(u'if_end1, true)
else
out(u'if_end1, true)
)
| (in(u'if_end1, u'tvar2: bool);
)); out(u'end, true).'''
        model = Translator.from_line(source, False).translate()
        _, actual = model.functions[0]
        self.assertEqual(expected, actual)

    def test_switch_single_default(self):
        source = '''void main()
{
    int selector;
    switch (selector) default: selector = 42;
}'''
        expected = '''let main(u'end: channel) = new selector: nat;
new u'sw0_end: channel;
new u'sw0_default: channel;
((
out(u'sw0_default, true))
| (in(u'sw0_default, u'tvar0: bool);
let selector = 42 in
out(u'sw0_end, true))
| (in(u'sw0_end, u'tvar1: bool);
)); out(u'end, true).'''
        model = Translator.from_line(source, False).translate()
        _, actual = model.functions[0]
        self.assertEqual(expected, actual)

    def test_switch_single_case(self):
        source = '''void main()
{
    int selector;
    switch (selector) case 42: selector = 42;
}'''
        expected = '''let main(u'end: channel) = new selector: nat;
new u'sw0_end: channel;
new u'sw0_case0: channel;
((
if selector = 42 then out(u'sw0_case0, true) else out(u'sw0_end, true))
| (in(u'sw0_case0, u'tvar0: bool);
let selector = 42 in
out(u'sw0_end, true))
| (in(u'sw0_end, u'tvar1: bool);
)); out(u'end, true).'''
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
        expected = '''let main(u'end: channel) = new selector: nat;
new u'sw0_end: channel;
new u'sw0_default: channel;
new u'sw0_case0: channel;
new u'sw0_case1: channel;
new u'sw0_case2: channel;
new u'sw0_case3: channel;
((
if selector = 0 then out(u'sw0_case3, true)
else if selector = 1 then out(u'sw0_case2, true)
else if selector = 2 then out(u'sw0_case1, true)
else if selector = 3 then out(u'sw0_case0, true)
else out(u'sw0_default, true))
| (in(u'sw0_case3, u'tvar4: bool);
let selector = 1 in
out(u'sw0_case2, true))
| (in(u'sw0_case2, u'tvar3: bool);
let selector = 2 in
out(u'sw0_case1, true))
| (in(u'sw0_case1, u'tvar2: bool);
let selector = 4 in
out(u'sw0_case0, true))
| (in(u'sw0_case0, u'tvar1: bool);
let selector = 8 in
out(u'sw0_default, true))
| (in(u'sw0_default, u'tvar0: bool);
let selector = 16 in
out(u'sw0_end, true))
| (in(u'sw0_end, u'tvar5: bool);
)); out(u'end, true).'''
        model = Translator.from_line(source, False).translate()
        _, actual = model.functions[0]
        self.maxDiff = None
        self.assertEqual(expected, actual)
