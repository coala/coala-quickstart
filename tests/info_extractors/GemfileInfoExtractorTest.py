import os
import unittest

from coala_quickstart.info_extractors.GemfileInfoExtractor import (
    GemfileInfoExtractor)
from coala_quickstart.info_extraction.Information import (
    ProjectDependencyInfo, VersionInfo)
from tests.TestUtilities import generate_files


test_file = """
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

# Some comment
# gem "not_to_consider"

group :development, :test, :cucumber do
  gem "rspec-rails", "~> 2.0.0"
  gem "ruby-debug19", :platforms => :mri_19
end
"""


class GemfileInfoExtractorTest(unittest.TestCase):

    def setUp(self):
        self.current_dir = os.getcwd()

    def test_extracted_information(self):

        with generate_files(
              ['Gemfile'],
              [test_file],
              self.current_dir) as gen_file:

            self.uut = GemfileInfoExtractor(
                ['Gemfile'],
                self.current_dir)

            extracted_info = self.uut.extract_information()
            extracted_info = extracted_info[
                os.path.normcase('Gemfile')]

            information_types = extracted_info.keys()

            self.assertIn('ProjectDependencyInfo', information_types)
            dep_info = extracted_info['ProjectDependencyInfo']
            self.assertEqual(len(dep_info), 9)

            gems = [('some-gem', ''), ('puppet-lint', '2.1.1'),
                    ('rubocop', '0.47.1'), ('scss_lint', ''), ('RedCloth', ''),
                    ('rspec-rails', '>= 2.6.1'), ('rspec-rails', '~> 2.0.0'),
                    ('ruby-debug19', ''), ('omniauth', '>= 0.2.6')]

            deps = [(d.value, d.version.value) for d in dep_info]
            self.assertNotIn(('not_to_consider', ''), deps)
            for gem in gems:
                self.assertIn(gem, deps)

            source_urls = [d.url for d in dep_info]
            self.assertIn('https://gems.example.com', source_urls)
