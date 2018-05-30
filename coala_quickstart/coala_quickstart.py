import argparse
import logging
import os
import sys

from pyprint.ConsolePrinter import ConsolePrinter

from coala_utils.FilePathCompleter import FilePathCompleter
from coala_utils.Question import ask_question

from coala_quickstart.interaction.Logo import print_welcome_message
from coala_quickstart.generation.InfoCollector import collect_info
from coala_quickstart.generation.Project import (
    valid_path, get_used_languages, print_used_languages)
from coala_quickstart.generation.FileGlobs import get_project_files
from coala_quickstart.generation.Bears import (
    filter_relevant_bears,
    print_relevant_bears,
    get_non_optional_settings_bears,
    remove_unusable_bears,
)
from coala_quickstart.generation.Settings import (
    generate_settings, write_coafile)


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
        '-v', '--version', action='version', version='0.4.0')

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

    return arg_parser


def main():
    arg_parser = _get_arg_parser()
    args = arg_parser.parse_args()

    logging.basicConfig(stream=sys.stdout)
    printer = ConsolePrinter()
    logging.getLogger(__name__)

    fpc = None
    project_dir = os.getcwd()

    if not args.non_interactive:
        fpc = FilePathCompleter()
        fpc.activate()
        print_welcome_message(printer)
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

    relevant_bears = filter_relevant_bears(
        used_languages, printer, arg_parser, extracted_information)

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
