# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=line-too-long

import unittest
import translator


class TestTranslator(unittest.TestCase):

    def test_translation_func(self):
        trans = translator.Translator()
        with open("asm/func.asm", "r", encoding='utf-8') as file:
            trans.parse_file(file)

        self.assertEqual(trans.labels, ['.start', '.hlt'])
        self.assertEqual(trans.lvalues, {'0': 0, '1': 5})
        self.assertEqual(trans.pointers, ['one', 'two', 'tt'])
        self.assertEqual(trans.program_section, 5)

    def test_translation_prob5(self):
        trans = translator.Translator()
        with open("asm/prob5.asm", "r", encoding='utf-8') as file:
            trans.parse_file(file)

        self.assertEqual(trans.labels, ['.start', '.loop', '.inner_loop', '.mul_to_max', '.mul_loop', '.hlt'])
        self.assertEqual(trans.lvalues, {'0': 0, '1': 2, '2': 8, '3': 17, '4': 18, '5': 26})
        self.assertEqual(trans.pointers, ['result', 'prime', 'target', 'count'])
        self.assertEqual(trans.program_section, 6)
