import json
import logging

from coala_quickstart.info_extraction.InfoExtractor import InfoExtractor
from coala_quickstart.info_extraction.Information import (
    LicenseUsedInfo, ProjectDependencyInfo, IncludePathsInfo, ManFilesInfo,
    VersionInfo)


class PackageJSONInfoExtractor(InfoExtractor):
    supported_file_globs = ('package.json',)

    spec_references = [
        'https://docs.npmjs.com/files/package.json',
        'https://gitlab.com/coala/GSoC-2017/issues/167']

    supported_info_kinds = (
        LicenseUsedInfo,
        ProjectDependencyInfo,
        IncludePathsInfo,
        ManFilesInfo)

    def parse_file(self, fname, file_content):
        parsed_file = {}

        try:
            parsed_file = json.loads(file_content)
        except Exception:
            logging.warning('Error while parsing the file {}'.format(fname))

        return parsed_file

    def find_information(self, fname, parsed_file):
        results = []

        if parsed_file.get('license'):
            results.append(
                LicenseUsedInfo(fname, parsed_file['license']))

        if parsed_file.get('dependencies'):
            for package_name, version_range in (
                    parsed_file['dependencies'].items()):
                results.append(
                    ProjectDependencyInfo(
                        fname,
                        package_name,
                        self.__class__.__name__,
                        VersionInfo(fname, version_range)))

        if parsed_file.get('files'):
            results.append(
                IncludePathsInfo(fname, parsed_file['files']))

        if parsed_file.get('man'):
            results.append(
                ManFilesInfo(
                    fname,
                    parsed_file['man'],
                    keyword=parsed_file.get('name')))

        return results
