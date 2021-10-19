from evo_util import bounce_back, wrap_around, sort_to_chunks
import pytest
from individual import Individual

def test_bounce_back():
    assert bounce_back(3, [1,2]) == 1
    assert bounce_back(3.1, [0.1, 3.0]) == 2.9
    assert bounce_back(0.0, [0.1, 3.0]) == 0.2

    with pytest.raises(ValueError):
        bounce_back(4, [2.5, 3])

    with pytest.raises(ValueError):
        bounce_back(0, [1, 1.5])

def test_wrap_around():
    assert wrap_around(2, [1,1.5]) == 1
    assert wrap_around(1, [1.5, 3]) == 3

def test_sort_to_chunk():
    inds = [Individual() for _ in range(6)]
    inds[0].needs_evaluation = True
    inds[2].needs_evaluation = True
    inds[4].needs_evaluation = True

    inds[1].needs_evaluation = False
    inds[3].needs_evaluation = False
    inds[5].needs_evaluation = False

    sorted = sort_to_chunks(inds, 2)

    assert sorted == [
        inds[0],
        inds[4],
        inds[3],
        inds[2],
        inds[5],
        inds[1],
    ]

    sorted = sort_to_chunks(inds, 3)

    assert sorted == [
        inds[0],
        inds[5],
        inds[2],
        inds[3],
        inds[4],
        inds[1],
    ]

    sorted = sort_to_chunks(inds, 6)

    assert sorted == [
        inds[0],
        inds[2],
        inds[4],
        inds[5],
        inds[3],
        inds[1],
    ]
