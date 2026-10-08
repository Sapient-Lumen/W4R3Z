"""Redacted diagnostics/metrics guard for DHT experiments.

Observability is a metadata side channel.  rev0034 treats metrics emission as a
protocol boundary: labels must be scoped, bounded, redacted, and budgeted before
operator feedback can be recorded.

This is a local guard, not a production telemetry system.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Mapping

from .bencode import bencode
from .ids import DOMAIN, sha256

METRICS_VEIL_DOMAIN = DOMAIN + b":metrics-veil-v1:"
HEX64_RE = re.compile(r"\b[0-9a-fA-F]{64}\b")
HEX40_RE = re.compile(r"\b[0-9a-fA-F]{40}\b")
B32_I2P_RE = re.compile(r"[a-z2-7]{20,}\.b32\.i2p", re.IGNORECASE)


class MetricDecisionKind(str, Enum):
    ACCEPT_REDACTED_METRIC = "accept_redacted_metric"
    ACCEPT_AGGREGATE_METRIC = "accept_aggregate_metric"
    HOLD_CARDINALITY_BUDGET = "hold_cardinality_budget"
    QUARANTINE_RAW_KEY_LABEL = "quarantine_raw_key_label"
    QUARANTINE_RAW_DESTINATION_LABEL = "quarantine_raw_destination_label"
    QUARANTINE_SCOPE_MISMATCH = "quarantine_scope_mismatch"
    QUARANTINE_LABEL_TOO_LONG = "quarantine_label_too_long"
    QUARANTINE_UNKNOWN_LABEL = "quarantine_unknown_label"
    QUARANTINE_NAME = "quarantine_name"


@dataclass(frozen=True)
class MetricsPolicy:
    allowed_names: tuple[str, ...] = (
        "launch_quorum_decision",
        "provider_probe_result",
        "garden_refusal",
        "sam_probe_result",
        "storage_repair_debt",
    )
    allowed_label_keys: tuple[str, ...] = ("scope", "decision", "mode", "family", "bucket", "window", "kind")
    max_label_bytes: int = 48
    max_values_per_label: int = 8
    require_scope: bool = True

    def validate(self) -> None:
        if self.max_label_bytes <= 0 or self.max_values_per_label <= 0:
            raise ValueError("metrics policy budgets must be positive")


@dataclass(frozen=True)
class MetricEvent:
    name: str
    labels: tuple[tuple[str, str], ...]
    value: int
    scope_digest: bytes
    issued_at: int

    @classmethod
    def create(cls, *, name: str, labels: Mapping[str, str], value: int, scope_digest: bytes, issued_at: int) -> "MetricEvent":
        return cls(name, tuple(sorted((str(k), str(v)) for k, v in labels.items())), value, scope_digest, issued_at)

    def __post_init__(self) -> None:
        if not self.name or not re.match(r"^[a-z][a-z0-9_]{0,63}$", self.name):
            raise ValueError("metric event name must be a simple snake-case token")
        if len(self.scope_digest) != 32:
            raise ValueError("metric scope digest must be 32 bytes")
        if self.value < 0 or self.issued_at < 0:
            raise ValueError("metric value/time must be non-negative")

    @property
    def event_digest(self) -> bytes:
        return sha256(METRICS_VEIL_DOMAIN + b":event:" + bencode({
            b"name": self.name,
            b"labels": [[k, v] for k, v in self.labels],
            b"value": self.value,
            b"scope": self.scope_digest,
            b"issued_at": self.issued_at,
        }))


@dataclass(frozen=True)
class VeiledMetric:
    name: str
    label_digests: tuple[tuple[str, bytes], ...]
    value: int
    scope_digest: bytes
    event_digest: bytes
    metric_digest: bytes


@dataclass(frozen=True)
class MetricAssessment:
    decision_kind: MetricDecisionKind
    accept: bool
    reason: str
    event_digest: bytes
    leaked_fragments: tuple[str, ...]
    label_keys: tuple[str, ...]
    veiled_metric: VeiledMetric | None
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _looks_raw_key(value: str) -> bool:
    return bool(HEX64_RE.search(value) or HEX40_RE.search(value))


def _looks_raw_destination(value: str) -> bool:
    lowered = value.lower()
    return bool(B32_I2P_RE.search(lowered) or "destination=" in lowered or len(value) > 516)


def _label_digest(key: str, value: str) -> bytes:
    return sha256(METRICS_VEIL_DOMAIN + b":label:" + key.encode("utf-8") + b"\x00" + value.encode("utf-8"))


def _assess(kind: MetricDecisionKind, accept: bool, reason: str, event: MetricEvent, leaked: tuple[str, ...], veiled: VeiledMetric | None) -> MetricAssessment:
    label_keys = tuple(key for key, _ in event.labels)
    digest = sha256(METRICS_VEIL_DOMAIN + b":assessment:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"event": event.event_digest,
        b"leaked": list(leaked),
        b"keys": list(label_keys),
        b"veiled": b"" if veiled is None else veiled.metric_digest,
    }))
    return MetricAssessment(kind, accept, reason, event.event_digest, leaked, label_keys, veiled, digest)


def assess_metric_event(event: MetricEvent, *, policy: MetricsPolicy | None = None, prior_label_values: Mapping[str, set[str]] | None = None, expected_scope_digest: bytes | None = None) -> MetricAssessment:
    """Assess and redact a metric event before it can leave local memory."""
    policy = policy or MetricsPolicy()
    policy.validate()
    if event.name not in policy.allowed_names:
        return _assess(MetricDecisionKind.QUARANTINE_NAME, False, "metric name is not in local allowlist", event, (event.name,), None)
    if expected_scope_digest is not None and expected_scope_digest != event.scope_digest:
        return _assess(MetricDecisionKind.QUARANTINE_SCOPE_MISMATCH, False, "metric scope does not match caller scope", event, (event.scope_digest.hex(),), None)
    allowed_keys = set(policy.allowed_label_keys)
    for key, value in event.labels:
        if key not in allowed_keys:
            return _assess(MetricDecisionKind.QUARANTINE_UNKNOWN_LABEL, False, "metric label key is not locally allowed", event, (key,), None)
        if _looks_raw_destination(value):
            return _assess(MetricDecisionKind.QUARANTINE_RAW_DESTINATION_LABEL, False, "metric label looks like raw I2P destination material", event, (value[:48],), None)
        if _looks_raw_key(value):
            return _assess(MetricDecisionKind.QUARANTINE_RAW_KEY_LABEL, False, "metric label looks like raw content/key material", event, (value[:48],), None)
        if len(value.encode("utf-8")) > policy.max_label_bytes:
            return _assess(MetricDecisionKind.QUARANTINE_LABEL_TOO_LONG, False, "metric label exceeds redaction budget", event, (key,), None)
    prior = prior_label_values or {}
    for key, value in event.labels:
        values = set(prior.get(key, set()))
        if value not in values and len(values) >= policy.max_values_per_label:
            return _assess(MetricDecisionKind.HOLD_CARDINALITY_BUDGET, False, "metric label cardinality budget would grow", event, (key,), None)
    label_digests = tuple((key, _label_digest(key, value)) for key, value in event.labels)
    metric_digest = sha256(METRICS_VEIL_DOMAIN + b":veiled:" + bencode({
        b"name": event.name,
        b"labels": [[key, digest] for key, digest in label_digests],
        b"value": event.value,
        b"scope": event.scope_digest,
        b"event": event.event_digest,
    }))
    veiled = VeiledMetric(event.name, label_digests, event.value, event.scope_digest, event.event_digest, metric_digest)
    kind = MetricDecisionKind.ACCEPT_AGGREGATE_METRIC if not event.labels else MetricDecisionKind.ACCEPT_REDACTED_METRIC
    return _assess(kind, True, "metric accepted after local redaction and budget checks", event, (), veiled)
