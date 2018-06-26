from coala_quickstart.generation.Utilities import (
    search_for_orig, get_all_args, get_default_args)


def in_annot(func, key):
    """
    Checks if a setting name as key is present in function
    annotations.
    :param func:
        Function object.
    :param key:
        The setting name as a string.
    :return:
        The value of type annotated or False.
    """
    return func.__annotations__[key] if key in func.__annotations__ else False


def in_annot_recursive(bear, key):
    """
    Checks if a setting name as key is present in function
    annotations, recursively through the bear dependencies.
    :param bear:
        The bear object.
    :param key:
        The setting name as a string.
    :return:
        The value of type annotated or False.
    """
    found = False
    func = bear.run
    if key in func.__annotations__:
        return func.__annotations__[key]
    else:
        found = False
        for dep in bear.BEAR_DEPS:
            found = in_annot_recursive(dep, key)
            if found is not False:
                return found
        return False


def in_default_args(func, key):
    """
    Checks if a setting name as key is present in function
    arguments with default value.
    :param func:
        Function object.
    :param key:
        The setting name as a string.
    :return:
        True if key is present in args with default value else False.
    """
    return True if key in get_default_args(func) else False


def in_all_args(func, key):
    """
    Checks if a setting name as key is present in function
    arguments.
    :param func:
        Function object.
    :param key:
        The setting name as a string.
    :return:
        True if key is present in args of a function else False.
    """
    return True if key in get_all_args(func) else False


def parse_dep_tree_optional(bear):
    """
    Parse the dependency tree of the bears looking for optional settings.
    :param bear:
        The bear object for which to get optional settings and parse the
        dependency tree further.
    :return:
        Dict of optional settings of the current bear and recursively
        all the optional settings of its dependencies.
    """
    deps = bear.BEAR_DEPS
    optional_settings = get_default_args(bear.run)
    for dep in deps:
        optional_settings.update(parse_dep_tree_optional(dep))
    return optional_settings


class SettingTypes:

    """
    Categorizes the settings into Type bool and Type others
    """

    def __init__(self, settings, functions, bear, trigger):
        """
        :param settings:
            Either a dict of non-optional settings of the form:
            {'setting_name': ('Description.', <class 'type'>),}
            or
            a dict of optional settings of the form:
            {'setting_name': default_values,}
        :param functions:
            A list of function objects i.e. either containing the run() method
            or the create_arguments() + generate_config() methods of the linter
            bears.
        :param bear:
            The current bear object.
        :param trigger:
            String of value either 'optional' or 'non-optional'
            depending on type of settings
        """
        self.settings_bool = []
        self.settings_others = []
        self.fillup_settings(functions, settings, bear, trigger)

    def fillup_settings(self, functions, settings, bear, trigger):
        """
        Fill settings_bool and settings_others depending upon whether the
        particular setting by the bear takes a bool value or any other.
        :param functions:
            A list of function objects i.e. either containing the run() method
            or the create_arguments() + generate_config() methods of the linter
            bears.
        :param settings:
            Either a dict of non-optional settings of the form:
            {'setting_name': ('Description.', <class 'type'>),}
            or
            a dict of optional settings of the form:
            {'setting_name': default_values,}
        :param bear:
            The current bear object.
        :param trigger:
            String of value either 'optional' or 'non-optional'
            depending on type of settings
        """
        for key in settings:
            if trigger == 'optional':
                self.fillup_optional_settings(key, functions, bear, settings)
            elif trigger == 'non-optional':
                self.fillup_non_optional_settings(key, functions, bear)
            else:
                raise ValueError('Invalid trigger Type')

    def fillup_optional_settings(self, key, funcs, bear, settings):
        """
        Function to populate the optional settings
        for the classes to store metadata.
        :param key:
            The setting value as a string.
        :param funcs:
            A list of function objects i.e. either containing the run() method
            or the create_arguments() + generate_config() methods of the linter
            bears.
        :param bear:
            The bear object.
        :param settings:
            Dict of optional bear settings of the form:
            {'setting_name': default_values,}
        """
        present_in_annot = False
        if len(funcs) == 1:
            present_in_annot = in_annot_recursive(bear, key)
        else:
            for func in funcs:
                inside_annot = in_annot(func, key)
                if inside_annot is not False:
                    present_in_annot = inside_annot
                    break

        if present_in_annot:
            self.diff_bool_others(key, present_in_annot)
        else:
            self.diff_bool_others_default(
                key, settings[key])

    def fillup_non_optional_settings(self, key, funcs, bear):
        """
        Function to populate the non-optional settings
        for the classes to store metadata.
        :param key:
            The setting value as a string.
        :param funcs:
            A list of function objects i.e. either containing the run() method
            or the create_arguments() + generate_config() methods of the linter
            bears.
        :param bear:
            The bear object.
        """
        present_in_annot = False
        present_in_default_args = False
        present_in_all_args = False
        function = None

        for func in funcs:
            present_in_annot = in_annot(func, key)
            if present_in_annot is not False:
                break

        for func in funcs:
            present_in_default_args = in_default_args(func, key)
            if present_in_default_args:
                break

        for func in funcs:
            present_in_all_args = in_all_args(func, key)
            if present_in_all_args:
                function = func
                break

        if present_in_annot:
            self.diff_bool_others(key, present_in_annot)
        elif present_in_all_args and not present_in_default_args:
            self.diff_bool_others(key, get_all_args(function)[key])
        else:
            self.parse_dep_tree_non_optional(bear, key)

    def parse_dep_tree_non_optional(self, bear, key):
        """
        Parses the bear's dependency tree looking for
        non-optional setting and their Type.
        :param bear:
            The bear object.
        :param key:
            The setting value as a string.
        """
        deps = bear.BEAR_DEPS
        for dep in deps:
            present_in_annot = in_annot(dep.run, key)
            if present_in_annot:
                self.diff_bool_others(key, present_in_annot)
            else:
                settings = get_all_args(dep.run)
                for pointer in get_default_args(dep.run):
                    del settings[pointer]
                if key in settings:
                    self.diff_bool_others(key, settings[key])
            self.parse_dep_tree_non_optional(dep, key)

    def diff_bool_others(self, key, check):
        """
        Checks if a settings is of Type bool or any other based
        on the value of check and feeds
        up the classes to store metadata in the list variables,
        SettingTypes.setting_bool and SettingTypes.setting_others.
        :param key:
            The Setting value as a string.
        :param check:
            The Type to which the key is to be checked against.
        """

        if check == bool:
            self.settings_bool.append(key)
        else:
            self.settings_others.append(key)

    def diff_bool_others_default(self, key, check):
        """
        Checks if a settings is of Type bool or any other based
        on the value of check and feeds
        up the metaclass.
        :param key:
            The Setting value as a string.
        :param check:
            The Type to which the key is to be checked against.
        """
        if isinstance(check, bool):
            self.settings_bool.append(key)
        else:
            self.settings_others.append(key)


