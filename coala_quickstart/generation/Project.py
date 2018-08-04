import os
import operator
from collections import defaultdict
import re

from coala_utils.string_processing.StringConverter import StringConverter
from coala_utils.Extensions import exts
from coala_quickstart.generation.Utilities import get_language_from_hashbang
from coala_quickstart.Constants import HASHBANG_REGEX


def valid_path(path: StringConverter):
    """
    Raises an exception if the given ``StringConverter`` object is
    not a valid directory. Example:

    >>> from coala_utils.string_processing.StringConverter import (
    ...     StringConverter)
    >>> import os
    >>> os.getcwd() == valid_path(StringConverter(""))
    True
    >>> valid_path(StringConverter("invalid_dir"))
    Traceback (most recent call last):
      ...
    ValueError: The given path doesn't exist.

    :param path: A ``StringConverter`` object.
    :return:     The full expanded path if the path has relative elements.
    """
    path = os.path.abspath(os.path.expanduser(str(path)))
    if not os.path.isdir(path):
        raise ValueError("The given path doesn't exist.")
    return path


def language_percentage(file_paths):
    """
    Computes the percentage composition of each language, with unknown
    extensions tagged with the ``Unknown`` key.

    :param file_paths: A list of file paths.
    :return:           A dict with file name as key and the percentage
                       of occurences as the value.
    """
    if file_paths:
        delta = 100 / len(file_paths)

    results = defaultdict(lambda: 0)
    for file_path in file_paths:
        ext = os.path.splitext(file_path)[1]

        if ext in exts:
            for lang in exts[ext]:
                results[lang] += delta

        elif os.path.exists(file_path):
            with open(file_path, 'r') as data:
                hashbang = data.readline()
                if re.match(HASHBANG_REGEX, hashbang):
                    language = get_language_from_hashbang(hashbang).lower()
                    for ext in exts:
                        for lang in exts[ext]:
                            if language == lang.lower():
                                results[lang.lower()] += delta

    return results


def get_used_languages(file_paths):
    """
    Identifies the most used languages in the user's project directory
    from the files matched from the given glob expression.

    :param file_paths:
        A list of absolute file paths in the user's project directory.
    :return:
        A tuple iterator containing a language name as the first value
        and percentage usage in the project as the second value.
    """
    return sorted(
        language_percentage(file_paths).items(),
        key=operator.itemgetter(1),
        reverse=True)


def ask_to_select_languages(languages, printer):
    print(languages)
    only_languages = []
    percentages = []
    max_length = -1
    PROMPT_QUESTION = ('Which languages would you like to generate a config '
                       'file for?\n'
                       'Please select some languages using '
                       "their numbers or just press 'Enter' to select "
                       'all of them\n')
    for language in languages:
        only_languages.append(language[0])
        percentages.append(language[1])
        if len(language[0]) > max_length:
            max_length = len(language[0])
    total_options = len(only_languages) + 1
    printer.print(PROMPT_QUESTION, color='yellow')
    for idx, lang in enumerate(only_languages):
        num_spaces = max_length - len(lang)
        spaces = ''
        for i in range(num_spaces):
            spaces += ' '
        printer.print(
            '    {}. {}{} {:>2}%'.format(
                idx + 1, lang, spaces, int(percentages[idx])), color='green')

    selected_numbers = []
    try:
        selected_numbers = list(map(int, re.split('\D+', input())))
    except Exception:
        # Parsing failed, choose all the default capabilities
        selected_numbers = [total_options]

    selected_languages = []

    for num in selected_numbers:
        if num >= 0 and num < total_options:
            selected_languages.append(languages[int(num) - 1])
        elif num == total_options:
            selected_languages = languages
        else:
            printer.print(
                '{} is not a valid option. Please choose the right'
                ' option numbers'.format(str(num)))
            return ask_to_select_languages(languages,
                                           printer)
    return selected_languages


def print_used_languages(printer, results, non_interactive=True):
    """
    Prints the sorted list of used languages along with each language's
    percentage use.

    :param printer:
        A ``ConsolePrinter`` object used for console interactions.
    :param results:
        A list of tuples containing a language name as the first value
        and percentage usage in the project as the second value.
    :param non_interactive:
        Variable that defines whether quickstart is in non_interactive
        mode or not.
    """
    if non_interactive:
        printer.print(
            'The following languages have been automatically detected:\n')
    else:
        printer.print(
            'The following languages have been selected by you:\n')
    for lang, percent in results:
        formatted_line = '{:>25}: {:>2}%'.format(lang, int(percent))
        printer.print(formatted_line, color='cyan')
    printer.print()
