import os
import sys
import unittest
from copy import deepcopy


from pyprint.ConsolePrinter import ConsolePrinter
from coala_utils.ContextManagers import (
    retrieve_stdout, simulate_console_inputs)
from coala_quickstart.generation.Bears import (
    filter_relevant_bears, print_relevant_bears)
from coala_quickstart.coala_quickstart import main
from coala_quickstart.coala_quickstart import _get_arg_parser
from coala_quickstart.Constants import (
    IMPORTANT_BEAR_LIST, ALL_CAPABILITIES)
from coala_quickstart.generation.InfoCollector import collect_info
from tests.TestUtilities import bear_test_module, generate_files


editorconfig = """
[*]
indent_style = tab
end_of_line = lf
insert_final_newline = true
charset = utf-8
trim_trailing_whitespace = true
indent_size = 4
"""

package_json = """
{
  "name": "awesome-packages",
  "dependencies": {
    "babel-eslint": "~8",
    "eslint": "~3",
    "eslint-plugin-import": "~2",
    "bootlint": "~0",
    "csslint": "~1",
    "happiness": "~10",
    "jshint": "~2",
    "some_linter": "~2"
    }
}
"""

gemfile = """
source 'https://rubygems.org'

gem "csvlint"
gem "reek"
gem "scss_lint"
gem "sqlint"
"""

gruntfile = """
'use strict';

/* jshint node: true */
module.exports = function ( grunt ) {
    grunt.loadNpmTasks( 'grunt-contrib-csslint' );
    grunt.loadNpmTasks( 'grunt-contrib-jshint' );
    grunt.loadNpmTasks( 'grunt-contrib-some_lint' );
    // Project configuration.
    grunt.initConfig( {
        jshint: {
            options: {
                jshintrc: true
            },
            all: [
                '*.js',
                'src/*.js',
                'rules/**/*.js',
                'test/**/*.js'
            ]
        },
        csslint: {
            all: [
                'css/**/*.css'
            ]
        },
        some_lint: {
            ignore: [
                'foo/**.bar'
            ]
        },
        watch: {
            files: [
                '.{csslintrc,jshintignore,jshintrc}',
                '<%= jshint.all %>',
                '<%= csslint.all %>'
            ],
            tasks: 'lint'
        }
    } );

    // Default task.
    grunt.registerTask( 'lint', [
        'jshint', 'csslint', 'some_lint'] );
    grunt.registerTask( 'default', [ 'lint', 'test' ] );
};
"""

context_filenames = [".editorconfig", "package.json", "Gemfile", "Gruntfile.js"]
context_file_contents = [editorconfig, package_json, gemfile, gruntfile]


