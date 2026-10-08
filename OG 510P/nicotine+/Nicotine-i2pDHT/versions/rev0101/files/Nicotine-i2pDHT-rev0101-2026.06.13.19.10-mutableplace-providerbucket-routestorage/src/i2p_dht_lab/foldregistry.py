"""Declarative fold registry for current revision audits.

Earlier cube turns created many one-off fold modules.  rev0036 starts a tiny
registry so future folds can describe active modules/tests/docs in one place and
then let specific fold modules add predecessor checks.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256

FOLD_REGISTRY_DOMAIN = DOMAIN + b":fold-registry-v1:"


@dataclass(frozen=True)
class FoldRegistryEntry:
    revision: str
    path: str
    role: str
    current: bool = True

    def bvalue(self) -> dict[bytes, object]:
        return {b"revision": self.revision, b"path": self.path, b"role": self.role, b"current": 1 if self.current else 0}


@dataclass(frozen=True)
class FoldRegistryFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class FoldRegistryReport:
    revision: str
    status: str
    entries: tuple[FoldRegistryEntry, ...]
    findings: tuple[FoldRegistryFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")


REV0036_REGISTRY = (
    FoldRegistryEntry("rev0036", "src/i2p_dht_lab/servicecatalog.py", "signed garden service catalogs bound to start profiles"),
    FoldRegistryEntry("rev0036", "src/i2p_dht_lab/loadsheath.py", "per-service load shedding/refusal sheath"),
    FoldRegistryEntry("rev0036", "src/i2p_dht_lab/profilegc.py", "profile/config-change garbage collection preserving hard negatives"),
    FoldRegistryEntry("rev0036", "src/i2p_dht_lab/foldregistry.py", "declarative fold registry"),
    FoldRegistryEntry("rev0036", "src/i2p_dht_lab/servicefold.py", "rev0036 service/start fold audit"),
    FoldRegistryEntry("rev0036", "tests/test_rev0036_servicecatalog_loadsheath_profilegc.py", "current tests"),
    FoldRegistryEntry("rev0036", "docs/360-rev0036-servicecatalog-loadsheath-profilegc.md", "current revision doc"),
    FoldRegistryEntry("rev0036", "docs/361-service-catalog-capsules.md", "service catalog doc"),
    FoldRegistryEntry("rev0036", "docs/362-load-sheath-useful-refusal-profiles.md", "load sheath doc"),
    FoldRegistryEntry("rev0036", "docs/363-profile-gc-config-change-pressure.md", "profile GC doc"),
    FoldRegistryEntry("rev0036", "docs/364-foldregistry-servicefold-audit.md", "fold registry audit doc"),
)

REV0037_REGISTRY = (
    FoldRegistryEntry("rev0037", "src/i2p_dht_lab/serviceticket.py", "exact-scope garden service ticket grants"),
    FoldRegistryEntry("rev0037", "src/i2p_dht_lab/servicereceipt.py", "signed service receipts and refusal-loop pressure"),
    FoldRegistryEntry("rev0037", "src/i2p_dht_lab/ticketfold.py", "rev0037 ticket/receipt fold audit"),
    FoldRegistryEntry("rev0037", "src/i2p_dht_lab/serviceannounce.py", "redacted service announcement branchlet"),
    FoldRegistryEntry("rev0037", "src/i2p_dht_lab/ingressgate.py", "ingress gate announcement pressure branchlet"),
    FoldRegistryEntry("rev0037", "src/i2p_dht_lab/serviceguardfold.py", "rev0037 serviceguard folded branchlet audit"),
    FoldRegistryEntry("rev0037", "tests/test_rev0037_service_ticket_receipt_fold.py", "ticket tests"),
    FoldRegistryEntry("rev0037", "tests/test_rev0037_serviceannounce_ingressgate_registryfold.py", "serviceguard branchlet tests"),
    FoldRegistryEntry("rev0037", "docs/371-rev0037-ticketlane-servicereceipt-registryfold.md", "current revision doc"),
    FoldRegistryEntry("rev0037", "docs/372-service-ticket-exact-scope-grants.md", "service ticket doc"),
    FoldRegistryEntry("rev0037", "docs/373-service-receipts-and-refusal-loops.md", "service receipt doc"),
    FoldRegistryEntry("rev0037", "docs/374-ticketfold-audit-refactor.md", "ticketfold audit doc"),
    FoldRegistryEntry("rev0037", "docs/380-service-announcement-redaction.md", "service announcement branchlet doc"),
    FoldRegistryEntry("rev0037", "docs/381-ingress-gate-announcement-pressure.md", "ingress gate branchlet doc"),
    FoldRegistryEntry("rev0037", "docs/382-serviceguardfold-branchlet.md", "serviceguard branchlet fold doc"),
)


REV0038_REGISTRY = (
    FoldRegistryEntry("rev0038", "src/i2p_dht_lab/catalogwire.py", "folded catalog wire exposure branchlet"),
    FoldRegistryEntry("rev0038", "src/i2p_dht_lab/serviceprobe.py", "folded metadata-budgeted service probe branchlet"),
    FoldRegistryEntry("rev0038", "src/i2p_dht_lab/profilegcjoin.py", "folded profile-GC restart-memory join branchlet"),
    FoldRegistryEntry("rev0038", "src/i2p_dht_lab/catalogsuccession.py", "folded catalog key-crisis succession branchlet"),
    FoldRegistryEntry("rev0038", "src/i2p_dht_lab/servicewithdrawal.py", "folded service withdrawal negative-evidence branchlet"),
    FoldRegistryEntry("rev0038", "src/i2p_dht_lab/servicerelay.py", "folded service relay evidence branchlet"),
    FoldRegistryEntry("rev0038", "src/i2p_dht_lab/serviceusegate.py", "folded exact service-use gate branchlet"),
    FoldRegistryEntry("rev0038", "src/i2p_dht_lab/handofflane.py", "folded service handoff/egress branchlet"),
    FoldRegistryEntry("rev0038", "src/i2p_dht_lab/receiptveil.py", "folded veiled contribution receipt branchlet"),
    FoldRegistryEntry("rev0038", "src/i2p_dht_lab/servicecontinuity.py", "joined service-continuity boundary"),
    FoldRegistryEntry("rev0038", "src/i2p_dht_lab/servicecontinuityfold.py", "rev0038 branchfold audit"),
    FoldRegistryEntry("rev0038", "tests/test_rev0038_servicecontinuity_branchfold.py", "current service-continuity tests"),
    FoldRegistryEntry("rev0038", "docs/383-rev0038-servicecontinuity-branchfold.md", "current revision doc"),
    FoldRegistryEntry("rev0038", "docs/384-service-continuity-joined-boundary.md", "joined service-continuity doc"),
    FoldRegistryEntry("rev0038", "docs/385-branchlet-fold-service-surfaces.md", "folded branchlet service surfaces doc"),
    FoldRegistryEntry("rev0038", "docs/386-profile-gc-catalog-succession-joins.md", "profile-GC/catalog-succession joins doc"),
    FoldRegistryEntry("rev0038", "docs/387-servicecontinuityfold-audit-refactor.md", "servicecontinuityfold audit doc"),
)


REV0039_REGISTRY = (
    FoldRegistryEntry("rev0039", "src/i2p_dht_lab/servicehealth.py", "post-continuity service health pressure"),
    FoldRegistryEntry("rev0039", "src/i2p_dht_lab/servicedrain.py", "safe service drain and hard-negative preservation"),
    FoldRegistryEntry("rev0039", "src/i2p_dht_lab/continuityjournal.py", "restart continuity journal preserving hard negatives"),
    FoldRegistryEntry("rev0039", "src/i2p_dht_lab/serviceopsfold.py", "rev0039 serviceops fold audit"),
    FoldRegistryEntry("rev0039", "tests/test_rev0039_serviceops_journal_drain.py", "serviceops risk tests"),
    FoldRegistryEntry("rev0039", "docs/393-rev0039-serviceops-healthdrain-journalfold.md", "current revision doc"),
    FoldRegistryEntry("rev0039", "docs/394-service-health-post-continuity.md", "servicehealth doc"),
    FoldRegistryEntry("rev0039", "docs/395-service-drain-safe-stop.md", "servicedrain doc"),
    FoldRegistryEntry("rev0039", "docs/396-continuity-journal-restart-memory.md", "continuityjournal doc"),
    FoldRegistryEntry("rev0039", "docs/397-serviceopsfold-audit-refactor.md", "serviceopsfold doc"),
)


REV0040_REGISTRY = (
    FoldRegistryEntry("rev0040", "src/i2p_dht_lab/operatorintent.py", "operator intent capsules for service pause/resume/demotion/freeze"),
    FoldRegistryEntry("rev0040", "src/i2p_dht_lab/servicebreaker.py", "circuit-breaker pressure for post-continuity garden services"),
    FoldRegistryEntry("rev0040", "src/i2p_dht_lab/serviceexit.py", "joined service exit/resume gate"),
    FoldRegistryEntry("rev0040", "src/i2p_dht_lab/operationsfold.py", "rev0040 operations fold audit"),
    FoldRegistryEntry("rev0040", "tests/test_rev0040_operator_breaker_exit_fold.py", "operations risk tests"),
    FoldRegistryEntry("rev0040", "docs/414-rev0040-operatorbreaker-serviceexit-fold.md", "current revision doc"),
    FoldRegistryEntry("rev0040", "docs/415-operator-intent-capsules.md", "operator intent doc"),
    FoldRegistryEntry("rev0040", "docs/416-service-breaker-pressure.md", "service breaker doc"),
    FoldRegistryEntry("rev0040", "docs/417-service-exit-join.md", "service exit doc"),
    FoldRegistryEntry("rev0040", "docs/418-operationsfold-audit-refactor.md", "operationsfold audit doc"),
)


REV0041_REGISTRY = (
    FoldRegistryEntry("rev0041", "src/i2p_dht_lab/routerstop.py", "router-stop shadows after service exit"),
    FoldRegistryEntry("rev0041", "src/i2p_dht_lab/sessionresume.py", "joined session-resume gate"),
    FoldRegistryEntry("rev0041", "src/i2p_dht_lab/exitjournal.py", "append-only exit/control journal"),
    FoldRegistryEntry("rev0041", "src/i2p_dht_lab/controlfold.py", "rev0041 control fold audit"),
    FoldRegistryEntry("rev0041", "tests/test_rev0041_routerstop_sessionresume_exitjournal.py", "control risk tests"),
    FoldRegistryEntry("rev0041", "docs/424-rev0041-routerstop-sessionresume-exitjournal.md", "current revision doc"),
    FoldRegistryEntry("rev0041", "docs/425-router-stop-shadow-boundary.md", "router stop doc"),
    FoldRegistryEntry("rev0041", "docs/426-session-resume-joined-gate.md", "session resume doc"),
    FoldRegistryEntry("rev0041", "docs/427-exit-journal-restart-memory.md", "exit journal doc"),
    FoldRegistryEntry("rev0041", "docs/428-controlfold-audit-refactor.md", "controlfold audit doc"),
)


REV0042_REGISTRY = (
    FoldRegistryEntry("rev0042", "src/i2p_dht_lab/multiservice.py", "multi-service router/session interaction pressure"),
    FoldRegistryEntry("rev0042", "src/i2p_dht_lab/profilecooldown.py", "profile cooldown after emergency freeze"),
    FoldRegistryEntry("rev0042", "src/i2p_dht_lab/operatorkey.py", "operator key rotation/recovery pressure"),
    FoldRegistryEntry("rev0042", "src/i2p_dht_lab/announcementrepair.py", "catalog and announcement repair after bridge disable"),
    FoldRegistryEntry("rev0042", "src/i2p_dht_lab/controlplanefold.py", "rev0042 control-plane fold audit"),
    FoldRegistryEntry("rev0042", "tests/test_rev0042_multiservice_cooldown_keyoperator.py", "current control-plane tests"),
    FoldRegistryEntry("rev0042", "docs/434-rev0042-multiservice-cooldown-keyoperator.md", "current revision doc"),
    FoldRegistryEntry("rev0042", "docs/435-multi-service-router-session-pressure.md", "multi-service doc"),
    FoldRegistryEntry("rev0042", "docs/436-profile-cooldown-emergency-freeze.md", "profile cooldown doc"),
    FoldRegistryEntry("rev0042", "docs/437-operator-key-rotation-recovery.md", "operator key doc"),
    FoldRegistryEntry("rev0042", "docs/438-announcement-repair-after-bridge-disable.md", "announcement repair doc"),
    FoldRegistryEntry("rev0042", "docs/439-controlplanefold-audit-refactor.md", "controlplanefold audit doc"),
)


REV0043_REGISTRY = (
    FoldRegistryEntry("rev0043", "src/i2p_dht_lab/keycompartment.py", "key-compartment role separation pressure"),
    FoldRegistryEntry("rev0043", "src/i2p_dht_lab/authoritysplit.py", "joined authority split gate"),
    FoldRegistryEntry("rev0043", "src/i2p_dht_lab/compartmentfold.py", "rev0043 compartment fold audit"),
    FoldRegistryEntry("rev0043", "tests/test_rev0043_keycompartment_authoritysplit.py", "current compartment tests"),
    FoldRegistryEntry("rev0043", "docs/445-rev0043-keycompartment-authoritysplit-fold.md", "current revision doc"),
    FoldRegistryEntry("rev0043", "docs/446-key-compartment-boundaries.md", "key compartment doc"),
    FoldRegistryEntry("rev0043", "docs/447-authority-split-joined-gate.md", "authority split doc"),
    FoldRegistryEntry("rev0043", "docs/448-compartmentfold-audit-refactor.md", "compartmentfold audit doc"),
)



REV0044_REGISTRY = (
    FoldRegistryEntry("rev0044", "src/i2p_dht_lab/policyfirebreak.py", "subjective policy firebreak before authority-sensitive side effects"),
    FoldRegistryEntry("rev0044", "src/i2p_dht_lab/authorityreceipt.py", "authority receipt mesh preserving scoped local evidence"),
    FoldRegistryEntry("rev0044", "src/i2p_dht_lab/branchsealfold.py", "rev0044 branch-seal fold audit"),
    FoldRegistryEntry("rev0044", "src/i2p_dht_lab/controlintent.py", "folded rev0043 control-intent branchlet"),
    FoldRegistryEntry("rev0044", "src/i2p_dht_lab/bridgefirewall.py", "folded rev0043 bridge-firewall branchlet"),
    FoldRegistryEntry("rev0044", "tests/test_rev0044_policyfirebreak_authorityreceipt_branchseal.py", "current policy/firebreak tests"),
    FoldRegistryEntry("rev0044", "docs/465-rev0044-policyfirebreak-authorityreceipt-branchseal.md", "current revision doc"),
    FoldRegistryEntry("rev0044", "docs/466-policy-firebreak-subjective-authority.md", "policy firebreak doc"),
    FoldRegistryEntry("rev0044", "docs/467-authority-receipt-mesh.md", "authority receipt mesh doc"),
    FoldRegistryEntry("rev0044", "docs/468-branchseal-audit-refactor.md", "branch-seal audit doc"),
    FoldRegistryEntry("rev0044", "artifacts/branchlets/rev0043_controlintent_bridgefirewall/445-rev0043-controlintent-bridgefirewall-foldtrim.md", "folded branchlet doc"),
)


REV0045_REGISTRY = (
    FoldRegistryEntry("rev0045", "src/i2p_dht_lab/bridgeepoch.py", "public bridge epoch windows and stale announcement pressure"),
    FoldRegistryEntry("rev0045", "src/i2p_dht_lab/keyreceiptlane.py", "operator/key authority receipt lane"),
    FoldRegistryEntry("rev0045", "src/i2p_dht_lab/shadowfire.py", "joined shadow-fire public bridge gate"),
    FoldRegistryEntry("rev0045", "src/i2p_dht_lab/bridgeepochfold.py", "rev0045 bridge epoch fold audit"),
    FoldRegistryEntry("rev0045", "tests/test_rev0045_bridgeepoch_keyreceipt_shadowfire.py", "current bridge epoch tests"),
    FoldRegistryEntry("rev0045", "docs/469-rev0045-bridgeepoch-keyreceipt-shadowfire.md", "current revision doc"),
    FoldRegistryEntry("rev0045", "docs/470-public-bridge-epoch-windows.md", "bridge epoch doc"),
    FoldRegistryEntry("rev0045", "docs/471-key-receipt-lane.md", "key receipt lane doc"),
    FoldRegistryEntry("rev0045", "docs/472-shadow-fire-joined-boundary.md", "shadow fire doc"),
    FoldRegistryEntry("rev0045", "docs/473-bridgeepochfold-audit-refactor.md", "bridgeepochfold audit doc"),
)


REV0046_REGISTRY = (
    FoldRegistryEntry("rev0046", "src/i2p_dht_lab/moderationquarantine.py", "subjective moderation quarantine allegations as local pressure"),
    FoldRegistryEntry("rev0046", "src/i2p_dht_lab/redresslane.py", "redress and appeal receipts before quarantine pressure hardens"),
    FoldRegistryEntry("rev0046", "src/i2p_dht_lab/bridgeledger.py", "bridge ledger joining policy, moderation, redress, and shadow-fire"),
    FoldRegistryEntry("rev0046", "src/i2p_dht_lab/moderationfold.py", "rev0046 moderation fold audit"),
    FoldRegistryEntry("rev0046", "tests/test_rev0046_moderation_redress_bridgeledger.py", "current moderation/redress/bridge-ledger tests"),
    FoldRegistryEntry("rev0046", "docs/479-rev0046-moderationquarantine-redresslane-bridgeledger.md", "current revision doc"),
    FoldRegistryEntry("rev0046", "docs/480-moderation-quarantine-as-allegation.md", "moderation quarantine doc"),
    FoldRegistryEntry("rev0046", "docs/481-redress-lane-appeal-receipts.md", "redress lane doc"),
    FoldRegistryEntry("rev0046", "docs/482-bridge-ledger-policy-replay.md", "bridge ledger doc"),
    FoldRegistryEntry("rev0046", "docs/483-moderationfold-audit-refactor.md", "moderationfold audit doc"),
)


REV0047_REGISTRY = (
    FoldRegistryEntry("rev0047", "src/i2p_dht_lab/witnessappealmesh.py", "witness appeal mesh for watched bridge-publication decisions"),
    FoldRegistryEntry("rev0047", "src/i2p_dht_lab/publicationledger.py", "public bridge publication ledger boundary"),
    FoldRegistryEntry("rev0047", "src/i2p_dht_lab/bridgequenchlane.py", "bridge quench/cooldown lane"),
    FoldRegistryEntry("rev0047", "src/i2p_dht_lab/appealpublicationfold.py", "rev0047 appeal/publication fold audit"),
    FoldRegistryEntry("rev0047", "tests/test_rev0047_appeal_publication_quench.py", "current appeal/publication/quench tests"),
    FoldRegistryEntry("rev0047", "docs/490-rev0047-appealmesh-publicationquench-branchfold.md", "current revision doc"),
    FoldRegistryEntry("rev0047", "docs/491-witness-appeal-mesh.md", "witness appeal mesh doc"),
    FoldRegistryEntry("rev0047", "docs/492-publication-ledger-boundary.md", "publication ledger doc"),
    FoldRegistryEntry("rev0047", "docs/493-bridge-quench-lane.md", "bridge quench doc"),
    FoldRegistryEntry("rev0047", "docs/494-appealpublicationfold-audit-refactor.md", "appealpublicationfold audit doc"),
    FoldRegistryEntry("rev0047", "artifacts/branchlets/rev0046_public_bridge_branchlets/README.md", "folded rev0046 public bridge branchlet evidence"),
    FoldRegistryEntry("rev0047", "src/i2p_dht_lab/policyportfolio.py", "policy source portfolio capture-pressure addendum"),
    FoldRegistryEntry("rev0047", "src/i2p_dht_lab/publicationguard.py", "final publication guard addendum"),
    FoldRegistryEntry("rev0047", "src/i2p_dht_lab/publicationfold.py", "policy/publication addendum fold audit"),
    FoldRegistryEntry("rev0047", "tests/test_rev0047_policyportfolio_publicationguard.py", "policy/publication addendum tests"),
    FoldRegistryEntry("rev0047", "docs/501-policy-portfolio-source-capture.md", "policy portfolio addendum doc"),
    FoldRegistryEntry("rev0047", "docs/502-publication-guard-final-side-effect.md", "publication guard addendum doc"),
    FoldRegistryEntry("rev0047", "docs/503-branchlet-fold-rev0046-publication-chaos.md", "publication chaos branchlet fold doc"),
    FoldRegistryEntry("rev0047", "docs/504-publicationfold-audit-refactor.md", "publicationfold addendum doc"),
)


REV0048_REGISTRY = (
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge shadow side-effect boundary after publication/ledger/quench"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "audit receipt diversity for public bridge publication shadows"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress/moderation evidence GC retention boundary"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/shadowauditfold.py", "rev0048 shadow audit fold"),
    FoldRegistryEntry("rev0048", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "current bridge shadow/audit/redress tests"),
    FoldRegistryEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "current revision doc"),
    FoldRegistryEntry("rev0048", "docs/506-bridge-shadow-publication-side-effect.md", "bridge shadow doc"),
    FoldRegistryEntry("rev0048", "docs/507-audit-quorum-local-evidence.md", "audit quorum doc"),
    FoldRegistryEntry("rev0048", "docs/508-redress-gc-retention-boundary.md", "redress GC doc"),
    FoldRegistryEntry("rev0048", "docs/509-shadowauditfold-audit-refactor.md", "shadowauditfold audit doc"),
)

REGISTRY_BY_REVISION = {"rev0036": REV0036_REGISTRY, "rev0037": REV0037_REGISTRY, "rev0038": REV0038_REGISTRY, "rev0039": REV0039_REGISTRY, "rev0040": REV0040_REGISTRY, "rev0041": REV0041_REGISTRY, "rev0042": REV0042_REGISTRY, "rev0043": REV0043_REGISTRY, "rev0044": REV0044_REGISTRY, "rev0045": REV0045_REGISTRY, "rev0046": REV0046_REGISTRY, "rev0047": REV0047_REGISTRY, "rev0048": REV0048_REGISTRY}
NEEDLES_BY_REVISION = {"rev0036": ("servicecatalog", "loadsheath", "profilegc", "foldregistry", "servicefold"), "rev0037": ("serviceticket", "servicereceipt", "ticketfold", "serviceannounce", "ingressgate", "serviceguardfold"), "rev0038": ("servicecontinuity", "servicecontinuityfold", "catalogwire", "serviceprobe", "servicewithdrawal", "servicerelay", "serviceusegate", "handofflane", "receiptveil"), "rev0039": ("servicehealth", "servicedrain", "continuityjournal", "serviceopsfold"), "rev0040": ("operatorintent", "servicebreaker", "serviceexit", "operationsfold"), "rev0041": ("routerstop", "sessionresume", "exitjournal", "controlfold"), "rev0042": ("multiservice", "profilecooldown", "operatorkey", "announcementrepair", "controlplanefold"), "rev0043": ("keycompartment", "authoritysplit", "compartmentfold"), "rev0044": ("policyfirebreak", "authorityreceipt", "branchsealfold", "controlintent", "bridgefirewall"), "rev0045": ("bridgeepoch", "keyreceiptlane", "shadowfire", "bridgeepochfold"), "rev0046": ("moderationquarantine", "redresslane", "bridgeledger", "moderationfold"), "rev0047": ("witnessappealmesh", "publicationledger", "bridgequenchlane", "appealpublicationfold", "policyportfolio", "publicationguard", "publicationfold"), "rev0048": ("bridgeshadow", "auditquorum", "redressgc", "shadowauditfold")}


def registry_for_revision(revision: str) -> tuple[FoldRegistryEntry, ...]:
    try:
        return REGISTRY_BY_REVISION[revision]
    except KeyError as exc:
        raise ValueError(f"unknown fold registry revision: {revision}") from exc


def audit_fold_registry(root: str | Path, *, revision: str = "rev0036", entries: Iterable[FoldRegistryEntry] | None = None) -> FoldRegistryReport:
    root_path = Path(root)
    registry_entries = tuple(entries or registry_for_revision(revision))
    findings: list[FoldRegistryFinding] = []
    for entry in registry_entries:
        if not (root_path / entry.path).exists():
            findings.append(FoldRegistryFinding("error", "missing_registry_path", entry.path, f"missing {entry.role}"))
    public_text = (root_path / "PUBLIC_SURFACE.json").read_text(encoding="utf-8") if (root_path / "PUBLIC_SURFACE.json").exists() else ""
    head_text = (root_path / "HEAD_REGISTRY.json").read_text(encoding="utf-8") if (root_path / "HEAD_REGISTRY.json").exists() else ""
    index_text = (root_path / "docs/00-index.md").read_text(encoding="utf-8") if (root_path / "docs/00-index.md").exists() else ""
    for needle in NEEDLES_BY_REVISION.get(revision, ()): 
        if needle not in public_text:
            findings.append(FoldRegistryFinding("error", "public_surface_missing_needle", "PUBLIC_SURFACE.json", f"missing {needle}"))
        if needle not in head_text:
            findings.append(FoldRegistryFinding("error", "head_registry_missing_needle", "HEAD_REGISTRY.json", f"missing {needle}"))
        if needle not in index_text:
            findings.append(FoldRegistryFinding("error", "index_missing_needle", "docs/00-index.md", f"missing {needle}"))
    status = "pass" if not any(finding.severity == "error" for finding in findings) else "fail"
    digest = sha256(FOLD_REGISTRY_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"status": status,
        b"entries": [entry.bvalue() for entry in registry_entries],
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return FoldRegistryReport(revision, status, registry_entries, tuple(findings), digest)

# rev0048 bridge-shadow/audit-quorum/redress-GC current registry addendum.
REV0048_REGISTRY = (
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "transparency-style publication checkpoint quorum"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge-shadow joined side-effect gate"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress/evidence GC preserving hard negatives"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/bridgeauditfold.py", "rev0048 bridge audit fold"),
    FoldRegistryEntry("rev0048", "tests/test_rev0048_bridge_shadow_audit_redress.py", "current bridge-shadow/audit/redress tests"),
    FoldRegistryEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "current revision doc"),
    FoldRegistryEntry("rev0048", "docs/506-audit-quorum-transparency-witness.md", "audit quorum doc"),
    FoldRegistryEntry("rev0048", "docs/507-bridge-shadow-final-side-effect.md", "bridge shadow doc"),
    FoldRegistryEntry("rev0048", "docs/508-redress-gc-hard-negative-memory.md", "redress GC doc"),
    FoldRegistryEntry("rev0048", "docs/509-bridgeauditfold-audit-refactor.md", "bridgeauditfold doc"),
)
REGISTRY_BY_REVISION["rev0048"] = REV0048_REGISTRY
NEEDLES_BY_REVISION["rev0048"] = ("auditquorum", "bridgeshadow", "redressgc", "bridgeauditfold")

# rev0048 final registry reconciliation.
REV0048_REGISTRY = (
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge shadow public side-effect boundary"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "local audit receipts for public bridge shadow evidence"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress/evidence GC retention pressure"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/bridgeshadowfold.py", "rev0048 bridgeshadow fold audit"),
    FoldRegistryEntry("rev0048", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "current bridge-shadow/audit/redress-GC tests"),
    FoldRegistryEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "current revision doc"),
    FoldRegistryEntry("rev0048", "docs/506-bridge-shadow-public-side-effect.md", "bridge shadow doc"),
    FoldRegistryEntry("rev0048", "docs/507-audit-quorum-local-receipts.md", "audit quorum doc"),
    FoldRegistryEntry("rev0048", "docs/508-redress-gc-retention-pressure.md", "redress GC doc"),
    FoldRegistryEntry("rev0048", "docs/509-bridgeshadowfold-audit-refactor.md", "bridgeshadowfold doc"),
    FoldRegistryEntry("rev0048", "artifacts/branchlets/rev0048_publicshadow_bridgeaudit/README.md", "folded publicshadow/bridgeaudit branchlet"),
)
REGISTRY_BY_REVISION["rev0048"] = REV0048_REGISTRY
NEEDLES_BY_REVISION["rev0048"] = ("bridgeshadow", "auditquorum", "redressgc", "bridgeshadowfold")

# rev0048 governance-fold final reconciliation.
REV0048_REGISTRY = (
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge-shadow dry-run gate before public bridge side effects"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "local audit evidence for public bridge shadow boundaries"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress/evidence GC preserving hard negatives"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/bridgegovernancefold.py", "rev0048 bridge governance fold audit"),
    FoldRegistryEntry("rev0048", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "current bridge-shadow/audit/redress-GC tests"),
    FoldRegistryEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "current revision doc"),
    FoldRegistryEntry("rev0048", "docs/506-bridge-shadow-side-effect-dryrun.md", "bridge shadow doc"),
    FoldRegistryEntry("rev0048", "docs/507-audit-quorum-is-local-evidence.md", "audit quorum doc"),
    FoldRegistryEntry("rev0048", "docs/508-redress-gc-hard-negative-retention.md", "redress GC doc"),
    FoldRegistryEntry("rev0048", "docs/509-bridgegovernancefold-audit-refactor.md", "bridge governance fold doc"),
    FoldRegistryEntry("rev0048", "artifacts/branchlets/rev0048_stale_doc_branchlet/README.md", "stale rev0048 doc branchlet preserved"),
    FoldRegistryEntry("rev0048", "artifacts/branchlets/rev0048_stale_code_branchlet/README.md", "stale rev0048 code branchlet preserved"),
)
REGISTRY_BY_REVISION["rev0048"] = REV0048_REGISTRY
NEEDLES_BY_REVISION["rev0048"] = ("bridgeshadow", "auditquorum", "redressgc", "bridgegovernancefold")

# rev0048 final bridge-governance fold override.
REV0048_REGISTRY = (
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge shadow dry-run side-effect boundary"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "audit quorum local evidence"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress/evidence GC retention"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/bridgegovernancefold.py", "rev0048 bridge governance fold"),
    FoldRegistryEntry("rev0048", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "current bridge governance tests"),
    FoldRegistryEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "current revision doc"),
    FoldRegistryEntry("rev0048", "docs/506-bridge-shadow-side-effect-dryrun.md", "bridge shadow dry-run doc"),
    FoldRegistryEntry("rev0048", "docs/507-audit-quorum-is-local-evidence.md", "audit quorum doc"),
    FoldRegistryEntry("rev0048", "docs/508-redress-gc-hard-negative-retention.md", "redress GC doc"),
    FoldRegistryEntry("rev0048", "docs/509-bridgegovernancefold-audit-refactor.md", "bridgegovernancefold doc"),
)
REGISTRY_BY_REVISION["rev0048"] = REV0048_REGISTRY
NEEDLES_BY_REVISION["rev0048"] = ("bridgeshadow", "auditquorum", "redressgc", "bridgegovernancefold")

# rev0048 canonical registry override after stale bridgeaudit branchlet fold-out.
REV0048_REGISTRY = (
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge shadow side-effect boundary after publication/ledger/quench"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "audit receipt diversity for public bridge publication shadows"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress/moderation evidence GC retention boundary"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/shadowauditfold.py", "rev0048 shadow audit fold"),
    FoldRegistryEntry("rev0048", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "current bridge shadow/audit/redress tests"),
    FoldRegistryEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "current revision doc"),
    FoldRegistryEntry("rev0048", "docs/506-bridge-shadow-publication-side-effect.md", "bridge shadow doc"),
    FoldRegistryEntry("rev0048", "docs/507-audit-quorum-local-evidence.md", "audit quorum doc"),
    FoldRegistryEntry("rev0048", "docs/508-redress-gc-retention-boundary.md", "redress GC doc"),
    FoldRegistryEntry("rev0048", "docs/509-shadowauditfold-audit-refactor.md", "shadowauditfold audit doc"),
)
REGISTRY_BY_REVISION["rev0048"] = REV0048_REGISTRY
NEEDLES_BY_REVISION["rev0048"] = ("bridgeshadow", "auditquorum", "redressgc", "shadowauditfold")

# rev0048 final shadowauditfold registry reconciliation.
REV0048_REGISTRY = (
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge shadow publication side-effect boundary"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "local audit receipt evidence for bridge shadows"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress/evidence GC retention boundary"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/shadowauditfold.py", "rev0048 shadowauditfold audit"),
    FoldRegistryEntry("rev0048", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "current bridge-shadow/audit/redress-GC tests"),
    FoldRegistryEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "current revision doc"),
    FoldRegistryEntry("rev0048", "docs/506-bridge-shadow-publication-side-effect.md", "bridge shadow doc"),
    FoldRegistryEntry("rev0048", "docs/507-audit-quorum-local-evidence.md", "audit quorum doc"),
    FoldRegistryEntry("rev0048", "docs/508-redress-gc-retention-boundary.md", "redress GC doc"),
    FoldRegistryEntry("rev0048", "docs/509-shadowauditfold-audit-refactor.md", "shadowauditfold doc"),
    FoldRegistryEntry("rev0048", "artifacts/branchlets/rev0048_publicshadow_bridgeaudit/README.md", "folded publicshadow/bridgeaudit branchlet"),
)
REGISTRY_BY_REVISION["rev0048"] = REV0048_REGISTRY
NEEDLES_BY_REVISION["rev0048"] = ("bridgeshadow", "auditquorum", "redressgc", "shadowauditfold")


# rev0048 canonical bridge-governance override: final active rev0048 path after
# shadowauditfold/bridgeaudit branchlets were preserved as history.
REV0048_REGISTRY = (
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge shadow dry-run side-effect boundary after publication/ledger/quench"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "audit quorum local evidence for public bridge shadow boundaries"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress/evidence GC preserving hard negatives and appeals"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/bridgegovernancefold.py", "rev0048 bridge governance fold audit"),
    FoldRegistryEntry("rev0048", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "current bridge-shadow/audit/redress-GC tests"),
    FoldRegistryEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "current revision doc"),
    FoldRegistryEntry("rev0048", "docs/506-bridge-shadow-side-effect-dryrun.md", "bridge shadow dry-run doc"),
    FoldRegistryEntry("rev0048", "docs/507-audit-quorum-is-local-evidence.md", "audit quorum doc"),
    FoldRegistryEntry("rev0048", "docs/508-redress-gc-hard-negative-retention.md", "redress GC doc"),
    FoldRegistryEntry("rev0048", "docs/509-bridgegovernancefold-audit-refactor.md", "bridgegovernancefold audit doc"),
    FoldRegistryEntry("rev0048", "artifacts/branchlets/rev0048_publicshadow_bridgeaudit/README.md", "folded publicshadow/bridgeaudit branchlet history"),
)
REGISTRY_BY_REVISION["rev0048"] = REV0048_REGISTRY
NEEDLES_BY_REVISION["rev0048"] = ("bridgeshadow", "auditquorum", "redressgc", "bridgegovernancefold")

# rev0048 FINAL canonical shadowauditfold registry override after branchlet reconciliation.
REV0048_REGISTRY = (
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge shadow publication side-effect boundary"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "audit quorum local evidence for bridge shadow decisions"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress/evidence GC retention boundary"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/shadowauditfold.py", "rev0048 shadowauditfold audit"),
    FoldRegistryEntry("rev0048", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "current bridge-shadow/audit/redress-GC tests"),
    FoldRegistryEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "current revision doc"),
    FoldRegistryEntry("rev0048", "docs/506-bridge-shadow-publication-side-effect.md", "bridge shadow publication doc"),
    FoldRegistryEntry("rev0048", "docs/507-audit-quorum-local-evidence.md", "audit quorum doc"),
    FoldRegistryEntry("rev0048", "docs/508-redress-gc-retention-boundary.md", "redress GC doc"),
    FoldRegistryEntry("rev0048", "docs/509-shadowauditfold-audit-refactor.md", "shadowauditfold doc"),
    FoldRegistryEntry("rev0048", "artifacts/branchlets/rev0048_publicshadow_bridgeaudit/README.md", "folded publicshadow/bridgeaudit branchlet"),
    FoldRegistryEntry("rev0048", "artifacts/branchlets/rev0048_accidental_bridge_shadow_redressgc/test_rev0048_bridge_shadow_audit_redressgc.py", "folded accidental test branchlet"),
)
REGISTRY_BY_REVISION["rev0048"] = REV0048_REGISTRY
NEEDLES_BY_REVISION["rev0048"] = ("bridgeshadow", "auditquorum", "redressgc", "shadowauditfold")

# rev0048 absolute final shadowauditfold registry override after bridgegovernance branchlet quarantine.
REV0048_REGISTRY = (
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge shadow publication side-effect boundary"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "local audit receipt evidence for bridge shadows"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress/evidence GC retention boundary"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/shadowauditfold.py", "rev0048 shadowauditfold audit"),
    FoldRegistryEntry("rev0048", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "current bridge-shadow/audit/redress-GC tests"),
    FoldRegistryEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "current revision doc"),
    FoldRegistryEntry("rev0048", "docs/506-bridge-shadow-publication-side-effect.md", "bridge shadow doc"),
    FoldRegistryEntry("rev0048", "docs/507-audit-quorum-local-evidence.md", "audit quorum doc"),
    FoldRegistryEntry("rev0048", "docs/508-redress-gc-retention-boundary.md", "redress GC doc"),
    FoldRegistryEntry("rev0048", "docs/509-shadowauditfold-audit-refactor.md", "shadowauditfold doc"),
    FoldRegistryEntry("rev0048", "artifacts/branchlets/rev0048_publicshadow_bridgeaudit/README.md", "folded publicshadow/bridgeaudit branchlet"),
    FoldRegistryEntry("rev0048", "artifacts/branchlets/rev0048_stale_doc_branchlet/README.md", "folded stale doc branchlet"),
    FoldRegistryEntry("rev0048", "artifacts/branchlets/rev0048_stale_code_branchlet/README.md", "folded stale code branchlet"),
)
REGISTRY_BY_REVISION["rev0048"] = REV0048_REGISTRY
NEEDLES_BY_REVISION["rev0048"] = ("bridgeshadow", "auditquorum", "redressgc", "shadowauditfold")


# rev0048 canonical bridge-governance override: final active path aligned with
# bridgegovernancefold.REV0048_PATHS after branchlet reconciliation.
REV0048_REGISTRY = (
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge shadow dry-run side-effect boundary after publication/ledger/quench"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "audit quorum local evidence for public bridge shadow boundaries"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress/evidence GC preserving hard negatives and appeals"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/bridgegovernancefold.py", "rev0048 bridge governance fold audit"),
    FoldRegistryEntry("rev0048", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "current bridge-shadow/audit/redress-GC tests"),
    FoldRegistryEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "current revision doc"),
    FoldRegistryEntry("rev0048", "docs/506-bridge-shadow-side-effect-dryrun.md", "bridge shadow dry-run doc"),
    FoldRegistryEntry("rev0048", "docs/507-audit-quorum-is-local-evidence.md", "audit quorum doc"),
    FoldRegistryEntry("rev0048", "docs/508-redress-gc-hard-negative-retention.md", "redress GC doc"),
    FoldRegistryEntry("rev0048", "docs/509-bridgegovernancefold-audit-refactor.md", "bridgegovernancefold audit doc"),
    FoldRegistryEntry("rev0048", "artifacts/branchlets/rev0048_publicshadow_bridgeaudit/README.md", "folded publicshadow/bridgeaudit branchlet history"),
)
REGISTRY_BY_REVISION["rev0048"] = REV0048_REGISTRY
NEEDLES_BY_REVISION["rev0048"] = ("bridgeshadow", "auditquorum", "redressgc", "bridgegovernancefold")

# rev0048 final active-path repair after branchlet reconciliation.
REV0048_REGISTRY = (
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge shadow public side-effect boundary"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "local audit receipts for public bridge publication shadows"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress/moderation evidence GC retention boundary"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/bridgegovernancefold.py", "rev0048 bridge governance fold audit wrapper"),
    FoldRegistryEntry("rev0048", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "current bridge-shadow/audit/redress-GC tests"),
    FoldRegistryEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "current revision doc"),
    FoldRegistryEntry("rev0048", "docs/506-bridge-shadow-publication-side-effect.md", "bridge shadow doc"),
    FoldRegistryEntry("rev0048", "docs/507-audit-quorum-local-evidence.md", "audit quorum doc"),
    FoldRegistryEntry("rev0048", "docs/508-redress-gc-retention-boundary.md", "redress GC doc"),
    FoldRegistryEntry("rev0048", "docs/509-shadowauditfold-audit-refactor.md", "bridge governance fold doc"),
    FoldRegistryEntry("rev0048", "artifacts/branchlets/rev0048_stale_doc_branchlet/README.md", "stale rev0048 doc branchlet preserved"),
    FoldRegistryEntry("rev0048", "artifacts/branchlets/rev0048_stale_code_branchlet/README.md", "stale rev0048 code branchlet preserved"),
)
REGISTRY_BY_REVISION["rev0048"] = REV0048_REGISTRY
NEEDLES_BY_REVISION["rev0048"] = ("bridgeshadow", "auditquorum", "redressgc", "bridgegovernancefold")

# rev0048 ABSOLUTE FINAL canonical bridge-governance registry override after stale
# shadowaudit/bridgeaudit branchlet path cleanup.
REV0048_REGISTRY = (
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge shadow dry-run side-effect boundary after publication/ledger/quench"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "audit quorum local evidence for public bridge shadow boundaries"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress/evidence GC preserving hard negatives and appeals"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/bridgegovernancefold.py", "rev0048 bridge governance fold audit"),
    FoldRegistryEntry("rev0048", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "current bridge-shadow/audit/redress-GC tests"),
    FoldRegistryEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "current revision doc"),
    FoldRegistryEntry("rev0048", "docs/506-bridge-shadow-side-effect-dryrun.md", "bridge shadow dry-run doc"),
    FoldRegistryEntry("rev0048", "docs/507-audit-quorum-is-local-evidence.md", "audit quorum doc"),
    FoldRegistryEntry("rev0048", "docs/508-redress-gc-hard-negative-retention.md", "redress GC doc"),
    FoldRegistryEntry("rev0048", "docs/509-bridgegovernancefold-audit-refactor.md", "bridgegovernancefold audit doc"),
)
REGISTRY_BY_REVISION["rev0048"] = REV0048_REGISTRY
NEEDLES_BY_REVISION["rev0048"] = ("bridgeshadow", "auditquorum", "redressgc", "bridgegovernancefold")

# rev0048 TRUE LAST active registry override: shadowauditfold is canonical; bridgegovernancefold is historical branchlet glue.
REV0048_REGISTRY = (
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge shadow publication side-effect boundary"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "audit quorum local evidence for bridge shadow decisions"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress/evidence GC retention boundary"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/shadowauditfold.py", "rev0048 shadowauditfold audit"),
    FoldRegistryEntry("rev0048", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "current bridge-shadow/audit/redress-GC tests"),
    FoldRegistryEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "current revision doc"),
    FoldRegistryEntry("rev0048", "docs/506-bridge-shadow-publication-side-effect.md", "bridge shadow doc"),
    FoldRegistryEntry("rev0048", "docs/507-audit-quorum-local-evidence.md", "audit quorum doc"),
    FoldRegistryEntry("rev0048", "docs/508-redress-gc-retention-boundary.md", "redress GC doc"),
    FoldRegistryEntry("rev0048", "docs/509-shadowauditfold-audit-refactor.md", "shadowauditfold doc"),
    FoldRegistryEntry("rev0048", "artifacts/branchlets/rev0048_publicshadow_bridgeaudit/README.md", "folded publicshadow/bridgeaudit branchlet"),
    FoldRegistryEntry("rev0048", "artifacts/branchlets/rev0048_stale_doc_branchlet/README.md", "folded stale doc branchlet"),
    FoldRegistryEntry("rev0048", "artifacts/branchlets/rev0048_stale_code_branchlet/README.md", "folded stale code branchlet"),
)
REGISTRY_BY_REVISION["rev0048"] = REV0048_REGISTRY
NEEDLES_BY_REVISION["rev0048"] = ("bridgeshadow", "auditquorum", "redressgc", "shadowauditfold")

# rev0048 FINAL-FINAL shadowauditfold registry override: appended after all historical branchlet overrides.
REV0048_REGISTRY = (
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge shadow publication side-effect boundary"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "local audit receipt evidence for bridge shadows"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress/evidence GC retention boundary"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/shadowauditfold.py", "rev0048 shadowauditfold audit"),
    FoldRegistryEntry("rev0048", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "current bridge-shadow/audit/redress-GC tests"),
    FoldRegistryEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "current revision doc"),
    FoldRegistryEntry("rev0048", "docs/506-bridge-shadow-publication-side-effect.md", "bridge shadow doc"),
    FoldRegistryEntry("rev0048", "docs/507-audit-quorum-local-evidence.md", "audit quorum doc"),
    FoldRegistryEntry("rev0048", "docs/508-redress-gc-retention-boundary.md", "redress GC doc"),
    FoldRegistryEntry("rev0048", "docs/509-shadowauditfold-audit-refactor.md", "shadowauditfold doc"),
    FoldRegistryEntry("rev0048", "artifacts/branchlets/rev0048_publicshadow_bridgeaudit/README.md", "folded publicshadow/bridgeaudit branchlet"),
    FoldRegistryEntry("rev0048", "artifacts/branchlets/rev0048_stale_doc_branchlet/README.md", "folded stale doc branchlet"),
    FoldRegistryEntry("rev0048", "artifacts/branchlets/rev0048_stale_code_branchlet/README.md", "folded stale code branchlet"),
)
REGISTRY_BY_REVISION["rev0048"] = REV0048_REGISTRY
NEEDLES_BY_REVISION["rev0048"] = ("bridgeshadow", "auditquorum", "redressgc", "shadowauditfold")

# rev0048 TRUE FINAL shadowauditfold registry override after bridgegovernance branchlet quarantine.
REV0048_REGISTRY = (
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge shadow public side-effect boundary"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "local audit receipts for public bridge publication shadows"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress/moderation evidence GC retention boundary"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/shadowauditfold.py", "rev0048 shadowauditfold audit"),
    FoldRegistryEntry("rev0048", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "current bridge-shadow/audit/redress-GC tests"),
    FoldRegistryEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "current revision doc"),
    FoldRegistryEntry("rev0048", "docs/506-bridge-shadow-publication-side-effect.md", "bridge shadow doc"),
    FoldRegistryEntry("rev0048", "docs/507-audit-quorum-local-evidence.md", "audit quorum doc"),
    FoldRegistryEntry("rev0048", "docs/508-redress-gc-retention-boundary.md", "redress GC doc"),
    FoldRegistryEntry("rev0048", "docs/509-shadowauditfold-audit-refactor.md", "shadowauditfold doc"),
    FoldRegistryEntry("rev0048", "artifacts/branchlets/rev0048_publicshadow_bridgeaudit/README.md", "folded publicshadow/bridgeaudit branchlet"),
    FoldRegistryEntry("rev0048", "artifacts/branchlets/rev0048_stale_doc_branchlet/README.md", "folded stale doc branchlet"),
    FoldRegistryEntry("rev0048", "artifacts/branchlets/rev0048_stale_code_branchlet/README.md", "folded stale code branchlet"),
)
REGISTRY_BY_REVISION["rev0048"] = REV0048_REGISTRY
NEEDLES_BY_REVISION["rev0048"] = ("bridgeshadow", "auditquorum", "redressgc", "shadowauditfold")

# rev0048 ACTUAL FINAL bridgegovernancefold registry override. This line intentionally
# supersedes stale shadowauditfold branchlet overrides left above for history.
REV0048_REGISTRY = (
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge shadow dry-run side-effect boundary after publication/ledger/quench"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "audit quorum local evidence for public bridge shadow boundaries"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress/evidence GC preserving hard negatives and appeals"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/bridgegovernancefold.py", "rev0048 bridge governance fold audit"),
    FoldRegistryEntry("rev0048", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "current bridge-shadow/audit/redress-GC tests"),
    FoldRegistryEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "current revision doc"),
    FoldRegistryEntry("rev0048", "docs/506-bridge-shadow-side-effect-dryrun.md", "bridge shadow dry-run doc"),
    FoldRegistryEntry("rev0048", "docs/507-audit-quorum-is-local-evidence.md", "audit quorum doc"),
    FoldRegistryEntry("rev0048", "docs/508-redress-gc-hard-negative-retention.md", "redress GC doc"),
    FoldRegistryEntry("rev0048", "docs/509-bridgegovernancefold-audit-refactor.md", "bridgegovernancefold audit doc"),
)
REGISTRY_BY_REVISION["rev0048"] = REV0048_REGISTRY
NEEDLES_BY_REVISION["rev0048"] = ("bridgeshadow", "auditquorum", "redressgc", "bridgegovernancefold")

# rev0048 ABSOLUTE FINAL ACTIVE registry override: shadowauditfold chosen as active path; bridgegovernancefold kept as branchlet history.
REV0048_REGISTRY = (
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge shadow publication side-effect boundary"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "audit quorum local evidence for bridge shadow decisions"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress/evidence GC retention boundary"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/shadowauditfold.py", "rev0048 shadowauditfold audit"),
    FoldRegistryEntry("rev0048", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "current bridge-shadow/audit/redress-GC tests"),
    FoldRegistryEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "current revision doc"),
    FoldRegistryEntry("rev0048", "docs/506-bridge-shadow-publication-side-effect.md", "bridge shadow doc"),
    FoldRegistryEntry("rev0048", "docs/507-audit-quorum-local-evidence.md", "audit quorum doc"),
    FoldRegistryEntry("rev0048", "docs/508-redress-gc-retention-boundary.md", "redress GC doc"),
    FoldRegistryEntry("rev0048", "docs/509-shadowauditfold-audit-refactor.md", "shadowauditfold doc"),
)
REGISTRY_BY_REVISION["rev0048"] = REV0048_REGISTRY
NEEDLES_BY_REVISION["rev0048"] = ("bridgeshadow", "auditquorum", "redressgc", "shadowauditfold")

# rev0048 final bridgegovernancefold registry override after JSON/doc repair.
REV0048_REGISTRY = (
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge shadow public side-effect dry-run boundary"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "local audit receipt evidence for bridge shadows"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress/evidence GC retention boundary"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/bridgegovernancefold.py", "rev0048 bridgegovernancefold audit"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/shadowauditfold.py", "rev0048 shadowauditfold compatibility audit"),
    FoldRegistryEntry("rev0048", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "current bridge-shadow/audit/redress-GC tests"),
    FoldRegistryEntry("rev0048", "tests/test_rev0048_bridge_shadow_audit_redressgc.py", "compatibility pointer test"),
    FoldRegistryEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "current revision doc"),
    FoldRegistryEntry("rev0048", "docs/506-bridge-shadow-publication-side-effect.md", "bridge shadow doc"),
    FoldRegistryEntry("rev0048", "docs/507-audit-quorum-local-evidence.md", "audit quorum doc"),
    FoldRegistryEntry("rev0048", "docs/508-redress-gc-retention-boundary.md", "redress GC doc"),
    FoldRegistryEntry("rev0048", "docs/509-shadowauditfold-audit-refactor.md", "bridgegovernancefold/shadowauditfold audit doc"),
    FoldRegistryEntry("rev0048", "artifacts/branchlets/rev0048_publicshadow_bridgeaudit/README.md", "folded publicshadow/bridgeaudit branchlet"),
    FoldRegistryEntry("rev0048", "artifacts/branchlets/rev0048_stale_doc_branchlet/README.md", "folded stale doc branchlet"),
    FoldRegistryEntry("rev0048", "artifacts/branchlets/rev0048_stale_code_branchlet/README.md", "folded stale code branchlet"),
)
REGISTRY_BY_REVISION["rev0048"] = REV0048_REGISTRY
NEEDLES_BY_REVISION["rev0048"] = ("bridgeshadow", "auditquorum", "redressgc", "bridgegovernancefold")

# rev0048 TRUE FINAL shadowauditfold registry override after bridgegovernance branchlet quarantine.
REV0048_REGISTRY = (
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge shadow public side-effect boundary"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "local audit receipts for public bridge publication shadows"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress/moderation evidence GC retention boundary"),
    FoldRegistryEntry("rev0048", "src/i2p_dht_lab/shadowauditfold.py", "rev0048 shadowauditfold audit"),
    FoldRegistryEntry("rev0048", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "current bridge-shadow/audit/redress-GC tests"),
    FoldRegistryEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "current revision doc"),
    FoldRegistryEntry("rev0048", "docs/506-bridge-shadow-publication-side-effect.md", "bridge shadow doc"),
    FoldRegistryEntry("rev0048", "docs/507-audit-quorum-local-evidence.md", "audit quorum doc"),
    FoldRegistryEntry("rev0048", "docs/508-redress-gc-retention-boundary.md", "redress GC doc"),
    FoldRegistryEntry("rev0048", "docs/509-shadowauditfold-audit-refactor.md", "shadowauditfold doc"),
    FoldRegistryEntry("rev0048", "artifacts/branchlets/rev0048_publicshadow_bridgeaudit/README.md", "folded publicshadow/bridgeaudit branchlet"),
    FoldRegistryEntry("rev0048", "artifacts/branchlets/rev0048_stale_doc_branchlet/README.md", "folded stale doc branchlet"),
    FoldRegistryEntry("rev0048", "artifacts/branchlets/rev0048_stale_code_branchlet/README.md", "folded stale code branchlet"),
)
REGISTRY_BY_REVISION["rev0048"] = REV0048_REGISTRY
NEEDLES_BY_REVISION["rev0048"] = ("bridgeshadow", "auditquorum", "redressgc", "shadowauditfold")

# rev0049 active publish dry-run / witness compaction / scope-journal registry.
REV0049_REGISTRY = (
    FoldRegistryEntry("rev0049", "src/i2p_dht_lab/publishdryrun.py", "no-network publish dry-run side-effect boundary"),
    FoldRegistryEntry("rev0049", "src/i2p_dht_lab/witnesscompact.py", "witness/evidence compaction preserving hard negatives"),
    FoldRegistryEntry("rev0049", "src/i2p_dht_lab/scopejournal.py", "scoped restart journal for publish/witness memory"),
    FoldRegistryEntry("rev0049", "src/i2p_dht_lab/publishfold.py", "rev0049 publishfold audit"),
    FoldRegistryEntry("rev0049", "tests/test_rev0049_publishdryrun_witnesscompact_scopejournal.py", "current publish/witness/journal tests"),
    FoldRegistryEntry("rev0049", "docs/510-rev0049-publishdryrun-witnesscompact-scopejournal.md", "current revision doc"),
    FoldRegistryEntry("rev0049", "docs/511-publish-dryrun-side-effect-boundary.md", "publish dry-run doc"),
    FoldRegistryEntry("rev0049", "docs/512-witness-compaction-memory-pressure.md", "witness compaction doc"),
    FoldRegistryEntry("rev0049", "docs/513-scope-journal-restart-boundary.md", "scope journal doc"),
    FoldRegistryEntry("rev0049", "docs/514-publishfold-audit-refactor.md", "publishfold doc"),
)
REGISTRY_BY_REVISION["rev0049"] = REV0049_REGISTRY
NEEDLES_BY_REVISION["rev0049"] = ("publishdryrun", "witnesscompact", "scopejournal", "publishfold")

# rev0049 public outbox / audit-gap registry.
REV0049_REGISTRY = (
    FoldRegistryEntry("rev0049", "src/i2p_dht_lab/publicoutbox.py", "signed exact-scope public outbox staging"),
    FoldRegistryEntry("rev0049", "src/i2p_dht_lab/auditgap.py", "audit-gap repair and withdrawal planning"),
    FoldRegistryEntry("rev0049", "src/i2p_dht_lab/outboxfold.py", "rev0049 outboxfold audit"),
    FoldRegistryEntry("rev0049", "tests/test_rev0049_publicoutbox_auditgap_fold.py", "current publicoutbox/auditgap tests"),
    FoldRegistryEntry("rev0049", "docs/514-rev0049-outboxlane-auditgap-fold.md", "current revision doc"),
    FoldRegistryEntry("rev0049", "docs/515-public-outbox-side-effect-staging.md", "publicoutbox doc"),
    FoldRegistryEntry("rev0049", "docs/516-audit-gap-repair-planning.md", "auditgap doc"),
    FoldRegistryEntry("rev0049", "docs/517-outboxfold-audit-refactor.md", "outboxfold doc"),
)
REGISTRY_BY_REVISION["rev0049"] = REV0049_REGISTRY
NEEDLES_BY_REVISION["rev0049"] = ("publicoutbox", "auditgap", "outboxfold")

# rev0049 integrated registry override after publish/outbox branchlets and
# auditcompact refute/fork-preservation lane were reconciled.
REV0049_REGISTRY = (
    FoldRegistryEntry("rev0049", "src/i2p_dht_lab/publishdryrun.py", "no-network public-edge dry-run"),
    FoldRegistryEntry("rev0049", "src/i2p_dht_lab/witnesscompact.py", "witness compaction preserving hard evidence"),
    FoldRegistryEntry("rev0049", "src/i2p_dht_lab/scopejournal.py", "scope journal restart memory"),
    FoldRegistryEntry("rev0049", "src/i2p_dht_lab/publishdryrunfold.py", "publishdryrunfold audit"),
    FoldRegistryEntry("rev0049", "src/i2p_dht_lab/publicoutbox.py", "public outbox side-effect staging"),
    FoldRegistryEntry("rev0049", "src/i2p_dht_lab/auditgap.py", "audit gap repair/withdraw planning"),
    FoldRegistryEntry("rev0049", "src/i2p_dht_lab/outboxfold.py", "outboxfold audit"),
    FoldRegistryEntry("rev0049", "src/i2p_dht_lab/auditcompact.py", "audit receipt compaction preserving refutes/forks"),
    FoldRegistryEntry("rev0049", "tests/test_rev0049_publishdryrun_witnesscompact_scopejournal.py", "publishdryrun tests"),
    FoldRegistryEntry("rev0049", "tests/test_rev0049_publicoutbox_auditgap_fold.py", "outbox tests"),
    FoldRegistryEntry("rev0049", "tests/test_rev0049_publishdryrun_auditcompact_scopejournal.py", "auditcompact tests"),
    FoldRegistryEntry("rev0049", "docs/510-rev0049-publishdryrun-witnesscompact-scopejournal.md", "current revision doc"),
    FoldRegistryEntry("rev0049", "docs/515-publish-dry-run-public-edge.md", "publishdryrun doc"),
    FoldRegistryEntry("rev0049", "docs/516-witness-compact-hard-evidence.md", "witnesscompact doc"),
    FoldRegistryEntry("rev0049", "docs/517-scope-journal-restart-memory.md", "scopejournal doc"),
    FoldRegistryEntry("rev0049", "docs/518-publishdryrunfold-audit-refactor.md", "publishdryrunfold doc"),
    FoldRegistryEntry("rev0049", "docs/515-public-outbox-side-effect-staging.md", "publicoutbox doc"),
    FoldRegistryEntry("rev0049", "docs/516-audit-gap-repair-planning.md", "auditgap doc"),
    FoldRegistryEntry("rev0049", "docs/517-outboxfold-audit-refactor.md", "outboxfold doc"),
    FoldRegistryEntry("rev0049", "docs/523-auditcompact-refute-fork-preservation.md", "auditcompact doc"),
)
REGISTRY_BY_REVISION["rev0049"] = REV0049_REGISTRY
NEEDLES_BY_REVISION["rev0049"] = ("publishdryrun", "witnesscompact", "scopejournal", "publishdryrunfold", "publicoutbox", "auditgap", "outboxfold", "auditcompact")

# rev0050 outbox-drain / SAM-canary / compact-join registry.
REV0050_REGISTRY = (
    FoldRegistryEntry("rev0050", "src/i2p_dht_lab/outboxdrain.py", "no-network outbox drain prepare/commit receipts"),
    FoldRegistryEntry("rev0050", "src/i2p_dht_lab/samcanary.py", "SAM-shadow canary before live router-backed send"),
    FoldRegistryEntry("rev0050", "src/i2p_dht_lab/compactjoin.py", "joined compaction preserving negative evidence"),
    FoldRegistryEntry("rev0050", "src/i2p_dht_lab/drainfold.py", "rev0050 drain/canary/compact fold audit"),
    FoldRegistryEntry("rev0050", "tests/test_rev0050_outboxdrain_samcanary_compactjoin.py", "current rev0050 tests"),
    FoldRegistryEntry("rev0050", "docs/524-rev0050-outboxdrain-samcanary-compactjoin.md", "current revision doc"),
    FoldRegistryEntry("rev0050", "docs/525-outbox-drain-commit-receipts.md", "outbox drain doc"),
    FoldRegistryEntry("rev0050", "docs/526-sam-canary-before-live-send.md", "SAM canary doc"),
    FoldRegistryEntry("rev0050", "docs/527-compact-join-negative-evidence.md", "compact join doc"),
    FoldRegistryEntry("rev0050", "docs/528-drainfold-audit-refactor.md", "drainfold audit doc"),
)
REGISTRY_BY_REVISION["rev0050"] = REV0050_REGISTRY
NEEDLES_BY_REVISION["rev0050"] = ("outboxdrain", "samcanary", "compactjoin", "drainfold")

# rev0051 send-valve / effect-ledger fold merge registry.
REV0051_REGISTRY = (
    FoldRegistryEntry("rev0051", "src/i2p_dht_lab/commitbarrier.py", "folded no-network public commit barrier branchlet"),
    FoldRegistryEntry("rev0051", "src/i2p_dht_lab/sendvalve.py", "join commit/drain/canary/compact before future live send"),
    FoldRegistryEntry("rev0051", "src/i2p_dht_lab/effectledger.py", "idempotent public-effect restart memory"),
    FoldRegistryEntry("rev0051", "src/i2p_dht_lab/sendfold.py", "rev0051 sendfold audit"),
    FoldRegistryEntry("rev0051", "tests/test_rev0051_sendvalve_effectledger_foldmerge.py", "current rev0051 tests"),
    FoldRegistryEntry("rev0051", "docs/534-rev0051-sendvalve-effectledger-foldmerge.md", "current revision doc"),
    FoldRegistryEntry("rev0051", "docs/535-send-valve-joined-boundary.md", "send valve doc"),
    FoldRegistryEntry("rev0051", "docs/536-effect-ledger-idempotent-memory.md", "effect ledger doc"),
    FoldRegistryEntry("rev0051", "docs/537-foldmerge-commitbarrier-branchlet.md", "commitbarrier branchlet fold doc"),
    FoldRegistryEntry("rev0051", "docs/538-sendfold-audit-refactor.md", "sendfold audit doc"),
    FoldRegistryEntry("rev0051", "artifacts/branchlets/rev0050_commitbarrier_publicedgefold/publicedgefold.py", "folded rev0050 publicedgefold branchlet"),
)
REGISTRY_BY_REVISION["rev0051"] = REV0051_REGISTRY
NEEDLES_BY_REVISION["rev0051"] = ("commitbarrier", "sendvalve", "effectledger", "sendfold")

# rev0051 ingress-drain / router-canary / red-team registry.
REV0051_REGISTRY = (
    FoldRegistryEntry("rev0051", "src/i2p_dht_lab/routercanary.py", "router canary before public-edge SAM side effects"),
    FoldRegistryEntry("rev0051", "src/i2p_dht_lab/ingressdrain.py", "ingress drain before public-bridge handler work"),
    FoldRegistryEntry("rev0051", "src/i2p_dht_lab/redteamfold.py", "rev0051 redteamfold current audit"),
    FoldRegistryEntry("rev0051", "tests/test_rev0051_ingressdrain_routercanary_redteamfold.py", "current rev0051 tests"),
    FoldRegistryEntry("rev0051", "docs/534-rev0051-ingressdrain-routercanary-redteamfold.md", "current revision doc"),
    FoldRegistryEntry("rev0051", "docs/535-router-canary-public-edge.md", "router canary doc"),
    FoldRegistryEntry("rev0051", "docs/536-ingress-drain-public-bridge.md", "ingress drain doc"),
    FoldRegistryEntry("rev0051", "docs/537-redteamfold-audit-refactor.md", "redteamfold audit doc"),
)
REGISTRY_BY_REVISION["rev0051"] = REV0051_REGISTRY
NEEDLES_BY_REVISION["rev0051"] = ("routercanary", "ingressdrain", "redteamfold")

# rev0052 live-adapter / backpressure / profile-edge fold registry.
REV0052_REGISTRY = (
    FoldRegistryEntry("rev0052", "src/i2p_dht_lab/liveadapter.py", "live adapter no-network seam before live send or handler side effect"),
    FoldRegistryEntry("rev0052", "src/i2p_dht_lab/backpressuremesh.py", "shared inbound/outbound public-edge backpressure mesh"),
    FoldRegistryEntry("rev0052", "src/i2p_dht_lab/profileedge.py", "profile-edge joined boundary binding adapter, pressure, profile budget, and negative scan"),
    FoldRegistryEntry("rev0052", "src/i2p_dht_lab/edgefold.py", "rev0052 edgefold audit"),
    FoldRegistryEntry("rev0052", "tests/test_rev0052_liveadapter_backpressure_profileedge.py", "current liveadapter/backpressure/profileedge tests"),
    FoldRegistryEntry("rev0052", "docs/548-rev0052-liveadapter-backpressure-profileedge.md", "current revision doc"),
    FoldRegistryEntry("rev0052", "docs/549-live-adapter-no-network-boundary.md", "live adapter doc"),
    FoldRegistryEntry("rev0052", "docs/550-backpressure-mesh-shared-edge.md", "backpressure mesh doc"),
    FoldRegistryEntry("rev0052", "docs/551-profile-edge-joined-boundary.md", "profile edge doc"),
    FoldRegistryEntry("rev0052", "docs/552-edgefold-audit-refactor.md", "edgefold audit doc"),
)
REGISTRY_BY_REVISION["rev0052"] = REV0052_REGISTRY
NEEDLES_BY_REVISION["rev0052"] = ("liveadapter", "backpressuremesh", "profileedge", "edgefold")

# rev0053 handler-capsule / side-effect journal / adapter-fuzz fold registry.
REV0053_REGISTRY = (
    FoldRegistryEntry("rev0053", "src/i2p_dht_lab/handlercapsule.py", "handler capsules behind inbound live adapter work"),
    FoldRegistryEntry("rev0053", "src/i2p_dht_lab/sideeffectjournal.py", "append-only local side-effect journal for prepare/commit/abort memory"),
    FoldRegistryEntry("rev0053", "src/i2p_dht_lab/adapterfuzz.py", "adapter/profile-edge mismatch coverage algebra"),
    FoldRegistryEntry("rev0053", "src/i2p_dht_lab/handlerfold.py", "rev0053 handlerfold current audit"),
    FoldRegistryEntry("rev0053", "tests/test_rev0053_handlercapsule_sideeffect_adapterfuzz.py", "current handler capsule / journal / fuzz tests"),
    FoldRegistryEntry("rev0053", "docs/559-rev0053-handlercapsule-sideeffectjournal-adapterfuzz.md", "current revision doc"),
    FoldRegistryEntry("rev0053", "docs/560-handler-capsule-boundary.md", "handler capsule doc"),
    FoldRegistryEntry("rev0053", "docs/561-side-effect-journal-boundary.md", "side-effect journal doc"),
    FoldRegistryEntry("rev0053", "docs/562-adapter-fuzz-coverage.md", "adapter fuzz doc"),
    FoldRegistryEntry("rev0053", "docs/563-handlerfold-audit-refactor.md", "handlerfold audit doc"),
)
REGISTRY_BY_REVISION["rev0053"] = REV0053_REGISTRY
NEEDLES_BY_REVISION["rev0053"] = ("handlercapsule", "sideeffectjournal", "adapterfuzz", "handlerfold")

# rev0054 replay-lab / handler-quench / fuzz-ledger fold registry.
REV0054_REGISTRY = (
    FoldRegistryEntry("rev0054", "src/i2p_dht_lab/handlerreplay.py", "restart replay window for handler and side-effect reports"),
    FoldRegistryEntry("rev0054", "src/i2p_dht_lab/handlerquench.py", "handler near-miss cooldown and metadata pressure"),
    FoldRegistryEntry("rev0054", "src/i2p_dht_lab/fuzzledger.py", "persistent adapter fuzz coverage ledger"),
    FoldRegistryEntry("rev0054", "src/i2p_dht_lab/replayfold.py", "rev0054 replayfold current audit"),
    FoldRegistryEntry("rev0054", "tests/test_rev0054_replay_quench_fuzzledger.py", "current replay/quench/fuzzledger tests"),
    FoldRegistryEntry("rev0054", "docs/579-rev0054-replaylab-handlerquench-fuzzledger.md", "current revision doc"),
    FoldRegistryEntry("rev0054", "docs/570-handler-replay-restart-boundary.md", "handler replay doc"),
    FoldRegistryEntry("rev0054", "docs/571-handler-quench-cooldown.md", "handler quench doc"),
    FoldRegistryEntry("rev0054", "docs/572-fuzz-ledger-persistent-coverage.md", "fuzz ledger doc"),
    FoldRegistryEntry("rev0054", "docs/573-replayfold-audit-refactor.md", "replayfold doc"),
)
REGISTRY_BY_REVISION["rev0054"] = REV0054_REGISTRY
NEEDLES_BY_REVISION["rev0054"] = ("handlerreplay", "handlerquench", "fuzzledger", "replayfold")

# rev0055 restart-chaos / effect-seal / fuzz-shrink fold registry.
REV0055_REGISTRY = (
    FoldRegistryEntry("rev0055", "src/i2p_dht_lab/restartchaos.py", "crash-cut restart chaos lane joining replay/journal/quench/fuzz components"),
    FoldRegistryEntry("rev0055", "src/i2p_dht_lab/effectseal.py", "exact-boundary effect seal after restart and fuzz evidence"),
    FoldRegistryEntry("rev0055", "src/i2p_dht_lab/fuzzshrink.py", "fuzz coverage shrink/compaction without losing required mutation evidence"),
    FoldRegistryEntry("rev0055", "src/i2p_dht_lab/restartfold.py", "rev0055 restartfold current audit"),
    FoldRegistryEntry("rev0055", "tests/test_rev0055_restartchaos_effectseal_fuzzshrink.py", "current restart/effect/fuzz-shrink tests"),
    FoldRegistryEntry("rev0055", "docs/580-rev0055-restartchaos-effectseal-fuzzshrink.md", "current revision doc"),
    FoldRegistryEntry("rev0055", "docs/581-restart-chaos-crash-cut-boundary.md", "restart chaos doc"),
    FoldRegistryEntry("rev0055", "docs/582-effect-seal-joined-boundary.md", "effect seal doc"),
    FoldRegistryEntry("rev0055", "docs/583-fuzz-shrink-coverage-compaction.md", "fuzz shrink doc"),
    FoldRegistryEntry("rev0055", "docs/584-restartfold-audit-refactor.md", "restartfold audit doc"),
)
REGISTRY_BY_REVISION["rev0055"] = REV0055_REGISTRY
NEEDLES_BY_REVISION["rev0055"] = ("restartchaos", "effectseal", "fuzzshrink", "restartfold")

# rev0056 recovery-mesh / safe-cleanup / chaos-budget fold registry.
REV0056_REGISTRY = (
    FoldRegistryEntry("rev0056", "src/i2p_dht_lab/recoverymesh.py", "recovery mesh after effect seal and restart replay"),
    FoldRegistryEntry("rev0056", "src/i2p_dht_lab/safecleanup.py", "signed cleanup tickets preserving hard negatives and accepted seals"),
    FoldRegistryEntry("rev0056", "src/i2p_dht_lab/chaosbudget.py", "post-effect chaos budget and metadata spend pressure"),
    FoldRegistryEntry("rev0056", "src/i2p_dht_lab/recoveryfold.py", "rev0056 recoveryfold current audit"),
    FoldRegistryEntry("rev0056", "tests/test_rev0056_recovery_cleanup_chaosbudget.py", "current recovery/cleanup/chaos-budget tests"),
    FoldRegistryEntry("rev0056", "docs/590-rev0056-recoverymesh-safecleanup-chaosbudget.md", "current revision doc"),
    FoldRegistryEntry("rev0056", "docs/591-recovery-mesh-after-effect-seal.md", "recovery mesh doc"),
    FoldRegistryEntry("rev0056", "docs/592-safe-cleanup-hard-negative-boundary.md", "safe cleanup doc"),
    FoldRegistryEntry("rev0056", "docs/593-chaos-budget-post-effect-pressure.md", "chaos budget doc"),
    FoldRegistryEntry("rev0056", "docs/594-recoveryfold-audit-refactor.md", "recoveryfold audit doc"),
)
REGISTRY_BY_REVISION["rev0056"] = REV0056_REGISTRY
NEEDLES_BY_REVISION["rev0056"] = ("recoverymesh", "safecleanup", "chaosbudget", "recoveryfold")

# rev0056 recovery mesh / safe cleanup / chaos budget fold registry.
REV0056_REGISTRY = (
    FoldRegistryEntry("rev0056", "src/i2p_dht_lab/sealreplay.py", "restart-generation seal replay memory"),
    FoldRegistryEntry("rev0056", "src/i2p_dht_lab/corpuswitness.py", "fuzz-shrink corpus witness receipts"),
    FoldRegistryEntry("rev0056", "src/i2p_dht_lab/recoverymesh.py", "post-effect recovery mesh join"),
    FoldRegistryEntry("rev0056", "src/i2p_dht_lab/safecleanup.py", "safe cleanup preserving hard negatives and accepted seals"),
    FoldRegistryEntry("rev0056", "src/i2p_dht_lab/chaosbudget.py", "bounded post-effect chaos and metadata budget"),
    FoldRegistryEntry("rev0056", "src/i2p_dht_lab/recoveryfold.py", "rev0056 recoveryfold current audit"),
    FoldRegistryEntry("rev0056", "tests/test_rev0056_recovery_cleanup_chaosbudget.py", "current recovery/cleanup/chaos tests"),
    FoldRegistryEntry("rev0056", "docs/590-rev0056-recoverymesh-safecleanup-chaosbudget.md", "current revision doc"),
    FoldRegistryEntry("rev0056", "docs/591-recovery-mesh-after-effect-seal.md", "recovery mesh doc"),
    FoldRegistryEntry("rev0056", "docs/592-safe-cleanup-hard-negative-boundary.md", "safe cleanup doc"),
    FoldRegistryEntry("rev0056", "docs/593-chaos-budget-post-effect-pressure.md", "chaos budget doc"),
    FoldRegistryEntry("rev0056", "docs/594-recoveryfold-audit-refactor.md", "recoveryfold audit doc"),
)
REGISTRY_BY_REVISION["rev0056"] = REV0056_REGISTRY
NEEDLES_BY_REVISION["rev0056"] = ("sealreplay", "corpuswitness", "recoverymesh", "safecleanup", "chaosbudget", "recoveryfold")

# rev0057 dead-letter / retry-quorum / effect-reconcile fold registry.
REV0057_REGISTRY = (
    FoldRegistryEntry("rev0057", "src/i2p_dht_lab/deadletter.py", "signed dead-letter memory for prepared-only or ambiguous effects"),
    FoldRegistryEntry("rev0057", "src/i2p_dht_lab/retryquorum.py", "retry quorum after dead-letter and recovery watch"),
    FoldRegistryEntry("rev0057", "src/i2p_dht_lab/effectreconcile.py", "joined local effect reconciliation boundary"),
    FoldRegistryEntry("rev0057", "src/i2p_dht_lab/reconcilefold.py", "rev0057 reconcilefold current audit"),
    FoldRegistryEntry("rev0057", "tests/test_rev0057_deadletter_retry_reconcile.py", "current dead-letter/retry/reconcile tests"),
    FoldRegistryEntry("rev0057", "docs/600-rev0057-deadletter-retryquorum-effectreconcile.md", "current revision doc"),
    FoldRegistryEntry("rev0057", "docs/601-dead-letter-lane-prepared-only.md", "dead-letter lane doc"),
    FoldRegistryEntry("rev0057", "docs/602-retry-quorum-after-recovery-watch.md", "retry quorum doc"),
    FoldRegistryEntry("rev0057", "docs/603-effect-reconcile-boundary.md", "effect reconcile doc"),
    FoldRegistryEntry("rev0057", "docs/604-reconcilefold-audit-refactor.md", "reconcilefold audit doc"),
)
REGISTRY_BY_REVISION["rev0057"] = REV0057_REGISTRY
NEEDLES_BY_REVISION["rev0057"] = ("deadletter", "retryquorum", "effectreconcile", "reconcilefold")

# rev0058 finality-ledger / retry-escrow / prune-guard fold registry.
REV0058_REGISTRY = (
    FoldRegistryEntry("rev0058", "src/i2p_dht_lab/finalityledger.py", "signed local finality markers after effect reconciliation"),
    FoldRegistryEntry("rev0058", "src/i2p_dht_lab/retryescrow.py", "retry escrow that carries dead-letter memory across attempts"),
    FoldRegistryEntry("rev0058", "src/i2p_dht_lab/pruneguard.py", "prune guard preserving hard negatives and pending retry/dead-letter evidence"),
    FoldRegistryEntry("rev0058", "src/i2p_dht_lab/finalityfold.py", "rev0058 finalityfold current audit"),
    FoldRegistryEntry("rev0058", "tests/test_rev0058_finality_retryescrow_pruneguard.py", "current finality/retry/prune tests"),
    FoldRegistryEntry("rev0058", "docs/610-rev0058-finalityledger-retryescrow-pruneguard.md", "current revision doc"),
    FoldRegistryEntry("rev0058", "docs/611-finality-ledger-after-reconcile.md", "finality ledger doc"),
    FoldRegistryEntry("rev0058", "docs/612-retry-escrow-deadletter-carry.md", "retry escrow doc"),
    FoldRegistryEntry("rev0058", "docs/613-prune-guard-terminal-pending.md", "prune guard doc"),
    FoldRegistryEntry("rev0058", "docs/614-finalityfold-audit-refactor.md", "finalityfold audit doc"),
)
REGISTRY_BY_REVISION["rev0058"] = REV0058_REGISTRY
NEEDLES_BY_REVISION["rev0058"] = ("finalityledger", "retryescrow", "pruneguard", "finalityfold")

# rev0059 settlement-store / tomb-repair / canary-join registry, with terminal receipt branchlet visible.
REV0059_REGISTRY = (
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/settlementstore.py", "joined store between finality and folded settlement branchlet"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/tombrepairjoin.py", "tombstone repair and prune-pressure join after settlement store"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/canaryjoin.py", "no-network canary join after settlement/tomb repair"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/settlementstorefold.py", "rev0059 fold audit preserving both rev0058 predecessors"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/terminalreceipt.py", "terminal receipt branchlet after finality ledger"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/idempotencyrepair.py", "idempotency repair branchlet after terminal receipt"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/compactionaudit.py", "compaction audit branchlet preserving hard negatives"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/terminalfold.py", "terminal receipt branchlet fold audit"),
    FoldRegistryEntry("rev0059", "tests/test_rev0059_settlementstore_tombmesh_canaryjoin.py", "current settlement/tomb/canary tests"),
    FoldRegistryEntry("rev0059", "tests/test_rev0059_settlementstore_terminalreceipt.py", "settlement-store and terminal receipt tests"),
    FoldRegistryEntry("rev0059", "docs/620-rev0059-settlementstore-tombmesh-canaryjoin.md", "current revision doc"),
    FoldRegistryEntry("rev0059", "docs/621-settlement-store-branch-join.md", "settlementstore doc"),
    FoldRegistryEntry("rev0059", "docs/622-tomb-repair-join-after-prune.md", "tombrepairjoin doc"),
    FoldRegistryEntry("rev0059", "docs/623-canary-join-after-settlement.md", "canaryjoin doc"),
    FoldRegistryEntry("rev0059", "docs/624-settlementstorefold-audit-refactor.md", "settlementstorefold doc"),
)
REGISTRY_BY_REVISION["rev0059"] = REV0059_REGISTRY
NEEDLES_BY_REVISION["rev0059"] = ("settlementstore", "tombrepairjoin", "canaryjoin", "settlementstorefold", "terminalreceipt", "idempotencyrepair", "compactionaudit", "terminalfold")

# rev0059 final settlement-store/terminal-receipt fold registry override.
REV0059_REGISTRY = (
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/attestationpack.py", "typed signed evidence packs for component report digests"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/settlementlane.py", "settlement lane preserving retry/dead-letter holds after finality"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/tombstonerepair.py", "tombstone repair after settlement with resurrection-pressure quarantine"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/settlementstore.py", "joined settlement store across finality, settlement, prune, attestation, tombstone, and retry escrow"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/terminalreceipt.py", "terminal receipt after finality and prune agree"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/settlementfold.py", "rev0059 settlementfold current audit"),
    FoldRegistryEntry("rev0059", "tests/test_rev0059_settlement_attestation_tombrepair.py", "current settlement/attestation/tombstone-repair tests"),
    FoldRegistryEntry("rev0059", "tests/test_rev0059_settlementstore_terminalreceipt.py", "current settlementstore/terminalreceipt tests"),
    FoldRegistryEntry("rev0059", "docs/620-rev0059-settlementstore-tombmesh-canaryjoin.md", "current revision doc"),
    FoldRegistryEntry("rev0059", "docs/621-settlement-lane-after-finality.md", "settlement lane doc"),
    FoldRegistryEntry("rev0059", "docs/622-attestation-pack-typed-evidence.md", "attestation pack doc"),
    FoldRegistryEntry("rev0059", "docs/623-tombstone-repair-after-settlement.md", "tombstone repair doc"),
    FoldRegistryEntry("rev0059", "docs/624-settlementfold-audit-refactor.md", "settlementfold audit doc"),
    FoldRegistryEntry("rev0059", "docs/625-settlement-store-branch-join.md", "settlement store doc"),
    FoldRegistryEntry("rev0059", "docs/626-terminal-receipt-after-finality.md", "terminal receipt doc"),
)
REGISTRY_BY_REVISION["rev0059"] = REV0059_REGISTRY
NEEDLES_BY_REVISION["rev0059"] = ("attestationpack", "settlementlane", "tombstonerepair", "settlementstore", "terminalreceipt", "settlementfold")

# rev0059 terminal receipt / idempotency repair / compaction audit final override.
REV0059_REGISTRY = (
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/terminalreceipt.py", "terminal receipt after finality and prune agree"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/idempotencyrepair.py", "idempotency repair preserving retry/dead-letter lineage"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/compactionaudit.py", "compaction audit preserving terminal and hard-negative evidence"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/settlementstore.py", "folded branch join for settlement store pressure"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/terminalfold.py", "rev0059 terminalfold current audit"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/settlementfold.py", "folded settlement branch audit"),
    FoldRegistryEntry("rev0059", "tests/test_rev0059_terminalreceipt_idemrepair_compactionaudit.py", "current terminal receipt / idempotency repair / compaction audit tests"),
    FoldRegistryEntry("rev0059", "tests/test_rev0059_settlement_attestation_tombrepair.py", "folded settlement/attestation/tombstone repair tests"),
    FoldRegistryEntry("rev0059", "docs/620-rev0059-terminalreceipt-idemrepair-compactionaudit.md", "current revision doc"),
    FoldRegistryEntry("rev0059", "docs/621-terminal-receipt-after-finality.md", "terminal receipt doc"),
    FoldRegistryEntry("rev0059", "docs/622-idempotency-repair-lineage.md", "idempotency repair doc"),
    FoldRegistryEntry("rev0059", "docs/623-compaction-audit-hard-negatives.md", "compaction audit doc"),
    FoldRegistryEntry("rev0059", "docs/624-terminalfold-audit-refactor.md", "terminalfold audit doc"),
)
REGISTRY_BY_REVISION["rev0059"] = REV0059_REGISTRY
NEEDLES_BY_REVISION["rev0059"] = ("terminalreceipt", "idempotencyrepair", "compactionaudit", "settlementstore", "terminalfold")

# rev0059 settlementstore/tombmesh/canary final override after folded branchlet reconciliation.
REGISTRY_BY_REVISION["rev0059"] = (
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/settlementstore.py", "joined store between finality and folded settlement branchlet"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/tombrepairjoin.py", "tombstone repair and prune-pressure join after settlement store"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/canaryjoin.py", "no-network canary join after settlement/tomb repair"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/settlementstorefold.py", "rev0059 fold audit preserving both rev0058 predecessors"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/settlementlane.py", "folded rev0058 settlement branchlet lane"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/attestationpack.py", "folded rev0058 attestation pack branchlet"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/tombstonerepair.py", "folded rev0058 tombstone repair branchlet"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/settlementfold.py", "folded rev0058 settlementfold branchlet audit"),
    FoldRegistryEntry("rev0059", "tests/test_rev0059_settlementstore_tombmesh_canaryjoin.py", "current settlement/tomb/canary tests"),
    FoldRegistryEntry("rev0059", "tests/test_rev0058_settlement_attestation_tombrepair.py", "folded branchlet tests"),
    FoldRegistryEntry("rev0059", "docs/620-rev0059-settlementstore-tombmesh-canaryjoin.md", "current revision doc"),
    FoldRegistryEntry("rev0059", "docs/621-settlement-store-branch-join.md", "settlementstore doc"),
    FoldRegistryEntry("rev0059", "docs/622-tomb-repair-join-after-prune.md", "tombrepairjoin doc"),
    FoldRegistryEntry("rev0059", "docs/623-canary-join-after-settlement.md", "canaryjoin doc"),
    FoldRegistryEntry("rev0059", "docs/624-settlementstorefold-audit-refactor.md", "settlementstorefold doc"),
)
NEEDLES_BY_REVISION["rev0059"] = ("settlementstore", "tombrepairjoin", "canaryjoin", "settlementstorefold", "settlementlane", "attestationpack", "tombstonerepair")


# rev0059 unified settlement-store / terminal-receipt fold-map override.
REV0059_CURRENT = (
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/settlementstore.py", "settlement_store_branch_join", True),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/tombrepairjoin.py", "tomb_repair_join_after_prune", True),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/canaryjoin.py", "canary_join_after_settlement", True),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/settlementstorefold.py", "settlementstorefold_current_audit", True),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/settlementlane.py", "folded_settlement_lane", True),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/attestationpack.py", "folded_attestation_pack", True),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/tombstonerepair.py", "folded_tombstone_repair", True),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/settlementfold.py", "settlementfold_branch_audit", True),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/terminalreceipt.py", "terminal_receipt_after_finality", True),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/idempotencyrepair.py", "idempotency_repair_lineage", True),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/compactionaudit.py", "compaction_audit_hard_negative_boundary", True),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/terminalfold.py", "terminalfold_current_audit", True),
    FoldRegistryEntry("rev0059", "tests/test_rev0059_settlementstore_tombmesh_canaryjoin.py", "settlementstore_tomb_canary_tests", True),
    FoldRegistryEntry("rev0059", "tests/test_rev0059_settlementstore_terminalreceipt.py", "settlementstore_terminal_receipt_tests", True),
    FoldRegistryEntry("rev0059", "tests/test_rev0059_terminalreceipt_idemrepair_compactionaudit.py", "terminal_current_tests", True),
    FoldRegistryEntry("rev0059", "tests/test_rev0059_settlement_attestation_tombrepair.py", "folded_settlement_tests", True),
    FoldRegistryEntry("rev0059", "docs/620-rev0059-settlementstore-tombmesh-canaryjoin.md", "settlementstore_revision_doc", True),
    FoldRegistryEntry("rev0059", "docs/620-rev0059-terminalreceipt-idemrepair-compactionaudit.md", "terminal_revision_doc", True),
    FoldRegistryEntry("rev0059", "docs/621-settlement-store-branch-join.md", "settlementstore_doc", True),
    FoldRegistryEntry("rev0059", "docs/621-terminal-receipt-after-finality.md", "terminalreceipt_doc", True),
    FoldRegistryEntry("rev0059", "docs/622-tomb-repair-join-after-prune.md", "tombrepairjoin_doc", True),
    FoldRegistryEntry("rev0059", "docs/622-idempotency-repair-lineage.md", "idempotencyrepair_doc", True),
    FoldRegistryEntry("rev0059", "docs/623-canary-join-after-settlement.md", "canaryjoin_doc", True),
    FoldRegistryEntry("rev0059", "docs/623-compaction-audit-hard-negatives.md", "compactionaudit_doc", True),
    FoldRegistryEntry("rev0059", "docs/624-settlementstorefold-audit-refactor.md", "settlementstorefold_doc", True),
    FoldRegistryEntry("rev0059", "docs/624-settlementfold-audit-refactor.md", "settlementfold_doc", True),
    FoldRegistryEntry("rev0059", "docs/624-terminalfold-audit-refactor.md", "terminalfold_doc", True),
)
REGISTRY_BY_REVISION["rev0059"] = REV0059_CURRENT
NEEDLES_BY_REVISION["rev0059"] = ("settlementstore", "tombrepairjoin", "canaryjoin", "settlementstorefold", "settlementlane", "attestationpack", "tombstonerepair", "settlementfold", "terminalreceipt", "idempotencyrepair", "compactionaudit", "terminalfold")

# rev0059 unified settlement-store / terminal-receipt active registry override.
REV0059_REGISTRY = (
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/settlementstore.py", "settlement store branch join"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/tombrepairjoin.py", "tombstone repair / prune join"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/canaryjoin.py", "SAM/router canary join after settlement"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/settlementstorefold.py", "rev0059 settlementstorefold current audit"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/settlementlane.py", "settlement lane after finality"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/attestationpack.py", "typed attestation pack evidence"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/tombstonerepair.py", "tombstone repair after settlement"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/settlementfold.py", "rev0059 settlementfold audit"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/terminalreceipt.py", "terminal receipt after finality/prune"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/idempotencyrepair.py", "idempotency repair carrying retry/dead-letter lineage"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/compactionaudit.py", "compaction audit preserving hard negatives"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/terminalfold.py", "rev0059 terminalfold audit"),
    FoldRegistryEntry("rev0059", "tests/test_rev0059_settlementstore_tombmesh_canaryjoin.py", "settlementstore/tomb/canary tests"),
    FoldRegistryEntry("rev0059", "tests/test_rev0059_settlement_attestation_tombrepair.py", "settlement/attestation/tombstone tests"),
    FoldRegistryEntry("rev0059", "tests/test_rev0059_terminalreceipt_idemrepair_compactionaudit.py", "terminal/idempotency/compaction tests"),
    FoldRegistryEntry("rev0059", "docs/620-rev0059-settlementstore-tombmesh-canaryjoin.md", "current revision doc"),
    FoldRegistryEntry("rev0059", "docs/621-settlement-lane-after-finality.md", "settlement lane doc"),
    FoldRegistryEntry("rev0059", "docs/621-settlement-store-branch-join.md", "settlement store doc"),
    FoldRegistryEntry("rev0059", "docs/621-terminal-receipt-after-finality.md", "terminal receipt doc"),
    FoldRegistryEntry("rev0059", "docs/622-attestation-pack-typed-evidence.md", "attestation pack doc"),
    FoldRegistryEntry("rev0059", "docs/622-tomb-repair-join-after-prune.md", "tomb repair join doc"),
    FoldRegistryEntry("rev0059", "docs/622-idempotency-repair-lineage.md", "idempotency repair doc"),
    FoldRegistryEntry("rev0059", "docs/623-tombstone-repair-after-settlement.md", "tombstone repair doc"),
    FoldRegistryEntry("rev0059", "docs/623-canary-join-after-settlement.md", "canary join doc"),
    FoldRegistryEntry("rev0059", "docs/623-compaction-audit-hard-negatives.md", "compaction audit doc"),
    FoldRegistryEntry("rev0059", "docs/624-settlementfold-audit-refactor.md", "settlementfold doc"),
    FoldRegistryEntry("rev0059", "docs/624-settlementstorefold-audit-refactor.md", "settlementstorefold doc"),
    FoldRegistryEntry("rev0059", "docs/624-terminalfold-audit-refactor.md", "terminalfold doc"),
)
REGISTRY_BY_REVISION["rev0059"] = REV0059_REGISTRY
NEEDLES_BY_REVISION["rev0059"] = ("settlementstore", "tombrepairjoin", "canaryjoin", "settlementstorefold", "settlementlane", "attestationpack", "tombstonerepair", "settlementfold", "terminalreceipt", "idempotencyrepair", "compactionaudit", "terminalfold")


# rev0059 merged settlement / terminal / canary final registry override.
REV0059_REGISTRY = (
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/settlementlane.py", "settlement lane after finality"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/attestationpack.py", "typed attestation pack evidence"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/tombstonerepair.py", "tombstone repair after settlement"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/settlementstore.py", "settlement store branch join"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/tombrepairjoin.py", "tomb repair prune join"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/canaryjoin.py", "canary join after settlement"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/terminalreceipt.py", "terminal receipt after finality"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/idempotencyrepair.py", "idempotency repair preserving lineage"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/compactionaudit.py", "compaction audit preserving hard negatives"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/settlementfold.py", "settlementfold audit"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/settlementstorefold.py", "settlementstorefold audit"),
    FoldRegistryEntry("rev0059", "src/i2p_dht_lab/terminalfold.py", "terminalfold audit"),
    FoldRegistryEntry("rev0059", "tests/test_rev0059_settlement_attestation_tombrepair.py", "settlement branchlet tests"),
    FoldRegistryEntry("rev0059", "tests/test_rev0059_settlementstore_tombmesh_canaryjoin.py", "settlementstore tomb/canary tests"),
    FoldRegistryEntry("rev0059", "tests/test_rev0059_settlementstore_terminalreceipt.py", "settlementstore terminalreceipt tests"),
    FoldRegistryEntry("rev0059", "tests/test_rev0059_terminalreceipt_idemrepair_compactionaudit.py", "terminal idempotency compaction tests"),
    FoldRegistryEntry("rev0059", "docs/620-rev0059-settlementstore-tombmesh-canaryjoin.md", "current settlementstore revision doc"),
    FoldRegistryEntry("rev0059", "docs/620-rev0059-terminalreceipt-idemrepair-compactionaudit.md", "terminal branch doc"),
    FoldRegistryEntry("rev0059", "docs/621-settlement-lane-after-finality.md", "settlementlane doc"),
    FoldRegistryEntry("rev0059", "docs/621-settlement-store-branch-join.md", "settlementstore doc"),
    FoldRegistryEntry("rev0059", "docs/621-terminal-receipt-after-finality.md", "terminalreceipt doc"),
    FoldRegistryEntry("rev0059", "docs/622-attestation-pack-typed-evidence.md", "attestationpack doc"),
    FoldRegistryEntry("rev0059", "docs/622-tomb-repair-join-after-prune.md", "tombrepairjoin doc"),
    FoldRegistryEntry("rev0059", "docs/622-idempotency-repair-lineage.md", "idempotencyrepair doc"),
    FoldRegistryEntry("rev0059", "docs/623-tombstone-repair-after-settlement.md", "tombstonerepair doc"),
    FoldRegistryEntry("rev0059", "docs/623-canary-join-after-settlement.md", "canaryjoin doc"),
    FoldRegistryEntry("rev0059", "docs/623-compaction-audit-hard-negatives.md", "compactionaudit doc"),
    FoldRegistryEntry("rev0059", "docs/624-settlementfold-audit-refactor.md", "settlementfold doc"),
    FoldRegistryEntry("rev0059", "docs/624-settlementstorefold-audit-refactor.md", "settlementstorefold doc"),
    FoldRegistryEntry("rev0059", "docs/624-terminalfold-audit-refactor.md", "terminalfold doc"),
)
REGISTRY_BY_REVISION["rev0059"] = REV0059_REGISTRY
NEEDLES_BY_REVISION["rev0059"] = ("settlementlane", "attestationpack", "tombstonerepair", "settlementstore", "tombrepairjoin", "canaryjoin", "terminalreceipt", "idempotencyrepair", "compactionaudit", "settlementfold", "settlementstorefold", "terminalfold")

# rev0060 live-send / delivery-witness / send-fence active registry.
REV0060_REGISTRY = (
    FoldRegistryEntry("rev0060", "src/i2p_dht_lab/livesendgate.py", "live-send gate before future network write"),
    FoldRegistryEntry("rev0060", "src/i2p_dht_lab/deliverywitness.py", "delivery witness receipts after no-network live-send gate"),
    FoldRegistryEntry("rev0060", "src/i2p_dht_lab/sendfence.py", "send fence restart memory after delivery witness"),
    FoldRegistryEntry("rev0060", "src/i2p_dht_lab/fenceaudit.py", "rev0060 fenceaudit current audit"),
    FoldRegistryEntry("rev0060", "tests/test_rev0060_livesend_delivery_fence.py", "current live-send/delivery/fence tests"),
    FoldRegistryEntry("rev0060", "docs/637-rev0060-livesendgate-deliverywitness-fenceaudit.md", "current revision doc"),
    FoldRegistryEntry("rev0060", "docs/638-live-send-gate-before-network-write.md", "live-send gate doc"),
    FoldRegistryEntry("rev0060", "docs/639-delivery-witness-after-send.md", "delivery witness doc"),
    FoldRegistryEntry("rev0060", "docs/640-send-fence-restart-memory.md", "send fence doc"),
    FoldRegistryEntry("rev0060", "docs/641-fenceaudit-audit-refactor.md", "fenceaudit doc"),
)
REGISTRY_BY_REVISION["rev0060"] = REV0060_REGISTRY
NEEDLES_BY_REVISION["rev0060"] = ("livesendgate", "deliverywitness", "sendfence", "fenceaudit")

# rev0061 delivery settlement / ack archive / ack prune join registry.
REV0061_REGISTRY = (
    FoldRegistryEntry("rev0061", "src/i2p_dht_lab/deliverysettlement.py", "delivery settlement after live-send/delivery/fence agree"),
    FoldRegistryEntry("rev0061", "src/i2p_dht_lab/ackarchive.py", "ack archive restart memory for settled sends"),
    FoldRegistryEntry("rev0061", "src/i2p_dht_lab/ackprunejoin.py", "ack prune join after settlement and archive"),
    FoldRegistryEntry("rev0061", "src/i2p_dht_lab/ackfold.py", "rev0061 ackfold current audit"),
    FoldRegistryEntry("rev0061", "tests/test_rev0061_deliverysettlement_ackarchive_prunejoin.py", "current settlement/archive/prune tests"),
    FoldRegistryEntry("rev0061", "docs/647-rev0061-deliverysettlement-ackarchive-prunejoin.md", "current revision doc"),
    FoldRegistryEntry("rev0061", "docs/648-delivery-settlement-after-fence.md", "delivery settlement doc"),
    FoldRegistryEntry("rev0061", "docs/649-ack-archive-restart-memory.md", "ack archive doc"),
    FoldRegistryEntry("rev0061", "docs/650-ack-prune-join-boundary.md", "ack prune join doc"),
    FoldRegistryEntry("rev0061", "docs/651-ackfold-audit-refactor.md", "ackfold doc"),
)
REGISTRY_BY_REVISION["rev0061"] = REV0061_REGISTRY
NEEDLES_BY_REVISION["rev0061"] = ("deliverysettlement", "ackarchive", "ackprunejoin", "ackfold")

# rev0062 ACK/repair live-egress retry fence registry.
REV0062_REGISTRY = (
    FoldRegistryEntry("rev0062", "src/i2p_dht_lab/deliveryrepair.py", "folded delivery-repair branchlet"),
    FoldRegistryEntry("rev0062", "src/i2p_dht_lab/rollbackprobe.py", "rollback probe before retry/withdraw"),
    FoldRegistryEntry("rev0062", "src/i2p_dht_lab/liveegress.py", "live egress retry/withdraw readiness"),
    FoldRegistryEntry("rev0062", "src/i2p_dht_lab/ackrepairjoin.py", "ACK terminal path vs repair path join"),
    FoldRegistryEntry("rev0062", "src/i2p_dht_lab/retryfence.py", "retry fence restart memory"),
    FoldRegistryEntry("rev0062", "src/i2p_dht_lab/repairpruneguard.py", "repair prune guard"),
    FoldRegistryEntry("rev0062", "src/i2p_dht_lab/egressrepairfold.py", "rev0062 egressrepairfold audit"),
    FoldRegistryEntry("rev0062", "tests/test_rev0062_ackrepair_liveegress_retryfence.py", "current ACK/repair live-egress retry-fence tests"),
    FoldRegistryEntry("rev0062", "docs/657-rev0062-ackrepair-liveegress-retryfence.md", "current revision doc"),
    FoldRegistryEntry("rev0062", "docs/658-delivery-repair-live-egress-branchfold.md", "delivery repair branchfold doc"),
    FoldRegistryEntry("rev0062", "docs/659-ack-repair-join-boundary.md", "ackrepairjoin doc"),
    FoldRegistryEntry("rev0062", "docs/660-retry-fence-restart-memory.md", "retryfence doc"),
    FoldRegistryEntry("rev0062", "docs/661-repair-prune-guard.md", "repairpruneguard doc"),
    FoldRegistryEntry("rev0062", "docs/662-egressrepairfold-audit-refactor.md", "egressrepairfold doc"),
)
REGISTRY_BY_REVISION["rev0062"] = REV0062_REGISTRY
NEEDLES_BY_REVISION["rev0062"] = ("deliveryrepair", "rollbackprobe", "liveegress", "ackrepairjoin", "retryfence", "repairpruneguard", "egressrepairfold")

# rev0063 late ACK / retry settlement / egress journal registry.
REV0063_REGISTRY = (
    FoldRegistryEntry("rev0063", "src/i2p_dht_lab/lateack.py", "late ACK after retry fence evidence"),
    FoldRegistryEntry("rev0063", "src/i2p_dht_lab/retrysettlement.py", "retry and withdraw settlement after retry fence"),
    FoldRegistryEntry("rev0063", "src/i2p_dht_lab/withdrawrepair.py", "withdraw repair publication memory"),
    FoldRegistryEntry("rev0063", "src/i2p_dht_lab/egressjournal.py", "egress journal compaction preserving contradictions"),
    FoldRegistryEntry("rev0063", "src/i2p_dht_lab/lateackfold.py", "rev0063 lateackfold audit"),
    FoldRegistryEntry("rev0063", "tests/test_rev0063_lateack_retrysettle_egressjournal.py", "current late ACK / retry settlement tests"),
    FoldRegistryEntry("rev0063", "docs/668-rev0063-lateack-retrysettle-egressjournal.md", "current revision doc"),
    FoldRegistryEntry("rev0063", "docs/669-late-ack-after-retry-fence.md", "late ACK doc"),
    FoldRegistryEntry("rev0063", "docs/670-retry-settlement-and-withdraw-repair.md", "retry settlement and withdraw repair doc"),
    FoldRegistryEntry("rev0063", "docs/671-egress-journal-compaction.md", "egress journal doc"),
    FoldRegistryEntry("rev0063", "docs/672-lateackfold-audit-refactor.md", "lateackfold doc"),
)
REGISTRY_BY_REVISION["rev0063"] = REV0063_REGISTRY
NEEDLES_BY_REVISION["rev0063"] = ("lateack", "retrysettlement", "withdrawrepair", "egressjournal", "lateackfold")

# rev0064 retry publication / idempotency mesh / delivery repair registry.
REV0064_REGISTRY = (
    FoldRegistryEntry("rev0064", "src/i2p_dht_lab/retrypublish.py", "retry-publication staging after retry/withdraw settlement"),
    FoldRegistryEntry("rev0064", "src/i2p_dht_lab/idempotencymesh.py", "idempotency mesh joining original/retry/contradiction lineage"),
    FoldRegistryEntry("rev0064", "src/i2p_dht_lab/deliveryrepairmesh.py", "remote witness pressure for duplicate delivery repair"),
    FoldRegistryEntry("rev0064", "src/i2p_dht_lab/retrypublishfold.py", "rev0064 retry publish fold audit"),
    FoldRegistryEntry("rev0064", "tests/test_rev0064_retrypublish_idempotencymesh_deliveryrepair.py", "current retry publish / idempotency mesh tests"),
    FoldRegistryEntry("rev0064", "docs/678-rev0064-retrypublish-idempotencymesh-deliveryrepair.md", "current revision doc"),
    FoldRegistryEntry("rev0064", "docs/679-retry-publication-outbox.md", "retry publication outbox doc"),
    FoldRegistryEntry("rev0064", "docs/680-idempotency-mesh-lineage.md", "idempotency mesh doc"),
    FoldRegistryEntry("rev0064", "docs/681-delivery-repair-remote-witness.md", "delivery repair remote witness doc"),
    FoldRegistryEntry("rev0064", "docs/682-retrypublishfold-audit-refactor.md", "retrypublishfold doc"),
)
REGISTRY_BY_REVISION["rev0064"] = REV0064_REGISTRY
NEEDLES_BY_REVISION["rev0064"] = ("retrypublish", "idempotencymesh", "deliveryrepairmesh", "retrypublishfold")

# rev0065 remote witness / repair outbox / conflict cooldown registry.
REV0065_REGISTRY = (
    FoldRegistryEntry("rev0065", "src/i2p_dht_lab/remotewitnessledger.py", "remote witness ledger rounds"),
    FoldRegistryEntry("rev0065", "src/i2p_dht_lab/repairoutbox.py", "repair outbox after duplicate conflict"),
    FoldRegistryEntry("rev0065", "src/i2p_dht_lab/conflictcooldown.py", "conflict cooldown duplicate pressure"),
    FoldRegistryEntry("rev0065", "src/i2p_dht_lab/remoterepairfold.py", "rev0065 remote repair fold audit"),
    FoldRegistryEntry("rev0065", "tests/test_rev0065_remotewitness_repairoutbox_conflictcooldown.py", "current remote witness / repair outbox tests"),
    FoldRegistryEntry("rev0065", "docs/688-rev0065-remotewitness-repairoutbox-conflictcooldown.md", "current revision doc"),
    FoldRegistryEntry("rev0065", "docs/689-remote-witness-ledger-rounds.md", "remote witness ledger doc"),
    FoldRegistryEntry("rev0065", "docs/690-repair-outbox-after-duplicate-conflict.md", "repair outbox doc"),
    FoldRegistryEntry("rev0065", "docs/691-conflict-cooldown-duplicate-pressure.md", "conflict cooldown doc"),
    FoldRegistryEntry("rev0065", "docs/692-remoterepairfold-audit-refactor.md", "remoterepairfold doc"),
)
REGISTRY_BY_REVISION["rev0065"] = REV0065_REGISTRY
NEEDLES_BY_REVISION["rev0065"] = ("remotewitnessledger", "repairoutbox", "conflictcooldown", "remoterepairfold")

# rev0066 repair publish / ACK ledger / duplicate closure registry.
REV0066_REGISTRY = (
    FoldRegistryEntry("rev0066", "src/i2p_dht_lab/repairpublishgate.py", "repair publication gate after repair outbox/cooldown"),
    FoldRegistryEntry("rev0066", "src/i2p_dht_lab/repairackledger.py", "repair ACK ledger after repair publication readiness"),
    FoldRegistryEntry("rev0066", "src/i2p_dht_lab/duplicateclosure.py", "duplicate closure finality after repair ACK"),
    FoldRegistryEntry("rev0066", "src/i2p_dht_lab/repairpublishfold.py", "rev0066 repair publish fold audit"),
    FoldRegistryEntry("rev0066", "tests/test_rev0066_repairpublish_ackclosure.py", "current repair publish / ACK / closure tests"),
    FoldRegistryEntry("rev0066", "docs/698-rev0066-repairpublish-ackclosure-duplicatefinality.md", "current revision doc"),
    FoldRegistryEntry("rev0066", "docs/699-repair-publish-gate-after-cooldown.md", "repair publish gate doc"),
    FoldRegistryEntry("rev0066", "docs/700-repair-ack-ledger.md", "repair ACK ledger doc"),
    FoldRegistryEntry("rev0066", "docs/701-duplicate-closure-finality.md", "duplicate closure doc"),
    FoldRegistryEntry("rev0066", "docs/702-repairpublishfold-audit-refactor.md", "repairpublishfold doc"),
)
REGISTRY_BY_REVISION["rev0066"] = REV0066_REGISTRY
NEEDLES_BY_REVISION["rev0066"] = ("repairpublishgate", "repairackledger", "duplicateclosure", "repairpublishfold")

# rev0067 repair settlement / closure archive / repair prune registry.
REV0067_REGISTRY = (
    FoldRegistryEntry("rev0067", "src/i2p_dht_lab/repairsettlement.py", "repair settlement after duplicate closure"),
    FoldRegistryEntry("rev0067", "src/i2p_dht_lab/closurearchive.py", "closure archive restart memory"),
    FoldRegistryEntry("rev0067", "src/i2p_dht_lab/repairprune.py", "repair prune protected memory"),
    FoldRegistryEntry("rev0067", "src/i2p_dht_lab/repairsettlementfold.py", "rev0067 repair settlement fold audit"),
    FoldRegistryEntry("rev0067", "tests/test_rev0067_repairsettlement_archive_prune.py", "current repair settlement / archive / prune tests"),
    FoldRegistryEntry("rev0067", "docs/708-rev0067-repairsettlement-closurearchive-repairprune.md", "current revision doc"),
    FoldRegistryEntry("rev0067", "docs/709-repair-settlement-after-duplicate-closure.md", "repair settlement doc"),
    FoldRegistryEntry("rev0067", "docs/710-closure-archive-restart-memory.md", "closure archive doc"),
    FoldRegistryEntry("rev0067", "docs/711-repair-prune-protected-memory.md", "repair prune doc"),
    FoldRegistryEntry("rev0067", "docs/712-repairsettlementfold-audit-refactor.md", "repairsettlementfold doc"),
)
REGISTRY_BY_REVISION["rev0067"] = REV0067_REGISTRY
NEEDLES_BY_REVISION["rev0067"] = ("repairsettlement", "closurearchive", "repairprune", "repairsettlementfold")

# rev0068 archive journal / prune replay / closure audit registry.
REV0068_REGISTRY = (
    FoldRegistryEntry("rev0068", "src/i2p_dht_lab/archivejournal.py", "archive journal after repair prune"),
    FoldRegistryEntry("rev0068", "src/i2p_dht_lab/prunereplay.py", "prune replay resistance across restart generations"),
    FoldRegistryEntry("rev0068", "src/i2p_dht_lab/closureaudit.py", "closure audit joining settlement/archive/prune/journal/replay"),
    FoldRegistryEntry("rev0068", "src/i2p_dht_lab/archivejournalfold.py", "rev0068 archive journal fold audit"),
    FoldRegistryEntry("rev0068", "tests/test_rev0068_archivejournal_prunereplay_closureaudit.py", "current archive journal / prune replay / closure audit tests"),
    FoldRegistryEntry("rev0068", "docs/718-rev0068-archivejournal-prunereplay-closureaudit.md", "current revision doc"),
    FoldRegistryEntry("rev0068", "docs/719-archive-journal-after-prune.md", "archive journal doc"),
    FoldRegistryEntry("rev0068", "docs/720-prune-replay-resistance.md", "prune replay doc"),
    FoldRegistryEntry("rev0068", "docs/721-closure-audit-restart-boundary.md", "closure audit doc"),
    FoldRegistryEntry("rev0068", "docs/722-archivejournalfold-audit-refactor.md", "archivejournalfold doc"),
)
REGISTRY_BY_REVISION["rev0068"] = REV0068_REGISTRY
NEEDLES_BY_REVISION["rev0068"] = ("archivejournal", "prunereplay", "closureaudit", "archivejournalfold")

# rev0069 closure seal / retention proof / audit export registry.
REV0069_REGISTRY = (
    FoldRegistryEntry("rev0069", "src/i2p_dht_lab/closureseal.py", "closure seal after closure audit"),
    FoldRegistryEntry("rev0069", "src/i2p_dht_lab/retentionproof.py", "retention proof preserving required evidence classes"),
    FoldRegistryEntry("rev0069", "src/i2p_dht_lab/auditexport.py", "redacted audit export boundary"),
    FoldRegistryEntry("rev0069", "src/i2p_dht_lab/closuresealfold.py", "rev0069 closure seal fold audit"),
    FoldRegistryEntry("rev0069", "tests/test_rev0069_closureseal_retention_export.py", "current closure seal / retention / export tests"),
    FoldRegistryEntry("rev0069", "docs/728-rev0069-closureseal-retentionproof-exportaudit.md", "current revision doc"),
    FoldRegistryEntry("rev0069", "docs/729-closure-seal-after-audit.md", "closure seal doc"),
    FoldRegistryEntry("rev0069", "docs/730-retention-proof-hard-negative-carry.md", "retention proof doc"),
    FoldRegistryEntry("rev0069", "docs/731-audit-export-redacted-boundary.md", "audit export doc"),
    FoldRegistryEntry("rev0069", "docs/732-closuresealfold-audit-refactor.md", "closuresealfold doc"),
)
REGISTRY_BY_REVISION["rev0069"] = REV0069_REGISTRY
NEEDLES_BY_REVISION["rev0069"] = ("closureseal", "retentionproof", "auditexport", "closuresealfold")

# rev0070 export receipt / retention GC / closure handoff registry.
REV0070_REGISTRY = (
    FoldRegistryEntry("rev0070", "src/i2p_dht_lab/exportreceipt.py", "export receipt restart memory after redacted audit export"),
    FoldRegistryEntry("rev0070", "src/i2p_dht_lab/retentiongc.py", "retention GC after accepted export receipt"),
    FoldRegistryEntry("rev0070", "src/i2p_dht_lab/closurehandoff.py", "redacted closure handoff after receipt and GC"),
    FoldRegistryEntry("rev0070", "src/i2p_dht_lab/exporthandofffold.py", "rev0070 export handoff fold audit"),
    FoldRegistryEntry("rev0070", "tests/test_rev0070_exportreceipt_retentiongc_handoff.py", "current export receipt / retention GC / handoff tests"),
    FoldRegistryEntry("rev0070", "docs/738-rev0070-exportreceipt-retentiongc-closurehandoff.md", "current revision doc"),
    FoldRegistryEntry("rev0070", "docs/739-export-receipt-restart-memory.md", "export receipt doc"),
    FoldRegistryEntry("rev0070", "docs/740-retention-gc-after-export.md", "retention GC doc"),
    FoldRegistryEntry("rev0070", "docs/741-closure-handoff-redacted-boundary.md", "closure handoff doc"),
    FoldRegistryEntry("rev0070", "docs/742-exporthandofffold-audit-refactor.md", "exporthandofffold doc"),
)
REGISTRY_BY_REVISION["rev0070"] = REV0070_REGISTRY
NEEDLES_BY_REVISION["rev0070"] = ("exportreceipt", "retentiongc", "closurehandoff", "exporthandofffold")

# rev0071 handoff receipt / import / summary lineage registry.
REV0071_REGISTRY = (
    FoldRegistryEntry("rev0071", "src/i2p_dht_lab/handoffreceipt.py", "recipient receipt memory after redacted closure handoff"),
    FoldRegistryEntry("rev0071", "src/i2p_dht_lab/handoffimport.py", "redacted import markers after accepted handoff receipt"),
    FoldRegistryEntry("rev0071", "src/i2p_dht_lab/summarylineage.py", "redacted summary lineage after accepted import"),
    FoldRegistryEntry("rev0071", "src/i2p_dht_lab/handoffreceiptfold.py", "rev0071 handoff receipt fold audit"),
    FoldRegistryEntry("rev0071", "tests/test_rev0071_handoffreceipt_import_summarylineage.py", "current handoff receipt / import / summary tests"),
    FoldRegistryEntry("rev0071", "docs/748-rev0071-handoffreceipt-importsummary-ledgerfold.md", "current revision doc"),
    FoldRegistryEntry("rev0071", "docs/749-handoff-receipt-recipient-boundary.md", "handoff receipt doc"),
    FoldRegistryEntry("rev0071", "docs/750-handoff-import-redacted-state.md", "handoff import doc"),
    FoldRegistryEntry("rev0071", "docs/751-summary-lineage-redacted-boundary.md", "summary lineage doc"),
    FoldRegistryEntry("rev0071", "docs/752-handoffreceiptfold-audit-refactor.md", "handoffreceiptfold doc"),
)
REGISTRY_BY_REVISION["rev0071"] = REV0071_REGISTRY
NEEDLES_BY_REVISION["rev0071"] = ("handoffreceipt", "handoffimport", "summarylineage", "handoffreceiptfold")

# rev0072 summary receipt / import archive / lineage prune registry.
REV0072_REGISTRY = (
    FoldRegistryEntry("rev0072", "src/i2p_dht_lab/summaryreceipt.py", "summary receipt after redacted lineage"),
    FoldRegistryEntry("rev0072", "src/i2p_dht_lab/importarchive.py", "restart-sticky import archive after summary receipt"),
    FoldRegistryEntry("rev0072", "src/i2p_dht_lab/lineageprune.py", "lineage prune guard preserving contradiction/import/archive memory"),
    FoldRegistryEntry("rev0072", "src/i2p_dht_lab/summaryreceiptfold.py", "rev0072 summary receipt fold audit"),
    FoldRegistryEntry("rev0072", "tests/test_rev0072_summaryreceipt_importarchive_lineageprune.py", "current summary receipt / import archive / lineage prune tests"),
    FoldRegistryEntry("rev0072", "docs/758-rev0072-summaryreceipt-importarchive-lineageprune.md", "current revision doc"),
    FoldRegistryEntry("rev0072", "docs/759-summary-receipt-after-lineage.md", "summary receipt doc"),
    FoldRegistryEntry("rev0072", "docs/760-import-archive-after-summary-receipt.md", "import archive doc"),
    FoldRegistryEntry("rev0072", "docs/761-lineage-prune-guard.md", "lineage prune doc"),
    FoldRegistryEntry("rev0072", "docs/762-summaryreceiptfold-audit-refactor.md", "summaryreceiptfold doc"),
)
REGISTRY_BY_REVISION["rev0072"] = REV0072_REGISTRY
NEEDLES_BY_REVISION["rev0072"] = ("summaryreceipt", "importarchive", "lineageprune", "summaryreceiptfold")

# rev0073 summary publication / redaction witness / import-prune audit registry.
REV0073_REGISTRY = (
    FoldRegistryEntry("rev0073", "src/i2p_dht_lab/summarypublish.py", "summary publication after lineage prune"),
    FoldRegistryEntry("rev0073", "src/i2p_dht_lab/redactionwitness.py", "redaction witness receipts"),
    FoldRegistryEntry("rev0073", "src/i2p_dht_lab/importpruneaudit.py", "import-prune audit after restart"),
    FoldRegistryEntry("rev0073", "src/i2p_dht_lab/summarypublishfold.py", "rev0073 summary publish fold audit"),
    FoldRegistryEntry("rev0073", "tests/test_rev0073_summarypublish_redactionwitness_importpruneaudit.py", "current summary publication / redaction witness / import-prune audit tests"),
    FoldRegistryEntry("rev0073", "docs/768-rev0073-summarypublish-redactionwitness-importpruneaudit.md", "current revision doc"),
    FoldRegistryEntry("rev0073", "docs/769-summary-publication-after-lineage-prune.md", "summary publication doc"),
    FoldRegistryEntry("rev0073", "docs/770-redaction-witness-receipts.md", "redaction witness doc"),
    FoldRegistryEntry("rev0073", "docs/771-import-prune-audit-after-restart.md", "import-prune audit doc"),
    FoldRegistryEntry("rev0073", "docs/772-summarypublishfold-audit-refactor.md", "summarypublishfold doc"),
)
REGISTRY_BY_REVISION["rev0073"] = REV0073_REGISTRY
NEEDLES_BY_REVISION["rev0073"] = ("summarypublish", "redactionwitness", "importpruneaudit", "summarypublishfold")

# rev0074 summary outbox / redaction archive / publish fence registry.
REV0074_REGISTRY = (
    FoldRegistryEntry("rev0074", "src/i2p_dht_lab/summaryoutbox.py", "summary outbox staging after publication/redaction/audit"),
    FoldRegistryEntry("rev0074", "src/i2p_dht_lab/redactionarchive.py", "redaction archive restart memory"),
    FoldRegistryEntry("rev0074", "src/i2p_dht_lab/publishfence.py", "summary publish fence before live/public write"),
    FoldRegistryEntry("rev0074", "src/i2p_dht_lab/summaryoutboxfold.py", "rev0074 summary outbox fold audit"),
    FoldRegistryEntry("rev0074", "tests/test_rev0074_summaryoutbox_redactionarchive_publishfence.py", "current summary outbox / redaction archive / publish fence tests"),
    FoldRegistryEntry("rev0074", "docs/778-rev0074-summaryoutbox-redactionarchive-publishfence.md", "current revision doc"),
    FoldRegistryEntry("rev0074", "docs/779-summary-outbox-after-publication.md", "summary outbox doc"),
    FoldRegistryEntry("rev0074", "docs/780-redaction-archive-restart-memory.md", "redaction archive doc"),
    FoldRegistryEntry("rev0074", "docs/781-publish-fence-before-summary-write.md", "publish fence doc"),
    FoldRegistryEntry("rev0074", "docs/782-summaryoutboxfold-audit-refactor.md", "summaryoutboxfold doc"),
)
REGISTRY_BY_REVISION["rev0074"] = REV0074_REGISTRY
NEEDLES_BY_REVISION["rev0074"] = ("summaryoutbox", "redactionarchive", "publishfence", "summaryoutboxfold")

# rev0075 summary send canary / redaction GC / outbox settlement registry.
REV0075_REGISTRY = (
    FoldRegistryEntry("rev0075", "src/i2p_dht_lab/summarysendcanary.py", "no-network summary-send canary after publish fence"),
    FoldRegistryEntry("rev0075", "src/i2p_dht_lab/redactiongc.py", "redaction GC preserving archive/fence/contradiction memory"),
    FoldRegistryEntry("rev0075", "src/i2p_dht_lab/outboxsettlement.py", "prepared/committed/aborted/suppressed summary outbox settlement"),
    FoldRegistryEntry("rev0075", "src/i2p_dht_lab/summarysendfold.py", "rev0075 summary-send fold audit"),
    FoldRegistryEntry("rev0075", "tests/test_rev0075_summarysendcanary_redactiongc_outboxsettlement.py", "current summary send / redaction GC / settlement tests"),
    FoldRegistryEntry("rev0075", "docs/788-rev0075-summarysendcanary-redactiongc-outboxsettlement.md", "current revision doc"),
    FoldRegistryEntry("rev0075", "docs/789-summary-send-canary-before-live-write.md", "summary-send canary doc"),
    FoldRegistryEntry("rev0075", "docs/790-redaction-gc-join-after-archive.md", "redaction GC doc"),
    FoldRegistryEntry("rev0075", "docs/791-outbox-settlement-prepared-aborted-suppressed.md", "outbox settlement doc"),
    FoldRegistryEntry("rev0075", "docs/792-summarysendfold-audit-refactor.md", "summarysendfold doc"),
)
REGISTRY_BY_REVISION["rev0075"] = REV0075_REGISTRY
NEEDLES_BY_REVISION["rev0075"] = ("summarysendcanary", "redactiongc", "outboxsettlement", "summarysendfold")

# rev0075 summary send canary / redaction GC / outbox settlement active registry.
REV0075_REGISTRY = REV0074_REGISTRY + (
    FoldRegistryEntry("rev0075", "src/i2p_dht_lab/summarysendcanary.py", "no-network summary-send canary after publish fence"),
    FoldRegistryEntry("rev0075", "src/i2p_dht_lab/redactiongc.py", "redaction GC joined after archive/fence/canary"),
    FoldRegistryEntry("rev0075", "src/i2p_dht_lab/outboxsettlement.py", "prepared/aborted/suppressed outbox settlement markers"),
    FoldRegistryEntry("rev0075", "src/i2p_dht_lab/summarysendfold.py", "rev0075 summary send fold audit"),
    FoldRegistryEntry("rev0075", "tests/test_rev0075_summarysendcanary_redactiongc_outboxsettlement.py", "current summary-send / redaction-GC / outbox-settlement tests"),
    FoldRegistryEntry("rev0075", "docs/788-rev0075-summarysendcanary-redactiongc-outboxsettlement.md", "current revision doc"),
    FoldRegistryEntry("rev0075", "docs/789-summary-send-canary-before-live-write.md", "summary send canary doc"),
    FoldRegistryEntry("rev0075", "docs/790-redaction-gc-join-after-archive.md", "redaction GC doc"),
    FoldRegistryEntry("rev0075", "docs/791-outbox-settlement-prepared-aborted-suppressed.md", "outbox settlement doc"),
    FoldRegistryEntry("rev0075", "docs/792-summarysendfold-audit-refactor.md", "summarysendfold doc"),
)
REGISTRY_BY_REVISION["rev0075"] = REV0075_REGISTRY
NEEDLES_BY_REVISION["rev0075"] = ("summarysendcanary", "redactiongc", "outboxsettlement", "summarysendfold")

# rev0075 corrected active registry after folding the sibling summary-settlement branchlet.
REV0075_REGISTRY = (
    FoldRegistryEntry("rev0075", "src/i2p_dht_lab/outboxsettlement.py", "outbox settlement branch join"),
    FoldRegistryEntry("rev0075", "src/i2p_dht_lab/summarysendcanary.py", "no-network summary send canary"),
    FoldRegistryEntry("rev0075", "src/i2p_dht_lab/summarysettlement.py", "folded summary-settlement branchlet"),
    FoldRegistryEntry("rev0075", "src/i2p_dht_lab/publicledger.py", "folded public-ledger branchlet"),
    FoldRegistryEntry("rev0075", "src/i2p_dht_lab/redactiongc.py", "folded redaction-GC branchlet"),
    FoldRegistryEntry("rev0075", "src/i2p_dht_lab/summarysendfold.py", "rev0075 summary-send fold audit"),
    FoldRegistryEntry("rev0075", "tests/test_rev0075_summarysendcanary_redactiongc_outboxsettlement.py", "current summary-send canary / outbox-settlement tests"),
    FoldRegistryEntry("rev0075", "tests/test_rev0074_summarysettlement_publicledger_redactiongc.py", "folded sibling branchlet tests"),
    FoldRegistryEntry("rev0075", "docs/788-rev0075-summarysendcanary-redactiongc-outboxsettlement.md", "current revision doc"),
    FoldRegistryEntry("rev0075", "docs/791-outbox-settlement-prepared-aborted-suppressed.md", "outbox settlement doc"),
    FoldRegistryEntry("rev0075", "docs/789-summary-send-canary-before-live-write.md", "summary send canary doc"),
    FoldRegistryEntry("rev0075", "docs/790-redaction-gc-join-after-archive.md", "summary-settlement branchlet fold doc"),
    FoldRegistryEntry("rev0075", "docs/792-summarysendfold-audit-refactor.md", "summarysendfold audit doc"),
    FoldRegistryEntry("rev0075", "artifacts/branchlets/rev0074_summarysettlement_publicledger_redactiongc/test_rev0074_summarysettlement_publicledger_redactiongc.py", "folded branchlet artifact"),
)
REGISTRY_BY_REVISION["rev0075"] = REV0075_REGISTRY
NEEDLES_BY_REVISION["rev0075"] = ("outboxsettlement", "summarysendcanary", "summarysettlement", "publicledger", "redactiongc", "summarysendfold")

# rev0076 summary drain / delivery witness / settlement fence registry.
REV0076_REGISTRY = (
    FoldRegistryEntry("rev0076", "src/i2p_dht_lab/summarydrain.py", "summary drain after summary send canary"),
    FoldRegistryEntry("rev0076", "src/i2p_dht_lab/summarydeliverywitness.py", "delivery witness observations after no-network drain"),
    FoldRegistryEntry("rev0076", "src/i2p_dht_lab/settlementfence.py", "settlement fence after delivery witness"),
    FoldRegistryEntry("rev0076", "src/i2p_dht_lab/summarydeliveryfold.py", "rev0076 summary delivery fold audit"),
    FoldRegistryEntry("rev0076", "tests/test_rev0076_summarydrain_deliverywitness_settlementfence.py", "current summary drain / delivery witness / settlement fence tests"),
    FoldRegistryEntry("rev0076", "docs/798-rev0076-summarydrain-deliverywitness-settlementfence.md", "current revision doc"),
    FoldRegistryEntry("rev0076", "docs/799-summary-drain-after-canary.md", "summary drain doc"),
    FoldRegistryEntry("rev0076", "docs/800-summary-delivery-witness.md", "summary delivery witness doc"),
    FoldRegistryEntry("rev0076", "docs/801-settlement-fence-after-delivery.md", "settlement fence doc"),
    FoldRegistryEntry("rev0076", "docs/802-summarydeliveryfold-audit-refactor.md", "summarydeliveryfold doc"),
)
REGISTRY_BY_REVISION["rev0076"] = REV0076_REGISTRY
NEEDLES_BY_REVISION["rev0076"] = ("summarydrain", "summarydeliverywitness", "settlementfence", "summarydeliveryfold")

# rev0077 summary ACK ledger / delivery archive / prune fence registry.
REV0077_REGISTRY = (
    FoldRegistryEntry("rev0077", "src/i2p_dht_lab/summaryackledger.py", "ACK settlement ledger after summary settlement fence"),
    FoldRegistryEntry("rev0077", "src/i2p_dht_lab/deliveryarchive.py", "restart-sticky delivery archive after ACK settlement"),
    FoldRegistryEntry("rev0077", "src/i2p_dht_lab/summaryprunefence.py", "soft prune fence preserving ACK/archive/redaction/contradiction memory"),
    FoldRegistryEntry("rev0077", "src/i2p_dht_lab/summaryackfold.py", "rev0077 summary ACK fold audit"),
    FoldRegistryEntry("rev0077", "tests/test_rev0077_summaryackledger_deliveryarchive_prunefence.py", "current summary ACK/archive/prune tests"),
    FoldRegistryEntry("rev0077", "docs/808-rev0077-summaryackledger-deliveryarchive-prunefence.md", "current revision doc"),
    FoldRegistryEntry("rev0077", "docs/809-summary-ack-ledger-after-settlement-fence.md", "summary ACK ledger doc"),
    FoldRegistryEntry("rev0077", "docs/810-delivery-archive-restart-memory.md", "delivery archive doc"),
    FoldRegistryEntry("rev0077", "docs/811-summary-prune-fence.md", "summary prune fence doc"),
    FoldRegistryEntry("rev0077", "docs/812-summaryackfold-audit-refactor.md", "summaryackfold doc"),
)
REGISTRY_BY_REVISION["rev0077"] = REV0077_REGISTRY
NEEDLES_BY_REVISION["rev0077"] = ("summaryackledger", "deliveryarchive", "summaryprunefence", "summaryackfold")

# rev0078 summary replay / ACK closure / export fence registry.
REV0078_REGISTRY = (
    FoldRegistryEntry("rev0078", "src/i2p_dht_lab/summaryreplay.py", "restart replay after summary ACK/archive/prune fence"),
    FoldRegistryEntry("rev0078", "src/i2p_dht_lab/ackclosure.py", "ACK closure after restart replay"),
    FoldRegistryEntry("rev0078", "src/i2p_dht_lab/summaryexportfence.py", "no-network redacted summary export fence"),
    FoldRegistryEntry("rev0078", "src/i2p_dht_lab/summaryreplayfold.py", "rev0078 summary replay fold audit"),
    FoldRegistryEntry("rev0078", "tests/test_rev0078_summaryreplay_ackclosure_exportfence.py", "current summary replay / ACK closure / export fence tests"),
    FoldRegistryEntry("rev0078", "docs/818-rev0078-summaryreplay-ackclosure-exportfence.md", "current revision doc"),
    FoldRegistryEntry("rev0078", "docs/819-summary-replay-after-prune-fence.md", "summary replay doc"),
    FoldRegistryEntry("rev0078", "docs/820-ack-closure-after-restart-replay.md", "ACK closure doc"),
    FoldRegistryEntry("rev0078", "docs/821-summary-export-fence.md", "summary export fence doc"),
    FoldRegistryEntry("rev0078", "docs/822-summaryreplayfold-audit-refactor.md", "summaryreplayfold doc"),
)
REGISTRY_BY_REVISION["rev0078"] = REV0078_REGISTRY
NEEDLES_BY_REVISION["rev0078"] = ("summaryreplay", "ackclosure", "summaryexportfence", "summaryreplayfold")

# rev0079 summary export receipt / import gate / retention audit registry.
REV0079_REGISTRY = (
    FoldRegistryEntry("rev0079", "src/i2p_dht_lab/summaryexportreceipt.py", "recipient receipt after redacted summary export fence"),
    FoldRegistryEntry("rev0079", "src/i2p_dht_lab/summaryimportgate.py", "import gate after export recipient receipt"),
    FoldRegistryEntry("rev0079", "src/i2p_dht_lab/exportretentionaudit.py", "retention audit preserving redaction and contradiction memory"),
    FoldRegistryEntry("rev0079", "src/i2p_dht_lab/summaryexportreceiptfold.py", "rev0079 summary export receipt fold audit"),
    FoldRegistryEntry("rev0079", "tests/test_rev0079_summaryexportreceipt_importgate_retentionaudit.py", "current summary export receipt / import gate / retention audit tests"),
    FoldRegistryEntry("rev0079", "docs/828-rev0079-summaryexportreceipt-importgate-retentionaudit.md", "current revision doc"),
    FoldRegistryEntry("rev0079", "docs/829-summary-export-receipt-after-export-fence.md", "summary export receipt doc"),
    FoldRegistryEntry("rev0079", "docs/830-summary-import-gate-after-receipt.md", "summary import gate doc"),
    FoldRegistryEntry("rev0079", "docs/831-export-retention-audit.md", "export retention audit doc"),
    FoldRegistryEntry("rev0079", "docs/832-summaryexportreceiptfold-audit-refactor.md", "summaryexportreceiptfold doc"),
)
REGISTRY_BY_REVISION["rev0079"] = REV0079_REGISTRY
NEEDLES_BY_REVISION["rev0079"] = ("summaryexportreceipt", "summaryimportgate", "exportretentionaudit", "summaryexportreceiptfold")

# rev0080 import settlement / archive / retention seal registry.
REV0080_REGISTRY = (
    FoldRegistryEntry("rev0080", "src/i2p_dht_lab/summaryimportsettlement.py", "summary import settlement after receipt/import/retention agreement"),
    FoldRegistryEntry("rev0080", "src/i2p_dht_lab/importarchiveledger.py", "restart-sticky import archive after settlement"),
    FoldRegistryEntry("rev0080", "src/i2p_dht_lab/importretentionseal.py", "retention seal joining settlement/archive/audit"),
    FoldRegistryEntry("rev0080", "src/i2p_dht_lab/importsettlementfold.py", "rev0080 import settlement fold audit"),
    FoldRegistryEntry("rev0080", "tests/test_rev0080_importsettlement_archive_retentionseal.py", "current import settlement / archive / retention seal tests"),
    FoldRegistryEntry("rev0080", "docs/838-rev0080-importsettlement-archive-retentionseal.md", "current revision doc"),
    FoldRegistryEntry("rev0080", "docs/839-summary-import-settlement-after-gate.md", "summary import settlement doc"),
    FoldRegistryEntry("rev0080", "docs/840-import-archive-ledger.md", "import archive ledger doc"),
    FoldRegistryEntry("rev0080", "docs/841-import-retention-seal.md", "import retention seal doc"),
    FoldRegistryEntry("rev0080", "docs/842-importsettlementfold-audit-refactor.md", "importsettlementfold doc"),
)
REGISTRY_BY_REVISION["rev0080"] = REV0080_REGISTRY
NEEDLES_BY_REVISION["rev0080"] = ("summaryimportsettlement", "importarchiveledger", "importretentionseal", "importsettlementfold")

# rev0081 Python-first / GCC leaf-kernel registry.
REV0081_REGISTRY = (
    FoldRegistryEntry("rev0081", "src/i2p_dht_lab/nativeboundary.py", "Python-first policy with narrow GCC-native leaf kernels"),
    FoldRegistryEntry("rev0081", "src/i2p_dht_lab/gccffi.py", "GCC/FFI contract guard for native leaf kernels"),
    FoldRegistryEntry("rev0081", "src/i2p_dht_lab/nativehotpaths.py", "portable Python references for native hotpaths"),
    FoldRegistryEntry("rev0081", "native/gcc/xor_distance.c", "tiny GCC-compiled XOR distance comparator candidate"),
    FoldRegistryEntry("rev0081", "src/i2p_dht_lab/nativeboundaryfold.py", "rev0081 native-boundary fold audit"),
    FoldRegistryEntry("rev0081", "tests/test_rev0081_nativeboundary_gccffi_hotpath.py", "current native boundary / GCC FFI / hotpath tests"),
    FoldRegistryEntry("rev0081", "docs/848-rev0081-nativeboundary-gccffi-hotpath.md", "current revision doc"),
    FoldRegistryEntry("rev0081", "docs/849-python-first-native-leaf-boundary.md", "Python-first native-leaf boundary doc"),
    FoldRegistryEntry("rev0081", "docs/850-gcc-ffi-contract.md", "GCC FFI contract doc"),
    FoldRegistryEntry("rev0081", "docs/851-native-hotpath-xor-kernel.md", "native hotpath XOR kernel doc"),
    FoldRegistryEntry("rev0081", "docs/852-nativeboundaryfold-audit-refactor.md", "nativeboundaryfold doc"),
)
REGISTRY_BY_REVISION["rev0081"] = REV0081_REGISTRY
NEEDLES_BY_REVISION["rev0081"] = ("nativeboundary", "gccffi", "nativehotpaths", "nativeboundaryfold")

# rev0082 native parity / ABI guard / fallback seal registry.
REV0082_REGISTRY = (
    FoldRegistryEntry("rev0082", "src/i2p_dht_lab/nativeparity.py", "Python/native parity guard before optional native hotpath selection"),
    FoldRegistryEntry("rev0082", "src/i2p_dht_lab/abiguard.py", "ABI/load guard for optional native artifacts"),
    FoldRegistryEntry("rev0082", "src/i2p_dht_lab/fallbackseal.py", "fallback seal so native quarantine routes to Python reference"),
    FoldRegistryEntry("rev0082", "src/i2p_dht_lab/nativeparityfold.py", "rev0082 native parity fold audit"),
    FoldRegistryEntry("rev0082", "tests/test_rev0082_nativeparity_abiguard_fallbackseal.py", "current native parity / ABI guard / fallback seal tests"),
    FoldRegistryEntry("rev0082", "docs/858-rev0082-nativeparity-abiguard-fallbackseal.md", "current revision doc"),
    FoldRegistryEntry("rev0082", "docs/859-native-parity-before-selection.md", "native parity doc"),
    FoldRegistryEntry("rev0082", "docs/860-abi-guard-load-boundary.md", "ABI guard doc"),
    FoldRegistryEntry("rev0082", "docs/861-fallback-seal-native-quarantine.md", "fallback seal doc"),
    FoldRegistryEntry("rev0082", "docs/862-nativeparityfold-audit-refactor.md", "nativeparityfold doc"),
)
REGISTRY_BY_REVISION["rev0082"] = REV0082_REGISTRY
NEEDLES_BY_REVISION["rev0082"] = ("nativeparity", "abiguard", "fallbackseal", "nativeparityfold")

# rev0083 native runtime / dispatch seal / source audit registry.
REV0083_REGISTRY = (
    FoldRegistryEntry("rev0083", "src/i2p_dht_lab/nativeruntime.py", "runtime drift guard after parity/ABI/fallback seal"),
    FoldRegistryEntry("rev0083", "src/i2p_dht_lab/nativedispatch.py", "exact-boundary dispatch seal for optional native XOR calls"),
    FoldRegistryEntry("rev0083", "src/i2p_dht_lab/nativeaudit.py", "textual source audit for tiny GCC leaf sources"),
    FoldRegistryEntry("rev0083", "src/i2p_dht_lab/nativedispatchfold.py", "rev0083 native dispatch fold audit"),
    FoldRegistryEntry("rev0083", "tests/test_rev0083_nativeruntime_dispatchaudit_fallbackbudget.py", "current native runtime / dispatch / source audit tests"),
    FoldRegistryEntry("rev0083", "docs/868-rev0083-nativeruntime-dispatchaudit-fallbackbudget.md", "current revision doc"),
    FoldRegistryEntry("rev0083", "docs/869-native-runtime-drift-guard.md", "native runtime drift doc"),
    FoldRegistryEntry("rev0083", "docs/870-native-dispatch-seal.md", "native dispatch seal doc"),
    FoldRegistryEntry("rev0083", "docs/871-native-source-audit.md", "native source audit doc"),
    FoldRegistryEntry("rev0083", "docs/872-nativedispatchfold-audit-refactor.md", "nativedispatchfold doc"),
)
REGISTRY_BY_REVISION["rev0083"] = REV0083_REGISTRY
NEEDLES_BY_REVISION["rev0083"] = ("nativeruntime", "nativedispatch", "nativeaudit", "nativedispatchfold")

# rev0084 parser hold / sanitizer plan / native budget registry.
REV0084_REGISTRY = (
    FoldRegistryEntry("rev0084", "src/i2p_dht_lab/parserhold.py", "parser hold keeps hostile-byte parsing Python-owned"),
    FoldRegistryEntry("rev0084", "src/i2p_dht_lab/sanitizerplan.py", "sanitizer and fuzz posture before native expansion"),
    FoldRegistryEntry("rev0084", "src/i2p_dht_lab/nativebudget.py", "native optimization budget for leaf kernels"),
    FoldRegistryEntry("rev0084", "src/i2p_dht_lab/nativebudgetfold.py", "rev0084 native budget fold audit"),
    FoldRegistryEntry("rev0084", "tests/test_rev0084_parserhold_sanitizer_nativebudget.py", "current parser hold / sanitizer / native budget tests"),
    FoldRegistryEntry("rev0084", "docs/878-rev0084-parserhold-sanitizerplan-nativebudget.md", "current revision doc"),
    FoldRegistryEntry("rev0084", "docs/879-parser-hold-python-owned.md", "parser hold doc"),
    FoldRegistryEntry("rev0084", "docs/880-sanitizer-plan-before-native-expansion.md", "sanitizer plan doc"),
    FoldRegistryEntry("rev0084", "docs/881-native-optimization-budget.md", "native budget doc"),
    FoldRegistryEntry("rev0084", "docs/882-nativebudgetfold-audit-refactor.md", "nativebudgetfold doc"),
)
REGISTRY_BY_REVISION["rev0084"] = REV0084_REGISTRY
NEEDLES_BY_REVISION["rev0084"] = ("parserhold", "sanitizerplan", "nativebudget", "nativebudgetfold")

# rev0085 native provenance / corpus / quarantine registry.
REV0085_REGISTRY = (
    FoldRegistryEntry("rev0085", "src/i2p_dht_lab/nativeprovenance.py", "native build provenance joins source audit / sanitizer / budget / artifact digests"),
    FoldRegistryEntry("rev0085", "src/i2p_dht_lab/nativecorpus.py", "differential native corpus against the Python XOR oracle"),
    FoldRegistryEntry("rev0085", "src/i2p_dht_lab/nativequarantine.py", "sticky quarantine memory for bad native artifacts"),
    FoldRegistryEntry("rev0085", "src/i2p_dht_lab/nativeprovenancefold.py", "rev0085 native provenance fold audit"),
    FoldRegistryEntry("rev0085", "tests/test_rev0085_nativeprovenance_corpus_quarantine.py", "current native provenance / corpus / quarantine tests"),
    FoldRegistryEntry("rev0085", "docs/888-rev0085-nativeprovenance-corpusquarantine-buildseal.md", "current revision doc"),
    FoldRegistryEntry("rev0085", "docs/889-native-build-provenance.md", "native build provenance doc"),
    FoldRegistryEntry("rev0085", "docs/890-differential-native-corpus.md", "differential native corpus doc"),
    FoldRegistryEntry("rev0085", "docs/891-native-quarantine-store.md", "native quarantine store doc"),
    FoldRegistryEntry("rev0085", "docs/892-nativeprovenancefold-audit-refactor.md", "nativeprovenancefold doc"),
)
REGISTRY_BY_REVISION["rev0085"] = REV0085_REGISTRY
NEEDLES_BY_REVISION["rev0085"] = ("nativeprovenance", "nativecorpus", "nativequarantine", "nativeprovenancefold")

# rev0086 native selection / fallback journal / promotion hold registry.
REV0086_REGISTRY = (
    FoldRegistryEntry("rev0086", "src/i2p_dht_lab/nativeselection.py", "native selection exact-boundary gate after provenance/corpus/quarantine"),
    FoldRegistryEntry("rev0086", "src/i2p_dht_lab/fallbackjournal.py", "restart-sticky fallback routing journal"),
    FoldRegistryEntry("rev0086", "src/i2p_dht_lab/nativepromotion.py", "promotion hold preserving fallback/quarantine memory"),
    FoldRegistryEntry("rev0086", "src/i2p_dht_lab/nativeselectionfold.py", "rev0086 native selection fold audit"),
    FoldRegistryEntry("rev0086", "tests/test_rev0086_nativeselection_fallbackjournal_promotehold.py", "current native selection / fallback journal / promotion tests"),
    FoldRegistryEntry("rev0086", "docs/898-rev0086-nativeselection-fallbackjournal-promotehold.md", "current revision doc"),
    FoldRegistryEntry("rev0086", "docs/899-native-selection-exact-boundary.md", "native selection doc"),
    FoldRegistryEntry("rev0086", "docs/900-fallback-journal-restart-memory.md", "fallback journal doc"),
    FoldRegistryEntry("rev0086", "docs/901-native-promotion-hold.md", "native promotion hold doc"),
    FoldRegistryEntry("rev0086", "docs/902-nativeselectionfold-audit-refactor.md", "nativeselectionfold doc"),
)
REGISTRY_BY_REVISION["rev0086"] = REV0086_REGISTRY
NEEDLES_BY_REVISION["rev0086"] = ("nativeselection", "fallbackjournal", "nativepromotion", "nativeselectionfold")

# rev0087 native lifecycle registry.
REV0087_REGISTRY = (
    FoldRegistryEntry("rev0087", "src/i2p_dht_lab/nativeload.py", "native load lifecycle gate after selection and promotion"),
    FoldRegistryEntry("rev0087", "src/i2p_dht_lab/nativecrashledger.py", "sticky native crash/fault ledger forcing fallback/quarantine"),
    FoldRegistryEntry("rev0087", "src/i2p_dht_lab/nativeperfguard.py", "performance guard treating profile data as operator hint only"),
    FoldRegistryEntry("rev0087", "src/i2p_dht_lab/nativelifecyclefold.py", "rev0087 native lifecycle fold audit"),
    FoldRegistryEntry("rev0087", "tests/test_rev0087_nativeload_crashledger_perfguard.py", "current native load / crash / performance tests"),
    FoldRegistryEntry("rev0087", "docs/908-rev0087-nativeload-crashledger-perfguard.md", "current revision doc"),
    FoldRegistryEntry("rev0087", "docs/909-native-load-lifecycle-boundary.md", "native load doc"),
    FoldRegistryEntry("rev0087", "docs/910-native-crash-ledger.md", "native crash ledger doc"),
    FoldRegistryEntry("rev0087", "docs/911-native-performance-guard.md", "native performance guard doc"),
    FoldRegistryEntry("rev0087", "docs/912-nativelifecyclefold-audit-refactor.md", "nativelifecyclefold doc"),
)
REGISTRY_BY_REVISION["rev0087"] = REV0087_REGISTRY
NEEDLES_BY_REVISION["rev0087"] = ("nativeload", "nativecrashledger", "nativeperfguard", "nativelifecyclefold")

# rev0088 native unload / sandbox-stub / crash-GC registry.
REV0088_REGISTRY = (
    FoldRegistryEntry("rev0088", "src/i2p_dht_lab/nativeunload.py", "native unload and quarantine boundary after load/crash/perf"),
    FoldRegistryEntry("rev0088", "src/i2p_dht_lab/nativesandboxstub.py", "no-network sandbox-stub boundary for native leaves"),
    FoldRegistryEntry("rev0088", "src/i2p_dht_lab/nativecrashgc.py", "native crash-ledger GC preserving hard faults"),
    FoldRegistryEntry("rev0088", "src/i2p_dht_lab/nativecontrolfold.py", "rev0088 native control fold audit"),
    FoldRegistryEntry("rev0088", "tests/test_rev0088_nativeunload_sandboxstub_crashgc.py", "current native control tests"),
    FoldRegistryEntry("rev0088", "docs/918-rev0088-nativeunload-sandboxstub-crashgc.md", "current revision doc"),
    FoldRegistryEntry("rev0088", "docs/919-native-unload-quarantine-boundary.md", "native unload doc"),
    FoldRegistryEntry("rev0088", "docs/920-native-sandbox-stub.md", "native sandbox stub doc"),
    FoldRegistryEntry("rev0088", "docs/921-native-crash-gc.md", "native crash GC doc"),
    FoldRegistryEntry("rev0088", "docs/922-nativecontrolfold-audit-refactor.md", "nativecontrolfold doc"),
)
REGISTRY_BY_REVISION["rev0088"] = REV0088_REGISTRY

# rev0089 native cold-start / probe corpus / loader-GC registry.
REV0089_REGISTRY = (
    FoldRegistryEntry("rev0089", "src/i2p_dht_lab/nativecoldstart.py", "native cold-start after unload/sandbox/crash-GC"),
    FoldRegistryEntry("rev0089", "src/i2p_dht_lab/probecorpus.py", "probe corpus refresh against Python oracle"),
    FoldRegistryEntry("rev0089", "src/i2p_dht_lab/loadergc.py", "loader-GC preserving tombstone/fallback/quarantine memory"),
    FoldRegistryEntry("rev0089", "src/i2p_dht_lab/nativecoldfold.py", "rev0089 native cold-start fold audit"),
    FoldRegistryEntry("rev0089", "tests/test_rev0089_nativecoldstart_probecorpus_loadergc.py", "current native cold-start/probe/loader-GC tests"),
    FoldRegistryEntry("rev0089", "docs/928-rev0089-nativecoldstart-probecorpus-loadergc.md", "current revision doc"),
    FoldRegistryEntry("rev0089", "docs/929-native-cold-start-after-unload.md", "native cold-start doc"),
    FoldRegistryEntry("rev0089", "docs/930-probe-corpus-refresh.md", "probe corpus doc"),
    FoldRegistryEntry("rev0089", "docs/931-loader-gc-after-cold-start.md", "loader-GC doc"),
    FoldRegistryEntry("rev0089", "docs/932-nativecoldfold-audit-refactor.md", "nativecoldfold doc"),
)
REGISTRY_BY_REVISION["rev0089"] = REV0089_REGISTRY
NEEDLES_BY_REVISION["rev0089"] = ("nativecoldstart", "probecorpus", "loadergc", "nativecoldfold")

# rev0090 native handoff / relaunch gate / loader seal registry.
REV0090_REGISTRY = (
    FoldRegistryEntry("rev0090", "src/i2p_dht_lab/nativehandoff.py", "native handoff from cold-start/probe/loader-GC to relaunch candidate only"),
    FoldRegistryEntry("rev0090", "src/i2p_dht_lab/relaunchgate.py", "native relaunch gate requiring prior native lane revalidation"),
    FoldRegistryEntry("rev0090", "src/i2p_dht_lab/loaderseal.py", "restart-sticky loader seal for relaunch candidates"),
    FoldRegistryEntry("rev0090", "src/i2p_dht_lab/nativefoldspine.py", "native branch fold-spine audit"),
    FoldRegistryEntry("rev0090", "src/i2p_dht_lab/nativehandofffold.py", "rev0090 native handoff fold audit"),
    FoldRegistryEntry("rev0090", "tests/test_rev0090_nativehandoff_relaunchgate_loaderseal.py", "current native handoff / relaunch / loader seal tests"),
    FoldRegistryEntry("rev0090", "docs/938-rev0090-nativehandoff-relaunchgate-loaderseal.md", "current revision doc"),
    FoldRegistryEntry("rev0090", "docs/939-native-handoff-relaunch-candidate.md", "native handoff doc"),
    FoldRegistryEntry("rev0090", "docs/940-relaunch-gate-prior-lanes.md", "native relaunch gate doc"),
    FoldRegistryEntry("rev0090", "docs/941-loader-seal-restart-memory.md", "native loader seal doc"),
    FoldRegistryEntry("rev0090", "docs/942-native-fold-spine-audit-refactor.md", "native fold-spine doc"),
)
REGISTRY_BY_REVISION["rev0090"] = REV0090_REGISTRY
NEEDLES_BY_REVISION["rev0090"] = ("nativehandoff", "relaunchgate", "loaderseal", "nativefoldspine", "nativehandofffold")


# rev0091 native oracle seal / preflight / re-entry journal registry.
REV0091_REGISTRY = (
    FoldRegistryEntry("rev0091", "src/i2p_dht_lab/nativeoracleseal.py", "Python oracle seal before native re-entry"),
    FoldRegistryEntry("rev0091", "src/i2p_dht_lab/nativepreflight.py", "native preflight routes only back to load gate"),
    FoldRegistryEntry("rev0091", "src/i2p_dht_lab/nativereentryjournal.py", "restart-sticky native re-entry journal"),
    FoldRegistryEntry("rev0091", "src/i2p_dht_lab/nativefoldspine.py", "native branch fold-spine audit through rev0091"),
    FoldRegistryEntry("rev0091", "src/i2p_dht_lab/nativereentryfold.py", "rev0091 native re-entry fold audit"),
    FoldRegistryEntry("rev0091", "tests/test_rev0091_nativereentry_oracleseal_preflight.py", "current native re-entry/oracle/preflight tests"),
    FoldRegistryEntry("rev0091", "docs/948-rev0091-nativereentry-oracleseal-preflight.md", "current revision doc"),
    FoldRegistryEntry("rev0091", "docs/949-native-oracle-seal.md", "native oracle seal doc"),
    FoldRegistryEntry("rev0091", "docs/950-native-preflight-route-to-load-gate.md", "native preflight doc"),
    FoldRegistryEntry("rev0091", "docs/951-native-reentry-journal.md", "native re-entry journal doc"),
    FoldRegistryEntry("rev0091", "docs/952-nativereentryfold-audit-refactor.md", "nativereentryfold doc"),
)
REGISTRY_BY_REVISION["rev0091"] = REV0091_REGISTRY
NEEDLES_BY_REVISION["rev0091"] = ("nativeoracleseal", "nativepreflight", "nativereentryjournal", "nativereentryfold", "nativefoldspine")

# rev0092 native load re-entry / revalidation seal / call hold registry.
REV0092_REGISTRY = (
    FoldRegistryEntry("rev0092", "src/i2p_dht_lab/nativeloadreentry.py", "native load re-entry request only, no load/dispatch"),
    FoldRegistryEntry("rev0092", "src/i2p_dht_lab/revalidationseal.py", "fresh prior-lane revalidation seal"),
    FoldRegistryEntry("rev0092", "src/i2p_dht_lab/nativecallhold.py", "native call hold on Python fallback oracle"),
    FoldRegistryEntry("rev0092", "src/i2p_dht_lab/nativefoldspine.py", "native branch fold-spine audit through rev0092"),
    FoldRegistryEntry("rev0092", "src/i2p_dht_lab/nativeloadreentryfold.py", "rev0092 native load re-entry fold audit"),
    FoldRegistryEntry("rev0092", "tests/test_rev0092_nativeloadreentry_revalidationseal_callhold.py", "current native load re-entry/revalidation/call-hold tests"),
    FoldRegistryEntry("rev0092", "docs/958-rev0092-nativeloadreentry-revalidationseal-callhold.md", "current revision doc"),
    FoldRegistryEntry("rev0092", "docs/959-native-load-reentry-request.md", "native load re-entry doc"),
    FoldRegistryEntry("rev0092", "docs/960-revalidation-seal-prior-lanes.md", "revalidation seal doc"),
    FoldRegistryEntry("rev0092", "docs/961-native-call-hold.md", "native call hold doc"),
    FoldRegistryEntry("rev0092", "docs/962-nativeloadreentryfold-audit-refactor.md", "nativeloadreentryfold doc"),
)
REGISTRY_BY_REVISION["rev0092"] = REV0092_REGISTRY
NEEDLES_BY_REVISION["rev0092"] = ("nativeloadreentry", "revalidationseal", "nativecallhold", "nativeloadreentryfold", "nativefoldspine")

# rev0093 native load loop / call canary / dispatch fence registry.
REV0093_REGISTRY = (
    FoldRegistryEntry("rev0093", "src/i2p_dht_lab/nativeloadloop.py", "native load loopback held on Python fallback"),
    FoldRegistryEntry("rev0093", "src/i2p_dht_lab/nativecallcanary.py", "native call canary carrying Python oracle result only"),
    FoldRegistryEntry("rev0093", "src/i2p_dht_lab/dispatchfence.py", "native dispatch fence before any call release"),
    FoldRegistryEntry("rev0093", "src/i2p_dht_lab/nativefoldspine.py", "native branch fold-spine audit through rev0093"),
    FoldRegistryEntry("rev0093", "src/i2p_dht_lab/nativeloadloopfold.py", "rev0093 native load loop fold audit"),
    FoldRegistryEntry("rev0093", "tests/test_rev0093_nativeloadloop_callcanary_dispatchfence.py", "current native load loop / call canary / dispatch fence tests"),
    FoldRegistryEntry("rev0093", "docs/968-rev0093-nativeloadloop-callcanary-dispatchfence.md", "current revision doc"),
    FoldRegistryEntry("rev0093", "docs/969-native-load-loopback.md", "native load loopback doc"),
    FoldRegistryEntry("rev0093", "docs/970-native-call-canary.md", "native call canary doc"),
    FoldRegistryEntry("rev0093", "docs/971-dispatch-fence.md", "dispatch fence doc"),
    FoldRegistryEntry("rev0093", "docs/972-nativeloadloopfold-audit-refactor.md", "nativeloadloopfold doc"),
)
REGISTRY_BY_REVISION["rev0093"] = REV0093_REGISTRY
NEEDLES_BY_REVISION["rev0093"] = ("nativeloadloop", "nativecallcanary", "dispatchfence", "nativeloadloopfold", "nativefoldspine")

# rev0094 native shadow-call / result-diff / fault-seal registry.
REV0094_REGISTRY = (
    FoldRegistryEntry("rev0094", "src/i2p_dht_lab/nativeshadowcall.py", "native shadow-call evidence only, never native authority"),
    FoldRegistryEntry("rev0094", "src/i2p_dht_lab/resultdiff.py", "native result diff against Python oracle with mismatch fault pressure"),
    FoldRegistryEntry("rev0094", "src/i2p_dht_lab/faultseal.py", "native fault seal preserving fallback/quarantine/crash memory"),
    FoldRegistryEntry("rev0094", "src/i2p_dht_lab/nativefoldspine.py", "native branch fold-spine audit through rev0094"),
    FoldRegistryEntry("rev0094", "src/i2p_dht_lab/nativeshadowfold.py", "rev0094 native shadow fold audit"),
    FoldRegistryEntry("rev0094", "tests/test_rev0094_nativeshadowcall_resultdiff_faultseal.py", "current native shadow/result-diff/fault-seal tests"),
    FoldRegistryEntry("rev0094", "docs/978-rev0094-nativeshadowcall-resultdiff-faultseal.md", "current revision doc"),
    FoldRegistryEntry("rev0094", "docs/979-native-shadow-call.md", "native shadow call doc"),
    FoldRegistryEntry("rev0094", "docs/980-native-result-diff.md", "native result diff doc"),
    FoldRegistryEntry("rev0094", "docs/981-native-fault-seal.md", "native fault seal doc"),
    FoldRegistryEntry("rev0094", "docs/982-nativeshadowfold-audit-refactor.md", "nativeshadowfold doc"),
)
REGISTRY_BY_REVISION["rev0094"] = REV0094_REGISTRY
NEEDLES_BY_REVISION["rev0094"] = ("nativeshadowcall", "resultdiff", "faultseal", "nativeshadowfold", "nativefoldspine")

# rev0095 native shadow-settlement / admission / call ledger registry.
REV0095_REGISTRY = (
    FoldRegistryEntry("rev0095", "src/i2p_dht_lab/nativeshadowsettlement.py", "native shadow settlement evidence only"),
    FoldRegistryEntry("rev0095", "src/i2p_dht_lab/nativeadmission.py", "held native admission to shadow slot only"),
    FoldRegistryEntry("rev0095", "src/i2p_dht_lab/nativecallledger.py", "native call ledger preserving Python route"),
    FoldRegistryEntry("rev0095", "src/i2p_dht_lab/nativefoldspine.py", "native branch fold-spine audit through rev0095"),
    FoldRegistryEntry("rev0095", "src/i2p_dht_lab/nativesettlementfold.py", "rev0095 native settlement fold audit"),
    FoldRegistryEntry("rev0095", "tests/test_rev0095_shadowsettlement_admission_callledger.py", "current native settlement/admission/call-ledger tests"),
    FoldRegistryEntry("rev0095", "docs/988-rev0095-shadowsettlement-admission-callledger.md", "current revision doc"),
    FoldRegistryEntry("rev0095", "docs/989-native-shadow-settlement.md", "native shadow settlement doc"),
    FoldRegistryEntry("rev0095", "docs/990-native-admission-held.md", "native admission doc"),
    FoldRegistryEntry("rev0095", "docs/991-native-call-ledger.md", "native call ledger doc"),
    FoldRegistryEntry("rev0095", "docs/992-nativesettlementfold-audit-refactor.md", "nativesettlementfold doc"),
)
REGISTRY_BY_REVISION["rev0095"] = REV0095_REGISTRY
NEEDLES_BY_REVISION["rev0095"] = ("nativeshadowsettlement", "nativeadmission", "nativecallledger", "nativesettlementfold", "nativefoldspine")

# rev0096 native call archive / promotion denial / shadow-GC registry.
REV0096_REGISTRY = (
    FoldRegistryEntry("rev0096", "src/i2p_dht_lab/nativecallarchive.py", "native call archive preserving Python route and call-ledger evidence"),
    FoldRegistryEntry("rev0096", "src/i2p_dht_lab/nativepromotiondeny.py", "native promotion denial after repeated matching shadow evidence"),
    FoldRegistryEntry("rev0096", "src/i2p_dht_lab/nativeshadowgc.py", "native shadow-GC compacting soft vectors while preserving Python-route denial memory"),
    FoldRegistryEntry("rev0096", "src/i2p_dht_lab/nativefoldspine.py", "native branch fold-spine audit through rev0096"),
    FoldRegistryEntry("rev0096", "src/i2p_dht_lab/nativearchivefold.py", "rev0096 native archive fold audit"),
    FoldRegistryEntry("rev0096", "tests/test_rev0096_callarchive_promotedeny_shadowgc.py", "current native archive / promotion-denial / shadow-GC tests"),
    FoldRegistryEntry("rev0096", "docs/998-rev0096-callarchive-promotedeny-shadowgc.md", "current revision doc"),
    FoldRegistryEntry("rev0096", "docs/999-native-call-archive.md", "native call archive doc"),
    FoldRegistryEntry("rev0096", "docs/1000-native-promotion-denial.md", "native promotion denial doc"),
    FoldRegistryEntry("rev0096", "docs/1001-native-shadow-gc.md", "native shadow-GC doc"),
    FoldRegistryEntry("rev0096", "docs/1002-nativearchivefold-audit-refactor.md", "nativearchivefold doc"),
)
REGISTRY_BY_REVISION["rev0096"] = REV0096_REGISTRY
NEEDLES_BY_REVISION["rev0096"] = ("nativecallarchive", "nativepromotiondeny", "nativeshadowgc", "nativearchivefold", "nativefoldspine")

# rev0097 native archive replay / promotion review / spine compact registry.
REV0097_REGISTRY = (
    FoldRegistryEntry("rev0097", "src/i2p_dht_lab/nativearchivereplay.py", "native archive replay after restart without native permission"),
    FoldRegistryEntry("rev0097", "src/i2p_dht_lab/nativepromotereview.py", "held promotion review preserving Python fallback"),
    FoldRegistryEntry("rev0097", "src/i2p_dht_lab/nativefoldspine.py", "compact native branch fold-spine audit through rev0097"),
    FoldRegistryEntry("rev0097", "src/i2p_dht_lab/nativearchivereplayfold.py", "rev0097 native archive replay fold audit"),
    FoldRegistryEntry("rev0097", "tests/test_rev0097_nativearchivereplay_promotereview_spinecompact.py", "current native archive replay / promotion-review tests"),
    FoldRegistryEntry("rev0097", "docs/1008-rev0097-nativearchivereplay-promotereview-spinecompact.md", "current revision doc"),
    FoldRegistryEntry("rev0097", "docs/1009-native-archive-replay.md", "native archive replay doc"),
    FoldRegistryEntry("rev0097", "docs/1010-native-promotion-review-held.md", "native promotion review doc"),
    FoldRegistryEntry("rev0097", "docs/1011-native-fold-spine-compact-refactor.md", "native fold spine compact refactor doc"),
    FoldRegistryEntry("rev0097", "docs/1012-nativearchivereplayfold-audit-refactor.md", "nativearchivereplayfold doc"),
)
REGISTRY_BY_REVISION["rev0097"] = REV0097_REGISTRY
NEEDLES_BY_REVISION["rev0097"] = ("nativearchivereplay", "nativepromotereview", "nativearchivereplayfold", "nativefoldspine")

# rev0098 native branch-close / promotion archive / shadow-only policy registry.
REV0098_REGISTRY = (
    FoldRegistryEntry("rev0098", "src/i2p_dht_lab/nativepromotearchive.py", "archive held native promotion review without native permission"),
    FoldRegistryEntry("rev0098", "src/i2p_dht_lab/nativepromotionpolicy.py", "shadow-only native promotion policy"),
    FoldRegistryEntry("rev0098", "src/i2p_dht_lab/nativebranchclose.py", "native branch close preserving Python fallback"),
    FoldRegistryEntry("rev0098", "src/i2p_dht_lab/nativefoldspine.py", "native fold spine through rev0098"),
    FoldRegistryEntry("rev0098", "src/i2p_dht_lab/nativebranchclosefold.py", "rev0098 native branch close fold audit"),
    FoldRegistryEntry("rev0098", "tests/test_rev0098_nativebranchclose_promotearchive_policy.py", "current native branch close tests"),
    FoldRegistryEntry("rev0098", "docs/1018-rev0098-nativebranchclose-promotearchive-policyseal.md", "current revision doc"),
    FoldRegistryEntry("rev0098", "docs/1019-native-promotion-archive.md", "native promotion archive doc"),
    FoldRegistryEntry("rev0098", "docs/1020-native-promotion-policy-shadow-only.md", "native promotion policy doc"),
    FoldRegistryEntry("rev0098", "docs/1021-native-branch-close.md", "native branch close doc"),
    FoldRegistryEntry("rev0098", "docs/1022-nativebranchclosefold-audit-refactor.md", "nativebranchclosefold doc"),
)
REGISTRY_BY_REVISION["rev0098"] = REV0098_REGISTRY
NEEDLES_BY_REVISION["rev0098"] = ("nativepromotearchive", "nativepromotionpolicy", "nativebranchclose", "nativebranchclosefold", "nativefoldspine")

# rev0099 return from native branch to Python-owned DHT substrate record plane.
REV0099_REGISTRY = (
    FoldRegistryEntry("rev0099", "src/i2p_dht_lab/recordplaneoracle.py", "Python-owned DHT record-plane oracle after native branch close"),
    FoldRegistryEntry("rev0099", "src/i2p_dht_lab/substratereentry.py", "substrate re-entry gate after native branch close"),
    FoldRegistryEntry("rev0099", "src/i2p_dht_lab/nativefoldspine.py", "native fold spine through rev0099"),
    FoldRegistryEntry("rev0099", "src/i2p_dht_lab/substratereturnfold.py", "rev0099 substrate return fold audit"),
    FoldRegistryEntry("rev0099", "tests/test_rev0099_substratereturn_recordoracle_spineaudit.py", "current substrate return tests"),
    FoldRegistryEntry("rev0099", "docs/1028-rev0099-substratereturn-recordoracle-spineaudit.md", "current revision doc"),
    FoldRegistryEntry("rev0099", "docs/1029-record-plane-oracle-after-native-close.md", "record plane oracle doc"),
    FoldRegistryEntry("rev0099", "docs/1030-substrate-reentry-after-native-close.md", "substrate re-entry doc"),
    FoldRegistryEntry("rev0099", "docs/1031-substratereturnfold-audit-refactor.md", "substratereturnfold doc"),
)
REGISTRY_BY_REVISION["rev0099"] = REV0099_REGISTRY
NEEDLES_BY_REVISION["rev0099"] = ("recordplaneoracle", "substratereentry", "substratereturnfold", "nativebranchclosefold", "nativefoldspine")

# rev0100 substrate record ingress / provider semantics / routing anchor registry.
REV0100_REGISTRY = (
    FoldRegistryEntry("rev0100", "src/i2p_dht_lab/recordingress.py", "Python-owned DHT record-ingress gate after substrate return"),
    FoldRegistryEntry("rev0100", "src/i2p_dht_lab/providersemantics.py", "provider semantic proof join after provider record ingress"),
    FoldRegistryEntry("rev0100", "src/i2p_dht_lab/routinganchor.py", "I2P routing-anchor gate for signed contact records"),
    FoldRegistryEntry("rev0100", "src/i2p_dht_lab/substratespine.py", "substrate spine after native branch close"),
    FoldRegistryEntry("rev0100", "src/i2p_dht_lab/substratecenturyfold.py", "rev0100 substrate-century fold audit"),
    FoldRegistryEntry("rev0100", "tests/test_rev0100_recordingress_providersemantics_routingspine.py", "current substrate ingress/provider/routing tests"),
    FoldRegistryEntry("rev0100", "docs/1038-rev0100-recordingress-providersemantics-routingspine.md", "current revision doc"),
    FoldRegistryEntry("rev0100", "docs/1039-record-ingress-after-substrate-return.md", "record ingress doc"),
    FoldRegistryEntry("rev0100", "docs/1040-provider-semantics-after-record-ingress.md", "provider semantics doc"),
    FoldRegistryEntry("rev0100", "docs/1041-routing-anchor-after-record-ingress.md", "routing anchor doc"),
    FoldRegistryEntry("rev0100", "docs/1042-substrate-spine-century-audit.md", "substrate spine / fold audit doc"),
)
REGISTRY_BY_REVISION["rev0100"] = REV0100_REGISTRY
NEEDLES_BY_REVISION["rev0100"] = ("recordingress", "providersemantics", "routinganchor", "substratespine", "substratecenturyfold")

# rev0101 mutable placement / provider bucket / route storage registry.
REV0101_REGISTRY = (
    FoldRegistryEntry("rev0101", "src/i2p_dht_lab/mutableplacement.py", "mutable-head observation placement after Python-owned record ingress"),
    FoldRegistryEntry("rev0101", "src/i2p_dht_lab/providerbucket.py", "provider-index bucket admission after provider semantic proof"),
    FoldRegistryEntry("rev0101", "src/i2p_dht_lab/routestorage.py", "routing-table storage after I2P routing anchor acceptance"),
    FoldRegistryEntry("rev0101", "src/i2p_dht_lab/substratespine.py", "substrate spine through rev0101"),
    FoldRegistryEntry("rev0101", "src/i2p_dht_lab/substrateplacementfold.py", "rev0101 substrate placement fold audit"),
    FoldRegistryEntry("rev0101", "tests/test_rev0101_mutableplace_providerbucket_routestorage.py", "current mutable placement / provider bucket / route storage tests"),
    FoldRegistryEntry("rev0101", "docs/1048-rev0101-mutableplace-providerbucket-routestorage.md", "current revision doc"),
    FoldRegistryEntry("rev0101", "docs/1049-mutable-placement-after-record-ingress.md", "mutable placement doc"),
    FoldRegistryEntry("rev0101", "docs/1050-provider-bucket-after-provider-semantics.md", "provider bucket doc"),
    FoldRegistryEntry("rev0101", "docs/1051-route-storage-after-routing-anchor.md", "route storage doc"),
    FoldRegistryEntry("rev0101", "docs/1052-substrate-placementfold-audit.md", "substrate placement fold doc"),
)
REGISTRY_BY_REVISION["rev0101"] = REV0101_REGISTRY
NEEDLES_BY_REVISION["rev0101"] = ("mutableplacement", "providerbucket", "routestorage", "substratespine", "substrateplacementfold")
