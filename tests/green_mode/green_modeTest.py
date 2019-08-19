import operator
import os
import unittest
import yaml
from copy import deepcopy
from pathlib import Path
from textwrap import dedent
from unittest.mock import patch

from coala_quickstart.generation.SettingsClass import (
    collect_bear_settings,
)
from coala_quickstart.green_mode.Setting import (
    find_max_min_of_setting,
)
from coala_quickstart.green_mode import green_mode
from coala_quickstart.green_mode.green_mode import (
    bear_test_fun,
    check_bear_results,
    generate_complete_filename_list,
    generate_data_struct_for_sections,
    generate_green_mode_sections,
    get_kwargs,
    get_setting_type,
    global_bear_test,
    initialize_project_data,
    local_bear_test,
    run_quickstartbear,
)
from coala_quickstart.generation.Utilities import (
    append_to_contents,
    dump_yaml_to_file,
    get_yaml_contents,
)
from coala_quickstart.green_mode.QuickstartBear import (
    QuickstartBear)
from coalib.results.Result import Result
from coalib.results.SourceRange import (
    SourcePosition,
    SourceRange,
)
from coala_utils.string_processing.Core import escape
from tests.test_bears.AllKindsOfSettingsDependentBear import (
    AllKindsOfSettingsBaseBear,
)
from tests.test_bears.AnotherTestLocalDepBear import AnotherTestLocalDepBear
from tests.test_bears.TestGlobalBear import TestGlobalBear
from tests.test_bears.TestLocalBear import TestLocalBear
from tests.test_bears.TestLocalDepBear import TestLocalDepBear

settings_key = 'green_mode_infinite_value_settings'


