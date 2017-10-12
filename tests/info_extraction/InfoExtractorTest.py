import os
import unittest

from coala_quickstart.info_extraction.Info import Info
from coala_quickstart.info_extraction.InfoExtractor import InfoExtractor
from tests.TestUtilities import generate_files


class InfoExtractorTest(unittest.TestCase):

    def setUp(self):
        self.current_dir = os.getcwd()

        class DummyInfo(Info):
            description = 'Some dummy information with no meaning.'

        class AnotherDummyInfo(Info):
            description = 'Another such information.'

        class DummyInfoExtractor(InfoExtractor):
            spec_references = ['some/dummy/link', 'another/dummy/link']

            def parse_file(self, fname, file_content):
                return file_content

            def find_information(self, fname, parsed_file):
                return [DummyInfo(
                    fname,
                    'Dummy information it is!')]

        class DummyMultiInfoExtractor(InfoExtractor):

            def parse_file(self, fname, file_content):
                return file_content

            def find_information(self, fname, parsed_file):
                return [
                    DummyInfo(
                        fname,
                        'Dummy information it is!'),
                    DummyInfo(
                        fname,
                        'Same kind of dummy information it is!'),
                    AnotherDummyInfo(
                        fname,
                        'Another kind of dummy information!!')]

        class NoInfoExtractor(InfoExtractor):

            def parse_file(self, fname, file_content):
                return file_content

            def find_information(self, fname, parsed_file):
                return []

        class WrongSupportedInfoExtractor(InfoExtractor):
            supported_file_globs = ('**',)
            supported_info_kinds = (DummyInfoExtractor,)

            def parse_file(self, fname, file_content):
                return file_content

            def find_information(self, fname, parsed_file):
                # The extractor returns AnotherDummyInfo instead
                # of DummyInfo.
                return [AnotherDummyInfo(
                            fname,
                            'Some random information it is!')]

        class TempfileExtractor(InfoExtractor):
            supported_file_globs = ('tempfile**', '**tempfile')

            def parse_file(self, fname, file_content):
                return file_content

            def find_information(self, fname, parsed_file):
                return [DummyInfo(
                            fname,
                            'Some random information it is!')]

        self.DummyInfo = DummyInfo
        self.DummyInfoExtractor = DummyInfoExtractor
        self.DummyMultiInfoExtractor = DummyMultiInfoExtractor
        self.NoInfoExtractor = NoInfoExtractor
        self.TempfileExtractor = TempfileExtractor
        self.WrongSupportedInfoExtractor = WrongSupportedInfoExtractor

    def test_implementation(self):

        uut = InfoExtractor(
            ['**'],
            self.current_dir)

        self.assertRaises(NotImplementedError, uut.parse_file, 'foo', '')
        self.assertRaises(
            NotImplementedError,
            uut.find_information,
            'some_filename',
            'some_parsed_file')

    def test_multiple_target_globs(self):

        target_filenames = [
            'target_file_1',
            'target_file_2',
            'another_target_file']

        target_file_contents = ['Some content.', 'Any content', 'More content']

        with generate_files(
                target_filenames,
                target_file_contents,
                self.current_dir) as gen_files:

            uut = self.DummyInfoExtractor(
                ['target_file_**', 'another_target_file'],
                self.current_dir)

            extracted_info = uut.extract_information()

            self.assertEqual(len(extracted_info.keys()), len(target_filenames))
            self.assertEqual(extracted_info, uut.information)

            for tf in target_filenames:
                self.assertEqual(len(extracted_info[tf]['DummyInfo']), 1)
                self.assertIsInstance(
                    extracted_info[tf]['DummyInfo'][0],
                    self.DummyInfo)
                self.assertEqual(
                    extracted_info[tf]['DummyInfo'][0].source, tf)

                # test if the extractor field is added automatically
                self.assertIsInstance(
                    extracted_info[tf]['DummyInfo'][0].extractor,
                    InfoExtractor)

    def test_multiple_information(self):

        target_filenames = ['target_file_1', ]

        target_file_contents = ['Some content.']

        with generate_files(
                target_filenames,
                target_file_contents,
                self.current_dir) as gen_files:

            uut = self.DummyMultiInfoExtractor(
                ['target_file_**', 'another_target_file'],
                self.current_dir)

            extracted_info = uut.extract_information()

            self.assertEqual(len(extracted_info.keys()), len(target_filenames))
            self.assertEqual(extracted_info, uut.information)

            for tf in target_filenames:
                self.assertEqual(len(extracted_info[tf]), 2)
                self.assertEqual(len(extracted_info[tf]['DummyInfo']), 2)
                self.assertIsInstance(
                    extracted_info[tf]['DummyInfo'][1],
                    self.DummyInfo)
                self.assertEqual(len(extracted_info[tf]['AnotherDummyInfo']), 1)
                self.assertIsInstance(
                    extracted_info[tf]['DummyInfo'][0],
                    self.DummyInfo)

    def test_no_information_found(self):
        target_filenames = ['target_file_1', ]

        target_file_contents = ['Some content.']

        uut = self.NoInfoExtractor(
            ['target_file_**', 'another_target_file'],
            self.current_dir)

        with generate_files(
                target_filenames,
                target_file_contents,
                self.current_dir) as gen_files:

            extracted_info = uut.extract_information()

            self.assertEqual(len(extracted_info.keys()), 0)
            self.assertEqual(extracted_info, uut.information)

            for tf in target_filenames:
                self.assertIsNone(extracted_info.get(tf))

    def test_filemname_field(self):

        class TestInfoExtractor(InfoExtractor):

            def parse_file(self, fname, file_content):
                assert os.path.exists(fname) == 1

            def find_information(self, fname, parsed_file):
                return []

        target_filenames = ['target_file_1']

        target_file_contents = ['Some content.']

        uut = TestInfoExtractor(
            ['target_file_**'],
            self.current_dir)

        with generate_files(
                target_filenames,
                target_file_contents,
                self.current_dir) as gen_file:
            uut.extract_information()

    def test_unsupported_files(self):
        target_filenames = ['tempfile1', '1tempfile', 'tmpfile_not_allowed']

        target_file_contents = ['Some content.', 'More content', 'Content']

        with generate_files(
                target_filenames,
                target_file_contents,
                self.current_dir) as gen_files:

            with self.assertRaisesRegexp(
                    ValueError,
                    ('The taraget file tmpfile_not_allowed does not match the '
                     "supported file globs \('tempfile\*\*', '\*\*tempfile'\) "
                     'of TempfileExtractor')):
                uut = self.TempfileExtractor(
                    ['tempfile1', 'tmpfile_not_allowed'],
                    self.current_dir)

                uut.extract_information()

            uut = self.TempfileExtractor(
                ['**tempfile**'],
                self.current_dir)

            extracted_info = uut.extract_information()
            self.assertEqual(len(extracted_info.keys()), 2)

            uut = self.TempfileExtractor(
                ['tempfile1', 'tempfile_not_present'],
                self.current_dir)

            extracted_info = uut.extract_information()
            self.assertEqual(len(extracted_info.keys()), 1)

    def test_supported_info_kinds(self):
        target_filenames = ['target_file_1', ]

        target_file_contents = ['Some content.']

        with generate_files(
                target_filenames,
                target_file_contents,
                self.current_dir) as gen_files:

            uut = self.WrongSupportedInfoExtractor(
                ['target_file_**'],
                self.current_dir)

            with self.assertRaisesRegexp(
                    ValueError,
                    ('The class AnotherDummyInfo is not present in supported '
                     'information kinds of WrongSupportedInfoExtractor')):

                uut.extract_information()

    def test_spec_references_filed(self):
        uut = self.DummyInfoExtractor
        self.assertEqual(len(uut.spec_references), 2)
        self.assertEqual(
            uut.spec_references,
            ['some/dummy/link', 'another/dummy/link'])

        uut = self.DummyMultiInfoExtractor
        self.assertEqual(uut.spec_references, [])
