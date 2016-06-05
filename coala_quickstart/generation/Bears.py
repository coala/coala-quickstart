from pyprint.NullPrinter import NullPrinter

from coala_quickstart.Strings import BEAR_HELP
from coala_utils.Question import ask_question
from coalib.settings.ConfigurationGathering import (
    load_configuration, get_filtered_bears)
from coalib.misc.DictUtilities import inverse_dicts
from coalib.collecting.Collectors import (
    collect_all_bears_from_sections, filter_section_bears_by_languages)
from coalib.output.printers.LogPrinter import LogPrinter


def filter_relevant_bears(used_languages):
    """
    From the bear dict, filter the bears per relevant language.

    :param used_languages:
        A list of tuples with language name as the first element
        and percentage usage as the second element; sorted by
        percentage usage.
    :return:
        A dict with language name as key and bear classes as value.
    """
    log_printer = LogPrinter(NullPrinter())
    used_languages.append(("All", 100))

    result = {lang: set(inverse_dicts(*get_filtered_bears(
        [lang], log_printer)).keys()) for lang, _ in used_languages}

    # Each language would also have the language independent bears. We remove
    # those and put them in the "All" category.
    lang_bears = {lang: result[lang] - result["All"]
                  for lang, _ in used_languages}
    lang_bears["All"] = result["All"]
    return lang_bears


def print_relevant_bears(printer, relevant_bears):
    """
    Prints the relevant bears in sections separated by language.

    :param printer:
        A ``ConsolePrinter`` object used for console interactions.
    :param relevant_bears:
        A dict with language name as key and bear classes as value.
    """
    printer.print(BEAR_HELP)
    printer.print("\nBased on the languages used in project the following "
                  "bears have been identified to be relevant:")
    for language in relevant_bears:
        printer.print("\t[" + language + "]", color="green")
        for bear in relevant_bears[language]:
            printer.print("\t" + bear.name, color="cyan")
        printer.print("")
