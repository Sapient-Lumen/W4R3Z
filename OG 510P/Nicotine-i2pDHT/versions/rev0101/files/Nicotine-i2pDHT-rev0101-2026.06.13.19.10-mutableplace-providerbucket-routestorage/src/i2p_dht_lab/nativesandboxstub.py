"""rev0088 native sandbox-stub boundary.

This is deliberately not a production sandbox.  It is a typed no-network stub
that prevents native execution from spreading into parsing, crypto, I/O, or
transport surfaces while we are still proving the Python semantics.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256
from .nativeload import NativeLoadReport
from .nativeunload import NativeUnloadReport

NATIVE_SANDBOX_DOMAIN = DOMAIN + b":native-sandbox-stub-v1:"
ALLOWED_ISOLATION_KINDS = {"ctypes_leaf_stub", "process_stub", "fallback_only_stub"}


class NativeSandboxDecisionKind(str, Enum):
    ACCEPT_NO_NETWORK_STUB = "accept_no_network_stub"
    ACCEPT_FALLBACK_ONLY = "accept_fallback_only"
    HOLD_SANDBOX_NOT_PRODUCTION = "hold_sandbox_not_production"
    QUARANTINE_UNTRUSTED_BYTES_OR_CRYPTO = "quarantine_untrusted_bytes_or_crypto"
    QUARANTINE_IO_OR_PROCESS_POWER = "quarantine_io_or_process_power"
    QUARANTINE_NATIVE_REQUEST_AFTER_UNLOAD = "quarantine_native_request_after_unload"
    QUARANTINE_NO_FALLBACK = "quarantine_no_fallback"
    QUARANTINE_BOUNDS = "quarantine_bounds"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class NativeSandboxPlan:
    component: str
    profile: str
    operation: str
    request_id: str
    sequence: int
    previous_digest: bytes
    load_digest: bytes
    unload_digest: bytes
    isolation_kind: str
    native_execution_requested: bool
    nonproduction_stub_ack: bool
    python_fallback_available: bool
    touches_untrusted_bytes: bool
    touches_crypto_or_secret_keys: bool
    allow_filesystem: bool
    allow_network: bool
    allow_process_spawn: bool
    allow_threads: bool
    allow_dynamic_load: bool
    max_input_bytes: int
    max_runtime_us: int
    family_id: str
    path_family_id: str
    note: str = ""

    @property
    def plan_digest(self) -> bytes:
        return sha256(NATIVE_SANDBOX_DOMAIN + b":plan:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"operation": self.operation,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"load": self.load_digest,
            b"unload": self.unload_digest,
            b"isolation": self.isolation_kind,
            b"native_requested": 1 if self.native_execution_requested else 0,
            b"stub_ack": 1 if self.nonproduction_stub_ack else 0,
            b"fallback": 1 if self.python_fallback_available else 0,
            b"untrusted_bytes": 1 if self.touches_untrusted_bytes else 0,
            b"crypto": 1 if self.touches_crypto_or_secret_keys else 0,
            b"fs": 1 if self.allow_filesystem else 0,
            b"net": 1 if self.allow_network else 0,
            b"proc": 1 if self.allow_process_spawn else 0,
            b"threads": 1 if self.allow_threads else 0,
            b"dynamic_load": 1 if self.allow_dynamic_load else 0,
            b"max_input": self.max_input_bytes,
            b"max_runtime_us": self.max_runtime_us,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"note": self.note,
        }))


@dataclass(frozen=True)
class NativeSandboxReport:
    decision_kind: NativeSandboxDecisionKind
    accepted: bool
    native_execution_allowed: bool
    fallback_only: bool
    watch: bool
    quarantine: bool
    obligations: tuple[str, ...]
    plan_digest: bytes
    load_digest: bytes
    unload_digest: bytes
    family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(NATIVE_SANDBOX_DOMAIN + b":report:" + bencode({
            b"decision": NativeSandboxDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"native_allowed": 1 if self.native_execution_allowed else 0,
            b"fallback_only": 1 if self.fallback_only else 0,
            b"watch": 1 if self.watch else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"obligations": list(self.obligations),
            b"plan": self.plan_digest,
            b"load": self.load_digest,
            b"unload": self.unload_digest,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def assess_native_sandbox_stub(
    load: NativeLoadReport,
    unload: NativeUnloadReport,
    plan: NativeSandboxPlan,
    *,
    previous: NativeSandboxPlan | None = None,
    prior_plan_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
    max_input_bytes: int = 4096,
    max_runtime_us: int = 250_000,
) -> NativeSandboxReport:
    families = set(observed_families or (plan.family_id,))
    path_families = set(observed_path_families or (plan.path_family_id,))

    def report(kind: NativeSandboxDecisionKind, accepted: bool, native: bool, fallback_only: bool, watch: bool, quarantine: bool, obligations: tuple[str, ...]) -> NativeSandboxReport:
        return NativeSandboxReport(kind, accepted, native, fallback_only, watch, quarantine, obligations, plan.plan_digest, load.report_digest, unload.report_digest, len(families), len(path_families))

    if plan.plan_digest in prior_plan_digests:
        return report(NativeSandboxDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, False, True, ("native-sandbox-plan-replay",))
    if previous is not None:
        if plan.sequence < previous.sequence:
            return report(NativeSandboxDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, False, True, ("native-sandbox-rollback",))
        if plan.sequence == previous.sequence and plan.plan_digest != previous.plan_digest:
            return report(NativeSandboxDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, False, True, False, True, ("native-sandbox-same-sequence-fork",))
        if plan.sequence > previous.sequence and plan.previous_digest != previous.plan_digest:
            return report(NativeSandboxDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, True, False, True, ("native-sandbox-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(NativeSandboxDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, True, False, True, ("native-sandbox-low-diversity",))
    if plan.load_digest != load.report_digest or plan.unload_digest != unload.report_digest:
        return report(NativeSandboxDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, False, True, ("native-sandbox-component-digest-drift",))
    if plan.touches_untrusted_bytes or plan.touches_crypto_or_secret_keys:
        return report(NativeSandboxDecisionKind.QUARANTINE_UNTRUSTED_BYTES_OR_CRYPTO, False, False, True, False, True, ("native-stub-cannot-own-parser-crypto-or-secret-keys",))
    if plan.allow_filesystem or plan.allow_network or plan.allow_process_spawn or plan.allow_threads or plan.allow_dynamic_load:
        return report(NativeSandboxDecisionKind.QUARANTINE_IO_OR_PROCESS_POWER, False, False, True, False, True, ("native-stub-must-not-carry-io-network-process-thread-or-dlopen-power",))
    if not plan.python_fallback_available:
        return report(NativeSandboxDecisionKind.QUARANTINE_NO_FALLBACK, False, False, True, False, True, ("native-sandbox-requires-python-fallback",))
    if plan.max_input_bytes <= 0 or plan.max_input_bytes > max_input_bytes or plan.max_runtime_us <= 0 or plan.max_runtime_us > max_runtime_us:
        return report(NativeSandboxDecisionKind.QUARANTINE_BOUNDS, False, False, True, False, True, ("native-sandbox-bounds-exceeded",))
    if plan.native_execution_requested and (unload.unloaded or unload.quarantine or not load.native_load_allowed):
        return report(NativeSandboxDecisionKind.QUARANTINE_NATIVE_REQUEST_AFTER_UNLOAD, False, False, True, False, True, ("native-requested-after-unload-or-quarantine",))
    if not plan.native_execution_requested:
        return report(NativeSandboxDecisionKind.ACCEPT_FALLBACK_ONLY, True, False, True, False, False, ("fallback-only-stub", "no-native-execution"))
    if plan.isolation_kind not in ALLOWED_ISOLATION_KINDS or not plan.nonproduction_stub_ack:
        return report(NativeSandboxDecisionKind.HOLD_SANDBOX_NOT_PRODUCTION, True, False, True, True, False, ("sandbox-is-nonproduction-stub", "require-explicit-ack-before-native-experiment"))
    return report(NativeSandboxDecisionKind.ACCEPT_NO_NETWORK_STUB, True, True, False, False, False, ("no-network-native-leaf-stub", "python-fallback-retained", "not-production-sandbox"))
