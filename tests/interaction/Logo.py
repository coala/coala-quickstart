import unittest

from pyprint.ConsolePrinter import ConsolePrinter
from coala_utils.ContextManagers import retrieve_stdout
from coala_quickstart.interaction.Logo import (
    print_welcome_message, print_side_by_side)


class TestLogo(unittest.TestCase):

    def setUp(self):
        self.printer = ConsolePrinter()

    def test_print_side_by_side(self):
        with retrieve_stdout() as custom_stdout:
            print_side_by_side(
                self.printer,
                ['Left side content.'],
                ['Right side content',
                 'that is longer than the',
                 'left side.'],
                limit=80)
            self.assertIn(
                'side content.\x1b[0m \x1b[34mRight side',
                custom_stdout.getvalue())

    def test_print_welcome_message(self):
        with retrieve_stdout() as custom_stdout:
            print_welcome_message(self.printer)
            self.assertIn('o88Oo', custom_stdout.getvalue())
