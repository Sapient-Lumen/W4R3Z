"""rev0082 ABI/load guard for optional GCC-native leaf kernels."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256

ABI_GUARD_DOMAIN = DOMAIN + b":abi-guard-v1:"


class AbiGuardDecisionKind(str, Enum):
    ACCEPT_NATIVE_ARTIFACT = "accept_native_artifact"
    USE_FALLBACK_ARTIFACT_MISSING = "use_fallback_artifact_missing"
    QUARANTINE_ABI_VERSION = "quarantine_abi_version"
    QUARANTINE_SYMBOL_SET = "quarantine_symbol_set"
    QUARANTINE_SOURCE_DIGEST = "quarantine_source_digest"
    QUARANTINE_COMPILER_FLAGS = "quarantine_compiler_flags"
    QUARANTINE_OBJECT_DIGEST = "quarantine_object_digest"
    QUARANTINE_INPUT_LIMIT = "quarantine_input_limit"
    QUARANTINE_NO_FALLBACK = "quarantine_no_fallback"


@dataclass(frozen=True)
class NativeArtifactManifest:
    component: str
    abi_version: int
    required_symbols: tuple[str, ...]
    source_digest: bytes
    compiler_flags_digest: bytes
    object_digest: bytes
    max_input_len: int
    fallback_available: bool
    notes: str = ""

    @property
    def manifest_digest(self) -> bytes:
        return sha256(ABI_GUARD_DOMAIN + b":manifest:" + bencode({
            b"component": self.component,
            b"abi": self.abi_version,
            b"symbols": list(self.required_symbols),
            b"source": self.source_digest,
            b"flags": self.compiler_flags_digest,
            b"object": self.object_digest,
            b"max": self.max_input_len,
            b"fallback": 1 if self.fallback_available else 0,
            b"notes": self.notes,
        }))


@dataclass(frozen=True)
class NativeRuntimeProbe:
    artifact_present: bool
    abi_version: int | None
    symbols_present: tuple[str, ...]
    source_digest: bytes | None
    compiler_flags_digest: bytes | None
    object_digest: bytes | None
    max_input_len: int | None

    @property
    def probe_digest(self) -> bytes:
        return sha256(ABI_GUARD_DOMAIN + b":probe:" + bencode({
            b"present": 1 if self.artifact_present else 0,
            b"abi": self.abi_version if self.abi_version is not None else -1,
            b"symbols": list(self.symbols_present),
            b"source": self.source_digest or b"",
            b"flags": self.compiler_flags_digest or b"",
            b"object": self.object_digest or b"",
            b"max": self.max_input_len if self.max_input_len is not None else -1,
        }))


@dataclass(frozen=True)
class AbiGuardReport:
    decision_kind: AbiGuardDecisionKind
    accepted: bool
    native_allowed: bool
    fallback_allowed: bool
    watch: bool
    obligations: tuple[str, ...]
    manifest_digest: bytes
    probe_digest: bytes

    @property
    def report_digest(self) -> bytes:
        return sha256(ABI_GUARD_DOMAIN + b":report:" + bencode({
            b"decision": AbiGuardDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"native_allowed": 1 if self.native_allowed else 0,
            b"fallback_allowed": 1 if self.fallback_allowed else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"manifest": self.manifest_digest,
            b"probe": self.probe_digest,
        }))


def assess_native_abi(manifest: NativeArtifactManifest, probe: NativeRuntimeProbe) -> AbiGuardReport:
    if not manifest.fallback_available:
        return AbiGuardReport(
            AbiGuardDecisionKind.QUARANTINE_NO_FALLBACK,
            accepted=False,
            native_allowed=False,
            fallback_allowed=False,
            watch=False,
            obligations=("never-require-native-without-fallback",),
            manifest_digest=manifest.manifest_digest,
            probe_digest=probe.probe_digest,
        )
    if not probe.artifact_present:
        return AbiGuardReport(
            AbiGuardDecisionKind.USE_FALLBACK_ARTIFACT_MISSING,
            accepted=True,
            native_allowed=False,
            fallback_allowed=True,
            watch=True,
            obligations=("record-native-missing", "use-python-reference"),
            manifest_digest=manifest.manifest_digest,
            probe_digest=probe.probe_digest,
        )
    if probe.abi_version != manifest.abi_version:
        return AbiGuardReport(AbiGuardDecisionKind.QUARANTINE_ABI_VERSION, False, False, True, False, ("reject-native", "use-python-fallback"), manifest.manifest_digest, probe.probe_digest)
    missing_symbols = tuple(sorted(set(manifest.required_symbols) - set(probe.symbols_present)))
    if missing_symbols:
        return AbiGuardReport(AbiGuardDecisionKind.QUARANTINE_SYMBOL_SET, False, False, True, False, tuple("missing-symbol:" + symbol for symbol in missing_symbols), manifest.manifest_digest, probe.probe_digest)
    if probe.source_digest != manifest.source_digest:
        return AbiGuardReport(AbiGuardDecisionKind.QUARANTINE_SOURCE_DIGEST, False, False, True, False, ("source-digest-mismatch",), manifest.manifest_digest, probe.probe_digest)
    if probe.compiler_flags_digest != manifest.compiler_flags_digest:
        return AbiGuardReport(AbiGuardDecisionKind.QUARANTINE_COMPILER_FLAGS, False, False, True, False, ("compiler-flags-digest-mismatch",), manifest.manifest_digest, probe.probe_digest)
    if probe.object_digest != manifest.object_digest:
        return AbiGuardReport(AbiGuardDecisionKind.QUARANTINE_OBJECT_DIGEST, False, False, True, False, ("object-digest-mismatch",), manifest.manifest_digest, probe.probe_digest)
    if probe.max_input_len is None or probe.max_input_len > manifest.max_input_len or probe.max_input_len <= 0:
        return AbiGuardReport(AbiGuardDecisionKind.QUARANTINE_INPUT_LIMIT, False, False, True, False, ("bounded-input-contract-drift",), manifest.manifest_digest, probe.probe_digest)
    return AbiGuardReport(
        AbiGuardDecisionKind.ACCEPT_NATIVE_ARTIFACT,
        accepted=True,
        native_allowed=True,
        fallback_allowed=True,
        watch=False,
        obligations=("rerun-parity", "keep-python-fallback", "pin-artifact-digest"),
        manifest_digest=manifest.manifest_digest,
        probe_digest=probe.probe_digest,
    )
