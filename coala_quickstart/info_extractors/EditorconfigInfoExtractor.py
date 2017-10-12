import re

from coala_quickstart.info_extractors.EditorconfigParsing import (
    parse_editorconfig_file, translate_editorconfig_section_to_regex)
from coala_quickstart.info_extraction.InfoExtractor import InfoExtractor
from coala_quickstart.info_extraction.Information import (
    IndentStyleInfo, IndentSizeInfo, TrailingWhitespaceInfo, FinalNewlineInfo,
    CharsetInfo, LineBreaksInfo)


class EditorconfigInfoExtractor(InfoExtractor):
    supported_file_globs = ('.editorconfig',)

    spec_references = [
        'http://editorconfig.org/#file-format-details',
        'https://gitlab.com/coala/GSoC-2017/issues/172']

    supported_info_kinds = (
        IndentStyleInfo, IndentSizeInfo, TrailingWhitespaceInfo,
        FinalNewlineInfo, CharsetInfo, LineBreaksInfo)

    def parse_file(self, fname, file_content):
        return parse_editorconfig_file(fname, file_content)

    def find_information(self, fname, parsed_file):
        results = []

        for section_name, config in parsed_file.items():
            translated_regex = (
                    translate_editorconfig_section_to_regex(section_name))
            for key, value in config.items():
                if key == 'indent_size':
                    if value == 'tab':
                        #  When set to "tab", the value of tab_width
                        # (if specified) will be used
                        if config.get('tab_width'):
                            results.append(
                                IndentSizeInfo(
                                    fname,
                                    int(config['tab_width']),
                                    scope=translated_regex,
                                    container_section=section_name))
                    else:
                        results.append(
                            IndentSizeInfo(
                                fname, int(value), scope=translated_regex,
                                container_section=section_name))
                if key == 'indent_style':
                    results.append(
                        IndentStyleInfo(
                            fname, value, scope=translated_regex,
                            container_section=section_name))
                if key == 'trim_trailing_whitespace':
                    if value == 'true':
                        results.append(
                            TrailingWhitespaceInfo(
                                fname, True, scope=translated_regex,
                                container_section=section_name))
                    if value == 'false':
                        results.append(
                            TrailingWhitespaceInfo(
                                fname, False, scope=translated_regex,
                                container_section=section_name))
                if key == 'insert_final_newline':
                    if value == 'true':
                        results.append(
                            FinalNewlineInfo(
                                fname, True, scope=translated_regex,
                                container_section=section_name))
                    if value == 'false':
                        results.append(
                            FinalNewlineInfo(
                                fname, False, scope=translated_regex,
                                container_section=section_name))
                if key == 'charset':
                    results.append(
                        CharsetInfo(fname, value, scope=translated_regex,
                                    container_section=section_name))
                if key == 'end_of_line':
                    results.append(
                        LineBreaksInfo(fname, value, scope=translated_regex,
                                       container_section=section_name))

        return results


def editorconfig_file_match_method(files, info):
    """
    Checks if the ``Info`` instance extracted by EditorconfigInfoExtractor
    is applicable to all the files passed.

    :param files: list of files to be checked.
    :param info:  An ``Info`` instance stored inside an
                  ``EditorconfigInfoExtractor`` object.
    """
    if info.source != '.editorconfig':
        raise ValueError('The ``editorconfig_file_match_method`` received an'
                         '``Info`` instance not extracted by '
                         '``EditorconfigInfoExtractor``.')
    accepted_files_regex = info.scope[0]

    for fname in files:
        if not re.match(accepted_files_regex, fname):
            return False
    return True
