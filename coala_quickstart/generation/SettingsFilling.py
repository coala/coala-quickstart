
from termcolor import colored

from coalib.settings.Setting import Setting
from coalib.misc.Constants import TRUE_STRINGS, FALSE_STRINGS
from coala_quickstart.generation.InfoMapping import INFO_SETTING_MAPS
from coala_utils.string_processing.Core import join_names


def fill_section(section,
                 acquire_settings,
                 log_printer,
                 bears,
                 extracted_info):
    """
    Retrieves needed settings from given bears and asks the user for
    missing values.

    If a setting is requested by several bears, the help text from the
    latest bear will be taken.

    :param section:          A section containing available settings. Settings
                             will be added if some are missing.
    :param acquire_settings: The method to use for requesting settings. It will
                             get a parameter which is a dictionary with the
                             settings name as key and a list containing a
                             description in [0] and the names of the bears
                             who need this setting in all following indexes.
    :param log_printer:      The log printer for logging.
    :param bears:            All bear classes or instances.
    :param extracted_info:   A list of information extracted from the project
                             files by ``InfoExtractor`` classes.
    :return:                 The new section.
    """
    # Retrieve needed settings.
    prel_needed_settings = {}

    for bear in bears:
        needed = bear.get_non_optional_settings()
        for key in needed:
            if key in prel_needed_settings:
                prel_needed_settings[key]['bears'].append(bear.name)
            else:
                prel_needed_settings[key] = {
                    'help_text': needed[key][0],
                    'bears': [bear.name],
                    'type': needed[key][1],
                }

    # Strip away existent settings.
    needed_settings = {}
    for setting, setting_info in prel_needed_settings.items():
        if setting not in section:
            needed_settings[setting] = setting_info

    # Fill the settings with existing values if possible
    satisfied_settings = []

    for setting in needed_settings.keys():
        setting_bears = needed_settings[setting]['bears']
        setting_help_text = needed_settings[setting]['help_text']
        to_fill_values = list(autofill_value_if_possible(
            setting, section, setting_bears, extracted_info))

        if len(set(to_fill_values)) == 1:
            section[setting] = to_fill_values[0]
            satisfied_settings.append(setting)

        elif len(to_fill_values) > 1:
            section[setting] = resolve_anomaly(
                setting, setting_help_text, setting_bears, to_fill_values)
            satisfied_settings.append(setting)

        else:
            pass

    for setting in satisfied_settings:
        del needed_settings[setting]

    # Get missing ones.
    if len(needed_settings) > 0:
        new_vals = acquire_settings(log_printer, needed_settings, section)
        for setting, help_text in new_vals.items():
            section.append(Setting(setting, help_text))

    return section


def autofill_value_if_possible(setting_key,
                               section,
                               bears,
                               extracted_information):
    """
    For the given setting configurations, checks if there is a
    possiblity of filling the value from the extracted information,
    and returns the values if these value are applicable.

    :param setting_key:           The name of the setting to be checked
                                  for autofill.
    :param section:               The section to which the setting_key
                                  belongs.
    :param bears:                 list of bears having the setting_key
                                  as one of the settings.
    :param extracted_information: list of information extracted from
                                  ``InfoExtractor`` classes.
    :return:                      yields possible values that can be
                                  used to fill the setting_key.
    """
    if INFO_SETTING_MAPS.get(setting_key):
        for mapping in INFO_SETTING_MAPS[setting_key]:
            scope = mapping['scope']
            if (scope.check_belongs_to_scope(
                    section, bears)):
                # look for the values in extracted information
                # from all the ``InfoExtractor`` instances.
                values = extracted_information.get(
                    mapping['info_kind'].__name__)
                if values:
                    for val in values:
                        if scope.check_is_applicable_information(section, val):
                            yield mapping['mapper_function'](val)


def is_autofill_possible(setting_key,
                         section,
                         bears,
                         extracted_info):
    """
    Checks if it is possible to autofill the setting values.
    """
    if INFO_SETTING_MAPS.get(setting_key):
        for mapping in INFO_SETTING_MAPS[setting_key]:
            scope = mapping['scope']
            if (scope.check_belongs_to_scope(
                    section, bears)):
                values = extracted_info.get(
                    mapping['info_kind'].__name__)
                for val in values:
                    if scope.check_is_applicable_information(section, val):
                        return True
    return False


