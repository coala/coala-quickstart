import copy
import random
import re
from collections import defaultdict


from coala_quickstart.Constants import (
    IMPORTANT_BEAR_LIST, ALL_CAPABILITIES, DEFAULT_CAPABILTIES)
from coala_quickstart.Strings import BEAR_HELP
from coala_quickstart.generation.SettingsFilling import is_autofill_possible
from coalib.bearlib.abstractions.LinterClass import LinterClass
from coalib.settings.ConfigurationGathering import get_filtered_bears
from coalib.misc.DictUtilities import inverse_dicts


def filter_relevant_bears(used_languages,
                          printer,
                          arg_parser,
                          extracted_info,
                          log_printer=None):
    """
    From the bear dict, filter the bears per relevant language.

    :param used_languages:
        A list of tuples with language name as the first element
        and percentage usage as the second element; sorted by
        percentage usage.
    :param printer:
        ``ConsolePrinter`` object to be used for console interactions.
    :param arg_parser:
        ``argparse.ArgumentParser`` object containing the arguments
        passed.
    :param extracted_info:
        list of information extracted from ``InfoExtractor`` classes.
    :return:
        A dict with language name as key and bear classes as value.
    """
    args = arg_parser.parse_args() if arg_parser else None
    used_languages.append(('All', 100))

    bears_by_lang = {
        lang: set(inverse_dicts(*get_filtered_bears([lang],
                                                    log_printer,
                                                    arg_parser,
                                                    silent=True)).keys())
        for lang, _ in used_languages
    }

    # Each language would also have the language independent bears. We remove
    # those and put them in the "All" category.
    all_lang_bears = bears_by_lang['All']
    bears_by_lang = {lang: bears_by_lang[lang] - bears_by_lang['All']
                     for lang, _ in used_languages}
    bears_by_lang['All'] = all_lang_bears

    selected_bears = {}
    candidate_bears = copy.copy(bears_by_lang)
    to_propose_bears = {}

    # Initialize selected_bears with IMPORTANT_BEAR_LIST
    for lang, lang_bears in candidate_bears.items():
        if lang_bears and lang in IMPORTANT_BEAR_LIST:
            selected_bears[lang] = set()
            for bear in lang_bears:
                if bear.__name__ in IMPORTANT_BEAR_LIST[lang]:
                    selected_bears[lang].add(bear)
        if lang_bears and lang not in IMPORTANT_BEAR_LIST:
            selected_bears[lang] = set(lang_bears)

        candidate_bears[lang] = set(
            [bear for bear in lang_bears
             if lang in selected_bears and
             bear not in selected_bears[lang]])

    if not args.no_filter_by_capabilities:
        # Ask user for capablities
        user_selected_capabilities = set()
        if not args.non_interactive:
            user_selected_capabilities = ask_to_select_capabilties(
                list(ALL_CAPABILITIES), list(DEFAULT_CAPABILTIES), printer)

        desired_capabilities = (
            user_selected_capabilities if user_selected_capabilities
            else DEFAULT_CAPABILTIES)

        # Filter bears based on capabilties
        for lang, lang_bears in candidate_bears.items():
            # Eliminate bears which doesn't contain the desired capabilites
            capable_bears = get_bears_with_given_capabilities(
                lang_bears, desired_capabilities)
            candidate_bears[lang] = capable_bears

    lint_task_info = extracted_info.get('LintTaskInfo', [])
    project_dependency_info = extracted_info.get('ProjectDependencyInfo', [])

    # Use lint_task_info to propose bears to user.
    for lang, lang_bears in candidate_bears.items():
        matching_linter_bears = get_matching_linter_bears(
                lang_bears, lint_task_info)
        to_propose_bears[lang] = matching_linter_bears

    # Use project_dependency_info to propose bears to user.
    for lang, lang_bears in candidate_bears.items():
        matching_dep_bears = get_bears_with_matching_dependencies(
            lang_bears, project_dependency_info)
        if to_propose_bears.get(lang):
            to_propose_bears[lang].update(matching_dep_bears)
        else:
            to_propose_bears[lang] = matching_dep_bears

    for lang, lang_bears in to_propose_bears.items():
        for bear in lang_bears:
            # get the non-optional settings of the bears
            settings = bear.get_non_optional_settings()
            if settings:
                user_input_reqd = False
                for setting in settings:
                    if not is_autofill_possible(
                            setting, lang, bear, extracted_info):
                        user_input_reqd = True
                        break

                if user_input_reqd:
                    # Ask user to activate the bear
                    if (args and not args.non_interactive and
                            prompt_to_activate(bear, printer)):
                        selected_bears[lang].add(bear)
                else:
                    # All the non-optional settings can be filled automatically
                    selected_bears[lang].add(bear)
            else:
                # no non-optional setting, select it right away!
                selected_bears[lang].add(bear)

    if not args.no_filter_by_capabilities:
        # capabilities satisfied till now
        satisfied_capabilities = get_bears_capabilties(selected_bears)
        remaining_capabilities = {
            lang: [cap for cap in desired_capabilities
                   if lang in satisfied_capabilities and
                   cap not in satisfied_capabilities[lang]]
            for lang in candidate_bears}

        filtered_bears = {}
        for lang, lang_bears in candidate_bears.items():
            filtered_bears[lang] = get_bears_with_given_capabilities(
                lang_bears, remaining_capabilities[lang])

        # Remove overlapping capabilty bears
        filtered_bears = remove_bears_with_conflicting_capabilties(
            filtered_bears)

        # Add to the selectecd_bears
        for lang, lang_bears in filtered_bears.items():
            if not selected_bears.get(lang):
                selected_bears[lang] = lang_bears
            else:
                selected_bears[lang].update(lang_bears)

    return selected_bears


