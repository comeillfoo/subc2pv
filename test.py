#!/usr/bin/env python3
import unittest
import itertools

import tests.lut
import tests.translator


if __name__ == '__main__':
    loader = unittest.TestLoader()
    suites = unittest.TestSuite(
        map(loader.loadTestsFromTestCase,
            itertools.chain(tests.lut.suite(),
                            tests.translator.suite()))
    )
    runner = unittest.TextTestRunner()
    _ = runner.run(suites)
