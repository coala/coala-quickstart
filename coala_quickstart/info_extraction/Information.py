from coala_quickstart.info_extraction.Info import Info


class LicenseUsedInfo(Info):
    description = 'License of the project.'
    value_type = (str,)
    example_values = ['MIT', 'GPL-3', 'Apache-2.0']


class VersionInfo(Info):
    description = 'Version information, see http://semver.org/'
    value_type = (str,)
    example_values = ['>=1.2.7', '~1.2.3', '^0.2']


class ProjectDependencyInfo(Info):
    description = 'Dependency of the project.'
    value_type = (str,)
    example_values = ['some_npm_package_name', 'some_gem_name', 'other_dep']

    def __init__(self,
                 source,
                 value,
                 extractor=None,
                 version=None,
                 url=''):
        super().__init__(source, value, extractor, version=version, url=url)


class StyleInfo(Info):
    description = 'Information related to code styling.'

    def __init__(self,
                 source,
                 value,
                 extractor=None,
                 scope=['**'],
                 **kwargs):
        """
        :param scope: list of files to which the styling information
                      is applicable.
        """
        super().__init__(source, value, extractor, scope=scope, **kwargs)


class PathsInfo(Info):
    description = 'File path globs mentioned in the file.'
    value_type = ([str],)
    example_values = ['**.py', 'dev/tests/**']


class IncludePathsInfo(PathsInfo):
    description = 'Target files to perform analysis.'


class IgnorePathsInfo(PathsInfo):
    description = 'Files to ignore during analysis.'


class ManFilesInfo(Info):
    description = 'Filenames to put in place for the man program to find.'
    value_type = (str, [str])
    example_values = ['./man/doc.1', ['./man/foo.1', './man/bar.1']]

    def __init__(self,
                 source,
                 value,
                 extractor=None,
                 keyword=''):
        """
        :param keyword: Primary keyword for ``man`` command that would display
                        the man pages provided in value argument.
        """
        super().__init__(source, value, extractor, keyword=keyword)


class IndentStyleInfo(StyleInfo):
    description = "'Tab' or 'Space' to use hard tabs or soft tabs."
    value_type = ('tab', 'space')


class IndentSizeInfo(StyleInfo):
    description = 'The number of columns used for each indentation level.'
    value_type = (int,)
    example_values = [2, 4]


class TrailingWhitespaceInfo(StyleInfo):
    description = ('Information representing whether whitespace characters '
                   'preceding newline characters are allowed or not.')
    value_type = (bool,)


class FinalNewlineInfo(StyleInfo):
    description = ('Information representing whether to enformce file ending '
                   ' with a newline or not.')
    value_type = (bool,)


class CharsetInfo(StyleInfo):
    description = 'Information regarding character set.'
    value_type = (str,)
    example_values = ['utf-8', 'latin1', 'utf-8-bom']


class LineBreaksInfo(StyleInfo):
    description = ('Information regarding how line breaks are represented '
                   'i.e. "lf", "cr", or "crlf"')
    value_type = ('lf', 'cr', 'crlf')


class MentionedTasksInfo(Info):
    description = 'Names of the tasks mentioned in the project configuration.'
    value_type = ([str],)
    example_values = [['csslint', 'copy', 'quint', 'uglify']]


class LintTaskInfo(Info):
    description = 'Information about a task used in project.'
    value_type = (str,)
    example_values = ['csslint', 'jshint']

    def __init__(self,
                 source,
                 value,
                 extractor=None,
                 include_paths=None,
                 ignore_paths=None,
                 config={}):
        """
        :param include_paths: list of file globs on which the
                              lint task is being run.
        :param ignore_paths:  list of file globs which are ignored
                              by the lint task.
        :param config:        dict of configuration settings of the
                              linter and their values.
        """
        super().__init__(
            source, value, include_paths=include_paths,
            ignore_paths=ignore_paths, config=config)
