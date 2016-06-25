import os
import unittest

from pyprint.ConsolePrinter import ConsolePrinter
from coalib.output.printers.LogPrinter import LogPrinter
from coalib.misc.ContextManagers import (
    simulate_console_inputs, suppress_stdout, retrieve_stdout)
from coala_quickstart.generation.FileGlobs import get_project_files

class TestQuestion(unittest.TestCase):

    def setUp(self):
        self.printer = ConsolePrinter()
        self.log_printer = LogPrinter(self.printer)

    def test_get_project_files(self):
        orig_cwd = os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        os.makedirs("file_globs_testfiles", exist_ok=True)
        os.chdir("file_globs_testfiles")

        os.makedirs("src", exist_ok=True)
        os.makedirs("ignore_dir", exist_ok=True)
        open(os.path.join("src", "file.c"), "w").close()
        open("root.c", "w").close()
        open(os.path.join("ignore_dir", "src.c"), "w").close()
        open(os.path.join("ignore_dir", "src.js"), "w").close()

        with suppress_stdout(), simulate_console_inputs("**.c", "ignore_dir/**"):
            res = get_project_files(self.log_printer, self.printer, os.getcwd())
            self.assertIn(os.path.join(os.getcwd(), "src", "file.c"), res)
            self.assertIn(os.path.join(os.getcwd(), "root.c"), res)
            self.assertNotIn(os.path.join(os.getcwd(), "ignore_dir/src.c"), res)
            self.assertNotIn(os.path.join(os.getcwd(), "ignore_dir/src.js"), res)

        os.chdir(orig_cwd)
