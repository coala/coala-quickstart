import os
import unittest

from coala_quickstart.generation.InfoCollector import (
    collect_info)
from tests.TestUtilities import generate_files


package_json = """
{
    "name": "awesome-packages",
    "version": "0.8.0",
    "license": "MIT",
    "dependencies": {
        "coffeelint": "~1",
        "ramllint": ">=1.2.2 <1.2.4"
    },
    "files": ["dist"],
    "man" : ["./man/foo.1", "./man/bar.1"]
}
"""

editorconfig = """
root = true

[*]
end_of_line = lf
insert_final_newline = true

[*.{js,py}]
charset = utf-8
trim_trailing_whitespace = true
indent_size = tab
tab_width = 4

[*.py]
indent_style = space
indent_size = 4

[{package.json,.travis.yml}]
indent_style = space
indent_size = 2
"""

gemfile = """
source "https://rubygems.org"

gem "puppet-lint", "2.1.1"
gem "rubocop", "0.47.1"
gem "scss_lint", require: false
gem "RedCloth", :require => "redcloth"
gem "omniauth", ">= 0.2.6", :git => "git://github.com/intridea/omniauth.git"

group :assets do
  gem 'some-gem', source: "https://gems.example.com"
end
gem "rspec-rails", ">= 2.6.1", :group => [:development, :test]
end
"""


class InfoCollectorTest(unittest.TestCase):

    def setUp(self):
        self.uut = collect_info
        self.test_dir = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'information_collector_testfiles')

    def test_collected_info(self):

        files_to_create = ['package.json', '.editorconfig', 'Gemfile']
        target_file_contents = [package_json, editorconfig, gemfile]

        with generate_files(
                files_to_create,
                target_file_contents,
                self.test_dir) as gen_files:

            collected_info = self.uut(self.test_dir)

            expected_results = [
                ('TrailingWhitespaceInfo', ['.editorconfig'], 1),
                ('FinalNewlineInfo', ['.editorconfig'], 1),
                ('IndentStyleInfo', ['.editorconfig'], 2),
                ('IndentSizeInfo', ['.editorconfig'], 3),
                ('LineBreaksInfo', ['.editorconfig'], 1),
                ('CharsetInfo', ['.editorconfig'], 1),
                ('ProjectDependencyInfo', ['Gemfile', 'package.json'], 9),
                ('ManFilesInfo', ['package.json'], 1),
                ('LicenseUsedInfo', ['package.json'], 1),
                ('IncludePathsInfo', ['package.json'], 1)]

            self.assertEqual(len(collected_info.keys()), len(expected_results))

            for iname, isources, icount in expected_results:
                self.assertEqual(len(collected_info[iname]), icount)
                isources = [os.path.normcase(i) for i in isources]
                for info in collected_info[iname]:
                    self.assertIn(info.source, isources)
