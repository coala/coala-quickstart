from coala_quickstart.info_extraction.Utilities import assert_type_signature


class Info:
    description = 'Some Description.'

    # type signature for the information value.
    value_type = (object,)

    # Some example values for reference that also match the value_type.
    example_values = []

    def __init__(self,
                 source,
                 value,
                 extractor=None,
                 **kwargs):
        """
        :param source:    Source from where the information is discovered.
        :param value:     Value of the infomation to be represented.
        :param extractor: ``InfoExtractor`` instance used to extract the
                          information.
        """
        if not self.value_type:
            self.value_type = (object,)

        assert_type_signature(value, self.value_type, 'value')
        self.source = source
        self._value = value
        self.extractor = extractor
        for key, val in kwargs.items():
            setattr(self, key, val)

    @property
    def value(self):
        return self._value

    @property
    def name(self):
        return self.__class__.__name__
