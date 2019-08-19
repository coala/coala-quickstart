import os

from coala_quickstart.generation.Utilities import (
    get_yaml_contents,
    dump_yaml_to_file,
    )
from coala_quickstart.green_mode.green_mode import (
    bear_test_fun,
    generate_data_struct_for_sections,
    generate_green_mode_sections,
    initialize_project_data,
    run_quickstartbear,
    )
from coala_quickstart.green_mode.filename_operations import (
    check_filename_prefix_postfix,
    )

PROJECT_DATA = '.project_data.yaml'


def green_mode(project_dir: str, ignore_globs, bears, bear_settings_obj,
               op_args_limit, value_to_op_args_limit, in_toml, project_files,
               printer=None):
    """
    Runs the green mode of coala-quickstart.

    Generates '.project_data.yaml' which contains the files and directory
    structure of the project, runs the QuickstartBear which guesses some values
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
        The bears from Constants.GREEN_MODE_COMPATIBLE_BEAR_LIST along
        with Constants.IMPORTANT_BEAR_LIST.
    :param bear_settings_obj:
        The object of SettingsClass/BearSettings which stores the metadata
        about whether a setting takes a boolean value or any other value.
    :param op_args_limit:
        The maximum number of optional bear arguments allowed for guessing.
    :param in_toml:
        Decides whether to generate configuration file in toml or not
    :param project_files:
        The list of files in the project.
    :param value_to_op_args_limit:
        The maximum number of values to run the bear again and again for
        a optional setting.
    """
    from coala_quickstart.green_mode.filename_operations import (
        check_filename_prefix_postfix)
    ignore_globs.append(os.path.join(project_dir, '.git', '**'))
    project_data = project_dir + os.sep + PROJECT_DATA

    # Currently as a temporary measure, recreating the file at each run from
    # scratch, as there is no mechanism created uptil now to reuse this data.
    if os.path.isfile(project_data):
        os.remove(project_data)

    if not os.path.isfile(project_data):
        new_data = initialize_project_data(project_dir + os.sep, ignore_globs)
        data_to_dump = {'dir_structure': new_data}
        dump_yaml_to_file(project_data, data_to_dump)

    # Operations before the running of QuickstartBear are done over here.
    # Eg. do operations on filenames over here.
    project_data_contents = get_yaml_contents(project_data)
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
    settings_non_op = generate_data_struct_for_sections(
        final_non_op_results)
    settings_unified = generate_data_struct_for_sections(
        final_unified_results)

    # Combine the settings for the sections due to the missed out bears in
    # unified results due to the limitations on maximum number of optionanl
    # arguments and the values to those arguments that can be supplied.
    for bear in settings_non_op:
        if bear not in settings_unified:
            settings_unified[bear] = settings_non_op[bear]

    generate_green_mode_sections(
        settings_unified, project_dir, project_files, ignore_globs,
        in_toml, printer)

    # Final Dump.
    dump_yaml_to_file(project_data, project_data_contents)

    # Delete .project_data.yaml for now as there is currently no mechanism
    # added to reuse this data.
    os.remove(project_data)
