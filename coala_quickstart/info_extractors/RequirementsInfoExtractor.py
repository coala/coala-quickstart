from requirements import parse

from coala_quickstart.info_extraction.InfoExtractor import InfoExtractor
from coala_quickstart.info_extraction.Information import (
    ProjectDependencyInfo, VersionInfo)


class RequirementsInfoExtractor(InfoExtractor):
    supported_file_globs = ("requirements.txt",)

    supported_information_kinds = (
        ProjectDependencyInfo, VersionInfo)

    def parse_file(self, fname, file_content):
        parsed_file = []
        with open(fname, 'r') as f:
            parsed_file = parse(f)
        return parsed_file

    def find_information(self, fname, parsed_file):
        results = []
        for dependency in parsed_file:
            results.append(
                ProjectDependencyInfo(
                    fname,
                    dependency.name,
                    # FIXME: VersionInfo is a string, that stores only the
                    # first version.
                    version=VersionInfo(fname,
                                        ''.join(''.join(dependency.specs[0])))
                )
            )

        return results
