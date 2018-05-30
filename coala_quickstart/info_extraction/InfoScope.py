from coala_quickstart.info_extraction.Utilities import assert_type_signature


class InfoScope:
    """
    A class representing the scope of applicability of an ``Info``
    instance. An ``InfoScope`` instance can be used to restrict the
    usability of an ``Info`` instance as a setting value.
    """

    def __init__(self,
                 level,
                 sections=[],
                 bears=[],
                 section_match_method=None,
                 allowed_sources=[],
                 allowed_extractors=tuple()):
        """
        :param level:
            Broad-level scope, possible values are "global", "section",
            and "bear".
        :param sections:
            list of section names, considered only for the ``level``
            "section" and "bear".
        :param bears:
            list of bear names, considered only for the "bear" ``level``.
        :param section_match_method:
            A function object implementing a function of the form-
            ```
            def dummy_section_match_method(section_files, Info):
                '''
                Checks if the Info is applicable to all the files in the
                section.

                :param section_files: list of files contained in the section.
                :param Info:          The Info which is to be checked.
                :returns:             A boolean value
                '''
            ```
        :param allowed_sources:
            list containing names of the sources of ``Info`` classes which fall
            within this scope, empty list will means the ``Info`` instance is
            applicable for all the sources.
        :param allowed_extractors:
            list of allowed ``InfoExtractor`` derived classes for the scope.
        """
        assert_type_signature(level, ['global', 'section', 'bear'], 'level')

        self.level = level
        if level == 'section':
            self.sections = sections
        elif level == 'bear':
            self.sections = sections
            self.bears = bears
        self.section_match_method = section_match_method
        self.allowed_sources = allowed_sources
        self.allowed_extractors = allowed_extractors

    def check_belongs_to_scope(self,
                               section_name,
                               bear_name):
        """
        Checks if the given section_name and bear_name
        belong to the ``InfoScope`` or not.
        """
        if self.level == 'global':
            return True

        elif self.level == 'section':
            if section_name in self.sections:
                return True
        else:
            if self.sections:
                if (section_name in self.sections and
                        bear_name in self.bears):
                    # list of allowed section exists and
                    # the given section is included in it.
                    # belongs = True
                    return True
            else:
                if bear_name in self.bears:
                    return True

        return False

    def check_is_applicable_information(self, section, info):
        """
        Checks if the given ``Info`` instance contains
        information applicable to the ``InfoScope`` or not
        based on the attributes `allowed_sources` and
        `allowed_extractors`. If none of them is specified, True
        is returned.
        """
        if self.section_match_method and section.get('files').value:
            if not self.section_match_method(section['files'], info):
                return False

        if not self.allowed_sources and not self.allowed_extractors:
            return True

        elif self.allowed_sources and self.allowed_extractors:
            if (info.source in self.allowed_sources and
                    isinstance(info.extractor, self.allowed_extractors)):
                return True

        else:
            if (info.source in self.allowed_sources or
                    isinstance(info.extractor, self.allowed_extractors)):
                return True

        return False
