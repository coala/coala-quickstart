import fnmatch
import itertools
import operator
import os
import sys
from collections import OrderedDict
from copy import deepcopy
from pathlib import Path

from coala_quickstart.generation.Utilities import (
    contained_in,
    get_all_args,
    get_extensions,
    get_yaml_contents,
    split_by_language,
)

from coala_quickstart.green_mode.file_aggregator import (
    aggregate_files,
)
from coala_quickstart.green_mode.Setting import (
    find_max_min_of_setting,
)
from coala_quickstart.generation.Settings import (
    generate_ignore_field,
)
from coala_quickstart.green_mode.QuickstartBear import (
    QuickstartBear,
)
from coala_utils.string_processing.Core import (
    escape,
)
from coalib.bears.GlobalBear import GlobalBear
from coalib.output.ConfWriter import ConfWriter
from coalib.output.ConfigConverter import ConfigConverter
from coalib.processes.Processing import (
    get_file_dict,
    yield_ignore_ranges,
)
from coalib.settings.Section import Section

settings_key = 'green_mode_infinite_value_settings'
_CI_PYTEST_ACTIVE = os.environ.get('CI') and os.environ.get('PYTEST')
_PYTHON_VERSION_MINOR = sys.version_info[0:2]
_RESERVE_CPUS = 1
# FIXME: Multiprocessing not working on windows.
# Also Python 3.5 fails even with _RESERVE_CPUS set to 2
_DISABLE_MP = os.name == 'nt' or _PYTHON_VERSION_MINOR == (3, 5)

if _CI_PYTEST_ACTIVE:  # pragma: no cover
    if _DISABLE_MP:
        _RESERVE_CPUS = sys.maxsize


def initialize_project_data(dir, ignore_globs):
    """
    Generates the values for the key 'dir_structure'
    for PROJECT_DATA which is directories as
    dicts with key name as dir names and value as
    list of files or nested dict of dirs.
    :param dir:
        The directory for which to add the directory structure
        and files.
    :param ignore_globs:
        The globs of files to ignore from writing to the
        'PROJECT_DATA'.
    :return:
        The python object that was written as YAML data
        to PROJECT_DATA.
    """
    files_dirs = os.listdir(dir)
    # files_dirs holds names of both files and dirs.
    dir_name = dir[dir.rfind(os.sep) + 1:]
    final_data = []

    for i in files_dirs:
        to_continue = False
        for glob in ignore_globs:
            if fnmatch.fnmatch(dir + i, glob):
                to_continue = True
        if to_continue is True:
            continue
        if os.path.isfile(dir + i):
            final_data.append(i)
        else:
            look_into_dir = dir + i + os.sep
            data = initialize_project_data(look_into_dir,
                                           ignore_globs)
            final_data.append({i: data})
    return final_data


def generate_complete_filename_list(contents, project_dir):
    """
    Generates only a list of files with complete file
    paths from the 'dir_structure' key of PROJECT_DATA.
    :param contents:
        The python object which contains the already parsed
        directories and files.
    :param project_dir:
        The current directory from which to generate the list
        of files and directories within itself.
    :return:
        List of files or nested lists of directories and the
        structures within it to be appended to the contents
        from where the function is called.
    """
    prefix = project_dir + os.sep
    file_names_list = []
    for item in contents:
        if not isinstance(item, dict):
            file_names_list.append(prefix + item)
        else:
            file_names_list += generate_complete_filename_list(
                item[next(iter(item))], prefix + next(iter(item)))
    return file_names_list


