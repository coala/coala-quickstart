import os
import unittest

from coala_quickstart.info_extraction.Info import Info
from coala_quickstart.info_extraction.InfoExtractor import InfoExtractor


class InfoTest(unittest.TestCase):

    def setUp(self):

        class DummyInfoExtractor(InfoExtractor):

            def parse_file(self, file_content):
                return file_content

            def find_information(self, fname, parsed_file):
                return [Info(
                    fname,
                    'Dummy information it is!')]

        self.base_info = Info(
            'source_file',
            'base_info_value',
            DummyInfoExtractor(['some_file'], os.getcwd()))

        class InfoA(Info):
            description = 'Information A'
            value_type = (str, int)
            example_values = ['coala', 420]

        class InfoB(Info):
            description = 'Info class without value_type'
            example_values = [['literally', 'anything']]

        self.info_a = InfoA(
            'source_file',
            'info_a_value',
            extra_param='extra_param_value')

        self.InfoA = InfoA
        self.InfoB = InfoB

    def test_main(self):
        self.assertEqual(self.base_info.name, 'Info')
        self.assertEqual(self.base_info.value, 'base_info_value')
        self.assertEqual(self.base_info.source, 'source_file')
        self.assertEqual(self.base_info.description, 'Some Description.')
        self.assertEqual(len(self.base_info.example_values), 0)
        self.assertIsInstance(self.base_info.extractor, InfoExtractor)

    def test_derived_instances(self):
        self.assertEqual(self.info_a.name, 'InfoA')
        self.assertEqual(self.info_a.value, 'info_a_value')
        self.assertEqual(self.info_a.source, 'source_file')
        self.assertEqual(self.info_a.extra_param, 'extra_param_value')
        self.assertEqual(self.info_a.description, 'Information A')
        self.assertEqual(self.info_a.example_values, ['coala', 420])

    def test_value_type(self):
        with self.assertRaisesRegexp(
                TypeError,
                'value must be an instance of one of '
                "\(<class 'str'>, <class 'int'>\) \(provided value: 5.5\)"):
            self.InfoA('source_file', 5.5)

        self.InfoB('source_file', 5.5)
