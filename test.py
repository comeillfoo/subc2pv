#!/usr/bin/env python3
import unittest


from lut import LookUpTable

class LUTTestCases(unittest.TestCase):
    def test_nolines(self):
        lut = LookUpTable.from_lines([])


    def test_gibberish(self):
        no_directives = [
            ['asdfsfdsfds'],
            ['asdfdf', '1234498324034', '!@#$%^&*'],
            ['@#RTGVRUI', '@#$176234ksdn', 'vbiwnf34792472', 'bvsdc23864892'],
        ]
        for no_directive in no_directives:
            lut = LookUpTable.from_lines(no_directive)


    def test_single_file(self):
        cases = [
            ['%F main.c'],
            ['%F\tmain.c'],
            ['%F  /a/b/c/d/main.c'],
        ]
        for case in cases:
            lut = LookUpTable.from_lines(case)


    def test_multiple_files(self):
        cases = [
            ['%F a.c', '%F b.c', '%F c.c']
        ]
        for case in cases:
            lut = LookUpTable.from_lines(case)


if __name__ == '__main__':
    unittest.main()
