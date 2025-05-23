#!/usr/bin/env python3
import unittest
import pathlib
from typing import Tuple

from translator import Translator

class TranslatorTestCases(unittest.TestCase):
    IDENTIFIERS = [ 'T', 'asdfadsfsdf', '____', 'Mtypes', '_', 'A', 'asdfkljdsfn',
        '_tmp8', 'message', 'client', 'server', 'ASF', 'Q', 'WFD2', 'x', 'port',
        'addr', 'field', 'PP9', '__qwerty__' ]

    TESTS_TYPES = {
        '_Bool': 'bool',
        'bool': 'bool',
        'char': 'nat',
        'short': 'nat',
        'int': 'nat',
        'long': 'nat',
        'long long': 'nat',
        '__m128': 'nat',
        '__m128d': 'nat',
        '__m128i': 'nat',
        'enum _Enum': '_Enum',
        'struct _Struct': '_Struct',
        'union _Union': '_Union',
        'void*': 'bitstring',
        'const long*': 'bitstring',
        'int const*': 'bitstring',
        '_Bool***********************': 'bitstring',
        'enum _Enum* restrict': 'bitstring',
        'const short * const': 'bitstring',
        'struct _Struct const * const': 'bitstring',
    }

    def test_empty_stream(self):
        model = Translator.from_line('', False).translate()
        self.assertTrue(not model.functions, 'No functions should be parsed')
        self.assertTrue(not model.preamble, 'No preamble should be generated')

    def test_empty_stream_with_helpers(self):
        model = Translator.from_line('').translate()
        self.assertTrue(not model.functions, 'No functions should be parsed')
        self.assertEqual(model.preamble, '\n'.join(Translator.AUXILARY_GLOBALS))

    def _enum_declaration_subtest(self, name: str):
        model = Translator.from_line(f'enum {name};', False).translate()
        self.assertTrue(not model.functions, 'No functions should be parsed')
        self.assertEqual(model.preamble, f'type {name}.\n')

    def test_enum_declaration(self):
        for name in self.IDENTIFIERS:
            with self.subTest(name):
                self._enum_declaration_subtest(name)

    def _enum_definition_subtest(self, name: str, consts: list[Tuple[str, str]]):
        lines = [f'enum {name}', '{']
        expected = [f'type {name}.']
        for ec_name, ec_value in consts:
            if ec_value != '':
                ec_value = f' = {ec_value}'
            lines.append(f'\t{ec_name}{ec_value},')
            expected.append(f'const {ec_name}: {name}.')
        lines.append('};')
        expected.append('\n')

        model = Translator.from_lines(lines, False).translate()
        self.assertTrue(not model.functions)
        self.assertEqual(model.preamble, '\n'.join(expected))

    def test_enum_definition(self):
        const_sets = [
            [ ('A', ''), ('b', ''), ('C', '') ],
            [ ('adsff', '42'), ('aslkdnf', '')],
            [ ('__', '0xDEADBEEF') ],
            [ ('SEND', ''), ('RECV', '0b101'), ('ACK', ''), ('NACK', '0777') ]
        ]
        for name in self.IDENTIFIERS:
            for consts in const_sets:
                with self.subTest(f'{name}: {consts}'):
                    self._enum_definition_subtest(name, consts)

    def _fielded_declaration_subtest(self, name: str, ttype: str):
        model = Translator.from_line(f'{ttype} {name};', False).translate()
        self.assertTrue(not model.functions)
        self.assertEqual(model.preamble, f'type {name}.\n')

    def _dict2fielded_def(self, name: str, fields: Tuple[str, str] = [],
                          ttype: str = 'struct') -> str:
        lines = [f'{ttype} {name}', '{']
        for fname, ftype in fields:
            lines.append(f'{ftype} {fname};')
        lines.append('};')
        return '\n'.join(lines)

    def _fielded_empty_definition_subtest(self, name: str, ttype: str):
        model = Translator.from_line(
            self._dict2fielded_def(name, ttype=ttype), False).translate()
        self.assertTrue(not model.functions)
        expected = '\n'.join([f'type {name}.', '',
                                f'fun _{name}_init(): {name}.'])
        self.assertEqual(model.preamble, expected)

    def _fielded_with_single_enum_subtest(self, name: str, ttype: str):
        model = Translator.from_line(
            self._dict2fielded_def(name, [('x', 'enum A')], ttype),
            False).translate()
        self.assertTrue(not model.functions)
        expected = '\n'.join([
            f'type {name}.', '', f'fun _{name}_get_x(self: {name}): A.',
            f'fun _{name}_set_x(self: {name}, x: A): {name}.',
            f'fun _{name}_init(x: A): {name}.'])
        self.assertEqual(model.preamble, expected)

    def _fielded_single_integer_helper(self, name: str, ttype: str, fname: str,
                                       ftype: str):
        fielded_definition = self._dict2fielded_def(name, [(fname, ftype)], ttype)
        translator = Translator.from_line(fielded_definition, False)
        model = translator.translate()
        self.assertTrue(not model.functions)
        expected = '\n'.join([
            f'type {name}.', '', f'fun _{name}_get_{fname}(self: {name}): nat.',
            f'fun _{name}_set_{fname}(self: {name}, {fname}: nat): {name}.',
            f'fun _{name}_init({fname}: nat): {name}.'])
        self.assertEqual(model.preamble, expected)

    def _fielded_single_integer_subtest(self, name: str, ttype: str):
        ftypes = ['char', 'short', 'int', 'long', '__m128', '__m128d', '__m128i']
        for fname in self.IDENTIFIERS:
            for ftype in ftypes:
                self._fielded_single_integer_helper(name, ttype, fname, ftype)

    def _fielded_single_bool_subtest(self, name: str, ttype: str):
        for fname in self.IDENTIFIERS:
            fielded_definition = self._dict2fielded_def(name, [(fname, '_Bool')],
                                                        ttype)
            model = Translator.from_line(fielded_definition, False).translate()
            self.assertTrue(not model.functions)
            expected = '\n'.join([
                f'type {name}.', '', f'fun _{name}_get_{fname}(self: {name}): bool.',
                f'fun _{name}_set_{fname}(self: {name}, {fname}: bool): {name}.',
                f'fun _{name}_init({fname}: bool): {name}.'])
            self.assertEqual(model.preamble, expected)

    def test_fielded(self):
        def at_subtest(name: str, ttype: str, subtest: str, fun):
            with self.subTest(f'{subtest}:{ttype}:{name}'):
                fun(name, ttype)
        for ttype in ('struct', 'union'):
            for name in self.IDENTIFIERS:
                at_subtest(name, ttype, 'declaration',
                           self._fielded_declaration_subtest)
                at_subtest(name, ttype, 'empty-definition',
                           self._fielded_empty_definition_subtest)
                at_subtest(name, ttype, 'single-enum-definition',
                           self._fielded_with_single_enum_subtest)
                at_subtest(name, ttype, 'single-integer-definition',
                           self._fielded_single_integer_subtest)
                at_subtest(name, ttype, 'single-bool-definition',
                           self._fielded_single_bool_subtest)

    def _function_declare_void_0_arity(self, name: str, use_void: bool = False):
        source = f'static _Noreturn inline void {name}({"void" if use_void else ""});'
        model = Translator.from_line(source, False).translate()
        self.assertTrue(not model.preamble)
        self.assertEqual((name, f'let {name}() = 0.'), model.functions[0])

    def _function_declare_nonvoid_0_arity(self, name: str, use_void: bool = False):
        tmplt = 'extern __stdcall __inline__ {} %s(%s);' \
            % (name, 'void' if use_void else '')
        for rtype, pvtype in self.TESTS_TYPES.items():
            model = Translator.from_line(tmplt.format(rtype), False).translate()
            self.assertTrue(not model.preamble)
            self.assertEqual((name, f'fun {name}(): {pvtype}.'),
                             model.functions[0])

    def _function_0_arity_declarations_subtest(self, name: str):
        for use_void in (False, True):
            self._function_declare_void_0_arity(name, use_void)
            self._function_declare_nonvoid_0_arity(name, use_void)

    def _function_declare_void_1_arity(self, name: str, anon: bool):
        tmplt = 'void {}({});'
        for ptype, pvtype in self.TESTS_TYPES.items():
            param_name = 'p0' if anon else f'arg_{name}'
            param = ptype + ('' if anon else f' {param_name}')
            model = Translator.from_line(tmplt.format(name, param),
                                         False).translate()
            self.assertTrue(not model.preamble)
            self.assertEqual((name, f'let {name}({param_name}: {pvtype}) = 0.'),
                             model.functions[0])

    def _function_declare_nonvoid_1_arity(self, name: str, anon: bool):
        tmplt = 'static {} %s({});' % (name)
        pname = 'p0' if anon else f'arg_{name}'
        def _test_single(rtype: str, rpvtype: str, ptype: str, ppvtype: str):
            param = ptype + ('' if anon else f' {pname}')
            model = Translator.from_line(tmplt.format(rtype, param),
                                         False).translate()
            self.assertTrue(not model.preamble)
            self.assertEqual((name, f'fun {name}({pname}: {ppvtype}): {rpvtype}.'),
                             model.functions[0])
        for rtype, rpvtype in self.TESTS_TYPES.items():
            for ptype, ppvtype in self.TESTS_TYPES.items():
                _test_single(rtype, rpvtype, ptype, ppvtype)

    def _function_1_arity_declarations_subtest(self, name: str):
        for anon in (False, True):
            self._function_declare_void_1_arity(name, anon)
            self._function_declare_nonvoid_1_arity(name, anon)

    def test_single_function_declaration(self):
        def at_subtest(name: str, subtest: str, fun):
            with self.subTest(f'{subtest}:{name}'):
                fun(name)
        for name in self.IDENTIFIERS:
            at_subtest(name, 'function-0_arity-declaration',
                       self._function_0_arity_declarations_subtest)
            at_subtest(name, 'function-1_arity-declaration',
                       self._function_1_arity_declarations_subtest)


    def _function_define_empty_void_0_arity(self, name: str, use_void: bool = False):
        source = '_Noreturn void %s(%s) { }' % (name, 'void' if use_void else '')
        model = Translator.from_line(source, False).translate()
        self.assertTrue(not model.preamble)
        self.assertEqual((name, f'let {name}() = 0.'), model.functions[0])

    def _function_define_empty_nonvoid_0_arity(self, name: str, use_void: bool = False):
        for rtype, _ in self.TESTS_TYPES.items():
            tmplt = '__stdcall %s %s(%s) { }' % (rtype, name,
                                                 'void' if use_void else '')
            model = Translator.from_line(tmplt, False).translate()
            self.assertTrue(not model.preamble)
            self.assertEqual((name, f'let {name}(_ret_ch: channel) = 0.'),
                             model.functions[0])

    def _function_0_arity_definitions_empty_subtest(self, name: str):
        for use_void in (False, True):
            self._function_define_empty_void_0_arity(name, use_void)
            self._function_define_empty_nonvoid_0_arity(name, use_void)

    def _function_variable_no_init_subtest(self, name: str):
        source = 'void %s() { int a; }' % (name)
        model = Translator.from_line(source, False).translate()
        self.assertTrue(not model.preamble)
        self.assertEqual((name, f'let {name}() = new a: nat.'),
                         model.functions[0])

    def _function_variable_primitive_init_subtest(self, name: str):
        for ttype, pvtype in self.TESTS_TYPES.items():
            source = 'void %s(%s a) { %s b = a; }' % (name, ttype, ttype)
            model = Translator.from_line(source, False).translate()
            self.assertTrue(not model.preamble)
            expected = f'let {name}(a: {pvtype}) = new b: {pvtype}.'
            self.assertEqual((name, expected), model.functions[0])

    def _function_variable_assign_to_constant_subtest(self, name: str):
        source = 'void %s() { int a; a = 42; }' % (name)
        model = Translator.from_line(source, False).translate()
        self.assertTrue(not model.preamble)
        expected = f'let {name}() = new a: nat;\nlet a = 42 in 0.'
        self.assertEqual((name, expected), model.functions[0])

    def _function_variable_assign_to_identifier_subtest(self, name: str):
        for ttype, pvtype in self.TESTS_TYPES.items():
            source = 'void %s(%s a) { %s b; b = a; }' % (name, ttype, ttype)
            model = Translator.from_line(source, False).translate()
            self.assertTrue(not model.preamble)
            expected = f'let {name}(a: {pvtype}) = new b: {pvtype};\nlet b = a in 0.'
            self.assertEqual((name, expected), model.functions[0])

    def _function_variable_assign_to_strings_subtest(self, name: str):
        strings_cases = [
            [''],
            ['', ''],
            ['A', 'B'],
            ['alsdf'],
            ['__', '---', 'lorem ipsum']
        ]
        for strings_case in strings_cases:
            joined = ''.join(strings_case)
            unique = set([*strings_case, joined])
            _id = len(unique) - 1
            expr = ''.join(map(lambda s: f'"{s}"', strings_case))
            source = 'void %s() { char *a; a = %s; }' % (name, expr)
            model = Translator.from_line(source, False).translate()
            expected = f'let {name}() = new a: bitstring;\nlet a = _strlit{_id} in 0.'
            self.assertEqual((name, expected), model.functions[0],
                             f'functions differs with {strings_case}')

    def test_single_function_definition(self):
        def at_subtest(name: str, subtest: str, fun):
            with self.subTest(f'{subtest}:{name}'):
                fun(name)
        for name in self.IDENTIFIERS:
            at_subtest(name, 'function-0_arity_definitions-empty',
                       self._function_0_arity_definitions_empty_subtest)
            at_subtest(name, 'function-variable-declaration-no-init-value',
                       self._function_variable_no_init_subtest)
            at_subtest(name, 'function-variable-primitive-init-value',
                       self._function_variable_primitive_init_subtest)
            at_subtest(name, 'function-variable-assign-to-constant',
                       self._function_variable_assign_to_constant_subtest)
            at_subtest(name, 'function-variable-assign-to-identifier',
                       self._function_variable_assign_to_identifier_subtest)
            at_subtest(name, 'function-variable-assign-to-strings',
                       self._function_variable_assign_to_strings_subtest)

    def _expression_parenthesis_subtest(self, subc_tmplt: str,
                                        pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('(42)'), pv_tmplt % ('', '42'))

    def _expression_post_inc_subtest(self, subc_tmplt: str,
                                     pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('6++'),
                pv_tmplt % ('let _tmpvar0: nat = 6 + 1 in \n', '_tmpvar0'))

    def _expression_post_dec_subtest(self, subc_tmplt: str,
                                     pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('42--'),
                pv_tmplt % ('let _tmpvar0: nat = 42 - 1 in \n', '_tmpvar0'))

    def _expression_no_args_funcall_subtest(self, subc_tmplt: str,
                                                  pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('baz()'),
                pv_tmplt % ('let _tmpvar0 = baz() in \n', '_tmpvar0'))

    def _expression_single_arg_funcall_subtest(self, subc_tmplt: str,
                                               pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('baz(42)'),
                pv_tmplt % ('let _tmpvar0 = baz(42) in \n', '_tmpvar0'))

    def _expression_sizeof_subtest(self, subc_tmplt: str,
                                   pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('sizeof(a)'),
                pv_tmplt % ('let _tmpvar0: nat = _sizeof(a) in \n', '_tmpvar0'))

    def _expression_logic_not_subtest(self, subc_tmplt: str,
                                      pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('!0'),
                pv_tmplt % ('let _tmpvar0: bool = not(0) in \n', '_tmpvar0'))

    def _expression_bitwise_not_subtest(self, subc_tmplt: str,
                                        pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('~1'),
                pv_tmplt % ('let _tmpvar0: nat = _not(1) in \n', '_tmpvar0'))

    def _expression_unary_plus_subtest(self, subc_tmplt: str,
                                       pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('+11'),
                pv_tmplt % ('let _tmpvar0: nat = 0 + 11 in \n', '_tmpvar0'))

    def _expression_negation_subtest(self, subc_tmplt: str,
                                     pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('-3'),
                pv_tmplt % ('let _tmpvar0: nat = 0 - 3 in \n', '_tmpvar0'))

    def _expression_dereference_subtest(self, subc_tmplt: str,
                                        pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('*NULL'),
                pv_tmplt % ('let _tmpvar0: bitstring = _deref(NULL) in \n',
                            '_tmpvar0'))

    def _expression_addressof_subtest(self, subc_tmplt: str,
                                      pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('&a'),
                pv_tmplt % ('let _tmpvar0: bitstring = _addressof(a) in \n',
                            '_tmpvar0'))

    def _expression_cast_subtest(self, subc_tmplt: str,
                                pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('(bool) a'),
                pv_tmplt % ('let _tmpvar0: bool = _cast2bool(a) in \n',
                            '_tmpvar0'))

    def _expression_modulo_subtest(self, subc_tmplt: str,
                                   pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('a % 2'),
                pv_tmplt % ('let _tmpvar0: nat = _mod(a, 2) in \n',
                            '_tmpvar0'))

    def _expression_division_subtest(self, subc_tmplt: str,
                                     pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('a / a'),
                pv_tmplt % ('let _tmpvar0: nat = _div(a, a) in \n', '_tmpvar0'))

    def _expression_multiply_subtest(self, subc_tmplt: str,
                                     pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('a * a'),
                pv_tmplt % ('let _tmpvar0: nat = _mul(a, a) in \n', '_tmpvar0'))

    def _expression_subtraction_subtest(self, subc_tmplt: str,
                                        pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('a - 3'),
                pv_tmplt % ('let _tmpvar0: nat = a - 3 in \n', '_tmpvar0'))

    def _expression_addition_subtest(self, subc_tmplt: str,
                                     pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('42 + a'),
                pv_tmplt % ('let _tmpvar0: nat = 42 + a in \n', '_tmpvar0'))

    def _expression_right_shift_subtest(self, subc_tmplt: str,
                                        pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('a >> 32'),
                pv_tmplt % ('let _tmpvar0: nat = _shr(a, 32) in \n', '_tmpvar0'))

    def _expression_left_shift_subtest(self, subc_tmplt: str,
                                       pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('1 << a'),
                pv_tmplt % ('let _tmpvar0: nat = _shl(1, a) in \n', '_tmpvar0'))

    def _expression_greater_or_equals_subtest(self, subc_tmplt: str,
                                              pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('1 >= 0'),
                pv_tmplt % ('let _tmpvar0: bool = 1 >= 0 in \n', '_tmpvar0'))

    def _expression_less_or_equals_subtest(self, subc_tmplt: str,
                                           pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('42 <= a'),
                pv_tmplt % ('let _tmpvar0: bool = 42 <= a in \n', '_tmpvar0'))

    def _expression_greater_subtest(self, subc_tmplt: str,
                                    pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('a > a'),
                pv_tmplt % ('let _tmpvar0: bool = a > a in \n', '_tmpvar0'))

    def _expression_less_subtest(self, subc_tmplt: str,
                                 pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('a < 0'),
                pv_tmplt % ('let _tmpvar0: bool = a < 0 in \n', '_tmpvar0'))

    def _expression_unequal_subtest(self, subc_tmplt: str,
                                    pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('a != a'),
                pv_tmplt % ('let _tmpvar0: bool = a <> a in \n', '_tmpvar0'))

    def _expression_equal_subtest(self, subc_tmplt: str,
                                  pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('4 == 8'),
                pv_tmplt % ('let _tmpvar0: bool = 4 = 8 in \n', '_tmpvar0'))

    def _expression_bitwise_and_subtest(self, subc_tmplt: str,
                                        pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('a & a'),
                pv_tmplt % ('let _tmpvar0: nat = _and(a, a) in \n', '_tmpvar0'))

    def _expression_bitwise_xor_subtest(self, subc_tmplt: str,
                                        pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('0 ^ a'),
                pv_tmplt % ('let _tmpvar0: nat = _xor(0, a) in \n', '_tmpvar0'))

    def _expression_bitwise_or_subtest(self, subc_tmplt: str,
                                       pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('8 | 4'),
                pv_tmplt % ('let _tmpvar0: nat = _or(8, 4) in \n', '_tmpvar0'))

    def _expression_conjuction_subtest(self, subc_tmplt: str,
                                       pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('1 && 1'),
                pv_tmplt % ('let _tmpvar0: bool = 1 && 1 in \n', '_tmpvar0'))

    def _expression_disjunction_subtest(self, subc_tmplt: str,
                                        pv_tmplt: str) -> Tuple[str, str]:
        return (subc_tmplt % ('0 || 0'),
                pv_tmplt % ('let _tmpvar0: bool = 0 || 0 in \n', '_tmpvar0'))

    def test_expressions_with_integers(self):
        subc_tmplt = 'void foo(int a) { a = %s; }'
        pv_tmplt = 'let foo(a: nat) = %slet a = %s in 0.'
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