def run_quickstartbear(contents, project_dir):
    """
    Runs the QuickstartBear which pareses the file_dict
    to get the exact value of some settings which can attain
    any infinite amount of values.
    :param contents:
        The python object written to 'PROJECT_DATA' which
        contains the directory structure and values of some
        settings which can attain an infinite set of values.
    :param project_dir:
        The project directory from which to get the files for the
        QuickstartBear to run.
    :return:
        - An updated contents value after guessing values of certain
          settings.
        - Collection of SourceRange objects indicating the parts of
          code to ignore.
        - The complete file dict contains file names as keys and file
          contents as values to those keys.
        - The complete file name list from the project directory and sub
          directories.
    """
    section = Section('green_mode')
    quickstartbear_obj = QuickstartBear(section, None)

    complete_filename_list = generate_complete_filename_list(
        contents['dir_structure'], project_dir)
    complete_file_dict = get_file_dict(complete_filename_list,
                                       allow_raw_files=True)
    ignore_ranges = list(yield_ignore_ranges(complete_file_dict))
    find_max = ['max_lines_per_file', 'max_line_length']
    find_min = ['min_lines_per_file']
    for key in complete_file_dict:
        return_val = quickstartbear_obj.execute(
            filename=key, file=complete_file_dict[key])
        return_val = return_val[0]
        # eg. return_val = {'setting_name': value, ...}
        if return_val is not None:
            for setting in find_max:
                contents = find_max_min_of_setting(
                    setting, return_val[setting], contents,
                    operator.gt)

            for setting in find_min:
                contents = find_max_min_of_setting(
                    setting, return_val[setting], contents,
                    operator.lt)

    bear_settings = get_yaml_contents(str(
        Path(__file__).parent / 'bear_settings.yaml'))['type2']
    full_dict = {}

    for small_dict in bear_settings.values():
        full_dict.update(small_dict)

    resort_to_default_settings = deepcopy(find_max)
    resort_to_default_settings += find_min

    for setting_name in resort_to_default_settings:
        default_val = full_dict[setting_name]
        insert_index = -1
        for index, dict_ in enumerate(contents[settings_key]):
            if setting_name in dict_:
                current_val = dict_[setting_name]
                insert_index = index
                break
        if 'current_val' in locals() and current_val < default_val:
            contents[settings_key][insert_index][setting_name] = default_val

    return (contents, ignore_ranges, complete_file_dict,
            complete_filename_list)


def get_setting_type(setting, bear, dir=None):
    """
    Retrieves the type of setting according to cEP0022.md
    and seperates the other settings from generation/SettingsClass
    into type2, type3, type4 or unguessable at the moment based on
    the data in bear_settings.yaml.
    :param setting:
        The setting name.
    :param bear:
        The bear class to which the setting belongs.
    :param dir:
        The directory where to look for `bear_settings.yaml`, defaults
        to the `green_mode` directory.
    :return:
        - The type of setting according to bear_settings.yaml.
        - The list of acceptable values in case of type3 setting
          or the value guessed by the QuickstartBear which fits
          the project or the default value in case of unguessable
          settings.
    """
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__))) if (
            dir is None) else dir
    bear_settings = get_yaml_contents(os.path.join(
        __location__, 'bear_settings.yaml'))
    for type_setting in bear_settings:
        for bear_names in bear_settings[type_setting]:
            if bear_names in str(bear):
                if setting in bear_settings[type_setting][bear_names]:
                    return (type_setting,
                            bear_settings[type_setting][bear_names][setting])


def get_kwargs(settings, bear, contents, dir=None):
    """
    Generates the keyword arguments to be provided to the run /
    create_arguments / generate_config methods of the bears except
    the keys: file and filename .
    :param settings:
        SettingsClass.BearSettings.optional_settings object or
        SettingsClass.BearSettings.non_optional_settings object.
    :param bear:
        The bear class.
    :param contents:
        The python object containing the file and
        directory structure written to 'PROJECT_DATA' and
        some value of settings detected by QuickstartBear.
    :param dir:
        The directory where to look for `bear_settings.yaml`.
    :return:
        The keyword arguments required for the running of the bear
        except the keys: file and filename.
    """
    bool_options = [True, False]
    kwargs = {}
    for setting in settings.settings_bool:
        kwargs[setting] = bool_options
    for setting in settings.settings_others:
        ret_val = get_setting_type(setting, bear, dir)
        if ret_val is not None:
            type_setting, values = ret_val
        else:
            type_setting, values = None, None
        if type_setting == 'type2':
            for items in contents[settings_key]:
                for setting_name in items:
                    if setting_name == setting:
                        # FIXME: will fail if a type2 setting accepts list
                        # as an input.
                        kwargs[setting_name] = [items[setting_name]] if (
                            not type(items[setting_name]) is list) else (
                            items[setting_name])
        if type_setting == 'type3':
            kwargs[setting] = values

    return kwargs


def check_bear_results(ret_val, ignore_ranges):
    if len(ret_val) == 0:
        return True
    elif len(ignore_ranges) == 0:
        return False
    # Check whether all the results lie in an ignore_ranges object
    for result in ret_val:
        for ignores in ignore_ranges:
            for range_object in result.affected_code:
                if not contained_in(range_object, ignores[1]):
                    return False
    return True


def _create_mp_pool(jobs: int = 0):
    """
    Create a multiprocessing pool.

    :param jobs: Number of jobs to run concurrently.
                 0 means auto-detect.  1 means no pool.
    """
    if not isinstance(jobs, int):
        raise TypeError('jobs must be an int')
    if jobs == 1:
        return
    if jobs < 0:
        raise ValueError('jobs must be 0 or a positive integer')

    import multiprocessing as mp
    cpu_count = mp.cpu_count()
    if cpu_count <= _RESERVE_CPUS:
        return
    if jobs == 0 or jobs > cpu_count - _RESERVE_CPUS:
        jobs = cpu_count - _RESERVE_CPUS
    pool = mp.Pool(processes=jobs)
    return pool