def get_non_optional_settings(bears):
    """
    From the bear dict, get the non-optional settings.

    :param bears:
        A dict with language name as key and bear classes as value.
    :return:
        A dict with Bear class as key and bear non-optional settings as value.
    """
    non_optional_settings = {}
    for language in bears:
        for bear in bears[language]:
            if bear not in non_optional_settings:
                needed = bear.get_non_optional_settings()
                # FIXME: This only finds non-optional settings for immediate
                # dependencies.  See https://github.com/coala/coala/issues/3149
                for bear_dep in bear.BEAR_DEPS:
                    needed.update(bear_dep.get_non_optional_settings())

                non_optional_settings[bear] = needed

    return non_optional_settings


def get_non_optional_settings_bears(bears):
    """
    Return tuple of bears with non optional settings.

    :param unusable_bears:
        A collection of Bear classes.
    """
    non_optional_settings = get_non_optional_settings(bears)
    non_optional_settings = tuple(bear for bear, settings
                                  in non_optional_settings.items()
                                  if settings)
    return non_optional_settings


def remove_unusable_bears(bears, unusable_bears):
    """
    From the bears dict, filter the bears appearing in unusable_bears.

    :param bears:
        A dict with language name as key and bear classes as value.
    :param unusable_bears:
        A collection of Bear classes.
    """
    for language, language_bears in bears.items():
        for bear in tuple(language_bears):
            if bear in unusable_bears:
                bears[language].remove(bear)


def print_relevant_bears(printer, relevant_bears, label='relevant'):
    """
    Prints the relevant bears in sections separated by language.

    :param printer:
        A ``ConsolePrinter`` object used for console interactions.
    :param relevant_bears:
        A dict with language name as key and bear classes as value.
    """
    if label == 'relevant':
        printer.print(BEAR_HELP)

    printer.print('\nBased on the languages used in project the following '
                  'bears have been identified to be %s:' % label)
    for language in relevant_bears:
        printer.print('    [' + language + ']', color='green')
        for bear in relevant_bears[language]:
            printer.print('    ' + bear.name, color='cyan')
        printer.print('')


def generate_requirements_map(bears):
    """
    For the given list of bears, returns a dict of the form
    ```
    {
        “requirement_name” : {
            “requirement_type” : NpmRequirement,
            "version" : ">=0.4.2"
            “bear” : "bear_wrapping_the_executable",
        }
    }
    ```
    """
    requirements_meta = {}
    for bear in bears:
        for req in bear.REQUIREMENTS:
            to_add = {
                'bear': bear,
                'version': req.version,
                'type': req.type,
            }
            requirements_meta[req.package] = to_add
    return requirements_meta


