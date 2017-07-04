import os

from coalib.parsing.Globbing import glob_escape
from coala_quickstart.generation.Utilities import (
    get_gitignore_glob, get_npmignore_glob)
from coala_utils.Question import ask_question
from coala_quickstart.Strings import GLOB_HELP
from coalib.collecting.Collectors import collect_files


def get_project_files(log_printer, printer, project_dir, non_interactive=False):
    """
    Gets the list of files matching files in the user's project directory
    after prompting for glob expressions.

    :param log_printer:
        A ``LogPrinter`` object.
    :param printer:
        A ``ConsolePrinter`` object.
    :param non_interactive
        Whether coala-quickstart is in non-interactive mode
    :return:
        A list of file paths matching the files.
    """
    file_globs = ["**"]

    ignore_globs = None
    if os.path.isfile(os.path.join(project_dir, ".gitignore")):
        printer.print("The contents of your .gitignore file for the project "
                      "will be automatically loaded as the files to ignore.",
                      color="green")
        ignore_globs = get_gitignore_glob(project_dir)

    npmignore_dir_list = []

    for dir_name, subdir_name, files in os.walk(project_dir):
        if(os.path.isfile(os.path.join(dir_name, ".npmignore"))):
            npmignore_dir_list += [dir_name]

    if(npmignore_dir_list):
        printer.print("The contents of your .npmignore file for the project "
                      "will be automatically loaded as files to ignore.",
                      color="green")
        if ignore_globs is None:
            ignore_globs = get_npmignore_glob(project_dir, npmignore_dir_list)
        else:
            ignore_globs += get_npmignore_glob(project_dir, npmignore_dir_list)

    if non_interactive and not ignore_globs:
        ignore_globs = []

    if ignore_globs is None:
        printer.print(GLOB_HELP)
        ignore_globs = ask_question(
            "Which files do you want coala to ignore?",
            printer=printer,
            typecast=list)
    printer.print()

    escaped_project_dir = glob_escape(project_dir)
    file_path_globs = [os.path.join(
        escaped_project_dir, glob_exp) for glob_exp in file_globs]
    ignore_path_globs = [os.path.join(
        escaped_project_dir, glob_exp) for glob_exp in ignore_globs]

    ignore_path_globs.append(os.path.join(escaped_project_dir, ".git/**"))

    file_paths = collect_files(
        file_path_globs,
        log_printer,
        ignored_file_paths=ignore_path_globs)

    return file_paths, ignore_globs
