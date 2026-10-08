"""Declarative fold-map audit for current and historical cube paths.

rev0032 keeps the rev0031 fold-map idea but makes it revision-aware.  The
current path is scopeledger/storedebt/samtrace/scopefold; rev0031 remains a
predecessor map, not a failing stale surface.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .surfaceledger import audit_surface_ledger, entries_for_revision

FOLD_MAP_DOMAIN = DOMAIN + b":fold-map-v1:"


@dataclass(frozen=True)
class FoldMapEntry:
    revision: str
    path: str
    role: str
    current: bool = False

    def bvalue(self) -> dict[bytes, object]:
        return {b"revision": self.revision, b"path": self.path, b"role": self.role, b"current": 1 if self.current else 0}


@dataclass(frozen=True)
class FoldMapFinding:
    severity: str
    code: str
    path: str
    detail: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"severity": self.severity, b"code": self.code, b"path": self.path, b"detail": self.detail}


@dataclass(frozen=True)
class FoldMapReport:
    revision: str
    artifact_stem: str
    status: str
    current_entry_count: int
    historical_entry_count: int
    findings: tuple[FoldMapFinding, ...]
    report_digest: bytes

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")


REV0031_CURRENT = (
    FoldMapEntry("rev0031", "src/i2p_dht_lab/probeledger.py", "repeated_round_probe_memory", True),
    FoldMapEntry("rev0031", "src/i2p_dht_lab/crisisroute.py", "key_crisis_route_gate", True),
    FoldMapEntry("rev0031", "src/i2p_dht_lab/sketchboundary.py", "set_reconciliation_adapter_boundary", True),
    FoldMapEntry("rev0031", "src/i2p_dht_lab/foldmap.py", "declarative_fold_map", True),
    FoldMapEntry("rev0031", "tests/test_rev0031_probeledger_crisisroute_sketchboundary.py", "current_tests", True),
    FoldMapEntry("rev0031", "docs/313-rev0031-probeledger-crisisroute-sketchboundary.md", "current_revision_doc", True),
    FoldMapEntry("rev0031", "docs/314-repeated-round-probe-ledger.md", "probeledger_doc", True),
    FoldMapEntry("rev0031", "docs/315-key-crisis-route-gating.md", "crisisroute_doc", True),
    FoldMapEntry("rev0031", "docs/316-set-reconciliation-adapter-boundary.md", "sketchboundary_doc", True),
    FoldMapEntry("rev0031", "docs/317-foldmap-audit-refactor.md", "foldmap_doc", True),
)

REV0032_CURRENT = (
    FoldMapEntry("rev0032", "src/i2p_dht_lab/scopeledger.py", "joined_scope_ledger", True),
    FoldMapEntry("rev0032", "src/i2p_dht_lab/storedebt.py", "store_debt_pressure", True),
    FoldMapEntry("rev0032", "src/i2p_dht_lab/samtrace.py", "sam_trace_scope_join", True),
    FoldMapEntry("rev0032", "src/i2p_dht_lab/scopefold.py", "scopefold_current_audit", True),
    FoldMapEntry("rev0032", "tests/test_rev0032_scopeledger_storedebt_samtrace.py", "current_tests", True),
    FoldMapEntry("rev0032", "docs/319-rev0032-scopeledger-storedebt-samtrace.md", "current_revision_doc", True),
    FoldMapEntry("rev0032", "docs/320-scope-ledger-joined-advance.md", "scopeledger_doc", True),
    FoldMapEntry("rev0032", "docs/321-store-debt-repair-pressure.md", "storedebt_doc", True),
    FoldMapEntry("rev0032", "docs/322-sam-trace-scope-boundary.md", "samtrace_doc", True),
    FoldMapEntry("rev0032", "docs/323-scopefold-audit-refactor.md", "scopefold_doc", True),
)

REV0033_CURRENT = (
    FoldMapEntry("rev0033", "src/i2p_dht_lab/negotiationlane.py", "protocol_negotiation_lane", True),
    FoldMapEntry("rev0033", "src/i2p_dht_lab/migrationlane.py", "state_migration_lane", True),
    FoldMapEntry("rev0033", "src/i2p_dht_lab/safestart.py", "safe_start_join", True),
    FoldMapEntry("rev0033", "src/i2p_dht_lab/negotiationfold.py", "negotiationfold_current_audit", True),
    FoldMapEntry("rev0033", "tests/test_rev0033_negotiation_migration_safestart.py", "current_tests", True),
    FoldMapEntry("rev0033", "docs/329-rev0033-negotiationlane-migrationseal.md", "current_revision_doc", True),
    FoldMapEntry("rev0033", "docs/330-protocol-negotiation-downgrade-pressure.md", "negotiationlane_doc", True),
    FoldMapEntry("rev0033", "docs/331-state-migration-hard-negative-preservation.md", "migrationlane_doc", True),
    FoldMapEntry("rev0033", "docs/332-safe-start-joined-boundary.md", "safestart_doc", True),
    FoldMapEntry("rev0033", "docs/333-negotiationfold-audit-refactor.md", "negotiationfold_doc", True),
)

REV0034_CURRENT = (
    FoldMapEntry("rev0034", "src/i2p_dht_lab/launchquorum.py", "launch_quorum_join", True),
    FoldMapEntry("rev0034", "src/i2p_dht_lab/metricsveil.py", "metrics_veil_guard", True),
    FoldMapEntry("rev0034", "src/i2p_dht_lab/foldmerge.py", "foldmerge_current_audit", True),
    FoldMapEntry("rev0034", "src/i2p_dht_lab/persistjoin.py", "folded_persistjoin_branchlet", True),
    FoldMapEntry("rev0034", "src/i2p_dht_lab/samprobe.py", "folded_samprobe_branchlet", True),
    FoldMapEntry("rev0034", "tests/test_rev0034_launch_metrics_foldmerge.py", "current_tests", True),
    FoldMapEntry("rev0034", "docs/339-rev0034-launchquorum-metricsveil-foldmerge.md", "current_revision_doc", True),
    FoldMapEntry("rev0034", "docs/340-launch-quorum-cold-start-boundary.md", "launchquorum_doc", True),
    FoldMapEntry("rev0034", "docs/341-metrics-veil-observability-pressure.md", "metricsveil_doc", True),
    FoldMapEntry("rev0034", "docs/342-foldmerge-audit-refactor.md", "foldmerge_doc", True),
)

REV0035_CURRENT = (
    FoldMapEntry("rev0035", "src/i2p_dht_lab/startmatrix.py", "start_profile_matrix", True),
    FoldMapEntry("rev0035", "src/i2p_dht_lab/routerharness.py", "router_harness_capsule", True),
    FoldMapEntry("rev0035", "src/i2p_dht_lab/telemetrydebt.py", "telemetry_retention_debt", True),
    FoldMapEntry("rev0035", "src/i2p_dht_lab/startfold.py", "startfold_current_audit", True),
    FoldMapEntry("rev0035", "tests/test_rev0035_startmatrix_telemetry_router.py", "current_tests", True),
    FoldMapEntry("rev0035", "docs/349-rev0035-startmatrix-telemetrydebt-routerharness.md", "current_revision_doc", True),
    FoldMapEntry("rev0035", "docs/350-start-profile-matrix.md", "startmatrix_doc", True),
    FoldMapEntry("rev0035", "docs/351-router-harness-config-capsule.md", "routerharness_doc", True),
    FoldMapEntry("rev0035", "docs/352-telemetry-debt-retention.md", "telemetrydebt_doc", True),
    FoldMapEntry("rev0035", "docs/353-startfold-audit-refactor.md", "startfold_doc", True),
)

REV0036_CURRENT = (
    FoldMapEntry("rev0036", "src/i2p_dht_lab/servicecatalog.py", "service_catalog_capsules", True),
    FoldMapEntry("rev0036", "src/i2p_dht_lab/loadsheath.py", "load_sheath_profiles", True),
    FoldMapEntry("rev0036", "src/i2p_dht_lab/profilegc.py", "profile_gc_config_pressure", True),
    FoldMapEntry("rev0036", "src/i2p_dht_lab/foldregistry.py", "declarative_fold_registry", True),
    FoldMapEntry("rev0036", "src/i2p_dht_lab/servicefold.py", "servicefold_current_audit", True),
    FoldMapEntry("rev0036", "tests/test_rev0036_servicecatalog_loadsheath_profilegc.py", "current_tests", True),
    FoldMapEntry("rev0036", "docs/360-rev0036-servicecatalog-loadsheath-profilegc.md", "current_revision_doc", True),
    FoldMapEntry("rev0036", "docs/361-service-catalog-capsules.md", "servicecatalog_doc", True),
    FoldMapEntry("rev0036", "docs/362-load-sheath-useful-refusal-profiles.md", "loadsheath_doc", True),
    FoldMapEntry("rev0036", "docs/363-profile-gc-config-change-pressure.md", "profilegc_doc", True),
    FoldMapEntry("rev0036", "docs/364-foldregistry-servicefold-audit.md", "servicefold_doc", True),
)

REV0037_CURRENT = (
    FoldMapEntry("rev0037", "src/i2p_dht_lab/serviceticket.py", "service_ticket_exact_scope_grants", True),
    FoldMapEntry("rev0037", "src/i2p_dht_lab/servicereceipt.py", "service_receipts_refusal_loop_pressure", True),
    FoldMapEntry("rev0037", "src/i2p_dht_lab/ticketfold.py", "ticketfold_current_audit", True),
    FoldMapEntry("rev0037", "src/i2p_dht_lab/serviceannounce.py", "service_announcement_redaction", True),
    FoldMapEntry("rev0037", "src/i2p_dht_lab/ingressgate.py", "ingress_gate_announcement_pressure", True),
    FoldMapEntry("rev0037", "src/i2p_dht_lab/serviceguardfold.py", "serviceguardfold_branchlet_audit", True),
    FoldMapEntry("rev0037", "tests/test_rev0037_service_ticket_receipt_fold.py", "ticket_tests", True),
    FoldMapEntry("rev0037", "tests/test_rev0037_serviceannounce_ingressgate_registryfold.py", "serviceguard_tests", True),
    FoldMapEntry("rev0037", "docs/371-rev0037-ticketlane-servicereceipt-registryfold.md", "current_revision_doc", True),
    FoldMapEntry("rev0037", "docs/372-service-ticket-exact-scope-grants.md", "serviceticket_doc", True),
    FoldMapEntry("rev0037", "docs/373-service-receipts-and-refusal-loops.md", "servicereceipt_doc", True),
    FoldMapEntry("rev0037", "docs/374-ticketfold-audit-refactor.md", "ticketfold_doc", True),
    FoldMapEntry("rev0037", "docs/380-service-announcement-redaction.md", "serviceannounce_doc", True),
    FoldMapEntry("rev0037", "docs/381-ingress-gate-announcement-pressure.md", "ingressgate_doc", True),
    FoldMapEntry("rev0037", "docs/382-serviceguardfold-branchlet.md", "serviceguardfold_doc", True),
)

HISTORICAL_FOLDS = (
    FoldMapEntry("rev0035", "src/i2p_dht_lab/startfold.py", "predecessor_fold", False),
    FoldMapEntry("rev0031", "src/i2p_dht_lab/foldmap.py", "predecessor_fold", False),
    FoldMapEntry("rev0030", "src/i2p_dht_lab/keycrisisfold.py", "predecessor_fold", False),
    FoldMapEntry("rev0029", "src/i2p_dht_lab/foldseal.py", "predecessor_fold", False),
    FoldMapEntry("rev0028", "src/i2p_dht_lab/foldspine.py", "predecessor_fold", False),
    FoldMapEntry("rev0027", "src/i2p_dht_lab/branchmergefold.py", "predecessor_fold", False),
)


REV0038_CURRENT = (
    FoldMapEntry("rev0038", "src/i2p_dht_lab/catalogwire.py", "catalog_wire_branchlet_folded", True),
    FoldMapEntry("rev0038", "src/i2p_dht_lab/serviceprobe.py", "service_probe_branchlet_folded", True),
    FoldMapEntry("rev0038", "src/i2p_dht_lab/profilegcjoin.py", "profile_gc_join_branchlet_folded", True),
    FoldMapEntry("rev0038", "src/i2p_dht_lab/catalogsuccession.py", "catalog_succession_branchlet_folded", True),
    FoldMapEntry("rev0038", "src/i2p_dht_lab/servicewithdrawal.py", "service_withdrawal_branchlet_folded", True),
    FoldMapEntry("rev0038", "src/i2p_dht_lab/servicerelay.py", "service_relay_branchlet_folded", True),
    FoldMapEntry("rev0038", "src/i2p_dht_lab/serviceusegate.py", "service_use_gate_branchlet_folded", True),
    FoldMapEntry("rev0038", "src/i2p_dht_lab/handofflane.py", "handoff_lane_branchlet_folded", True),
    FoldMapEntry("rev0038", "src/i2p_dht_lab/receiptveil.py", "receipt_veil_branchlet_folded", True),
    FoldMapEntry("rev0038", "src/i2p_dht_lab/servicecontinuity.py", "service_continuity_joined_boundary", True),
    FoldMapEntry("rev0038", "src/i2p_dht_lab/servicecontinuityfold.py", "service_continuity_fold_audit", True),
    FoldMapEntry("rev0038", "tests/test_rev0038_servicecontinuity_branchfold.py", "service_continuity_tests", True),
    FoldMapEntry("rev0038", "docs/383-rev0038-servicecontinuity-branchfold.md", "current_revision_doc", True),
    FoldMapEntry("rev0038", "docs/384-service-continuity-joined-boundary.md", "service_continuity_doc", True),
    FoldMapEntry("rev0038", "docs/385-branchlet-fold-service-surfaces.md", "branchlet_fold_doc", True),
    FoldMapEntry("rev0038", "docs/386-profile-gc-catalog-succession-joins.md", "profile_gc_catalog_succession_doc", True),
    FoldMapEntry("rev0038", "docs/387-servicecontinuityfold-audit-refactor.md", "servicecontinuityfold_doc", True),
)


REV0039_CURRENT = (
    FoldMapEntry("rev0039", "src/i2p_dht_lab/servicehealth.py", "service_health_post_continuity", True),
    FoldMapEntry("rev0039", "src/i2p_dht_lab/servicedrain.py", "service_drain_safe_stop", True),
    FoldMapEntry("rev0039", "src/i2p_dht_lab/continuityjournal.py", "continuity_journal_restart_memory", True),
    FoldMapEntry("rev0039", "src/i2p_dht_lab/serviceopsfold.py", "serviceops_fold_audit", True),
    FoldMapEntry("rev0039", "tests/test_rev0039_serviceops_journal_drain.py", "serviceops_tests", True),
    FoldMapEntry("rev0039", "docs/393-rev0039-serviceops-healthdrain-journalfold.md", "current_revision_doc", True),
    FoldMapEntry("rev0039", "docs/394-service-health-post-continuity.md", "servicehealth_doc", True),
    FoldMapEntry("rev0039", "docs/395-service-drain-safe-stop.md", "servicedrain_doc", True),
    FoldMapEntry("rev0039", "docs/396-continuity-journal-restart-memory.md", "continuityjournal_doc", True),
    FoldMapEntry("rev0039", "docs/397-serviceopsfold-audit-refactor.md", "serviceopsfold_doc", True),
)


REV0040_CURRENT = (
    FoldMapEntry("rev0040", "src/i2p_dht_lab/operatorintent.py", "operator_intent_capsules", True),
    FoldMapEntry("rev0040", "src/i2p_dht_lab/servicebreaker.py", "service_breaker_pressure", True),
    FoldMapEntry("rev0040", "src/i2p_dht_lab/serviceexit.py", "service_exit_joined_boundary", True),
    FoldMapEntry("rev0040", "src/i2p_dht_lab/operationsfold.py", "operations_fold_audit", True),
    FoldMapEntry("rev0040", "tests/test_rev0040_operator_breaker_exit_fold.py", "operations_tests", True),
    FoldMapEntry("rev0040", "docs/414-rev0040-operatorbreaker-serviceexit-fold.md", "current_revision_doc", True),
    FoldMapEntry("rev0040", "docs/415-operator-intent-capsules.md", "operatorintent_doc", True),
    FoldMapEntry("rev0040", "docs/416-service-breaker-pressure.md", "servicebreaker_doc", True),
    FoldMapEntry("rev0040", "docs/417-service-exit-join.md", "serviceexit_doc", True),
    FoldMapEntry("rev0040", "docs/418-operationsfold-audit-refactor.md", "operationsfold_doc", True),
)


REV0041_CURRENT = (
    FoldMapEntry("rev0041", "src/i2p_dht_lab/routerstop.py", "router_stop_shadow_boundary", True),
    FoldMapEntry("rev0041", "src/i2p_dht_lab/sessionresume.py", "session_resume_joined_gate", True),
    FoldMapEntry("rev0041", "src/i2p_dht_lab/exitjournal.py", "exit_journal_restart_memory", True),
    FoldMapEntry("rev0041", "src/i2p_dht_lab/controlfold.py", "control_fold_audit", True),
    FoldMapEntry("rev0041", "tests/test_rev0041_routerstop_sessionresume_exitjournal.py", "control_tests", True),
    FoldMapEntry("rev0041", "docs/424-rev0041-routerstop-sessionresume-exitjournal.md", "current_revision_doc", True),
    FoldMapEntry("rev0041", "docs/425-router-stop-shadow-boundary.md", "routerstop_doc", True),
    FoldMapEntry("rev0041", "docs/426-session-resume-joined-gate.md", "sessionresume_doc", True),
    FoldMapEntry("rev0041", "docs/427-exit-journal-restart-memory.md", "exitjournal_doc", True),
    FoldMapEntry("rev0041", "docs/428-controlfold-audit-refactor.md", "controlfold_doc", True),
)


REV0042_CURRENT = (
    FoldMapEntry("rev0042", "src/i2p_dht_lab/multiservice.py", "multi_service_router_session_pressure", True),
    FoldMapEntry("rev0042", "src/i2p_dht_lab/profilecooldown.py", "profile_cooldown_emergency_freeze", True),
    FoldMapEntry("rev0042", "src/i2p_dht_lab/operatorkey.py", "operator_key_rotation_recovery", True),
    FoldMapEntry("rev0042", "src/i2p_dht_lab/announcementrepair.py", "announcement_repair_after_bridge_disable", True),
    FoldMapEntry("rev0042", "src/i2p_dht_lab/controlplanefold.py", "controlplane_fold_audit", True),
    FoldMapEntry("rev0042", "tests/test_rev0042_multiservice_cooldown_keyoperator.py", "controlplane_tests", True),
    FoldMapEntry("rev0042", "docs/434-rev0042-multiservice-cooldown-keyoperator.md", "current_revision_doc", True),
    FoldMapEntry("rev0042", "docs/435-multi-service-router-session-pressure.md", "multiservice_doc", True),
    FoldMapEntry("rev0042", "docs/436-profile-cooldown-emergency-freeze.md", "profilecooldown_doc", True),
    FoldMapEntry("rev0042", "docs/437-operator-key-rotation-recovery.md", "operatorkey_doc", True),
    FoldMapEntry("rev0042", "docs/438-announcement-repair-after-bridge-disable.md", "announcementrepair_doc", True),
    FoldMapEntry("rev0042", "docs/439-controlplanefold-audit-refactor.md", "controlplanefold_doc", True),
)


REV0043_CURRENT = (
    FoldMapEntry("rev0043", "src/i2p_dht_lab/keycompartment.py", "key_compartment_boundaries", True),
    FoldMapEntry("rev0043", "src/i2p_dht_lab/authoritysplit.py", "authority_split_joined_gate", True),
    FoldMapEntry("rev0043", "src/i2p_dht_lab/compartmentfold.py", "compartment_fold_audit", True),
    FoldMapEntry("rev0043", "tests/test_rev0043_keycompartment_authoritysplit.py", "compartment_tests", True),
    FoldMapEntry("rev0043", "docs/445-rev0043-keycompartment-authoritysplit-fold.md", "current_revision_doc", True),
    FoldMapEntry("rev0043", "docs/446-key-compartment-boundaries.md", "keycompartment_doc", True),
    FoldMapEntry("rev0043", "docs/447-authority-split-joined-gate.md", "authoritysplit_doc", True),
    FoldMapEntry("rev0043", "docs/448-compartmentfold-audit-refactor.md", "compartmentfold_doc", True),
)



REV0044_CURRENT = (
    FoldMapEntry("rev0044", "src/i2p_dht_lab/policyfirebreak.py", "subjective_policy_firebreak", True),
    FoldMapEntry("rev0044", "src/i2p_dht_lab/authorityreceipt.py", "authority_receipt_mesh", True),
    FoldMapEntry("rev0044", "src/i2p_dht_lab/branchsealfold.py", "branchseal_fold_audit", True),
    FoldMapEntry("rev0044", "src/i2p_dht_lab/controlintent.py", "folded_controlintent_branchlet", True),
    FoldMapEntry("rev0044", "src/i2p_dht_lab/bridgefirewall.py", "folded_bridgefirewall_branchlet", True),
    FoldMapEntry("rev0044", "tests/test_rev0044_policyfirebreak_authorityreceipt_branchseal.py", "policyfirebreak_tests", True),
    FoldMapEntry("rev0044", "docs/465-rev0044-policyfirebreak-authorityreceipt-branchseal.md", "current_revision_doc", True),
    FoldMapEntry("rev0044", "docs/466-policy-firebreak-subjective-authority.md", "policyfirebreak_doc", True),
    FoldMapEntry("rev0044", "docs/467-authority-receipt-mesh.md", "authorityreceipt_doc", True),
    FoldMapEntry("rev0044", "docs/468-branchseal-audit-refactor.md", "branchseal_doc", True),
    FoldMapEntry("rev0044", "artifacts/branchlets/rev0043_controlintent_bridgefirewall/445-rev0043-controlintent-bridgefirewall-foldtrim.md", "folded_control_firewall_doc", True),
)


REV0045_CURRENT = (
    FoldMapEntry("rev0045", "src/i2p_dht_lab/bridgeepoch.py", "public_bridge_epoch_windows", True),
    FoldMapEntry("rev0045", "src/i2p_dht_lab/keyreceiptlane.py", "key_receipt_lane", True),
    FoldMapEntry("rev0045", "src/i2p_dht_lab/shadowfire.py", "shadow_fire_joined_boundary", True),
    FoldMapEntry("rev0045", "src/i2p_dht_lab/bridgeepochfold.py", "bridge_epoch_fold_audit", True),
    FoldMapEntry("rev0045", "tests/test_rev0045_bridgeepoch_keyreceipt_shadowfire.py", "current_tests", True),
    FoldMapEntry("rev0045", "docs/469-rev0045-bridgeepoch-keyreceipt-shadowfire.md", "current_revision_doc", True),
    FoldMapEntry("rev0045", "docs/470-public-bridge-epoch-windows.md", "bridgeepoch_doc", True),
    FoldMapEntry("rev0045", "docs/471-key-receipt-lane.md", "keyreceiptlane_doc", True),
    FoldMapEntry("rev0045", "docs/472-shadow-fire-joined-boundary.md", "shadowfire_doc", True),
    FoldMapEntry("rev0045", "docs/473-bridgeepochfold-audit-refactor.md", "bridgeepochfold_doc", True),
)


REV0046_CURRENT = (
    FoldMapEntry("rev0046", "src/i2p_dht_lab/moderationquarantine.py", "subjective_moderation_quarantine", True),
    FoldMapEntry("rev0046", "src/i2p_dht_lab/redresslane.py", "redress_appeal_receipts", True),
    FoldMapEntry("rev0046", "src/i2p_dht_lab/bridgeledger.py", "bridge_ledger_policy_moderation_boundary", True),
    FoldMapEntry("rev0046", "src/i2p_dht_lab/moderationfold.py", "moderationfold_current_audit", True),
    FoldMapEntry("rev0046", "tests/test_rev0046_moderation_redress_bridgeledger.py", "current_tests", True),
    FoldMapEntry("rev0046", "docs/479-rev0046-moderationquarantine-redresslane-bridgeledger.md", "current_revision_doc", True),
    FoldMapEntry("rev0046", "docs/480-moderation-quarantine-as-allegation.md", "moderationquarantine_doc", True),
    FoldMapEntry("rev0046", "docs/481-redress-lane-appeal-receipts.md", "redresslane_doc", True),
    FoldMapEntry("rev0046", "docs/482-bridge-ledger-policy-replay.md", "bridgeledger_doc", True),
    FoldMapEntry("rev0046", "docs/483-moderationfold-audit-refactor.md", "moderationfold_doc", True),
)


REV0047_CURRENT = (
    FoldMapEntry("rev0047", "src/i2p_dht_lab/witnessappealmesh.py", "witness_appeal_mesh", True),
    FoldMapEntry("rev0047", "src/i2p_dht_lab/publicationledger.py", "publication_ledger", True),
    FoldMapEntry("rev0047", "src/i2p_dht_lab/bridgequenchlane.py", "bridge_quench_lane", True),
    FoldMapEntry("rev0047", "src/i2p_dht_lab/appealpublicationfold.py", "appeal_publication_fold", True),
    FoldMapEntry("rev0047", "tests/test_rev0047_appeal_publication_quench.py", "current_tests", True),
    FoldMapEntry("rev0047", "docs/490-rev0047-appealmesh-publicationquench-branchfold.md", "current_revision_doc", True),
    FoldMapEntry("rev0047", "docs/491-witness-appeal-mesh.md", "witnessappealmesh_doc", True),
    FoldMapEntry("rev0047", "docs/492-publication-ledger-boundary.md", "publicationledger_doc", True),
    FoldMapEntry("rev0047", "docs/493-bridge-quench-lane.md", "bridgequenchlane_doc", True),
    FoldMapEntry("rev0047", "docs/494-appealpublicationfold-audit-refactor.md", "appealpublicationfold_doc", True),
    FoldMapEntry("rev0047", "artifacts/branchlets/rev0046_public_bridge_branchlets/README.md", "folded_public_bridge_branchlets", True),
    FoldMapEntry("rev0047", "src/i2p_dht_lab/policyportfolio.py", "policy_portfolio_addendum", True),
    FoldMapEntry("rev0047", "src/i2p_dht_lab/publicationguard.py", "publication_guard_addendum", True),
    FoldMapEntry("rev0047", "src/i2p_dht_lab/publicationfold.py", "publicationfold_addendum", True),
    FoldMapEntry("rev0047", "tests/test_rev0047_policyportfolio_publicationguard.py", "policy_publication_tests", True),
    FoldMapEntry("rev0047", "docs/501-policy-portfolio-source-capture.md", "policyportfolio_doc", True),
    FoldMapEntry("rev0047", "docs/502-publication-guard-final-side-effect.md", "publicationguard_doc", True),
    FoldMapEntry("rev0047", "docs/503-branchlet-fold-rev0046-publication-chaos.md", "publication_branchlet_fold_doc", True),
    FoldMapEntry("rev0047", "docs/504-publicationfold-audit-refactor.md", "publicationfold_doc", True),
)


REV0048_CURRENT = (
    FoldMapEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge_shadow_publication_side_effect", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "audit_quorum_local_evidence", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress_gc_retention_boundary", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/shadowauditfold.py", "shadow_audit_fold", True),
    FoldMapEntry("rev0048", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "current_tests", True),
    FoldMapEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "current_revision_doc", True),
    FoldMapEntry("rev0048", "docs/506-bridge-shadow-publication-side-effect.md", "bridgeshadow_doc", True),
    FoldMapEntry("rev0048", "docs/507-audit-quorum-local-evidence.md", "auditquorum_doc", True),
    FoldMapEntry("rev0048", "docs/508-redress-gc-retention-boundary.md", "redressgc_doc", True),
    FoldMapEntry("rev0048", "docs/509-shadowauditfold-audit-refactor.md", "shadowauditfold_doc", True),
)

CURRENT_BY_REVISION = {"rev0031": REV0031_CURRENT, "rev0032": REV0032_CURRENT, "rev0033": REV0033_CURRENT, "rev0034": REV0034_CURRENT, "rev0035": REV0035_CURRENT, "rev0036": REV0036_CURRENT, "rev0037": REV0037_CURRENT, "rev0038": REV0038_CURRENT, "rev0039": REV0039_CURRENT, "rev0040": REV0040_CURRENT, "rev0041": REV0041_CURRENT, "rev0042": REV0042_CURRENT, "rev0043": REV0043_CURRENT, "rev0044": REV0044_CURRENT, "rev0045": REV0045_CURRENT, "rev0046": REV0046_CURRENT, "rev0047": REV0047_CURRENT, "rev0048": REV0048_CURRENT}
NEEDLES_BY_REVISION = {
    "rev0031": ("probeledger", "crisisroute", "sketchboundary", "foldmap"),
    "rev0032": ("scopeledger", "storedebt", "samtrace", "scopefold"),
    "rev0033": ("negotiationlane", "migrationlane", "safestart", "negotiationfold"),
    "rev0034": ("launchquorum", "metricsveil", "foldmerge", "persistjoin", "samprobe"),
    "rev0035": ("startmatrix", "routerharness", "telemetrydebt", "startfold"),
    "rev0036": ("servicecatalog", "loadsheath", "profilegc", "foldregistry", "servicefold"),
    "rev0037": ("serviceticket", "servicereceipt", "ticketfold", "serviceannounce", "ingressgate", "serviceguardfold"),
    "rev0038": ("servicecontinuity", "servicecontinuityfold", "catalogwire", "serviceprobe", "servicewithdrawal", "servicerelay", "serviceusegate", "handofflane", "receiptveil"),
    "rev0039": ("servicehealth", "servicedrain", "continuityjournal", "serviceopsfold"),
    "rev0040": ("operatorintent", "servicebreaker", "serviceexit", "operationsfold"),
    "rev0041": ("routerstop", "sessionresume", "exitjournal", "controlfold"),
    "rev0042": ("multiservice", "profilecooldown", "operatorkey", "announcementrepair", "controlplanefold"),
    "rev0043": ("keycompartment", "authoritysplit", "compartmentfold"),
    "rev0044": ("policyfirebreak", "authorityreceipt", "branchsealfold", "controlintent", "bridgefirewall"),
    "rev0045": ("bridgeepoch", "keyreceiptlane", "shadowfire", "bridgeepochfold"),
    "rev0046": ("moderationquarantine", "redresslane", "bridgeledger", "moderationfold"),
    "rev0047": ("witnessappealmesh", "publicationledger", "bridgequenchlane", "appealpublicationfold", "policyportfolio", "publicationguard", "publicationfold"),
    "rev0048": ("bridgeshadow", "auditquorum", "redressgc", "shadowauditfold"),
}


def default_fold_map(*, revision: str = "rev0033") -> tuple[FoldMapEntry, ...]:
    try:
        current = CURRENT_BY_REVISION[revision]
    except KeyError as exc:
        raise ValueError(f"unknown fold-map revision: {revision}") from exc
    return current + HISTORICAL_FOLDS


def audit_fold_map(root: str | Path, *, revision: str = "rev0033", artifact_stem: str | None = None, entries: Iterable[FoldMapEntry] | None = None) -> FoldMapReport:
    if revision not in CURRENT_BY_REVISION:
        raise ValueError(f"foldmap does not know revision {revision}")
    root_path = Path(root)
    artifact_stem = artifact_stem or root_path.name
    fold_entries = tuple(entries or default_fold_map(revision=revision))
    findings: list[FoldMapFinding] = []
    for entry in fold_entries:
        if not (root_path / entry.path).exists():
            findings.append(FoldMapFinding("error", "foldmap_missing_path", entry.path, f"missing {entry.revision} {entry.role}"))
    public_text = (root_path / "PUBLIC_SURFACE.json").read_text(encoding="utf-8") if (root_path / "PUBLIC_SURFACE.json").exists() else ""
    head_text = (root_path / "HEAD_REGISTRY.json").read_text(encoding="utf-8") if (root_path / "HEAD_REGISTRY.json").exists() else ""
    index_text = (root_path / "docs/00-index.md").read_text(encoding="utf-8") if (root_path / "docs/00-index.md").exists() else ""
    for needle in NEEDLES_BY_REVISION[revision]:
        if needle not in public_text:
            findings.append(FoldMapFinding("error", "public_surface_missing_current_needle", "PUBLIC_SURFACE.json", f"missing {needle}"))
        if needle not in head_text:
            findings.append(FoldMapFinding("error", "head_registry_missing_current_needle", "HEAD_REGISTRY.json", f"missing {needle}"))
        if needle not in index_text:
            findings.append(FoldMapFinding("error", "index_missing_current_needle", "docs/00-index.md", f"missing {needle}"))
    try:
        public = json.loads(public_text)
        current_version_path = root_path / "VERSION"
        current_version = current_version_path.read_text(encoding="utf-8").strip() if current_version_path.exists() else revision
        if revision == current_version and public.get("revision") != revision:
            findings.append(FoldMapFinding("error", "public_revision_drift", "PUBLIC_SURFACE.json", f"public surface revision is not {revision}"))
    except json.JSONDecodeError as exc:
        findings.append(FoldMapFinding("error", "public_json_invalid", "PUBLIC_SURFACE.json", str(exc)))
    try:
        ledger = audit_surface_ledger(root_path, entries_for_revision(revision))
        if ledger.error_count:
            findings.append(FoldMapFinding("error", "surface_ledger_errors", "src/i2p_dht_lab/surfaceledger.py", f"surface ledger does not pass for {revision}"))
    except Exception as exc:  # pragma: no cover - defensive audit surface
        findings.append(FoldMapFinding("error", "surface_ledger_exception", "src/i2p_dht_lab/surfaceledger.py", str(exc)))
    status = "pass" if not any(f.severity == "error" for f in findings) else "fail"
    digest = sha256(FOLD_MAP_DOMAIN + b":report:" + bencode({
        b"revision": revision,
        b"artifact": artifact_stem,
        b"entries": [entry.bvalue() for entry in fold_entries],
        b"status": status,
        b"findings": [finding.bvalue() for finding in findings],
    }))
    return FoldMapReport(revision, artifact_stem, status, sum(1 for e in fold_entries if e.current), sum(1 for e in fold_entries if not e.current), tuple(findings), digest)

# rev0048 current fold-map addendum.
REV0048_CURRENT = (
    FoldMapEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "audit_quorum_transparency_witness", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge_shadow_joined_side_effect", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress_gc_hard_negative_memory", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/bridgeauditfold.py", "bridgeauditfold_current_audit", True),
    FoldMapEntry("rev0048", "tests/test_rev0048_bridge_shadow_audit_redress.py", "bridge_shadow_audit_redress_tests", True),
    FoldMapEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "current_revision_doc", True),
    FoldMapEntry("rev0048", "docs/506-audit-quorum-transparency-witness.md", "auditquorum_doc", True),
    FoldMapEntry("rev0048", "docs/507-bridge-shadow-final-side-effect.md", "bridgeshadow_doc", True),
    FoldMapEntry("rev0048", "docs/508-redress-gc-hard-negative-memory.md", "redressgc_doc", True),
    FoldMapEntry("rev0048", "docs/509-bridgeauditfold-audit-refactor.md", "bridgeauditfold_doc", True),
)
CURRENT_BY_REVISION["rev0048"] = REV0048_CURRENT
NEEDLES_BY_REVISION["rev0048"] = ("auditquorum", "bridgeshadow", "redressgc", "bridgeauditfold")

# rev0048 final fold-map reconciliation: bridgeshadowfold is the active path;
# bridgeauditfold/shadowauditfold are preserved as branch history.
REV0048_CURRENT = (
    FoldMapEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge_shadow_public_side_effect", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "audit_quorum_local_receipts", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress_gc_retention_pressure", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/bridgeshadowfold.py", "bridgeshadowfold_current_audit", True),
    FoldMapEntry("rev0048", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "current_tests", True),
    FoldMapEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "current_revision_doc", True),
    FoldMapEntry("rev0048", "docs/506-bridge-shadow-public-side-effect.md", "bridgeshadow_doc", True),
    FoldMapEntry("rev0048", "docs/507-audit-quorum-local-receipts.md", "auditquorum_doc", True),
    FoldMapEntry("rev0048", "docs/508-redress-gc-retention-pressure.md", "redressgc_doc", True),
    FoldMapEntry("rev0048", "docs/509-bridgeshadowfold-audit-refactor.md", "bridgeshadowfold_doc", True),
    FoldMapEntry("rev0048", "artifacts/branchlets/rev0048_publicshadow_bridgeaudit/README.md", "folded_publicshadow_bridgeaudit_branchlet", False),
)
CURRENT_BY_REVISION["rev0048"] = REV0048_CURRENT
NEEDLES_BY_REVISION["rev0048"] = ("bridgeshadow", "auditquorum", "redressgc", "bridgeshadowfold")

# rev0048 governance-fold final reconciliation.
REV0048_CURRENT = (
    FoldMapEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge_shadow_side_effect_dryrun", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "audit_quorum_local_evidence", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress_gc_hard_negative_retention", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/bridgegovernancefold.py", "bridgegovernancefold_current_audit", True),
    FoldMapEntry("rev0048", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "current_tests", True),
    FoldMapEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "current_revision_doc", True),
    FoldMapEntry("rev0048", "docs/506-bridge-shadow-side-effect-dryrun.md", "bridgeshadow_doc", True),
    FoldMapEntry("rev0048", "docs/507-audit-quorum-is-local-evidence.md", "auditquorum_doc", True),
    FoldMapEntry("rev0048", "docs/508-redress-gc-hard-negative-retention.md", "redressgc_doc", True),
    FoldMapEntry("rev0048", "docs/509-bridgegovernancefold-audit-refactor.md", "bridgegovernancefold_doc", True),
    FoldMapEntry("rev0048", "artifacts/branchlets/rev0048_stale_doc_branchlet/README.md", "stale_doc_branchlet_preserved", False),
    FoldMapEntry("rev0048", "artifacts/branchlets/rev0048_stale_code_branchlet/README.md", "stale_code_branchlet_preserved", False),
)
CURRENT_BY_REVISION["rev0048"] = REV0048_CURRENT
NEEDLES_BY_REVISION["rev0048"] = ("bridgeshadow", "auditquorum", "redressgc", "bridgegovernancefold")

# rev0048 final bridge-governance fold-map override.
REV0048_CURRENT = (
    FoldMapEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge_shadow_dryrun_side_effect", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "audit_quorum_local_evidence", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress_gc_hard_negative_retention", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/bridgegovernancefold.py", "bridgegovernancefold_current_audit", True),
    FoldMapEntry("rev0048", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "bridge_governance_tests", True),
    FoldMapEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "current_revision_doc", True),
    FoldMapEntry("rev0048", "docs/506-bridge-shadow-side-effect-dryrun.md", "bridgeshadow_doc", True),
    FoldMapEntry("rev0048", "docs/507-audit-quorum-is-local-evidence.md", "auditquorum_doc", True),
    FoldMapEntry("rev0048", "docs/508-redress-gc-hard-negative-retention.md", "redressgc_doc", True),
    FoldMapEntry("rev0048", "docs/509-bridgegovernancefold-audit-refactor.md", "bridgegovernancefold_doc", True),
)
CURRENT_BY_REVISION["rev0048"] = REV0048_CURRENT
NEEDLES_BY_REVISION["rev0048"] = ("bridgeshadow", "auditquorum", "redressgc", "bridgegovernancefold")

# rev0048 canonical shadow/audit/redress fold override after branchlet reconciliation.
REV0048_CURRENT = (
    FoldMapEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge_shadow_publication_side_effect", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "audit_quorum_local_evidence", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress_gc_retention_boundary", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/shadowauditfold.py", "shadowauditfold_current_audit", True),
    FoldMapEntry("rev0048", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "bridge_shadow_audit_redress_tests", True),
    FoldMapEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "current_revision_doc", True),
    FoldMapEntry("rev0048", "docs/506-bridge-shadow-publication-side-effect.md", "bridgeshadow_doc", True),
    FoldMapEntry("rev0048", "docs/507-audit-quorum-local-evidence.md", "auditquorum_doc", True),
    FoldMapEntry("rev0048", "docs/508-redress-gc-retention-boundary.md", "redressgc_doc", True),
    FoldMapEntry("rev0048", "docs/509-shadowauditfold-audit-refactor.md", "shadowauditfold_doc", True),
)
CURRENT_BY_REVISION["rev0048"] = REV0048_CURRENT
NEEDLES_BY_REVISION["rev0048"] = ("bridgeshadow", "auditquorum", "redressgc", "shadowauditfold")

# rev0048 final shadowauditfold reconciliation: this supersedes the temporary
# bridgeauditfold/bridgeshadowfold branchlet overrides above.
REV0048_CURRENT = (
    FoldMapEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge_shadow_publication_side_effect", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "audit_quorum_local_evidence", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress_gc_retention_boundary", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/shadowauditfold.py", "shadowauditfold_current_audit", True),
    FoldMapEntry("rev0048", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "current_tests", True),
    FoldMapEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "current_revision_doc", True),
    FoldMapEntry("rev0048", "docs/506-bridge-shadow-publication-side-effect.md", "bridgeshadow_doc", True),
    FoldMapEntry("rev0048", "docs/507-audit-quorum-local-evidence.md", "auditquorum_doc", True),
    FoldMapEntry("rev0048", "docs/508-redress-gc-retention-boundary.md", "redressgc_doc", True),
    FoldMapEntry("rev0048", "docs/509-shadowauditfold-audit-refactor.md", "shadowauditfold_doc", True),
    FoldMapEntry("rev0048", "artifacts/branchlets/rev0048_publicshadow_bridgeaudit/README.md", "folded_publicshadow_bridgeaudit_branchlet", False),
)
CURRENT_BY_REVISION["rev0048"] = REV0048_CURRENT
NEEDLES_BY_REVISION["rev0048"] = ("bridgeshadow", "auditquorum", "redressgc", "shadowauditfold")


# rev0048 canonical bridge-governance fold-map override: final active rev0048
# path after shadowauditfold/bridgeaudit branchlets were folded into history.
REV0048_CURRENT = (
    FoldMapEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge_shadow_dryrun_side_effect", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "audit_quorum_local_evidence", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress_gc_hard_negative_retention", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/bridgegovernancefold.py", "bridgegovernancefold_current_audit", True),
    FoldMapEntry("rev0048", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "bridge_governance_tests", True),
    FoldMapEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "current_revision_doc", True),
    FoldMapEntry("rev0048", "docs/506-bridge-shadow-side-effect-dryrun.md", "bridgeshadow_doc", True),
    FoldMapEntry("rev0048", "docs/507-audit-quorum-is-local-evidence.md", "auditquorum_doc", True),
    FoldMapEntry("rev0048", "docs/508-redress-gc-hard-negative-retention.md", "redressgc_doc", True),
    FoldMapEntry("rev0048", "docs/509-bridgegovernancefold-audit-refactor.md", "bridgegovernancefold_doc", True),
    FoldMapEntry("rev0048", "artifacts/branchlets/rev0048_publicshadow_bridgeaudit/README.md", "folded_publicshadow_bridgeaudit_branchlet", False),
)
CURRENT_BY_REVISION["rev0048"] = REV0048_CURRENT
NEEDLES_BY_REVISION["rev0048"] = ("bridgeshadow", "auditquorum", "redressgc", "bridgegovernancefold")

# rev0048 FINAL canonical shadowauditfold override after branchlet reconciliation.
# Keep this last for rev0048: bridgegovernancefold/bridgeauditfold/bridgeshadowfold
# remain historical branchlet paths, not active revision needles.
REV0048_CURRENT = (
    FoldMapEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge_shadow_publication_side_effect", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "audit_quorum_local_evidence", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress_gc_retention_boundary", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/shadowauditfold.py", "shadowauditfold_current_audit", True),
    FoldMapEntry("rev0048", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "bridge_shadow_audit_redress_tests", True),
    FoldMapEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "current_revision_doc", True),
    FoldMapEntry("rev0048", "docs/506-bridge-shadow-publication-side-effect.md", "bridgeshadow_doc", True),
    FoldMapEntry("rev0048", "docs/507-audit-quorum-local-evidence.md", "auditquorum_doc", True),
    FoldMapEntry("rev0048", "docs/508-redress-gc-retention-boundary.md", "redressgc_doc", True),
    FoldMapEntry("rev0048", "docs/509-shadowauditfold-audit-refactor.md", "shadowauditfold_doc", True),
    FoldMapEntry("rev0048", "artifacts/branchlets/rev0048_publicshadow_bridgeaudit/README.md", "folded_publicshadow_bridgeaudit_branchlet", False),
    FoldMapEntry("rev0048", "artifacts/branchlets/rev0048_accidental_bridge_shadow_redressgc/test_rev0048_bridge_shadow_audit_redressgc.py", "folded_accidental_test_branchlet", False),
)
CURRENT_BY_REVISION["rev0048"] = REV0048_CURRENT
NEEDLES_BY_REVISION["rev0048"] = ("bridgeshadow", "auditquorum", "redressgc", "shadowauditfold")

# rev0048 absolute final shadowauditfold override after bridgegovernance branchlet quarantine.
REV0048_CURRENT = (
    FoldMapEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge_shadow_publication_side_effect", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "audit_quorum_local_evidence", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress_gc_retention_boundary", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/shadowauditfold.py", "shadowauditfold_current_audit", True),
    FoldMapEntry("rev0048", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "current_tests", True),
    FoldMapEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "current_revision_doc", True),
    FoldMapEntry("rev0048", "docs/506-bridge-shadow-publication-side-effect.md", "bridgeshadow_doc", True),
    FoldMapEntry("rev0048", "docs/507-audit-quorum-local-evidence.md", "auditquorum_doc", True),
    FoldMapEntry("rev0048", "docs/508-redress-gc-retention-boundary.md", "redressgc_doc", True),
    FoldMapEntry("rev0048", "docs/509-shadowauditfold-audit-refactor.md", "shadowauditfold_doc", True),
    FoldMapEntry("rev0048", "artifacts/branchlets/rev0048_publicshadow_bridgeaudit/README.md", "folded_publicshadow_branchlet", False),
    FoldMapEntry("rev0048", "artifacts/branchlets/rev0048_stale_doc_branchlet/README.md", "folded_stale_doc_branchlet", False),
    FoldMapEntry("rev0048", "artifacts/branchlets/rev0048_stale_code_branchlet/README.md", "folded_stale_code_branchlet", False),
)
CURRENT_BY_REVISION["rev0048"] = REV0048_CURRENT
NEEDLES_BY_REVISION["rev0048"] = ("bridgeshadow", "auditquorum", "redressgc", "shadowauditfold")


# rev0048 canonical bridge-governance fold-map override aligned with
# bridgegovernancefold.REV0048_PATHS after branchlet reconciliation.
REV0048_CURRENT = (
    FoldMapEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge_shadow_dryrun_side_effect", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "audit_quorum_local_evidence", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress_gc_hard_negative_retention", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/bridgegovernancefold.py", "bridgegovernancefold_current_audit", True),
    FoldMapEntry("rev0048", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "bridge_governance_tests", True),
    FoldMapEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "current_revision_doc", True),
    FoldMapEntry("rev0048", "docs/506-bridge-shadow-side-effect-dryrun.md", "bridgeshadow_doc", True),
    FoldMapEntry("rev0048", "docs/507-audit-quorum-is-local-evidence.md", "auditquorum_doc", True),
    FoldMapEntry("rev0048", "docs/508-redress-gc-hard-negative-retention.md", "redressgc_doc", True),
    FoldMapEntry("rev0048", "docs/509-bridgegovernancefold-audit-refactor.md", "bridgegovernancefold_doc", True),
    FoldMapEntry("rev0048", "artifacts/branchlets/rev0048_publicshadow_bridgeaudit/README.md", "folded_publicshadow_bridgeaudit_branchlet", False),
)
CURRENT_BY_REVISION["rev0048"] = REV0048_CURRENT
NEEDLES_BY_REVISION["rev0048"] = ("bridgeshadow", "auditquorum", "redressgc", "bridgegovernancefold")

# rev0048 final active-path repair after branchlet reconciliation.
REV0048_CURRENT = (
    FoldMapEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge_shadow_public_side_effect", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "audit_quorum_local_receipts", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress_gc_retention_pressure", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/bridgegovernancefold.py", "bridgegovernancefold_current_audit", True),
    FoldMapEntry("rev0048", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "current_tests", True),
    FoldMapEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "current_revision_doc", True),
    FoldMapEntry("rev0048", "docs/506-bridge-shadow-publication-side-effect.md", "bridgeshadow_doc", True),
    FoldMapEntry("rev0048", "docs/507-audit-quorum-local-evidence.md", "auditquorum_doc", True),
    FoldMapEntry("rev0048", "docs/508-redress-gc-retention-boundary.md", "redressgc_doc", True),
    FoldMapEntry("rev0048", "docs/509-shadowauditfold-audit-refactor.md", "bridgegovernancefold_doc", True),
    FoldMapEntry("rev0048", "artifacts/branchlets/rev0048_stale_doc_branchlet/README.md", "stale_doc_branchlet_preserved", False),
    FoldMapEntry("rev0048", "artifacts/branchlets/rev0048_stale_code_branchlet/README.md", "stale_code_branchlet_preserved", False),
)
CURRENT_BY_REVISION["rev0048"] = REV0048_CURRENT
NEEDLES_BY_REVISION["rev0048"] = ("bridgeshadow", "auditquorum", "redressgc", "bridgegovernancefold")

# rev0048 ABSOLUTE FINAL canonical bridge-governance override after stale
# shadowaudit/bridgeaudit branchlet path cleanup.
REV0048_CURRENT = (
    FoldMapEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge_shadow_dryrun_side_effect", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "audit_quorum_local_evidence", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress_gc_hard_negative_retention", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/bridgegovernancefold.py", "bridgegovernancefold_current_audit", True),
    FoldMapEntry("rev0048", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "bridge_governance_tests", True),
    FoldMapEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "current_revision_doc", True),
    FoldMapEntry("rev0048", "docs/506-bridge-shadow-side-effect-dryrun.md", "bridgeshadow_doc", True),
    FoldMapEntry("rev0048", "docs/507-audit-quorum-is-local-evidence.md", "auditquorum_doc", True),
    FoldMapEntry("rev0048", "docs/508-redress-gc-hard-negative-retention.md", "redressgc_doc", True),
    FoldMapEntry("rev0048", "docs/509-bridgegovernancefold-audit-refactor.md", "bridgegovernancefold_doc", True),
)
CURRENT_BY_REVISION["rev0048"] = REV0048_CURRENT
NEEDLES_BY_REVISION["rev0048"] = ("bridgeshadow", "auditquorum", "redressgc", "bridgegovernancefold")

# rev0048 TRUE LAST active-path override: shadowauditfold is canonical; bridgegovernancefold is historical branchlet glue.
REV0048_CURRENT = (
    FoldMapEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge_shadow_publication_side_effect", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "audit_quorum_local_evidence", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress_gc_retention_boundary", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/shadowauditfold.py", "shadowauditfold_current_audit", True),
    FoldMapEntry("rev0048", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "current_tests", True),
    FoldMapEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "current_revision_doc", True),
    FoldMapEntry("rev0048", "docs/506-bridge-shadow-publication-side-effect.md", "bridgeshadow_doc", True),
    FoldMapEntry("rev0048", "docs/507-audit-quorum-local-evidence.md", "auditquorum_doc", True),
    FoldMapEntry("rev0048", "docs/508-redress-gc-retention-boundary.md", "redressgc_doc", True),
    FoldMapEntry("rev0048", "docs/509-shadowauditfold-audit-refactor.md", "shadowauditfold_doc", True),
    FoldMapEntry("rev0048", "artifacts/branchlets/rev0048_publicshadow_bridgeaudit/README.md", "folded_publicshadow_bridgeaudit_branchlet", False),
    FoldMapEntry("rev0048", "artifacts/branchlets/rev0048_stale_doc_branchlet/README.md", "folded_stale_doc_branchlet", False),
    FoldMapEntry("rev0048", "artifacts/branchlets/rev0048_stale_code_branchlet/README.md", "folded_stale_code_branchlet", False),
)
CURRENT_BY_REVISION["rev0048"] = REV0048_CURRENT
NEEDLES_BY_REVISION["rev0048"] = ("bridgeshadow", "auditquorum", "redressgc", "shadowauditfold")

# rev0048 FINAL-FINAL shadowauditfold override: appended after all historical branchlet overrides.
REV0048_CURRENT = (
    FoldMapEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge_shadow_publication_side_effect", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "audit_quorum_local_evidence", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress_gc_retention_boundary", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/shadowauditfold.py", "shadowauditfold_current_audit", True),
    FoldMapEntry("rev0048", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "current_tests", True),
    FoldMapEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "current_revision_doc", True),
    FoldMapEntry("rev0048", "docs/506-bridge-shadow-publication-side-effect.md", "bridgeshadow_doc", True),
    FoldMapEntry("rev0048", "docs/507-audit-quorum-local-evidence.md", "auditquorum_doc", True),
    FoldMapEntry("rev0048", "docs/508-redress-gc-retention-boundary.md", "redressgc_doc", True),
    FoldMapEntry("rev0048", "docs/509-shadowauditfold-audit-refactor.md", "shadowauditfold_doc", True),
    FoldMapEntry("rev0048", "artifacts/branchlets/rev0048_publicshadow_bridgeaudit/README.md", "folded_publicshadow_branchlet", False),
    FoldMapEntry("rev0048", "artifacts/branchlets/rev0048_stale_doc_branchlet/README.md", "folded_stale_doc_branchlet", False),
    FoldMapEntry("rev0048", "artifacts/branchlets/rev0048_stale_code_branchlet/README.md", "folded_stale_code_branchlet", False),
)
CURRENT_BY_REVISION["rev0048"] = REV0048_CURRENT
NEEDLES_BY_REVISION["rev0048"] = ("bridgeshadow", "auditquorum", "redressgc", "shadowauditfold")

# rev0048 TRUE FINAL shadowauditfold override after bridgegovernance branchlet quarantine.
REV0048_CURRENT = (
    FoldMapEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge_shadow_publication_side_effect", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "audit_quorum_local_evidence", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress_gc_retention_boundary", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/shadowauditfold.py", "shadowauditfold_current_audit", True),
    FoldMapEntry("rev0048", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "current_bridge_shadow_audit_redress_tests", True),
    FoldMapEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "current_revision_doc", True),
    FoldMapEntry("rev0048", "docs/506-bridge-shadow-publication-side-effect.md", "bridgeshadow_doc", True),
    FoldMapEntry("rev0048", "docs/507-audit-quorum-local-evidence.md", "auditquorum_doc", True),
    FoldMapEntry("rev0048", "docs/508-redress-gc-retention-boundary.md", "redressgc_doc", True),
    FoldMapEntry("rev0048", "docs/509-shadowauditfold-audit-refactor.md", "shadowauditfold_doc", True),
    FoldMapEntry("rev0048", "artifacts/branchlets/rev0048_publicshadow_bridgeaudit/README.md", "folded_publicshadow_bridgeaudit_branchlet", False),
    FoldMapEntry("rev0048", "artifacts/branchlets/rev0048_stale_doc_branchlet/README.md", "folded_stale_doc_branchlet", False),
    FoldMapEntry("rev0048", "artifacts/branchlets/rev0048_stale_code_branchlet/README.md", "folded_stale_code_branchlet", False),
)
CURRENT_BY_REVISION["rev0048"] = REV0048_CURRENT
NEEDLES_BY_REVISION["rev0048"] = ("bridgeshadow", "auditquorum", "redressgc", "shadowauditfold")

# rev0048 ACTUAL FINAL bridgegovernancefold override. This line intentionally
# supersedes stale shadowauditfold branchlet overrides left above for history.
REV0048_CURRENT = (
    FoldMapEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge_shadow_dryrun_side_effect", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "audit_quorum_local_evidence", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress_gc_hard_negative_retention", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/bridgegovernancefold.py", "bridgegovernancefold_current_audit", True),
    FoldMapEntry("rev0048", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "bridge_governance_tests", True),
    FoldMapEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "current_revision_doc", True),
    FoldMapEntry("rev0048", "docs/506-bridge-shadow-side-effect-dryrun.md", "bridgeshadow_doc", True),
    FoldMapEntry("rev0048", "docs/507-audit-quorum-is-local-evidence.md", "auditquorum_doc", True),
    FoldMapEntry("rev0048", "docs/508-redress-gc-hard-negative-retention.md", "redressgc_doc", True),
    FoldMapEntry("rev0048", "docs/509-bridgegovernancefold-audit-refactor.md", "bridgegovernancefold_doc", True),
)
CURRENT_BY_REVISION["rev0048"] = REV0048_CURRENT
NEEDLES_BY_REVISION["rev0048"] = ("bridgeshadow", "auditquorum", "redressgc", "bridgegovernancefold")

# rev0048 ABSOLUTE FINAL ACTIVE override: shadowauditfold chosen as active path; bridgegovernancefold kept as branchlet history.
REV0048_CURRENT = (
    FoldMapEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge_shadow_publication_side_effect", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "audit_quorum_local_evidence", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress_gc_retention_boundary", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/shadowauditfold.py", "shadowauditfold_current_audit", True),
    FoldMapEntry("rev0048", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "current_tests", True),
    FoldMapEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "current_revision_doc", True),
    FoldMapEntry("rev0048", "docs/506-bridge-shadow-publication-side-effect.md", "bridgeshadow_doc", True),
    FoldMapEntry("rev0048", "docs/507-audit-quorum-local-evidence.md", "auditquorum_doc", True),
    FoldMapEntry("rev0048", "docs/508-redress-gc-retention-boundary.md", "redressgc_doc", True),
    FoldMapEntry("rev0048", "docs/509-shadowauditfold-audit-refactor.md", "shadowauditfold_doc", True),
)
CURRENT_BY_REVISION["rev0048"] = REV0048_CURRENT
NEEDLES_BY_REVISION["rev0048"] = ("bridgeshadow", "auditquorum", "redressgc", "shadowauditfold")

# rev0048 final bridgegovernancefold fold-map override after JSON/doc repair.
REV0048_CURRENT = (
    FoldMapEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge shadow public side-effect dry-run boundary"),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "audit quorum local evidence for public bridge shadows"),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress/evidence GC retention boundary"),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/bridgegovernancefold.py", "bridgegovernancefold current-path audit"),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/shadowauditfold.py", "shadowauditfold compatibility audit retained as history"),
    FoldMapEntry("rev0048", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "current rev0048 regression tests"),
    FoldMapEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "rev0048 current overview"),
    FoldMapEntry("rev0048", "docs/506-bridge-shadow-publication-side-effect.md", "bridge shadow doc"),
    FoldMapEntry("rev0048", "docs/507-audit-quorum-local-evidence.md", "audit quorum doc"),
    FoldMapEntry("rev0048", "docs/508-redress-gc-retention-boundary.md", "redress GC doc"),
    FoldMapEntry("rev0048", "docs/509-shadowauditfold-audit-refactor.md", "bridgegovernancefold/shadowauditfold audit doc"),
)
CURRENT_BY_REVISION["rev0048"] = REV0048_CURRENT
NEEDLES_BY_REVISION["rev0048"] = ("bridgeshadow", "auditquorum", "redressgc", "bridgegovernancefold")

# rev0048 TRUE FINAL shadowauditfold override after bridgegovernance branchlet quarantine.
REV0048_CURRENT = (
    FoldMapEntry("rev0048", "src/i2p_dht_lab/bridgeshadow.py", "bridge_shadow_publication_side_effect", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/auditquorum.py", "audit_quorum_local_evidence", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/redressgc.py", "redress_gc_retention_boundary", True),
    FoldMapEntry("rev0048", "src/i2p_dht_lab/shadowauditfold.py", "shadowauditfold_current_audit", True),
    FoldMapEntry("rev0048", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "current_bridge_shadow_audit_redress_tests", True),
    FoldMapEntry("rev0048", "docs/505-rev0048-bridgeshadow-auditquorum-redressgc.md", "current_revision_doc", True),
    FoldMapEntry("rev0048", "docs/506-bridge-shadow-publication-side-effect.md", "bridgeshadow_doc", True),
    FoldMapEntry("rev0048", "docs/507-audit-quorum-local-evidence.md", "auditquorum_doc", True),
    FoldMapEntry("rev0048", "docs/508-redress-gc-retention-boundary.md", "redressgc_doc", True),
    FoldMapEntry("rev0048", "docs/509-shadowauditfold-audit-refactor.md", "shadowauditfold_doc", True),
    FoldMapEntry("rev0048", "artifacts/branchlets/rev0048_publicshadow_bridgeaudit/README.md", "folded_publicshadow_bridgeaudit_branchlet", False),
    FoldMapEntry("rev0048", "artifacts/branchlets/rev0048_stale_doc_branchlet/README.md", "folded_stale_doc_branchlet", False),
    FoldMapEntry("rev0048", "artifacts/branchlets/rev0048_stale_code_branchlet/README.md", "folded_stale_code_branchlet", False),
)
CURRENT_BY_REVISION["rev0048"] = REV0048_CURRENT
NEEDLES_BY_REVISION["rev0048"] = ("bridgeshadow", "auditquorum", "redressgc", "shadowauditfold")

# rev0049 active publish dry-run / witness compaction / scope-journal fold map.
REV0049_CURRENT = (
    FoldMapEntry("rev0049", "src/i2p_dht_lab/publishdryrun.py", "publish_dryrun_side_effect_boundary", True),
    FoldMapEntry("rev0049", "src/i2p_dht_lab/witnesscompact.py", "witness_compaction_memory_pressure", True),
    FoldMapEntry("rev0049", "src/i2p_dht_lab/scopejournal.py", "scope_journal_restart_boundary", True),
    FoldMapEntry("rev0049", "src/i2p_dht_lab/publishfold.py", "publishfold_current_audit", True),
    FoldMapEntry("rev0049", "tests/test_rev0049_publishdryrun_witnesscompact_scopejournal.py", "current_tests", True),
    FoldMapEntry("rev0049", "docs/510-rev0049-publishdryrun-witnesscompact-scopejournal.md", "current_revision_doc", True),
    FoldMapEntry("rev0049", "docs/511-publish-dryrun-side-effect-boundary.md", "publishdryrun_doc", True),
    FoldMapEntry("rev0049", "docs/512-witness-compaction-memory-pressure.md", "witnesscompact_doc", True),
    FoldMapEntry("rev0049", "docs/513-scope-journal-restart-boundary.md", "scopejournal_doc", True),
    FoldMapEntry("rev0049", "docs/514-publishfold-audit-refactor.md", "publishfold_doc", True),
)
CURRENT_BY_REVISION["rev0049"] = REV0049_CURRENT
NEEDLES_BY_REVISION["rev0049"] = ("publishdryrun", "witnesscompact", "scopejournal", "publishfold")

# rev0049 public outbox / audit-gap fold map.
REV0049_CURRENT = (
    FoldMapEntry("rev0049", "src/i2p_dht_lab/publicoutbox.py", "public_outbox_side_effect_staging", True),
    FoldMapEntry("rev0049", "src/i2p_dht_lab/auditgap.py", "audit_gap_repair_planning", True),
    FoldMapEntry("rev0049", "src/i2p_dht_lab/outboxfold.py", "outboxfold_current_audit", True),
    FoldMapEntry("rev0049", "tests/test_rev0049_publicoutbox_auditgap_fold.py", "current_tests", True),
    FoldMapEntry("rev0049", "docs/514-rev0049-outboxlane-auditgap-fold.md", "current_revision_doc", True),
    FoldMapEntry("rev0049", "docs/515-public-outbox-side-effect-staging.md", "publicoutbox_doc", True),
    FoldMapEntry("rev0049", "docs/516-audit-gap-repair-planning.md", "auditgap_doc", True),
    FoldMapEntry("rev0049", "docs/517-outboxfold-audit-refactor.md", "outboxfold_doc", True),
)
CURRENT_BY_REVISION["rev0049"] = REV0049_CURRENT
NEEDLES_BY_REVISION["rev0049"] = ("publicoutbox", "auditgap", "outboxfold")

# rev0049 integrated current fold-map override: both public-edge dry-run and
# public outbox/audit-gap branchlets are active, auditcompact is pinned as the
# additional refute/fork-preserving compaction lane.
REV0049_CURRENT = (
    FoldMapEntry("rev0049", "src/i2p_dht_lab/publishdryrun.py", "publish_dry_run_public_edge", True),
    FoldMapEntry("rev0049", "src/i2p_dht_lab/witnesscompact.py", "witness_compaction_hard_evidence", True),
    FoldMapEntry("rev0049", "src/i2p_dht_lab/scopejournal.py", "scope_journal_restart_memory", True),
    FoldMapEntry("rev0049", "src/i2p_dht_lab/publishdryrunfold.py", "publishdryrunfold_current_audit", True),
    FoldMapEntry("rev0049", "src/i2p_dht_lab/publicoutbox.py", "public_outbox_side_effect_staging", True),
    FoldMapEntry("rev0049", "src/i2p_dht_lab/auditgap.py", "audit_gap_repair_planning", True),
    FoldMapEntry("rev0049", "src/i2p_dht_lab/outboxfold.py", "outboxfold_current_audit", True),
    FoldMapEntry("rev0049", "src/i2p_dht_lab/auditcompact.py", "audit_compact_refute_fork_preservation", True),
    FoldMapEntry("rev0049", "tests/test_rev0049_publishdryrun_witnesscompact_scopejournal.py", "publishdryrun_tests", True),
    FoldMapEntry("rev0049", "tests/test_rev0049_publicoutbox_auditgap_fold.py", "outbox_tests", True),
    FoldMapEntry("rev0049", "tests/test_rev0049_publishdryrun_auditcompact_scopejournal.py", "auditcompact_tests", True),
    FoldMapEntry("rev0049", "docs/510-rev0049-publishdryrun-witnesscompact-scopejournal.md", "current_revision_doc", True),
    FoldMapEntry("rev0049", "docs/515-publish-dry-run-public-edge.md", "publishdryrun_doc", True),
    FoldMapEntry("rev0049", "docs/516-witness-compact-hard-evidence.md", "witnesscompact_doc", True),
    FoldMapEntry("rev0049", "docs/517-scope-journal-restart-memory.md", "scopejournal_doc", True),
    FoldMapEntry("rev0049", "docs/518-publishdryrunfold-audit-refactor.md", "publishdryrunfold_doc", True),
    FoldMapEntry("rev0049", "docs/515-public-outbox-side-effect-staging.md", "publicoutbox_doc", True),
    FoldMapEntry("rev0049", "docs/516-audit-gap-repair-planning.md", "auditgap_doc", True),
    FoldMapEntry("rev0049", "docs/517-outboxfold-audit-refactor.md", "outboxfold_doc", True),
    FoldMapEntry("rev0049", "docs/523-auditcompact-refute-fork-preservation.md", "auditcompact_doc", True),
)
CURRENT_BY_REVISION["rev0049"] = REV0049_CURRENT
NEEDLES_BY_REVISION["rev0049"] = ("publishdryrun", "witnesscompact", "scopejournal", "publishdryrunfold", "publicoutbox", "auditgap", "outboxfold", "auditcompact")

# rev0050 outbox-drain / SAM-canary / compact-join fold map.
REV0050_CURRENT = (
    FoldMapEntry("rev0050", "src/i2p_dht_lab/outboxdrain.py", "outbox_drain_commit_receipts", True),
    FoldMapEntry("rev0050", "src/i2p_dht_lab/samcanary.py", "sam_canary_before_live_send", True),
    FoldMapEntry("rev0050", "src/i2p_dht_lab/compactjoin.py", "compact_join_negative_evidence", True),
    FoldMapEntry("rev0050", "src/i2p_dht_lab/drainfold.py", "drainfold_current_audit", True),
    FoldMapEntry("rev0050", "tests/test_rev0050_outboxdrain_samcanary_compactjoin.py", "current_tests", True),
    FoldMapEntry("rev0050", "docs/524-rev0050-outboxdrain-samcanary-compactjoin.md", "current_revision_doc", True),
    FoldMapEntry("rev0050", "docs/525-outbox-drain-commit-receipts.md", "outboxdrain_doc", True),
    FoldMapEntry("rev0050", "docs/526-sam-canary-before-live-send.md", "samcanary_doc", True),
    FoldMapEntry("rev0050", "docs/527-compact-join-negative-evidence.md", "compactjoin_doc", True),
    FoldMapEntry("rev0050", "docs/528-drainfold-audit-refactor.md", "drainfold_doc", True),
)
CURRENT_BY_REVISION["rev0050"] = REV0050_CURRENT
NEEDLES_BY_REVISION["rev0050"] = ("outboxdrain", "samcanary", "compactjoin", "drainfold")

# rev0051 send-valve / effect-ledger fold merge registry.
REV0051_CURRENT = (
    FoldMapEntry("rev0051", "src/i2p_dht_lab/commitbarrier.py", "folded_commit_barrier_branchlet", True),
    FoldMapEntry("rev0051", "src/i2p_dht_lab/sendvalve.py", "send_valve_join_before_live_send", True),
    FoldMapEntry("rev0051", "src/i2p_dht_lab/effectledger.py", "public_effect_idempotency_memory", True),
    FoldMapEntry("rev0051", "src/i2p_dht_lab/sendfold.py", "rev0051_sendfold_audit", True),
    FoldMapEntry("rev0051", "tests/test_rev0051_sendvalve_effectledger_foldmerge.py", "current_tests", True),
    FoldMapEntry("rev0051", "docs/534-rev0051-sendvalve-effectledger-foldmerge.md", "current_revision_doc", True),
    FoldMapEntry("rev0051", "docs/535-send-valve-joined-boundary.md", "sendvalve_doc", True),
    FoldMapEntry("rev0051", "docs/536-effect-ledger-idempotent-memory.md", "effectledger_doc", True),
    FoldMapEntry("rev0051", "docs/537-foldmerge-commitbarrier-branchlet.md", "branchlet_fold_doc", True),
    FoldMapEntry("rev0051", "docs/538-sendfold-audit-refactor.md", "sendfold_doc", True),
    FoldMapEntry("rev0051", "artifacts/branchlets/rev0050_commitbarrier_publicedgefold/publicedgefold.py", "folded_rev0050_publicedge_branchlet", False),
)
CURRENT_BY_REVISION["rev0051"] = REV0051_CURRENT
NEEDLES_BY_REVISION["rev0051"] = ("commitbarrier", "sendvalve", "effectledger", "sendfold")

# rev0051 ingress-drain / router-canary / red-team fold map.
REV0051_CURRENT = (
    FoldMapEntry("rev0051", "src/i2p_dht_lab/routercanary.py", "router_canary_public_edge_boundary", True),
    FoldMapEntry("rev0051", "src/i2p_dht_lab/ingressdrain.py", "ingress_drain_public_bridge_boundary", True),
    FoldMapEntry("rev0051", "src/i2p_dht_lab/redteamfold.py", "redteamfold_current_audit", True),
    FoldMapEntry("rev0051", "tests/test_rev0051_ingressdrain_routercanary_redteamfold.py", "current_tests", True),
    FoldMapEntry("rev0051", "docs/534-rev0051-ingressdrain-routercanary-redteamfold.md", "current_revision_doc", True),
    FoldMapEntry("rev0051", "docs/535-router-canary-public-edge.md", "routercanary_doc", True),
    FoldMapEntry("rev0051", "docs/536-ingress-drain-public-bridge.md", "ingressdrain_doc", True),
    FoldMapEntry("rev0051", "docs/537-redteamfold-audit-refactor.md", "redteamfold_doc", True),
)
CURRENT_BY_REVISION["rev0051"] = REV0051_CURRENT
NEEDLES_BY_REVISION["rev0051"] = ("routercanary", "ingressdrain", "redteamfold")

# rev0052 live-adapter / backpressure / profile-edge fold map.
REV0052_CURRENT = (
    FoldMapEntry("rev0052", "src/i2p_dht_lab/liveadapter.py", "live_adapter_no_network_boundary", True),
    FoldMapEntry("rev0052", "src/i2p_dht_lab/backpressuremesh.py", "shared_public_edge_backpressure", True),
    FoldMapEntry("rev0052", "src/i2p_dht_lab/profileedge.py", "profile_edge_joined_boundary", True),
    FoldMapEntry("rev0052", "src/i2p_dht_lab/edgefold.py", "edgefold_current_audit", True),
    FoldMapEntry("rev0052", "tests/test_rev0052_liveadapter_backpressure_profileedge.py", "current_tests", True),
    FoldMapEntry("rev0052", "docs/548-rev0052-liveadapter-backpressure-profileedge.md", "current_revision_doc", True),
    FoldMapEntry("rev0052", "docs/549-live-adapter-no-network-boundary.md", "liveadapter_doc", True),
    FoldMapEntry("rev0052", "docs/550-backpressure-mesh-shared-edge.md", "backpressuremesh_doc", True),
    FoldMapEntry("rev0052", "docs/551-profile-edge-joined-boundary.md", "profileedge_doc", True),
    FoldMapEntry("rev0052", "docs/552-edgefold-audit-refactor.md", "edgefold_doc", True),
)
CURRENT_BY_REVISION["rev0052"] = REV0052_CURRENT
NEEDLES_BY_REVISION["rev0052"] = ("liveadapter", "backpressuremesh", "profileedge", "edgefold")

# rev0053 handler-capsule / side-effect journal / adapter-fuzz fold map.
REV0053_CURRENT = (
    FoldMapEntry("rev0053", "src/i2p_dht_lab/handlercapsule.py", "handler_capsule_boundary", True),
    FoldMapEntry("rev0053", "src/i2p_dht_lab/sideeffectjournal.py", "side_effect_journal_boundary", True),
    FoldMapEntry("rev0053", "src/i2p_dht_lab/adapterfuzz.py", "adapter_fuzz_coverage", True),
    FoldMapEntry("rev0053", "src/i2p_dht_lab/handlerfold.py", "handlerfold_current_audit", True),
    FoldMapEntry("rev0053", "tests/test_rev0053_handlercapsule_sideeffect_adapterfuzz.py", "current_tests", True),
    FoldMapEntry("rev0053", "docs/559-rev0053-handlercapsule-sideeffectjournal-adapterfuzz.md", "current_revision_doc", True),
    FoldMapEntry("rev0053", "docs/560-handler-capsule-boundary.md", "handlercapsule_doc", True),
    FoldMapEntry("rev0053", "docs/561-side-effect-journal-boundary.md", "sideeffectjournal_doc", True),
    FoldMapEntry("rev0053", "docs/562-adapter-fuzz-coverage.md", "adapterfuzz_doc", True),
    FoldMapEntry("rev0053", "docs/563-handlerfold-audit-refactor.md", "handlerfold_doc", True),
)
CURRENT_BY_REVISION["rev0053"] = REV0053_CURRENT
NEEDLES_BY_REVISION["rev0053"] = ("handlercapsule", "sideeffectjournal", "adapterfuzz", "handlerfold")

# rev0054 replay-lab / handler-quench / fuzz-ledger fold map.
REV0054_CURRENT = (
    FoldMapEntry("rev0054", "src/i2p_dht_lab/handlerreplay.py", "handler_replay_restart_boundary", True),
    FoldMapEntry("rev0054", "src/i2p_dht_lab/handlerquench.py", "handler_quench_cooldown", True),
    FoldMapEntry("rev0054", "src/i2p_dht_lab/fuzzledger.py", "persistent_adapter_fuzz_ledger", True),
    FoldMapEntry("rev0054", "src/i2p_dht_lab/replayfold.py", "replayfold_current_audit", True),
    FoldMapEntry("rev0054", "tests/test_rev0054_replay_quench_fuzzledger.py", "current_tests", True),
    FoldMapEntry("rev0054", "docs/579-rev0054-replaylab-handlerquench-fuzzledger.md", "current_revision_doc", True),
    FoldMapEntry("rev0054", "docs/570-handler-replay-restart-boundary.md", "handlerreplay_doc", True),
    FoldMapEntry("rev0054", "docs/571-handler-quench-cooldown.md", "handlerquench_doc", True),
    FoldMapEntry("rev0054", "docs/572-fuzz-ledger-persistent-coverage.md", "fuzzledger_doc", True),
    FoldMapEntry("rev0054", "docs/573-replayfold-audit-refactor.md", "replayfold_doc", True),
)
CURRENT_BY_REVISION["rev0054"] = REV0054_CURRENT
NEEDLES_BY_REVISION["rev0054"] = ("handlerreplay", "handlerquench", "fuzzledger", "replayfold")

# rev0055 restart-chaos / effect-seal / fuzz-shrink fold map.
REV0055_CURRENT = (
    FoldMapEntry("rev0055", "src/i2p_dht_lab/restartchaos.py", "restart_chaos_crash_cut_boundary", True),
    FoldMapEntry("rev0055", "src/i2p_dht_lab/effectseal.py", "effect_seal_joined_boundary", True),
    FoldMapEntry("rev0055", "src/i2p_dht_lab/fuzzshrink.py", "fuzz_shrink_coverage_compaction", True),
    FoldMapEntry("rev0055", "src/i2p_dht_lab/restartfold.py", "restartfold_current_audit", True),
    FoldMapEntry("rev0055", "tests/test_rev0055_restartchaos_effectseal_fuzzshrink.py", "current_tests", True),
    FoldMapEntry("rev0055", "docs/580-rev0055-restartchaos-effectseal-fuzzshrink.md", "current_revision_doc", True),
    FoldMapEntry("rev0055", "docs/581-restart-chaos-crash-cut-boundary.md", "restartchaos_doc", True),
    FoldMapEntry("rev0055", "docs/582-effect-seal-joined-boundary.md", "effectseal_doc", True),
    FoldMapEntry("rev0055", "docs/583-fuzz-shrink-coverage-compaction.md", "fuzzshrink_doc", True),
    FoldMapEntry("rev0055", "docs/584-restartfold-audit-refactor.md", "restartfold_doc", True),
)
CURRENT_BY_REVISION["rev0055"] = REV0055_CURRENT
NEEDLES_BY_REVISION["rev0055"] = ("restartchaos", "effectseal", "fuzzshrink", "restartfold")

# rev0056 recovery-mesh / safe-cleanup / chaos-budget fold map.
REV0056_CURRENT = (
    FoldMapEntry("rev0056", "src/i2p_dht_lab/recoverymesh.py", "recovery_mesh_after_effect_seal", True),
    FoldMapEntry("rev0056", "src/i2p_dht_lab/safecleanup.py", "safe_cleanup_hard_negative_boundary", True),
    FoldMapEntry("rev0056", "src/i2p_dht_lab/chaosbudget.py", "chaos_budget_post_effect_pressure", True),
    FoldMapEntry("rev0056", "src/i2p_dht_lab/recoveryfold.py", "recoveryfold_current_audit", True),
    FoldMapEntry("rev0056", "tests/test_rev0056_recovery_cleanup_chaosbudget.py", "current_tests", True),
    FoldMapEntry("rev0056", "docs/590-rev0056-recoverymesh-safecleanup-chaosbudget.md", "current_revision_doc", True),
    FoldMapEntry("rev0056", "docs/591-recovery-mesh-after-effect-seal.md", "recoverymesh_doc", True),
    FoldMapEntry("rev0056", "docs/592-safe-cleanup-hard-negative-boundary.md", "safecleanup_doc", True),
    FoldMapEntry("rev0056", "docs/593-chaos-budget-post-effect-pressure.md", "chaosbudget_doc", True),
    FoldMapEntry("rev0056", "docs/594-recoveryfold-audit-refactor.md", "recoveryfold_doc", True),
)
CURRENT_BY_REVISION["rev0056"] = REV0056_CURRENT
NEEDLES_BY_REVISION["rev0056"] = ("recoverymesh", "safecleanup", "chaosbudget", "recoveryfold")

# rev0056 recovery mesh / safe cleanup / chaos budget fold map.
REV0056_CURRENT = (
    FoldMapEntry("rev0056", "src/i2p_dht_lab/sealreplay.py", "effect_seal_restart_generation_replay", True),
    FoldMapEntry("rev0056", "src/i2p_dht_lab/corpuswitness.py", "fuzz_shrink_corpus_witnesses", True),
    FoldMapEntry("rev0056", "src/i2p_dht_lab/recoverymesh.py", "post_effect_recovery_mesh", True),
    FoldMapEntry("rev0056", "src/i2p_dht_lab/safecleanup.py", "hard_negative_preserving_cleanup", True),
    FoldMapEntry("rev0056", "src/i2p_dht_lab/chaosbudget.py", "post_effect_chaos_budget", True),
    FoldMapEntry("rev0056", "src/i2p_dht_lab/recoveryfold.py", "recoveryfold_current_audit", True),
    FoldMapEntry("rev0056", "tests/test_rev0056_recovery_cleanup_chaosbudget.py", "current_tests", True),
    FoldMapEntry("rev0056", "docs/590-rev0056-recoverymesh-safecleanup-chaosbudget.md", "current_revision_doc", True),
    FoldMapEntry("rev0056", "docs/591-recovery-mesh-after-effect-seal.md", "recoverymesh_doc", True),
    FoldMapEntry("rev0056", "docs/592-safe-cleanup-hard-negative-boundary.md", "safecleanup_doc", True),
    FoldMapEntry("rev0056", "docs/593-chaos-budget-post-effect-pressure.md", "chaosbudget_doc", True),
    FoldMapEntry("rev0056", "docs/594-recoveryfold-audit-refactor.md", "recoveryfold_doc", True),
)
CURRENT_BY_REVISION["rev0056"] = REV0056_CURRENT
NEEDLES_BY_REVISION["rev0056"] = ("sealreplay", "corpuswitness", "recoverymesh", "safecleanup", "chaosbudget", "recoveryfold")

# rev0057 dead-letter / retry-quorum / effect-reconcile fold map.
REV0057_CURRENT = (
    FoldMapEntry("rev0057", "src/i2p_dht_lab/deadletter.py", "prepared_only_dead_letter_memory", True),
    FoldMapEntry("rev0057", "src/i2p_dht_lab/retryquorum.py", "retry_quorum_after_recovery_watch", True),
    FoldMapEntry("rev0057", "src/i2p_dht_lab/effectreconcile.py", "effect_reconcile_join", True),
    FoldMapEntry("rev0057", "src/i2p_dht_lab/reconcilefold.py", "reconcilefold_current_audit", True),
    FoldMapEntry("rev0057", "tests/test_rev0057_deadletter_retry_reconcile.py", "current_tests", True),
    FoldMapEntry("rev0057", "docs/600-rev0057-deadletter-retryquorum-effectreconcile.md", "current_revision_doc", True),
    FoldMapEntry("rev0057", "docs/601-dead-letter-lane-prepared-only.md", "deadletter_doc", True),
    FoldMapEntry("rev0057", "docs/602-retry-quorum-after-recovery-watch.md", "retryquorum_doc", True),
    FoldMapEntry("rev0057", "docs/603-effect-reconcile-boundary.md", "effectreconcile_doc", True),
    FoldMapEntry("rev0057", "docs/604-reconcilefold-audit-refactor.md", "reconcilefold_doc", True),
)
CURRENT_BY_REVISION["rev0057"] = REV0057_CURRENT
NEEDLES_BY_REVISION["rev0057"] = ("deadletter", "retryquorum", "effectreconcile", "reconcilefold")

# rev0058 finality-ledger / retry-escrow / prune-guard fold map.
REV0058_CURRENT = (
    FoldMapEntry("rev0058", "src/i2p_dht_lab/finalityledger.py", "finality_ledger_after_reconcile", True),
    FoldMapEntry("rev0058", "src/i2p_dht_lab/retryescrow.py", "retry_escrow_deadletter_carry", True),
    FoldMapEntry("rev0058", "src/i2p_dht_lab/pruneguard.py", "prune_guard_terminal_pending", True),
    FoldMapEntry("rev0058", "src/i2p_dht_lab/finalityfold.py", "finalityfold_current_audit", True),
    FoldMapEntry("rev0058", "tests/test_rev0058_finality_retryescrow_pruneguard.py", "current_tests", True),
    FoldMapEntry("rev0058", "docs/610-rev0058-finalityledger-retryescrow-pruneguard.md", "current_revision_doc", True),
    FoldMapEntry("rev0058", "docs/611-finality-ledger-after-reconcile.md", "finalityledger_doc", True),
    FoldMapEntry("rev0058", "docs/612-retry-escrow-deadletter-carry.md", "retryescrow_doc", True),
    FoldMapEntry("rev0058", "docs/613-prune-guard-terminal-pending.md", "pruneguard_doc", True),
    FoldMapEntry("rev0058", "docs/614-finalityfold-audit-refactor.md", "finalityfold_doc", True),
)
CURRENT_BY_REVISION["rev0058"] = REV0058_CURRENT
NEEDLES_BY_REVISION["rev0058"] = ("finalityledger", "retryescrow", "pruneguard", "finalityfold")

# rev0059 settlement/attestation/tombstone-repair fold map.
REV0059_CURRENT = (
    FoldMapEntry("rev0059", "src/i2p_dht_lab/attestationpack.py", "typed_attestation_pack_evidence", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/settlementlane.py", "settlement_lane_after_finality", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/tombstonerepair.py", "tombstone_repair_after_settlement", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/settlementfold.py", "settlementfold_current_audit", True),
    FoldMapEntry("rev0059", "tests/test_rev0059_settlement_attestation_tombrepair.py", "current_tests", True),
    FoldMapEntry("rev0059", "docs/620-rev0059-settlementstore-tombmesh-canaryjoin.md", "current_revision_doc", True),
    FoldMapEntry("rev0059", "docs/621-settlement-lane-after-finality.md", "settlementlane_doc", True),
    FoldMapEntry("rev0059", "docs/622-attestation-pack-typed-evidence.md", "attestationpack_doc", True),
    FoldMapEntry("rev0059", "docs/623-tombstone-repair-after-settlement.md", "tombstonerepair_doc", True),
    FoldMapEntry("rev0059", "docs/624-settlementfold-audit-refactor.md", "settlementfold_doc", True),
)
CURRENT_BY_REVISION["rev0059"] = REV0059_CURRENT
NEEDLES_BY_REVISION["rev0059"] = ("attestationpack", "settlementlane", "tombstonerepair", "settlementfold")

# rev0059 settlement-store / tomb-repair / canary-join fold map.
REV0059_CURRENT = (
    FoldMapEntry("rev0059", "src/i2p_dht_lab/settlementstore.py", "settlement_store_branch_join", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/tombrepairjoin.py", "tomb_repair_prune_join", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/canaryjoin.py", "canary_join_after_settlement", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/settlementstorefold.py", "settlementstorefold_current_audit", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/settlementlane.py", "folded_rev0058_settlement_lane", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/attestationpack.py", "folded_rev0058_attestation_pack", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/tombstonerepair.py", "folded_rev0058_tombstone_repair", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/settlementfold.py", "folded_rev0058_settlementfold", True),
    FoldMapEntry("rev0059", "tests/test_rev0059_settlementstore_tombmesh_canaryjoin.py", "current_tests", True),
    FoldMapEntry("rev0059", "tests/test_rev0058_settlement_attestation_tombrepair.py", "folded_branchlet_tests", True),
    FoldMapEntry("rev0059", "docs/620-rev0059-settlementstore-tombmesh-canaryjoin.md", "current_revision_doc", True),
    FoldMapEntry("rev0059", "docs/621-settlement-store-branch-join.md", "settlementstore_doc", True),
    FoldMapEntry("rev0059", "docs/622-tomb-repair-join-after-prune.md", "tombrepairjoin_doc", True),
    FoldMapEntry("rev0059", "docs/623-canary-join-after-settlement.md", "canaryjoin_doc", True),
    FoldMapEntry("rev0059", "docs/624-settlementstorefold-audit-refactor.md", "settlementstorefold_doc", True),
    FoldMapEntry("rev0059", "artifacts/branchlets/rev0058_settlement_branchlet/settlementlane.py", "preserved_rev0058_settlement_branchlet", False),
)
CURRENT_BY_REVISION["rev0059"] = REV0059_CURRENT
NEEDLES_BY_REVISION["rev0059"] = ("settlementstore", "tombrepairjoin", "canaryjoin", "settlementstorefold", "settlementlane", "attestationpack", "tombstonerepair")

# rev0059 final settlement-store/terminal-receipt fold map override.
REV0059_CURRENT = (
    FoldMapEntry("rev0059", "src/i2p_dht_lab/attestationpack.py", "typed_attestation_pack_evidence", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/settlementlane.py", "settlement_lane_after_finality", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/tombstonerepair.py", "tombstone_repair_after_settlement", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/settlementstore.py", "joined_settlement_store_branch_join", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/terminalreceipt.py", "terminal_receipt_after_finality", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/settlementfold.py", "settlementfold_current_audit", True),
    FoldMapEntry("rev0059", "tests/test_rev0059_settlement_attestation_tombrepair.py", "settlement_branchlet_tests", True),
    FoldMapEntry("rev0059", "tests/test_rev0059_settlementstore_terminalreceipt.py", "settlementstore_terminalreceipt_tests", True),
    FoldMapEntry("rev0059", "docs/620-rev0059-settlementstore-tombmesh-canaryjoin.md", "current_revision_doc", True),
    FoldMapEntry("rev0059", "docs/621-settlement-lane-after-finality.md", "settlementlane_doc", True),
    FoldMapEntry("rev0059", "docs/622-attestation-pack-typed-evidence.md", "attestationpack_doc", True),
    FoldMapEntry("rev0059", "docs/623-tombstone-repair-after-settlement.md", "tombstonerepair_doc", True),
    FoldMapEntry("rev0059", "docs/624-settlementfold-audit-refactor.md", "settlementfold_doc", True),
    FoldMapEntry("rev0059", "docs/625-settlement-store-branch-join.md", "settlementstore_doc", True),
    FoldMapEntry("rev0059", "docs/626-terminal-receipt-after-finality.md", "terminalreceipt_doc", True),
    FoldMapEntry("rev0059", "artifacts/branchlets/rev0058_settlement_attestation_tombrepair/README.md", "folded_rev0058_settlement_branchlet", False),
)
CURRENT_BY_REVISION["rev0059"] = REV0059_CURRENT
NEEDLES_BY_REVISION["rev0059"] = ("attestationpack", "settlementlane", "tombstonerepair", "settlementstore", "terminalreceipt", "settlementfold")

# rev0059 terminal receipt / idempotency repair / compaction audit final override.
REV0059_CURRENT = (
    FoldMapEntry("rev0059", "src/i2p_dht_lab/terminalreceipt.py", "terminal_receipt_after_finality", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/idempotencyrepair.py", "idempotency_repair_lineage", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/compactionaudit.py", "compaction_audit_hard_negative_boundary", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/settlementstore.py", "settlement_store_branch_join", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/terminalfold.py", "terminalfold_current_audit", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/settlementfold.py", "folded_settlement_branch_audit", True),
    FoldMapEntry("rev0059", "tests/test_rev0059_terminalreceipt_idemrepair_compactionaudit.py", "terminal_current_tests", True),
    FoldMapEntry("rev0059", "tests/test_rev0059_settlement_attestation_tombrepair.py", "folded_settlement_tests", True),
    FoldMapEntry("rev0059", "docs/620-rev0059-terminalreceipt-idemrepair-compactionaudit.md", "current_revision_doc", True),
    FoldMapEntry("rev0059", "docs/621-terminal-receipt-after-finality.md", "terminalreceipt_doc", True),
    FoldMapEntry("rev0059", "docs/622-idempotency-repair-lineage.md", "idempotencyrepair_doc", True),
    FoldMapEntry("rev0059", "docs/623-compaction-audit-hard-negatives.md", "compactionaudit_doc", True),
    FoldMapEntry("rev0059", "docs/624-terminalfold-audit-refactor.md", "terminalfold_doc", True),
)
CURRENT_BY_REVISION["rev0059"] = REV0059_CURRENT
NEEDLES_BY_REVISION["rev0059"] = ("terminalreceipt", "idempotencyrepair", "compactionaudit", "settlementstore", "terminalfold")

# rev0059 settlementstore/tombmesh/canary final override after folded branchlet reconciliation.
CURRENT_BY_REVISION["rev0059"] = (
    FoldMapEntry("rev0059", "src/i2p_dht_lab/settlementstore.py", "settlement_store_branch_join", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/tombrepairjoin.py", "tomb_repair_prune_join", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/canaryjoin.py", "canary_join_after_settlement", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/settlementstorefold.py", "settlementstorefold_current_audit", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/settlementlane.py", "folded_rev0058_settlement_lane", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/attestationpack.py", "folded_rev0058_attestation_pack", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/tombstonerepair.py", "folded_rev0058_tombstone_repair", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/settlementfold.py", "folded_rev0058_settlementfold", True),
    FoldMapEntry("rev0059", "tests/test_rev0059_settlementstore_tombmesh_canaryjoin.py", "current_tests", True),
    FoldMapEntry("rev0059", "tests/test_rev0058_settlement_attestation_tombrepair.py", "folded_branchlet_tests", True),
    FoldMapEntry("rev0059", "docs/620-rev0059-settlementstore-tombmesh-canaryjoin.md", "current_revision_doc", True),
    FoldMapEntry("rev0059", "docs/621-settlement-store-branch-join.md", "settlementstore_doc", True),
    FoldMapEntry("rev0059", "docs/622-tomb-repair-join-after-prune.md", "tombrepairjoin_doc", True),
    FoldMapEntry("rev0059", "docs/623-canary-join-after-settlement.md", "canaryjoin_doc", True),
    FoldMapEntry("rev0059", "docs/624-settlementstorefold-audit-refactor.md", "settlementstorefold_doc", True),
    FoldMapEntry("rev0059", "artifacts/branchlets/rev0058_settlement_branchlet/settlementlane.py", "preserved_rev0058_settlement_branchlet", False),
)
NEEDLES_BY_REVISION["rev0059"] = ("settlementstore", "tombrepairjoin", "canaryjoin", "settlementstorefold", "settlementlane", "attestationpack", "tombstonerepair")


# rev0059 unified settlement-store / terminal-receipt fold-map override.
REV0059_CURRENT = (
    FoldMapEntry("rev0059", "src/i2p_dht_lab/settlementstore.py", "settlement_store_branch_join", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/tombrepairjoin.py", "tomb_repair_join_after_prune", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/canaryjoin.py", "canary_join_after_settlement", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/settlementstorefold.py", "settlementstorefold_current_audit", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/settlementlane.py", "folded_settlement_lane", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/attestationpack.py", "folded_attestation_pack", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/tombstonerepair.py", "folded_tombstone_repair", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/settlementfold.py", "settlementfold_branch_audit", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/terminalreceipt.py", "terminal_receipt_after_finality", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/idempotencyrepair.py", "idempotency_repair_lineage", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/compactionaudit.py", "compaction_audit_hard_negative_boundary", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/terminalfold.py", "terminalfold_current_audit", True),
    FoldMapEntry("rev0059", "tests/test_rev0059_settlementstore_tombmesh_canaryjoin.py", "settlementstore_tomb_canary_tests", True),
    FoldMapEntry("rev0059", "tests/test_rev0059_settlementstore_terminalreceipt.py", "settlementstore_terminal_receipt_tests", True),
    FoldMapEntry("rev0059", "tests/test_rev0059_terminalreceipt_idemrepair_compactionaudit.py", "terminal_current_tests", True),
    FoldMapEntry("rev0059", "tests/test_rev0059_settlement_attestation_tombrepair.py", "folded_settlement_tests", True),
    FoldMapEntry("rev0059", "docs/620-rev0059-settlementstore-tombmesh-canaryjoin.md", "settlementstore_revision_doc", True),
    FoldMapEntry("rev0059", "docs/620-rev0059-terminalreceipt-idemrepair-compactionaudit.md", "terminal_revision_doc", True),
    FoldMapEntry("rev0059", "docs/621-settlement-store-branch-join.md", "settlementstore_doc", True),
    FoldMapEntry("rev0059", "docs/621-terminal-receipt-after-finality.md", "terminalreceipt_doc", True),
    FoldMapEntry("rev0059", "docs/622-tomb-repair-join-after-prune.md", "tombrepairjoin_doc", True),
    FoldMapEntry("rev0059", "docs/622-idempotency-repair-lineage.md", "idempotencyrepair_doc", True),
    FoldMapEntry("rev0059", "docs/623-canary-join-after-settlement.md", "canaryjoin_doc", True),
    FoldMapEntry("rev0059", "docs/623-compaction-audit-hard-negatives.md", "compactionaudit_doc", True),
    FoldMapEntry("rev0059", "docs/624-settlementstorefold-audit-refactor.md", "settlementstorefold_doc", True),
    FoldMapEntry("rev0059", "docs/624-settlementfold-audit-refactor.md", "settlementfold_doc", True),
    FoldMapEntry("rev0059", "docs/624-terminalfold-audit-refactor.md", "terminalfold_doc", True),
)
CURRENT_BY_REVISION["rev0059"] = REV0059_CURRENT
NEEDLES_BY_REVISION["rev0059"] = ("settlementstore", "tombrepairjoin", "canaryjoin", "settlementstorefold", "settlementlane", "attestationpack", "tombstonerepair", "settlementfold", "terminalreceipt", "idempotencyrepair", "compactionaudit", "terminalfold")

# rev0059 unified settlement-store / terminal-receipt active fold-map override.
REV0059_CURRENT = (
    FoldMapEntry("rev0059", "src/i2p_dht_lab/settlementstore.py", "settlement_store_branch_join", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/tombrepairjoin.py", "tomb_repair_prune_join", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/canaryjoin.py", "canary_join_after_settlement", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/settlementstorefold.py", "settlementstorefold_current_audit", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/settlementlane.py", "settlement_lane_after_finality", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/attestationpack.py", "typed_attestation_pack_evidence", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/tombstonerepair.py", "tombstone_repair_after_settlement", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/settlementfold.py", "settlementfold_current_audit", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/terminalreceipt.py", "terminal_receipt_after_finality", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/idempotencyrepair.py", "idempotency_repair_lineage", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/compactionaudit.py", "compaction_audit_hard_negative_boundary", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/terminalfold.py", "terminalfold_current_audit", True),
    FoldMapEntry("rev0059", "tests/test_rev0059_settlementstore_tombmesh_canaryjoin.py", "settlementstore_current_tests", True),
    FoldMapEntry("rev0059", "tests/test_rev0059_settlement_attestation_tombrepair.py", "settlement_branch_tests", True),
    FoldMapEntry("rev0059", "tests/test_rev0059_terminalreceipt_idemrepair_compactionaudit.py", "terminal_current_tests", True),
    FoldMapEntry("rev0059", "docs/620-rev0059-settlementstore-tombmesh-canaryjoin.md", "current_revision_doc", True),
    FoldMapEntry("rev0059", "docs/621-settlement-lane-after-finality.md", "settlementlane_doc", True),
    FoldMapEntry("rev0059", "docs/621-settlement-store-branch-join.md", "settlementstore_doc", True),
    FoldMapEntry("rev0059", "docs/621-terminal-receipt-after-finality.md", "terminalreceipt_doc", True),
    FoldMapEntry("rev0059", "docs/622-attestation-pack-typed-evidence.md", "attestationpack_doc", True),
    FoldMapEntry("rev0059", "docs/622-tomb-repair-join-after-prune.md", "tombrepairjoin_doc", True),
    FoldMapEntry("rev0059", "docs/622-idempotency-repair-lineage.md", "idempotencyrepair_doc", True),
    FoldMapEntry("rev0059", "docs/623-tombstone-repair-after-settlement.md", "tombstonerepair_doc", True),
    FoldMapEntry("rev0059", "docs/623-canary-join-after-settlement.md", "canaryjoin_doc", True),
    FoldMapEntry("rev0059", "docs/623-compaction-audit-hard-negatives.md", "compactionaudit_doc", True),
    FoldMapEntry("rev0059", "docs/624-settlementfold-audit-refactor.md", "settlementfold_doc", True),
    FoldMapEntry("rev0059", "docs/624-settlementstorefold-audit-refactor.md", "settlementstorefold_doc", True),
    FoldMapEntry("rev0059", "docs/624-terminalfold-audit-refactor.md", "terminalfold_doc", True),
)
CURRENT_BY_REVISION["rev0059"] = REV0059_CURRENT
NEEDLES_BY_REVISION["rev0059"] = ("settlementstore", "tombrepairjoin", "canaryjoin", "settlementstorefold", "settlementlane", "attestationpack", "tombstonerepair", "settlementfold", "terminalreceipt", "idempotencyrepair", "compactionaudit", "terminalfold")


# rev0059 merged settlement / terminal / canary final override.
REV0059_CURRENT = (
    FoldMapEntry("rev0059", "src/i2p_dht_lab/settlementlane.py", "settlement_lane_after_finality", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/attestationpack.py", "typed_attestation_pack_evidence", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/tombstonerepair.py", "tombstone_repair_after_settlement", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/settlementstore.py", "settlement_store_branch_join", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/tombrepairjoin.py", "tomb_repair_prune_join", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/canaryjoin.py", "canary_join_after_settlement", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/terminalreceipt.py", "terminal_receipt_after_finality", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/idempotencyrepair.py", "idempotency_repair_lineage", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/compactionaudit.py", "compaction_audit_hard_negative_boundary", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/settlementfold.py", "settlementfold_current_audit", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/settlementstorefold.py", "settlementstorefold_current_audit", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/terminalfold.py", "terminalfold_current_audit", True),
    FoldMapEntry("rev0059", "tests/test_rev0059_settlement_attestation_tombrepair.py", "settlement_branchlet_tests", True),
    FoldMapEntry("rev0059", "tests/test_rev0059_settlementstore_tombmesh_canaryjoin.py", "settlementstore_tombmesh_canary_tests", True),
    FoldMapEntry("rev0059", "tests/test_rev0059_settlementstore_terminalreceipt.py", "settlementstore_terminalreceipt_tests", True),
    FoldMapEntry("rev0059", "tests/test_rev0059_terminalreceipt_idemrepair_compactionaudit.py", "terminal_current_tests", True),
    FoldMapEntry("rev0059", "docs/620-rev0059-settlementstore-tombmesh-canaryjoin.md", "current_revision_doc", True),
    FoldMapEntry("rev0059", "docs/620-rev0059-terminalreceipt-idemrepair-compactionaudit.md", "terminal_branch_doc", True),
    FoldMapEntry("rev0059", "docs/621-settlement-lane-after-finality.md", "settlementlane_doc", True),
    FoldMapEntry("rev0059", "docs/621-settlement-store-branch-join.md", "settlementstore_doc", True),
    FoldMapEntry("rev0059", "docs/621-terminal-receipt-after-finality.md", "terminalreceipt_doc", True),
    FoldMapEntry("rev0059", "docs/622-attestation-pack-typed-evidence.md", "attestationpack_doc", True),
    FoldMapEntry("rev0059", "docs/622-tomb-repair-join-after-prune.md", "tombrepairjoin_doc", True),
    FoldMapEntry("rev0059", "docs/622-idempotency-repair-lineage.md", "idempotencyrepair_doc", True),
    FoldMapEntry("rev0059", "docs/623-tombstone-repair-after-settlement.md", "tombstonerepair_doc", True),
    FoldMapEntry("rev0059", "docs/623-canary-join-after-settlement.md", "canaryjoin_doc", True),
    FoldMapEntry("rev0059", "docs/623-compaction-audit-hard-negatives.md", "compactionaudit_doc", True),
    FoldMapEntry("rev0059", "docs/624-settlementfold-audit-refactor.md", "settlementfold_doc", True),
    FoldMapEntry("rev0059", "docs/624-settlementstorefold-audit-refactor.md", "settlementstorefold_doc", True),
    FoldMapEntry("rev0059", "docs/624-terminalfold-audit-refactor.md", "terminalfold_doc", True),
    FoldMapEntry("rev0059", "artifacts/branchlets/rev0058_settlement_attestation_tombrepair/README.md", "folded_settlement_branchlet", False),
)
CURRENT_BY_REVISION["rev0059"] = REV0059_CURRENT
NEEDLES_BY_REVISION["rev0059"] = ("settlementlane", "attestationpack", "tombstonerepair", "settlementstore", "tombrepairjoin", "canaryjoin", "terminalreceipt", "idempotencyrepair", "compactionaudit", "settlementfold", "settlementstorefold", "terminalfold")

# rev0060 live-send / delivery-witness / send-fence active fold-map.
REV0060_CURRENT = (
    FoldMapEntry("rev0060", "src/i2p_dht_lab/livesendgate.py", "live_send_gate_before_network_write", True),
    FoldMapEntry("rev0060", "src/i2p_dht_lab/deliverywitness.py", "delivery_witness_after_send", True),
    FoldMapEntry("rev0060", "src/i2p_dht_lab/sendfence.py", "send_fence_restart_memory", True),
    FoldMapEntry("rev0060", "src/i2p_dht_lab/fenceaudit.py", "fenceaudit_current_audit", True),
    FoldMapEntry("rev0060", "tests/test_rev0060_livesend_delivery_fence.py", "current_tests", True),
    FoldMapEntry("rev0060", "docs/637-rev0060-livesendgate-deliverywitness-fenceaudit.md", "current_revision_doc", True),
    FoldMapEntry("rev0060", "docs/638-live-send-gate-before-network-write.md", "livesendgate_doc", True),
    FoldMapEntry("rev0060", "docs/639-delivery-witness-after-send.md", "deliverywitness_doc", True),
    FoldMapEntry("rev0060", "docs/640-send-fence-restart-memory.md", "sendfence_doc", True),
    FoldMapEntry("rev0060", "docs/641-fenceaudit-audit-refactor.md", "fenceaudit_doc", True),
    FoldMapEntry("rev0059", "src/i2p_dht_lab/settlementstorefold.py", "predecessor_settlementstorefold", False),
)
CURRENT_BY_REVISION["rev0060"] = REV0060_CURRENT
NEEDLES_BY_REVISION["rev0060"] = ("livesendgate", "deliverywitness", "sendfence", "fenceaudit")

# rev0061 delivery-settlement / ack-archive / ack-prune active fold-map.
REV0061_CURRENT = (
    FoldMapEntry("rev0061", "src/i2p_dht_lab/deliverysettlement.py", "delivery_settlement_after_fence", True),
    FoldMapEntry("rev0061", "src/i2p_dht_lab/ackarchive.py", "ack_archive_restart_memory", True),
    FoldMapEntry("rev0061", "src/i2p_dht_lab/ackprunejoin.py", "ack_prune_join_boundary", True),
    FoldMapEntry("rev0061", "src/i2p_dht_lab/ackfold.py", "ackfold_current_audit", True),
    FoldMapEntry("rev0061", "tests/test_rev0061_deliverysettlement_ackarchive_prunejoin.py", "current_tests", True),
    FoldMapEntry("rev0061", "docs/647-rev0061-deliverysettlement-ackarchive-prunejoin.md", "current_revision_doc", True),
    FoldMapEntry("rev0061", "docs/648-delivery-settlement-after-fence.md", "deliverysettlement_doc", True),
    FoldMapEntry("rev0061", "docs/649-ack-archive-restart-memory.md", "ackarchive_doc", True),
    FoldMapEntry("rev0061", "docs/650-ack-prune-join-boundary.md", "ackprunejoin_doc", True),
    FoldMapEntry("rev0061", "docs/651-ackfold-audit-refactor.md", "ackfold_doc", True),
    FoldMapEntry("rev0060", "src/i2p_dht_lab/fenceaudit.py", "predecessor_fenceaudit", False),
)
CURRENT_BY_REVISION["rev0061"] = REV0061_CURRENT
NEEDLES_BY_REVISION["rev0061"] = ("deliverysettlement", "ackarchive", "ackprunejoin", "ackfold")

# rev0062 ACK/repair live-egress retry fence active fold-map.
REV0062_CURRENT = (
    FoldMapEntry("rev0062", "src/i2p_dht_lab/deliveryrepair.py", "deliveryrepair_folded_branchlet", True),
    FoldMapEntry("rev0062", "src/i2p_dht_lab/rollbackprobe.py", "rollbackprobe_folded_branchlet", True),
    FoldMapEntry("rev0062", "src/i2p_dht_lab/liveegress.py", "liveegress_folded_branchlet", True),
    FoldMapEntry("rev0062", "src/i2p_dht_lab/ackrepairjoin.py", "ack_repair_join_boundary", True),
    FoldMapEntry("rev0062", "src/i2p_dht_lab/retryfence.py", "retry_fence_restart_memory", True),
    FoldMapEntry("rev0062", "src/i2p_dht_lab/repairpruneguard.py", "repair_prune_guard", True),
    FoldMapEntry("rev0062", "src/i2p_dht_lab/egressrepairfold.py", "egressrepairfold_current_audit", True),
    FoldMapEntry("rev0062", "tests/test_rev0062_ackrepair_liveegress_retryfence.py", "current_tests", True),
    FoldMapEntry("rev0062", "docs/657-rev0062-ackrepair-liveegress-retryfence.md", "current_revision_doc", True),
    FoldMapEntry("rev0062", "docs/658-delivery-repair-live-egress-branchfold.md", "deliveryrepair_branchfold_doc", True),
    FoldMapEntry("rev0062", "docs/659-ack-repair-join-boundary.md", "ackrepairjoin_doc", True),
    FoldMapEntry("rev0062", "docs/660-retry-fence-restart-memory.md", "retryfence_doc", True),
    FoldMapEntry("rev0062", "docs/661-repair-prune-guard.md", "repairpruneguard_doc", True),
    FoldMapEntry("rev0062", "docs/662-egressrepairfold-audit-refactor.md", "egressrepairfold_doc", True),
)
CURRENT_BY_REVISION["rev0062"] = REV0062_CURRENT
NEEDLES_BY_REVISION["rev0062"] = ("deliveryrepair", "rollbackprobe", "liveegress", "ackrepairjoin", "retryfence", "repairpruneguard", "egressrepairfold")

# rev0063 late ACK / retry settlement / egress journal active fold-map override.
REV0063_CURRENT = (
    FoldMapEntry("rev0063", "src/i2p_dht_lab/lateack.py", "late_ack_after_retry_fence", True),
    FoldMapEntry("rev0063", "src/i2p_dht_lab/retrysettlement.py", "retry_and_withdraw_settlement", True),
    FoldMapEntry("rev0063", "src/i2p_dht_lab/withdrawrepair.py", "withdraw_repair_publication_memory", True),
    FoldMapEntry("rev0063", "src/i2p_dht_lab/egressjournal.py", "egress_journal_compaction", True),
    FoldMapEntry("rev0063", "src/i2p_dht_lab/lateackfold.py", "lateackfold_current_audit", True),
    FoldMapEntry("rev0063", "tests/test_rev0063_lateack_retrysettle_egressjournal.py", "current_tests", True),
    FoldMapEntry("rev0063", "docs/668-rev0063-lateack-retrysettle-egressjournal.md", "current_revision_doc", True),
    FoldMapEntry("rev0063", "docs/669-late-ack-after-retry-fence.md", "lateack_doc", True),
    FoldMapEntry("rev0063", "docs/670-retry-settlement-and-withdraw-repair.md", "retrysettlement_withdrawrepair_doc", True),
    FoldMapEntry("rev0063", "docs/671-egress-journal-compaction.md", "egressjournal_doc", True),
    FoldMapEntry("rev0063", "docs/672-lateackfold-audit-refactor.md", "lateackfold_doc", True),
)
CURRENT_BY_REVISION["rev0063"] = REV0063_CURRENT
NEEDLES_BY_REVISION["rev0063"] = ("lateack", "retrysettlement", "withdrawrepair", "egressjournal", "lateackfold")

# rev0064 retry publication / idempotency mesh / delivery repair active fold-map.
REV0064_CURRENT = (
    FoldMapEntry("rev0064", "src/i2p_dht_lab/retrypublish.py", "retry_publication_outbox", True),
    FoldMapEntry("rev0064", "src/i2p_dht_lab/idempotencymesh.py", "idempotency_mesh_lineage", True),
    FoldMapEntry("rev0064", "src/i2p_dht_lab/deliveryrepairmesh.py", "delivery_repair_remote_witness", True),
    FoldMapEntry("rev0064", "src/i2p_dht_lab/retrypublishfold.py", "retrypublishfold_current_audit", True),
    FoldMapEntry("rev0064", "tests/test_rev0064_retrypublish_idempotencymesh_deliveryrepair.py", "current_tests", True),
    FoldMapEntry("rev0064", "docs/678-rev0064-retrypublish-idempotencymesh-deliveryrepair.md", "current_revision_doc", True),
    FoldMapEntry("rev0064", "docs/679-retry-publication-outbox.md", "retrypublish_doc", True),
    FoldMapEntry("rev0064", "docs/680-idempotency-mesh-lineage.md", "idempotencymesh_doc", True),
    FoldMapEntry("rev0064", "docs/681-delivery-repair-remote-witness.md", "deliveryrepairmesh_doc", True),
    FoldMapEntry("rev0064", "docs/682-retrypublishfold-audit-refactor.md", "retrypublishfold_doc", True),
    FoldMapEntry("rev0063", "src/i2p_dht_lab/lateackfold.py", "predecessor_lateackfold", False),
)
CURRENT_BY_REVISION["rev0064"] = REV0064_CURRENT
NEEDLES_BY_REVISION["rev0064"] = ("retrypublish", "idempotencymesh", "deliveryrepairmesh", "retrypublishfold")

# rev0065 remote witness / repair outbox / conflict cooldown active fold-map.
REV0065_CURRENT = (
    FoldMapEntry("rev0065", "src/i2p_dht_lab/remotewitnessledger.py", "remote_witness_ledger_rounds", True),
    FoldMapEntry("rev0065", "src/i2p_dht_lab/repairoutbox.py", "repair_outbox_after_duplicate_conflict", True),
    FoldMapEntry("rev0065", "src/i2p_dht_lab/conflictcooldown.py", "conflict_cooldown_duplicate_pressure", True),
    FoldMapEntry("rev0065", "src/i2p_dht_lab/remoterepairfold.py", "remoterepairfold_current_audit", True),
    FoldMapEntry("rev0065", "tests/test_rev0065_remotewitness_repairoutbox_conflictcooldown.py", "current_tests", True),
    FoldMapEntry("rev0065", "docs/688-rev0065-remotewitness-repairoutbox-conflictcooldown.md", "current_revision_doc", True),
    FoldMapEntry("rev0065", "docs/689-remote-witness-ledger-rounds.md", "remotewitnessledger_doc", True),
    FoldMapEntry("rev0065", "docs/690-repair-outbox-after-duplicate-conflict.md", "repairoutbox_doc", True),
    FoldMapEntry("rev0065", "docs/691-conflict-cooldown-duplicate-pressure.md", "conflictcooldown_doc", True),
    FoldMapEntry("rev0065", "docs/692-remoterepairfold-audit-refactor.md", "remoterepairfold_doc", True),
    FoldMapEntry("rev0064", "src/i2p_dht_lab/retrypublishfold.py", "predecessor_retrypublishfold", False),
)
CURRENT_BY_REVISION["rev0065"] = REV0065_CURRENT
NEEDLES_BY_REVISION["rev0065"] = ("remotewitnessledger", "repairoutbox", "conflictcooldown", "remoterepairfold")

# rev0066 repair-publish / ACK-ledger / duplicate-closure active fold-map.
REV0066_CURRENT = (
    FoldMapEntry("rev0066", "src/i2p_dht_lab/repairpublishgate.py", "repair_publish_gate_after_cooldown", True),
    FoldMapEntry("rev0066", "src/i2p_dht_lab/repairackledger.py", "repair_ack_ledger", True),
    FoldMapEntry("rev0066", "src/i2p_dht_lab/duplicateclosure.py", "duplicate_closure_finality", True),
    FoldMapEntry("rev0066", "src/i2p_dht_lab/repairpublishfold.py", "repairpublishfold_current_audit", True),
    FoldMapEntry("rev0066", "tests/test_rev0066_repairpublish_ackclosure.py", "current_tests", True),
    FoldMapEntry("rev0066", "docs/698-rev0066-repairpublish-ackclosure-duplicatefinality.md", "current_revision_doc", True),
    FoldMapEntry("rev0066", "docs/699-repair-publish-gate-after-cooldown.md", "repairpublishgate_doc", True),
    FoldMapEntry("rev0066", "docs/700-repair-ack-ledger.md", "repairackledger_doc", True),
    FoldMapEntry("rev0066", "docs/701-duplicate-closure-finality.md", "duplicateclosure_doc", True),
    FoldMapEntry("rev0066", "docs/702-repairpublishfold-audit-refactor.md", "repairpublishfold_doc", True),
    FoldMapEntry("rev0065", "src/i2p_dht_lab/remoterepairfold.py", "predecessor_remoterepairfold", False),
)
CURRENT_BY_REVISION["rev0066"] = REV0066_CURRENT
NEEDLES_BY_REVISION["rev0066"] = ("repairpublishgate", "repairackledger", "duplicateclosure", "repairpublishfold")

# rev0067 repair-settlement / closure-archive / repair-prune active fold-map.
REV0067_CURRENT = (
    FoldMapEntry("rev0067", "src/i2p_dht_lab/repairsettlement.py", "repair_settlement_after_duplicate_closure", True),
    FoldMapEntry("rev0067", "src/i2p_dht_lab/closurearchive.py", "closure_archive_restart_memory", True),
    FoldMapEntry("rev0067", "src/i2p_dht_lab/repairprune.py", "repair_prune_protected_memory", True),
    FoldMapEntry("rev0067", "src/i2p_dht_lab/repairsettlementfold.py", "repairsettlementfold_current_audit", True),
    FoldMapEntry("rev0067", "tests/test_rev0067_repairsettlement_archive_prune.py", "current_tests", True),
    FoldMapEntry("rev0067", "docs/708-rev0067-repairsettlement-closurearchive-repairprune.md", "current_revision_doc", True),
    FoldMapEntry("rev0067", "docs/709-repair-settlement-after-duplicate-closure.md", "repairsettlement_doc", True),
    FoldMapEntry("rev0067", "docs/710-closure-archive-restart-memory.md", "closurearchive_doc", True),
    FoldMapEntry("rev0067", "docs/711-repair-prune-protected-memory.md", "repairprune_doc", True),
    FoldMapEntry("rev0067", "docs/712-repairsettlementfold-audit-refactor.md", "repairsettlementfold_doc", True),
    FoldMapEntry("rev0066", "src/i2p_dht_lab/repairpublishfold.py", "predecessor_repairpublishfold", False),
)
CURRENT_BY_REVISION["rev0067"] = REV0067_CURRENT
NEEDLES_BY_REVISION["rev0067"] = ("repairsettlement", "closurearchive", "repairprune", "repairsettlementfold")

# rev0068 archive journal / prune replay / closure audit active fold-map.
REV0068_CURRENT = (
    FoldMapEntry("rev0068", "src/i2p_dht_lab/archivejournal.py", "archive_journal_after_prune", True),
    FoldMapEntry("rev0068", "src/i2p_dht_lab/prunereplay.py", "prune_replay_resistance", True),
    FoldMapEntry("rev0068", "src/i2p_dht_lab/closureaudit.py", "closure_audit_restart_boundary", True),
    FoldMapEntry("rev0068", "src/i2p_dht_lab/archivejournalfold.py", "archivejournalfold_current_audit", True),
    FoldMapEntry("rev0068", "tests/test_rev0068_archivejournal_prunereplay_closureaudit.py", "current_tests", True),
    FoldMapEntry("rev0068", "docs/718-rev0068-archivejournal-prunereplay-closureaudit.md", "current_revision_doc", True),
    FoldMapEntry("rev0068", "docs/719-archive-journal-after-prune.md", "archivejournal_doc", True),
    FoldMapEntry("rev0068", "docs/720-prune-replay-resistance.md", "prunereplay_doc", True),
    FoldMapEntry("rev0068", "docs/721-closure-audit-restart-boundary.md", "closureaudit_doc", True),
    FoldMapEntry("rev0068", "docs/722-archivejournalfold-audit-refactor.md", "archivejournalfold_doc", True),
    FoldMapEntry("rev0067", "src/i2p_dht_lab/repairsettlementfold.py", "predecessor_repairsettlementfold", False),
)
CURRENT_BY_REVISION["rev0068"] = REV0068_CURRENT
NEEDLES_BY_REVISION["rev0068"] = ("archivejournal", "prunereplay", "closureaudit", "archivejournalfold")

# rev0069 closure seal / retention proof / audit export active fold-map.
REV0069_CURRENT = (
    FoldMapEntry("rev0069", "src/i2p_dht_lab/closureseal.py", "closure_seal_after_audit", True),
    FoldMapEntry("rev0069", "src/i2p_dht_lab/retentionproof.py", "retention_proof_after_closure_seal", True),
    FoldMapEntry("rev0069", "src/i2p_dht_lab/auditexport.py", "redacted_audit_export_boundary", True),
    FoldMapEntry("rev0069", "src/i2p_dht_lab/closuresealfold.py", "closuresealfold_current_audit", True),
    FoldMapEntry("rev0069", "tests/test_rev0069_closureseal_retention_export.py", "current_tests", True),
    FoldMapEntry("rev0069", "docs/728-rev0069-closureseal-retentionproof-exportaudit.md", "current_revision_doc", True),
    FoldMapEntry("rev0069", "docs/729-closure-seal-after-audit.md", "closureseal_doc", True),
    FoldMapEntry("rev0069", "docs/730-retention-proof-hard-negative-carry.md", "retentionproof_doc", True),
    FoldMapEntry("rev0069", "docs/731-audit-export-redacted-boundary.md", "auditexport_doc", True),
    FoldMapEntry("rev0069", "docs/732-closuresealfold-audit-refactor.md", "closuresealfold_doc", True),
    FoldMapEntry("rev0068", "src/i2p_dht_lab/archivejournalfold.py", "predecessor_archivejournalfold", False),
)
CURRENT_BY_REVISION["rev0069"] = REV0069_CURRENT
NEEDLES_BY_REVISION["rev0069"] = ("closureseal", "retentionproof", "auditexport", "closuresealfold")

# rev0070 export receipt / retention GC / closure handoff active fold-map.
REV0070_CURRENT = (
    FoldMapEntry("rev0070", "src/i2p_dht_lab/exportreceipt.py", "export_receipt_restart_memory", True),
    FoldMapEntry("rev0070", "src/i2p_dht_lab/retentiongc.py", "retention_gc_after_export", True),
    FoldMapEntry("rev0070", "src/i2p_dht_lab/closurehandoff.py", "closure_handoff_redacted_boundary", True),
    FoldMapEntry("rev0070", "src/i2p_dht_lab/exporthandofffold.py", "exporthandofffold_current_audit", True),
    FoldMapEntry("rev0070", "tests/test_rev0070_exportreceipt_retentiongc_handoff.py", "current_tests", True),
    FoldMapEntry("rev0070", "docs/738-rev0070-exportreceipt-retentiongc-closurehandoff.md", "current_revision_doc", True),
    FoldMapEntry("rev0070", "docs/739-export-receipt-restart-memory.md", "exportreceipt_doc", True),
    FoldMapEntry("rev0070", "docs/740-retention-gc-after-export.md", "retentiongc_doc", True),
    FoldMapEntry("rev0070", "docs/741-closure-handoff-redacted-boundary.md", "closurehandoff_doc", True),
    FoldMapEntry("rev0070", "docs/742-exporthandofffold-audit-refactor.md", "exporthandofffold_doc", True),
    FoldMapEntry("rev0069", "src/i2p_dht_lab/closuresealfold.py", "predecessor_closuresealfold", False),
)
CURRENT_BY_REVISION["rev0070"] = REV0070_CURRENT
NEEDLES_BY_REVISION["rev0070"] = ("exportreceipt", "retentiongc", "closurehandoff", "exporthandofffold")

# rev0071 handoff receipt / import / summary lineage active fold-map.
REV0071_CURRENT = (
    FoldMapEntry("rev0071", "src/i2p_dht_lab/handoffreceipt.py", "handoff_receipt_recipient_boundary", True),
    FoldMapEntry("rev0071", "src/i2p_dht_lab/handoffimport.py", "handoff_import_redacted_state", True),
    FoldMapEntry("rev0071", "src/i2p_dht_lab/summarylineage.py", "summary_lineage_redacted_boundary", True),
    FoldMapEntry("rev0071", "src/i2p_dht_lab/handoffreceiptfold.py", "handoffreceiptfold_current_audit", True),
    FoldMapEntry("rev0071", "tests/test_rev0071_handoffreceipt_import_summarylineage.py", "current_tests", True),
    FoldMapEntry("rev0071", "docs/748-rev0071-handoffreceipt-importsummary-ledgerfold.md", "current_revision_doc", True),
    FoldMapEntry("rev0071", "docs/749-handoff-receipt-recipient-boundary.md", "handoffreceipt_doc", True),
    FoldMapEntry("rev0071", "docs/750-handoff-import-redacted-state.md", "handoffimport_doc", True),
    FoldMapEntry("rev0071", "docs/751-summary-lineage-redacted-boundary.md", "summarylineage_doc", True),
    FoldMapEntry("rev0071", "docs/752-handoffreceiptfold-audit-refactor.md", "handoffreceiptfold_doc", True),
    FoldMapEntry("rev0070", "src/i2p_dht_lab/exporthandofffold.py", "predecessor_exporthandofffold", False),
)
CURRENT_BY_REVISION["rev0071"] = REV0071_CURRENT
NEEDLES_BY_REVISION["rev0071"] = ("handoffreceipt", "handoffimport", "summarylineage", "handoffreceiptfold")

# rev0072 summary receipt / import archive / lineage prune active fold-map.
REV0072_CURRENT = (
    FoldMapEntry("rev0072", "src/i2p_dht_lab/summaryreceipt.py", "summary_receipt_after_lineage", True),
    FoldMapEntry("rev0072", "src/i2p_dht_lab/importarchive.py", "import_archive_after_summary_receipt", True),
    FoldMapEntry("rev0072", "src/i2p_dht_lab/lineageprune.py", "lineage_prune_guard", True),
    FoldMapEntry("rev0072", "src/i2p_dht_lab/summaryreceiptfold.py", "summaryreceiptfold_current_audit", True),
    FoldMapEntry("rev0072", "tests/test_rev0072_summaryreceipt_importarchive_lineageprune.py", "current_tests", True),
    FoldMapEntry("rev0072", "docs/758-rev0072-summaryreceipt-importarchive-lineageprune.md", "current_revision_doc", True),
    FoldMapEntry("rev0072", "docs/759-summary-receipt-after-lineage.md", "summaryreceipt_doc", True),
    FoldMapEntry("rev0072", "docs/760-import-archive-after-summary-receipt.md", "importarchive_doc", True),
    FoldMapEntry("rev0072", "docs/761-lineage-prune-guard.md", "lineageprune_doc", True),
    FoldMapEntry("rev0072", "docs/762-summaryreceiptfold-audit-refactor.md", "summaryreceiptfold_doc", True),
    FoldMapEntry("rev0071", "src/i2p_dht_lab/handoffreceiptfold.py", "predecessor_handoffreceiptfold", False),
)
CURRENT_BY_REVISION["rev0072"] = REV0072_CURRENT
NEEDLES_BY_REVISION["rev0072"] = ("summaryreceipt", "importarchive", "lineageprune", "summaryreceiptfold")

# rev0073 summary publication / redaction witness / import-prune audit active fold-map.
REV0073_CURRENT = (
    FoldMapEntry("rev0073", "src/i2p_dht_lab/summarypublish.py", "summary_publication_after_lineage_prune", True),
    FoldMapEntry("rev0073", "src/i2p_dht_lab/redactionwitness.py", "redaction_witness_receipts", True),
    FoldMapEntry("rev0073", "src/i2p_dht_lab/importpruneaudit.py", "import_prune_audit_after_restart", True),
    FoldMapEntry("rev0073", "src/i2p_dht_lab/summarypublishfold.py", "summarypublishfold_current_audit", True),
    FoldMapEntry("rev0073", "tests/test_rev0073_summarypublish_redactionwitness_importpruneaudit.py", "current_tests", True),
    FoldMapEntry("rev0073", "docs/768-rev0073-summarypublish-redactionwitness-importpruneaudit.md", "current_revision_doc", True),
    FoldMapEntry("rev0073", "docs/769-summary-publication-after-lineage-prune.md", "summarypublish_doc", True),
    FoldMapEntry("rev0073", "docs/770-redaction-witness-receipts.md", "redactionwitness_doc", True),
    FoldMapEntry("rev0073", "docs/771-import-prune-audit-after-restart.md", "importpruneaudit_doc", True),
    FoldMapEntry("rev0073", "docs/772-summarypublishfold-audit-refactor.md", "summarypublishfold_doc", True),
    FoldMapEntry("rev0072", "src/i2p_dht_lab/summaryreceiptfold.py", "predecessor_summaryreceiptfold", False),
)
CURRENT_BY_REVISION["rev0073"] = REV0073_CURRENT
NEEDLES_BY_REVISION["rev0073"] = ("summarypublish", "redactionwitness", "importpruneaudit", "summarypublishfold")

# rev0074 summary outbox / redaction archive / publish fence active fold-map.
REV0074_CURRENT = (
    FoldMapEntry("rev0074", "src/i2p_dht_lab/summaryoutbox.py", "summary_outbox_after_publication", True),
    FoldMapEntry("rev0074", "src/i2p_dht_lab/redactionarchive.py", "redaction_archive_restart_memory", True),
    FoldMapEntry("rev0074", "src/i2p_dht_lab/publishfence.py", "publish_fence_before_summary_write", True),
    FoldMapEntry("rev0074", "src/i2p_dht_lab/summaryoutboxfold.py", "summaryoutboxfold_current_audit", True),
    FoldMapEntry("rev0074", "tests/test_rev0074_summaryoutbox_redactionarchive_publishfence.py", "current_tests", True),
    FoldMapEntry("rev0074", "docs/778-rev0074-summaryoutbox-redactionarchive-publishfence.md", "current_revision_doc", True),
    FoldMapEntry("rev0074", "docs/779-summary-outbox-after-publication.md", "summaryoutbox_doc", True),
    FoldMapEntry("rev0074", "docs/780-redaction-archive-restart-memory.md", "redactionarchive_doc", True),
    FoldMapEntry("rev0074", "docs/781-publish-fence-before-summary-write.md", "publishfence_doc", True),
    FoldMapEntry("rev0074", "docs/782-summaryoutboxfold-audit-refactor.md", "summaryoutboxfold_doc", True),
    FoldMapEntry("rev0073", "src/i2p_dht_lab/summarypublishfold.py", "predecessor_summarypublishfold", False),
)
CURRENT_BY_REVISION["rev0074"] = REV0074_CURRENT
NEEDLES_BY_REVISION["rev0074"] = ("summaryoutbox", "redactionarchive", "publishfence", "summaryoutboxfold")

# rev0075 summary send canary / redaction GC / outbox settlement active fold-map.
REV0075_CURRENT = (
    FoldMapEntry("rev0075", "src/i2p_dht_lab/summarysendcanary.py", "summary_send_canary_after_publish_fence", True),
    FoldMapEntry("rev0075", "src/i2p_dht_lab/redactiongc.py", "redaction_gc_after_archive_fence", True),
    FoldMapEntry("rev0075", "src/i2p_dht_lab/outboxsettlement.py", "outbox_settlement_markers", True),
    FoldMapEntry("rev0075", "src/i2p_dht_lab/summarysendfold.py", "summarysendfold_current_audit", True),
    FoldMapEntry("rev0075", "tests/test_rev0075_summarysendcanary_redactiongc_outboxsettlement.py", "current_tests", True),
    FoldMapEntry("rev0075", "docs/788-rev0075-summarysendcanary-redactiongc-outboxsettlement.md", "current_revision_doc", True),
    FoldMapEntry("rev0075", "docs/789-summary-send-canary-before-live-write.md", "summarysendcanary_doc", True),
    FoldMapEntry("rev0075", "docs/790-redaction-gc-join-after-archive.md", "redactiongc_doc", True),
    FoldMapEntry("rev0075", "docs/791-outbox-settlement-prepared-aborted-suppressed.md", "outboxsettlement_doc", True),
    FoldMapEntry("rev0075", "docs/792-summarysendfold-audit-refactor.md", "summarysendfold_doc", True),
    FoldMapEntry("rev0074", "src/i2p_dht_lab/summaryoutboxfold.py", "predecessor_summaryoutboxfold", False),
)
CURRENT_BY_REVISION["rev0075"] = REV0075_CURRENT
NEEDLES_BY_REVISION["rev0075"] = ("summarysendcanary", "redactiongc", "outboxsettlement", "summarysendfold")

# rev0075 summary send canary / redaction GC / outbox settlement active fold-map.
REV0075_CURRENT = (
    FoldMapEntry("rev0075", "src/i2p_dht_lab/summarysendcanary.py", "summary_send_canary_before_live_write", True),
    FoldMapEntry("rev0075", "src/i2p_dht_lab/redactiongc.py", "redaction_gc_after_archive", True),
    FoldMapEntry("rev0075", "src/i2p_dht_lab/outboxsettlement.py", "outbox_settlement_prepared_aborted_suppressed", True),
    FoldMapEntry("rev0075", "src/i2p_dht_lab/summarysendfold.py", "summarysendfold_current_audit", True),
    FoldMapEntry("rev0075", "tests/test_rev0075_summarysendcanary_redactiongc_outboxsettlement.py", "current_tests", True),
    FoldMapEntry("rev0075", "docs/788-rev0075-summarysendcanary-redactiongc-outboxsettlement.md", "current_revision_doc", True),
    FoldMapEntry("rev0075", "docs/789-summary-send-canary-before-live-write.md", "summarysendcanary_doc", True),
    FoldMapEntry("rev0075", "docs/790-redaction-gc-join-after-archive.md", "redactiongc_doc", True),
    FoldMapEntry("rev0075", "docs/791-outbox-settlement-prepared-aborted-suppressed.md", "outboxsettlement_doc", True),
    FoldMapEntry("rev0075", "docs/792-summarysendfold-audit-refactor.md", "summarysendfold_doc", True),
    FoldMapEntry("rev0074", "src/i2p_dht_lab/summaryoutboxfold.py", "predecessor_summaryoutboxfold", False),
)
CURRENT_BY_REVISION["rev0075"] = REV0075_CURRENT
NEEDLES_BY_REVISION["rev0075"] = ("summarysendcanary", "redactiongc", "outboxsettlement", "summarysendfold")

# rev0075 corrected active fold-map after folding the sibling summary-settlement branchlet.
REV0075_CURRENT = (
    FoldMapEntry("rev0075", "src/i2p_dht_lab/outboxsettlement.py", "outbox_settlement_branch_join", True),
    FoldMapEntry("rev0075", "src/i2p_dht_lab/summarysendcanary.py", "summary_send_canary_no_network", True),
    FoldMapEntry("rev0075", "src/i2p_dht_lab/summarysettlement.py", "folded_summary_settlement_branchlet", True),
    FoldMapEntry("rev0075", "src/i2p_dht_lab/publicledger.py", "folded_public_ledger_branchlet", True),
    FoldMapEntry("rev0075", "src/i2p_dht_lab/redactiongc.py", "folded_redaction_gc_branchlet", True),
    FoldMapEntry("rev0075", "src/i2p_dht_lab/summarysendfold.py", "summarysendfold_current_audit", True),
    FoldMapEntry("rev0075", "tests/test_rev0075_summarysendcanary_redactiongc_outboxsettlement.py", "current_tests", True),
    FoldMapEntry("rev0075", "tests/test_rev0074_summarysettlement_publicledger_redactiongc.py", "folded_branchlet_tests", True),
    FoldMapEntry("rev0075", "docs/788-rev0075-summarysendcanary-redactiongc-outboxsettlement.md", "current_revision_doc", True),
    FoldMapEntry("rev0075", "docs/791-outbox-settlement-prepared-aborted-suppressed.md", "outboxsettlement_doc", True),
    FoldMapEntry("rev0075", "docs/789-summary-send-canary-before-live-write.md", "summarysendcanary_doc", True),
    FoldMapEntry("rev0075", "docs/790-redaction-gc-join-after-archive.md", "summarysettlement_branchlet_doc", True),
    FoldMapEntry("rev0075", "docs/792-summarysendfold-audit-refactor.md", "summarysendfold_doc", True),
    FoldMapEntry("rev0074", "src/i2p_dht_lab/summaryoutboxfold.py", "predecessor_summaryoutboxfold", False),
)
CURRENT_BY_REVISION["rev0075"] = REV0075_CURRENT
NEEDLES_BY_REVISION["rev0075"] = ("outboxsettlement", "summarysendcanary", "summarysettlement", "publicledger", "redactiongc", "summarysendfold")

# rev0076 summary drain / delivery witness / settlement fence active fold-map.
REV0076_CURRENT = (
    FoldMapEntry("rev0076", "src/i2p_dht_lab/summarydrain.py", "summary_drain_after_canary", True),
    FoldMapEntry("rev0076", "src/i2p_dht_lab/summarydeliverywitness.py", "summary_delivery_witness", True),
    FoldMapEntry("rev0076", "src/i2p_dht_lab/settlementfence.py", "settlement_fence_after_delivery", True),
    FoldMapEntry("rev0076", "src/i2p_dht_lab/summarydeliveryfold.py", "summarydeliveryfold_current_audit", True),
    FoldMapEntry("rev0076", "tests/test_rev0076_summarydrain_deliverywitness_settlementfence.py", "current_tests", True),
    FoldMapEntry("rev0076", "docs/798-rev0076-summarydrain-deliverywitness-settlementfence.md", "current_revision_doc", True),
    FoldMapEntry("rev0076", "docs/799-summary-drain-after-canary.md", "summarydrain_doc", True),
    FoldMapEntry("rev0076", "docs/800-summary-delivery-witness.md", "summarydeliverywitness_doc", True),
    FoldMapEntry("rev0076", "docs/801-settlement-fence-after-delivery.md", "settlementfence_doc", True),
    FoldMapEntry("rev0076", "docs/802-summarydeliveryfold-audit-refactor.md", "summarydeliveryfold_doc", True),
    FoldMapEntry("rev0075", "src/i2p_dht_lab/summarysendfold.py", "predecessor_summarysendfold", False),
)
CURRENT_BY_REVISION["rev0076"] = REV0076_CURRENT
NEEDLES_BY_REVISION["rev0076"] = ("summarydrain", "summarydeliverywitness", "settlementfence", "summarydeliveryfold")

# rev0077 summary ACK ledger / delivery archive / prune fence active fold-map.
REV0077_CURRENT = (
    FoldMapEntry("rev0077", "src/i2p_dht_lab/summaryackledger.py", "summary_ack_ledger_after_settlement_fence", True),
    FoldMapEntry("rev0077", "src/i2p_dht_lab/deliveryarchive.py", "delivery_archive_restart_memory", True),
    FoldMapEntry("rev0077", "src/i2p_dht_lab/summaryprunefence.py", "summary_prune_fence_after_archive", True),
    FoldMapEntry("rev0077", "src/i2p_dht_lab/summaryackfold.py", "summaryackfold_current_audit", True),
    FoldMapEntry("rev0077", "tests/test_rev0077_summaryackledger_deliveryarchive_prunefence.py", "current_tests", True),
    FoldMapEntry("rev0077", "docs/808-rev0077-summaryackledger-deliveryarchive-prunefence.md", "current_revision_doc", True),
    FoldMapEntry("rev0077", "docs/809-summary-ack-ledger-after-settlement-fence.md", "summaryackledger_doc", True),
    FoldMapEntry("rev0077", "docs/810-delivery-archive-restart-memory.md", "deliveryarchive_doc", True),
    FoldMapEntry("rev0077", "docs/811-summary-prune-fence.md", "summaryprunefence_doc", True),
    FoldMapEntry("rev0077", "docs/812-summaryackfold-audit-refactor.md", "summaryackfold_doc", True),
    FoldMapEntry("rev0076", "src/i2p_dht_lab/summarydeliveryfold.py", "predecessor_summarydeliveryfold", False),
)
CURRENT_BY_REVISION["rev0077"] = REV0077_CURRENT
NEEDLES_BY_REVISION["rev0077"] = ("summaryackledger", "deliveryarchive", "summaryprunefence", "summaryackfold")

# rev0078 summary replay / ACK closure / export fence active fold-map.
REV0078_CURRENT = (
    FoldMapEntry("rev0078", "src/i2p_dht_lab/summaryreplay.py", "summary_replay_after_prune_fence", True),
    FoldMapEntry("rev0078", "src/i2p_dht_lab/ackclosure.py", "ack_closure_after_restart_replay", True),
    FoldMapEntry("rev0078", "src/i2p_dht_lab/summaryexportfence.py", "summary_export_fence_no_network", True),
    FoldMapEntry("rev0078", "src/i2p_dht_lab/summaryreplayfold.py", "summaryreplayfold_current_audit", True),
    FoldMapEntry("rev0078", "tests/test_rev0078_summaryreplay_ackclosure_exportfence.py", "current_tests", True),
    FoldMapEntry("rev0078", "docs/818-rev0078-summaryreplay-ackclosure-exportfence.md", "current_revision_doc", True),
    FoldMapEntry("rev0078", "docs/819-summary-replay-after-prune-fence.md", "summaryreplay_doc", True),
    FoldMapEntry("rev0078", "docs/820-ack-closure-after-restart-replay.md", "ackclosure_doc", True),
    FoldMapEntry("rev0078", "docs/821-summary-export-fence.md", "summaryexportfence_doc", True),
    FoldMapEntry("rev0078", "docs/822-summaryreplayfold-audit-refactor.md", "summaryreplayfold_doc", True),
    FoldMapEntry("rev0077", "src/i2p_dht_lab/summaryackfold.py", "predecessor_summaryackfold", False),
)
CURRENT_BY_REVISION["rev0078"] = REV0078_CURRENT
NEEDLES_BY_REVISION["rev0078"] = ("summaryreplay", "ackclosure", "summaryexportfence", "summaryreplayfold")

# rev0079 summary export receipt / import gate / retention audit active fold-map.
REV0079_CURRENT = (
    FoldMapEntry("rev0079", "src/i2p_dht_lab/summaryexportreceipt.py", "summary_export_receipt_after_export_fence", True),
    FoldMapEntry("rev0079", "src/i2p_dht_lab/summaryimportgate.py", "summary_import_gate_after_receipt", True),
    FoldMapEntry("rev0079", "src/i2p_dht_lab/exportretentionaudit.py", "export_retention_audit", True),
    FoldMapEntry("rev0079", "src/i2p_dht_lab/summaryexportreceiptfold.py", "summaryexportreceiptfold_current_audit", True),
    FoldMapEntry("rev0079", "tests/test_rev0079_summaryexportreceipt_importgate_retentionaudit.py", "current_tests", True),
    FoldMapEntry("rev0079", "docs/828-rev0079-summaryexportreceipt-importgate-retentionaudit.md", "current_revision_doc", True),
    FoldMapEntry("rev0079", "docs/829-summary-export-receipt-after-export-fence.md", "summaryexportreceipt_doc", True),
    FoldMapEntry("rev0079", "docs/830-summary-import-gate-after-receipt.md", "summaryimportgate_doc", True),
    FoldMapEntry("rev0079", "docs/831-export-retention-audit.md", "exportretentionaudit_doc", True),
    FoldMapEntry("rev0079", "docs/832-summaryexportreceiptfold-audit-refactor.md", "summaryexportreceiptfold_doc", True),
    FoldMapEntry("rev0078", "src/i2p_dht_lab/summaryreplayfold.py", "predecessor_summaryreplayfold", False),
)
CURRENT_BY_REVISION["rev0079"] = REV0079_CURRENT
NEEDLES_BY_REVISION["rev0079"] = ("summaryexportreceipt", "summaryimportgate", "exportretentionaudit", "summaryexportreceiptfold")

# rev0080 import settlement / archive / retention seal active fold-map.
REV0080_CURRENT = (
    FoldMapEntry("rev0080", "src/i2p_dht_lab/summaryimportsettlement.py", "summary_import_settlement_after_gate", True),
    FoldMapEntry("rev0080", "src/i2p_dht_lab/importarchiveledger.py", "import_archive_restart_memory", True),
    FoldMapEntry("rev0080", "src/i2p_dht_lab/importretentionseal.py", "import_retention_seal", True),
    FoldMapEntry("rev0080", "src/i2p_dht_lab/importsettlementfold.py", "importsettlementfold_current_audit", True),
    FoldMapEntry("rev0080", "tests/test_rev0080_importsettlement_archive_retentionseal.py", "current_tests", True),
    FoldMapEntry("rev0080", "docs/838-rev0080-importsettlement-archive-retentionseal.md", "current_revision_doc", True),
    FoldMapEntry("rev0080", "docs/839-summary-import-settlement-after-gate.md", "summaryimportsettlement_doc", True),
    FoldMapEntry("rev0080", "docs/840-import-archive-ledger.md", "importarchiveledger_doc", True),
    FoldMapEntry("rev0080", "docs/841-import-retention-seal.md", "importretentionseal_doc", True),
    FoldMapEntry("rev0080", "docs/842-importsettlementfold-audit-refactor.md", "importsettlementfold_doc", True),
    FoldMapEntry("rev0079", "src/i2p_dht_lab/summaryexportreceiptfold.py", "predecessor_summaryexportreceiptfold", False),
)
CURRENT_BY_REVISION["rev0080"] = REV0080_CURRENT
NEEDLES_BY_REVISION["rev0080"] = ("summaryimportsettlement", "importarchiveledger", "importretentionseal", "importsettlementfold")

# rev0081 Python-first / GCC leaf-kernel active fold-map.
REV0081_CURRENT = (
    FoldMapEntry("rev0081", "src/i2p_dht_lab/nativeboundary.py", "python_first_native_leaf_policy", True),
    FoldMapEntry("rev0081", "src/i2p_dht_lab/gccffi.py", "gcc_ffi_contract_guard", True),
    FoldMapEntry("rev0081", "src/i2p_dht_lab/nativehotpaths.py", "python_reference_native_hotpaths", True),
    FoldMapEntry("rev0081", "native/gcc/xor_distance.c", "gcc_xor_distance_leaf_kernel", True),
    FoldMapEntry("rev0081", "src/i2p_dht_lab/nativeboundaryfold.py", "nativeboundaryfold_current_audit", True),
    FoldMapEntry("rev0081", "tests/test_rev0081_nativeboundary_gccffi_hotpath.py", "current_tests", True),
    FoldMapEntry("rev0081", "docs/848-rev0081-nativeboundary-gccffi-hotpath.md", "current_revision_doc", True),
    FoldMapEntry("rev0081", "docs/849-python-first-native-leaf-boundary.md", "nativeboundary_doc", True),
    FoldMapEntry("rev0081", "docs/850-gcc-ffi-contract.md", "gccffi_doc", True),
    FoldMapEntry("rev0081", "docs/851-native-hotpath-xor-kernel.md", "nativehotpath_doc", True),
    FoldMapEntry("rev0081", "docs/852-nativeboundaryfold-audit-refactor.md", "nativeboundaryfold_doc", True),
    FoldMapEntry("rev0080", "src/i2p_dht_lab/importsettlementfold.py", "predecessor_importsettlementfold", False),
)
CURRENT_BY_REVISION["rev0081"] = REV0081_CURRENT
NEEDLES_BY_REVISION["rev0081"] = ("nativeboundary", "gccffi", "nativehotpaths", "nativeboundaryfold")

# rev0082 native parity / ABI guard / fallback seal active fold-map.
REV0082_CURRENT = (
    FoldMapEntry("rev0082", "src/i2p_dht_lab/nativeparity.py", "native_python_parity_guard", True),
    FoldMapEntry("rev0082", "src/i2p_dht_lab/abiguard.py", "native_artifact_abi_guard", True),
    FoldMapEntry("rev0082", "src/i2p_dht_lab/fallbackseal.py", "python_fallback_selection_seal", True),
    FoldMapEntry("rev0082", "src/i2p_dht_lab/nativeparityfold.py", "nativeparityfold_current_audit", True),
    FoldMapEntry("rev0082", "tests/test_rev0082_nativeparity_abiguard_fallbackseal.py", "current_tests", True),
    FoldMapEntry("rev0082", "docs/858-rev0082-nativeparity-abiguard-fallbackseal.md", "current_revision_doc", True),
    FoldMapEntry("rev0082", "docs/859-native-parity-before-selection.md", "nativeparity_doc", True),
    FoldMapEntry("rev0082", "docs/860-abi-guard-load-boundary.md", "abiguard_doc", True),
    FoldMapEntry("rev0082", "docs/861-fallback-seal-native-quarantine.md", "fallbackseal_doc", True),
    FoldMapEntry("rev0082", "docs/862-nativeparityfold-audit-refactor.md", "nativeparityfold_doc", True),
    FoldMapEntry("rev0081", "src/i2p_dht_lab/nativeboundaryfold.py", "predecessor_nativeboundaryfold", False),
)
CURRENT_BY_REVISION["rev0082"] = REV0082_CURRENT
NEEDLES_BY_REVISION["rev0082"] = ("nativeparity", "abiguard", "fallbackseal", "nativeparityfold")

# rev0083 native runtime / dispatch seal / source audit active fold-map.
REV0083_CURRENT = (
    FoldMapEntry("rev0083", "src/i2p_dht_lab/nativeruntime.py", "native_runtime_drift_guard", True),
    FoldMapEntry("rev0083", "src/i2p_dht_lab/nativedispatch.py", "native_dispatch_exact_boundary_seal", True),
    FoldMapEntry("rev0083", "src/i2p_dht_lab/nativeaudit.py", "native_source_side_effect_audit", True),
    FoldMapEntry("rev0083", "src/i2p_dht_lab/nativedispatchfold.py", "nativedispatchfold_current_audit", True),
    FoldMapEntry("rev0083", "tests/test_rev0083_nativeruntime_dispatchaudit_fallbackbudget.py", "current_tests", True),
    FoldMapEntry("rev0083", "docs/868-rev0083-nativeruntime-dispatchaudit-fallbackbudget.md", "current_revision_doc", True),
    FoldMapEntry("rev0083", "docs/869-native-runtime-drift-guard.md", "nativeruntime_doc", True),
    FoldMapEntry("rev0083", "docs/870-native-dispatch-seal.md", "nativedispatch_doc", True),
    FoldMapEntry("rev0083", "docs/871-native-source-audit.md", "nativeaudit_doc", True),
    FoldMapEntry("rev0083", "docs/872-nativedispatchfold-audit-refactor.md", "nativedispatchfold_doc", True),
    FoldMapEntry("rev0082", "src/i2p_dht_lab/nativeparityfold.py", "predecessor_nativeparityfold", False),
)
CURRENT_BY_REVISION["rev0083"] = REV0083_CURRENT
NEEDLES_BY_REVISION["rev0083"] = ("nativeruntime", "nativedispatch", "nativeaudit", "nativedispatchfold")

# rev0084 parser hold / sanitizer plan / native optimization budget fold map.
REV0084_CURRENT = (
    FoldMapEntry("rev0084", "src/i2p_dht_lab/parserhold.py", "parser_hold_python_owned_untrusted_bytes", True),
    FoldMapEntry("rev0084", "src/i2p_dht_lab/sanitizerplan.py", "sanitizer_plan_before_native_expansion", True),
    FoldMapEntry("rev0084", "src/i2p_dht_lab/nativebudget.py", "native_optimization_budget", True),
    FoldMapEntry("rev0084", "src/i2p_dht_lab/nativebudgetfold.py", "nativebudgetfold_current_audit", True),
    FoldMapEntry("rev0084", "tests/test_rev0084_parserhold_sanitizer_nativebudget.py", "current_tests", True),
    FoldMapEntry("rev0084", "docs/878-rev0084-parserhold-sanitizerplan-nativebudget.md", "current_revision_doc", True),
    FoldMapEntry("rev0084", "docs/879-parser-hold-python-owned.md", "parserhold_doc", True),
    FoldMapEntry("rev0084", "docs/880-sanitizer-plan-before-native-expansion.md", "sanitizerplan_doc", True),
    FoldMapEntry("rev0084", "docs/881-native-optimization-budget.md", "nativebudget_doc", True),
    FoldMapEntry("rev0084", "docs/882-nativebudgetfold-audit-refactor.md", "nativebudgetfold_doc", True),
)
CURRENT_BY_REVISION["rev0084"] = REV0084_CURRENT
NEEDLES_BY_REVISION["rev0084"] = ("parserhold", "sanitizerplan", "nativebudget", "nativebudgetfold")

# rev0085 native provenance / corpus / quarantine fold map.
REV0085_CURRENT = (
    FoldMapEntry("rev0085", "src/i2p_dht_lab/nativeprovenance.py", "native_build_provenance", True),
    FoldMapEntry("rev0085", "src/i2p_dht_lab/nativecorpus.py", "differential_native_corpus", True),
    FoldMapEntry("rev0085", "src/i2p_dht_lab/nativequarantine.py", "native_quarantine_store", True),
    FoldMapEntry("rev0085", "src/i2p_dht_lab/nativeprovenancefold.py", "nativeprovenancefold_current_audit", True),
    FoldMapEntry("rev0085", "tests/test_rev0085_nativeprovenance_corpus_quarantine.py", "current_tests", True),
    FoldMapEntry("rev0085", "docs/888-rev0085-nativeprovenance-corpusquarantine-buildseal.md", "current_revision_doc", True),
    FoldMapEntry("rev0085", "docs/889-native-build-provenance.md", "nativeprovenance_doc", True),
    FoldMapEntry("rev0085", "docs/890-differential-native-corpus.md", "nativecorpus_doc", True),
    FoldMapEntry("rev0085", "docs/891-native-quarantine-store.md", "nativequarantine_doc", True),
    FoldMapEntry("rev0085", "docs/892-nativeprovenancefold-audit-refactor.md", "nativeprovenancefold_doc", True),
    FoldMapEntry("rev0084", "src/i2p_dht_lab/nativebudgetfold.py", "predecessor_nativebudgetfold", False),
)
CURRENT_BY_REVISION["rev0085"] = REV0085_CURRENT
NEEDLES_BY_REVISION["rev0085"] = ("nativeprovenance", "nativecorpus", "nativequarantine", "nativeprovenancefold")

# rev0086 native selection / fallback journal / promotion hold fold map.
REV0086_CURRENT = (
    FoldMapEntry("rev0086", "src/i2p_dht_lab/nativeselection.py", "native_selection_exact_boundary", True),
    FoldMapEntry("rev0086", "src/i2p_dht_lab/fallbackjournal.py", "fallback_journal_restart_memory", True),
    FoldMapEntry("rev0086", "src/i2p_dht_lab/nativepromotion.py", "native_promotion_hold", True),
    FoldMapEntry("rev0086", "src/i2p_dht_lab/nativeselectionfold.py", "nativeselectionfold_current_audit", True),
    FoldMapEntry("rev0086", "tests/test_rev0086_nativeselection_fallbackjournal_promotehold.py", "current_tests", True),
    FoldMapEntry("rev0086", "docs/898-rev0086-nativeselection-fallbackjournal-promotehold.md", "current_revision_doc", True),
    FoldMapEntry("rev0086", "docs/899-native-selection-exact-boundary.md", "nativeselection_doc", True),
    FoldMapEntry("rev0086", "docs/900-fallback-journal-restart-memory.md", "fallbackjournal_doc", True),
    FoldMapEntry("rev0086", "docs/901-native-promotion-hold.md", "nativepromotion_doc", True),
    FoldMapEntry("rev0086", "docs/902-nativeselectionfold-audit-refactor.md", "nativeselectionfold_doc", True),
    FoldMapEntry("rev0085", "src/i2p_dht_lab/nativeprovenancefold.py", "predecessor_nativeprovenancefold", False),
)
CURRENT_BY_REVISION["rev0086"] = REV0086_CURRENT
NEEDLES_BY_REVISION["rev0086"] = ("nativeselection", "fallbackjournal", "nativepromotion", "nativeselectionfold")

# rev0087 native load / crash ledger / performance guard fold map.
REV0087_CURRENT = (
    FoldMapEntry("rev0087", "src/i2p_dht_lab/nativeload.py", "native_load_lifecycle_boundary", True),
    FoldMapEntry("rev0087", "src/i2p_dht_lab/nativecrashledger.py", "native_crash_ledger", True),
    FoldMapEntry("rev0087", "src/i2p_dht_lab/nativeperfguard.py", "native_performance_guard", True),
    FoldMapEntry("rev0087", "src/i2p_dht_lab/nativelifecyclefold.py", "nativelifecyclefold_current_audit", True),
    FoldMapEntry("rev0087", "tests/test_rev0087_nativeload_crashledger_perfguard.py", "current_tests", True),
    FoldMapEntry("rev0087", "docs/908-rev0087-nativeload-crashledger-perfguard.md", "current_revision_doc", True),
    FoldMapEntry("rev0087", "docs/909-native-load-lifecycle-boundary.md", "nativeload_doc", True),
    FoldMapEntry("rev0087", "docs/910-native-crash-ledger.md", "nativecrashledger_doc", True),
    FoldMapEntry("rev0087", "docs/911-native-performance-guard.md", "nativeperfguard_doc", True),
    FoldMapEntry("rev0087", "docs/912-nativelifecyclefold-audit-refactor.md", "nativelifecyclefold_doc", True),
    FoldMapEntry("rev0086", "src/i2p_dht_lab/nativeselectionfold.py", "predecessor_nativeselectionfold", False),
)
CURRENT_BY_REVISION["rev0087"] = REV0087_CURRENT
NEEDLES_BY_REVISION["rev0087"] = ("nativeload", "nativecrashledger", "nativeperfguard", "nativelifecyclefold")

# rev0088 native unload / sandbox-stub / crash-GC fold map.
REV0088_CURRENT = (
    FoldMapEntry("rev0088", "src/i2p_dht_lab/nativeunload.py", "native_unload_quarantine_boundary", True),
    FoldMapEntry("rev0088", "src/i2p_dht_lab/nativesandboxstub.py", "native_sandbox_stub_no_network_boundary", True),
    FoldMapEntry("rev0088", "src/i2p_dht_lab/nativecrashgc.py", "native_crash_ledger_gc", True),
    FoldMapEntry("rev0088", "src/i2p_dht_lab/nativecontrolfold.py", "nativecontrolfold_current_audit", True),
    FoldMapEntry("rev0088", "tests/test_rev0088_nativeunload_sandboxstub_crashgc.py", "current_tests", True),
    FoldMapEntry("rev0088", "docs/918-rev0088-nativeunload-sandboxstub-crashgc.md", "current_revision_doc", True),
    FoldMapEntry("rev0088", "docs/919-native-unload-quarantine-boundary.md", "nativeunload_doc", True),
    FoldMapEntry("rev0088", "docs/920-native-sandbox-stub.md", "nativesandboxstub_doc", True),
    FoldMapEntry("rev0088", "docs/921-native-crash-gc.md", "nativecrashgc_doc", True),
    FoldMapEntry("rev0088", "docs/922-nativecontrolfold-audit-refactor.md", "nativecontrolfold_doc", True),
    FoldMapEntry("rev0087", "src/i2p_dht_lab/nativelifecyclefold.py", "predecessor_nativelifecyclefold", False),
)
CURRENT_BY_REVISION["rev0088"] = REV0088_CURRENT
NEEDLES_BY_REVISION["rev0088"] = ("nativeunload", "nativesandboxstub", "nativecrashgc", "nativecontrolfold")

# rev0089 native cold-start / probe corpus / loader-GC fold map.
REV0089_CURRENT = (
    FoldMapEntry("rev0089", "src/i2p_dht_lab/nativecoldstart.py", "native_cold_start_after_unload", True),
    FoldMapEntry("rev0089", "src/i2p_dht_lab/probecorpus.py", "native_probe_corpus_refresh", True),
    FoldMapEntry("rev0089", "src/i2p_dht_lab/loadergc.py", "native_loader_gc_tombstone_memory", True),
    FoldMapEntry("rev0089", "src/i2p_dht_lab/nativecoldfold.py", "nativecoldfold_current_audit", True),
    FoldMapEntry("rev0089", "tests/test_rev0089_nativecoldstart_probecorpus_loadergc.py", "current_tests", True),
    FoldMapEntry("rev0089", "docs/928-rev0089-nativecoldstart-probecorpus-loadergc.md", "current_revision_doc", True),
    FoldMapEntry("rev0089", "docs/929-native-cold-start-after-unload.md", "nativecoldstart_doc", True),
    FoldMapEntry("rev0089", "docs/930-probe-corpus-refresh.md", "probecorpus_doc", True),
    FoldMapEntry("rev0089", "docs/931-loader-gc-after-cold-start.md", "loadergc_doc", True),
    FoldMapEntry("rev0089", "docs/932-nativecoldfold-audit-refactor.md", "nativecoldfold_doc", True),
    FoldMapEntry("rev0088", "src/i2p_dht_lab/nativecontrolfold.py", "predecessor_nativecontrolfold", False),
)
CURRENT_BY_REVISION["rev0089"] = REV0089_CURRENT
NEEDLES_BY_REVISION["rev0089"] = ("nativecoldstart", "probecorpus", "loadergc", "nativecoldfold")

# rev0090 native handoff / relaunch gate / loader seal fold map.
REV0090_CURRENT = (
    FoldMapEntry("rev0090", "src/i2p_dht_lab/nativehandoff.py", "native_handoff_relaunch_candidate", True),
    FoldMapEntry("rev0090", "src/i2p_dht_lab/relaunchgate.py", "native_relaunch_gate_prior_lane_revalidation", True),
    FoldMapEntry("rev0090", "src/i2p_dht_lab/loaderseal.py", "native_loader_seal_restart_memory", True),
    FoldMapEntry("rev0090", "src/i2p_dht_lab/nativefoldspine.py", "native_fold_spine_audit_refactor", True),
    FoldMapEntry("rev0090", "src/i2p_dht_lab/nativehandofffold.py", "nativehandofffold_current_audit", True),
    FoldMapEntry("rev0090", "tests/test_rev0090_nativehandoff_relaunchgate_loaderseal.py", "current_tests", True),
    FoldMapEntry("rev0090", "docs/938-rev0090-nativehandoff-relaunchgate-loaderseal.md", "current_revision_doc", True),
    FoldMapEntry("rev0090", "docs/939-native-handoff-relaunch-candidate.md", "nativehandoff_doc", True),
    FoldMapEntry("rev0090", "docs/940-relaunch-gate-prior-lanes.md", "relaunchgate_doc", True),
    FoldMapEntry("rev0090", "docs/941-loader-seal-restart-memory.md", "loaderseal_doc", True),
    FoldMapEntry("rev0090", "docs/942-native-fold-spine-audit-refactor.md", "nativefoldspine_doc", True),
    FoldMapEntry("rev0089", "src/i2p_dht_lab/nativecoldfold.py", "predecessor_nativecoldfold", False),
)
CURRENT_BY_REVISION["rev0090"] = REV0090_CURRENT
NEEDLES_BY_REVISION["rev0090"] = ("nativehandoff", "relaunchgate", "loaderseal", "nativefoldspine", "nativehandofffold")


# rev0091 native oracle seal / preflight / re-entry journal fold map.
REV0091_CURRENT = (
    FoldMapEntry("rev0091", "src/i2p_dht_lab/nativeoracleseal.py", "python_oracle_seal", True),
    FoldMapEntry("rev0091", "src/i2p_dht_lab/nativepreflight.py", "route_to_load_gate_only", True),
    FoldMapEntry("rev0091", "src/i2p_dht_lab/nativereentryjournal.py", "native_reentry_journal", True),
    FoldMapEntry("rev0091", "src/i2p_dht_lab/nativefoldspine.py", "native_fold_spine_audit_refactor", True),
    FoldMapEntry("rev0091", "src/i2p_dht_lab/nativereentryfold.py", "nativereentryfold_current_audit", True),
    FoldMapEntry("rev0091", "tests/test_rev0091_nativereentry_oracleseal_preflight.py", "current_tests", True),
    FoldMapEntry("rev0091", "docs/948-rev0091-nativereentry-oracleseal-preflight.md", "current_revision_doc", True),
    FoldMapEntry("rev0091", "docs/949-native-oracle-seal.md", "nativeoracleseal_doc", True),
    FoldMapEntry("rev0091", "docs/950-native-preflight-route-to-load-gate.md", "nativepreflight_doc", True),
    FoldMapEntry("rev0091", "docs/951-native-reentry-journal.md", "nativereentryjournal_doc", True),
    FoldMapEntry("rev0091", "docs/952-nativereentryfold-audit-refactor.md", "nativereentryfold_doc", True),
    FoldMapEntry("rev0090", "src/i2p_dht_lab/nativehandofffold.py", "predecessor_nativehandofffold", False),
)
CURRENT_BY_REVISION["rev0091"] = REV0091_CURRENT
NEEDLES_BY_REVISION["rev0091"] = ("nativeoracleseal", "nativepreflight", "nativereentryjournal", "nativereentryfold", "nativefoldspine")

# rev0092 native load re-entry / revalidation seal / call hold fold map.
REV0092_CURRENT = (
    FoldMapEntry("rev0092", "src/i2p_dht_lab/nativeloadreentry.py", "native_load_reentry_request_only", True),
    FoldMapEntry("rev0092", "src/i2p_dht_lab/revalidationseal.py", "prior_native_lane_revalidation_seal", True),
    FoldMapEntry("rev0092", "src/i2p_dht_lab/nativecallhold.py", "native_call_hold_python_fallback", True),
    FoldMapEntry("rev0092", "src/i2p_dht_lab/nativefoldspine.py", "native_fold_spine_audit_refactor", True),
    FoldMapEntry("rev0092", "src/i2p_dht_lab/nativeloadreentryfold.py", "nativeloadreentryfold_current_audit", True),
    FoldMapEntry("rev0092", "tests/test_rev0092_nativeloadreentry_revalidationseal_callhold.py", "current_tests", True),
    FoldMapEntry("rev0092", "docs/958-rev0092-nativeloadreentry-revalidationseal-callhold.md", "current_revision_doc", True),
    FoldMapEntry("rev0092", "docs/959-native-load-reentry-request.md", "nativeloadreentry_doc", True),
    FoldMapEntry("rev0092", "docs/960-revalidation-seal-prior-lanes.md", "revalidationseal_doc", True),
    FoldMapEntry("rev0092", "docs/961-native-call-hold.md", "nativecallhold_doc", True),
    FoldMapEntry("rev0092", "docs/962-nativeloadreentryfold-audit-refactor.md", "nativeloadreentryfold_doc", True),
    FoldMapEntry("rev0091", "src/i2p_dht_lab/nativereentryfold.py", "predecessor_nativereentryfold", False),
)
CURRENT_BY_REVISION["rev0092"] = REV0092_CURRENT
NEEDLES_BY_REVISION["rev0092"] = ("nativeloadreentry", "revalidationseal", "nativecallhold", "nativeloadreentryfold", "nativefoldspine")

# rev0093 native load loop / call canary / dispatch fence fold map.
REV0093_CURRENT = (
    FoldMapEntry("rev0093", "src/i2p_dht_lab/nativeloadloop.py", "native_load_loopback_held_on_python", True),
    FoldMapEntry("rev0093", "src/i2p_dht_lab/nativecallcanary.py", "native_call_canary_python_result", True),
    FoldMapEntry("rev0093", "src/i2p_dht_lab/dispatchfence.py", "native_dispatch_fence_python_route", True),
    FoldMapEntry("rev0093", "src/i2p_dht_lab/nativefoldspine.py", "native_fold_spine_audit_refactor", True),
    FoldMapEntry("rev0093", "src/i2p_dht_lab/nativeloadloopfold.py", "nativeloadloopfold_current_audit", True),
    FoldMapEntry("rev0093", "tests/test_rev0093_nativeloadloop_callcanary_dispatchfence.py", "current_tests", True),
    FoldMapEntry("rev0093", "docs/968-rev0093-nativeloadloop-callcanary-dispatchfence.md", "current_revision_doc", True),
    FoldMapEntry("rev0093", "docs/969-native-load-loopback.md", "nativeloadloop_doc", True),
    FoldMapEntry("rev0093", "docs/970-native-call-canary.md", "nativecallcanary_doc", True),
    FoldMapEntry("rev0093", "docs/971-dispatch-fence.md", "dispatchfence_doc", True),
    FoldMapEntry("rev0093", "docs/972-nativeloadloopfold-audit-refactor.md", "nativeloadloopfold_doc", True),
    FoldMapEntry("rev0092", "src/i2p_dht_lab/nativeloadreentryfold.py", "predecessor_nativeloadreentryfold", False),
)
CURRENT_BY_REVISION["rev0093"] = REV0093_CURRENT
NEEDLES_BY_REVISION["rev0093"] = ("nativeloadloop", "nativecallcanary", "dispatchfence", "nativeloadloopfold", "nativefoldspine")

# rev0094 native shadow-call / result-diff / fault-seal fold map.
REV0094_CURRENT = (
    FoldMapEntry("rev0094", "src/i2p_dht_lab/nativeshadowcall.py", "native_shadow_call_evidence_only", True),
    FoldMapEntry("rev0094", "src/i2p_dht_lab/resultdiff.py", "native_result_diff_python_oracle", True),
    FoldMapEntry("rev0094", "src/i2p_dht_lab/faultseal.py", "native_fault_seal_to_fallback", True),
    FoldMapEntry("rev0094", "src/i2p_dht_lab/nativefoldspine.py", "native_fold_spine_audit_refactor", True),
    FoldMapEntry("rev0094", "src/i2p_dht_lab/nativeshadowfold.py", "nativeshadowfold_current_audit", True),
    FoldMapEntry("rev0094", "tests/test_rev0094_nativeshadowcall_resultdiff_faultseal.py", "current_tests", True),
    FoldMapEntry("rev0094", "docs/978-rev0094-nativeshadowcall-resultdiff-faultseal.md", "current_revision_doc", True),
    FoldMapEntry("rev0094", "docs/979-native-shadow-call.md", "nativeshadowcall_doc", True),
    FoldMapEntry("rev0094", "docs/980-native-result-diff.md", "resultdiff_doc", True),
    FoldMapEntry("rev0094", "docs/981-native-fault-seal.md", "faultseal_doc", True),
    FoldMapEntry("rev0094", "docs/982-nativeshadowfold-audit-refactor.md", "nativeshadowfold_doc", True),
    FoldMapEntry("rev0093", "src/i2p_dht_lab/nativeloadloopfold.py", "predecessor_nativeloadloopfold", False),
)
CURRENT_BY_REVISION["rev0094"] = REV0094_CURRENT
NEEDLES_BY_REVISION["rev0094"] = ("nativeshadowcall", "resultdiff", "faultseal", "nativeshadowfold", "nativefoldspine")

# rev0095 native shadow-settlement / admission / call ledger fold map.
REV0095_CURRENT = (
    FoldMapEntry("rev0095", "src/i2p_dht_lab/nativeshadowsettlement.py", "native_shadow_settlement_evidence", True),
    FoldMapEntry("rev0095", "src/i2p_dht_lab/nativeadmission.py", "native_admission_held_shadow_slot", True),
    FoldMapEntry("rev0095", "src/i2p_dht_lab/nativecallledger.py", "native_call_ledger_python_route", True),
    FoldMapEntry("rev0095", "src/i2p_dht_lab/nativefoldspine.py", "native_fold_spine_audit_refactor", True),
    FoldMapEntry("rev0095", "src/i2p_dht_lab/nativesettlementfold.py", "nativesettlementfold_current_audit", True),
    FoldMapEntry("rev0095", "tests/test_rev0095_shadowsettlement_admission_callledger.py", "current_tests", True),
    FoldMapEntry("rev0095", "docs/988-rev0095-shadowsettlement-admission-callledger.md", "current_revision_doc", True),
    FoldMapEntry("rev0095", "docs/989-native-shadow-settlement.md", "nativeshadowsettlement_doc", True),
    FoldMapEntry("rev0095", "docs/990-native-admission-held.md", "nativeadmission_doc", True),
    FoldMapEntry("rev0095", "docs/991-native-call-ledger.md", "nativecallledger_doc", True),
    FoldMapEntry("rev0095", "docs/992-nativesettlementfold-audit-refactor.md", "nativesettlementfold_doc", True),
    FoldMapEntry("rev0094", "src/i2p_dht_lab/nativeshadowfold.py", "predecessor_nativeshadowfold", False),
)
CURRENT_BY_REVISION["rev0095"] = REV0095_CURRENT
NEEDLES_BY_REVISION["rev0095"] = ("nativeshadowsettlement", "nativeadmission", "nativecallledger", "nativesettlementfold", "nativefoldspine")

# rev0096 native call archive / promotion denial / shadow-GC fold map.
REV0096_CURRENT = (
    FoldMapEntry("rev0096", "src/i2p_dht_lab/nativecallarchive.py", "native_call_archive_python_route_memory", True),
    FoldMapEntry("rev0096", "src/i2p_dht_lab/nativepromotiondeny.py", "native_promotion_denial_after_shadow_match", True),
    FoldMapEntry("rev0096", "src/i2p_dht_lab/nativeshadowgc.py", "native_shadow_gc_preserving_python_route", True),
    FoldMapEntry("rev0096", "src/i2p_dht_lab/nativefoldspine.py", "native_fold_spine_audit_through_rev0096", True),
    FoldMapEntry("rev0096", "src/i2p_dht_lab/nativearchivefold.py", "nativearchivefold_current_audit", True),
    FoldMapEntry("rev0096", "tests/test_rev0096_callarchive_promotedeny_shadowgc.py", "current_tests", True),
    FoldMapEntry("rev0096", "docs/998-rev0096-callarchive-promotedeny-shadowgc.md", "current_revision_doc", True),
    FoldMapEntry("rev0096", "docs/999-native-call-archive.md", "nativecallarchive_doc", True),
    FoldMapEntry("rev0096", "docs/1000-native-promotion-denial.md", "nativepromotiondeny_doc", True),
    FoldMapEntry("rev0096", "docs/1001-native-shadow-gc.md", "nativeshadowgc_doc", True),
    FoldMapEntry("rev0096", "docs/1002-nativearchivefold-audit-refactor.md", "nativearchivefold_doc", True),
    FoldMapEntry("rev0095", "src/i2p_dht_lab/nativesettlementfold.py", "predecessor_nativesettlementfold", False),
)
CURRENT_BY_REVISION["rev0096"] = REV0096_CURRENT
NEEDLES_BY_REVISION["rev0096"] = ("nativecallarchive", "nativepromotiondeny", "nativeshadowgc", "nativearchivefold", "nativefoldspine")

# rev0097 native archive replay / promotion review / compact fold spine fold map.
REV0097_CURRENT = (
    FoldMapEntry("rev0097", "src/i2p_dht_lab/nativearchivereplay.py", "native_archive_replay_restart_memory", True),
    FoldMapEntry("rev0097", "src/i2p_dht_lab/nativepromotereview.py", "native_promotion_review_held", True),
    FoldMapEntry("rev0097", "src/i2p_dht_lab/nativefoldspine.py", "native_fold_spine_compact_refactor", True),
    FoldMapEntry("rev0097", "src/i2p_dht_lab/nativearchivereplayfold.py", "nativearchivereplayfold_current_audit", True),
    FoldMapEntry("rev0097", "tests/test_rev0097_nativearchivereplay_promotereview_spinecompact.py", "current_tests", True),
    FoldMapEntry("rev0097", "docs/1008-rev0097-nativearchivereplay-promotereview-spinecompact.md", "current_revision_doc", True),
    FoldMapEntry("rev0097", "docs/1009-native-archive-replay.md", "nativearchivereplay_doc", True),
    FoldMapEntry("rev0097", "docs/1010-native-promotion-review-held.md", "nativepromotereview_doc", True),
    FoldMapEntry("rev0097", "docs/1011-native-fold-spine-compact-refactor.md", "nativefoldspine_doc", True),
    FoldMapEntry("rev0097", "docs/1012-nativearchivereplayfold-audit-refactor.md", "nativearchivereplayfold_doc", True),
    FoldMapEntry("rev0096", "src/i2p_dht_lab/nativearchivefold.py", "predecessor_nativearchivefold", False),
)
CURRENT_BY_REVISION["rev0097"] = REV0097_CURRENT
NEEDLES_BY_REVISION["rev0097"] = ("nativearchivereplay", "nativepromotereview", "nativearchivereplayfold", "nativefoldspine")

# rev0098 native branch-close / promotion archive / shadow-only policy fold map.
REV0098_CURRENT = (
    FoldMapEntry("rev0098", "src/i2p_dht_lab/nativepromotearchive.py", "native_promotion_review_archive", True),
    FoldMapEntry("rev0098", "src/i2p_dht_lab/nativepromotionpolicy.py", "native_shadow_only_policy", True),
    FoldMapEntry("rev0098", "src/i2p_dht_lab/nativebranchclose.py", "native_branch_close_shadow_only", True),
    FoldMapEntry("rev0098", "src/i2p_dht_lab/nativefoldspine.py", "native_fold_spine_through_rev0098", True),
    FoldMapEntry("rev0098", "src/i2p_dht_lab/nativebranchclosefold.py", "nativebranchclosefold_current_audit", True),
    FoldMapEntry("rev0098", "tests/test_rev0098_nativebranchclose_promotearchive_policy.py", "current_tests", True),
    FoldMapEntry("rev0098", "docs/1018-rev0098-nativebranchclose-promotearchive-policyseal.md", "current_revision_doc", True),
    FoldMapEntry("rev0098", "docs/1019-native-promotion-archive.md", "nativepromotearchive_doc", True),
    FoldMapEntry("rev0098", "docs/1020-native-promotion-policy-shadow-only.md", "nativepromotionpolicy_doc", True),
    FoldMapEntry("rev0098", "docs/1021-native-branch-close.md", "nativebranchclose_doc", True),
    FoldMapEntry("rev0098", "docs/1022-nativebranchclosefold-audit-refactor.md", "nativebranchclosefold_doc", True),
    FoldMapEntry("rev0097", "src/i2p_dht_lab/nativearchivereplayfold.py", "predecessor_nativearchivereplayfold", False),
)
CURRENT_BY_REVISION["rev0098"] = REV0098_CURRENT
NEEDLES_BY_REVISION["rev0098"] = ("nativepromotearchive", "nativepromotionpolicy", "nativebranchclose", "nativebranchclosefold", "nativefoldspine")

# rev0099 return from native branch to Python-owned DHT substrate record plane.
REV0099_CURRENT = (
    FoldMapEntry("rev0099", "src/i2p_dht_lab/recordplaneoracle.py", "python_owned_record_plane_oracle", True),
    FoldMapEntry("rev0099", "src/i2p_dht_lab/substratereentry.py", "substrate_reentry_after_native_close", True),
    FoldMapEntry("rev0099", "src/i2p_dht_lab/nativefoldspine.py", "native_fold_spine_through_rev0099", True),
    FoldMapEntry("rev0099", "src/i2p_dht_lab/substratereturnfold.py", "substratereturnfold_current_audit", True),
    FoldMapEntry("rev0099", "tests/test_rev0099_substratereturn_recordoracle_spineaudit.py", "current_tests", True),
    FoldMapEntry("rev0099", "docs/1028-rev0099-substratereturn-recordoracle-spineaudit.md", "current_revision_doc", True),
    FoldMapEntry("rev0099", "docs/1029-record-plane-oracle-after-native-close.md", "recordplaneoracle_doc", True),
    FoldMapEntry("rev0099", "docs/1030-substrate-reentry-after-native-close.md", "substratereentry_doc", True),
    FoldMapEntry("rev0099", "docs/1031-substratereturnfold-audit-refactor.md", "substratereturnfold_doc", True),
    FoldMapEntry("rev0098", "src/i2p_dht_lab/nativebranchclosefold.py", "predecessor_nativebranchclosefold", False),
)
CURRENT_BY_REVISION["rev0099"] = REV0099_CURRENT
NEEDLES_BY_REVISION["rev0099"] = ("recordplaneoracle", "substratereentry", "substratereturnfold", "nativebranchclosefold", "nativefoldspine")

# rev0100 substrate record ingress / provider semantics / routing anchor fold map.
REV0100_CURRENT = (
    FoldMapEntry("rev0100", "src/i2p_dht_lab/recordingress.py", "python_owned_record_ingress_gate", True),
    FoldMapEntry("rev0100", "src/i2p_dht_lab/providersemantics.py", "provider_semantic_proof_join", True),
    FoldMapEntry("rev0100", "src/i2p_dht_lab/routinganchor.py", "i2p_routing_anchor_gate", True),
    FoldMapEntry("rev0100", "src/i2p_dht_lab/substratespine.py", "substrate_spine_after_native_return", True),
    FoldMapEntry("rev0100", "src/i2p_dht_lab/substratecenturyfold.py", "substratecenturyfold_current_audit", True),
    FoldMapEntry("rev0100", "tests/test_rev0100_recordingress_providersemantics_routingspine.py", "current_tests", True),
    FoldMapEntry("rev0100", "docs/1038-rev0100-recordingress-providersemantics-routingspine.md", "current_revision_doc", True),
    FoldMapEntry("rev0100", "docs/1039-record-ingress-after-substrate-return.md", "recordingress_doc", True),
    FoldMapEntry("rev0100", "docs/1040-provider-semantics-after-record-ingress.md", "providersemantics_doc", True),
    FoldMapEntry("rev0100", "docs/1041-routing-anchor-after-record-ingress.md", "routinganchor_doc", True),
    FoldMapEntry("rev0100", "docs/1042-substrate-spine-century-audit.md", "substrate_spine_doc", True),
    FoldMapEntry("rev0099", "src/i2p_dht_lab/substratereturnfold.py", "predecessor_substratereturnfold", False),
)
CURRENT_BY_REVISION["rev0100"] = REV0100_CURRENT
NEEDLES_BY_REVISION["rev0100"] = ("recordingress", "providersemantics", "routinganchor", "substratespine", "substratecenturyfold")

# rev0101 mutable placement / provider bucket / route storage fold map.
REV0101_CURRENT = (
    FoldMapEntry("rev0101", "src/i2p_dht_lab/mutableplacement.py", "mutable_head_observation_placement", True),
    FoldMapEntry("rev0101", "src/i2p_dht_lab/providerbucket.py", "provider_index_bucket_admission", True),
    FoldMapEntry("rev0101", "src/i2p_dht_lab/routestorage.py", "routing_table_storage_gate", True),
    FoldMapEntry("rev0101", "src/i2p_dht_lab/substratespine.py", "substrate_spine_after_record_ingress", True),
    FoldMapEntry("rev0101", "src/i2p_dht_lab/substrateplacementfold.py", "substrateplacementfold_current_audit", True),
    FoldMapEntry("rev0101", "tests/test_rev0101_mutableplace_providerbucket_routestorage.py", "current_tests", True),
    FoldMapEntry("rev0101", "docs/1048-rev0101-mutableplace-providerbucket-routestorage.md", "current_revision_doc", True),
    FoldMapEntry("rev0101", "docs/1049-mutable-placement-after-record-ingress.md", "mutableplacement_doc", True),
    FoldMapEntry("rev0101", "docs/1050-provider-bucket-after-provider-semantics.md", "providerbucket_doc", True),
    FoldMapEntry("rev0101", "docs/1051-route-storage-after-routing-anchor.md", "routestorage_doc", True),
    FoldMapEntry("rev0101", "docs/1052-substrate-placementfold-audit.md", "substrateplacementfold_doc", True),
    FoldMapEntry("rev0100", "src/i2p_dht_lab/substratecenturyfold.py", "predecessor_substratecenturyfold", False),
)
CURRENT_BY_REVISION["rev0101"] = REV0101_CURRENT
NEEDLES_BY_REVISION["rev0101"] = ("mutableplacement", "providerbucket", "routestorage", "substratespine", "substrateplacementfold")
