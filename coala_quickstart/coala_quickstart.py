import argparse
import logging
import os
import signal
import sys

from pyprint.ConsolePrinter import ConsolePrinter

from coala_utils.FilePathCompleter import FilePathCompleter
from coala_utils.Question import ask_question

from coala_quickstart import __version__
from coala_quickstart.interaction.Logo import print_welcome_message
from coala_quickstart.generation.InfoCollector import collect_info
from coala_quickstart.generation.Project import (
    ask_to_select_languages,
    get_used_languages,
    print_used_languages,
    valid_path,
    )
from coala_quickstart.generation.FileGlobs import get_project_files
from coala_quickstart.Strings import PROJECT_DIR_HELP
from coala_quickstart.generation.Bears import (
    filter_relevant_bears,
    print_relevant_bears,
    get_non_optional_settings_bears,
    remove_unusable_bears,
)
from coala_quickstart.generation.Settings import (
    generate_settings, write_coafile)
from coala_quickstart.generation.SettingsClass import (
    collect_bear_settings)
from coala_quickstart.green_mode.green_mode_core import green_mode

MAX_ARGS_GREEN_MODE = 5
MAX_VALUES_GREEN_MODE = 5


def _get_arg_parser():
    description = """
coala-quickstart automatically creates a .coafile for use by coala.
"""
    arg_parser = argparse.ArgumentParser(
        prog='coala-quickstart',
        description=description,
        add_help=True
    )

    arg_parser.add_argument(
        '-v', '--version', action='version', version=__version__)

    arg_parser.add_argument(
        '-C', '--non-interactive', const=True, action='store_const',
        help='run coala-quickstart in non interactive mode')

    arg_parser.add_argument(
        '--ci', action='store_const', dest='non_interactive', const=True,
        help='continuous integration run, alias for `--non-interactive`')

    arg_parser.add_argument(
        '--allow-incomplete-sections', action='store_const',
        dest='incomplete_sections', const=True,
        help='generate coafile with only `bears` and `files` field in sections')

    arg_parser.add_argument(
        '--no-filter-by-capabilities', action='store_const',
        dest='no_filter_by_capabilities', const=True,
        help='disable filtering of bears by their capabilties.')

    arg_parser.add_argument(
        '-g', '--green-mode', const=True, action='store_const',
        help='Produce "green" config files for you project. Green config files'
             ' don\'t generate any error in the project and match the coala'
             ' configuration as closely as possible to your project.')

    arg_parser.add_argument(
        '--max-args', nargs='?', type=int,
        help='Maximum number of optional settings allowed to be checked'
             ' by green_mode for each bear.')

    arg_parser.add_argument(
        '--max-values', nargs='?', type=int,
        help='Maximum number of values to optional settings allowed to be'
             ' checked by green_mode for each bear.')

    return arg_parser


def signal_handler(signal, frame):
    sys.exit(0)


def main():
    global MAX_ARGS_GREEN_MODE, MAX_VALUES_GREEN_MODE
    arg_parser = _get_arg_parser()
    args = arg_parser.parse_args()

    logging.basicConfig(stream=sys.stdout)
    printer = ConsolePrinter()
    logging.getLogger(__name__)
    signal.signal(signal.SIGINT, signal_handler)

    fpc = None
    project_dir = os.getcwd()

    if args.green_mode:
        args.no_filter_by_capabilities = None
        args.incomplete_sections = None
        if args.max_args:
            MAX_ARGS_GREEN_MODE = args.max_args
        if args.max_values:
            MAX_VALUES_GREEN_MODE = args.max_values

    if not args.green_mode and (args.max_args or args.max_values):
        logging.warning(' --max-args and --max-values can be used '
                        'only with --green-mode. The arguments will '
                        'be ignored.')

    if not args.non_interactive and not args.green_mode:
        fpc = FilePathCompleter()
        fpc.activate()
        print_welcome_message(printer)
        printer.print(PROJECT_DIR_HELP)
        project_dir = ask_question(
            'What is your project directory?',
            default=project_dir,
            typecast=valid_path)
        fpc.deactivate()

    project_files, ignore_globs = get_project_files(
        None,
        printer,
        project_dir,
        fpc,
        args.non_interactive)

    used_languages = list(get_used_languages(project_files))
    used_languages = ask_to_select_languages(used_languages, printer,
                                             args.non_interactive)

    extracted_information = collect_info(project_dir)

    relevant_bears = filter_relevant_bears(
        used_languages, printer, arg_parser, extracted_information)

    if args.green_mode:
        bear_settings_obj = collect_bear_settings(relevant_bears)
        green_mode(
            project_dir, ignore_globs, relevant_bears, bear_settings_obj,
            MAX_ARGS_GREEN_MODE,
            MAX_VALUES_GREEN_MODE,
            project_files,
            printer,
        )
        exit()

    print_relevant_bears(printer, relevant_bears)

    if args.non_interactive and not args.incomplete_sections:
        unusable_bears = get_non_optional_settings_bears(relevant_bears)
        remove_unusable_bears(relevant_bears, unusable_bears)
        print_relevant_bears(printer, relevant_bears, 'usable')

    settings = generate_settings(
        project_dir,
        project_files,
        ignore_globs,
        relevant_bears,
        extracted_information,
        args.incomplete_sections)

    write_coafile(printer, project_dir, settings)
