import fnmatch
import itertools
import os
import yaml
from copy import deepcopy
from pathlib import Path

from coala_quickstart.generation.Utilities import (
    split_by_language, peek, contained_in)
from coala_quickstart.generation.SettingsClass import (
    SettingTypes)
from coala_quickstart.green_mode.QuickstartBear import (
    QuickstartBear)
from coalib.bears.GlobalBear import GlobalBear
from coalib.processes.Processing import (
    get_file_dict, yield_ignore_ranges)
from coalib.settings.Section import Section


settings_key = 'green_mode_infinite_value_settings'


def get_contents(project_data):
    """
    Reads a YAML file and returns the data.
    :param project_data:
        The file path from which to read data.
    :return:
        The YAML data as python objects.
    """
    with open(project_data, 'r') as stream:
        return yaml.load(stream)


def append_to_contents(contents, key, values):
    """
    Appends data to a dict, adding the recieved values
    to the list of values at a given key or creating
    the key if it does not exist.
    :param contents:
        The dict to append data to.
    :param key:
        The key needed to be appended to the dict.
    :param values:
        The list of values needed to be appended to the
        values at a key in the dict.
    :return:
        The dict with appended key and values.
    """
    found = False
    if settings_key not in contents:
        contents[settings_key] = []
    for index, obj in enumerate(contents[settings_key]):
        if isinstance(obj, dict) and key in obj.keys():
            found = True
            contents[settings_key][index][key] += values
    if not found:
        contents[settings_key].append({key: values})

    return contents


def dump_to_file(file, contents):
    """
    Writes YAML data to a file.
    :param file:
        The file to write YAML data to.
    :param contents:
        The python objects to be written as YAML data.
    """
    with open(file, 'w+') as outfile:
        yaml.dump(contents, outfile,
                  default_flow_style=False)


def initialize_project_data(dir, ignore_globs):
    """
    Generates the values for the key 'dir_structure'
    for `.project_data.yaml` which is directories as
    dicts with key name as dir names and value as
    list of files or nested dict of dirs.
    :param dir:
        The directory for which to add the directory structure
        and files.
    :param ignore_globs:
        The globs of files to ignore from writing to the
        '.project_data.yaml'.
    :return:
        The python object that was written as YAML data
        to `.project_data.yaml`.
    """
    files_dirs = os.listdir(dir)
    # files_dirs holds names of both files and dirs.
    dir_name = dir[dir.rfind(os.sep)+1:]
    final_data = []

    for i in files_dirs:
        to_continue = False
        for glob in ignore_globs:
            if fnmatch.fnmatch(dir+i, glob):
                to_continue = True
        if to_continue is True:
            continue
        if os.path.isfile(dir+i):
            final_data.append(i)
        else:
            look_into_dir = dir+i+os.sep
            data = initialize_project_data(look_into_dir,
                                           ignore_globs)
            final_data.append({i: data})
    return final_data


