#!/usr/bin/env python3
from typing import Callable
import unittest

from translator import Translator


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

SOME_IDENTIFIER = 's0m4__1DENT'


def at_subtest(test: unittest.TestCase, func: Callable, *args):
    with test.subTest(func.__name__):
        func(*args)


def check_subtest_single(test: unittest.TestCase, func: Callable, *args):
    with test.subTest(func.__name__):
        source, expected = func(*args)
        model = Translator.from_line(source, False).translate()
        _, actual = model.functions[0]
        test.maxDiff = None
        test.assertEqual(expected, actual)


def check_subtests(test: unittest.TestCase, func: Callable, *args):
    with test.subTest(func.__name__):
        for source, expected in func(*args):
            model = Translator.from_line(source, False).translate()
            _, actual = model.functions[0]
            test.maxDiff = None
            test.assertEqual(expected, actual)
