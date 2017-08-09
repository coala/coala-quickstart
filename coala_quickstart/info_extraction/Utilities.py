def assert_type_signature(value, type_signature, argname):
    """
    Validates the value with the type_signature recursively. The type
    signature is either a single type object, or a collection of type
    objects or allowed values or type signatures.

    >>> assert_type_signature(3, int, "var")
    True
    >>> assert_type_signature(3, (3,), "var")
    True
    >>> assert_type_signature([3,4], ([int],), "var")
    True
    >>> assert_type_signature([3.0 ,4], ([int, float],), "var")
    True
    >>> assert_type_signature([3,4], ([1, 2, 3, 4],), "var")
    True
    >>> assert_type_signature(["foo", 420], [[str, int]], "var")
    True
    >>> assert_type_signature("tab", {"tab", "space"}, "var")
    True

    :param value:          Object to be validated against ``type_signature``.
    :param type_signature: Object that describes allowed types and values for
                           the ``value``.
    """
    iterables = (tuple, list, set)
    if isinstance(type_signature, type):
        type_signature = (type_signature,)
    else:
        if not isinstance(type_signature, iterables):
            raise TypeError('type_signature must be an Iterable or a type '
                            'object. Provided value: {}'.format(
                                type_signature))
    for typ in type_signature:
        if value == typ or (isinstance(typ, type) and isinstance(value, typ)):
            return True
        elif isinstance(value, iterables) and isinstance(value, type(typ)):
            for v in value:
                assert_type_signature(v, typ, argname)
            return True

    raise TypeError('{} must be an instance of one of {} (provided value: '
                    '{})'.format(argname, type_signature, repr(value)))
