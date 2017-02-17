import os
from collections import OrderedDict
from datetime import date

from pyprint.NullPrinter import NullPrinter
from pyprint.ConsolePrinter import ConsolePrinter
from coalib.output.ConsoleInteraction import acquire_settings
from coalib.settings.SectionFilling import fill_settings
from coalib.output.printers.LogPrinter import LogPrinter
from coala_quickstart.generation.Utilities import (
    split_by_language, get_extensions)
from coala_quickstart.generation.parse_gruntfile import get_gruntfile_info
from coalib.settings.Section import Section
from coalib.output.ConfWriter import ConfWriter
from coalib.collecting.Collectors import collect_files
from coala_quickstart.generation.Bears import print_relevant_bears_by_linter


def generate_section(section_name, extensions_used, bears, used_bears=[]):
    """
    Generates a section for a particular language (or default).

    :param section_name:
        Name of the section.
    :param extensions_used:
        A list of extensions associated with this section.
    :param bears:
        A list of bear classes.
    :param used_bears:
        A list of names of the bears already used in other section.
    :return:
        A ``Section`` object containing the section.
    """
    section = Section(section_name, None)
    bears = [bear.name for bear in bears if bear.name not in used_bears]
    section["bears"] = ", ".join(bear for bear in bears)
    section["files"] = ", ".join("**" + ext for ext in set(extensions_used))
    return section


def generate_sections_from_gruntfile(project_dir, project_files):
    gruntfile_info = get_gruntfile_info(project_dir)
    printer = ConsolePrinter()
    sections = []
    no_match_linters = []

    for info in gruntfile_info:
        if info.get("bears"):
            section_name = "gruntfile_" + info["linter"]
            section = Section(section_name, None)
            section["bears"] = ", ".join(bear for bear in info["bears"])
            if info.get("include"):
                section["files"] = ", ".join(
                    [path for path in set(info["include"])])
            else:
                files_from_languages = get_files_from_languages(
                    project_dir, project_files, info["languages"])
                if files_from_languages:
                    section["files"] = ", ".join(files_from_languages)
                else:
                    print("No files found")
                    continue
            if info.get("ignore"):
                section["files"] = info["ignore"]
            sections.append(section)
        else:
            no_match_linters.append(info["linter"])

    if no_match_linters:
        printer.print(
            "coala-quickstart could not identify following parts"
            " of Gruntile.js : {}".format(" ".join(no_match_linters)))

    bears_by_linter = {info["linter"]: info["bears"]
                       for info in gruntfile_info if info.get("bears")}
    print_relevant_bears_by_linter(printer, "Gruntfile.js", bears_by_linter)

    return sections


def get_files_from_languages(project_dir, project_files, languages):
    lang_files = split_by_language(project_files)
    print("lang_files:", lang_files.keys(), languages)
    results = set()
    for lang in languages:
        if lang_files.get(lang.lower()):
            print("lang found")
            for file in lang_files[lang.lower()]:
                results.add(os.path.relpath(file, project_dir))
    return results


def generate_ignore_field(project_dir, languages, extset, ignore_globs):
    """
    Generate the ignore field for the ``default`` section.

    :param project_dir:
        Full path of the user's project directory.
    :param languages:
        A list of languages present in the project.
    :param extset:
        A dict with language name as key and a set of extensions as
        value. This includes only those extensions used by the project.
    :return:
        A comma-separated string containing the globs to ignore.
    """
    null_printer = LogPrinter(NullPrinter())

    all_files = set(collect_files(
        "**",
        null_printer,
        ignored_file_paths=ignore_globs))

    ignores = []
    for glob in ignore_globs:
        gitignore_files = {file
                           for file in collect_files([glob], null_printer)}
        if not all_files.isdisjoint(gitignore_files):
            ignores.append(os.path.relpath(glob, project_dir))

    return ", ".join(ignores)


def generate_settings(project_dir, project_files, ignore_globs, relevant_bears):
    """
    Generates the settings for the given project.

    :param project_dir:
        Full path of the user's project directory.
    :param project_files:
        A list of file paths matched in the user's project directory.
    :param ignore_globs:
        The list of ignore glob expressions.
    :param relevant_bears:
        A dict with language name as key and bear classes as value.
    :return:
        A dict with section name as key and a ``Section`` object as value.
    """
    lang_map = {lang.lower(): lang for lang in relevant_bears}
    lang_files = split_by_language(project_files)
    extset = get_extensions(project_files)
    settings = OrderedDict()

    settings["default"] = generate_section(
        "default",
        [ext for lang in lang_files for ext in extset[lang]],
        relevant_bears[lang_map["all"]])

    ignored_files = generate_ignore_field(project_dir, lang_files.keys(),
                                          extset, ignore_globs)

    if ignored_files:
        settings["default"]["ignore"] = ignored_files

    used_bears = []
    gruntfile_sections = generate_sections_from_gruntfile(
        project_dir, project_files)
    for sec in gruntfile_sections:
        settings[sec.name] = sec
        used_bears.append(str(sec["bears"]))

    for lang in lang_files:
        if lang != "unknown" and lang != "all":
            settings[lang_map[lang]] = generate_section(
                lang,
                extset[lang],
                relevant_bears[lang_map[lang]],
                used_bears)

    log_printer = LogPrinter(ConsolePrinter())
    fill_settings(settings, acquire_settings, log_printer)

    return settings


def write_info(writer):
    """
    Writes the generator information and generation date in the coafile.

    :param writer:
        A ``ConfWriter`` object used for writing the information.
    """
    generation_date = date.today().strftime("%d %b %Y")
    generation_comment = ('# Generated by coala-quickstart on '
                          '{date}.\n'.format(date=generation_date))
    writer._ConfWriter__file.write(generation_comment)


def write_coafile(printer, project_dir, settings):
    """
    Writes the coafile to disk.

    :param printer:
        A ``ConsolePrinter`` object used for console interactions.
    :param project_dir:
        Full path of the user's project directory.
    :param settings:
        A dict with section name as key and a ``Section`` object as value.
    """
    coafile = os.path.join(project_dir, ".coafile")
    if os.path.isfile(coafile):
        printer.print("'" + coafile + "' already exists.\nThe settings will be"
                      " written to '" + coafile + ".new'",
                      color="yellow")
        coafile = coafile + ".new"

    writer = ConfWriter(coafile)
    write_info(writer)
    writer.write_sections(settings)
    writer.close()

    printer.print("'" + coafile + "' successfully generated.", color="green")