def get_bears_with_matching_dependencies(bears, dependency_info):
    """
    Matches the `REQUIREMENTS` filed of bears against a list
    of ``ProjectDependencyInfo`` instances to return the bears
    that match the dependency requirements.

    :param bears:
        list of Bears
    :param dependency_info:
        list of ``ProjectDependencyInfo`` instances.
    :return:
        list of Bears whose all the requirements match in the
        given `dependency_info` list.
    """
    requirements_map = generate_requirements_map(bears)
    matched_requirements = []
    for req, req_info in requirements_map.items():
        for dep in dependency_info:
            # Check if names of requirements match
            if dep.value == req:
                installed_version = dep.version.value
                bear_requirement_version = req_info['version']
                if installed_version and bear_requirement_version:
                    is_newer_version = is_version_newer(
                        installed_version, bear_requirement_version)
                    if is_newer_version:
                        matched_requirements.append(req)
                else:
                    # No comparison can be made as the info is missing
                    # Assuming there are more chances of versions to be
                    # compatible in most of the cases, add the req to
                    # matched_requirements.
                    matched_requirements.append(req)

    result = set()
    for bear in bears:
        all_req_satisfied = True
        for req in bear.REQUIREMENTS:
            if req.package not in matched_requirements:
                all_req_satisfied = False
        if bear.REQUIREMENTS and all_req_satisfied:
            result.add(bear)
    return result


def get_matching_linter_bears(bears, lint_tasks_info):
    """
    Matches the `REQUIREMENTS` filed of bears against a list
    of ``LintTasksInfo`` instances to return the bears
    that match the dependency requirements.

    :param bears:
        list of Bears
    :param dependency_info:
        list of ``LintTasksInfo`` instances.
    :return:
        list of Bears which wrap the linters in the
        given `lint_task_info` list.
    """
    matched_bears = set()
    for task in lint_tasks_info:
        for bear in bears:
            if (issubclass(bear, LinterClass) and
                    bear.get_executable() == task.value):
                matched_bears.add(bear)
                break
            for req in bear.REQUIREMENTS:
                if req.package == task.value:
                    matched_bears.add(bear)
                    break

    return matched_bears


def get_bears_with_given_capabilities(bears, capabilities):
    """
    Returns a list of bears which contain at least one on the
    capability in ``capabilities`` list.

    :param bears:        list of bears.
    :param capabilities: A list of bear capabilities that coala
                         supports
    """
    result = set()
    for bear in bears:
        can_detect_caps = [c for c in list(bear.CAN_DETECT)]
        can_fix_caps = [c for c in list(bear.CAN_FIX)]
        eligible = False
        for cap in capabilities:
            if cap in can_fix_caps or cap in can_detect_caps:
                eligible = True
        if eligible:
            result.add(bear)

    return result


def get_bears_capabilties(bears_by_lang):
    """
    Return a dict of capabilties of all the bears by language
    in the `bears_by_lang` dictionary.

    :param bears_by_lang: dict with language names as keys
                          and the list of bears as values.
    :returns:             dict of capabilities by language.
    """
    result = {}
    for lang, lang_bears in bears_by_lang.items():
        result[lang] = set()
        for bear in lang_bears:
            for cap in bear.CAN_FIX | bear.CAN_DETECT:
                result[lang].add(cap)
    return result


def generate_capabilties_map(bears_by_lang):
    """
    Generates a dictionary of capabilities, languages and the
    corresponding bears from the given ``bears_by_lang`` dict.

    :param bears_by_lang: dict with language names as keys
                          and the list of bears as values.
    :returns:             dict of the form
                          {
                            "language": {
                                "detect": [list, of, bears]
                                "fix": [list, of, bears]
                            }
                          }
    """

    def nested_dict():
        return defaultdict(dict)
    capabilities_meta = defaultdict(nested_dict)

    # collectiong the capabilities meta-data
    for lang, bears in bears_by_lang.items():
        can_detect_meta = inverse_dicts(
            *[{bear: list(bear.CAN_DETECT)} for bear in bears])
        can_fix_meta = inverse_dicts(
            *[{bear: list(bear.CAN_FIX)} for bear in bears])

        for capability, bears in can_detect_meta.items():
            capabilities_meta[capability][lang]['DETECT'] = bears

        for capability, bears in can_fix_meta.items():
            capabilities_meta[capability][lang]['FIX'] = bears
    return capabilities_meta