class BearSettings:

    """
    Collect optional and non-optional settings for each bear
    """

    def __init__(self, bear):
        """
        :param bear:
            A bear class object.
        """
        self.bear = bear
        functions = None
        function = bear.create_arguments if (
            'create_arguments' in dir(bear)) else bear.run
        function_name = 'create_arguments' if (
            'create_arguments' in dir(bear)) else 'run'
        non_optional_settings = bear.get_non_optional_settings()

        # Get the actual function if the function is decorated.
        original_function = search_for_orig(function, function_name)
        if original_function is not None:
            function = original_function

        if function_name is 'run':
            # Recursively look for optional settings (which have a default
            # value) inside BEAR_DEPS
            optional_settings = get_default_args(function)
            optional_settings.update(parse_dep_tree_optional(self.bear))
            functions = [function]
        else:
            optional_settings_create_arguments = get_default_args(function)
            optional_settings_generate_config = {}
            # Appending the default arguments of bear method generate_config()
            # to those, with that of create_arguments().
            if hasattr(bear, 'generate_config'):
                gen_config_func = bear.generate_config
                # Again getting the actual method if it is decorated.
                gen_config = search_for_orig(gen_config_func,
                                             'generate_config')
                if gen_config is not None:
                    gen_config_func = gen_config
                optional_settings_generate_config = get_default_args(
                    gen_config_func)
                functions = [function, gen_config_func]
            optional_settings_create_arguments.update(
                optional_settings_generate_config)
            optional_settings = optional_settings_create_arguments
            functions = [function] if functions is None else functions

        self.create_setting_types_obj(optional_settings, non_optional_settings,
                                      functions, bear)

    def create_setting_types_obj(self, optional_settings,
                                 non_optional_settings, functions, bear):
        """
        :param optional_settings:
            A dict of optional settings for the bear.
        :param non_optional_settings:
            A dict of non-optional settings for the bear.
        :param functions:
            A list of function objects i.e. either containing the run() method
            or the create_arguments() + generate_config() methods of the linter
            bears.
        :param bear:
            The current bear object.
        """
        self.non_optional_settings = SettingTypes(
            non_optional_settings, functions, bear, trigger='non-optional')
        self.optional_settings = SettingTypes(
            optional_settings, functions, bear, trigger='optional')


def collect_bear_settings(bears):
    """
    :param bears:
        Dict of candidate bears for the project for each language.
    :return:
        A BearSettings object.
    """
    bear_settings_obj = []
    for language in bears:
        for bear in bears[language]:
            bear_settings_obj.append(BearSettings(bear))
    return bear_settings_obj
