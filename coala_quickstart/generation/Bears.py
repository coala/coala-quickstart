from pyprint.NullPrinter import NullPrinter

from coala_quickstart.Constants import IMPORTANT_BEAR_LIST
from coala_quickstart.Strings import BEAR_HELP
from coalib.settings.ConfigurationGathering import get_filtered_bears
from coalib.misc.DictUtilities import inverse_dicts
from coalib.output.printers.LogPrinter import LogPrinter


def filter_relevant_bears(used_languages, arg_parser=None):
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

    all_bears_by_lang = {
        lang: set(inverse_dicts(*get_filtered_bears([lang],
                                                    log_printer,
                                                    arg_parser)).keys())
        for lang, _ in used_languages
    }

    bears_by_lang = {}
    for lang in all_bears_by_lang:
        if lang in IMPORTANT_BEAR_LIST:
            bears_by_lang[lang] = {bear for bear in all_bears_by_lang[lang]
                                   if bear.name in IMPORTANT_BEAR_LIST[lang]}
        else:
            bears_by_lang[lang] = all_bears_by_lang[lang]

    # Each language would also have the language independent bears. We remove
    # those and put them in the "All" category.
    lang_bears = {lang: bears_by_lang[lang] - bears_by_lang["All"]
                  for lang, _ in used_languages}
    lang_bears["All"] = bears_by_lang["All"]
    return lang_bears


def get_non_optional_settings(bears):
    """
    From the bear dict, get the non-optional settings.

    :param bears:
        A dict with language name as key and bear classes as value.
    :return:
        A dict with Bear class as key and bear non-optional settings as value.
    """
    non_optional_settings = {}
    for language in bears:
        for bear in bears[language]:
            if bear not in non_optional_settings:
                needed = bear.get_non_optional_settings()
                # FIXME: This only finds non-optional settings for immediate
                # dependencies.  See https://github.com/coala/coala/issues/3149
                for bear_dep in bear.BEAR_DEPS:
                    needed.update(bear_dep.get_non_optional_settings())

                non_optional_settings[bear] = needed

    return non_optional_settings


def get_non_optional_settings_bears(bears):
    """
    Return tuple of bears with non optional settings.

    :param unusable_bears:
        A collection of Bear classes.
    """
    non_optional_settings = get_non_optional_settings(bears)
    non_optional_settings = tuple(bear for bear, settings
                                  in non_optional_settings.items()
                                  if settings)
    return non_optional_settings


def remove_unusable_bears(bears, unusable_bears):
    """
    From the bears dict, filter the bears appearing in unusable_bears.

    :param bears:
        A dict with language name as key and bear classes as value.
    :param unusable_bears:
        A collection of Bear classes.
    """
    for language, language_bears in bears.items():
        for bear in tuple(language_bears):
            if bear in unusable_bears:
                bears[language].remove(bear)


def print_relevant_bears_by_language(printer, relevant_bears, label='relevant'):
    """
    Prints the relevant bears in sections separated by language.

    :param printer:
        A ``ConsolePrinter`` object used for console interactions.
    :param relevant_bears:
        A dict with language name as key and bear classes as value.
    """
    if label == 'relevant':
        printer.print(BEAR_HELP)

    printer.print("\nBased on the languages used in project the following "
                  "bears have been identified to be %s:" % label)
    for language in relevant_bears:
        printer.print("    [" + language + "]", color="green")
        for bear in relevant_bears[language]:
            printer.print("    " + bear.name, color="cyan")
        printer.print("")


def print_relevant_bears_by_linter(printer,
                                   source,
                                   relevant_bears,
                                   label="relevant"):
    """
    Prints the relevant bears in sections separated by corresponding
    linter names.

    :param printer:
        A ``ConsolePrinter`` object used for console interactions.
    :param source:
        A string containing info about the source of information of
        the relevance of bears.
    :param relevant_bears:
        A dict with linter name as key and bear names as value.
    """

    printer.print("\nBased on the %s used in project the following "
                  "bears have been identified to be %s:" % (source, label))
    for linter in relevant_bears:
        printer.print("    [" + linter + "]", color="green")
        for bear in relevant_bears[linter]:
            printer.print("    " + bear, color="cyan")
        printer.print("")
