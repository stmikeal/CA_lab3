# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=line-too-long

import unittest
import translator


class TestTranslator(unittest.TestCase):

    def test_translation_many_add(self):
        t = translator.Translator()
        with open("examples/many_add_test.lisp", "rt", encoding="utf-8") as file:
            text = file.read()

        code = translator.translate(text)
        print(code)
        self.assertEqual([{'opcode': 'movv', 'arg': [0, 1]},
                          {'opcode': 'movv', 'arg': [1, 2]},
                          {'opcode': 'movv', 'arg': [2, 3]},
                          {'opcode': 'movv', 'arg': [3, 4]},
                          {'opcode': 'movv', 'arg': [4, 0]},
                          {'opcode': 'add', 'arg': [0, 1, 2, 3]},
                          {'opcode': 'mov', 'arg': [4]},
                          {'opcode': 'print', 'arg': [4]},
                          {'opcode': 'halt'}],
                         code)

    def test_translation_err1(self):
        with open("examples/err1.lisp", "rt", encoding="utf-8") as file:
            text = file.read()

        try:
            translator.translate(text)
            self.fail('validator verification test 1 failed')
        except AssertionError:
            isa_const.deep = 0
            isa_const.code.clear()
            isa_const.terms.clear()
            isa_const.term_number = 0

    def test_translation_err2(self):
        with open("examples/err2.lisp", "rt", encoding="utf-8") as file:
            text = file.read()

        try:
            translator.translate(text)
            self.fail('validator verification test 2 failed')
        except AssertionError:
            isa_const.deep = 0
            isa_const.code.clear()
            isa_const.terms.clear()
            isa_const.term_number = 0
