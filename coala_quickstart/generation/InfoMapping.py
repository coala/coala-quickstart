from coala_quickstart.info_extraction.InfoScope import InfoScope
from coala_quickstart.info_extraction.Information import (
    IndentStyleInfo, IndentSizeInfo, TrailingWhitespaceInfo, FinalNewlineInfo)
from coala_quickstart.info_extractors.EditorconfigInfoExtractor import (
    editorconfig_file_match_method)


INFO_SETTING_MAPS = {
    'use_spaces': [
        {
            'scope': InfoScope(
                level='global',
                section_match_method=editorconfig_file_match_method,
                allowed_sources=['.editorconfig']),
            'info_kind': IndentStyleInfo,
            'mapper_function': (
                lambda x: 'True' if x.value == 'space' else 'False'),
        }],
    'indent_size': [
        {
            'scope': InfoScope(
                level='global',
                section_match_method=editorconfig_file_match_method,
                allowed_sources=['.editorconfig']),
            'info_kind': IndentSizeInfo,
            'mapper_function': lambda x: x.value,
        }],
    'allow_trailing_whitespace': [
        {
            'scope': InfoScope(
                level='global',
                section_match_method=editorconfig_file_match_method,
                allowed_sources=['.editorconfig']),
            'info_kind': TrailingWhitespaceInfo,
            'mapper_function': lambda x: str(x.value),
        }],
    'enforce_newline_at_EOF': [
        {
            'scope': InfoScope(
                level='global',
                section_match_method=editorconfig_file_match_method,
                allowed_sources=['.editorconfig']),
            'info_kind': FinalNewlineInfo,
            'mapper_function': lambda x: str(x.value),
        }],
}
