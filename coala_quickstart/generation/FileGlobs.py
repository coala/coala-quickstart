import os

from coalib.parsing.Globbing import glob_escape
from coala_quickstart.generation.Utilities import get_gitignore_glob
from coala_utils.Question import ask_question
from coala_quickstart.Strings import GLOB_HELP
from coalib.collecting.Collectors import collect_files


def get_project_files(log_printer, printer, project_dir, is_CI_mode):
    """
    Gets the list of files matching files in the user's project directory
    after prompting for glob expressions.

    :param log_printer:
        A ``LogPrinter`` object.
    :param printer:
        A ``ConsolePrinter`` object.
    :param is_CI_mode:
        The running mode for coala-quickstart.
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

    if is_CI_mode:
        if ignore_globs is None:
            file = open(".gitignore", "w")
            file.write(".directory")
            ignore_globs = get_gitignore_glob(project_dir)

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

