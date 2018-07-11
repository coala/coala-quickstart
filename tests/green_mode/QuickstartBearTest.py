import unittest

from coala_quickstart.green_mode.QuickstartBear import (
    QuickstartBear)
from coalib.settings.Section import Section


class TestQuickstartBear(unittest.TestCase):

    def setUp(self):
        self.section = Section('test-section')

    def test_quickstartbear_for_random_files(self):
        bear = QuickstartBear(self.section, None)
        fileA = ('s=hex(0)\n',
                 'orig_hex = ""\n',
                 'mall_hex = ""\n',
                 'for i in orig:\n')
        ret_val = bear.run('some_file_name', fileA)
        self.assertEqual(ret_val, [{'max_line_length': 15,
                                    'max_lines_per_file': 4,
                                    'min_lines_per_file': 4}])
        # These are just data sets for the particular bear
        # settings, not actual values. The actual value
        # are further aggregated and then the actual value
        # for the setting is found out.
        ret_val = bear.run('some_random_file_name', None)
        self.assertEqual(ret_val, [None])
