# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=line-too-long

import unittest
import translator


class TestTranslator(unittest.TestCase):

    def test_translation_func(self):
        t = translator.Translator()
        with open("asm/func.asm", "r") as file:
            t.parse_file(file)

        self.assertEqual(t.labels, ['.start', '.hlt'])
        self.assertEqual(t.lvalues, {'0': 0, '1': 5})
        self.assertEqual(t.pointers, ['one', 'two', 'tt'])
        self.assertEqual(t.program_section, 5)

    def test_translation_prob5(self):
        t = translator.Translator()
        with open("asm/prob5.asm", "r") as file:
            t.parse_file(file)

        self.assertEqual(t.labels, ['.start', '.loop', '.inner_loop', '.mul_to_max', '.mul_loop', '.hlt'])
        self.assertEqual(t.lvalues, {'0': 0, '1': 2, '2': 8, '3': 17, '4': 18, '5': 26})
        self.assertEqual(t.pointers, ['result', 'prime', 'target', 'count'])
        self.assertEqual(t.program_section, 6)