class Test_green_mode(unittest.TestCase):

    def test_get_yaml_contents(self):
        project_data = 'example_.project_data.yaml'
        full_path = str(Path(__file__).parent / project_data)
        yaml_contents = get_yaml_contents(full_path)
        test_yaml_contents = {
            'dir_structure': ['.coafile',
                              'example_file_1',
                              {'example_folder_1': ['example_file_2',
                                                    {'example_nested_folder_1':
                                                     ['example_file_3']},
                                                    {'example_nested_folder_2':
                                                     ['example_file_4']},
                                                    'example_file_5']},
                              'example_file_6']}
        self.assertEqual(yaml_contents, test_yaml_contents)

    def test_append_to_contents_1(self):
        ret_contents = append_to_contents({}, 'key', [1, 2], settings_key)
        self.assertEqual(ret_contents, {settings_key: [{'key': [1, 2]}]})

    def test_append_to_contents_2(self):
        ret_contents = append_to_contents({settings_key: []}, 'key', [1, 2],
                                          settings_key)
        self.assertEqual(ret_contents, {settings_key: [{'key': [1, 2]}]})

    def test_append_to_contents_3(self):
        ret_contents = append_to_contents({settings_key: [{'key': [3]}]},
                                          'key', [1, 2], settings_key)
        self.assertEqual(ret_contents, {settings_key: [{'key': [3, 1, 2]}]})

    def test_append_to_contents_4(self):
        ret_contents = append_to_contents({settings_key:
                                           [{'key': [3]},
                                            {'some_other_key': [True]},
                                            'some_other_entry_in_list']},
                                          'key', [1, 2], settings_key)
        self.assertEqual(ret_contents, {settings_key:
                                        [{'key': [3, 1, 2]},
                                         {'some_other_key': [True]},
                                         'some_other_entry_in_list']})

    def test_dump_yaml_to_file(self):
        file_path = str(Path(__file__).parent.parent.parent / 'output.yanl')
        dump_yaml_to_file(file_path, ['GSoC 2018'])
        file_path = Path(file_path)
        with file_path.open() as stream:
            test_contents = yaml.load(stream)
        self.assertEqual(test_contents, ['GSoC 2018'])
        os.remove(str(file_path))

    def test_initialize_project_data(self):
        dir_path = str(Path(__file__).parent) + os.sep
        contents = initialize_project_data(dir_path, [])
        pycache_index = -1
        for index, content in enumerate(contents):
            if isinstance(content, dict):
                if '__pycache__' in content.keys():
                    pycache_index = index
                    break
        if not pycache_index == -1:
            del contents[pycache_index]
        list_indices = []
        for index, content in enumerate(contents):
            if content[-4:] == 'orig':
                list_indices.append(index)
        for i in range(0, len(list_indices)):
            del contents[list_indices[i]]
            for j in range(i + 1, len(list_indices)):
                list_indices[j] = list_indices[j] - 1
        self.assertIn(
            ['QuickstartBearTest.py', 'example_.project_data.yaml',
             'green_modeTest.py', 'filename_operationsTest.py'],
            contents)

    def test_initialize_project_data(self):
        dir_path = str(Path(__file__).parent) + os.sep
        ignore_globs = ['*pycache*', '**.pyc', '**.orig']
        final_data = initialize_project_data(dir_path, ignore_globs)
        test_final_data = ['QuickstartBearTest.py',
                           'example_.project_data.yaml',
                           'green_modeTest.py',
                           'filename_operationsTest.py',
                           'bear_settings.yaml',
                           {'test_dir': ['file_aggregatorTest.py',
                                         'test_file.py']}]
        for i in final_data:
            if not isinstance(i, dict):
                self.assertIn(i, test_final_data)
            else:
                for key in i:
                    for j in test_final_data:
                        if isinstance(j, dict):
                            if key in j:
                                to_test = j[key]
                    self.assertCountEqual(i[key], to_test)

    def test_generate_complete_filename_list(self):
        dir_path = str(Path(__file__).parent) + os.sep
        ignore_globs = ['*pycache*', '**.pyc', '**.orig']
        data = initialize_project_data(dir_path, ignore_globs)
        final_data = generate_complete_filename_list(data, dir_path[:-1])
        prefix = dir_path
        test_final_data = ['QuickstartBearTest.py',
                           'example_.project_data.yaml',
                           'bear_settings.yaml',
                           'green_modeTest.py',
                           'test_dir' + os.sep + 'file_aggregatorTest.py',
                           'filename_operationsTest.py',
                           'test_dir' + os.sep + 'test_file.py']
        test_final_data = [prefix + x for x in test_final_data]
        self.assertCountEqual(final_data, test_final_data)

    def test_find_max_min_of_setting_1(self):
        final_contents = find_max_min_of_setting('key', 1, {settings_key: []},
                                                 operator.gt)
        test_contents = {settings_key: [{'key': 1}]}
        self.assertEqual(final_contents, test_contents)

    def test_find_max_min_of_setting_2(self):
        final_contents = find_max_min_of_setting(
            'key', 1, {settings_key: [{'key': 0}]}, operator.gt)
        test_contents = {settings_key: [{'key': 1}]}
        self.assertEqual(final_contents, test_contents)

    def test_find_max_min_of_setting_3(self):
        final_contents = find_max_min_of_setting(
            'key', 1, {settings_key: [{'key': 2}]}, operator.gt)
        test_contents = {settings_key: [{'key': 2}]}
        self.assertEqual(final_contents, test_contents)

    def test_find_max_min_of_setting_4(self):
        final_contents = find_max_min_of_setting('key', 1, {settings_key: []},
                                                 operator.lt)
        test_contents = {settings_key: [{'key': 1}]}
        self.assertEqual(final_contents, test_contents)

    def test_find_max_min_of_setting_5(self):
        final_contents = find_max_min_of_setting(
            'key', 1, {settings_key: [{'key': 0}]}, operator.lt)
        test_contents = {settings_key: [{'key': 0}]}
        self.assertEqual(final_contents, test_contents)

    def test_find_max_min_of_setting_6(self):
        final_contents = find_max_min_of_setting(
            'key', 1, {settings_key: [{'key': 2}]}, operator.lt)
        test_contents = {settings_key: [{'key': 1}]}
        self.assertEqual(final_contents, test_contents)

    def test_run_quickstartbear(self):
        dir_path = str(Path(__file__).parent) + os.sep
        ignore_globs = ['*pycache*', '**.pyc', '**.orig']
        contents = initialize_project_data(dir_path, ignore_globs)
        contents = {'dir_structure': contents, settings_key: []}
        settings_key_values = [{'max_lines_per_file': 1000},  # default value
                               {'max_line_length': 80},
                               {'min_lines_per_file': 5}]
        test_contents = deepcopy(contents)
        test_contents[settings_key] = settings_key_values
        (final_contents, ignore_ranges, complete_file_dict,
         complete_filename_list) = run_quickstartbear(contents, dir_path)
        ignore_file_name = dir_path + 'test_dir' + os.sep + 'test_file.py'
        start = SourcePosition(ignore_file_name, line=3, column=1)
        stop = SourcePosition(ignore_file_name, line=4, column=20)
        self.assertEqual(test_contents, final_contents)
        # TODO: Test for the ignores too which is currently broken
        # due to the tests contained in this file have test coafile
        # which contain the ignore field which is also accounted
        # inside the ignore ranges.

    def test_run_quickstartbear_with_file_None(self):
        # Mocking the method
        QuickstartBear.execute = lambda *args, **kwargs: [None]
        dir_path = str(Path(__file__).parent) + os.sep
        contents = initialize_project_data(dir_path, [])
        contents = {'dir_structure': contents, settings_key: []}
        test_contents = deepcopy(contents)
        (final_contents, ignore_ranges, complete_file_dict,
         complete_filename_list) = run_quickstartbear(contents, dir_path)
        self.assertEqual(test_contents, final_contents)

    def test_get_setting_type(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        type_setting, val = get_setting_type(
            'key', 'GummyBear', __location__)
        self.assertEqual(type_setting, 'typeX')
        self.assertEqual(val, '')

    def test_get_kwargs_1(self):
        relevant_bears = {'test':
                          {AllKindsOfSettingsBaseBear, }}
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        dir_path = str(Path(__file__).parent) + os.sep
        ignore_globs = ['*pycache*', '**.pyc', '**.orig']
        bear_settings_obj = collect_bear_settings(relevant_bears)
        non_optional_settings = bear_settings_obj[0].non_optional_settings
        bear_settings_obj[0].optional_settings
        contents = initialize_project_data(dir_path, ignore_globs)
        contents = {'dir_structure': contents,
                    settings_key: [{'some_rubbish_setting': 'some_rubbish',
                                    'max_line_lengths': 60}]}
        kwargs = get_kwargs(non_optional_settings,
                            [AllKindsOfSettingsBaseBear],
                            contents, __location__)
        test_kwargs = {'use_bear': [True, False],
                       'max_line_lengths': [60],
                       'no_line': [1, 2]}
        self.assertEqual(kwargs, test_kwargs)

    def test_get_kwargs_2(self):
        relevant_bears = {'test':
                          {AllKindsOfSettingsBaseBear, }}
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        dir_path = str(Path(__file__).parent) + os.sep
        ignore_globs = ['*pycache*', '**.pyc', '**.orig']
        bear_settings_obj = collect_bear_settings(relevant_bears)
        bear_settings_obj[0].non_optional_settings
        optional_settings = bear_settings_obj[0].optional_settings
        contents = initialize_project_data(dir_path, ignore_globs)
        contents = {'dir_structure': contents,
                    settings_key: [{'some_rubbish_setting': 'some_rubbish',
                                    'max_line_lengths': 60}]}
        kwargs = get_kwargs(optional_settings,
                            [AllKindsOfSettingsBaseBear],
                            contents, __location__)
        test_kwargs = {'use_space': [True, False],
                       'use_tab': [True, False]}
        self.assertEqual(kwargs, test_kwargs)

    def test_check_bear_results_1(self):
        self.assertEqual(True, check_bear_results([], []))
        self.assertEqual(False, check_bear_results(['a'], []))

    def test_check_bear_results_2(self):
        start = SourcePosition('a.py', line=368, column=4)
        end = SourcePosition('a.py', line=442, column=2)
        range_object = SourceRange(start, end)
        results = [Result(affected_code=[range_object],
                          message='green_mode', origin=QuickstartBear)]

        start = SourcePosition('a.py', line=268, column=4)
        end = SourcePosition('a.py', line=542, column=2)
        ignore_object = SourceRange(start, end)
        ignore_ranges = [('+', ignore_object)]
        self.assertTrue(check_bear_results(results, ignore_ranges))

    def test_check_bear_results_3(self):
        start = SourcePosition('a.py', line=368, column=4)
        end = SourcePosition('a.py', line=442, column=2)
        range_object = SourceRange(start, end)
        results = [Result(affected_code=[range_object],
                          message='green_mode', origin=QuickstartBear)]

        start = SourcePosition('a.py', line=468, column=4)
        end = SourcePosition('a.py', line=478, column=2)
        ignore_object = SourceRange(start, end)
        ignore_ranges = [('+=', ignore_object)]
        self.assertFalse(check_bear_results(results, ignore_ranges))

    def test_bear_test_fun_1(self):
        from pyprint.ConsolePrinter import ConsolePrinter
        printer = ConsolePrinter()
        bears = {'Python': [TestLocalBear, TestGlobalBear]}
        relevant_bears = {'test':
                          {TestLocalBear, TestGlobalBear, }}
        bear_settings_obj = collect_bear_settings(relevant_bears)
        file_dict = {'A.py': {'a\n', 'b\n'}, 'C.py': {'c\n', 'd\n'}}
        dir_path = str(Path(__file__).parent) + os.sep
        contents = initialize_project_data(dir_path, [])
        file_names = ['A.py', 'C.py']
        non_op_results, unified_results = bear_test_fun(
            bears, bear_settings_obj, file_dict, [], contents,
            file_names, 5, 5, printer)
        test_non_op_results = [{TestLocalBear:
                                [{'filename': 'A.py'},
                                 {'filename': 'C.py'}]},
                               {TestGlobalBear: [{}]}]
        test_unified_results = [{TestLocalBear:
                                 [{'filename': 'A.py',
                                   'yield_results': False},
                                  {'filename': 'C.py',
                                   'yield_results': False}]},
                                {TestGlobalBear: [{'yield_results': False}]}]
        self.assertCountEqual(non_op_results[1][TestGlobalBear],
                              test_non_op_results[1][TestGlobalBear])
        self.assertCountEqual(unified_results[1][TestGlobalBear],
                              test_unified_results[1][TestGlobalBear])
        self.assertCountEqual(non_op_results[0][TestLocalBear],
                              test_non_op_results[0][TestLocalBear])
        self.assertCountEqual(unified_results[0][TestLocalBear],
                              test_unified_results[0][TestLocalBear])

    def test_bear_test_fun_2(self):
        from pyprint.ConsolePrinter import ConsolePrinter
        printer = ConsolePrinter()
        bears = {'Python': [TestLocalBear, TestGlobalBear]}
        relevant_bears = {'test':
                          {TestLocalBear, TestGlobalBear, }}
        bear_settings_obj = collect_bear_settings(relevant_bears)
        file_dict = {'A.py': {'a\n', 'b\n'}, 'C.py': {'c\n', 'd\n'}}
        dir_path = str(Path(__file__).parent) + os.sep
        contents = initialize_project_data(dir_path, [])
        file_names = ['A.py', 'C.py']
        non_op_results, unified_results = bear_test_fun(
            bears, bear_settings_obj, file_dict, [], contents,
            file_names, 1, 1, printer)
        test_non_op_results = [{TestLocalBear:
                                [{'filename': 'A.py'},
                                 {'filename': 'C.py'}]},
                               {TestGlobalBear: [{}]}]
        self.assertCountEqual(non_op_results[1][TestGlobalBear],
                              test_non_op_results[1][TestGlobalBear])
        self.assertCountEqual(non_op_results[0][TestLocalBear],
                              test_non_op_results[0][TestLocalBear])
        self.assertCountEqual(unified_results, [None, None])

    def test_bear_test_fun_3(self):
        from pyprint.ConsolePrinter import ConsolePrinter
        printer = ConsolePrinter()
        bears = {'Python': [TestLocalDepBear]}
        relevant_bears = {'test':
                          {TestLocalDepBear}}
        bear_settings_obj = collect_bear_settings(relevant_bears)
        file_dict = {'A.py': {'a\n', 'b\n'}, 'C.py': {'c\n', 'd\n'}}
        dir_path = str(Path(__file__).parent) + os.sep
        contents = initialize_project_data(dir_path, [])
        file_names = ['A.py', 'C.py']
        non_op_results, unified_results = bear_test_fun(
            bears, bear_settings_obj, file_dict, [], contents,
            file_names, 1, 1, printer)
        print('nonop:', non_op_results)
        print('op:', unified_results)
        test_results = [{TestLocalDepBear: []}]
        self.assertCountEqual(non_op_results[0][TestLocalDepBear],
                              test_results[0][TestLocalDepBear])
        self.assertCountEqual(unified_results, [None])

    def test_bear_test_fun_4(self):
        from pyprint.ConsolePrinter import ConsolePrinter
        printer = ConsolePrinter()
        bears = {'Python': [AnotherTestLocalDepBear]}
        relevant_bears = {'test':
                          {AnotherTestLocalDepBear}}
        bear_settings_obj = collect_bear_settings(relevant_bears)
        file_dict = {'A.py': {'a\n', 'b\n'}, 'C.py': {'c\n', 'd\n'}}
        dir_path = str(Path(__file__).parent) + os.sep
        contents = initialize_project_data(dir_path, [])
        file_names = ['A.py', 'C.py']
        non_op_results, unified_results = bear_test_fun(
            bears, bear_settings_obj, file_dict, [], contents,
            file_names, 1, 1, printer)
        print('nonop:', non_op_results)
        print('op:', unified_results)
        test_results = [{AnotherTestLocalDepBear: [{'filename': 'A.py'},
                                                   {'filename': 'C.py'}]}]
        self.assertCountEqual(non_op_results[0][AnotherTestLocalDepBear],
                              test_results[0][AnotherTestLocalDepBear])
        self.assertCountEqual(unified_results, [None])

    def test_write_coafile(self):
        from pyprint.ConsolePrinter import ConsolePrinter
        printer = ConsolePrinter()
        input_ = [{TestLocalBear: [{'filename': 'a.py', 'some_setting': 3},
                                   {'filename': 'b.py', 'some_setting': 3},
                                   {'filename': 'c.py', 'some_setting': 4},
                                   {'filename': 'd.py',
                                    'some_other_setting': 'x'}]},
                  None]
        data_struct = generate_data_struct_for_sections(input_)
        test_data_struct = {TestLocalBear: [[{'filename': ['a.py', 'b.py'],
                                              'some_setting': 3},
                                             {'filename': ['c.py'],
                                              'some_setting': 4}],
                                            [{'some_other_setting': 'x',
                                              'filename': ['d.py']}]]}
        self.assertEqual(data_struct, test_data_struct)
        project_files = ['a.py', 'b.py', 'c.py', 'd.py']
        coafile = '.coafile.green'
        toml_file = '.coafile.green.toml'
        full_path = str(Path(__file__).parent.parent.parent)
        full_path_coafile = str(Path(__file__).parent.parent.parent / coafile)
        full_path_toml = str(Path(__file__).parent.parent.parent / toml_file)

        with patch('os.walk') as mockwalk:
            mockwalk.return_val = mockwalk.return_value = [
                ('', (), ('a.py', 'b.py', 'c.py', 'd.py')), ]
            generate_green_mode_sections(data_struct, full_path,
                                         project_files, ['x'], False,
                                         printer)
            generate_green_mode_sections(data_struct, full_path,
                                         project_files, ['x'], True,
                                         printer)
        contents = ""

        with open(full_path_coafile) as f:
            for line in f.readlines():
                contents += line

        contents_toml = ""
        with open(full_path_toml) as f:
            for line in f.readlines():
                contents_toml += line

        full_path_glob = escape(full_path + os.sep + '**', '\\')

        test_contents = dedent("""
            [all]
            ignore = x

            [all.TestLocalBear1]
            ignore += a.py, b.py, c.py, d.py
            bears = TestLocalBear
            some_setting = 3
            files = a.py, b.py, {full_path_glob}

            [all.TestLocalBear2]
            ignore += a.py, b.py, c.py, d.py
            files = c.py, {full_path_glob}
            bears = TestLocalBear
            some_setting = 4

            [all.TestLocalBear3]
            ignore += a.py, b.py, c.py, d.py
            files = d.py, {full_path_glob}
            bears = TestLocalBear
            some_other_setting = x""").format(
            full_path_glob=full_path_glob)

        test_contents_toml = dedent("""
            [all]
            ignore = "x"

            [TestLocalBear1]
            some_setting = 3
            bears = "TestLocalBear"
            ignore = ["a.py", "b.py", "c.py", "d.py"]
            files = ["a.py", "b.py", \"{full_path_glob}\"]
            inherits = ["all"]
            appends.all = ["ignore"]

            [TestLocalBear2]
            some_setting = 4
            bears = "TestLocalBear"
            ignore = ["a.py", "b.py", "c.py", "d.py"]
            files = ["c.py", \"{full_path_glob}\"]
            inherits = ["all"]
            appends.all = ["ignore"]

            [TestLocalBear3]
            some_other_setting = "x"
            bears = "TestLocalBear"
            ignore = ["a.py", "b.py", "c.py", "d.py"]
            files = ["d.py", \"{full_path_glob}\"]
            inherits = ["all"]
            appends.all = ["ignore"]""").format(
            full_path_glob=full_path_glob)

        # Since the order of settings within a seciton is volatile.
        for line in test_contents.split('\n'):
            if line == 'ignore = x':
                continue  # Since the path depends on the test directory
            self.assertIn(line, [i.strip('\\').replace('\\\\C', 'C')
                                 for i in contents.split('\n')])

        for line in test_contents_toml.split('\n'):
            if line == 'ignore = "x"':
                continue  # Since the path depends on the test directory
            self.assertIn(line, [i.strip('\\').replace('\\\\C', 'C')
                                 for i in contents_toml.split('\n')])

        with patch('os.walk') as mockwalk:
            mockwalk.return_val = mockwalk.return_value = [
                ('', (), ('a.py', 'b.py', 'c.py', 'd.py')), ]
            generate_green_mode_sections(data_struct, full_path,
                                         project_files, [], False,
                                         printer)

            generate_green_mode_sections(data_struct, full_path,
                                         project_files, ['x'], True,
                                         printer)
        contents = ""

        with open(full_path_coafile) as f:
            for line in f.readlines():
                contents += line

        contents_toml = ""
        with open(full_path_toml) as f:
            for line in f.readlines():
                contents_toml += line

        # TODO: remove the prefix 'all.' from section names when section
        # all is not present which only happends when the ignore field
        # is empty.
        test_contents = dedent("""
            [all.TestLocalBear1]
            ignore = a.py, b.py, c.py, d.py
            files = a.py, b.py, {full_path_glob}
            bears = TestLocalBear
            some_setting = 3

            [all.TestLocalBear2]
            ignore = a.py, b.py, c.py, d.py
            files = c.py, {full_path_glob}
            bears = TestLocalBear
            some_setting = 4

            [all.TestLocalBear3]
            ignore = a.py, b.py, c.py, d.py
            files = d.py, {full_path_glob}
            bears = TestLocalBear
            some_other_setting = x""").format(
            full_path_glob=full_path_glob)

        test_contents_toml = dedent("""
        [all]
        ignore = "x"

        [TestLocalBear1]
        some_setting = 3
        bears = "TestLocalBear"
        ignore = ["a.py", "b.py", "c.py", "d.py"]
        files = ["a.py", "b.py", \"{full_path_glob}\"]
        inherits = ["all"]
        appends.all = ["ignore"]

        [TestLocalBear2]
        some_setting = 4
        bears = "TestLocalBear"
        ignore = ["a.py", "b.py", "c.py", "d.py"]
        files = ["c.py", \"{full_path_glob}\"]
        inherits = ["all"]
        appends.all = ["ignore"]

        [TestLocalBear3]
        some_other_setting = "x"
        bears = "TestLocalBear"
        ignore = ["a.py", "b.py", "c.py", "d.py"]
        files = ["d.py", \"{full_path_glob}\"]
        inherits = ["all"]
        appends.all = ["ignore"]""").format(
            full_path_glob=full_path_glob)

        # Since the order of settings within a seciton is volatile.
        for line in test_contents.split('\n'):
            if line == 'ignore = x':
                continue  # Since the path depends on the test directory
            self.assertIn(line, [i.strip('\\').replace('\\\\C', 'C')
                                 for i in contents.split('\n')])

        for line in test_contents_toml.split('\n'):
            if line == 'ignore = "x"':
                continue  # Since the path depends on the test directory
            self.assertIn(line, [i.strip('\\').replace('\\\\C', 'C')
                                 for i in contents_toml.split('\n')])

        test_data_struct = {TestLocalBear: [[{'filename': ['a.py', 'b.py'],
                                              'some_setting': 3},
                                             {'filename': ['c.py'],
                                              'some_setting': 4},
                                             {'filename': ['a.py', 'b.py'],
                                              'some_setting': 4}],
                                            [{'some_other_setting': 'x',
                                              'filename': ['d.py']}],
                                            []]}
        with patch('os.walk') as mockwalk:
            mockwalk.return_val = mockwalk.return_value = [
                ('', (), ('a.py', 'b.py', 'c.py', 'd.py')), ]
            generate_green_mode_sections(test_data_struct, full_path,
                                         project_files, [], False,
                                         printer)
            generate_green_mode_sections(test_data_struct, full_path,
                                         project_files, [], True,
                                         printer)
        contents = ""

        with open(full_path_coafile) as f:
            for line in f.readlines():
                contents += line

        contents_toml = ""
        with open(full_path_toml) as f:
            for line in f.readlines():
                contents_toml += line

        # TODO: section name enumerations should not skip integers.
        test_contents = dedent("""
            [all.TestLocalBear1]
            ignore = a.py, b.py, c.py, d.py
            files = a.py, b.py, {full_path_glob}
            bears = TestLocalBear
            some_setting = 3

            [all.TestLocalBear2]
            ignore = a.py, b.py, c.py, d.py
            files = c.py, {full_path_glob}
            bears = TestLocalBear
            some_setting = 4

            [all.TestLocalBear4]
            ignore = a.py, b.py, c.py, d.py
            files = d.py, {full_path_glob}
            bears = TestLocalBear
            some_other_setting = x""").format(
            full_path_glob=full_path_glob)

        test_contents_toml = dedent("""
        [TestLocalBear1]
        ignore = ["a.py", "b.py", "c.py", "d.py"]
        files = ["a.py", "b.py", \"{full_path_glob}\"]
        bears = "TestLocalBear"
        some_setting = 3
        inherits = ["all"]

        [TestLocalBear2]
        ignore = ["a.py", "b.py", "c.py", "d.py"]
        files = ["c.py", \"{full_path_glob}\"]
        bears = "TestLocalBear"
        some_setting = 4
        inherits = ["all"]

        [TestLocalBear4]
        some_other_setting = "x"
        bears = "TestLocalBear"
        ignore = ["a.py", "b.py", "c.py", "d.py"]
        files = ["d.py", \"{full_path_glob}\"]
        inherits = ["all"]""").format(
            full_path_glob=full_path_glob)

        # Since the order of settings within a seciton is volatile.
        for line in test_contents.split('\n'):
            if line == 'ignore = x':
                continue  # Since the path depends on the test directory
            self.assertIn(line, [i.strip('\\').replace('\\\\C', 'C')
                                 for i in contents.split('\n')])

        for line in test_contents_toml.split('\n'):
            if line == 'ignore = x':
                continue  # Since the path depends on the test directory
            self.assertIn(line, [i.strip('\\').replace('\\\\C', 'C')
                                 for i in contents_toml.split('\n')])


class MultiProcessingTest(unittest.TestCase):

    def setUp(self):
        self.orig_cpus = green_mode._RESERVE_CPUS

    def tearDown(self):
        green_mode._RESERVE_CPUS = self.orig_cpus

    def test_no_pool(self):
        with self.assertRaises(TypeError):
            green_mode._create_mp_pool(None)
        with self.assertRaises(ValueError):
            self.assertIsNone(green_mode._create_mp_pool(-1))
        self.assertIsNone(green_mode._create_mp_pool(1))

    def test_reserve_cpus(self):
        green_mode._RESERVE_CPUS = 1
        with patch('multiprocessing.cpu_count', return_value=1):
            self.assertIsNone(green_mode._create_mp_pool(0))
        green_mode._RESERVE_CPUS = 2
        with patch('multiprocessing.cpu_count', return_value=2):
            self.assertIsNone(green_mode._create_mp_pool(0))

        green_mode._RESERVE_CPUS = 1
        with patch('multiprocessing.cpu_count', return_value=2):
            self.assertIsNotNone(green_mode._create_mp_pool(0))

        green_mode._RESERVE_CPUS = 1
        with patch('multiprocessing.cpu_count', return_value=2):
            self.assertIsNotNone(green_mode._create_mp_pool(2))

        green_mode._RESERVE_CPUS = 1
        with patch('multiprocessing.cpu_count', return_value=10):
            self.assertIsNotNone(green_mode._create_mp_pool(2))

    def test_ci_pool_min(self):
        if not os.environ.get('CI'):
            return

        if green_mode._DISABLE_MP:
            with patch('multiprocessing.cpu_count', return_value=3):
                self.assertIsNone(green_mode._create_mp_pool(0))
            with patch('multiprocessing.cpu_count', return_value=100):
                self.assertIsNone(green_mode._create_mp_pool(0))
        elif green_mode._RESERVE_CPUS == 2:
            with patch('multiprocessing.cpu_count', return_value=2):
                self.assertIsNone(green_mode._create_mp_pool(0))
            with patch('multiprocessing.cpu_count', return_value=3):
                self.assertIsNotNone(green_mode._create_mp_pool(0))
        else:
            with patch('multiprocessing.cpu_count', return_value=2):
                self.assertIsNotNone(green_mode._create_mp_pool(2))
                self.assertIsNotNone(green_mode._create_mp_pool(0))
