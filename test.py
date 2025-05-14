#!/usr/bin/env python3
import unittest
import pathlib
from typing import Tuple

from translator import Translator

class TranslatorTestCases(unittest.TestCase):
    def test_empty_stream(self):
        translator = Translator.from_line('')
        model = translator.translate()
        self.assertTrue(not model.functions, 'No functions should be parsed')
        self.assertTrue(not model.preamble, 'No preamble should be generated')

    def test_enum_declaration(self):
        enum_names = [ 'T', 'asdfadsfsdf', '____', 'Mtypes', ]
        for enum_name in enum_names:
            translator = Translator.from_line(f'enum {enum_name};')
            model = translator.translate()
            self.assertTrue(not model.functions, 'No functions should be parsed')
            self.assertEqual(model.preamble, f'type {enum_name}.\n')

    def test_enum_definition(self):
        enums = [
            ('T', ('A', 'b', 'C')),
            ('asdfasdf', ('asdff', 'aslkdnf')),
            ('________', ('__')),
            ('Mtypes', ('SEND', 'RECV', 'ACK', 'NACK'))
        ]
        for (enum_name, enum_consts) in enums:
            lines = [f'enum {enum_name}', '{' ]
            expected = [f'type {enum_name}.']
            for enum_const in enum_consts:
                lines.append(f'\t{enum_const},')
                expected.append(f'const {enum_const}: {enum_name}.')
            lines.append('};')
            expected.append('\n')
            translator = Translator.from_lines(lines)
            model = translator.translate()
            self.assertTrue(not model.functions)
            self.assertEqual(model.preamble, '\n'.join(expected))

    def test_struct_and_union_declarations(self):
        names = [ '_', 'A', 'asdfkljdsfn', '_tmp8', 'message' ]
        for name in names:
            for ttype in ('struct', 'union'):
                translator = Translator.from_line(f'{ttype} {name};')
                model = translator.translate()
                self.assertTrue(not model.functions)
                self.assertEqual(model.preamble, f'type {name}.\n')

    def _dict2fielded_def(self, name: str, fields: Tuple[str, str] = [],
                          ttype: str = 'struct') -> str:
        lines = [f'{ttype} {name}', '{']
        for fname, ftype in fields:
            lines.append(f'{ftype} {fname};')
        lines.append('};')
        return '\n'.join(lines)

    def test_empty_struct_and_union_definitions(self):
        names = [ '_', 'A', 'asdfkljdsfn', '_tmp8', 'message' ]
        for name in names:
            for ttype in ('struct', 'union'):
                translator = Translator.from_line(
                    self._dict2fielded_def(name, ttype=ttype))
                model = translator.translate()
                self.assertTrue(not model.functions)
                expected = '\n'.join([f'type {name}.', '',
                                      f'fun _{name}_init(): {name}.'])
                self.assertEqual(model.preamble, expected)

    def test_struct_and_union_with_single_enum_definition(self):
        names = [ '_', 'A', 'asdfkljdsfn', '_tmp8', 'message' ]
        for name in names:
            for ttype in ('struct', 'union'):
                translator = Translator.from_line(
                    self._dict2fielded_def(name, [('x', 'enum A')], ttype))
                model = translator.translate()
                self.assertTrue(not model.functions)
                expected = '\n'.join([
                    f'type {name}.', '', f'fun _{name}_get_x(self: {name}): A.',
                    f'fun _{name}_set_x(self: {name}, x: A): {name}.',
                    f'fun _{name}_init(x: A): {name}.'])
                self.assertEqual(model.preamble, expected)

    def test_structs_single_integer(self):
        structs = [
            ('_', ('x', 'int')),
            ('A', ('x', 'char')),
            ('client', ('port', 'short')),
            ('server', ('addr', 'long')),
            ('asf', ('field', '__m128')),
            ('Q', ('PP9', '__m128d')),
            ('WFD2', ('_qwerty_', '__m128i')),
        ]

        for sname, sfield in structs:
            translator = Translator.from_line(self._dict2fielded_def(sname, [sfield]))
            model = translator.translate()
            self.assertTrue(not model.functions)
            fname, _ = sfield
            expected = '\n'.join([
                f'type {sname}.', '', f'fun _{sname}_get_{fname}(self: {sname}): nat.',
                f'fun _{sname}_set_{fname}(self: {sname}, {fname}: nat): {sname}.',
                f'fun _{sname}_init({fname}: nat): {sname}.'])
            self.assertEqual(model.preamble, expected)

    def test_structs_single_bool(self):
        structs = [
            ('_', ('x', '_Bool')),
            ('A', ('x', '_Bool')),
            ('client', ('port', '_Bool')),
            ('server', ('addr', '_Bool')),
            ('asf', ('field', '_Bool')),
            ('Q', ('PP9', '_Bool')),
            ('WFD2', ('_qwerty_', '_Bool')),
        ]

        for sname, sfield in structs:
            translator = Translator.from_line(self._dict2fielded_def(sname, [sfield]))
            model = translator.translate()
            self.assertTrue(not model.functions)
            fname, _ = sfield
            expected = '\n'.join([
                f'type {sname}.', '', f'fun _{sname}_get_{fname}(self: {sname}): bool.',
                f'fun _{sname}_set_{fname}(self: {sname}, {fname}: bool): {sname}.',
                f'fun _{sname}_init({fname}: bool): {sname}.'])
            self.assertEqual(model.preamble, expected)


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
