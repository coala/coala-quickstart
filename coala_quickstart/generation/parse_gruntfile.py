import os
from coala_quickstart.Constants import NPM_BEARS_META
from coala_quickstart.generation.Utilities import search_dict_recursively

from pyjsparser import PyJsParser

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def parse_javascript_file(file_path):
    """
    Returns an instance of PyJsParser created
    from the given `file_path`
    """
    source_code = ''
    with open(file_path, 'r') as file:
        source_code = file.read()
    if source_code:
        js_parser = PyJsParser()
        parsed_code = js_parser.parse(source_code)
        return parsed_code
    return None


def extract_lint_subtasks_from_gruntfile(parsed_file):
    """
    Extract the lint subtasks from the parsed JS file.
    Looks for identifiers like:
    grunt.registerTask( 'lint', [ 'csslint', 'jshint' ] );

    :param parsed_file:
        An instance of PyJsParser().parse
    :return:
        A list of lint_subtasks
    """
    keys_to_match = ['lint']

    # Serch for grunt.registerTask() identifiers
    search_results = search_dict_recursively(parsed_file, "callee", {
        "computed": False,
        "type": "MemberExpression",
        "property": {
            "name": "registerTask",
            "type": "Identifier"
        },
        "object": {
            "name": "grunt",
            "type": "Identifier"
        }
        })

    lint_subtasks = []
    is_lint = False

    for res in search_results:
        arguments = res["object"].get('arguments')
        if arguments:
            for arg in arguments:
                if arg.get('value') in keys_to_match:
                    is_lint = True
                    break
        if is_lint:
            for arg in arguments:
                if "elements" in arg.keys() and \
                        arg["type"] == "ArrayExpression":
                    lint_subtasks = [
                        elem["value"].split(':')[0]
                        for elem in arg["elements"]
                    ]
            return lint_subtasks


def get_configurations_from_gruntfile(parsed_file, tasks):
    """
    Extract the configurations from the PyJsParser instance
    of a Gruntfile and return configuration data(if any) of
    the task provided. Looks for patterns like
    {
        grunt.initConfig(
            {
                some configuration objects
            }
    }

    :param parsed_file:
        An instance of PyJsParser().parse
    :return:
        A list of configuration dicts
    """
    init_config_data = {}
    result = {}
    search_results = search_dict_recursively(
        parsed_file, "callee",
        {
            "computed": False,
            "type": "MemberExpression",
            "property": {
                "name": "initConfig",
                "type": "Identifier"
                },
            "object": {
                "name": "grunt",
                "type": "Identifier"
                }
        })
    if search_results:
        init_config_data = search_results[0]["object"]
        arguments = init_config_data.get('arguments')
        if arguments:
            for arg in arguments:
                if arg.get("properties"):
                    for p in arg["properties"]:
                        if p["key"]["name"] in tasks:
                            name = p["key"]["name"]
                            result[name] = p["value"]
    return result


def extract_literals_from_expression(obj):
    """
    From the given expression of PyJsParser.parse() instance,
    return the elements of type "Literal" by searching recursively.
    """
    results = []
    if obj.get("type") == "ArrayExpression" and "elements" in obj.keys():
        results = [
            elem["value"]
            for elem in obj["elements"] if elem["type"] == "Literal"
        ]

    elif obj.get("type") == "ObjectExpression":
        if obj["value"]["type"] == "ArrayExpression" and \
                "elements" in obj["value"].keys():
            results = [
                elem["value"]
                for elem in obj["elements"] if elem["type"] == "Literal"
            ]
        else:
            return extract_literals_from_expression(obj["value"])

    elif obj.get("type") == "Property":
        return extract_literals_from_expression(obj["value"])

    return results


def extract_globs_from_parsefile(parsed_config):
    """
    Extract the path glob literals matching ceratin keys
     from the PyJsParser().parse instance.

    :param parsed_file:
        An instance of PyJsParser().parse
    :return:
        A dictionary with keys `use` and `ignore` and values being the
        corresponding list of globs.
    """
    to_use_keys = ['all', 'main', 'files', 'src', 'sources']
    to_ignore_keys = ['ignore', 'exclude']

    result = {
        "include": [],
        "ignore": []
    }
    if parsed_config.get("type") == "ObjectExpression":
        for prop in parsed_config["properties"]:
            if prop["key"]["name"] in to_use_keys:
                result["include"] = extract_literals_from_expression(prop)
            elif prop["key"]["name"] in to_ignore_keys:
                result["ignore"] = extract_elements_from_array_expression(prop)
    return result


def get_gruntfile_info(project_dir, filename="Gruntfile.js"):
    """
    Extract useful information from the `Gruntfile.js` of the project

    :param project_dir:
        Directory of the project
    :param filename:
        Name of the file, default `Gruntfile.js`
    :return:
        A list of dicts of the form
        {
            "linter": name of the lint-subtask,
            "bears": list of matching bears to the linter,
            "languages": list of languages affected by the linter,
            "include": list of file globs to include for the linter,
            "ignore": list of file globs to ignore for the linter,
        }
    """
    gruntfile = os.path.join(project_dir, filename)

    parsed_gruntfile = parse_javascript_file(gruntfile)

    linters = extract_lint_subtasks_from_gruntfile(parsed_gruntfile)

    config = get_configurations_from_gruntfile(parsed_gruntfile, linters)

    results = []

    for linter in linters[:]:
        linter_result = {
            "linter": linter,
            "bears": [],
            "languages": [],
            "include": [],
            "ignore": []
        }

        matching_bear = None

        if NPM_BEARS_META.get(linter):
            matching_bear = NPM_BEARS_META[linter]
            linter_result["bears"] = matching_bear["bears"]
            linter_result["languages"] = matching_bear["languages"]

        if matching_bear and config.get(linter):
            globs = extract_globs_from_parsefile(config[linter])
            if globs.get("include"):
                linter_result["include"] = globs["include"]
            if globs.get("ignore"):
                linter_result["ignore"] = globs["ignore"]

        results.append(linter_result)

    return results
