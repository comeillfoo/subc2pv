#!/usr/bin/env python3
from typing import Tuple
import unittest


from tests.common import *

class FunctionCallTestCase(unittest.TestCase):
    def _funcall_nothing_around(self) -> Tuple[str, str]:
        source = '''void main()
{
    main();
}'''
        expected = '''let main(u'end: channel) = new u'fcall_begin0: channel;
new u'fcall_end0: channel;
((
out(u'fcall_begin0, true))
| (in(u'fcall_begin0, u'tvar0: bool);
main(u'fcall_end0)
)
| (in(u'fcall_end0, u'tvar1: bool);
)); out(u'end, true).'''
        return source, expected

    def _funcall_no_subsequent(self) -> Tuple[str, str]:
        source = '''void main(int argc)
{
    int args = 0;
    main(args);
}'''
        expected = '''let main(argc: nat, u'end: channel) = new args: nat;
new u'fcall_begin0: channel;
new u'fcall_end0: channel;
((
out(u'fcall_begin0, true))
| (in(u'fcall_begin0, u'tvar0: bool);
main(args, u'fcall_end0)
)
| (in(u'fcall_end0, u'tvar1: bool);
)); out(u'end, true).'''
        return source, expected

    def _funcall_no_preceding(self) -> Tuple[str, str]:
        source = '''void main(int argc)
{
    main(argc);
    int args = 0;
}'''
        expected = '''let main(argc: nat, u'end: channel) = new u'fcall_begin0: channel;
new u'fcall_end0: channel;
((
out(u'fcall_begin0, true))
| (in(u'fcall_begin0, u'tvar0: bool);
main(argc, u'fcall_end0)
)
| (in(u'fcall_end0, u'tvar1: bool);
new args: nat;
)); out(u'end, true).'''
        return source, expected

    def _funcall_both_around(self) -> Tuple[str, str]:
        source = '''void main(int a)
{
    int b = 8;
    main(a + b);
    int c = 6;
}'''
        expected = '''let main(a: nat, u'end: channel) = new b: nat;
new u'fcall_begin0: channel;
new u'fcall_end0: channel;
((
out(u'fcall_begin0, true))
| (in(u'fcall_begin0, u'tvar1: bool);
let u'tvar0: nat = a + b in
main(u'tvar0, u'fcall_end0)
)
| (in(u'fcall_end0, u'tvar2: bool);
new c: nat;
)); out(u'end, true).'''
        return source, expected


    def test_funcall_as_statements(self):
        check_subtest_single(self, self._funcall_nothing_around)
        check_subtest_single(self, self._funcall_no_subsequent)
        check_subtest_single(self, self._funcall_no_preceding)
        check_subtest_single(self, self._funcall_both_around)
