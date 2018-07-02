import inspect
import os
from collections import defaultdict

from coala_utils.Extensions import exts
from coala_utils.string_processing import unescaped_search_for


def is_glob_exp(line):
    """
    Determines whether the string is a gitignore glob expression.

    :param line:
        Given string.
    :return:
        True if the string is a glob expression. False otherwise.
    """
    results = unescaped_search_for('[*!?\[\]]', line, use_regex=True)
    return sum(1 for x in results) != 0


def parse_gitignore_line(line):
    """
    Parses the line from ``.gitignore`` and returns a list of globs.

    :param line: A line from the project's ``.gitignore`` file.
    :return:     A list of glob expressions translated to the
                 syntax used in coala globbing.
    """
    if line.isspace() or line.startswith('#'):
        return []

    cur = len(line) - 1

    # Strips whitespace from the end if it is not escaped
    while cur >= 0 and line[cur].isspace() and line[cur - 1] != '\\':
        cur -= 1
    line = line[:cur + 1]

    if line.startswith('/'):
        if not is_glob_exp(line[1:]):
            # /build should map to ./build/** and ./build
            yield os.path.join(line[1:], '**')
            yield line[1:]
        else:
            # /*.c should map to ./*.c
            yield line[1:]
    else:
        if not is_glob_exp(line):
            # Ignore any directory or file with the same name
            yield os.path.join('**', line, '**')
            yield os.path.join('**', line)
            yield line
            yield os.path.join(line, '**')
        else:
            # *.c should map to ./**/*.c
            yield os.path.join('**', line)
            yield line


def get_gitignore_glob(project_dir, filename='.gitignore'):
    """
    Generates a list of glob expressions equivalent to the
    contents of the user's project's ``.gitignore`` file.

    :param project_dir:
        The user's project directory.
    :return:
        A list generator of glob expressions generated from the
        ``.gitignore`` file.
    """
    gitignore = os.path.join(project_dir, filename)

    with open(gitignore) as file:
        for line in file:
            for glob in parse_gitignore_line(line):
                yield os.path.join(project_dir, glob)


def split_by_language(project_files):
    """
    Splits the given files based on language. This ignores unknown extensions.

    :param project_files: A list of file paths.
    :return:              A dict with language name as keys and a list of
                          files coming under that language as values.
    """
    lang_files = defaultdict(lambda: set())
    for file in project_files:
        name, ext = os.path.splitext(file)
        if ext in exts:
            for lang in exts[ext]:
                lang_files[lang.lower()].add(file)
                lang_files['all'].add(file)

    return lang_files


def get_extensions(project_files):
    """
    Generates the extensions available in the given project files.

    :param project_files: A list of file paths.
    :return:              The set of extensions used in the project_files
                          for which bears exist.
    """
    extset = defaultdict(lambda: set())
    for file in project_files:
        ext = os.path.splitext(file)[1]
        if ext in exts:
            for lang in exts[ext]:
                extset[lang.lower()].add(ext)

    return extset


def get_default_args(func):
    """
    :param func: Function name.
    :return:
        A dict of function paramters as keys
        and default values as value if default values exist.
    """
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }


def get_all_args(func):
    """
    :param func: Function name.
    :return:
        A dict of function paramters as keys
        and default values as value.
    """
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
    }


def search_for_orig(decorated, orig_name):
    """
    Extracts out the original function if the function is decorated with
    one or more decorators.
    :param decorated:
        The decorated function object.
    :param orig_name:
        The name of the original function.
    :return:
        None or the original function object.
    """
    if decorated.__closure__ is not None:
        for obj in (c.cell_contents for c in decorated.__closure__):
            if hasattr(obj, '__name__') and obj.__name__ == orig_name:
                return obj
            if hasattr(obj, '__closure__') and obj.__closure__:
                found = search_for_orig(obj, orig_name)
                return found


def concatenate(dict1, dict2):
    """
    Concatenates 2 dicts of the type:
    eg.

    dict1:
    {'key1': {value1, value2},
     'key2': {value3, value4}}

    dict2:
    {'key2': {value4, value5},
     'key3': {value6, value7}}

    output:
    {'key1': {value1, value2},
     'key2': {value3, value4, value5},
     'key3': {value6, value7}}

    :return:
        The concatenated dict.
    """
    for key in dict1:
        if key in dict2:
            dict1[key] = dict1[key].union(dict2[key])

    for key in dict2:
        if key not in dict1:
            dict1[key] = dict2[key]

    return dict1
