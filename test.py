#!/usr/bin/env python3
import unittest

class SubCRulesCases(unittest.TestCase):
    def test_hello_world(self):
        self.assertEqual(2 * 2, 4, 'Hello, World')


if __name__ == '__main__':
    unittest.main()
