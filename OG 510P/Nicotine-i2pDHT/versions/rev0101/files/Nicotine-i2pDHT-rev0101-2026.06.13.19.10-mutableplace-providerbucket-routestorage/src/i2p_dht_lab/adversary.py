"""Tiny adversarial-observation helpers for future chaos tests."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ResponseBehavior(str, Enum):
    HONEST = "honest"
    EMPTY = "empty"
    FALSE_PROVIDER = "false_provider"
    STALE_MUTABLE = "stale_mutable"
    DELAY = "delay"


@dataclass(frozen=True)
class BehaviorObservation:
    path_index: int
    behavior: ResponseBehavior
    responders: int = 1


@dataclass(frozen=True)
class AdversaryReadout:
    suspected: bool
    reason: str
    affected_paths: int
    honest_paths: int
    false_or_stale_paths: int
    empty_paths: int


def readout(observations: list[BehaviorObservation], *, min_honest_paths: int = 3) -> AdversaryReadout:
    paths = {obs.path_index for obs in observations}
    honest = {obs.path_index for obs in observations if obs.behavior is ResponseBehavior.HONEST}
    false_or_stale = {obs.path_index for obs in observations if obs.behavior in {ResponseBehavior.FALSE_PROVIDER, ResponseBehavior.STALE_MUTABLE}}
    empty = {obs.path_index for obs in observations if obs.behavior is ResponseBehavior.EMPTY}
    if len(false_or_stale) > 0:
        return AdversaryReadout(True, "semantic_poisoning_seen", len(paths), len(honest), len(false_or_stale), len(empty))
    if len(honest) < min_honest_paths and len(empty) >= 2:
        return AdversaryReadout(True, "empty_path_cluster", len(paths), len(honest), len(false_or_stale), len(empty))
    if len(honest) < min_honest_paths:
        return AdversaryReadout(False, "low_confidence_not_enough_honest_paths", len(paths), len(honest), len(false_or_stale), len(empty))
    return AdversaryReadout(False, "no_obvious_adversarial_pattern", len(paths), len(honest), len(false_or_stale), len(empty))
