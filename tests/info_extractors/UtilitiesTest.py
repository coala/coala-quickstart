import unittest

from coala_quickstart.info_extractors import Utilities


class UtititiesTest(unittest.TestCase):

    def setUp(self):
        self.simple_dict = {
            'key1': 'value1',
            'key2': 'value2'
        }
        self.nested_dict = {
            'key1': {
                'key1.1': 'value1.1'
            }
        }
        self.nested_dict_with_list = {
            'key1': {
                'key1.1': [
                    {
                        'key_a': 'value_a'
                    },
                    {
                        'key_b': [
                            {
                                'key_b_1': 'value_b_1'
                                }]
                    }]
            }
        }
        self.nested_list_with_dict = [
            {
                'key1': 'value1',
                'key2': 'value2'
            },
            {
                'key3': 'value3',
                'key4': 'value4'
            }
        ]
        self.dict_with_repeated_structure = {
            'key1': {
                'key1.1': 'value1.1'
            },
            'key2': {
                'key1.1': 'value1.1',
                'key2.1': 'value2.1'
            }
        }

    def test_search_object_recursively(self):
        uut = Utilities.search_object_recursively

        def assert_value_and_path(search_obj,
                                  search_key,
                                  search_value,
                                  expected_results,
                                  expected_paths):
            search_results = uut(search_obj, search_key, search_value)
            for obj, path in zip(expected_results, expected_paths):
                expected_result = {
                    'object': obj,
                    'path': path
                }
                self.assertIn(expected_result, search_results)

        assert_value_and_path(
            self.simple_dict, 'key1', None, ['value1'], [('key1',)])

        assert_value_and_path(self.simple_dict,
                              'key1',
                              'value1',
                              [{
                                 'key1': 'value1',
                                 'key2': 'value2'
                              }],
                              [('key1',)])

        assert_value_and_path(self.nested_dict,
                              'key1.1',
                              None,
                              ['value1.1'],
                              [('key1', 'key1.1')])

        assert_value_and_path(self.nested_dict,
                              'key1.1',
                              'value1.1',
                              [{
                                  'key1.1': 'value1.1'
                              }],
                              [('key1', 'key1.1')])

        assert_value_and_path(self.nested_dict_with_list,
                              'key_b_1',
                              None,
                              ['value_b_1'],
                              [('key1', 'key1.1', 1, 'key_b', 0, 'key_b_1')])

        assert_value_and_path(self.nested_dict_with_list,
                              'key_b_1',
                              'value_b_1',
                              [{
                                  'key_b_1': 'value_b_1'
                              }],
                              [('key1', 'key1.1', 1, 'key_b', 0, 'key_b_1')])

        assert_value_and_path(self.nested_list_with_dict,
                              'key3',
                              None,
                              ['value3'],
                              [(1, 'key3')])

        assert_value_and_path(self.nested_list_with_dict,
                              'key3',
                              'value3',
                              [{
                                  'key3': 'value3',
                                  'key4': 'value4'
                              }],
                              [(1, 'key3')])

        assert_value_and_path(self.dict_with_repeated_structure,
                              'key1.1',
                              None,
                              ['value1.1', 'value1.1'],
                              [('key1', 'key1.1'), ('key2', 'key1.1')])

        assert_value_and_path(self.dict_with_repeated_structure,
                              'key1.1',
                              'value1.1',
                              [
                                {
                                    'key1.1': 'value1.1',
                                    'key2.1': 'value2.1'
                                },
                                {
                                    'key1.1': 'value1.1',
                                }
                              ],
                              [('key2', 'key1.1'), ('key1', 'key1.1')])
