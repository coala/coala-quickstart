import os
import re
import unittest

from coala_quickstart.info_extractors.EditorconfigInfoExtractor import (
    EditorconfigInfoExtractor)
from coala_quickstart.info_extraction.Information import (
    IndentStyleInfo, IndentSizeInfo, TrailingWhitespaceInfo, FinalNewlineInfo,
    CharsetInfo, LineBreaksInfo)
from tests.TestUtilities import generate_files


test_file = """
# top-most EditorConfig file
root = true

# Unix-style newlines with a newline ending every file
[*]
end_of_line = lf
insert_final_newline = true

# Matches multiple files with brace expansion notation
# Set default charset
[*.{js,py}]
charset = utf-8
trim_trailing_whitespace = true
indent_size = tab
tab_width = 4

# 4 space indentation
[*.py]
indent_style = space
indent_size = 4

# Tab indentation (no size specified)
[Makefile]
indent_style = tab

# Indentation override for all JS under lib directory
[lib/**.js]
indent_style = space
indent_size = 2

# Matches the exact files either package.json or .travis.yml
[{package.json,.travis.yml}]
indent_style = space
indent_size = 2
"""


class EditorconfigInfoExtractorTest(unittest.TestCase):

    def setUp(self):
        self.current_dir = os.getcwd()

    def test_extracted_information(self):

        with generate_files(
              ['.editorconfig'],
              [test_file],
              self.current_dir) as gen_file:

            self.uut = EditorconfigInfoExtractor(
                ['.editorconfig'],
                self.current_dir)

            extracted_info = self.uut.extract_information()
            extracted_info = extracted_info['.editorconfig']

            information_types = extracted_info.keys()

            test_filenames = {
                '*': {
                    'valid': ['hello.js', 'hello.py'],
                    'invalid': []
                },
                '*.{js,py}': {
                    'valid': ['hello.py', 'hello.js'],
                    'invalid': ['hello.c']
                },
                '*.py': {
                    'valid': ['some_file.py', 'hello.py'],
                    'invalid': ['some.js', 'py']
                },
                'Makefile': {
                    'valid': ['Makefile'],
                    'invalid': ['NotAMakeFile']
                },
                'lib/**.js': {
                    'valid': ['lib/foo.js'],
                    'invalid': ['lib/foo', 'foo.js']
                },
                '{package.json,.travis.yml}': {
                    'valid': ['package.json', '.travis.yml'],
                    'invalid': ['someting_else']
                }
            }

            # defined configurations in test '.editorconfig' file
            defined_indent_styles = [
                ('*.py', 'space'), ('lib/**.js', 'space'), ('Makefile', 'tab'),
                ('{package.json,.travis.yml}', 'space')]
            defined_indent_sizes = [
                ('*.{js,py}', 4), ('lib/**.js', 2), ('*.py', 4),
                ('{package.json,.travis.yml}', 2)]
            defined_linebreak_types = [('*', 'lf')]
            defined_charsets = [('*.{js,py}', 'utf-8')]
            defined_final_newlines = [('*', True)]
            defined_trim_trailing_whitespaces = [('*.{js,py}', True)]

            for info_name, info in extracted_info.items():
                for i in info:
                    for fname in test_filenames[i.container_section]['valid']:
                        self.assertRegexpMatches(fname, i.scope[0])
                    for fname in test_filenames[i.container_section]['invalid']:
                        self.assertEqual(re.match(i.scope[0], fname), None)

            def compare_extracted_with_defined_info(defined_info,
                                                    info_name):
                self.assertIn(info_name, information_types)
                info_to_match = extracted_info[info_name]
                list_to_match = [(i.container_section, i.value)
                                 for i in info_to_match]
                self.assertEqual(len(defined_info), len(list_to_match))
                for info in defined_info:
                    self.assertIn(info, list_to_match)

            compare_extracted_with_defined_info(
                defined_indent_styles, 'IndentStyleInfo')

            compare_extracted_with_defined_info(
                defined_indent_sizes, 'IndentSizeInfo')

            compare_extracted_with_defined_info(
                defined_linebreak_types, 'LineBreaksInfo')

            compare_extracted_with_defined_info(
                defined_charsets, 'CharsetInfo')

            compare_extracted_with_defined_info(
                defined_final_newlines, 'FinalNewlineInfo')

            compare_extracted_with_defined_info(
                defined_trim_trailing_whitespaces, 'TrailingWhitespaceInfo')
