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

    def test_simplest_loops(self):
        subtests = [
            self._subtest_simplest_while,
            self._subtest_simplest_dowhile
        ]
        for subtest in subtests:
            name, source, expected = subtest()
            with self.subTest(name):
                model = Translator.from_line(source, False).translate()
                _, actual = model.functions[0]
                self.assertEqual(expected, actual)
