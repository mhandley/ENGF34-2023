def test_is_in():
    assert not is_in_binary([], 4)
    assert is_in_binary([1], 1)
    assert is_in_binary([1,2,3], 3)
    assert is_in_binary([1,2,3], 2)
    assert is_in_binary([1,2,3], 1)
    assert is_in_binary([1,2,3,4], 4)
    assert is_in_binary([1,2,3,4], 3)
    assert is_in_binary([1,2,3,4], 2)
    assert is_in_binary([1,2,3,4], 1)
    assert is_in_binary([1,2,2,2,3], 2)
    assert is_in_binary([2,3,4,5,6,7],3)
    assert not is_in_binary([1,2,3,3,3,10], 4)

def is_in_binary(lst, val):
    if len(lst) == 0:
        return False

    start = 0
    end = len(lst)
    while end - start > 1:
        middle = (start + end) // 2
        if val >= lst[middle]:
            start = middle
        else:
            end = middle
    return lst[start] == val