def resolve_anomaly(setting_name,
                    help_string,
                    associated_bears,
                    values):
    """
    Displays multiple possible values for the setting to the
    users and prompts them for actual value to be used.

    :param setting_name:     Name of setting for which multiple possible
                             values exist to fill.
    :param help_string:      string describing the setting.
    :param associated_bears: list of bears for which the setting is required.
    :param values:           list of possible values for the setting.
    :return:                 value provided by the user for the setting.
    """
    values = list(set(values))

    STR_ASK_FOR_CORRECT_VALUE = ('coala-quickstart has detected multiple '
                                 'potential values for the setting "{}" ({}) '
                                 'needed by {}. The detected values are: {}.\n'
                                 'Please provide the correct value to use:')
    REPORT_ANOMALY_COLOR = 'green'

    print(colored(STR_ASK_FOR_CORRECT_VALUE.format(setting_name,
                                                   help_string,
                                                   join_names(associated_bears),
                                                   join_names(values)),
                  REPORT_ANOMALY_COLOR))
    return input()


def require_setting(setting_name, setting_info, section):
    """
    This method is responsible for prompting a user about a missing setting and
    taking its value as input from the user.

    :param setting_name: Name of the setting missing
    :param setting_info: A dictionary of the form

    ::
        {
            "help_text": "help string for the setting",
            "bears": [SomeBear", "SomeOtherBear"],
            "type": bool
        }

    :param section:      The section the action corresponds to.
    :return:             The preferred value provided by the user
                         for the setting.
    """
    needed = join_names(setting_info['bears'])

    STR_GET_VAL_FOR_SETTING = ('\nPlease enter a value for the setting {} '
                               '({}) needed by {} for section {}: ')

    STR_REPORT_INVALID_VALUE_TYPE = ('coala-quickstart was unable to convert '
                                     'your input to the type {} required for '
                                     'the setting.')

    REQUIRED_SETTINGS_COLOR = 'green'
    REPORT_INVALID_TYPE_COLOR = 'cyan'

    user_input = ''

    while True:
        print(colored(STR_GET_VAL_FOR_SETTING.format(repr(setting_name),
                                                     setting_info['help_text'],
                                                     needed,
                                                     repr(section.name)),
                      REQUIRED_SETTINGS_COLOR))

        user_input = input()

        if setting_info['type']:
            try:
                if setting_info['type'] is bool:
                    processed_input = user_input.strip().strip('!').lower()
                    if processed_input in TRUE_STRINGS:
                        user_input = 'True'
                    elif processed_input in FALSE_STRINGS:
                        user_input = 'False'
                    else:
                        raise ValueError
                else:
                    setting_info['type'](user_input)

                break

            except ValueError:
                print(colored(
                    STR_REPORT_INVALID_VALUE_TYPE.format(setting_info['type']),
                    REPORT_INVALID_TYPE_COLOR))

    return user_input


def acquire_settings(log_printer, settings_dict, section):
    """
    This method prompts the user for the given settings.

    :param log_printer:
        Printer responsible for logging the messages. This is needed to comply
        with the interface.
    :param settings_names_dict:
        A dictionary with the settings name as key of the following form

    ::

        {
          "some_setting": {
              "help_text": "help string for the setting",
              "bears": [SomeBear", "SomeOtherBear"],
              "type": bool
        }

    :param section:
        The section the action corresponds to.
    :return:
        A dictionary with the settings name as key and the given value as
        value.
    """
    if not isinstance(settings_dict, dict):
        raise TypeError('The settings_names_dict parameter has to be a '
                        'dictionary.')

    result = {}
    for setting_name, setting_info in sorted(
            settings_dict.items(),
            key=lambda x: (join_names(x[1]['bears']), x[0])):
        # As quickstart generates language-based sections, the value for
        # `language` setting can be filled automatically.
        if setting_name == 'language':
            value = section.name
        else:
            value = require_setting(setting_name, setting_info, section)

        result.update({setting_name: value} if value is not None else {})

    return result