def local_bear_test(bear, file_dict, file_names, lang, kwargs,
                    ignore_ranges,
                    jobs: int = 0,
                    ):
    lang_files = split_by_language(file_names)
    lang_files = {k.lower(): v for k, v in lang_files.items()}

    pool = _create_mp_pool(jobs)

    file_results = []

    for file in lang_files[lang.lower()]:
        kwargs['filename'] = [file]
        kwargs['file'] = [file_dict[file]]

        results = []
        values = []

        for vals in itertools.product(*kwargs.values()):

            flag = 0
            for dep in bear.BEAR_DEPS:
                section = Section('dep-bear')
                bear_obj = dep(section, None)
                arguments = dict(zip(kwargs, vals))
                dep_args = get_all_args(dep.run)
                new_arguments = {}
                for arg_ in arguments.keys():
                    if arg_ in dep_args.keys():  # pragma: no cover
                        new_arguments[arg_] = arguments[arg_]
                arguments = new_arguments
                ret_val = bear_obj.run(**arguments)
                ret_val = [] if not ret_val else list(ret_val)
                dep_res = check_bear_results(ret_val, ignore_ranges)
                if not dep_res:
                    flag = 1
            if flag == 1:
                continue

            print_val = dict(zip(kwargs, vals))
            print_val.pop('file', None)
            values.append(vals)
            section = Section('test-section-local-bear')
            bear_obj = bear(section, None)
            ret_val = bear_obj.run(**dict(zip(kwargs, vals)))
            ret_val = [] if not ret_val else list(ret_val)
            if pool:  # pragma Python 3.5: no cover; pragma nt: no cover
                results.append(pool.apply(check_bear_results,
                                          args=(ret_val, ignore_ranges)))
            else:  # pragma Python 3.4,3.6,3.7: no cover
                results.append(check_bear_results(ret_val, ignore_ranges))

        for index, result in enumerate(results):
            if result is True:
                # A set of bear setting values is found to be green
                # for a particular file
                arguments = dict(zip(kwargs, values[index]))
                arguments.pop('file')
                file_results.append(arguments)

    return {bear: file_results}


def global_bear_test(bear, file_dict, kwargs, ignore_ranges,
                     jobs: int = 0,
                     ):
    results = []
    values = []
    file_results = []

    pool = _create_mp_pool(jobs)

    for vals in itertools.product(*kwargs.values()):
        values.append(vals)
        section = Section('test-section-global-bear')
        bear_obj = bear(section=section, message_queue=None,
                        file_dict=file_dict)
        bear_obj.file_dict = file_dict
        ret_val = bear_obj.run(**dict(zip(kwargs, vals)))
        ret_val = list(ret_val)
        if pool:  # pragma Python 3.5: no cover; pragma nt: no cover
            results.append(pool.apply(check_bear_results,
                                      args=(ret_val, ignore_ranges)))
        else:  # pragma Python 3.4,3.6,3.7: no cover
            results.append(check_bear_results(ret_val, ignore_ranges))

    for index, result in enumerate(results):
        if result is True:
            # A set of bear setting values is found to be green for this bear
            arguments = dict(zip(kwargs, values[index]))
            file_results.append(arguments)

    return {bear: file_results}


def run_test_on_each_bear(bear, file_dict, file_names, lang, kwargs,
                          ignore_ranges, type_of_setting, printer=None,
                          jobs: int = 0,
                          ):
    if type_of_setting == 'non-op':
        printer.print('Finding suitable values to necessary '
                      'settings for ' + bear.__name__ +
                      ' based on your project ...')
    else:
        printer.print('Finding suitable values to all settings '
                      'for ' + bear.__name__ +
                      ' based on your project ...',
                      color='green'
                      )
    if issubclass(bear, GlobalBear):
        file_results = global_bear_test(bear, file_dict, kwargs,
                                        ignore_ranges)
    else:
        file_results = local_bear_test(
            bear, file_dict, file_names, lang, kwargs, ignore_ranges)
    return file_results


