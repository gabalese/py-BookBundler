def matches(source, destination):
    """
    Basic mathing algorithm. Double iteration over src & dst, if the tuple of len matches for a line,
    find a match of string contents. One match is considered exhaustive, for now.

    :param source: list of input text
    :type source: list
    :param destination: list of reference text
    :type destination: list
    :rtype: bool
    """
    for i in source:
        for v in destination:
            if map(len, i.split(" ")) == map(len, v.split(" ")):
                if i == v:
                    return True
    else:
        return False
