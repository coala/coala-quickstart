from gemfileparser import GemfileParser

from coala_quickstart.info_extraction.InfoExtractor import InfoExtractor
from coala_quickstart.info_extraction.Information import (
    ProjectDependencyInfo, VersionInfo)


class GemfileInfoExtractor(InfoExtractor):
    supported_files = ('Gemfile',)

    spec_references = ['https://gitlab.com/coala/GSoC-2017/issues/167', ]
    supported_information_kinds = (
        ProjectDependencyInfo, VersionInfo)

    def parse_file(self, fname, file_content):
        parser = GemfileParser(fname)
        return parser.parse()

    def find_information(self, fname, parsed_file):
        results = []
        for grp, deps in parsed_file.items():
            for dep in deps:
                results.append(
                    ProjectDependencyInfo(
                        fname,
                        dep.name,
                        version=VersionInfo(fname, dep.requirement),
                        url=dep.source))

        return results
