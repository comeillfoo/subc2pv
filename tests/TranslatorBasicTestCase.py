#!/usr/bin/env python3
from typing import Tuple

from translator import Translator
from auxilaries.globals import GLOBALS
from tests.TranslatorCommonTestCase import TranslatorCommonTestCase


class TranslatorBasicTestCase(TranslatorCommonTestCase):
    def _subtest_empty_stream(self) -> Tuple[str, str]:
        return '', ''

    def _subtest_empty_stream_with_helpers(self):
        model = Translator.from_line('').translate()
        self.assert_preamble('\n'.join(GLOBALS), model)

    def test_empty_stream(self):
        self.check_preamble_subtest(self._subtest_empty_stream)
        self.at_subtest(self._subtest_empty_stream_with_helpers)
