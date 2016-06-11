import os

from coala_utils.Extensions import exts
from coalib.parsing.StringProcessing import unescaped_search_for


def is_glob_exp(line):
    """
    Determines whether the string is a glob expression.

    :param line:
        Given string.
    :return:
        True if the string is a glob expression. False otherwise.
    """
    results = unescaped_search_for("[*!?\[\]]", line, use_regex=True)
    return sum(1 for x in results) != 0


def parse_gitignore_line(line):
    """
    Parses the line from ``.gitignore`` and returns a list of globs.

    :param line: A line from the project's ``.gitignore`` file.
    :return:     A list of glob expressions translated to the
                 syntax used in coala globbing.
    """
    if line.isspace() or line.startswith("#"):
        return []

    result = []
    cur = len(line) - 1

    while cur >= 0 and line[cur].isspace() and line[cur - 1] != "\\":
        cur -= 1
    line = line[:cur + 1]

    if line.startswith("/"):
        if not is_glob_exp(line[1:]):
            # /build should map to /cwd/build/** and /cwd/build
            result.append(os.path.join(line[1:], "**"))
            result.append(line[1:])
        else:
            # /*.c should map to /cwd/*.c
            result.append(line[1:])
    else:
        if not is_glob_exp(line):
            # Ignore any directory or file with the same name
            result.append(os.path.join("**", line, "**"))
            result.append(os.path.join("**", line))
            result.append(line)
            result.append(os.path.join(line, "**"))
        else:
            # *.c should map to /cwd/**/*.c
            result.append(os.path.join("**", line))
            result.append(line)

    return result


def get_gitignore_glob(project_dir, filename=".gitignore"):
    """
    Generates a list of glob expressions equivalent to the
    contents of the user's project's ``.gitignore`` file.

    :param project_dir:
        The user's project directory.
    :return:
        A list of glob expressions generated from the
        ``.gitignore`` file.
    """
    result = []
    gitignore = os.path.join(project_dir, filename)

    with open(gitignore, "r") as file:
        for line in file:
            result += [os.path.join(
                project_dir, glob) for glob in parse_gitignore_line(line)]

    return result


def generate_lang_extensions():
    """
    Generates a dict with language name (lower case) as key and the
    corresponding extensions as values.

    :return: The corresponding dict.
    """
    lang_extensions = {}
    for ext in exts:
        for lang in exts[ext]:
            lang = lang.lower()
            if lang in lang_extensions:
                lang_extensions[lang].append(ext)
            else:
                lang_extensions[lang] = [ext]

    return lang_extensions


def split_by_language(project_files):
    """
    Splits the given files based on language.

    :param project_files: A list of file paths.
    :return:              A dict with language name as keys and a list of
                          files coming under that language as values.
    """
    lang_files = {"all": []}
    for file in project_files:
        name, ext = os.path.splitext(file)
        if ext in exts:
            for lang in exts[ext]:
                lang = lang.lower()
                if lang in lang_files:
                    lang_files[lang].append(file)
                else:
                    lang_files[lang] = [file]
                lang_files["all"].append(file)

    return lang_files


def get_extensions(project_files):
    """
    Generates the extensions available in the given project files.

    :param project_files: A list of file paths.
    :return:              The set of extensions used in the project_files
                          for which bears exist.
    """
    extset = set()
    for file in project_files:
        ext = os.path.splitext(file)[1]
        if ext in exts:
            extset.add(ext)

    return extset
