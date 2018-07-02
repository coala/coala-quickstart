from coalib.bearlib.abstractions.Linter import linter


@linter(executable='some_lint',
        output_format='regex',
        output_regex=r'.+:(?P<line>\d+):(?P<message>.*)')
class YetAnotherLinterBear:
    CAN_DETECT = {'Syntax', 'Security'}
    CAN_FIX = {'Formatting'}
    LANGUAGES = {'Javascript'}

    @staticmethod
    def create_arguments(filename, file, config_file, nonopsetting,
                         someoptionalsetting=True):
        return ()
