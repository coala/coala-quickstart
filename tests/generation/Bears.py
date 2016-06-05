import sys
import os
import unittest
from copy import deepcopy

from pyprint.ConsolePrinter import ConsolePrinter
from coalib.output.printers.LogPrinter import LogPrinter
from coalib.misc.ContextManagers import (
    simulate_console_inputs, suppress_stdout, retrieve_stdout)
from coala_quickstart.generation.Bears import (
    filter_relevant_bears, print_relevant_bears)

class TestBears(unittest.TestCase):

    def setUp(self):
        self.printer = ConsolePrinter()
        self.log_printer = LogPrinter(self.printer)
        self.old_argv = deepcopy(sys.argv)
        del sys.argv[1:]

    def tearDown(self):
        sys.argv = self.old_argv

    def test_filter_relevant_bears(self):
        res = filter_relevant_bears([('Python', 70), ('YAML', 20)])
        self.assertIn("YAML", res)
        self.assertIn("Python", res)
        self.assertTrue(len(res["YAML"]) > 0)
        self.assertTrue(len(res["Python"]) > 0)

    def test_print_relevant_bears(self):
        with retrieve_stdout() as custom_stdout:
            print_relevant_bears(self.printer, filter_relevant_bears(
                [('Python', 70), ('Unknown', 30)]))
            self.assertIn("PEP8Bear", custom_stdout.getvalue())