class TestBears(unittest.TestCase):

    def setUp(self):
        self.project_dir = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "project_dir")
        os.makedirs(self.project_dir, exist_ok=True)
        self.arg_parser = _get_arg_parser()
        self.printer = ConsolePrinter()
        self.log_printer = None
        self.old_argv = deepcopy(sys.argv)
        del sys.argv[1:]

    def tearDown(self):
        sys.argv = self.old_argv

    def test_filter_relevant_bears_simple(self):
        res = filter_relevant_bears([('Python', 70), ('C', 20)],
                                    self.printer,
                                    self.arg_parser,
                                    {})
        self.assertIn("C", res)
        self.assertIn("Python", res)
        self.assertTrue(len(res["C"]) > 0)
        self.assertTrue(len(res["Python"]) > 0)

    def test_filter_relevant_bears_green_mode(self):
        from argparse import Namespace
        from coalib.settings.ConfigurationGathering import (
            get_filtered_bears)
        self.arg_parser.parse_args = unittest.mock.MagicMock(
            return_value=Namespace(green_mode=True))
        res = filter_relevant_bears([('Python', 70), ('C', 20)],
                                    self.printer,
                                    self.arg_parser,
                                    {})
        all_bears = get_filtered_bears(['Python', 'C'])[0]
        bears = all_bears['all']
        bears += all_bears['all.python']
        important_bears = []

        for bear_set in list(IMPORTANT_BEAR_LIST.values()):
            for bear in bear_set:
                important_bears.append(bear)

        bear_objs = []
        for bear in bears:
            if bear.__name__ in important_bears:
                bear_objs.append(bear)

        bear_obj_dict = dict()
        for key in ['Python', 'C', 'All']:
            bear_obj_dict[key] = set()
            for bear in IMPORTANT_BEAR_LIST[key]:
                bear_obj_dict[key].update([x for x in bear_objs if (
                    x.__name__ == bear)])

        self.maxDiff = None
        self.assertEqual(res, bear_obj_dict)

    def test_filter_relevant_bears_with_extracted_info(self):
        # results without extracted information
        languages = [('JavaScript', 70), ('Ruby', 20)]
        res_1 = filter_relevant_bears(
            languages, self.printer, self.arg_parser, {})
        for lang, _ in languages:
            self.assertIn(lang, res_1)
            self.assertTrue(len(res_1[lang]) > 0)

        # results with extracted information
        res_2 = []

        # FIXME: Create and use Test bears with
        # ``TestUtilites.bear_test_module`` instead of running
        # tests on actual bears in coala-bears package.
        with generate_files(context_filenames,
                            context_file_contents,
                            self.project_dir) as gen_files:
            extracted_info = collect_info(self.project_dir)
            res_2 = filter_relevant_bears(languages,
                                          self.printer,
                                          self.arg_parser,
                                          extracted_info)
            for lang, _ in languages:
                self.assertIn(lang, res_2)
                self.assertTrue(len(res_2[lang]) > 0)

        # Comparing both the scenarios

        # The following dict has list of bears that have their requirements
        # caputred by `ProjectDependencyInfo` from the dependency files
        # but are not part of the `IMPORTANT_BEARS_LIST` in Constants.py
        additional_bears_by_lang = {
            "JavaScript": ["ESLintBear", "HappinessLintBear"],
            "Ruby": [],
            "All": []
        }
        for lang in res_1:
            additional_bears = [bear.name for bear in res_2[lang]
                                if bear not in res_1[lang]]
            for bear in additional_bears_by_lang[lang]:
                self.assertIn(bear, additional_bears)

    def test_filter_relevant_bears_with_non_optional_settings(self):
        sys.argv.append('--no-filter-by-capabilities')
        with bear_test_module():
            languages = []
            res_1 = filter_relevant_bears(
                languages, self.printer, self.arg_parser, {})

            # results with extracted information
            res_2 = []
            with generate_files(context_filenames,
                                context_file_contents,
                                self.project_dir):
                with simulate_console_inputs("Yes") as generator:
                    extracted_info = collect_info(self.project_dir)
                    res_2 = filter_relevant_bears(languages,
                                                  self.printer,
                                                  self.arg_parser,
                                                  extracted_info)
                    self.assertEqual(generator.last_input, 0)

            # Comparing both the scenarios
            additional_bears_by_lang = {
                "All": ["NonOptionalSettingBear"]
            }
            for lang in res_1:
                additional_bears = [bear.name for bear in res_2[lang]
                                    if bear not in res_1[lang]]
                for bear in additional_bears_by_lang[lang]:
                    self.assertIn(bear, additional_bears)

            # Simulating the situation when user rejects the bear
            res_2 = []
            with generate_files(context_filenames,
                                context_file_contents,
                                self.project_dir):
                with simulate_console_inputs(
                        "Some random text which will not be accepted",
                        "No") as generator:
                    extracted_info = collect_info(self.project_dir)
                    res_2 = filter_relevant_bears(languages,
                                                  self.printer,
                                                  self.arg_parser,
                                                  extracted_info)
                    self.assertEqual(generator.last_input, 1)

            # This time there will be no additional bears
            additional_bears_by_lang = {
                "All": []
            }
            for lang in res_1:
                additional_bears = [bear.name for bear in res_2[lang]
                                    if bear not in res_1[lang]]
                for bear in additional_bears_by_lang[lang]:
                    self.assertIn(bear, additional_bears)

    def test_filter_relevant_bears_with_capabilities(self):
        # Clear the IMPORTANT_BEARS_LIST
        import coala_quickstart.generation.Bears as Bears
        Bears.IMPORTANT_BEARS_LIST = {}

        with bear_test_module():
            languages = []
            capability_to_select = 'Smell'
            cap_number = (
                sorted(ALL_CAPABILITIES).index(capability_to_select) + 1)
            res = []
            with simulate_console_inputs('1000', str(cap_number)) as generator:
                res = filter_relevant_bears(languages,
                                            self.printer,
                                            self.arg_parser,
                                            {})
                # 1000 was not a valid option, so there will be two prompts
                self.assertEqual(generator.last_input, 1)

            expected_results = {
                "All": set(["SmellCapabilityBear"])
            }
            for lang, lang_bears in expected_results.items():
                for bear in lang_bears:
                    res_bears = [b.name for b in res[lang]]
                    self.assertIn(bear, res_bears)

    def test_filter_relevant_bears_gruntfile_present(self):
        # Reset the IMPORTANT_BEARS_LIST
        import coala_quickstart.generation.Bears as Bears
        Bears.IMPORTANT_BEARS_LIST = {
            "JavaScript": "DoesNotExistBear",
            "Python": "DoesNotExistAsWellBear"
        }

        sys.argv.append('--no-filter-by-capabilities')

        with bear_test_module():
            languages = [('JavaScript', 70), ('Python', 20)]
            res = {}
            with generate_files(["Gruntfile.js"],
                                [gruntfile],
                                self.project_dir) as gen_files:
                extracted_info = collect_info(self.project_dir)
                res = filter_relevant_bears(languages,
                                            self.printer,
                                            self.arg_parser,
                                            extracted_info)
            expected_results = {
                "JavaScript": set(["SomeLinterBear"]),
            }
            for lang, lang_bears in expected_results.items():
                for bear in lang_bears:
                    res_bears = [b.name for b in res[lang]]
                    self.assertIn(bear, res_bears)

    def test_print_relevant_bears(self):
        with retrieve_stdout() as custom_stdout:
            print_relevant_bears(self.printer, filter_relevant_bears(
                [('Python', 70), ('Unknown', 30)], self.printer,
                self.arg_parser, {}))
            self.assertIn("PycodestyleBear", custom_stdout.getvalue())

    def test_bears_allow_incomplete_sections_mode(self):
        sys.argv.append('--ci')
        sys.argv.append('--allow-incomplete-sections')
        orig_cwd = os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        os.chdir("bears_ci_testfiles")
        with retrieve_stdout() as custom_stdout:
            main()
            self.assertNotIn("usable",
                             custom_stdout.getvalue())
        os.remove('.coafile')
        os.chdir(orig_cwd)

    def test_bears_ci_mode(self):
        sys.argv.append('--ci')
        orig_cwd = os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        os.chdir("bears_ci_testfiles")
        with retrieve_stdout() as custom_stdout:
            main()
            self.assertIn("usable",
                          custom_stdout.getvalue())
        os.remove('.coafile')
        os.chdir(orig_cwd)

    def test_bears_no_filter_by_capability_mode(self):
        languages = []
        with bear_test_module():
            # Results without filtering
            sys.argv.append('--no-filter-by-capabilities')
            res = []
            with simulate_console_inputs() as generator:
                res = filter_relevant_bears(languages,
                                            self.printer,
                                            self.arg_parser,
                                            {})
                self.assertEqual(generator.last_input, -1)
            self.assertEqual(res, {"All": set()})

    def test_filter_bears_ci_mode(self):
        sys.argv.append('--ci')
        with bear_test_module():
            languages = []
            res_1 = filter_relevant_bears(
                languages, self.printer, self.arg_parser, {})

            res_2 = []
            with generate_files(context_filenames,
                                context_file_contents,
                                self.project_dir):
                with simulate_console_inputs("Yes") as generator:
                    extracted_info = collect_info(self.project_dir)
                    res_2 = filter_relevant_bears(languages,
                                                  self.printer,
                                                  self.arg_parser,
                                                  extracted_info)
                    # Make sure there was no prompt
                    self.assertEqual(generator.last_input, -1)

            # The NonOptionalSettingBear is not selected due to non-optional
            # setting value in non-interactive mode.
            additional_bears_by_lang = {
                "All": []
            }
            for lang in res_1:
                additional_bears = [bear.name for bear in res_2[lang]
                                    if bear not in res_1[lang]]
                for bear in additional_bears_by_lang[lang]:
                    self.assertIn(bear, additional_bears)

    def test_print_coala_quickstart_version_short(self):
        sys.argv.append('-v')
        with retrieve_stdout() as custom_stdout:
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEquals('0.4.0\n', custom_stdout.getvalue())

    def test_print_coala_quickstart_version_long(self):
        sys.argv.append('--version')
        with retrieve_stdout() as custom_stdout:
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEquals('0.4.0\n', custom_stdout.getvalue())
