from search_repeat_model import Response, SearchRepeatSystem


def test_first_response_after_search_again_at_cap_retires_token_and_adds_nothing():
    system = SearchRepeatSystem(token=70, cap=2)
    system.seed_results(["alice", "bob"])
    system.allowed_tokens.clear()  # The prior over-cap response already retired it.

    system.search_again_current(["carol"])
    outcome = system.receive(Response(70, "carol", "new"))

    assert outcome == "cap-retired"
    assert system.page.results == {"alice": "seed:alice", "bob": "seed:bob"}
    assert 70 not in system.allowed_tokens


def test_repeated_clicks_at_cap_fan_out_without_restoring_display_capacity():
    system = SearchRepeatSystem(token=70, cap=2)
    system.seed_results(["alice", "bob"])
    recipients = tuple(f"buddy-{index}" for index in range(32))

    for click in range(12):
        system.search_again_current(recipients)
        assert system.receive(Response(70, f"return-{click}", "new")) == "cap-retired"

    assert len(system.requests) == 12 * 32
    assert system.page.count == 2
    assert all(value.startswith("seed:") for value in system.page.results.values())


def test_cap_is_checked_before_the_returning_username_gate():
    system = SearchRepeatSystem(token=70, cap=1)
    system.seed_results(["alice"])
    system.search_again_current(["alice"])

    assert system.receive(Response(70, "alice", "duplicate")) == "cap-retired"
    assert 70 not in system.allowed_tokens
