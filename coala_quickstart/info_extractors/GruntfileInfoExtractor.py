import logging

from pyjsparser import PyJsParser

from coala_quickstart.info_extraction.InfoExtractor import InfoExtractor
from coala_quickstart.info_extraction.Information import (
    IncludePathsInfo, IgnorePathsInfo, LintTaskInfo, MentionedTasksInfo)
from coala_quickstart.info_extractors.Utilities import (
    search_object_recursively)


class GruntfileInfoExtractor(InfoExtractor):
    supported_file_globs = ('Gruntfile.js',)
    supported_info_kinds = (LintTaskInfo, MentionedTasksInfo)

    def parse_file(self, fname, file_content):
        js_parser = PyJsParser()
        return js_parser.parse(file_content)

    def find_information(self, fname, parsed_file):
        results = []

        npm_tasks = self.get_npm_tasks(parsed_file)
        linters = self.extract_lint_subtasks(parsed_file)
        config = self.get_configurations(parsed_file, linters)

        if npm_tasks:
            results.append(
                MentionedTasksInfo(fname, npm_tasks))

        for linter in linters:
            include_paths_info = None
            ignore_paths_info = None
            linter_config = None
            if config.get(linter):
                linter_config = config[linter]
                globs = self.extract_globs(linter_config)
                linter_config = self.get_task_config(linter_config)
                if globs.get('include_globs'):
                    include_paths = globs['include_globs']
                    include_paths_info = IncludePathsInfo(
                        fname, include_paths) if include_paths else None
                if globs.get('ignore_globs'):
                    ignore_paths = globs['ignore_globs']
                    ignore_paths_info = IgnorePathsInfo(
                        fname, ignore_paths) if ignore_paths else None
            results.append(
                LintTaskInfo(fname,
                             linter,
                             None,
                             include_paths_info,
                             ignore_paths_info,
                             linter_config))

        return results

    def extract_lint_subtasks(self, parsed_file):
        """
        Extract the lint subtasks from the parsed JS file.
        Looks for identifiers like:
        ``grunt.registerTask( "lint", [ "csslint", "jshint" ] );``

        :param parsed_file:
            An instance of PyJsParser().parse
        :return:
            A list of lint subtasks
        """
        # task names to match
        keys_to_match = ['lint']

        # Serch for grunt.registerTask() identifiers
        search_results = search_object_recursively(parsed_file, 'callee', {
            'computed': False,
            'type': 'MemberExpression',
            'property': {
                'name': 'registerTask',
                'type': 'Identifier',
                },
            'object': {
                'name': 'grunt',
                'type': 'Identifier',
                }
            })

        lint_subtasks = []
        is_lint = False

        for res in search_results:
            arguments = res['object'].get('arguments')
            # check if the task is a lint sub-task
            if arguments:
                for arg in arguments:
                    if arg.get('value') in keys_to_match:
                        is_lint = True
                        break

            if is_lint:
                for arg in arguments:
                    if (arg.get('elements') and
                            arg.get('type') == 'ArrayExpression'):
                        lint_subtasks += [
                            elem['value'].split(':')[0]
                            for elem in arg['elements']
                        ]
                        is_lint = False

        return lint_subtasks

    def get_configurations(self, parsed_file, tasks):
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
        :param tasks:
            list of task names for which configurations are
            to be extracted.
        :return:
            A list of configuration dicts
        """
        result = {}
        search_results = search_object_recursively(
            parsed_file, 'callee',
            {
                'computed': False,
                'type': 'MemberExpression',
                'property': {
                    'name': 'initConfig',
                    'type': 'Identifier',
                },
                'object': {
                    'name': 'grunt',
                    'type': 'Identifier',
                }
            })

        for s in search_results:
            if 'object' in s and 'arguments' in s['object']:
                for arg in s['object']['arguments']:
                    if 'properties' in arg:
                        for p in arg['properties']:
                            if ('key' in p and 'name' in p['key']
                                    and p['key']['name'] in tasks):
                                name = p['key']['name']
                                result[name] = p.get('value')

        return result

    def get_npm_tasks(self, parsed_file):
        """
        Extracts the npm tasks used in the Gruntfile.
        Searches for the identifiers like:
        ``grunt.loadNpmTasks( "grunt-contrib-concat" );``
        """
        search_results = search_object_recursively(
            parsed_file, 'callee',
            {
                'computed': False,
                'type': 'MemberExpression',
                'property': {
                    'name': 'loadNpmTasks',
                    'type': 'Identifier',
                    },
                'object': {
                    'name': 'grunt',
                    'type': 'Identifier',
                    }
            })

        tasks_found = []

        for result in search_results:
            if result.get('object'):
                try:
                    task_name = result['object']['arguments'][0]['value']
                    tasks_found.append(task_name)
                except KeyError:
                    pass

        return tasks_found

    def extract_literals_from_expression(self, obj):
        """
        From the given expression of PyJsParser.parse() instance,
        return the elements of type "Literal" by searching recursively.

        :param obj:
            A complete instance of PyJsParser.parse() or a part of it.
        :returns:
            list containing values of all the elements of type "Literal"
            found in the obj.
        """
        if (obj and obj.get('type') == 'ArrayExpression' and
                'elements' in obj.keys()):
            return [
                elem['value']
                for elem in obj['elements'] if elem['type'] == 'Literal'
            ]

        elif obj and obj.get('type') == 'ObjectExpression':
            if (obj.get('value') and
                obj['value']['type'] == 'ArrayExpression' and
                    'elements' in obj['value'].keys()):
                return [
                    elem['value']
                    for elem in obj['elements'] if elem['type'] == 'Literal'
                ]
            else:
                return self.extract_literals_from_expression(obj.get('value'))

        elif obj and obj.get('type') == 'Property':
            return self.extract_literals_from_expression(obj.get('value'))

        else:
            return []

    def get_task_config(self, parsed_config):
        """
        From the parsed configuration object for a task,
        extract and return the config settings in the form
        of a python dict.

        :param parsed_config:
            A portion of  `PyJsParser().parse` instance of
            "Gruntfile.js" that contains configuration of
            a task defined appearing in "Gruntfile.js" in the form
            of `grunt.initConfig({"task": "config"})`
        :returns:
            A python dictionary of configurations in the form of
            key-value pairs.
        """
        result = {}
        for prop in parsed_config['properties']:
            prop_value = None
            if prop['value']['type'] == 'Identifier':
                prop_value = prop['value']['name']

            elif prop['value']['type'] == 'Literal':
                prop_value = prop['value']['value']

            elif prop['value']['type'] == 'ObjectExpression':
                prop_value = self.get_task_config(prop['value'])

            elif prop['value']['type'] == 'ArrayExpression':
                prop_value = self.extract_literals_from_expression(prop)

            else:
                logging.warn(
                    'quickstart was not able to parse the value '
                    'of the config {}'.format(
                        prop['key']['name']))

            result[prop['key']['name']] = prop_value

        return result

    def extract_globs(self, parsed_config):
        """
        Extract the path glob literals matching ceratin keys
        from the ``PyJsParser().parse`` instance.

        :param parsed_file:
            An instance of ``PyJsParser().parse``
        :return:
            A dictionary with keys `include_globs` and `ignore_globs` and
            values being the corresponding list of globs.
        """
        to_use_keys = ['all', 'main', 'files', 'src', 'sources']
        to_ignore_keys = ['ignore', 'exclude']

        result = {
            'include_globs': [],
            'ignore_globs': [],
        }

        if parsed_config.get('type') == 'ObjectExpression':
            for prop in parsed_config['properties']:
                if prop['key']['name'] in to_use_keys:
                    result['include_globs'] += (
                        self.extract_literals_from_expression(prop))
                elif prop['key']['name'] in to_ignore_keys:
                    result['ignore_globs'] += (
                        self.extract_literals_from_expression(prop))

        return result
