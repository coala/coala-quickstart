import os

from coala_utils.Extensions import exts


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