def remove_bears_with_conflicting_capabilties(bears_by_lang):
    """
    Eliminate bears having no unique capabilities among the other
    bears present in the list.
    Gives preference to:
    - The bears already having dependencies installed.
    - Bears that can fix the capability rather that just detecting it.

    :param bears_by_lang: dict with language names as keys
                          and the list of bears as values.
    """
    result = {}
    for lang, bears in bears_by_lang.items():
        lang_result = set()
        capabilities_map = generate_capabilties_map({lang: bears})
        for cap in capabilities_map.keys():
            # bears that can fix the ``cap`` capabilitiy
            fix_bears = capabilities_map[cap][lang].get('FIX')
            if fix_bears:
                for bear in fix_bears:
                    if bear.check_prerequisites() is True:
                        # The dependecies for bear are already installed,
                        # so select it.
                        lang_result.add(bear)
                        break
                # None of the bear has it's dependency installed, select
                # a random bear.
                lang_result.add(random.choice(fix_bears))
                break
            # There were no bears to fix the capability
            detect_bears = capabilities_map[cap][lang].get('DETECT')
            if detect_bears:
                for bear in detect_bears:
                    if bear.check_prerequisites() is True:
                        lang_result.add(bear)
                        break
                lang_result.add(random.choice(detect_bears))
                break
        result[lang] = lang_result

    return result


def is_version_newer(semver1, semver2):
    """
    Compares version strings and checks if the semver1 is
    newer than semver2.
    :returns:
        True if semver1 is latest or matches semver2,
        False otherwise.
    """
    semver1 = tuple(map(int, (re.sub('[^0-9\.]', '', semver1).split('.'))))
    semver2 = tuple(map(int, (re.sub('[^0-9\.]', '', semver2).split('.'))))
    return semver1 >= semver2


def prompt_to_activate(bear, printer):
    """
    Prompts the user to activate a bear.

    :param bear:    The name of the bear.
    :param printer: A `ConsolePrinter` object for console interaction.
    """
    PROMPT_TO_ACTIVATE_STR = ('coala-quickstart has found {} to be useful '
                              'based of dependencies discovered from your '
                              'project files. \n Would you like to activate '
                              'it? (y/n)')
    printer.print(PROMPT_TO_ACTIVATE_STR)

    choice = input().lower()

    if choice.startswith('y'):
        return True
    elif choice.startswith('n'):
        return False
    else:
        return prompt_to_activate(bear, printer)


def ask_to_select_capabilties(all_capabilities,
                              default_capabilities,
                              console_printer):
    """
    Asks the users to select capabilties out of all_capabilities.
    """
    all_capabilities = sorted(all_capabilities)
    PROMPT_QUESTION = ('What would you like the bears to detect or fix? '
                       'Please select some bear capabilities using '
                       "their numbers or just press 'Enter' to select"
                       'default capabilities (highlighted in green)')
    console_printer.print(PROMPT_QUESTION, color='yellow')

    default_options = []
    total_options = len(all_capabilities) + 1

    for idx, cap in enumerate(all_capabilities):
        color = 'cyan'
        if cap in default_capabilities:
            color = 'green'
            default_options.append(idx)
        console_printer.print(
            '    {}. {}'.format(idx + 1, cap), color=color)
    console_printer.print(
        '    {}. Select all default capabilities.'.format(
            total_options), color='cyan')

    selected_numbers = []
    try:
        selected_numbers = list(map(int, re.split('\D+', input())))
    except Exception:
        # Parsing failed, choose all the default capabilities
        selected_numbers = [total_options]

    selected_capabilties = []

    for num in selected_numbers:
        if num >= 0 and num < total_options:
            selected_capabilties.append(all_capabilities[int(num) - 1])
        elif num == total_options:
            selected_capabilties += default_capabilities
        else:
            console_printer.print(
                '{} is not a valid option. Please choose the right'
                ' option numbers'.format(str(num)))
            ask_to_select_capabilties(all_capabilities,
                                      default_capabilities,
                                      console_printer)

    return set(selected_capabilties)
