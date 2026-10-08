from wishlist_scheduler_model import SCENARIOS, WishlistScheduler, run_matrix, run_scenario


def test_current_single_disabled_dispatches_failed_eligibility_candidate():
    result = run_scenario([("disabled", False)], 1, require_enabled_dispatch=False)
    assert result["selected"] == ["disabled"]
    assert result["ignored"] == {"disabled": False}


def test_current_all_disabled_repeats_final_item_after_full_rotation():
    result = run_scenario(
        [("a", False), ("b", False), ("c", False)],
        4,
        require_enabled_dispatch=False,
    )
    assert result["selected"] == ["c", "c", "c", "c"]
    assert result["order"] == ["a", "b", "c"]


def test_candidate_single_disabled_does_not_dispatch():
    result = run_scenario([("disabled", False)], 1, require_enabled_dispatch=True)
    assert result["selected"] == [None]
    assert result["ignored"] == {"disabled": True}


def test_candidate_all_disabled_does_not_dispatch_or_reactivate():
    result = run_scenario(
        [("a", False), ("b", False), ("c", False)],
        4,
        require_enabled_dispatch=True,
    )
    assert result["selected"] == [None, None, None, None]
    assert all(result["ignored"].values())


def test_empty_scheduler_is_a_noop_in_both_states():
    assert run_scenario([], 1, require_enabled_dispatch=False)["selected"] == [None]
    assert run_scenario([], 1, require_enabled_dispatch=True)["selected"] == [None]


def test_first_enabled_item_is_selected_after_disabled_prefix():
    expected = ["on-b", "on-b"]
    items = [("off-a", False), ("on-b", True)]
    assert run_scenario(items, 2, require_enabled_dispatch=False)["selected"] == expected
    assert run_scenario(items, 2, require_enabled_dispatch=True)["selected"] == expected


def test_enabled_item_before_disabled_suffix_remains_selected():
    expected = ["on-a", "on-a"]
    items = [("on-a", True), ("off-b", False)]
    assert run_scenario(items, 2, require_enabled_dispatch=False)["selected"] == expected
    assert run_scenario(items, 2, require_enabled_dispatch=True)["selected"] == expected


def test_all_enabled_round_robin_is_unchanged():
    expected = ["a", "b", "c", "a", "b", "c"]
    items = [("a", True), ("b", True), ("c", True)]
    assert run_scenario(items, 6, require_enabled_dispatch=False)["selected"] == expected
    assert run_scenario(items, 6, require_enabled_dispatch=True)["selected"] == expected


def test_mixed_enabled_round_robin_is_unchanged():
    expected = ["on-b", "on-d", "on-b", "on-d"]
    items = [("off-a", False), ("on-b", True), ("off-c", False), ("on-d", True)]
    assert run_scenario(items, 4, require_enabled_dispatch=False)["selected"] == expected
    assert run_scenario(items, 4, require_enabled_dispatch=True)["selected"] == expected


def test_full_matrix_has_exact_scenario_set():
    assert set(run_matrix(candidate=False)) == set(SCENARIOS)
    assert set(run_matrix(candidate=True)) == set(SCENARIOS)


def test_tick_preserves_wishlist_membership():
    scheduler = WishlistScheduler(
        [("off-a", False), ("on-b", True), ("off-c", False)],
        require_enabled_dispatch=True,
    )
    before = set(scheduler.wishlist)
    for _ in range(20):
        scheduler.tick()
    assert set(scheduler.wishlist) == before


def test_candidate_changes_only_no_enabled_item_outcome():
    current = run_matrix(candidate=False)
    candidate = run_matrix(candidate=True)
    changed = {name for name in current if current[name] != candidate[name]}
    assert changed == {"single_disabled", "all_disabled"}
