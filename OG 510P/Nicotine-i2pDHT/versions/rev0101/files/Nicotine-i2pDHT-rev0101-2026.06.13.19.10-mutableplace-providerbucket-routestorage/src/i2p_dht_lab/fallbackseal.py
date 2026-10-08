"""rev0082 fallback seal: native leaves cannot silently outrank Python."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .abiguard import AbiGuardDecisionKind, AbiGuardReport
from .bencode import bencode
from .ids import DOMAIN, sha256
from .nativeparity import NativeParityDecisionKind, NativeParityReport

FALLBACK_SEAL_DOMAIN = DOMAIN + b":fallback-seal-v1:"


class FallbackSealDecisionKind(str, Enum):
    USE_NATIVE_LEAF_WITH_PYTHON_ORACLE = "use_native_leaf_with_python_oracle"
    USE_PYTHON_FALLBACK_NATIVE_MISSING = "use_python_fallback_native_missing"
    USE_PYTHON_FALLBACK_NATIVE_QUARANTINED = "use_python_fallback_native_quarantined"
    QUARANTINE_NATIVE_REQUIRED_PROFILE = "quarantine_native_required_profile"
    HOLD_WATCH_PARITY_OR_ABI = "hold_watch_parity_or_abi"


@dataclass(frozen=True)
class FallbackSealReport:
    decision_kind: FallbackSealDecisionKind
    accepted: bool
    native_selected: bool
    fallback_selected: bool
    quarantine_native: bool
    watch: bool
    obligations: tuple[str, ...]
    parity_digest: bytes
    abi_digest: bytes

    @property
    def report_digest(self) -> bytes:
        return sha256(FALLBACK_SEAL_DOMAIN + b":report:" + bencode({
            b"decision": FallbackSealDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"native_selected": 1 if self.native_selected else 0,
            b"fallback_selected": 1 if self.fallback_selected else 0,
            b"quarantine_native": 1 if self.quarantine_native else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"parity": self.parity_digest,
            b"abi": self.abi_digest,
        }))


def seal_native_or_fallback(parity: NativeParityReport, abi: AbiGuardReport, *, native_required: bool = False) -> FallbackSealReport:
    if native_required and (not parity.native_allowed or not abi.native_allowed):
        return FallbackSealReport(
            FallbackSealDecisionKind.QUARANTINE_NATIVE_REQUIRED_PROFILE,
            accepted=False,
            native_selected=False,
            fallback_selected=False,
            quarantine_native=True,
            watch=False,
            obligations=("disable-native-required-profile", "do-not-launch-without-native-and-parity"),
            parity_digest=parity.report_digest,
            abi_digest=abi.report_digest,
        )

    if parity.decision_kind is NativeParityDecisionKind.ACCEPT_NATIVE_PARITY and abi.decision_kind is AbiGuardDecisionKind.ACCEPT_NATIVE_ARTIFACT:
        return FallbackSealReport(
            FallbackSealDecisionKind.USE_NATIVE_LEAF_WITH_PYTHON_ORACLE,
            accepted=True,
            native_selected=True,
            fallback_selected=True,
            quarantine_native=False,
            watch=False,
            obligations=("keep-python-oracle", "runtime-can-fall-back", "record-native-selection"),
            parity_digest=parity.report_digest,
            abi_digest=abi.report_digest,
        )

    if parity.decision_kind is NativeParityDecisionKind.USE_PYTHON_FALLBACK_NATIVE_MISSING or abi.decision_kind is AbiGuardDecisionKind.USE_FALLBACK_ARTIFACT_MISSING:
        return FallbackSealReport(
            FallbackSealDecisionKind.USE_PYTHON_FALLBACK_NATIVE_MISSING,
            accepted=True,
            native_selected=False,
            fallback_selected=True,
            quarantine_native=False,
            watch=True,
            obligations=("record-fallback-reason", "do-not-penalize-portable-profile"),
            parity_digest=parity.report_digest,
            abi_digest=abi.report_digest,
        )

    if parity.decision_kind in {
        NativeParityDecisionKind.QUARANTINE_NATIVE_MISMATCH,
        NativeParityDecisionKind.QUARANTINE_NATIVE_EXCEPTION,
    } or abi.decision_kind.name.startswith("QUARANTINE"):
        return FallbackSealReport(
            FallbackSealDecisionKind.USE_PYTHON_FALLBACK_NATIVE_QUARANTINED,
            accepted=True,
            native_selected=False,
            fallback_selected=True,
            quarantine_native=True,
            watch=False,
            obligations=("preserve-quarantine-evidence", "route-all-calls-to-python-reference"),
            parity_digest=parity.report_digest,
            abi_digest=abi.report_digest,
        )

    return FallbackSealReport(
        FallbackSealDecisionKind.HOLD_WATCH_PARITY_OR_ABI,
        accepted=False,
        native_selected=False,
        fallback_selected=True,
        quarantine_native=False,
        watch=True,
        obligations=("increase-parity-coverage", "resolve-abi-watch-before-native-selection"),
        parity_digest=parity.report_digest,
        abi_digest=abi.report_digest,
    )