def generate_complete_filename_list(contents, project_dir):
    """
    Generates only a list of files with complete file
    paths from the 'dir_structure' key of `.project_data.yaml`.
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
                item[next(iter(item))], prefix+next(iter(item)))
    return file_names_list


def find_max_of_setting(setting, value, contents):
    """
    Generates max value of a setting where this
    function is called upon for every value generated for
    every file in the project (excluding ignored files).
    :param setting:
        The setting for which to find the max value of.
    :param value:
        The current value to be compared against the
        supposedly max value stored in contents.
    :param contents:
        The python object to be written to '.project_data.yaml'
        which contains the max value of the setting which was
        encountered uptil now.
    :return:
        The contents with the max value of the setting encountered
        uptil now after comparing it with the current value recieved
        by the function.
    """
    found = False
    position = None
    for index, item in enumerate(contents[settings_key]):
        if isinstance(item, dict) and setting in item:
            found = True
            position = index
    if not found:
        contents[settings_key].append({setting: value})
        return contents
    else:
        current_val = contents[settings_key][position][setting]
    if value > current_val:
        contents[settings_key][position][setting] = value
    return contents


def find_min_of_setting(setting, value, contents):
    """
    Generates min value of a setting where this
    function is called upon for every value generated for
    every file in the project (excluding ignored files).
    :param setting:
        The setting for which to find the min value of.
    :param value:
        The current value to be compared against the
        supposedly min value stored in contents.
    :param contents:
        The python object to be written to '.project_data.yaml'
        which contains the min value of the setting which was
        encountered uptil now.
    :return:
        The contents with the min value of the setting encountered
        uptil now after comparing it with the current value recieved
        by the function.
    """
    found = False
    for index, item in enumerate(contents[settings_key]):
        if isinstance(item, dict) and setting in item:
            found = True
            position = index
    if not found:
        contents[settings_key].append({setting: value})
        return contents
    else:
        current_val = contents[settings_key][position][setting]
    if value < current_val:
        contents[settings_key][position][setting] = value
    return contents


def run_quickstartbear(contents, project_dir):
    """
    Runs the QuickstartBear which pareses the file_dict
    to get the exact value of some settings which can attain
    any infinite amount of values.
    :param contents:
        The python object written to '.project_data.yaml' which
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
                contents = find_max_of_setting(
                    setting, return_val[setting], contents)

            for setting in find_min:
                contents = find_min_of_setting(
                    setting, return_val[setting], contents)

    bear_settings = get_contents(str(
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


def get_type_of_setting(setting, bear, dir=None):
    """
    Retireves the type of setting according to cEP0022.md
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
    bear_settings = get_contents(os.path.join(
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
        directory structure written to '.project_data.yaml' and
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
        ret_val = get_type_of_setting(setting, bear, dir)
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
    else:
        # Check whether all the results lie in an ignore_ranges object
        for result in ret_val:
            for ignores in ignore_ranges:
                for range_object in result.affected_code:
                    if not contained_in(range_object, ignores[1]):
                        return False
        return True


def local_bear_test(bear, file_dict, file_names, lang, kwargs,
                    ignore_ranges):
    lang_files = split_by_language(file_names)
    lang_files = {k.lower(): v for k, v in lang_files.items()}

    import multiprocessing as mp
    pool = mp.Pool(processes=mp.cpu_count()-1)

    file_results = []

    for file in lang_files[lang.lower()]:
        kwargs['filename'] = [file]
        kwargs['file'] = [file_dict[file]]

        results = []
        values = []

        for vals in itertools.product(*kwargs.values()):
            print_val = dict(zip(kwargs, vals))
            print_val.pop('file', None)
            values.append(vals)
            section = Section('test-section-local-bear')
            bear_obj = bear(section, None)
            ret_val = bear_obj.run(**dict(zip(kwargs, vals)))
            ret_val = list(ret_val)
            results.append(pool.apply(check_bear_results,
                                      args=(ret_val, ignore_ranges)))

        for index, result in enumerate(results):
            if result is True:
                # A set of bear setting values is found to be green
                # for a particular file
                arguments = dict(zip(kwargs, values[index]))
                arguments.pop('file')
                file_results.append(arguments)

    return {bear: file_results}


def global_bear_test(bear, file_dict, kwargs, ignore_ranges):
    import multiprocessing as mp
    pool = mp.Pool(processes=mp.cpu_count()-1)

    results = []
    values = []
    file_results = []

    for vals in itertools.product(*kwargs.values()):
        values.append(vals)
        section = Section('test-section-global-bear')
        bear_obj = bear(section=section, message_queue=None,
                        file_dict=file_dict)
        bear_obj.file_dict = file_dict
        ret_val = bear_obj.run(**dict(zip(kwargs, vals)))
        ret_val = list(ret_val)
        results.append(pool.apply(check_bear_results,
                                  args=(ret_val, ignore_ranges)))

    for index, result in enumerate(results):
        if result is True:
            # A set of bear setting values is found to be green for this bear
            arguments = dict(zip(kwargs, values[index]))
            file_results.append(arguments)

    return {bear: file_results}


def run_test_on_each_bear(bear, file_dict, file_names, lang, kwargs,
                          ignore_ranges, type_of_setting, printer=None):
    if type_of_setting == 'non-op':
        printer.print('Finding suitable values to necessary '
                      'settings for ' + bear.__name__ +
                      ' based on your project ...',
                      color='green')
    else:
        printer.print('Finding suitable values to all settings '
                      'for ' + bear.__name__ +
                      ' based on your project ...',
                      color='yellow'
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
                  printer=None):
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
        The python object to be written to '.project_data.yaml' which
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
                ignore_ranges, 'non-op', printer)
            if len(op_kwargs) < op_args_limit and not(
                    True in [len(value) > value_to_op_args_limit
                             for key, value in op_kwargs.items()]):
                unified_kwargs = dict(non_op_kwargs)
                unified_kwargs.update(op_kwargs)
                unified_file_results = run_test_on_each_bear(
                    bear, file_dict, file_names, lang,
                    unified_kwargs, ignore_ranges, 'unified',
                    printer)
            else:
                unified_file_results = None
            final_non_op_results.append(non_op_file_results)
            final_unified_results.append(unified_file_results)

    return final_non_op_results, final_unified_results


def green_mode(project_dir, ignore_globs, bears, bear_settings_obj,
               op_args_limit, value_to_op_args_limit, printer=None):
    """
    Runs the green mode of coala-quickstart. Generates
    '.project_data.yaml' which contains the files and directory structure
    of the project, runs the QuickstartBear which guesses some values
    of settings the can take an infinite set of values by parsing the
    file_dict and appends to `.project_data.yaml`. Runs some further linting
    options based on file names etc. Calls the methods which test out whether
    a setting value is green for a bear i.e. does not point out any error in
    the code base and further generates sections and writes the green config
    file for the project.
    :param project_dir:
        The project directory.
    :param ignore_globs:
        The globs of the files to ignore from the linting process.
    :param bears:
        The bears from Constants/GREEN_MODE_COMPATIBLE_BEAR_LIST along
        with Constants/IMPORTANT_BEAR_LIST.
    :param bear_settings_obj:
        The object of SettingsClass/BearSettings which stores the metadata
        about whether a setting takes a boolean value or any other value.
    :param op_args_limit:
        The maximum number of optional bear arguments allowed for guessing.
    :param value_to_op_args_limit:
        The maximum number of values to run the bear again and again for
        a optioanl setting.
    """
    from coala_quickstart.green_mode.filename_operations import (
        check_filename_prefix_postfix)
    ignore_globs.append(project_dir+os.sep+'.git'+os.sep+'**')
    project_data = project_dir + os.sep + '.project_data.yaml'

    # Currently as a temporary measure, recreating the file at each run from
    # scratch, as there is no mechanism created uptil now to reuse this data.
    if os.path.isfile(project_data):
        os.remove(project_data)

    if not os.path.isfile(project_data):
        new_data = initialize_project_data(project_dir+os.sep, ignore_globs)
        data_to_dump = {'dir_structure': new_data}
        dump_to_file(project_data, data_to_dump)
    else:
        pass
        # Add steps to reuse this data and modify this file later on.

    # Operations before the running of QuickstartBear are done over here.
    # Eg. do operations on filenames over here.
    project_data_contents = get_contents(project_data)
    project_data_contents = check_filename_prefix_postfix(
        project_data_contents)

    # Run QuickstartBear
    (project_data_contents, ignore_ranges, file_dict,
     file_names) = run_quickstartbear(
        project_data_contents, project_dir)

    final_non_op_results, final_unified_results = bear_test_fun(
        bears, bear_settings_obj, file_dict,
        ignore_ranges, project_data_contents, file_names,
        op_args_limit, value_to_op_args_limit, printer)

    # Call to create `.coafile` goes over here.

    # Final Dump.
    dump_to_file(project_data, project_data_contents)

    # Delete .project_data.yaml for now as there is currently no mechanism
    # added to reuse this data.
    os.remove(project_dir+os.sep+'.project_data.yaml')
