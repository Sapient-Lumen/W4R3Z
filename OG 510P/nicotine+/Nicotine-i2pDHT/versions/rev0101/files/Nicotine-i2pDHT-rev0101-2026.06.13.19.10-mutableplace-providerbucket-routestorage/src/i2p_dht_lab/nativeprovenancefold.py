"""rev0085 fold audit for native provenance/corpus/quarantine."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .foldmap import audit_fold_map
from .foldregistry import audit_fold_registry
from .ids import DOMAIN, sha256
from .nativebudgetfold import audit_native_budget_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

NATIVE_PROVENANCE_FOLD_DOMAIN = DOMAIN + b":native-provenance-fold-v1:"


@dataclass(frozen=True)
class NativeProvenanceFoldFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class NativeProvenanceFoldReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    foldmap_status: str
    foldregistry_status: str
    surface_ledger_status: str
    findings: tuple[NativeProvenanceFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


def _exists(root: Path, rel: str, needle: str, findings: list[NativeProvenanceFoldFinding]) -> None:
    path = root / rel
    if not path.exists():
        findings.append(NativeProvenanceFoldFinding("error", "missing_path", rel, "rev0085 expected this path"))
        return
    if needle not in path.read_text(encoding="utf-8", errors="replace"):
        findings.append(NativeProvenanceFoldFinding("error", "missing_needle", rel, f"missing needle {needle!r}"))


def audit_native_provenance_fold(root: str | Path, *, revision: str = "rev0085", artifact_stem: str = "") -> NativeProvenanceFoldReport:
    root_path = Path(root)
    artifact = artifact_stem or root_path.name
    findings: list[NativeProvenanceFoldFinding] = []
    checks = {
        "src/i2p_dht_lab/nativeprovenance.py": "NativeProvenanceDecisionKind",
        "src/i2p_dht_lab/nativecorpus.py": "NativeCorpusDecisionKind",
        "src/i2p_dht_lab/nativequarantine.py": "NativeQuarantineDecisionKind",
        "src/i2p_dht_lab/nativeprovenancefold.py": "audit_native_provenance_fold",
        "tests/test_rev0085_nativeprovenance_corpus_quarantine.py": "test_native_provenance_accepts_reproducible_build",
        "docs/888-rev0085-nativeprovenance-corpusquarantine-buildseal.md": "rev0085",
        "docs/889-native-build-provenance.md": "Native build provenance",
        "docs/890-differential-native-corpus.md": "Differential native corpus",
        "docs/891-native-quarantine-store.md": "Native quarantine",
        "docs/892-nativeprovenancefold-audit-refactor.md": "nativeprovenancefold",
        "README.md": "nativeprovenancefold",
        "START_HERE.md": "nativeprovenancefold",
        "PUBLIC_SURFACE.json": "nativeprovenance",
        "HEAD_REGISTRY.json": "rev0085",
    }
    for rel, needle in checks.items():
        _exists(root_path, rel, needle, findings)
    predecessor = audit_native_budget_fold(root_path, revision="rev0084", artifact_stem=artifact)
    fold_map = audit_fold_map(root_path, revision=revision, artifact_stem=artifact)
    fold_registry = audit_fold_registry(root_path, revision=revision)
    surface = audit_surface_ledger(root_path, entries_for_revision(revision))
    if predecessor.status != "pass":
        findings.append(NativeProvenanceFoldFinding("error", "predecessor_failed", "rev0084", predecessor.status))
    if fold_map.status != "pass":
        findings.append(NativeProvenanceFoldFinding("error", "foldmap_failed", "foldmap", fold_map.status))
    if fold_registry.status != "pass":
        findings.append(NativeProvenanceFoldFinding("error", "foldregistry_failed", "foldregistry", fold_registry.status))
    if not surface.ok:
        findings.append(NativeProvenanceFoldFinding("error", "surface_ledger_failed", "surfaceledger", str(surface.error_count)))
    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    digest = sha256(NATIVE_PROVENANCE_FOLD_DOMAIN + bencode({
        b"revision": revision,
        b"artifact": artifact,
        b"status": status,
        b"predecessor": predecessor.status,
        b"foldmap": fold_map.status,
        b"registry": fold_registry.status,
        b"surface": 1 if surface.ok else 0,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return NativeProvenanceFoldReport(revision, artifact, status, predecessor.status, fold_map.status, fold_registry.status, "pass" if surface.ok else "fail", tuple(findings), digest)
