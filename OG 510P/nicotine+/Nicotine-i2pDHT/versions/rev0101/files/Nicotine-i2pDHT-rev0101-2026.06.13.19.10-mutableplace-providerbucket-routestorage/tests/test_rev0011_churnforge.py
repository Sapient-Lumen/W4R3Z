from __future__ import annotations

from dataclasses import replace

from i2p_dht_lab.churnforge import (
    ChurnContact,
    ChurnDecisionKind,
    ChurnFrontier,
    ChurnState,
    assess_churn_frontier,
    make_churn_transcript,
    select_churn_frontier,
)
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.routing import Contact


def contact(label: str, *, rtt_ms: int) -> Contact:
    return Contact(node_id=sha256(b"rev0011-churn-contact:" + label.encode()), destination=f"{label}.b32.i2p", rtt_ms=rtt_ms)


def churn(label: str, family: str, *, delay_ms: int, state: ChurnState = ChurnState.UP, last_seen_at: int = 0) -> ChurnContact:
    return ChurnContact(contact(label, rtt_ms=delay_ms), family, state=state, delay_ms=delay_ms, last_seen_at=last_seen_at)


def test_churn_frontier_rotates_families_before_latency_greed() -> None:
    target = sha256(b"rev0011-churn-target")
    candidates = (
        churn("evil-a", "evil", delay_ms=5, last_seen_at=1000),
        churn("evil-b", "evil", delay_ms=6, last_seen_at=1000),
        churn("evil-c", "evil", delay_ms=7, last_seen_at=1000),
        churn("garden-east", "garden-east", delay_ms=180, last_seen_at=990),
        churn("direct-west", "direct-west", delay_ms=220, last_seen_at=980),
    )

    frontier = select_churn_frontier(candidates, target=target, count=3, max_per_family=1, now=1000)

    assert frontier.families == frozenset({"evil", "garden-east", "direct-west"})
    assert sum(1 for item in frontier.contacts if item.family_id == "evil") == 1


def test_churn_frontier_detects_captured_fast_window_even_when_overall_frontier_is_diverse() -> None:
    target = sha256(b"rev0011-fast-window")
    frontier = select_churn_frontier(
        (
            churn("evil-a", "evil", delay_ms=5),
            churn("evil-b", "evil", delay_ms=6),
            churn("honest-a", "honest-a", delay_ms=160),
            churn("honest-b", "honest-b", delay_ms=170),
        ),
        target=target,
        count=4,
        max_per_family=2,
    )

    decision = assess_churn_frontier(frontier, min_families=3, fast_window_ms=75, max_fast_single_family_fraction=0.67)

    assert frontier.families == frozenset({"evil", "honest-a", "honest-b"})
    assert decision.kind is ChurnDecisionKind.CONTINUE_FAST_WINDOW_CAPTURED
    assert not decision.accept


def test_churn_frontier_rejects_too_many_bad_contacts_before_accepting_diversity() -> None:
    target = sha256(b"rev0011-bad-frontier")
    frontier = ChurnFrontier(
        target,
        (
            churn("a", "a", delay_ms=30, state=ChurnState.UP),
            churn("b", "b", delay_ms=40, state=ChurnState.DOWN),
            churn("c", "c", delay_ms=50, state=ChurnState.LYING),
            churn("d", "d", delay_ms=60, state=ChurnState.UP),
        ),
    )

    decision = assess_churn_frontier(frontier, min_families=3, max_bad_fraction=0.25)

    assert decision.kind is ChurnDecisionKind.CONTINUE_TOO_MANY_BAD


def test_churn_transcript_digest_is_order_stable_but_state_sensitive() -> None:
    request_id = sha256(b"rev0011-transcript-request")
    target = sha256(b"rev0011-transcript-target")
    a = churn("alpha", "alpha", delay_ms=40)
    b = churn("beta", "beta", delay_ms=80)
    frontier_ab = ChurnFrontier(target, (a, b))
    frontier_ba = ChurnFrontier(target, (b, a))
    frontier_changed = ChurnFrontier(target, (a, replace(b, state=ChurnState.SLOW)))

    assert make_churn_transcript(frontier_ab, request_id=request_id).digest == make_churn_transcript(frontier_ba, request_id=request_id).digest
    assert make_churn_transcript(frontier_ab, request_id=request_id).digest != make_churn_transcript(frontier_changed, request_id=request_id).digest
