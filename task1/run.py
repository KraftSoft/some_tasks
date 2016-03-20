class DuplicateKeyError(Exception):
    pass


def zip2(seq1, seq2):
    if not isinstance(seq1, list):
        raise TypeError('first argument must be a list instance')

    if not isinstance(seq2, list):
        raise TypeError('second argument must be a list instance')

    i = 0
    result = {}
    for key in seq1:

        if key in result:
            raise DuplicateKeyError('duplicate key "{0}" '.format(key))

        try:
            hash(key)
        except TypeError as e:
            raise TypeError('The {0} element has {1}'.format(i, e))

        if len(seq2) > i:
            result[key] = seq2[i]
        else:
            result[key] = None

        i += 1

    return result


if __name__ == '__main__':
    print(zip2(['a', 'b', 'c', 'd', 'e'], [1, 2, 3, 4, 5]))
    print(zip2(['a', 'b', 'c', 'd', 'e'], [1, 2, 3, 4]))
    print(zip2(['a', 'b', 'c', 'd'], [1, 2, 3, 4, 5]))
    print(zip2(['a', 'b', 'c', 'd', 'e'], [{1: 'a'}, {2: 'b'}, {3: 'c'}, {4: 'd'}, {5: 'e'}]))

    try:
        print(zip2([{'a': 1}, 'b', 'c', 'd', 'e'], [1, 2, 3, 4, 5]))
    except TypeError as e:
        print(e)

    try:
        print(zip2(['a', 'a', 'c', 'd', 'e'], [1, 2, 3, 4, 5]))
    except DuplicateKeyError as e:
        print(e)
