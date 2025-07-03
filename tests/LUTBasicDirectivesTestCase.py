#!/usr/bin/env python3
import unittest
import pathlib

from lut import LookUpTable


class LUTBasicDirectivesTestCase(unittest.TestCase):
    def setUp(self):
        self._gibberishes = [
            ['asdfsfdsfds'],
            ['asdfdf', '1234498324034', '!@#$%^&*'],
            ['@#RTGVRUI', '@#$176234ksdn', 'vbiwnf34792472', 'bvsdc23864892'],
        ]
        # File tests auxilaries
        self._stress_paths = [
            'main.c',
            'a.c',
            'a/b/c/d/proto.c',
            '/tmp/______/_some.c'
        ]
        self._file_templates = [
            '%F {}',
            '%F\t{}',
            '%F  \t{}',
            '%F {} asdasdf\t\tvknjdf___',
        ]
        self._multiple_files = list(map(lambda x: f'{x}.c', range(3)))
        self._multiple_files_templates = [
            ('%F {}\n%F {}', 1),
            ('%F {}\n____\n%F {}', 1),
            ('%F {}\n____\n%F {}\n%F {} adsfdsf', 2),
            ('%F {}\n____\n%F {}\n%F {}\nasdfdf', 2),
            ('%F {}\n____\n%F {}\nasdfdsf\n%F {}', 2),
        ]
        # Xtract tests auxilaries
        self._stress_functions = ['client', 'server', 'sendreceive',
            'readwrite', 'syscall', 'http_get', 'http_post']
        self._extract_templates = [
            '%X {}',
            '%X\t{}',
            '%X  \t{}',
            '%X {} asdasdf\t\tvknjdf___',
        ]
        # Substitute tests auxilaries
        self._stress_substitutions = ['fun main(argc: nat, argv: bitstring): nat.',
            'aldsnfdlskfn', '___________', 'fun a(): bool.']
        self._substitute_templates = [
            '%S main {}',
            '%S\tmain\t{}',
            '%S  main\t{}',
            '%S main    {}',
        ]
        # Paste tests auxilaries
        self._paste_template = '%P\n{}\n%%'
        self._stress_pastes = [
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
        return super().setUp()

    def _assert_empty_lut(self, lut: LookUpTable):
        self.assertIsNone(lut.file(), 'No path should be processed')
        self.assertEqual(lut.extracts(), set(), 'No functions should be extracted')
        self.assertEqual(lut.substitutes(), {}, 'No defines should be substituted')
        self.assertEqual(lut.paste(), '', 'No text should be pasted at the end')

    def test_nolines(self):
        self._assert_empty_lut(LookUpTable.from_lines([]))

    def test_gibberish(self):
        for gibberish in self._gibberishes:
            self._assert_empty_lut(LookUpTable.from_lines(gibberish))

    def test_single_file(self):
        for template in self._file_templates:
            for path in self._stress_paths:
                lut = LookUpTable.from_line(template.format(path))
                self.assertEqual(lut.file(), pathlib.Path(path))

    def test_multiple_files(self):
        for template, i in self._multiple_files_templates:
            lut = LookUpTable.from_line(template.format(*self._multiple_files))
            self.assertEqual(lut.file(), pathlib.Path(self._multiple_files[i]))

    def test_single_extract(self):
        for template in self._extract_templates:
            for function in self._stress_functions:
                lut = LookUpTable.from_line(template.format(function))
                self.assertEqual(lut.extracts(), set([function]))

    def test_single_substitution(self):
        for template in self._substitute_templates:
            for substitution in self._stress_substitutions:
                lut = LookUpTable.from_line(template.format(substitution))
                self.assertEqual(lut.substitute('main'), substitution)

    def test_single_paste(self):
        for paste in self._stress_pastes:
            lut = LookUpTable.from_line(self._paste_template.format(paste))
            self.assertEqual(lut.paste(), paste + '\n')
