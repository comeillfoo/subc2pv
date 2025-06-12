import unittest
from typing import Tuple

from translator import Translator


class ExpressionsTestCase(unittest.TestCase):
    def _expression_parenthesis_subtest(self, subc_tmplt: str,
                                        pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('(42)'), pv_tmplt % ('', '42'))

    def _expression_post_inc_subtest(self, subc_tmplt: str,
                                     pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('6++'),
                pv_tmplt % ('let _tvar0: nat = 6 + 1 in \n', '_tvar0'))

    def _expression_post_dec_subtest(self, subc_tmplt: str,
                                     pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('42--'),
                pv_tmplt % ('let _tvar0: nat = 42 - 1 in \n', '_tvar0'))

    def _expression_no_args_funcall_subtest(self, subc_tmplt: str,
                                                  pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('baz()'),
                pv_tmplt % ('let _tvar0 = baz() in \n', '_tvar0'))

    def _expression_single_arg_funcall_subtest(self, subc_tmplt: str,
                                               pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('baz(42)'),
                pv_tmplt % ('let _tvar0 = baz(42) in \n', '_tvar0'))

    def _expression_multi_args_funcall_subtest(self, subc_tmplt: str,
                                               pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('foo(42, true, "text")'),
                pv_tmplt % ('let _tvar0 = foo(42, true, _strlit0) in \n',
                            '_tvar0'))

    def _expression_sizeof_subtest(self, subc_tmplt: str,
                                   pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('sizeof(a)'),
                pv_tmplt % ('let _tvar0: nat = _sizeof(a) in \n', '_tvar0'))

    def _expression_logic_not_subtest(self, subc_tmplt: str,
                                      pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('!0'),
                pv_tmplt % ('let _tvar0: bool = not(0) in \n', '_tvar0'))

    def _expression_bitwise_not_subtest(self, subc_tmplt: str,
                                        pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('~1'),
                pv_tmplt % ('let _tvar0: nat = _not(1) in \n', '_tvar0'))

    def _expression_unary_plus_subtest(self, subc_tmplt: str,
                                       pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('+11'),
                pv_tmplt % ('let _tvar0: nat = 0 + 11 in \n', '_tvar0'))

    def _expression_negation_subtest(self, subc_tmplt: str,
                                     pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('-3'),
                pv_tmplt % ('let _tvar0: nat = 0 - 3 in \n', '_tvar0'))

    def _expression_dereference_subtest(self, subc_tmplt: str,
                                        pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('*NULL'),
                pv_tmplt % ('let _tvar0: bitstring = _deref(NULL) in \n',
                            '_tvar0'))

    def _expression_addressof_subtest(self, subc_tmplt: str,
                                      pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('&a'),
                pv_tmplt % ('let _tvar0: bitstring = _addressof(a) in \n',
                            '_tvar0'))

    def _expression_cast_subtest(self, subc_tmplt: str,
                                pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('(bool) a'),
                pv_tmplt % ('let _tvar0: bool = _cast2bool(a) in \n',
                            '_tvar0'))

    def _expression_modulo_subtest(self, subc_tmplt: str,
                                   pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('a % 2'),
                pv_tmplt % ('let _tvar0: nat = _mod(a, 2) in \n',
                            '_tvar0'))

    def _expression_division_subtest(self, subc_tmplt: str,
                                     pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('a / a'),
                pv_tmplt % ('let _tvar0: nat = _div(a, a) in \n', '_tvar0'))

    def _expression_multiply_subtest(self, subc_tmplt: str,
                                     pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('a * a'),
                pv_tmplt % ('let _tvar0: nat = _mul(a, a) in \n', '_tvar0'))

    def _expression_subtraction_subtest(self, subc_tmplt: str,
                                        pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('a - 3'),
                pv_tmplt % ('let _tvar0: nat = a - 3 in \n', '_tvar0'))

    def _expression_addition_subtest(self, subc_tmplt: str,
                                     pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('42 + a'),
                pv_tmplt % ('let _tvar0: nat = 42 + a in \n', '_tvar0'))

    def _expression_right_shift_subtest(self, subc_tmplt: str,
                                        pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('a >> 32'),
                pv_tmplt % ('let _tvar0: nat = _shr(a, 32) in \n', '_tvar0'))

    def _expression_left_shift_subtest(self, subc_tmplt: str,
                                       pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('1 << a'),
                pv_tmplt % ('let _tvar0: nat = _shl(1, a) in \n', '_tvar0'))

    def _expression_greater_or_equals_subtest(self, subc_tmplt: str,
                                              pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('1 >= 0'),
                pv_tmplt % ('let _tvar0: bool = 1 >= 0 in \n', '_tvar0'))

    def _expression_less_or_equals_subtest(self, subc_tmplt: str,
                                           pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('42 <= a'),
                pv_tmplt % ('let _tvar0: bool = 42 <= a in \n', '_tvar0'))

    def _expression_greater_subtest(self, subc_tmplt: str,
                                    pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('a > a'),
                pv_tmplt % ('let _tvar0: bool = a > a in \n', '_tvar0'))

    def _expression_less_subtest(self, subc_tmplt: str,
                                 pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('a < 0'),
                pv_tmplt % ('let _tvar0: bool = a < 0 in \n', '_tvar0'))

    def _expression_unequal_subtest(self, subc_tmplt: str,
                                    pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('a != a'),
                pv_tmplt % ('let _tvar0: bool = a <> a in \n', '_tvar0'))

    def _expression_equal_subtest(self, subc_tmplt: str,
                                  pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('4 == 8'),
                pv_tmplt % ('let _tvar0: bool = 4 = 8 in \n', '_tvar0'))

    def _expression_bitwise_and_subtest(self, subc_tmplt: str,
                                        pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('a & a'),
                pv_tmplt % ('let _tvar0: nat = _and(a, a) in \n', '_tvar0'))

    def _expression_bitwise_xor_subtest(self, subc_tmplt: str,
                                        pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('0 ^ a'),
                pv_tmplt % ('let _tvar0: nat = _xor(0, a) in \n', '_tvar0'))

    def _expression_bitwise_or_subtest(self, subc_tmplt: str,
                                       pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('8 | 4'),
                pv_tmplt % ('let _tvar0: nat = _or(8, 4) in \n', '_tvar0'))

    def _expression_conjuction_subtest(self, subc_tmplt: str,
                                       pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('1 && 1'),
                pv_tmplt % ('let _tvar0: bool = 1 && 1 in \n', '_tvar0'))

    def _expression_disjunction_subtest(self, subc_tmplt: str,
                                        pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('0 || 0'),
                pv_tmplt % ('let _tvar0: bool = 0 || 0 in \n', '_tvar0'))

    def _expression_conditional_subtest(self, subc_tmplt: str,
                                        pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('true ? a : 0'),
                pv_tmplt % ('let _tvar0 = _ternary(true, a, 0) in \n',
                            '_tvar0'))

    def test_expressions_with_integers(self):
        subc_tmplt = 'void foo(int a) { a = %s; }'
        pv_tmplt = 'let foo(a: nat, _end: channel) = %slet a = %s in out(_end, true).'
        def at_subtest(subtest: str, fun):
            with self.subTest(subtest):
                subc_src, pv_src = fun(subc_tmplt, pv_tmplt)
                model = Translator.from_line(subc_src, False).translate()
                self.assertEqual(('foo', pv_src), model.functions[0])
        at_subtest('parenthesis-expression', self._expression_parenthesis_subtest)
        at_subtest('post-increment-expression', self._expression_post_inc_subtest)
        at_subtest('post-decrement-expression', self._expression_post_dec_subtest)
        at_subtest('no-args-funcall-expression',
                   self._expression_no_args_funcall_subtest)
        at_subtest('single-arg-funcall-expression',
                   self._expression_single_arg_funcall_subtest)
        at_subtest('multi-args-funcall-expression',
                   self._expression_multi_args_funcall_subtest)
        at_subtest('sizeof-expression', self._expression_sizeof_subtest)
        at_subtest('logical-not-expression', self._expression_logic_not_subtest)
        at_subtest('bitwise-not-expression',
                   self._expression_bitwise_not_subtest)
        at_subtest('unary-plus-expression', self._expression_unary_plus_subtest)
        at_subtest('negation-expression', self._expression_negation_subtest)
        at_subtest('dereference-expression',
                   self._expression_dereference_subtest)
        at_subtest('addressof-expression', self._expression_addressof_subtest)
        at_subtest('cast-expression', self._expression_cast_subtest)
        at_subtest('modulo-expression', self._expression_modulo_subtest)
        at_subtest('division-expression', self._expression_division_subtest)
        at_subtest('multiply-expression', self._expression_multiply_subtest)
        at_subtest('subtraction-expression',
                   self._expression_subtraction_subtest)
        at_subtest('addition-expression', self._expression_addition_subtest)
        at_subtest('right-shift-expression', self._expression_right_shift_subtest)
        at_subtest('left-shift-expression', self._expression_left_shift_subtest)
        at_subtest('greater-or-equals-expression',
                   self._expression_greater_or_equals_subtest)
        at_subtest('less-or-equals-expression',
                   self._expression_less_or_equals_subtest)
        at_subtest('greater-than-expression', self._expression_greater_subtest)
        at_subtest('less-than-expression', self._expression_less_subtest)
        at_subtest('unequal-expression', self._expression_unequal_subtest)
        at_subtest('equal-expression', self._expression_equal_subtest)
        at_subtest('bitwise-and-expression', self._expression_bitwise_and_subtest)
        at_subtest('bitwise-or-expression', self._expression_bitwise_or_subtest)
        at_subtest('bitwise-xor-expression', self._expression_bitwise_xor_subtest)
        at_subtest('disjunction-expression', self._expression_disjunction_subtest)
        at_subtest('conjunction-expression', self._expression_conjuction_subtest)
        at_subtest('conditional-expression', self._expression_conditional_subtest)
