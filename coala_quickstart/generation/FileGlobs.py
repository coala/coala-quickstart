import os

from coala_utils.Question import ask_question
from coala_quickstart.Strings import GLOB_HELP
from coalib.collecting.Collectors import collect_files


def get_project_files(log_printer, printer, project_dir):
    """
    Gets the list of files matching files in the user's project directory
    after prompting for glob expressions.

    :param log_printer:
        A ``LogPrinter`` object.
    :param printer:
        A ``ConsolePrinter`` object.
    :return:
        A list of file paths matching the files.
    """
    printer.print(GLOB_HELP)
    file_globs = ask_question(
        "Which files do you want coala to run on?",
        default="**",
        printer=printer,
        typecast=list)
    ignore_globs = ask_question(
        "Which files do you want coala to run on?",
        printer=printer,
        typecast=list)
    printer.print()

    file_path_globs = [os.path.join(
        project_dir, glob_exp) for glob_exp in file_globs]
    ignore_path_globs = [os.path.join(
        project_dir, glob_exp) for glob_exp in ignore_globs]

    file_paths = collect_files(
        file_path_globs,
        log_printer,
        ignored_file_paths=ignore_path_globs)

    return file_paths
