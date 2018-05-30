from coala_quickstart.info_extractors.EditorconfigInfoExtractor import (
    EditorconfigInfoExtractor)
from coala_quickstart.info_extractors.PackageJSONInfoExtractor import (
    PackageJSONInfoExtractor)
from coala_quickstart.info_extractors.GemfileInfoExtractor import (
    GemfileInfoExtractor)
from coala_quickstart.info_extractors.GruntfileInfoExtractor import (
    GruntfileInfoExtractor)


def collect_info(project_dir):
    """
    Collects information extracted by various ``InfoExtractor``
    classes and returns them as a dictionary.
    """
    editorconfig_info = EditorconfigInfoExtractor(
        ['.editorconfig'], project_dir).extract_information()

    package_json_info = PackageJSONInfoExtractor(
        ['package.json'], project_dir).extract_information()

    gemfile_info = GemfileInfoExtractor(
        ['Gemfile'], project_dir).extract_information()

    gruntfile_info = GruntfileInfoExtractor(
        ['Gruntfile.js'], project_dir).extract_information()

    extracted_info = aggregate_info([
        editorconfig_info, package_json_info, gemfile_info, gruntfile_info])

    return extracted_info


def aggregate_info(infoextractors):
    """
    Aggregates inforamtion extracted from multiple ``InfoExtractor``
    instances to one dictionary.

    :param infoextractors: list of values of ``information`` attribute
                           of different ``InfoExtractor`` instances.
    """
    result = {}
    for ie in infoextractors:
        for fname, extracted_info in ie.items():
            for info_name, info_instances in extracted_info.items():
                if result.get(info_name):
                    result[info_name] += info_instances
                else:
                    result[info_name] = info_instances
    return result