def bear_test_fun(bears, bear_settings_obj, file_dict, ignore_ranges,
                  contents, file_names, op_args_limit, value_to_op_args_limit,
                  printer=None,
                  jobs: int = 0):
    """
    Tests the bears with the generated file dict and list of files
    along with the values recieved for each and every type of setting
    and checks whether they yield a result or not. A setting value
    is said to be 'green' if no results are produced by the bear. The
    bears are tested agains all possible combination of settings.
    :param bear:
        The bears from Constants/GREEN_MODE_COMPATIBLE_BEAR_LIST along
        with Constants/IMPORTANT_BEAR_LIST.
    :param bear_settings_obj:
        The object of SettingsClass/BearSettings which stores the metadata
        about whether a setting takes a boolean value or any other value.
    :param file_dict:
        A dict of file names as keys and file contents as values to those
        keys.
    :param ignore_ranges:
        Collection of SourceRange objects.
    :param contents:
        The python object to be written to 'PROJECT_DATA' which
        contains the file and directory structure of the project and values
        of some settings that can take an infinite set of values guessed
        by the QuickstartBear.
    :param file_names:
        The list of names of all the files in the project.
    :param op_args_limit:
        The maximum number of optional bear arguments allowed for guessing.
    :param value_to_op_args_limit:
        The maximum number of values to run the bear again and again for
        a optioanl setting.
    :return:
        Two Result data structures, one when the bears are run only with
        non-optional settings and the other including the optional settings.
        The data structure consists of a dict with bear name as key and
        a list of arguments for which a particular file was green with those
        arguments. The file name can be deduced from the arguments itself.
        The file contents have been chopped off from the arguments.
    """
    final_non_op_results = []
    final_unified_results = []
    for lang in bears:
        for bear in bears[lang]:
            for settings in bear_settings_obj:
                if settings.bear == bear:
                    # first get non optional settings
                    non_op_set = settings.non_optional_settings
                    op_set = settings.optional_settings
            non_op_kwargs = get_kwargs(non_op_set, bear, contents)
            op_kwargs = get_kwargs(op_set, bear, contents)
            non_op_file_results = run_test_on_each_bear(
                bear, file_dict, file_names, lang, non_op_kwargs,
                ignore_ranges, 'non-op', printer,
                jobs=jobs,
            )
            if len(op_kwargs) < op_args_limit and not (
                    True in [len(value) > value_to_op_args_limit
                             for key, value in op_kwargs.items()]):
                unified_kwargs = dict(non_op_kwargs)
                unified_kwargs.update(op_kwargs)
                unified_file_results = run_test_on_each_bear(
                    bear, file_dict, file_names, lang,
                    unified_kwargs, ignore_ranges, 'unified',
                    printer,
                    jobs=jobs,
                )
            else:
                unified_file_results = None
            final_non_op_results.append(non_op_file_results)
            final_unified_results.append(unified_file_results)

    return final_non_op_results, final_unified_results


def generate_data_struct_for_sections(results):
    """
    Interprets the results from the method `bear_test_fun()`
    which are inturn utilized by the method `generate_green_mode_sections()`
    to create sections for the coala config file.
    :param results:
        Individual values of the tuples returned by `bear_test_fun()`.
    """
    setting_vals = []
    for bear_dict in results:
        if not bear_dict:
            continue
        for bear in bear_dict:
            for dict_ in bear_dict[bear]:
                setting_vals.append(list(dict_.keys()))

    setting_vals_without_duplicates = []
    for elem in setting_vals:
        if elem not in setting_vals_without_duplicates:
            setting_vals_without_duplicates.append(elem)
    setting_vals = setting_vals_without_duplicates

    per_bear_settings = {}
    for bear_dict in results:

        if not bear_dict:
            continue

        data_struct = []
        for collection_of_settings in setting_vals:
            data_struct.append((collection_of_settings, []))

        for bear in bear_dict:
            for dict_ in bear_dict[bear]:
                for index, collection_of_settings in enumerate(setting_vals):
                    if list(dict_.keys()) == collection_of_settings:
                        # data_struct[collection_of_settings].append(dict_)
                        assert data_struct[index][0], collection_of_settings
                        data_struct[index][1].append(dict_)
        per_bear_settings[list(bear_dict.keys())[0]] = data_struct

    bear_data_struct = {}
    for bear in per_bear_settings:
        section_values = []
        for (setting_combs, list_of_vals) in per_bear_settings[bear]:
            dicts_with_settings = []
            for dict_ in list_of_vals:
                new_dict = deepcopy(dict_)
                new_dict.pop('filename')
                if new_dict not in dicts_with_settings:
                    dicts_with_settings.append(new_dict)
            dicts_with_settings_filename = deepcopy(dicts_with_settings)
            for item in dicts_with_settings_filename:
                item['filename'] = []
            for dict_ in list_of_vals:
                new_dict = deepcopy(dict_)
                new_dict.pop('filename')
                for id, to_append_dict in enumerate(dicts_with_settings):
                    if to_append_dict == new_dict:
                        dicts_with_settings_filename[id]['filename'].append(
                            dict_['filename'])
            section_values.append(dicts_with_settings_filename)
        bear_data_struct[bear] = section_values

    return bear_data_struct


