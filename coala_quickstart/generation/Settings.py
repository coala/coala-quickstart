import os

from coala_utils.Extensions import exts
from coala_quickstart.generation.Utilities import (
    generate_lang_extensions, split_by_language, get_extensions)
from coala_quickstart.generation.FileGlobs import generate_glob_exps
from coalib.settings.Section import Section
from coalib.output.ConfWriter import ConfWriter


def generate_settings(project_dir, project_files, relevant_bears):
    """
    Generates the settings for the given project.

    :param project_dir:
        Full path of the user's project directory.
    :param project_files:
        A list of file paths matched in the user's project directory.
    :param relevant_bears:
        A dict with language name as key and bear classes as value.
    :return:
        A dict with section name as key and a ``Section`` object as value.
    """
    lang_map = {lang.lower(): lang for lang in relevant_bears}
    lang_extensions = generate_lang_extensions()
    lang_files = split_by_language(project_files)
    extset = get_extensions(project_files)

    settings = {}

    for lang in lang_files:
        if lang == "unknown":
            continue

        section = Section("default" if lang == "all" else lang, None)

        files, ignore = generate_glob_exps(
            lang_files[lang],
            lang_extensions[lang] if lang != "all" else list(extset),
            project_dir)
        section["files"] = ", ".join(files)
        section["ignore"] = ", ".join(ignore)

        section["bears"] = ", ".join(
            bear.name for bear in relevant_bears[lang_map[lang]])

        settings[lang_map[lang]] = section

    return settings


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
    writer.write_sections(settings)
    writer.close()

    printer.print("'" + coafile + "' successfully generated.", color="green")
