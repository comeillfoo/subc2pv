#!/usr/bin/env python3
import unittest
import itertools

from tests.LUTBasicDirectivesTestCase import LUTBasicDirectivesTestCase
from tests.TranslatorBasicTestCase import TranslatorBasicTestCase
from tests.EnumsDeclarationsAndDefinitionsTestCase import EnumsDeclarationsAndDefinitionsTestCase
from tests.UnionsOrStructsDeclarationsAndDefinitionsTestCase import UnionsOrStructsDeclarationsAndDefinitionsTestCase
from tests.FunctionsDeclarationsTestCase import FunctionsDeclarationsTestCase
from tests.FunctionDefinitionsTestCase import FunctionDefinitionsTestCase
from tests.AssignmentsTestCase import AssignmentsTestCase
from tests.BranchingTestCase import BranchingTestCase
from tests.ExpressionsTestCase import ExpressionsTestCase
from tests.LoopsTestCase import LoopsTestCase
from tests.FunctionCallTestCase import FunctionCallTestCase


def lut_suite() -> list:
    return [LUTBasicDirectivesTestCase]

def translator_suite() -> list:
    return [
        TranslatorBasicTestCase,
        EnumsDeclarationsAndDefinitionsTestCase,
        UnionsOrStructsDeclarationsAndDefinitionsTestCase,
        FunctionsDeclarationsTestCase,
        FunctionDefinitionsTestCase,
        AssignmentsTestCase,
        BranchingTestCase,
        ExpressionsTestCase,
        LoopsTestCase,
        FunctionCallTestCase
    ]


if __name__ == '__main__':
    loader = unittest.TestLoader()
    suites = unittest.TestSuite(
        map(loader.loadTestsFromTestCase,
            itertools.chain(lut_suite(), translator_suite()))
    )
    runner = unittest.TextTestRunner()
    _ = runner.run(suites)