def write_sections(self, sections):
    """
    This method is a re-definition of the
    `coalib.output.ConfWriter.write_sections` method. The difference
    it creates is that instead of accepting a list of sections it
    accepts a dict of sections with list of sections as the value
    to each key.
    :param sections:
        A dict with value as a list of sections to each key.
    """
    # Always write the section 'all' first.
    if not sections['all'] == []:
        self.write_section(sections['all'][0])
        all_section = sections['all'][0]
        ignore_all = all_section['ignore']
        del sections['all']
    else:
        all_section = ''
        ignore_all = ''

    for section in sections:
        for individual_section in sections[section]:
            individual_section.defaults = all_section
            if not ignore_all == '':
                individual_section['ignore'] = str(
                    ignore_all) + ', ' + str(individual_section['ignore'])
            self.write_section(individual_section)


def write_toml_sections(self, sections):
    sections_dict = OrderedDict()

    if not sections['all'] == []:
        all_section = sections['all'][0]
        ignore_all = all_section['ignore']
        sections_dict[all_section.name] = all_section
        del sections['all']
    else:
        all_section = ''
        ignore_all = ''

    for section in sections:
        for individual_section in sections[section]:
            individual_section.defaults = all_section
            if not ignore_all == '':
                individual_section['ignore'] = str(
                    ignore_all) + ', ' + str(individual_section['ignore'])
            sections_dict[individual_section.name] = individual_section
    self.coafile_to_toml(sections_dict)


def generate_green_mode_sections(data, project_dir, project_files,
                                 ignore_globs, in_toml, printer=None,
                                 suffix=''):
    """
    Generates the section objects for the green_mode.
    :param data:
        This is the data structure generated from the method
        generate_data_struct_for_sections().
    :param project_dir:
        The path of the project directory.
    :param project_files:
        List of paths to only the files inside the project directory.
    :param ignore_globs:
        The globs of files to ignore.
    :param in_toml:
        Decides whether to generate configuration files in toml or not
    :param printer:
        The ConsolePrinter object.
    :param suffix:
        A suffix that can be added to the `.coafile.green`.
    """
    all_sections = {'all': [], }
    lang_files = split_by_language(project_files)
    extset = get_extensions(project_files)
    ignored_files = generate_ignore_field(project_dir, lang_files.keys(),
                                          extset, ignore_globs)
    if ignored_files:
        section_all = Section('all')
        section_all['ignore'] = ignored_files
        all_sections['all'].append(section_all)

    for bear in data:
        num = 0
        bear_sections = []
        for setting_combs in data[bear]:
            if not setting_combs:
                continue
            for dict_ in setting_combs:
                num = num + 1
                section = Section('all.' + bear.__name__ + str(num), None)
                for key_ in dict_:
                    if key_ == 'filename':
                        file_list_sec = dict_[key_]
                        file_list_sec, ignore_list = aggregate_files(
                            file_list_sec, project_dir)
                        dict_[key_] = file_list_sec
                        section['ignore'] = ', '.join(
                            escape(x, '\\') for x in ignore_list)
                        section['files'] = ', '.join(
                            escape(x, '\\') for x in dict_[key_])
                    else:
                        section[key_] = str(dict_[key_])
                    section['bears'] = bear.__name__
                bear_sections.append(section)
        # Remove sections for the same bear who have common files i.e. more
        # than one setting was found to be green.
        file_list = []
        new_bear_sections = []
        for index, section in enumerate(bear_sections):
            if not section.contents['files'] in file_list:
                file_list.append(section.contents['files'])
                new_bear_sections.append(section)
        all_sections[bear.__name__] = new_bear_sections

    if in_toml:
        toml_file = os.path.join(project_dir, '.coafile.green.toml' + suffix)
        writer = ConfigConverter(toml_file)
        write_toml_sections(writer, all_sections)
        printer.print("'" + toml_file + "' successfully generated.",
                      color='green')
    else:
        coafile = os.path.join(project_dir, '.coafile.green' + suffix)
        writer = ConfWriter(coafile)
        write_sections(writer, all_sections)
        writer.close()
        printer.print("'" + coafile + "' successfully generated.",
                      color='green')
