import os
import operator
from collections import defaultdict

from coala_utils.string_processing.StringConverter import StringConverter
from coala_utils.Extensions import exts


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


def print_used_languages(printer, results):
    """
    Prints the sorted list of used languages along with each language's
    percentage use.

    :param printer:
        A ``ConsolePrinter`` object used for console interactions.
    :param results:
        A list of tuples containing a language name as the first value
        and percentage usage in the project as the second value.
    """
    printer.print(
        'The following languages have been automatically detected:')
    for lang, percent in results:
        formatted_line = '{:>25}: {:>2}%'.format(lang, int(percent))
        printer.print(formatted_line, color='cyan')
    printer.print()
