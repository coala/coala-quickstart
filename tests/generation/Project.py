import unittest

from pyprint.ConsolePrinter import ConsolePrinter
from coala_utils.ContextManagers import (
    retrieve_stdout, simulate_console_inputs)
from coala_quickstart.generation.Project import (
    get_used_languages, print_used_languages,
    ask_to_select_languages)


class TestPopularLanguages(unittest.TestCase):

    def setUp(self):
        self.printer = ConsolePrinter()

    def test_get_used_languages(self):
        file_lists = [["/tmp/file.py", "/tmp/file.py"],
                      ["/tmp/file.py", "/tmp/test.cpp"],
                      ["/tmp/file.py"],
                      ["/tmp/file.py", "/tmp/unknown.extension"],
                      ["/tmp/unknown.extension"],
                      []]
        results = [[('Python', 100)],
                   [('Python', 50), ('C++', 50)],
                   [('Python', 100)],
                   [('Python', 50)],
                   [],
                   []]

        for file_list, expected_result in zip(file_lists, results):
            result = get_used_languages(file_list)
            self.assertEqual(sorted(result), sorted(expected_result))

    def test_print_used_languages(self):
        with retrieve_stdout() as custom_stdout:
            print_used_languages(self.printer, [('Python', 100)])
            res = custom_stdout.getvalue()
            self.assertIn("Python", res)
            self.assertIn("100%", res)

        with retrieve_stdout() as custom_stdout:
            print_used_languages(self.printer, [('Python', 75), ('C++', 25)])
            self.assertIn("75%\n", custom_stdout.getvalue())

    def test_no_results(self):
        with retrieve_stdout() as custom_stdout:
            print_used_languages(self.printer, [])
            self.assertNotIn("following langauges", custom_stdout.getvalue())

    def test_ask_to_select_languages(self):
        languages = [('lang1', 50), ('lang2', 25), ('language3', 25)]
        res = []
        with simulate_console_inputs('1 2') as generator:
            res = ask_to_select_languages(languages, self.printer)
            self.assertEqual(generator.last_input, 0)
        self.assertEqual(res, [('lang1', 50), ('lang2', 25)])

        with simulate_console_inputs('6', '1') as generator:
            res = ask_to_select_languages(languages, self.printer)
            self.assertEqual(generator.last_input, 1)
        self.assertEqual(res, [('lang1', 50)])

        with simulate_console_inputs('\n') as generator:
            res = ask_to_select_languages(languages, self.printer)
            self.assertEqual(generator.last_input, 0)
        self.assertEqual(res, [('lang1', 50), ('lang2', 25),
                               ('language3', 25)])
