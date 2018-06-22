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


class SettingTypes:

    """
    Categorizes the settings into Type bool and Type others
    """

    def __init__(self, settings, function, bear, trigger):
        """
        :param settings:
            Either a dict of non-optional settings of the form:
            {'setting_name': ('Description.', <class 'type'>),}
            or
            a dict of optional settings of the form:
            {'setting_name': default_values,}
        :param function:
            The function object i.e. either the run() method or
            the create_arguments() method of the bear.
        :param bear:
            The current bear object.
        :param trigger:
            String of value either 'optional' or 'non-optional'
            depending on type of settings
        """
        self.settings_bool = []
        self.settings_others = []
        self.fillup_settings(function, settings, bear, trigger)

    def fillup_settings(self, function, settings, bear, trigger):
        """
        Fill settings_bool and settings_others depending upon whether the
        particular setting by the bear takes a bool value or any other.
        :param function:
            The function object i.e. either the run() method or
            the create_arguments() method of the bear.
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
                self.fillup_optional_settings(key, function)
            elif trigger == 'non-optional':
                self.fillup_non_optional_settings(key, function, bear)
            else:
                raise ValueError('Invalid trigger Type')

    def fillup_optional_settings(self, key, func):
        """
        Function to populate the optional settings
        for the classes to store metadata.
        :param key:
            The setting value as a string.
        :param func:
            The function object. Either create_arguments() for linter bears
            or run() for other bears.
        """
        present_in_annot = in_annot(func, key)

        if present_in_annot:
            self.diff_bool_others(key, present_in_annot)
        else:
            self.diff_bool_others_default(key, get_default_args(func)[key])

    def fillup_non_optional_settings(self, key, func, bear):
        """
        Function to populate the non-optional settings
        for the classes to store metadata.
        :param key:
            The setting value as a string.
        :param func:
            The function object. Either create_arguments() for linter bears
            or run() for other bears.
        :param bear:
            The bear object.
        """
        present_in_annot = in_annot(func, key)
        present_in_default_args = in_default_args(func, key)
        present_in_all_args = in_all_args(func, key)

        if present_in_annot:
            self.diff_bool_others(key, present_in_annot)
        elif present_in_all_args and not present_in_default_args:
            self.diff_bool_others(key, get_all_args(func)[key])
        else:
            self.parse_dep_tree(bear, key)

    def parse_dep_tree(self, bear, key):
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
            self.parse_dep_tree(dep, key)

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
        function = bear.create_arguments if (
            'create_arguments' in dir(bear)) else bear.run
        function_name = 'create_arguments' if (
            'create_arguments' in dir(bear)) else 'run'
        non_optional_settings = bear.get_non_optional_settings()

        # Get the actual function if the function is decorated.
        original_function = search_for_orig(function, function_name)
        if original_function is not None:
            function = original_function

        optional_settings = get_default_args(function)
        self.create_setting_types_obj(optional_settings, non_optional_settings,
                                      function, bear)

    def create_setting_types_obj(self, optional_settings,
                                 non_optional_settings, function, bear):
        """
        :param optional_settings:
            A dict of optional settings for the bear.
        :param non_optional_settings:
            A dict of non-optional settings for the bear.
        :param function:
            The function object i.e. either the run() method or
            the create_arguments() method of the bear.
        :param bear:
            The current bear object.
        """
        self.non_optional_settings = SettingTypes(
            non_optional_settings, function, bear, trigger='non-optional')
        self.optional_settings = SettingTypes(
            optional_settings, function, bear, trigger='optional')


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
