import unittest
from typing import Tuple

from tests.common import *


class ExpressionsTestCase(unittest.TestCase):
    def _subtest_parenthesis(self, subc_tmplt: str,
                             pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('(42)'), pv_tmplt % ('', '42'))

    def _subtest_post_inc(self, subc_tmplt: str,
                          pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('6++'),
                pv_tmplt % ('let u\'tvar0: nat = 6 + 1 in\n', 'u\'tvar0'))

    def _subtest_post_dec(self, subc_tmplt: str,
                          pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('42--'),
                pv_tmplt % ('let u\'tvar0: nat = 42 - 1 in\n', 'u\'tvar0'))

    def _subtest_nullary_funcall(self, subc_tmplt: str,
                                 pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('baz()'),
                pv_tmplt % ('let u\'tvar0 = baz() in\n', 'u\'tvar0'))

    def _subtest_unary_funcall(self, subc_tmplt: str,
                               pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('baz(42)'),
                pv_tmplt % ('let u\'tvar0 = baz(42) in\n', 'u\'tvar0'))

    def _subtest_ternary_funcall(self, subc_tmplt: str,
                                 pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('foo(42, true, "text")'),
                pv_tmplt % ('let u\'tvar0 = foo(42, true, u\'strlit0) in\n',
                            'u\'tvar0'))

    def _subtest_sizeof(self, subc_tmplt: str, pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('sizeof(a)'),
                pv_tmplt % ('let u\'tvar0: nat = u\'sizeof(a) in\n', 'u\'tvar0'))

    def _subtest_logic_not(self, subc_tmplt: str,
                           pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('!0'),
                pv_tmplt % ('let u\'tvar0: bool = not(0) in\n', 'u\'tvar0'))

    def _subtest_bitwise_not(self, subc_tmplt: str,
                             pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('~1'),
                pv_tmplt % ('let u\'tvar0: nat = u\'not(1) in\n', 'u\'tvar0'))

    def _subtest_unary_plus(self, subc_tmplt: str,
                            pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('+11'),
                pv_tmplt % ('let u\'tvar0: nat = 0 + 11 in\n', 'u\'tvar0'))

    def _subtest_negation(self, subc_tmplt: str,
                          pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('-3'),
                pv_tmplt % ('let u\'tvar0: nat = 0 - 3 in\n', 'u\'tvar0'))

    def _subtest_dereference(self, subc_tmplt: str,
                             pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('*NULL'),
                pv_tmplt % ('let u\'tvar0: bitstring = u\'deref(NULL) in\n',
                            'u\'tvar0'))

    def _subtest_addressof(self, subc_tmplt: str,
                           pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('&a'),
                pv_tmplt % ('let u\'tvar0: bitstring = u\'addressof(a) in\n',
                            'u\'tvar0'))

    def _subtest_cast(self, subc_tmplt: str, pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('(bool) a'),
                pv_tmplt % ('let u\'tvar0: bool = u\'cast2bool(a) in\n',
                            'u\'tvar0'))

    def _subtest_modulo(self, subc_tmplt: str, pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('a % 2'),
                pv_tmplt % ('let u\'tvar0: nat = u\'mod(a, 2) in\n',
                            'u\'tvar0'))

    def _subtest_division(self, subc_tmplt: str, pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('a / a'),
                pv_tmplt % ('let u\'tvar0: nat = u\'div(a, a) in\n', 'u\'tvar0'))

    def _subtest_multiply(self, subc_tmplt: str, pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('a * a'),
                pv_tmplt % ('let u\'tvar0: nat = u\'mul(a, a) in\n', 'u\'tvar0'))

    def _subtest_subtraction(self, subc_tmplt: str, pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('a - 3'),
                pv_tmplt % ('let u\'tvar0: nat = a - 3 in\n', 'u\'tvar0'))

    def _subtest_addition(self, subc_tmplt: str, pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('42 + a'),
                pv_tmplt % ('let u\'tvar0: nat = 42 + a in\n', 'u\'tvar0'))

    def _subtest_right_shift(self, subc_tmplt: str, pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('a >> 32'),
                pv_tmplt % ('let u\'tvar0: nat = u\'shr(a, 32) in\n', 'u\'tvar0'))

    def _subtest_left_shift(self, subc_tmplt: str, pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('1 << a'),
                pv_tmplt % ('let u\'tvar0: nat = u\'shl(1, a) in\n', 'u\'tvar0'))

    def _subtest_greater_or_equals(self, subc_tmplt: str,
                                   pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('1 >= 0'),
                pv_tmplt % ('let u\'tvar0: bool = 1 >= 0 in\n', 'u\'tvar0'))

    def _subtest_less_or_equals(self, subc_tmplt: str,
                                pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('42 <= a'),
                pv_tmplt % ('let u\'tvar0: bool = 42 <= a in\n', 'u\'tvar0'))

    def _subtest_greater(self, subc_tmplt: str, pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('a > a'),
                pv_tmplt % ('let u\'tvar0: bool = a > a in\n', 'u\'tvar0'))

    def _subtest_less(self, subc_tmplt: str, pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('a < 0'),
                pv_tmplt % ('let u\'tvar0: bool = a < 0 in\n', 'u\'tvar0'))

    def _subtest_not_equal(self, subc_tmplt: str,
                           pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('a != a'),
                pv_tmplt % ('let u\'tvar0: bool = a <> a in\n', 'u\'tvar0'))

    def _subtest_equal(self, subc_tmplt: str, pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('4 == 8'),
                pv_tmplt % ('let u\'tvar0: bool = 4 = 8 in\n', 'u\'tvar0'))

    def _subtest_bitwise_and(self, subc_tmplt: str,
                             pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('a & a'),
                pv_tmplt % ('let u\'tvar0: nat = u\'and(a, a) in\n', 'u\'tvar0'))

    def _subtest_bitwise_xor(self, subc_tmplt: str, pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('0 ^ a'),
                pv_tmplt % ('let u\'tvar0: nat = u\'xor(0, a) in\n', 'u\'tvar0'))

    def _subtest_bitwise_or(self, subc_tmplt: str, pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('8 | 4'),
                pv_tmplt % ('let u\'tvar0: nat = u\'or(8, 4) in\n', 'u\'tvar0'))

    def _subtest_conjuction(self, subc_tmplt: str, pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('1 && 1'),
                pv_tmplt % ('let u\'tvar0: bool = 1 && 1 in\n', 'u\'tvar0'))

    def _subtest_disjunction(self, subc_tmplt: str, pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('0 || 0'),
                pv_tmplt % ('let u\'tvar0: bool = 0 || 0 in\n', 'u\'tvar0'))

    def _subtest_conditional(self, subc_tmplt: str, pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('true ? a : 0'),
                pv_tmplt % ('let u\'tvar0 = u\'ternary(true, a, 0) in\n',
                            'u\'tvar0'))

    def test_expressions_with_integers(self):
        subc_tmplt = 'void foo(int a) { a = %s; }'
        pv_tmplt = 'let foo(a: nat, u\'end: channel) = %slet a = %s in out(u\'end, true).'
        check_subtest_single(self, self._subtest_parenthesis, subc_tmplt, pv_tmplt)
        check_subtest_single(self, self._subtest_post_inc, subc_tmplt, pv_tmplt)
        check_subtest_single(self, self._subtest_post_dec, subc_tmplt, pv_tmplt)
        check_subtest_single(self, self._subtest_nullary_funcall, subc_tmplt, pv_tmplt)
        check_subtest_single(self, self._subtest_unary_funcall, subc_tmplt, pv_tmplt)
        check_subtest_single(self, self._subtest_ternary_funcall, subc_tmplt, pv_tmplt)
        check_subtest_single(self, self._subtest_sizeof, subc_tmplt, pv_tmplt)
        check_subtest_single(self, self._subtest_logic_not, subc_tmplt, pv_tmplt)
        check_subtest_single(self, self._subtest_bitwise_not, subc_tmplt, pv_tmplt)
        check_subtest_single(self, self._subtest_unary_plus, subc_tmplt, pv_tmplt)
        check_subtest_single(self, self._subtest_negation, subc_tmplt, pv_tmplt)
        check_subtest_single(self, self._subtest_dereference, subc_tmplt, pv_tmplt)
        check_subtest_single(self, self._subtest_addressof, subc_tmplt, pv_tmplt)
        check_subtest_single(self, self._subtest_cast, subc_tmplt, pv_tmplt)
        check_subtest_single(self, self._subtest_modulo, subc_tmplt, pv_tmplt)
        check_subtest_single(self, self._subtest_division, subc_tmplt, pv_tmplt)
        check_subtest_single(self, self._subtest_multiply, subc_tmplt, pv_tmplt)
        check_subtest_single(self, self._subtest_subtraction, subc_tmplt, pv_tmplt)
        check_subtest_single(self, self._subtest_addition, subc_tmplt, pv_tmplt)
        check_subtest_single(self, self._subtest_right_shift, subc_tmplt, pv_tmplt)
        check_subtest_single(self, self._subtest_left_shift, subc_tmplt, pv_tmplt)
        check_subtest_single(self, self._subtest_greater_or_equals, subc_tmplt, pv_tmplt)
        check_subtest_single(self, self._subtest_less_or_equals, subc_tmplt, pv_tmplt)
        check_subtest_single(self, self._subtest_greater, subc_tmplt, pv_tmplt)
        check_subtest_single(self, self._subtest_less, subc_tmplt, pv_tmplt)
        check_subtest_single(self, self._subtest_not_equal, subc_tmplt, pv_tmplt)
        check_subtest_single(self, self._subtest_equal, subc_tmplt, pv_tmplt)
        check_subtest_single(self, self._subtest_bitwise_and, subc_tmplt, pv_tmplt)
        check_subtest_single(self, self._subtest_bitwise_or, subc_tmplt, pv_tmplt)
        check_subtest_single(self, self._subtest_bitwise_xor, subc_tmplt, pv_tmplt)
        check_subtest_single(self, self._subtest_disjunction, subc_tmplt, pv_tmplt)
        check_subtest_single(self, self._subtest_conjuction, subc_tmplt, pv_tmplt)
        check_subtest_single(self, self._subtest_conditional, subc_tmplt, pv_tmplt)
