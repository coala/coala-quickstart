

def search_object_recursively(search_object,
                              key,
                              value=None,
                              prepath=(),
                              idx=-1):
    """
    Searches for the given ``key`` and ``value`` in an object
    containing nested lists, tuples and dicts.

    :param search_object:
        object to be searched
    :param key:
        key to look for, can be a dictionary as well.
    :param value:
        optional, if provided match the value of `key` parameter
        with this `value` parameter and the result will consist of
        all the objects having this key-value pair
    :param prepath:
        path traversed recursively so far.
    :param idx:
        index of current element being traversed while traversing a
        list or tuple of elements.
    :return:
        A list of dicts of the form
        {
            "object": list or dict that match the search criteria,
            "path": tuple of path to the object from the root of the
                    `search_object`
        }
    """
    results = []
    supported_types = (list, tuple, dict)

    if isinstance(search_object, (list, tuple)):
        for i in search_object:
            idx += 1
            results += search_object_recursively(
                i, key, value=value, prepath=prepath, idx=idx)

    elif isinstance(search_object, dict):
        for k, v in search_object.items():
            path = prepath + (k,) if idx < 0 else prepath + (idx, k,)
            if k == key:
                if value is not None and v == value:
                    results.append({
                        'object': search_object,
                        'path': path,
                    })
                elif value is None:
                    results.append({
                        'object': v,
                        'path': path,
                    })
            elif isinstance(v, supported_types):
                results += search_object_recursively(v,
                                                     key,
                                                     value=value,
                                                     prepath=path,
                                                     idx=-1)
    else:
        raise TypeError(
            'The object to be searched should only contain these types: {}'
            .format(','.join([str(t) for t in supported_types])))

    return results
