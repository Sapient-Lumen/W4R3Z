"""Bounded token observations relevant to reachability, not exploit proof."""
from pynicotine.slskmessages import increment_token, initial_token
from pynicotine.utils import UINT32_LIMIT


def test_initial_search_token_uses_reduced_random_range():
    samples = [initial_token() for _ in range(32)]
    assert all(0 <= token <= UINT32_LIMIT // 1000 for token in samples)


def test_one_observed_token_predicts_the_next_without_intervening_allocations():
    observed = 750030
    assert increment_token(observed) == 750031
