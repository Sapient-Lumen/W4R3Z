"""SAM-like fake transport latency, churn, and retry pressure.

This is not a SAM implementation.  rev0013 needs deterministic pressure before
live I2P/SAM transport: high-latency anonymous paths, useful refusals, timeouts,
lying fast windows, and retry scheduling can change lookup safety more than the
record algebra itself.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .ids import DOMAIN, sha256, xor_distance

LATENCY_FORGE_DOMAIN = DOMAIN + b":latency-forge-v1:"


class FakeEndpointState(str, Enum):
    OK = "ok"
    SLOW = "slow"
    REFUSING = "refusing"
    TIMEOUT = "timeout"
    LYING = "lying"


class LatencyEventKind(str, Enum):
    SEND = "send"
    RESPONSE_OK = "response_ok"
    RESPONSE_REFUSAL = "response_refusal"
    RESPONSE_LIE = "response_lie"
    TIMEOUT = "timeout"
    RETRY = "retry"


class LatencyDecisionKind(str, Enum):
    ACCEPT_DIVERSE_RESPONSES = "accept_diverse_responses"
    CONTINUE_RETRY_BUDGET_REMAINING = "continue_retry_budget_remaining"
    CONTINUE_FAST_WINDOW_CAPTURED = "continue_fast_window_captured"
    FAIL_RETRY_EXHAUSTED = "fail_retry_exhausted"
    FAIL_NO_ENDPOINTS = "fail_no_endpoints"


@dataclass(frozen=True)
class FakeEndpoint:
    node_id: bytes
    family_id: str
    delay_ms: int
    state: FakeEndpointState = FakeEndpointState.OK
    last_seen_at: int = 0
    reliability_score: int = 0

    @property
    def selectable(self) -> bool:
        return self.state is not FakeEndpointState.TIMEOUT or self.reliability_score >= 0

    @property
    def successful_response(self) -> bool:
        return self.state in {FakeEndpointState.OK, FakeEndpointState.SLOW, FakeEndpointState.REFUSING}


@dataclass(frozen=True)
class LatencyProbePolicy:
    alpha: int = 4
    min_response_families: int = 3
    max_per_family_per_round: int = 1
    timeout_ms: int = 600
    retry_budget: int = 2
    fast_window_ms: int = 150
    max_fast_single_family_fraction: float = 0.67
    count_refusals_as_reachable: bool = True

    def validate(self) -> None:
        if self.alpha <= 0 or self.min_response_families <= 0 or self.max_per_family_per_round <= 0:
            raise ValueError("latency thresholds must be positive")
        if self.timeout_ms <= 0 or self.retry_budget < 0 or self.fast_window_ms < 0:
            raise ValueError("latency timing values are invalid")
        if not (0 < self.max_fast_single_family_fraction <= 1):
            raise ValueError("fast-family fraction must be in (0, 1]")


@dataclass(frozen=True)
class LatencyEvent:
    kind: LatencyEventKind
    node_id: bytes
    family_id: str
    at_ms: int
    round_index: int
    state: FakeEndpointState

    @property
    def digest(self) -> bytes:
        return sha256(LATENCY_FORGE_DOMAIN + b":event:" + b"|".join((
            self.kind.value.encode(),
            self.node_id,
            self.family_id.encode(),
            str(self.at_ms).encode(),
            str(self.round_index).encode(),
            self.state.value.encode(),
        )))


@dataclass(frozen=True)
class LatencyDecision:
    kind: LatencyDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class LatencyForgeReport:
    decision: LatencyDecision
    events: tuple[LatencyEvent, ...]
    contacted_families: frozenset[str]
    responding_families: frozenset[str]
    fast_window_families: frozenset[str]
    rounds_used: int
    retry_events: int

    @property
    def transcript_digest(self) -> bytes:
        return sha256(LATENCY_FORGE_DOMAIN + b":transcript:" + b"".join(event.digest for event in self.events))


def _sort_endpoint(endpoint: FakeEndpoint, *, target: bytes, family_counts: dict[str, int], now_ms: int) -> tuple[int, int, int, int, bytes]:
    state_penalty = {
        FakeEndpointState.OK: 0,
        FakeEndpointState.REFUSING: 1,
        FakeEndpointState.SLOW: 2,
        FakeEndpointState.LYING: 3,
        FakeEndpointState.TIMEOUT: 4,
    }[endpoint.state]
    age = max(0, now_ms - endpoint.last_seen_at)
    return (
        family_counts.get(endpoint.family_id, 0),
        state_penalty,
        endpoint.delay_ms - endpoint.reliability_score,
        xor_distance(endpoint.node_id, target) // (2**248),
        endpoint.node_id,
    )


def select_latency_frontier(
    candidates: Iterable[FakeEndpoint],
    *,
    target: bytes,
    count: int,
    max_per_family: int,
    already_contacted: frozenset[bytes] = frozenset(),
    now_ms: int = 0,
) -> tuple[FakeEndpoint, ...]:
    remaining = [candidate for candidate in candidates if candidate.node_id not in already_contacted and candidate.selectable]
    selected: list[FakeEndpoint] = []
    family_counts: dict[str, int] = {}
    while remaining and len(selected) < count:
        remaining.sort(key=lambda item: _sort_endpoint(item, target=target, family_counts=family_counts, now_ms=now_ms))
        picked_index = None
        for idx, candidate in enumerate(remaining):
            if family_counts.get(candidate.family_id, 0) < max_per_family:
                picked_index = idx
                break
        if picked_index is None:
            break
        picked = remaining.pop(picked_index)
        selected.append(picked)
        family_counts[picked.family_id] = family_counts.get(picked.family_id, 0) + 1
    return tuple(selected)


def _response_kind(endpoint: FakeEndpoint) -> LatencyEventKind:
    if endpoint.state is FakeEndpointState.REFUSING:
        return LatencyEventKind.RESPONSE_REFUSAL
    if endpoint.state is FakeEndpointState.LYING:
        return LatencyEventKind.RESPONSE_LIE
    if endpoint.state is FakeEndpointState.TIMEOUT:
        return LatencyEventKind.TIMEOUT
    return LatencyEventKind.RESPONSE_OK


def run_latency_forge(
    endpoints: Iterable[FakeEndpoint],
    *,
    target: bytes,
    request_id: bytes,
    policy: LatencyProbePolicy | None = None,
    now_ms: int = 0,
) -> LatencyForgeReport:
    if policy is None:
        policy = LatencyProbePolicy()
    policy.validate()
    all_endpoints = tuple(endpoints)
    if not all_endpoints:
        return LatencyForgeReport(LatencyDecision(LatencyDecisionKind.FAIL_NO_ENDPOINTS, False, "no fake endpoints supplied"), (), frozenset(), frozenset(), frozenset(), 0, 0)

    events: list[LatencyEvent] = []
    contacted: set[bytes] = set()
    contacted_families: set[str] = set()
    responding_families: set[str] = set()
    response_events: list[LatencyEvent] = []
    retry_events = 0
    current_ms = now_ms

    for round_index in range(policy.retry_budget + 1):
        frontier = select_latency_frontier(
            all_endpoints,
            target=target,
            count=policy.alpha,
            max_per_family=policy.max_per_family_per_round,
            already_contacted=frozenset(contacted),
            now_ms=current_ms,
        )
        if not frontier:
            break
        if round_index > 0:
            retry_events += 1
            events.append(LatencyEvent(LatencyEventKind.RETRY, request_id, "client", current_ms, round_index, FakeEndpointState.OK))
        for endpoint in frontier:
            contacted.add(endpoint.node_id)
            contacted_families.add(endpoint.family_id)
            events.append(LatencyEvent(LatencyEventKind.SEND, endpoint.node_id, endpoint.family_id, current_ms, round_index, endpoint.state))
            kind = _response_kind(endpoint)
            arrival = current_ms + min(endpoint.delay_ms, policy.timeout_ms)
            if kind is LatencyEventKind.TIMEOUT or endpoint.delay_ms > policy.timeout_ms:
                event = LatencyEvent(LatencyEventKind.TIMEOUT, endpoint.node_id, endpoint.family_id, current_ms + policy.timeout_ms, round_index, endpoint.state)
            else:
                event = LatencyEvent(kind, endpoint.node_id, endpoint.family_id, arrival, round_index, endpoint.state)
            events.append(event)
            if event.kind in {LatencyEventKind.RESPONSE_OK, LatencyEventKind.RESPONSE_REFUSAL}:
                if event.kind is LatencyEventKind.RESPONSE_OK or policy.count_refusals_as_reachable:
                    responding_families.add(endpoint.family_id)
                    response_events.append(event)
            elif event.kind is LatencyEventKind.RESPONSE_LIE:
                response_events.append(event)
        if len(responding_families) >= policy.min_response_families:
            break
        current_ms += policy.timeout_ms

    fast = tuple(event for event in response_events if event.at_ms <= now_ms + policy.fast_window_ms)
    fast_families = frozenset(event.family_id for event in fast)
    if fast:
        counts: dict[str, int] = {}
        for event in fast:
            counts[event.family_id] = counts.get(event.family_id, 0) + 1
        if max(counts.values()) / len(fast) > policy.max_fast_single_family_fraction and len(responding_families) < policy.min_response_families:
            decision = LatencyDecision(LatencyDecisionKind.CONTINUE_FAST_WINDOW_CAPTURED, False, "fast response window is family-captured")
        elif len(responding_families) >= policy.min_response_families:
            decision = LatencyDecision(LatencyDecisionKind.ACCEPT_DIVERSE_RESPONSES, True, "enough responding path families")
        else:
            decision = LatencyDecision(LatencyDecisionKind.FAIL_RETRY_EXHAUSTED, False, "retry budget exhausted before enough families responded")
    elif len(responding_families) >= policy.min_response_families:
        decision = LatencyDecision(LatencyDecisionKind.ACCEPT_DIVERSE_RESPONSES, True, "enough responding path families")
    elif retry_events <= policy.retry_budget and len(contacted) < len(all_endpoints):
        decision = LatencyDecision(LatencyDecisionKind.CONTINUE_RETRY_BUDGET_REMAINING, False, "more endpoints remain for another scheduling policy")
    else:
        decision = LatencyDecision(LatencyDecisionKind.FAIL_RETRY_EXHAUSTED, False, "retry budget exhausted before enough families responded")

    return LatencyForgeReport(
        decision,
        tuple(sorted(events, key=lambda event: (event.at_ms, event.round_index, event.kind.value, event.family_id, event.node_id))),
        frozenset(contacted_families),
        frozenset(responding_families),
        fast_families,
        retry_events + 1 if events else 0,
        retry_events,
    )
