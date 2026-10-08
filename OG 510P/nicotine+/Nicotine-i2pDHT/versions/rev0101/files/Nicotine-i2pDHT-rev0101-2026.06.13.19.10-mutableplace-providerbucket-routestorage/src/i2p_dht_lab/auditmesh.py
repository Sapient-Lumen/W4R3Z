"""rev0031 audit mesh for scope fences, obligation debt, and decay.

The cube has many useful historical fold modules.  rev0031 keeps those intact
but pins the current path through one audit mesh: scope fence, proof-obligation
debt, evidence decay, current docs, public pointers, and the active surface
ledger.  The predecessor check stays rev0030 keycrisisfold.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .ids import DOMAIN, sha256
from .keycrisisfold import audit_keycrisis_fold
from .surfaceledger import audit_surface_ledger, entries_for_revision

AUDIT_MESH_DOMAIN = DOMAIN + b":audit-mesh-v1:"


@dataclass(frozen=True)
class AuditMeshFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class AuditMeshReport:
    revision: str
    artifact_stem: str
    status: str
    predecessor_status: str
    surface_ledger_status: str
    findings: tuple[AuditMeshFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


REV0031_MODULES = ("src/i2p_dht_lab/scopefence.py", "src/i2p_dht_lab/obligationdebt.py", "src/i2p_dht_lab/decaymesh.py", "src/i2p_dht_lab/auditmesh.py")
REV0031_TESTS = ("tests/test_rev0031_scopefence_obligation_decay.py",)
REV0031_DOCS = (
    "docs/304-rev0031-scopefence-obligationdebt-decaymesh.md",
    "docs/305-scope-fence-exact-boundary-pressure.md",
    "docs/306-obligation-debt-and-proof-carrying-local-decisions.md",
    "docs/307-decay-mesh-evidence-aging.md",
    "docs/308-auditmesh-refactor-rev0031.md",
    "docs/309-python-surface-rev0031.md",
    "docs/310-wake-from-amnesia-rev0031.md",
    "docs/311-risk-register-rev0031.md",
    "docs/312-proof-obligation-rev0031.md",
)
HEAD_NEEDLES = ("scope_fence", "scopefence", "obligation_debt", "obligationdebt", "decay_mesh", "decaymesh", "audit_mesh", "auditmesh")
PUBLIC_NEEDLES = ("rev0031", "scopefence", "obligationdebt", "decaymesh", "auditmesh", "docs/304-rev0031-scopefence-obligationdebt-decaymesh.md")
INDEX_NEEDLES = ("rev0031 scopefence / obligationdebt / decaymesh", "scope fence", "obligation debt", "decay mesh")


def _contains(path: Path, needle: str) -> bool:
    try:
        return needle in path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False


def audit_audit_mesh(root: str | Path, *, revision: str = "rev0031", artifact_stem: str | None = None) -> AuditMeshReport:
    if revision != "rev0031":
        raise ValueError("auditmesh currently pins the rev0031 active fold")
    root_path = Path(root)
    artifact_stem = artifact_stem or root_path.name
    findings: list[AuditMeshFinding] = []
    for rel in REV0031_MODULES + REV0031_TESTS + REV0031_DOCS:
        if not (root_path / rel).exists():
            findings.append(AuditMeshFinding("error", "missing_rev0031_path", rel, "rev0031 active path is absent"))
    for needle in HEAD_NEEDLES:
        if not _contains(root_path / "HEAD_REGISTRY.json", needle):
            findings.append(AuditMeshFinding("error", "head_registry_missing_needle", "HEAD_REGISTRY.json", f"missing {needle}"))
    for needle in PUBLIC_NEEDLES:
        if not _contains(root_path / "PUBLIC_SURFACE.json", needle):
            findings.append(AuditMeshFinding("error", "public_surface_missing_needle", "PUBLIC_SURFACE.json", f"missing {needle}"))
    for needle in INDEX_NEEDLES:
        if not _contains(root_path / "docs/00-index.md", needle):
            findings.append(AuditMeshFinding("error", "index_missing_needle", "docs/00-index.md", f"missing {needle}"))
    if not _contains(root_path / "README.md", revision):
        findings.append(AuditMeshFinding("error", "readme_revision_drift", "README.md", "README does not name rev0031"))
    if not _contains(root_path / "START_HERE.md", revision):
        findings.append(AuditMeshFinding("error", "start_here_revision_drift", "START_HERE.md", "START_HERE does not name rev0031"))
    try:
        predecessor = audit_keycrisis_fold(root_path, revision="rev0030", artifact_stem=artifact_stem)
        predecessor_status = f"rev0030_keycrisisfold:{predecessor.status}"
        if predecessor.status != "pass":
            findings.append(AuditMeshFinding("error", "predecessor_fold_failed", "src/i2p_dht_lab/keycrisisfold.py", predecessor_status))
    except Exception as exc:  # pragma: no cover
        predecessor_status = "rev0030_keycrisisfold:exception"
        findings.append(AuditMeshFinding("error", "predecessor_fold_exception", "src/i2p_dht_lab/keycrisisfold.py", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        surface_ledger_status = "pass" if ledger.error_count == 0 else "fail"
        if ledger.error_count:
            findings.append(AuditMeshFinding("error", "surface_ledger_errors", "src/i2p_dht_lab/surfaceledger.py", "surface ledger does not pass for rev0031"))
    except Exception as exc:  # pragma: no cover
        surface_ledger_status = "exception"
        findings.append(AuditMeshFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(finding.severity == "error" for finding in findings) else "fail"
    digest = sha256(AUDIT_MESH_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact_stem,
        b"status": status,
        b"predecessor": predecessor_status,
        b"surface_ledger": surface_ledger_status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return AuditMeshReport(revision, artifact_stem, status, predecessor_status, surface_ledger_status, tuple(findings), digest)


# Compatibility with a short-lived branchlet name.
def audit_auditmesh(root: str | Path, *, revision: str = "rev0031", artifact_stem: str | None = None) -> AuditMeshReport:
    return audit_audit_mesh(root, revision=revision, artifact_stem=artifact_stem)
