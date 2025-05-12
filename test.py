#!/usr/bin/env python3
import unittest
import pathlib


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
