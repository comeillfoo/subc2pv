#!/usr/bin/env python3
from typing import Callable
import unittest

from model import Model
from translator import Translator


class TranslatorCommonTestCase(unittest.TestCase):
    def setUp(self):
        self._stress_identifiers = [ 'T', 'asdfadsfsdf', '____', 'Mtypes', '_',
            'A', 'asdfkljdsfn', '_tmp8', 'message', 'client', 'server', 'ASF',
            'Q', 'WFD2', 'x', 'port', 'addr', 'field', 'PP9', '__qwerty__' ]
        self._stress_test_identifier = 's0m4__1DENT'
        self._types_table = {
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
        self._array_specifiers = ['', '[]', '[][]', '[6]', '[42][]', '[SIZE]']
        return super().setUp()

    def at_subtest(self, subtest: Callable, *args):
        with self.subTest(subtest.__name__):
            subtest(*args)

    def check_subtest_single(self, checker: Callable, subtest: Callable, *args):
        with self.subTest(subtest.__name__):
            source, expected = subtest(*args)
            model = Translator.from_line(source, False).translate()
            self.maxDiff = None
            checker(expected, model)

    def assert_single_function(self, expected: str, model: Model):
        _, actual = model.functions[0]
        self.assertEqual(expected, actual)

    def check_single_function_subtest(self, subtest: Callable, *args):
        self.check_subtest_single(self.assert_single_function, subtest, *args)

    def assert_preamble(self, expected: str, model: Model):
        self.assertTrue(not model.functions)
        self.assertEqual(expected, model.preamble)

    def check_preamble_subtest(self, subtest: Callable, *args):
        self.check_subtest_single(self.assert_preamble, subtest, *args)

    def check_subtests(self, checker: Callable, subtest: Callable, *args):
        with self.subTest(subtest.__name__):
            for source, expected in subtest(*args):
                model = Translator.from_line(source, False).translate()
                checker(expected, model)

    def check_single_function_subtests(self, subtest: Callable, *args):
        self.check_subtests(self.assert_single_function, subtest, *args)

    def check_preamble_subtests(self, subtest: Callable, *args):
        self.check_subtests(self.assert_preamble, subtest, *args)
