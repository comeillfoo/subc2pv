#!/usr/bin/env python3
import unittest

from translator import Translator


class TranslatorBasicTestCase(unittest.TestCase):
    def test_empty_stream(self):
        model = Translator.from_line('', False).translate()
        self.assertTrue(not model.functions, 'No functions should be parsed')
        self.assertTrue(not model.preamble, 'No preamble should be generated')

    def test_empty_stream_with_helpers(self):
        model = Translator.from_line('').translate()
        self.assertTrue(not model.functions, 'No functions should be parsed')
        self.assertEqual(model.preamble, '\n'.join(Translator.AUXILARY_GLOBALS))