from lut import LookUpTable

class LUTTestCases(unittest.TestCase):
    def _assert_empty_lut(self, lut: LookUpTable):
        self.assertIsNone(lut.file(), 'No path should be processed')
        self.assertEqual(lut.extracts(), set(), 'No functions should be extracted')
        self.assertEqual(lut.substitutes(), {}, 'No defines should be substituted')
        self.assertEqual(lut.paste(), '', 'No text should be pasted at the end')

    def test_nolines(self):
        self._assert_empty_lut(LookUpTable.from_lines([]))

    def test_gibberish(self):
        no_directives = [
            ['asdfsfdsfds'],
            ['asdfdf', '1234498324034', '!@#$%^&*'],
            ['@#RTGVRUI', '@#$176234ksdn', 'vbiwnf34792472', 'bvsdc23864892'],
        ]
        for no_directive in no_directives:
            self._assert_empty_lut(LookUpTable.from_lines(no_directive))

    def test_single_file(self):
        paths = [
            'main.c',
            'a.c',
            'a/b/c/d/proto.c',
            '/tmp/______/_some.c'
        ]
        templates = [
            '%F {}',
            '%F\t{}',
            '%F  \t{}',
            '%F {} asdasdf\t\tvknjdf___',
        ]
        for template in templates:
            for path in paths:
                lut = LookUpTable.from_line(template.format(path))
                self.assertEqual(lut.file(), pathlib.Path(path))

    def test_multiple_files(self):
        files = list(map(lambda x: f'{x}.c', range(3)))
        cases = [
            ('%F {}\n%F {}', 1),
            ('%F {}\n____\n%F {}', 1),
            ('%F {}\n____\n%F {}\n%F {} adsfdsf', 2),
            ('%F {}\n____\n%F {}\n%F {}\nasdfdf', 2),
            ('%F {}\n____\n%F {}\nasdfdsf\n%F {}', 2),
        ]
        for template, i in cases:
            lut = LookUpTable.from_line(template.format(*files))
            self.assertEqual(lut.file(), pathlib.Path(files[i]))

    def test_single_extract(self):
        functions = [ 'client', 'server', 'sendreceive', 'readwrite', 'syscall',
            'http_get', 'http_post']
        templates = [
            '%X {}',
            '%X\t{}',
            '%X  \t{}',
            '%X {} asdasdf\t\tvknjdf___',
        ]
        for template in templates:
            for function in functions:
                lut = LookUpTable.from_line(template.format(function))
                self.assertEqual(lut.extracts(), set([function]))

    def test_single_substitution(self):
        substitutions = ['fun main(argc: nat, argv: bitstring): nat.',
                         'aldsnfdlskfn', '___________', 'fun a(): bool.']
        templates = [
            '%S main {}',
            '%S\tmain\t{}',
            '%S  main\t{}',
            '%S main    {}',
        ]
        for template in templates:
            for substitution in substitutions:
                lut = LookUpTable.from_line(template.format(substitution))
                self.assertEqual(lut.substitute('main'), substitution)

    def test_single_paste(self):
        template = '%P\n{}\n%%'
        cases = [
            'process fail',
            'process 0',
            'aldfnkdsnfdnsfndskf',
            '\n\n\n\n\n\nn\n\n\n',
            'process main()',
            '''type a.
const A: a.
const B: a.
type b.

free c: channel [private].

process
    0''']
        for case in cases:
            lut = LookUpTable.from_line(template.format(case))
            self.assertEqual(lut.paste(), case)


if __name__ == '__main__':
    unittest.main()
