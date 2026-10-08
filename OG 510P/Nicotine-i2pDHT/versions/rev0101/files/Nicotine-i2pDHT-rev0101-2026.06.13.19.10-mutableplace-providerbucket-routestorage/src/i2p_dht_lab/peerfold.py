"""rev0029 peerbook/deltasketch/liveprobe audit fold."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .ids import DOMAIN, sha256
from .surfaceledger import audit_surface_ledger, entries_for_revision

PEER_FOLD_DOMAIN = DOMAIN + b":peer-fold-v1:"


@dataclass(frozen=True)
class PeerFoldFinding:
    severity: str
    code: str
    path: str
    detail: str


@dataclass(frozen=True)
class PeerFoldReport:
    revision: str
    status: str
    findings: tuple[PeerFoldFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for item in self.findings if item.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for item in self.findings if item.severity == "warning")


def _contains(path: Path, needle: str) -> bool:
    try:
        return needle in path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False


def audit_peer_fold(root: str | Path, *, revision: str = "rev0029") -> PeerFoldReport:
    root_path = Path(root)
    findings: list[PeerFoldFinding] = []
    required_paths = (
        "src/i2p_dht_lab/peerbook.py",
        "src/i2p_dht_lab/deltasketch.py",
        "src/i2p_dht_lab/liveprobe.py",
        "src/i2p_dht_lab/peerfold.py",
        "tests/test_rev0029_peerbook_deltasketch_liveprobe.py",
        "docs/279-rev0029-peerbook-deltasketch-liveprobe.md",
        "docs/280-peerbook-entrance-memory.md",
        "docs/281-delta-sketch-repair-planning.md",
        "docs/282-sam-live-probe-preflight.md",
        "docs/283-peerfold-audit-refactor.md",
    )
    for rel in required_paths:
        if not (root_path / rel).exists():
            findings.append(PeerFoldFinding("error", "missing_peerfold_path", rel, "rev0029 peer fold path is absent"))
    for path, needle in (
        ("PUBLIC_SURFACE.json", "docs/279-rev0029-peerbook-deltasketch-liveprobe.md"),
        ("HEAD_REGISTRY.json", "peerbook"),
        ("HEAD_REGISTRY.json", "delta_sketch"),
        ("HEAD_REGISTRY.json", "live_probe"),
        ("docs/00-index.md", "rev0029 peerbook / deltasketch / liveprobe"),
    ):
        if not _contains(root_path / path, needle):
            findings.append(PeerFoldFinding("error", "missing_peerfold_needle", path, f"missing {needle}"))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        if ledger.error_count:
            findings.append(PeerFoldFinding("error", "surface_ledger_errors", "src/i2p_dht_lab/surfaceledger.py", "surface ledger has errors for rev0029"))
    except Exception as exc:  # pragma: no cover
        findings.append(PeerFoldFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(item.severity == "error" for item in findings) else "fail"
    digest = sha256(PEER_FOLD_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"status": status,
        b"findings": [{b"severity": item.severity, b"code": item.code, b"path": item.path, b"detail": item.detail} for item in findings],
    }))
    return PeerFoldReport(revision, status, tuple(findings), digest)
