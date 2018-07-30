import argparse
import logging
import os
import sys
from collections import OrderedDict

from pyprint.ConsolePrinter import ConsolePrinter

from coala_utils.FilePathCompleter import FilePathCompleter
from coala_utils.Question import ask_question

from coala_quickstart import __version__
from coala_quickstart.interaction.Logo import print_welcome_message
from coala_quickstart.generation.InfoCollector import collect_info
from coala_quickstart.generation.Project import (
    valid_path, get_used_languages, print_used_languages)
from coala_quickstart.generation.FileGlobs import get_project_files
from coala_quickstart.Strings import PROJECT_DIR_HELP
from coala_quickstart.generation.Bears import (
    filter_relevant_bears,
    print_relevant_bears,
    get_non_optional_settings_bears,
    filter_unusable_bears,
)
from coala_quickstart.generation.Settings import (
    generate_settings, write_coafile)
from coala_quickstart.generation.SettingsClass import (
    collect_bear_settings)


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
             'don\'t generate any error in the project and match the coala'
             'configuration as closely as possible to your project.')

    return arg_parser


def main():
    arg_parser = _get_arg_parser()
    args = arg_parser.parse_args()

    logging.basicConfig(stream=sys.stdout)
    printer = ConsolePrinter()
    logging.getLogger(__name__)

    fpc = None
    project_dir = os.getcwd()

    if args.green_mode:
        args.non_interactive = None
        args.no_filter_by_capabilities = None
        args.incomplete_sections = None

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
    print_used_languages(printer, used_languages)

    extracted_information = collect_info(project_dir)

    selected_bears = filter_relevant_bears(
        used_languages, printer, arg_parser, extracted_information)

    if args.green_mode:
        collect_bear_settings(selected_bears)

    # OrderedDict used for print_relevant_bears to first print unusable bears
    relevant_bears = OrderedDict(
            [('unusable', {}),
             ('usable',
                 selected_bears)])

    if args.non_interactive and not args.incomplete_sections:
        unusable_bears = get_non_optional_settings_bears(
            relevant_bears['usable'])
        filter_unusable_bears(relevant_bears, unusable_bears)

    print_relevant_bears(printer, relevant_bears)

    # Drop unusable bears
    relevant_bears = relevant_bears['usable']

    settings = generate_settings(
        project_dir,
        project_files,
        ignore_globs,
        relevant_bears,
        extracted_information,
        args.incomplete_sections)

    write_coafile(printer, project_dir, settings)
