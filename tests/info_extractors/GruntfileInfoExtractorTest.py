import os
import unittest

from coala_quickstart.info_extractors.GruntfileInfoExtractor import (
    GruntfileInfoExtractor)
from coala_quickstart.info_extraction.Information import (
    IncludePathsInfo, IgnorePathsInfo, LintTaskInfo, MentionedTasksInfo)
from tests.TestUtilities import generate_files


test_file = """
'use strict';

/* jshint node: true */
module.exports = function ( grunt ) {
    grunt.loadNpmTasks( 'grunt-contrib-concat' );
    grunt.loadNpmTasks( 'grunt-contrib-copy' );
    grunt.loadNpmTasks( 'grunt-contrib-csslint' );
    grunt.loadNpmTasks( 'grunt-contrib-cssmin' );
    grunt.loadNpmTasks( 'grunt-contrib-jshint' );
    grunt.loadNpmTasks( 'grunt-contrib-qunit' );
    grunt.loadNpmTasks( 'grunt-contrib-uglify' );
    grunt.loadNpmTasks( 'grunt-contrib-watch' );
    grunt.loadNpmTasks( 'grunt-jscs' );
    // Project configuration.
    grunt.initConfig( {
        pkg: grunt.file.readJSON( 'package.json' ),
        concat: {
            options: {
                banner: '<%= meta.banner %>'
            },
            dist: {
                src: [
                    'src/jquery.ime.js',
                    'src/jquery.ime.selector.js',
                    'src/jquery.ime.preferences.js',
                    'src/jquery.ime.inputmethods.js'
                ],
                dest: 'dist/jquery.ime/<%= pkg.name %>.js'
            }
        },
        uglify: {
            options: {
                banner: '<%= meta.banner %>'
            },
            dist: {
                files: {
                    'dist/jquery.ime/<%= pkg.name %>.min.js': [
                        'src/jquery.ime.js',
                        'src/jquery.ime.selector.js',
                        'src/jquery.ime.preferences.js',
                        'src/jquery.ime.inputmethods.js',
                        'libs/rangy/rangy-core.js'
                    ]
                }
            }
        },
        copy: {
            dist: {
                files: {
                    'dist/jquery.ime/': [
                        'rules/**',
                        'images/**',
                        'css/**'
                    ]
                }
            }
        },
        qunit: {
            files: [ 'test/index.html' ]
        },
        jshint: {
            options: {
                jshintrc: true
            },
            all: [
                '*.js',
                'src/*.js',
                'rules/**/*.js',
                'test/**/*.js'
            ]
        },
        jscs: {
            fix: {
                options: {
                    fix: true
                },
                src: '<%= jshint.all %>'
            },
            main: {
                src: '<%= jshint.all %>'
            }
        },
        csslint: {
            all: [
                'css/**/*.css'
            ]
        },
        some_lint_task: {
            ignore: [
                'foo/**.bar'
            ]
        },
        watch: {
            files: [
                '.{csslintrc,jscsrc,jshintignore,jshintrc}',
                '<%= jshint.all %>',
                '<%= csslint.all %>'
            ],
            tasks: 'lint'
        }
    } );

    // Default task.
    grunt.registerTask( 'lint', [
        'jshint', 'jscs:main', 'csslint', 'some_lint_task'] );
    grunt.registerTask( 'build', [ 'concat', 'uglify', 'copy' ] );
    grunt.registerTask( 'test', [ 'build', 'qunit' ] );
    grunt.registerTask( 'default', [ 'lint', 'test' ] );
};
"""


class GruntfileInfoExtractorTest(unittest.TestCase):

    def setUp(self):
        self.current_dir = os.getcwd()

    def test_extracted_information(self):

        with generate_files(
              ['Gruntfile.js'],
              [test_file],
              self.current_dir) as gen_file:

            self.uut = GruntfileInfoExtractor(
                ['Gruntfile.js'],
                self.current_dir)

            extracted_info = self.uut.extract_information()
            extracted_info = extracted_info[os.path.normcase('Gruntfile.js')]

            information_types = extracted_info.keys()

            csslint_include_paths = ['css/**/*.css']
            jshint_include_paths = [
                '*.js', 'src/*.js', 'rules/**/*.js', 'test/**/*.js']

            jshint_config = {
                'options': {
                    'jshintrc': 'true'
                },
                'all': ['*.js', 'src/*.js', 'rules/**/*.js', 'test/**/*.js']
            }

            jscs_config = {
                'fix': {
                    'options': {
                        'fix': 'true'
                    },
                    'src': '<%= jshint.all %>'
                },
                'main': {
                    'src': '<%= jshint.all %>'
                }
            }

            csslint_config = {
                'all': ['css/**/*.css']
            }

            some_lint_task_config = {
                'ignore': ['foo/**.bar']
            }

            # Linter information contained in test 'Gruntfile.js' file
            # in the form of tuple
            # (linter_name, include_paths, ignore_paths, config)
            defined_info = [
                ('csslint', csslint_include_paths, None, None, csslint_config),
                ('jshint', jshint_include_paths, None, None, jshint_config),
                ('jscs', None, None, None, jscs_config),
                ('some_lint_task', None, ['foo/**.bar'],
                    None, some_lint_task_config)]
            info_name = 'LintTaskInfo'

            self.assertIn(info_name, information_types)
            info_to_match = extracted_info[info_name]
            names_to_match = [i.value for i in info_to_match]
            include_paths_to_match = [i.include_paths.value
                                      if i.include_paths else None
                                      for i in info_to_match]
            ignore_paths_to_match = [i.ignore_paths.value
                                     if i.ignore_paths else None
                                     for i in info_to_match]
            config_to_match = [i.config for i in info_to_match]
            self.assertEqual(len(defined_info), len(names_to_match))
            for info in defined_info:
                self.assertIn(info[0], names_to_match)
                self.assertIn(info[1], include_paths_to_match)
                self.assertIn(info[2], ignore_paths_to_match)
                if info[3] is not None:
                    self.assertIn(info[3], config_to_match)

            tasks_used = [
                'grunt-contrib-concat', 'grunt-contrib-copy',
                'grunt-contrib-csslint', 'grunt-contrib-cssmin',
                'grunt-contrib-jshint', 'grunt-contrib-qunit',
                'grunt-contrib-uglify', 'grunt-contrib-watch', 'grunt-jscs']
            info_name = 'MentionedTasksInfo'
            self.assertIn(info_name, information_types)
            info_to_match = extracted_info[info_name]
            tasks_lists = [t.value for t in info_to_match]
            tasks_to_match = []
            for tasks in tasks_lists:
                tasks_to_match += tasks
            for task in tasks_used:
                self.assertIn(task, tasks_to_match)
