# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=line-too-long
import contextlib
import io
import unittest

import translator
import machine


class TestTranslator(unittest.TestCase):

    def test_hello(self):
        source = "asm/hw.asm"
        target = "asm/hw.json"
        input_file = "input_files/helloWorld.input"
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            translator.main([0, source, target])
            machine.prepare_and_go([0, target, input_file])

        self.assertEqual(stdout.getvalue(), "Output: ['H', 'e', 'l', 'l', 'o', ',', ' ', 'W', 'o', 'r', 'l', 'd', "
                                            "'!']\nInstruction Counter: 41\nTicks: 154\n")

    def test_cat(self):
        source = "asm/cat.asm"
        target = "asm/cat.json"
        input_file = "input_files/cat.input"

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            translator.main([0, source, target])
            machine.prepare_and_go([0, target, input_file])

        self.assertEqual(stdout.getvalue(),"Output: ['C', 'A', 'T']\nInstruction Counter: 15\nTicks: 24\n")

    def test_func(self):
        source = "asm/func.asm"
        target = "asm/func.json"
        input_file = "input_files/cat.input"

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            with self.assertLogs('', level='DEBUG') as logs:
                translator.main([0, source, target])
                machine.prepare_and_go([0, target, input_file])

        self.assertEqual(stdout.getvalue(), 'Output: []\nInstruction Counter: 5\nTicks: 8\n')

        expect_log = [
            "DEBUG:root:TICK: 0, ADDR: 0, IP: 0, ACC: 0, ZCP: 101, SC: 0, WR: 7, RD: 29",
            "DEBUG:root:TICK: 1, ADDR: 28, IP: 0, ACC: 0, ZCP: 101, SC: 1, WR: 7, RD: 29",
            "DEBUG:root:TICK: 2, ADDR: 28, IP: 1, ACC: 13, ZCP: 101, SC: 0, WR: 7, RD: 29",
            "DEBUG:root:TICK: 3, ADDR: 27, IP: 1, ACC: 13, ZCP: 101, SC: 1, WR: 7, RD: 29",
            "DEBUG:root:TICK: 4, ADDR: 27, IP: 2, ACC: 26, ZCP: 001, SC: 0, WR: 7, RD: 29",
            "DEBUG:root:TICK: 5, ADDR: 27, IP: 3, ACC: 8, ZCP: 011, SC: 0, WR: 7, RD: 29",
            "DEBUG:root:TICK: 6, ADDR: 27, IP: 4, ACC: 7, ZCP: 001, SC: 0, WR: 7, RD: 29",
            "DEBUG:root:TICK: 7, ADDR: 27, IP: 5, ACC: 51, ZCP: 001, SC: 0, WR: 7, RD: 29"]
        print(logs.output)
        for expected in expect_log:
            contains = False
            for log in logs.output:
                contains |= log.count(expected)
            self.assertTrue(contains)
