import os
import unittest

from coala_quickstart.info_extractors.RequirementsInfoExtractor import (
    RequirementsInfoExtractor)
from coala_quickstart.info_extraction.Information import (
    ProjectDependencyInfo, VersionInfo)
from tests.TestUtilities import generate_files


test_file = """
# This is the file to test requirements extractor.
# It should not parse this line.
Babel<=2.3.4
Flask==0.11.1 # Everything after # must be ignored.
Django>=1.5 # This is a comment.
Django<1.4
Jinja~2.9.6
# Neither this.
"""


class RequirementsInfoExtractorTest(unittest.TestCase):

    def setUp(self):
        self.current_dir = os.getcwd()

    def test_extracted_information(self):

        with generate_files(
            ['requirements'],
            [test_file],
                self.current_dir) as gen_file:

            self.uut = RequirementsInfoExtractor(
                ['requirements'],
                self.current_dir)
            extracted_info = self.uut.extract_information()
            extracted_info = extracted_info[
                os.path.normcase('requirements')
            ]

            information_types = extracted_info.keys()
            self.assertIn("ProjectDependencyInfo", information_types)
            dep_info = extracted_info['ProjectDependencyInfo']
            self.assertEqual(len(dep_info), 4)

            requirements_list = [('Babel', '<=2.3.4'),
                                 ('Flask', '==0.11.1'),
                                 ('Django', '>=1.5'),
                                 ('Jinja', '~2.9.6'), ]

            deps = [(dep.value, dep.version.value) for dep in dep_info]
            self.assertNotIn(('ignore_this', '<=2.4'), deps)

            for requirement in requirements_list:
                self.assertIn(requirement, deps)
