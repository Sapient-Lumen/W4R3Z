"""Small active-surface ledger for cube audit/refactor work.

The cube has many historical modules. Deleting history is bad for
wake-from-amnesia, but active surfaces should still be named deliberately. This
module audits a tiny declarative ledger: current modules, their tests, and their
docs. It is intentionally weaker than a packaging manifest and stronger than a
human promise buried in prose.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bencode import bencode
from .ids import DOMAIN, sha256

SURFACE_LEDGER_DOMAIN = DOMAIN + b":surface-ledger-v1:"


@dataclass(frozen=True)
class SurfaceLedgerEntry:
    module: str
    test: str
    doc: str
    role: str

    def bvalue(self) -> dict[bytes, object]:
        return {b"module": self.module, b"test": self.test, b"doc": self.doc, b"role": self.role}


@dataclass(frozen=True)
class SurfaceLedgerFinding:
    severity: str
    code: str
    path: str
    detail: str


@dataclass(frozen=True)
class SurfaceLedgerReport:
    entries: tuple[SurfaceLedgerEntry, ...]
    findings: tuple[SurfaceLedgerFinding, ...]
    digest: bytes

    @property
    def ok(self) -> bool:
        return not any(finding.severity == "error" for finding in self.findings)

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")


def rev0019_entries() -> tuple[SurfaceLedgerEntry, ...]:
    return (
        SurfaceLedgerEntry("src/i2p_dht_lab/storeflight.py", "tests/test_rev0019_storeflight_leasequorum_surfaceclean.py", "docs/164-store-flight-durability-pressure.md", "garden store-flight admission/eviction/custody receipts"),
        SurfaceLedgerEntry("src/i2p_dht_lab/leasequorum.py", "tests/test_rev0019_storeflight_leasequorum_surfaceclean.py", "docs/165-lease-quorum-entrance-pressure.md", "channel-diverse contact lease quorum pressure"),
        SurfaceLedgerEntry("src/i2p_dht_lab/surfaceclean.py", "tests/test_rev0019_storeflight_leasequorum_surfaceclean.py", "docs/166-surface-clean-active-pointer-audit.md", "active revision pointer cleanup audit"),
        SurfaceLedgerEntry("src/i2p_dht_lab/budgetreceipt.py", "tests/test_rev0019_storeflight_leasequorum_surfaceclean.py", "docs/170-garden-budget-receipts-rev0019.md", "signed garden budget/throttle receipts"),
        SurfaceLedgerEntry("src/i2p_dht_lab/leaseroute.py", "tests/test_rev0019_leaseroute_storemesh_budgetreceipt.py", "docs/171-lease-route-gossip-pressure-rev0019.md", "contact leases bound to route-gossip repair"),
        SurfaceLedgerEntry("src/i2p_dht_lab/storemesh.py", "tests/test_rev0019_leaseroute_storemesh_budgetreceipt.py", "docs/172-store-mesh-tombstone-repair-rev0019.md", "store acknowledgements joined across mutable/provider/tombstone rounds"),
        SurfaceLedgerEntry("src/i2p_dht_lab/roundledger.py", "tests/test_rev0019_leaseroute_storemesh_budgetreceipt.py", "docs/173-repeated-round-ledger-rev0019.md", "repeated-round liveness/proof/witness coupling"),
        SurfaceLedgerEntry("src/i2p_dht_lab/storecontract.py", "tests/test_rev0019_custodylease_storeflight.py", "docs/174-store-contract-and-custody-lease.md", "signed exact-digest store contracts"),
        SurfaceLedgerEntry("src/i2p_dht_lab/custodyaudit.py", "tests/test_rev0019_custodylease_storeflight.py", "docs/175-custody-audit-challenge-proofs.md", "challenge-bound custody proof audits"),
        SurfaceLedgerEntry("src/i2p_dht_lab/storerepair.py", "tests/test_rev0019_custodylease_storeflight.py", "docs/176-store-repair-planning.md", "repair planning for leases/audits/refusals"),
        SurfaceLedgerEntry("src/i2p_dht_lab/surfaceledger.py", "tests/test_rev0019_custodylease_storeflight.py", "docs/167-python-surface-rev0019.md", "active module/test/doc ledger"),
    )


def rev0020_entries() -> tuple[SurfaceLedgerEntry, ...]:
    return rev0019_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/epochgate.py", "tests/test_rev0020_epochgate_repairmarket_wirecanon.py", "docs/181-epoch-gated-mutable-heads.md", "epoch-gated mutable control-plane heads"),
        SurfaceLedgerEntry("src/i2p_dht_lab/repairmarket.py", "tests/test_rev0020_epochgate_repairmarket_wirecanon.py", "docs/182-repair-market-without-authority.md", "garden repair-capacity selection without authority"),
        SurfaceLedgerEntry("src/i2p_dht_lab/wirecanon.py", "tests/test_rev0020_epochgate_repairmarket_wirecanon.py", "docs/183-wire-canonicalization-before-live-transport.md", "transport-neutral canonical frame fixtures"),
        SurfaceLedgerEntry("src/i2p_dht_lab/surfacefold.py", "tests/test_rev0020_epochgate_repairmarket_wirecanon.py", "docs/184-surface-fold-audit-refactor.md", "current-revision surface fold audit"),
    )


def rev0021_entries() -> tuple[SurfaceLedgerEntry, ...]:
    return rev0020_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/epochsplit.py", "tests/test_rev0021_epochsplit_storewire_repairreplay.py", "docs/189-epoch-split-view-pressure.md", "repeated mutable epoch split-view and stale replay pressure"),
        SurfaceLedgerEntry("src/i2p_dht_lab/storewire.py", "tests/test_rev0021_epochsplit_storewire_repairreplay.py", "docs/190-store-wire-custody-transcripts.md", "STORE/custody canonical wire transcript fixtures"),
        SurfaceLedgerEntry("src/i2p_dht_lab/repairreplay.py", "tests/test_rev0021_epochsplit_storewire_repairreplay.py", "docs/191-repair-market-replay-pressure.md", "repair-market replay and colluding-family pressure across windows"),
    )


def rev0022_entries() -> tuple[SurfaceLedgerEntry, ...]:
    return rev0021_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/parseguard.py", "tests/test_rev0022_antientropy_validatorwall_parseguard.py", "docs/197-parseguard-canonical-decode-pressure.md", "bounded canonical bdecode before network byte parsing"),
        SurfaceLedgerEntry("src/i2p_dht_lab/validatorwall.py", "tests/test_rev0022_antientropy_validatorwall_parseguard.py", "docs/198-validator-wall-before-dispatch.md", "semantic validation wall before DHT handler dispatch"),
        SurfaceLedgerEntry("src/i2p_dht_lab/antientropy.py", "tests/test_rev0022_antientropy_validatorwall_parseguard.py", "docs/199-anti-entropy-summary-pressure.md", "signed anti-entropy summaries for repair planning, not truth"),
        SurfaceLedgerEntry("src/i2p_dht_lab/surfaceindex.py", "tests/test_rev0022_antientropy_validatorwall_parseguard.py", "docs/200-surface-index-audit-refactor.md", "current-revision surface index navigation audit"),
    )


def rev0023_entries() -> tuple[SurfaceLedgerEntry, ...]:
    return rev0022_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/rangesketch.py", "tests/test_rev0023_rangesketch_admission_namespace.py", "docs/205-range-sketch-anti-entropy.md", "range-sketch anti-entropy repair hints and tombstone-first pressure"),
        SurfaceLedgerEntry("src/i2p_dht_lab/admissionwall.py", "tests/test_rev0023_rangesketch_admission_namespace.py", "docs/206-admission-wall-before-expensive-work.md", "namespace/family/budget admission wall before expensive handler work"),
        SurfaceLedgerEntry("src/i2p_dht_lab/namespaceregistry.py", "tests/test_rev0023_rangesketch_admission_namespace.py", "docs/207-namespace-registry-validator-policy.md", "signed local namespace validator policies and rollback/fork pressure"),
        SurfaceLedgerEntry("src/i2p_dht_lab/namespacefold.py", "tests/test_rev0023_rangesketch_admission_namespace.py", "docs/208-namespace-fold-audit-refactor.md", "current namespace/admission/range surface navigation audit"),
    )


def rev0024_entries() -> tuple[SurfaceLedgerEntry, ...]:
    return rev0023_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/interestmix.py", "tests/test_rev0024_interestmix_routeattest_gatefold.py", "docs/214-interest-mixing-provider-probe-pressure.md", "interest-mixed provider probes with cover targets, raw-key exposure limits, and repeat pressure"),
        SurfaceLedgerEntry("src/i2p_dht_lab/routeattest.py", "tests/test_rev0024_interestmix_routeattest_gatefold.py", "docs/215-route-attestation-capture-pressure.md", "signed route attestations bound to fresh contact leases and path-family diversity"),
        SurfaceLedgerEntry("src/i2p_dht_lab/gateaudit.py", "tests/test_rev0024_interestmix_routeattest_gatefold.py", "docs/216-dispatch-gate-audit-refactor.md", "dispatch-gate audit after canonical wire and validator-wall acceptance"),
        SurfaceLedgerEntry("src/i2p_dht_lab/gatefold.py", "tests/test_rev0024_interestmix_routeattest_gatefold.py", "docs/217-gatefold-branchlet-refactor.md", "rev0024 interest/route/gate surface navigation audit"),
        SurfaceLedgerEntry("src/i2p_dht_lab/policyepoch.py", "tests/test_rev0024_policyepoch_rangemerkle_queueforge.py", "docs/214-policy-epoch-heads.md", "mutable namespace-policy epoch heads with rollback/fork/prev-link pressure"),
        SurfaceLedgerEntry("src/i2p_dht_lab/rangemerkle.py", "tests/test_rev0024_policyepoch_rangemerkle_queueforge.py", "docs/215-range-merkle-repair-fixtures.md", "Merkle-ish range repair proofs and tombstone-first exact repair pressure"),
        SurfaceLedgerEntry("src/i2p_dht_lab/queueforge.py", "tests/test_rev0024_policyepoch_rangemerkle_queueforge.py", "docs/216-queue-forge-admission-scheduling.md", "garden admission queue scheduling under latency and overload"),
        SurfaceLedgerEntry("src/i2p_dht_lab/policyfold.py", "tests/test_rev0024_policyepoch_rangemerkle_queueforge.py", "docs/217-policy-fold-audit-refactor.md", "rev0024 policy/range/queue surface navigation audit"),
        SurfaceLedgerEntry("src/i2p_dht_lab/clockguard.py", "tests/test_rev0024_relayticket_gossipsieve_clockguard.py", "docs/222-clock-guard-and-time-window-pressure.md", "clock guard branchlet for local freshness, skew, rollback, and fork pressure"),
        SurfaceLedgerEntry("src/i2p_dht_lab/relayticket.py", "tests/test_rev0024_relayticket_gossipsieve_clockguard.py", "docs/223-relay-ticket-garden-capacity-boundaries.md", "relay-ticket branchlet for bounded garden assistance and replay/fork detection"),
        SurfaceLedgerEntry("src/i2p_dht_lab/gossipsieve.py", "tests/test_rev0024_relayticket_gossipsieve_clockguard.py", "docs/224-gossip-sieve-before-expensive-work.md", "gossip-sieve branchlet for interest-budgeted entrance hints and introducer capture pressure"),
        SurfaceLedgerEntry("src/i2p_dht_lab/clockfold.py", "tests/test_rev0024_relayticket_gossipsieve_clockguard.py", "docs/225-branchlet-fold-audit-refactor.md", "clock/relay/gossip surface navigation audit"),
        SurfaceLedgerEntry("src/i2p_dht_lab/interestledger.py", "tests/test_rev0024_relayticket_gossipsieve_clockguard.py", "docs/222-clock-guard-and-time-window-pressure.md", "recovered interest ledger branchlet remains visible to tests and docs"),
        SurfaceLedgerEntry("src/i2p_dht_lab/pressureledger.py", "tests/test_rev0024_relayticket_gossipsieve_clockguard.py", "docs/225-branchlet-fold-audit-refactor.md", "recovered pressure ledger branchlet remains visible to tests and docs"),
        SurfaceLedgerEntry("src/i2p_dht_lab/regionreceipt.py", "tests/test_rev0024_relayticket_gossipsieve_clockguard.py", "docs/225-branchlet-fold-audit-refactor.md", "recovered region receipt branchlet remains visible to tests and docs"),
        SurfaceLedgerEntry("src/i2p_dht_lab/branchletfold.py", "tests/test_rev0024_relayticket_gossipsieve_clockguard.py", "docs/225-branchlet-fold-audit-refactor.md", "branchlet audit/refactor surface for recovered speculative modules"),
    )


def rev0025_entries() -> tuple[SurfaceLedgerEntry, ...]:
    return rev0024_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/capgate.py", "tests/test_rev0025_capgate_evidence_splitmerge.py", "docs/232-capability-dispatch-gate.md", "capability-gated dispatch joining namespace validation, delegated grants, revocations, and admission"),
        SurfaceLedgerEntry("src/i2p_dht_lab/evidencegc.py", "tests/test_rev0025_capgate_evidence_splitmerge.py", "docs/233-evidence-gc-and-memory-pressure.md", "local evidence retention and garbage collection under rollback/fork/tombstone pressure"),
        SurfaceLedgerEntry("src/i2p_dht_lab/splitmerge.py", "tests/test_rev0025_capgate_evidence_splitmerge.py", "docs/234-partition-merge-and-split-brain.md", "partition merge and split-brain pressure for mutable epoch heads"),
        SurfaceLedgerEntry("src/i2p_dht_lab/riskfold.py", "tests/test_rev0025_capgate_evidence_splitmerge.py", "docs/235-riskfold-audit-refactor.md", "rev0025 cross-surface audit/refactor visibility for joined risk surfaces"),
    )


def rev0026_entries() -> tuple[SurfaceLedgerEntry, ...]:
    return rev0025_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/schedjoin.py", "tests/test_rev0026_schedjoin_custodygc_transportshadow.py", "docs/241-joined-scheduling-after-capability.md", "joined capability/admission/queue scheduling pressure"),
        SurfaceLedgerEntry("src/i2p_dht_lab/custodygc.py", "tests/test_rev0026_schedjoin_custodygc_transportshadow.py", "docs/242-custody-evidence-gc-join.md", "custody/tombstone/witness/revocation evidence normalization before GC"),
        SurfaceLedgerEntry("src/i2p_dht_lab/partitionwitness.py", "tests/test_rev0026_schedjoin_custodygc_transportshadow.py", "docs/243-partition-witness-route-merge.md", "split-merge committed only after route and witness pressure"),
        SurfaceLedgerEntry("src/i2p_dht_lab/transportshadow.py", "tests/test_rev0026_schedjoin_custodygc_transportshadow.py", "docs/244-transport-shadow-canonical-report-carrying.md", "canonical signed report-shadow frames before live SAM/I2P"),
        SurfaceLedgerEntry("src/i2p_dht_lab/joinfold.py", "tests/test_rev0026_schedjoin_custodygc_transportshadow.py", "docs/245-joinfold-audit-refactor.md", "rev0026 joined-boundary audit/refactor visibility"),
    )


def rev0027_entries() -> tuple[SurfaceLedgerEntry, ...]:
    return rev0026_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/lineagewindow.py", "tests/test_rev0026_lineagebundle_workmeter.py", "docs/251-lineage-window-gap-pressure.md", "merged rev0026 lineage-window branchlet for mutable-head gap/fork pressure"),
        SurfaceLedgerEntry("src/i2p_dht_lab/claimbundle.py", "tests/test_rev0026_lineagebundle_workmeter.py", "docs/252-claim-bundle-type-pressure.md", "merged rev0026 typed claim-bundle branchlet"),
        SurfaceLedgerEntry("src/i2p_dht_lab/workmeter.py", "tests/test_rev0026_lineagebundle_workmeter.py", "docs/253-work-meter-garden-contribution-pressure.md", "merged rev0026 garden work-meter branchlet"),
        SurfaceLedgerEntry("src/i2p_dht_lab/lineagefold.py", "tests/test_rev0026_lineagebundle_workmeter.py", "docs/254-lineagefold-audit-refactor-merged.md", "merged lineagefold audit/refactor visibility"),
        SurfaceLedgerEntry("src/i2p_dht_lab/persistlane.py", "tests/test_rev0027_persist_fuzz_refusal_branchmerge.py", "docs/259-persist-lane-crash-reload-pressure.md", "parseguarded signed persisted snapshots and hard-negative reload pressure"),
        SurfaceLedgerEntry("src/i2p_dht_lab/fuzzwire.py", "tests/test_rev0027_persist_fuzz_refusal_branchmerge.py", "docs/260-fuzzwire-generated-malformed-fixtures.md", "deterministic malformed parser/wire/shadow fixtures before live transport"),
        SurfaceLedgerEntry("src/i2p_dht_lab/refusalloop.py", "tests/test_rev0027_persist_fuzz_refusal_branchmerge.py", "docs/261-refusal-loop-across-garden-windows.md", "repeated useful-refusal laundering pressure across garden windows"),
        SurfaceLedgerEntry("src/i2p_dht_lab/branchmergefold.py", "tests/test_rev0027_persist_fuzz_refusal_branchmerge.py", "docs/262-branchmergefold-audit-refactor.md", "rev0027 branch merge audit/refactor visibility"),
    )


def rev0028_entries() -> tuple[SurfaceLedgerEntry, ...]:
    return rev0027_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/journallane.py", "tests/test_rev0028_journal_generator_refusal_sam_fold.py", "docs/269-journal-lane-crash-cut-replay.md", "signed journal replay, crash-cut prefix recovery, and hard-negative preservation"),
        SurfaceLedgerEntry("src/i2p_dht_lab/generatorfuzz.py", "tests/test_rev0028_journal_generator_refusal_sam_fold.py", "docs/270-generator-fuzz-corpus.md", "deterministic generated malformed corpus over parseguard/wire/shadow surfaces"),
        SurfaceLedgerEntry("src/i2p_dht_lab/refusaljoin.py", "tests/test_rev0028_journal_generator_refusal_sam_fold.py", "docs/271-refusal-join-scheduler-pressure.md", "refusal-loop evidence joined to garden scheduling without laundering overload"),
        SurfaceLedgerEntry("src/i2p_dht_lab/samwire.py", "tests/test_rev0028_journal_generator_refusal_sam_fold.py", "docs/272-sam-wire-shadow-script.md", "no-network SAM shadow scripts carrying canonical wire frames"),
        SurfaceLedgerEntry("src/i2p_dht_lab/foldspine.py", "tests/test_rev0028_journal_generator_refusal_sam_fold.py", "docs/273-foldspine-audit-refactor.md", "revision-aware current/predecessor fold audit spine"),
    )


def rev0029_entries() -> tuple[SurfaceLedgerEntry, ...]:
    return rev0028_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/checkpointlane.py", "tests/test_rev0029_checkpoint_egress_dispatch_foldseal.py", "docs/280-checkpoint-lane-restart-pressure.md", "signed local checkpoints preserving monotonic restart memory and hard negative facts"),
        SurfaceLedgerEntry("src/i2p_dht_lab/egressmeter.py", "tests/test_rev0029_checkpoint_egress_dispatch_foldseal.py", "docs/281-egress-meter-metadata-budget.md", "outbound metadata/byte/stream budget pressure before provider probes and SAM sends"),
        SurfaceLedgerEntry("src/i2p_dht_lab/dispatchjoin.py", "tests/test_rev0029_checkpoint_egress_dispatch_foldseal.py", "docs/282-dispatch-join-misbind-egress.md", "joined handler dispatch gate binding misbind guard results to egress budgets"),
        SurfaceLedgerEntry("src/i2p_dht_lab/foldseal.py", "tests/test_rev0029_checkpoint_egress_dispatch_foldseal.py", "docs/283-foldseal-audit-refactor.md", "rev0029 fold seal audit/refactor for current risk path and predecessor fold"),
    )


def rev0030_entries() -> tuple[SurfaceLedgerEntry, ...]:
    return rev0029_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/negspace.py", "tests/test_rev0030_negspace_peerdelta_keycrisis.py", "docs/290-negative-space-absence-pressure.md", "negative-space/absence observations as typed local pressure, not proof"),
        SurfaceLedgerEntry("src/i2p_dht_lab/peerbook.py", "tests/test_rev0030_negspace_peerdelta_keycrisis.py", "docs/291-peerbook-delta-reconciliation.md", "signed peer/address-book entrance view diversity pressure"),
        SurfaceLedgerEntry("src/i2p_dht_lab/peerdelta.py", "tests/test_rev0030_negspace_peerdelta_keycrisis.py", "docs/291-peerbook-delta-reconciliation.md", "peer-book range delta sketches before dumping whole entrance books"),
        SurfaceLedgerEntry("src/i2p_dht_lab/keycrisis.py", "tests/test_rev0030_negspace_peerdelta_keycrisis.py", "docs/292-key-crisis-gating.md", "key compromise/freeze/succession gating before keyed operations"),
        SurfaceLedgerEntry("src/i2p_dht_lab/absencegate.py", "tests/test_rev0030_joined_branch_surfaces.py", "docs/290-negative-space-absence-pressure.md", "alternate absence-window gate folded from rev0029 branchlet"),
        SurfaceLedgerEntry("src/i2p_dht_lab/liveprobe.py", "tests/test_rev0030_joined_branch_surfaces.py", "docs/291-peerbook-delta-reconciliation.md", "contact-lease liveness probe evidence before entrance state advance"),
        SurfaceLedgerEntry("src/i2p_dht_lab/livesmoke.py", "tests/test_rev0030_joined_branch_surfaces.py", "docs/300-bootstrap-join-live-smoke-pressure.md", "no-router SAM live-smoke transcript bound to contact leases"),
        SurfaceLedgerEntry("src/i2p_dht_lab/bootstrapjoin.py", "tests/test_rev0030_joined_branch_surfaces.py", "docs/300-bootstrap-join-live-smoke-pressure.md", "joined bootstrap advance after peerbook, live probe, absence, and egress pressure"),
        SurfaceLedgerEntry("src/i2p_dht_lab/deltasketch.py", "tests/test_rev0030_joined_branch_surfaces.py", "docs/291-peerbook-delta-reconciliation.md", "range delta sketch repair pressure folded from rev0029 branchlet"),
        SurfaceLedgerEntry("src/i2p_dht_lab/deltarepairjoin.py", "tests/test_rev0030_joined_branch_surfaces.py", "docs/302-delta-repair-tombstone-first-join.md", "delta repair joined with egress budget and tombstone-first replies"),
        SurfaceLedgerEntry("src/i2p_dht_lab/keycrisisjoin.py", "tests/test_rev0030_joined_branch_surfaces.py", "docs/301-keycrisis-checkpoint-join.md", "key-crisis recovery joined with checkpoint hard-negative memory and egress pressure"),
        SurfaceLedgerEntry("src/i2p_dht_lab/keycrisisfold.py", "tests/test_rev0030_negspace_peerdelta_keycrisis.py", "docs/293-keycrisisfold-audit-refactor.md", "rev0030 current-path audit/refactor fold preserving rev0029 predecessor"),
    )





def rev0031_entries() -> tuple[SurfaceLedgerEntry, ...]:
    return rev0030_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/scopefence.py", "tests/test_rev0031_scopefence_obligation_decay.py", "docs/305-scope-fence-exact-boundary-pressure.md", "exact signed scope/object/request/purpose fence before joined evidence can authorize work"),
        SurfaceLedgerEntry("src/i2p_dht_lab/obligationdebt.py", "tests/test_rev0031_scopefence_obligation_decay.py", "docs/306-obligation-debt-and-proof-carrying-local-decisions.md", "proof-obligation debt left by accept-with-watch or convenience decisions"),
        SurfaceLedgerEntry("src/i2p_dht_lab/decaymesh.py", "tests/test_rev0031_scopefence_obligation_decay.py", "docs/307-decay-mesh-evidence-aging.md", "typed evidence aging preserving hard negatives while dropping stale convenience memory"),
        SurfaceLedgerEntry("src/i2p_dht_lab/auditmesh.py", "tests/test_rev0031_scopefence_obligation_decay.py", "docs/308-auditmesh-refactor-rev0031.md", "rev0031 current-path audit/refactor mesh preserving rev0030 keycrisisfold predecessor"),
        SurfaceLedgerEntry("src/i2p_dht_lab/probeledger.py", "tests/test_rev0031_probeledger_crisisroute_sketchboundary.py", "docs/314-repeated-round-probe-ledger.md", "repeated-round bootstrap/probe memory before sticky entrance advance"),
        SurfaceLedgerEntry("src/i2p_dht_lab/crisisroute.py", "tests/test_rev0031_probeledger_crisisroute_sketchboundary.py", "docs/315-key-crisis-route-gating.md", "key-crisis route gating for old keys, successor leases, tombstones, and revocations"),
        SurfaceLedgerEntry("src/i2p_dht_lab/sketchboundary.py", "tests/test_rev0031_probeledger_crisisroute_sketchboundary.py", "docs/316-set-reconciliation-adapter-boundary.md", "adapter boundary between exact toy sketches and future native set reconciliation engines"),
        SurfaceLedgerEntry("src/i2p_dht_lab/foldmap.py", "tests/test_rev0031_probeledger_crisisroute_sketchboundary.py", "docs/317-foldmap-audit-refactor.md", "declarative current/historical fold-map audit for rev0031 surfaces"),
    )



def rev0032_entries() -> tuple[SurfaceLedgerEntry, ...]:
    return rev0031_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/scopeledger.py", "tests/test_rev0032_scopeledger_storedebt_samtrace.py", "docs/320-scope-ledger-joined-advance.md", "joined scope/probe/obligation ledger before sticky advance"),
        SurfaceLedgerEntry("src/i2p_dht_lab/storedebt.py", "tests/test_rev0032_scopeledger_storedebt_samtrace.py", "docs/321-store-debt-repair-pressure.md", "joined store/custody/tombstone/repair debt pressure"),
        SurfaceLedgerEntry("src/i2p_dht_lab/samtrace.py", "tests/test_rev0032_scopeledger_storedebt_samtrace.py", "docs/322-sam-trace-scope-boundary.md", "scope/object/request-bound SAM-shadow side-effect join"),
        SurfaceLedgerEntry("src/i2p_dht_lab/scopefold.py", "tests/test_rev0032_scopeledger_storedebt_samtrace.py", "docs/323-scopefold-audit-refactor.md", "rev0032 current-path audit/refactor preserving foldmap predecessor"),
    )


def rev0033_entries() -> tuple[SurfaceLedgerEntry, ...]:
    return rev0032_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/negotiationlane.py", "tests/test_rev0033_negotiation_migration_safestart.py", "docs/330-protocol-negotiation-downgrade-pressure.md", "signed protocol offer/selection negotiation with downgrade, feature, policy, and frame-budget pressure"),
        SurfaceLedgerEntry("src/i2p_dht_lab/migrationlane.py", "tests/test_rev0033_negotiation_migration_safestart.py", "docs/331-state-migration-hard-negative-preservation.md", "hard-negative-preserving local state migration pressure before upgraded memory is trusted"),
        SurfaceLedgerEntry("src/i2p_dht_lab/safestart.py", "tests/test_rev0033_negotiation_migration_safestart.py", "docs/332-safe-start-joined-boundary.md", "joined negotiation/migration/SAM-shadow safe-start boundary"),
        SurfaceLedgerEntry("src/i2p_dht_lab/negotiationfold.py", "tests/test_rev0033_negotiation_migration_safestart.py", "docs/333-negotiationfold-audit-refactor.md", "rev0033 current-path audit/refactor preserving scopefold predecessor"),
    )



def rev0034_entries() -> tuple[SurfaceLedgerEntry, ...]:
    return rev0033_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/persistjoin.py", "tests/test_rev0033_persistjoin_samprobe_foldreduce.py", "artifacts/branchlets/rev0033_persistjoin_samprobe/330-persist-join-restart-boundary.md", "folded rev0033 branchlet restart persistence join across reload, journal, checkpoint, scope, and store debt"),
        SurfaceLedgerEntry("src/i2p_dht_lab/samprobe.py", "tests/test_rev0033_persistjoin_samprobe_foldreduce.py", "artifacts/branchlets/rev0033_persistjoin_samprobe/331-sam-probe-no-router-harness.md", "folded rev0033 branchlet no-network SAM probe classifier for local streaming-first router assumptions"),
        SurfaceLedgerEntry("src/i2p_dht_lab/foldreduce.py", "tests/test_rev0033_persistjoin_samprobe_foldreduce.py", "artifacts/branchlets/rev0033_persistjoin_samprobe/332-foldreduce-audit-refactor.md", "folded rev0033 branchlet fold-reduction audit preserved as predecessor history"),
        SurfaceLedgerEntry("src/i2p_dht_lab/launchquorum.py", "tests/test_rev0034_launch_metrics_foldmerge.py", "docs/340-launch-quorum-cold-start-boundary.md", "cold-launch quorum joining safe-start, durable restart memory, and explicit SAM probe outcome"),
        SurfaceLedgerEntry("src/i2p_dht_lab/metricsveil.py", "tests/test_rev0034_launch_metrics_foldmerge.py", "docs/341-metrics-veil-observability-pressure.md", "redacted diagnostics guard treating operator metrics as metadata side effects"),
        SurfaceLedgerEntry("src/i2p_dht_lab/foldmerge.py", "tests/test_rev0034_launch_metrics_foldmerge.py", "docs/342-foldmerge-audit-refactor.md", "rev0034 fold-merge audit preserving rev0033 negotiation and folded persistjoin/samprobe branchlet"),
    )


def rev0035_entries() -> tuple[SurfaceLedgerEntry, ...]:
    return rev0034_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/startmatrix.py", "tests/test_rev0035_startmatrix_telemetry_router.py", "docs/350-start-profile-matrix.md", "launch profile matrix binding leaf/garden/bridge/offline modes to launch quorum and router harness"),
        SurfaceLedgerEntry("src/i2p_dht_lab/routerharness.py", "tests/test_rev0035_startmatrix_telemetry_router.py", "docs/351-router-harness-config-capsule.md", "bundle-first/external-SAM/offline router harness capsule before live side effects"),
        SurfaceLedgerEntry("src/i2p_dht_lab/telemetrydebt.py", "tests/test_rev0035_startmatrix_telemetry_router.py", "docs/352-telemetry-debt-retention.md", "retained veiled diagnostics as metadata/evidence memory debt"),
        SurfaceLedgerEntry("src/i2p_dht_lab/startfold.py", "tests/test_rev0035_startmatrix_telemetry_router.py", "docs/353-startfold-audit-refactor.md", "rev0035 start-boundary fold audit preserving rev0034 predecessor"),
    )


def rev0036_entries() -> tuple[SurfaceLedgerEntry, ...]:
    return rev0035_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/servicecatalog.py", "tests/test_rev0036_servicecatalog_loadsheath_profilegc.py", "docs/361-service-catalog-capsules.md", "signed garden service catalogs bound to accepted start profiles, router harness, and launch reports"),
        SurfaceLedgerEntry("src/i2p_dht_lab/loadsheath.py", "tests/test_rev0036_servicecatalog_loadsheath_profilegc.py", "docs/362-load-sheath-useful-refusal-profiles.md", "per-service load shedding and useful-refusal profiles under catalog-bound budgets"),
        SurfaceLedgerEntry("src/i2p_dht_lab/profilegc.py", "tests/test_rev0036_servicecatalog_loadsheath_profilegc.py", "docs/363-profile-gc-config-change-pressure.md", "profile/config-change garbage collection preserving hard-negative memory"),
        SurfaceLedgerEntry("src/i2p_dht_lab/foldregistry.py", "tests/test_rev0036_servicecatalog_loadsheath_profilegc.py", "docs/364-foldregistry-servicefold-audit.md", "declarative fold registry before more one-off folds"),
        SurfaceLedgerEntry("src/i2p_dht_lab/servicefold.py", "tests/test_rev0036_servicecatalog_loadsheath_profilegc.py", "docs/364-foldregistry-servicefold-audit.md", "rev0036 service-boundary fold audit preserving rev0035 startfold predecessor"),
    )


def rev0037_entries() -> tuple[SurfaceLedgerEntry, ...]:
    return rev0036_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/serviceticket.py", "tests/test_rev0037_service_ticket_receipt_fold.py", "docs/372-service-ticket-exact-scope-grants.md", "short-lived exact-scope garden service ticket grants after catalog/load acceptance"),
        SurfaceLedgerEntry("src/i2p_dht_lab/servicereceipt.py", "tests/test_rev0037_service_ticket_receipt_fold.py", "docs/373-service-receipts-and-refusal-loops.md", "signed service receipts and refusal-loop pressure without payment or global reputation"),
        SurfaceLedgerEntry("src/i2p_dht_lab/ticketfold.py", "tests/test_rev0037_service_ticket_receipt_fold.py", "docs/374-ticketfold-audit-refactor.md", "rev0037 ticket/receipt fold audit preserving rev0036 servicefold predecessor"),
        SurfaceLedgerEntry("src/i2p_dht_lab/serviceannounce.py", "tests/test_rev0037_serviceannounce_ingressgate_registryfold.py", "docs/380-service-announcement-redaction.md", "redacted service announcements before public gossip"),
        SurfaceLedgerEntry("src/i2p_dht_lab/ingressgate.py", "tests/test_rev0037_serviceannounce_ingressgate_registryfold.py", "docs/381-ingress-gate-announcement-pressure.md", "announcement-bound ingress gate before load/ticket work"),
        SurfaceLedgerEntry("src/i2p_dht_lab/serviceguardfold.py", "tests/test_rev0037_serviceannounce_ingressgate_registryfold.py", "docs/382-serviceguardfold-branchlet.md", "folded service announcement/ingress branchlet audit"),
    )


def rev0038_entries() -> tuple[SurfaceLedgerEntry, ...]:
    return rev0037_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/catalogwire.py", "tests/test_rev0038_servicecontinuity_branchfold.py", "docs/385-branchlet-fold-service-surfaces.md", "folded catalog wire branchlet: canonical/report-bound catalog exposure before live transport"),
        SurfaceLedgerEntry("src/i2p_dht_lab/serviceprobe.py", "tests/test_rev0038_servicecontinuity_branchfold.py", "docs/385-branchlet-fold-service-surfaces.md", "folded service probe branchlet with cover and raw-key metadata budgets"),
        SurfaceLedgerEntry("src/i2p_dht_lab/profilegcjoin.py", "tests/test_rev0038_servicecontinuity_branchfold.py", "docs/386-profile-gc-catalog-succession-joins.md", "folded profile-GC/restart-memory join preserving hard negatives"),
        SurfaceLedgerEntry("src/i2p_dht_lab/catalogsuccession.py", "tests/test_rev0038_servicecontinuity_branchfold.py", "docs/386-profile-gc-catalog-succession-joins.md", "folded catalog succession under key-crisis and previous-link pressure"),
        SurfaceLedgerEntry("src/i2p_dht_lab/servicewithdrawal.py", "tests/test_rev0038_servicecontinuity_branchfold.py", "docs/385-branchlet-fold-service-surfaces.md", "folded service withdrawal negative evidence before stale service use"),
        SurfaceLedgerEntry("src/i2p_dht_lab/servicerelay.py", "tests/test_rev0038_servicecontinuity_branchfold.py", "docs/385-branchlet-fold-service-surfaces.md", "folded service relay observation pressure without reputation"),
        SurfaceLedgerEntry("src/i2p_dht_lab/serviceusegate.py", "tests/test_rev0038_servicecontinuity_branchfold.py", "docs/385-branchlet-fold-service-surfaces.md", "folded exact service-use gate joining reports before service intent"),
        SurfaceLedgerEntry("src/i2p_dht_lab/handofflane.py", "tests/test_rev0038_servicecontinuity_branchfold.py", "docs/385-branchlet-fold-service-surfaces.md", "folded service handoff/egress branchlet"),
        SurfaceLedgerEntry("src/i2p_dht_lab/receiptveil.py", "tests/test_rev0038_servicecontinuity_branchfold.py", "docs/385-branchlet-fold-service-surfaces.md", "folded veiled receipt diagnostics without raw labels"),
        SurfaceLedgerEntry("src/i2p_dht_lab/servicecontinuity.py", "tests/test_rev0038_servicecontinuity_branchfold.py", "docs/384-service-continuity-joined-boundary.md", "joined service-continuity boundary across folded service branchlets"),
        SurfaceLedgerEntry("src/i2p_dht_lab/servicecontinuityfold.py", "tests/test_rev0038_servicecontinuity_branchfold.py", "docs/387-servicecontinuityfold-audit-refactor.md", "rev0038 service-continuity fold audit/refactor preserving rev0037 lanes"),
    )



def rev0039_entries() -> tuple[SurfaceLedgerEntry, ...]:
    return rev0038_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/servicehealth.py", "tests/test_rev0039_serviceops_journal_drain.py", "docs/394-service-health-post-continuity.md", "post-continuity service health under withdrawal, replay, family, metadata, and refusal pressure"),
        SurfaceLedgerEntry("src/i2p_dht_lab/servicedrain.py", "tests/test_rev0039_serviceops_journal_drain.py", "docs/395-service-drain-safe-stop.md", "safe garden-service drain/stop preserving receipts, withdrawals, public announcements, and hard negatives"),
        SurfaceLedgerEntry("src/i2p_dht_lab/continuityjournal.py", "tests/test_rev0039_serviceops_journal_drain.py", "docs/396-continuity-journal-restart-memory.md", "durable service-continuity journal preserving hard negatives after restart"),
        SurfaceLedgerEntry("src/i2p_dht_lab/serviceopsfold.py", "tests/test_rev0039_serviceops_journal_drain.py", "docs/397-serviceopsfold-audit-refactor.md", "rev0039 serviceops fold audit preserving rev0038 continuity predecessor"),
    )


def rev0040_entries() -> tuple[SurfaceLedgerEntry, ...]:
    return rev0039_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/operatorintent.py", "tests/test_rev0040_operator_breaker_exit_fold.py", "docs/415-operator-intent-capsules.md", "scoped operator intent capsules before service pause/demotion/resume/freeze side effects"),
        SurfaceLedgerEntry("src/i2p_dht_lab/servicebreaker.py", "tests/test_rev0040_operator_breaker_exit_fold.py", "docs/416-service-breaker-pressure.md", "service circuit-breaker pressure across false service, hard negatives, withdrawals, refusal loops, and recovery"),
        SurfaceLedgerEntry("src/i2p_dht_lab/serviceexit.py", "tests/test_rev0040_operator_breaker_exit_fold.py", "docs/417-service-exit-join.md", "joined service exit/resume boundary over operator intent, breaker, drain, continuity, and profile memory"),
        SurfaceLedgerEntry("src/i2p_dht_lab/operationsfold.py", "tests/test_rev0040_operator_breaker_exit_fold.py", "docs/418-operationsfold-audit-refactor.md", "rev0040 operations fold audit preserving rev0039 serviceops predecessor"),
    )


def rev0041_entries() -> tuple[SurfaceLedgerEntry, ...]:
    return rev0040_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/routerstop.py", "tests/test_rev0041_routerstop_sessionresume_exitjournal.py", "docs/425-router-stop-shadow-boundary.md", "router-stop shadows joining service exit, public bridge drain, persistent destination, and cover/transit assumptions"),
        SurfaceLedgerEntry("src/i2p_dht_lab/sessionresume.py", "tests/test_rev0041_routerstop_sessionresume_exitjournal.py", "docs/426-session-resume-joined-gate.md", "session resume gate across exit, breaker, lease, announcement, relay, router-session, and hard-negative scans"),
        SurfaceLedgerEntry("src/i2p_dht_lab/exitjournal.py", "tests/test_rev0041_routerstop_sessionresume_exitjournal.py", "docs/427-exit-journal-restart-memory.md", "append-only exit/control journal preserving hard negatives across restart"),
        SurfaceLedgerEntry("src/i2p_dht_lab/controlfold.py", "tests/test_rev0041_routerstop_sessionresume_exitjournal.py", "docs/428-controlfold-audit-refactor.md", "rev0041 control fold audit preserving rev0040 operations predecessor"),
    )


def rev0042_entries() -> tuple[SurfaceLedgerEntry, ...]:
    return rev0041_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/multiservice.py", "tests/test_rev0042_multiservice_cooldown_keyoperator.py", "docs/435-multi-service-router-session-pressure.md", "shared-router multi-service pressure before stop/offline side effects"),
        SurfaceLedgerEntry("src/i2p_dht_lab/profilecooldown.py", "tests/test_rev0042_multiservice_cooldown_keyoperator.py", "docs/436-profile-cooldown-emergency-freeze.md", "profile-level cooldown after emergency freeze before resume"),
        SurfaceLedgerEntry("src/i2p_dht_lab/operatorkey.py", "tests/test_rev0042_multiservice_cooldown_keyoperator.py", "docs/437-operator-key-rotation-recovery.md", "operator-key rotation, compromise, recovery, and hard-negative preservation"),
        SurfaceLedgerEntry("src/i2p_dht_lab/announcementrepair.py", "tests/test_rev0042_multiservice_cooldown_keyoperator.py", "docs/438-announcement-repair-after-bridge-disable.md", "catalog/announcement repair after public bridge disable"),
        SurfaceLedgerEntry("src/i2p_dht_lab/controlplanefold.py", "tests/test_rev0042_multiservice_cooldown_keyoperator.py", "docs/439-controlplanefold-audit-refactor.md", "rev0042 control-plane fold audit preserving rev0041 control predecessor"),
    )


def rev0043_entries() -> tuple[SurfaceLedgerEntry, ...]:
    return rev0042_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/keycompartment.py", "tests/test_rev0043_keycompartment_authoritysplit.py", "docs/446-key-compartment-boundaries.md", "role-separated key-binding capsules before router/operator/service/mutable authority can collapse"),
        SurfaceLedgerEntry("src/i2p_dht_lab/authoritysplit.py", "tests/test_rev0043_keycompartment_authoritysplit.py", "docs/447-authority-split-joined-gate.md", "joined authority split gate over key compartment, operator, cooldown, router, catalog, and hard-negative reports"),
        SurfaceLedgerEntry("src/i2p_dht_lab/compartmentfold.py", "tests/test_rev0043_keycompartment_authoritysplit.py", "docs/448-compartmentfold-audit-refactor.md", "rev0043 compartment fold audit preserving rev0042 control-plane predecessor"),
    )



def rev0044_entries() -> tuple[SurfaceLedgerEntry, ...]:
    return rev0043_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/controlintent.py", "tests/test_rev0044_policyfirebreak_authorityreceipt_branchseal.py", "artifacts/branchlets/rev0043_controlintent_bridgefirewall/446-control-intent-joined-profile-boundary.md", "folded rev0043 control-intent branchlet as current rev0044 branch history"),
        SurfaceLedgerEntry("src/i2p_dht_lab/bridgefirewall.py", "tests/test_rev0044_policyfirebreak_authorityreceipt_branchseal.py", "artifacts/branchlets/rev0043_controlintent_bridgefirewall/447-bridge-firewall-public-exposure-boundary.md", "folded rev0043 bridge-firewall branchlet as current rev0044 branch history"),
        SurfaceLedgerEntry("src/i2p_dht_lab/policyfirebreak.py", "tests/test_rev0044_policyfirebreak_authorityreceipt_branchseal.py", "docs/466-policy-firebreak-subjective-authority.md", "subjective scoped policy capsules joined with key/control/firewall signals before side effects"),
        SurfaceLedgerEntry("src/i2p_dht_lab/authorityreceipt.py", "tests/test_rev0044_policyfirebreak_authorityreceipt_branchseal.py", "docs/467-authority-receipt-mesh.md", "signed authority receipt mesh preserving local evidence without global reputation"),
        SurfaceLedgerEntry("src/i2p_dht_lab/branchsealfold.py", "tests/test_rev0044_policyfirebreak_authorityreceipt_branchseal.py", "docs/468-branchseal-audit-refactor.md", "rev0044 branch-seal audit folding key-compartment and control/firewall histories"),
    )


def rev0045_entries() -> tuple[SurfaceLedgerEntry, ...]:
    return rev0044_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/bridgeepoch.py", "tests/test_rev0045_bridgeepoch_keyreceipt_shadowfire.py", "docs/470-public-bridge-epoch-windows.md", "public bridge epoch windows with stale-announcement, rollback, fork, and repair pressure"),
        SurfaceLedgerEntry("src/i2p_dht_lab/keyreceiptlane.py", "tests/test_rev0045_bridgeepoch_keyreceipt_shadowfire.py", "docs/471-key-receipt-lane.md", "operator/key authority receipts for bridge epochs without global reputation"),
        SurfaceLedgerEntry("src/i2p_dht_lab/shadowfire.py", "tests/test_rev0045_bridgeepoch_keyreceipt_shadowfire.py", "docs/472-shadow-fire-joined-boundary.md", "joined public bridge shadow-fire gate over epochs, key receipts, policy, authority receipts, and repair"),
        SurfaceLedgerEntry("src/i2p_dht_lab/bridgeepochfold.py", "tests/test_rev0045_bridgeepoch_keyreceipt_shadowfire.py", "docs/473-bridgeepochfold-audit-refactor.md", "rev0045 bridge-epoch fold audit preserving rev0044 branch-seal predecessor"),
    )





def rev0046_entries() -> tuple[SurfaceLedgerEntry, ...]:
    return rev0045_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/moderationquarantine.py", "tests/test_rev0046_moderation_redress_bridgeledger.py", "docs/480-moderation-quarantine-as-allegation.md", "signed abuse allegations as local moderation pressure, not DHT truth"),
        SurfaceLedgerEntry("src/i2p_dht_lab/redresslane.py", "tests/test_rev0046_moderation_redress_bridgeledger.py", "docs/481-redress-lane-appeal-receipts.md", "redress and appeal receipt lane before quarantine-like pressure hardens"),
        SurfaceLedgerEntry("src/i2p_dht_lab/bridgeledger.py", "tests/test_rev0046_moderation_redress_bridgeledger.py", "docs/482-bridge-ledger-policy-replay.md", "bridge ledger joins policy sequence, moderation, redress, and shadow-fire"),
        SurfaceLedgerEntry("src/i2p_dht_lab/moderationfold.py", "tests/test_rev0046_moderation_redress_bridgeledger.py", "docs/483-moderationfold-audit-refactor.md", "rev0046 moderation fold audit preserving rev0045 bridge-epoch predecessor"),
    )


def rev0047_entries() -> tuple[SurfaceLedgerEntry, ...]:
    return rev0046_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/witnessappealmesh.py", "tests/test_rev0047_appeal_publication_quench.py", "docs/491-witness-appeal-mesh.md", "witness appeal mesh for watched public bridge decisions"),
        SurfaceLedgerEntry("src/i2p_dht_lab/publicationledger.py", "tests/test_rev0047_appeal_publication_quench.py", "docs/492-publication-ledger-boundary.md", "public bridge publication replay/fork/digest boundary"),
        SurfaceLedgerEntry("src/i2p_dht_lab/bridgequenchlane.py", "tests/test_rev0047_appeal_publication_quench.py", "docs/493-bridge-quench-lane.md", "bridge quench and cooldown pressure for stale public exposure"),
        SurfaceLedgerEntry("src/i2p_dht_lab/appealpublicationfold.py", "tests/test_rev0047_appeal_publication_quench.py", "docs/494-appealpublicationfold-audit-refactor.md", "rev0047 appeal/publication/quench fold audit preserving public-bridge branchlets"),
        SurfaceLedgerEntry("src/i2p_dht_lab/policyportfolio.py", "tests/test_rev0047_policyportfolio_publicationguard.py", "docs/501-policy-portfolio-source-capture.md", "policy source portfolio capture-pressure addendum"),
        SurfaceLedgerEntry("src/i2p_dht_lab/publicationguard.py", "tests/test_rev0047_policyportfolio_publicationguard.py", "docs/502-publication-guard-final-side-effect.md", "final publication guard after bridge ledger and policy portfolio"),
        SurfaceLedgerEntry("src/i2p_dht_lab/publicationfold.py", "tests/test_rev0047_policyportfolio_publicationguard.py", "docs/504-publicationfold-audit-refactor.md", "publicationfold addendum audit preserving rev0046 publication branchlets"),
    )


def rev0048_entries() -> tuple[SurfaceLedgerEntry, ...]:
    return rev0047_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/bridgeshadow.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/506-bridge-shadow-publication-side-effect.md", "bridge publication shadow side-effect boundary after publication/ledger/quench"),
        SurfaceLedgerEntry("src/i2p_dht_lab/auditquorum.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/507-audit-quorum-local-evidence.md", "local audit receipt diversity for public bridge publication shadows"),
        SurfaceLedgerEntry("src/i2p_dht_lab/redressgc.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/508-redress-gc-retention-boundary.md", "redress/moderation evidence GC preserving hard negatives and active appeals"),
        SurfaceLedgerEntry("src/i2p_dht_lab/shadowauditfold.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/509-shadowauditfold-audit-refactor.md", "rev0048 shadow/audit/redress fold audit preserving rev0047 predecessor"),
    )

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:
    mapping = {
        "rev0019": rev0019_entries,
        "rev0020": rev0020_entries,
        "rev0021": rev0021_entries,
        "rev0022": rev0022_entries,
        "rev0023": rev0023_entries,
        "rev0024": rev0024_entries,
        "rev0025": rev0025_entries,
        "rev0026": rev0026_entries,
        "rev0027": rev0027_entries,
        "rev0028": rev0028_entries,
        "rev0029": rev0029_entries,
        "rev0030": rev0030_entries,
        "rev0031": rev0031_entries,
        "rev0032": rev0032_entries,
        "rev0033": rev0033_entries,
        "rev0034": rev0034_entries,
        "rev0035": rev0035_entries,
        "rev0036": rev0036_entries,
        "rev0037": rev0037_entries,
        "rev0038": rev0038_entries,
        "rev0039": rev0039_entries,
        "rev0040": rev0040_entries,
        "rev0041": rev0041_entries,
        "rev0042": rev0042_entries,
        "rev0043": rev0043_entries,
        "rev0044": rev0044_entries,
        "rev0045": rev0045_entries,
        "rev0046": rev0046_entries,
        "rev0047": rev0047_entries,
        "rev0048": rev0048_entries,
    }
    try:
        return mapping[revision]()
    except KeyError as exc:
        raise ValueError(f"unknown surface ledger revision: {revision}") from exc


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:
    return rev0048_entries()


def audit_surface_ledger(root: str | Path, entries: tuple[SurfaceLedgerEntry, ...] | str | None = None) -> SurfaceLedgerReport:
    root_path = Path(root)
    if isinstance(entries, str):
        entries = entries_for_revision(entries)
    entries = entries or active_entries()
    findings: list[SurfaceLedgerFinding] = []
    seen_modules: set[str] = set()
    for entry in entries:
        if entry.module in seen_modules:
            findings.append(SurfaceLedgerFinding("error", "duplicate_surface_module", entry.module, "module appears more than once in active surface ledger"))
        seen_modules.add(entry.module)
        for kind, rel in (("module", entry.module), ("test", entry.test), ("doc", entry.doc)):
            if not (root_path / rel).exists():
                findings.append(SurfaceLedgerFinding("error", f"missing_{kind}", rel, f"active surface ledger references missing {kind}"))
    digest = sha256(SURFACE_LEDGER_DOMAIN + b":report:" + bencode({
        b"entries": [entry.bvalue() for entry in entries],
        b"findings": [{b"severity": item.severity, b"code": item.code, b"path": item.path, b"detail": item.detail} for item in findings],
    }))
    return SurfaceLedgerReport(entries, tuple(findings), digest)

# rev0048 active surface ledger addendum.
def rev0048_entries() -> tuple[SurfaceLedgerEntry, ...]:
    return rev0047_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/auditquorum.py", "tests/test_rev0048_bridge_shadow_audit_redress.py", "docs/506-audit-quorum-transparency-witness.md", "transparency-style checkpoint quorum for public bridge publication observations"),
        SurfaceLedgerEntry("src/i2p_dht_lab/bridgeshadow.py", "tests/test_rev0048_bridge_shadow_audit_redress.py", "docs/507-bridge-shadow-final-side-effect.md", "no-network joined gate before public bridge side effects"),
        SurfaceLedgerEntry("src/i2p_dht_lab/redressgc.py", "tests/test_rev0048_bridge_shadow_audit_redress.py", "docs/508-redress-gc-hard-negative-memory.md", "redress/evidence GC that preserves hard negatives and scope boundaries"),
        SurfaceLedgerEntry("src/i2p_dht_lab/bridgeauditfold.py", "tests/test_rev0048_bridge_shadow_audit_redress.py", "docs/509-bridgeauditfold-audit-refactor.md", "rev0048 bridge audit fold preserving rev0047 publication predecessor"),
    )



def rev0048_entries() -> tuple[SurfaceLedgerEntry, ...]:
    return rev0047_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/bridgeshadow.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/506-bridge-shadow-publication-side-effect.md", "bridge publication shadow side-effect boundary after publication/ledger/quench"),
        SurfaceLedgerEntry("src/i2p_dht_lab/auditquorum.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/507-audit-quorum-local-evidence.md", "local audit receipt diversity for public bridge publication shadows"),
        SurfaceLedgerEntry("src/i2p_dht_lab/redressgc.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/508-redress-gc-retention-boundary.md", "redress/moderation evidence GC preserving hard negatives and active appeals"),
        SurfaceLedgerEntry("src/i2p_dht_lab/shadowauditfold.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/509-shadowauditfold-audit-refactor.md", "rev0048 shadow/audit/redress fold audit preserving rev0047 predecessor"),
    )

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    mapping = {
        "rev0019": rev0019_entries,
        "rev0020": rev0020_entries,
        "rev0021": rev0021_entries,
        "rev0022": rev0022_entries,
        "rev0023": rev0023_entries,
        "rev0024": rev0024_entries,
        "rev0025": rev0025_entries,
        "rev0026": rev0026_entries,
        "rev0027": rev0027_entries,
        "rev0028": rev0028_entries,
        "rev0029": rev0029_entries,
        "rev0030": rev0030_entries,
        "rev0031": rev0031_entries,
        "rev0032": rev0032_entries,
        "rev0033": rev0033_entries,
        "rev0034": rev0034_entries,
        "rev0035": rev0035_entries,
        "rev0036": rev0036_entries,
        "rev0037": rev0037_entries,
        "rev0038": rev0038_entries,
        "rev0039": rev0039_entries,
        "rev0040": rev0040_entries,
        "rev0041": rev0041_entries,
        "rev0042": rev0042_entries,
        "rev0043": rev0043_entries,
        "rev0044": rev0044_entries,
        "rev0045": rev0045_entries,
        "rev0046": rev0046_entries,
        "rev0047": rev0047_entries,
        "rev0048": rev0048_entries,
        "rev0048": rev0048_entries,
    }
    try:
        return mapping[revision]()
    except KeyError as exc:
        raise ValueError(f"unknown surface ledger revision: {revision}") from exc


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0048_entries()

# rev0048 final surface-ledger reconciliation.
_prior_entries_for_revision_rev0048_reconcile = entries_for_revision

def rev0048_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0047_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/bridgeshadow.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/506-bridge-shadow-public-side-effect.md", "bridge shadow public side-effect boundary after publication/ledger/quench"),
        SurfaceLedgerEntry("src/i2p_dht_lab/auditquorum.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/507-audit-quorum-local-receipts.md", "local audit receipt diversity for public bridge publication shadows"),
        SurfaceLedgerEntry("src/i2p_dht_lab/redressgc.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/508-redress-gc-retention-pressure.md", "redress/moderation evidence GC preserving hard negatives and active appeals"),
        SurfaceLedgerEntry("src/i2p_dht_lab/bridgeshadowfold.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/509-bridgeshadowfold-audit-refactor.md", "rev0048 bridgeshadow/audit/redress-GC fold audit preserving rev0047 predecessor"),
    )

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0048":
        return rev0048_entries()
    return _prior_entries_for_revision_rev0048_reconcile(revision)

def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0048_entries()

# rev0048 governance-fold final reconciliation.
_prior_entries_for_revision_rev0048_governance = entries_for_revision

def rev0048_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0047_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/bridgeshadow.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/506-bridge-shadow-side-effect-dryrun.md", "bridge-shadow dry-run gate before public side effects"),
        SurfaceLedgerEntry("src/i2p_dht_lab/auditquorum.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/507-audit-quorum-is-local-evidence.md", "local audit statements for public bridge shadow boundaries"),
        SurfaceLedgerEntry("src/i2p_dht_lab/redressgc.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/508-redress-gc-hard-negative-retention.md", "redress/evidence GC preserving hard negatives under byte pressure"),
        SurfaceLedgerEntry("src/i2p_dht_lab/bridgegovernancefold.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/509-bridgegovernancefold-audit-refactor.md", "rev0048 bridge governance fold audit preserving rev0047 publication predecessor"),
    )

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0048":
        return rev0048_entries()
    return _prior_entries_for_revision_rev0048_governance(revision)

def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0048_entries()

# rev0048 final active surface ledger override.
def rev0048_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0047_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/bridgeshadow.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/506-bridge-shadow-side-effect-dryrun.md", "bridge shadow dry-run side-effect boundary after publication/ledger/quench"),
        SurfaceLedgerEntry("src/i2p_dht_lab/auditquorum.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/507-audit-quorum-is-local-evidence.md", "local audit receipt diversity for public bridge shadows"),
        SurfaceLedgerEntry("src/i2p_dht_lab/redressgc.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/508-redress-gc-hard-negative-retention.md", "redress/moderation evidence GC preserving hard negatives"),
        SurfaceLedgerEntry("src/i2p_dht_lab/bridgegovernancefold.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/509-bridgegovernancefold-audit-refactor.md", "rev0048 bridge governance fold audit preserving rev0047 predecessor"),
    )


def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    mapping = {
        "rev0019": rev0019_entries,
        "rev0020": rev0020_entries,
        "rev0021": rev0021_entries,
        "rev0022": rev0022_entries,
        "rev0023": rev0023_entries,
        "rev0024": rev0024_entries,
        "rev0025": rev0025_entries,
        "rev0026": rev0026_entries,
        "rev0027": rev0027_entries,
        "rev0028": rev0028_entries,
        "rev0029": rev0029_entries,
        "rev0030": rev0030_entries,
        "rev0031": rev0031_entries,
        "rev0032": rev0032_entries,
        "rev0033": rev0033_entries,
        "rev0034": rev0034_entries,
        "rev0035": rev0035_entries,
        "rev0036": rev0036_entries,
        "rev0037": rev0037_entries,
        "rev0038": rev0038_entries,
        "rev0039": rev0039_entries,
        "rev0040": rev0040_entries,
        "rev0041": rev0041_entries,
        "rev0042": rev0042_entries,
        "rev0043": rev0043_entries,
        "rev0044": rev0044_entries,
        "rev0045": rev0045_entries,
        "rev0046": rev0046_entries,
        "rev0047": rev0047_entries,
        "rev0048": rev0048_entries,
    }
    try:
        return mapping[revision]()
    except KeyError as exc:
        raise ValueError(f"unknown surface ledger revision: {revision}") from exc


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0048_entries()

# rev0048 final shadowauditfold surface-ledger reconciliation.
_prior_entries_for_revision_rev0048_shadowaudit_reconcile = entries_for_revision

def rev0048_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0047_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/bridgeshadow.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/506-bridge-shadow-publication-side-effect.md", "bridge shadow publication side-effect boundary after publication/ledger/quench"),
        SurfaceLedgerEntry("src/i2p_dht_lab/auditquorum.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/507-audit-quorum-local-evidence.md", "local audit receipt diversity for public bridge publication shadows"),
        SurfaceLedgerEntry("src/i2p_dht_lab/redressgc.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/508-redress-gc-retention-boundary.md", "redress/moderation evidence GC preserving hard negatives and active appeals"),
        SurfaceLedgerEntry("src/i2p_dht_lab/shadowauditfold.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/509-shadowauditfold-audit-refactor.md", "rev0048 shadow/audit/redress-GC fold audit preserving rev0047 predecessor"),
    )

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0048":
        return rev0048_entries()
    return _prior_entries_for_revision_rev0048_shadowaudit_reconcile(revision)

def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0048_entries()


# rev0048 canonical bridge-governance surface-ledger override after stale
# shadowauditfold branchlet reconciliation.
_prior_entries_for_revision_rev0048_bridgegovernance_final = entries_for_revision

def rev0048_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0047_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/bridgeshadow.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/506-bridge-shadow-side-effect-dryrun.md", "bridge shadow dry-run side-effect boundary after publication/ledger/quench"),
        SurfaceLedgerEntry("src/i2p_dht_lab/auditquorum.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/507-audit-quorum-is-local-evidence.md", "local audit receipt diversity for public bridge shadows"),
        SurfaceLedgerEntry("src/i2p_dht_lab/redressgc.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/508-redress-gc-hard-negative-retention.md", "redress/moderation evidence GC preserving hard negatives and appeals"),
        SurfaceLedgerEntry("src/i2p_dht_lab/bridgegovernancefold.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/509-bridgegovernancefold-audit-refactor.md", "rev0048 bridge governance fold audit preserving rev0047 predecessor"),
    )

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0048":
        return rev0048_entries()
    return _prior_entries_for_revision_rev0048_bridgegovernance_final(revision)

def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0048_entries()

# rev0048 FINAL canonical shadowauditfold surface-ledger override.
_prior_entries_for_revision_rev0048_final_shadowaudit = entries_for_revision

def rev0048_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0047_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/bridgeshadow.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/506-bridge-shadow-publication-side-effect.md", "bridge shadow publication side-effect boundary after publication/ledger/quench"),
        SurfaceLedgerEntry("src/i2p_dht_lab/auditquorum.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/507-audit-quorum-local-evidence.md", "local audit receipt diversity for public bridge publication shadows"),
        SurfaceLedgerEntry("src/i2p_dht_lab/redressgc.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/508-redress-gc-retention-boundary.md", "redress/moderation evidence GC preserving hard negatives and active appeals"),
        SurfaceLedgerEntry("src/i2p_dht_lab/shadowauditfold.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/509-shadowauditfold-audit-refactor.md", "rev0048 shadow/audit/redress-GC fold audit preserving rev0047 predecessor"),
    )

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0048":
        return rev0048_entries()
    return _prior_entries_for_revision_rev0048_final_shadowaudit(revision)

def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0048_entries()


# rev0048 canonical bridge-governance surface-ledger override aligned with
# bridgegovernancefold.REV0048_PATHS after branchlet reconciliation.
_prior_entries_for_revision_rev0048_bridgegovernance_paths = entries_for_revision

def rev0048_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0047_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/bridgeshadow.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/506-bridge-shadow-side-effect-dryrun.md", "bridge shadow dry-run side-effect boundary after publication/ledger/quench"),
        SurfaceLedgerEntry("src/i2p_dht_lab/auditquorum.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/507-audit-quorum-is-local-evidence.md", "local audit receipt diversity for public bridge shadows"),
        SurfaceLedgerEntry("src/i2p_dht_lab/redressgc.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/508-redress-gc-hard-negative-retention.md", "redress/moderation evidence GC preserving hard negatives and appeals"),
        SurfaceLedgerEntry("src/i2p_dht_lab/bridgegovernancefold.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/509-bridgegovernancefold-audit-refactor.md", "rev0048 bridge governance fold audit preserving rev0047 predecessor"),
    )

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0048":
        return rev0048_entries()
    return _prior_entries_for_revision_rev0048_bridgegovernance_paths(revision)

def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0048_entries()

# rev0048 final active-path repair after branchlet reconciliation.
_prior_entries_for_revision_rev0048_active_repair = entries_for_revision

def rev0048_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0047_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/bridgeshadow.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/506-bridge-shadow-publication-side-effect.md", "bridge shadow public side-effect boundary after publication/ledger/quench"),
        SurfaceLedgerEntry("src/i2p_dht_lab/auditquorum.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/507-audit-quorum-local-evidence.md", "local audit receipt diversity for public bridge publication shadows"),
        SurfaceLedgerEntry("src/i2p_dht_lab/redressgc.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/508-redress-gc-retention-boundary.md", "redress/moderation evidence GC preserving hard negatives and active appeals"),
        SurfaceLedgerEntry("src/i2p_dht_lab/bridgegovernancefold.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/509-shadowauditfold-audit-refactor.md", "rev0048 bridge-governance audit wrapper preserving stale branchlet history"),
    )

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0048":
        return rev0048_entries()
    return _prior_entries_for_revision_rev0048_active_repair(revision)

def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0048_entries()

# rev0048 TRUE FINAL shadowauditfold override after bridgegovernance branchlet quarantine.
# Keep this block last for rev0048.  The bridgegovernancefold/bridgeauditfold
# variants remain preserved historical branchlet surfaces, not the current ledger.
_prior_entries_for_revision_rev0048_true_final_shadowaudit = entries_for_revision

def rev0048_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0047_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/bridgeshadow.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/506-bridge-shadow-publication-side-effect.md", "bridge shadow public side-effect boundary after publication/ledger/quench"),
        SurfaceLedgerEntry("src/i2p_dht_lab/auditquorum.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/507-audit-quorum-local-evidence.md", "local audit receipt diversity for public bridge publication shadows"),
        SurfaceLedgerEntry("src/i2p_dht_lab/redressgc.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/508-redress-gc-retention-boundary.md", "redress/moderation evidence GC preserving hard negatives and active appeals"),
        SurfaceLedgerEntry("src/i2p_dht_lab/shadowauditfold.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/509-shadowauditfold-audit-refactor.md", "rev0048 shadow/audit/redress-GC fold audit preserving rev0047 predecessor"),
    )

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0048":
        return rev0048_entries()
    return _prior_entries_for_revision_rev0048_true_final_shadowaudit(revision)

def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0048_entries()

# rev0048 ACTUAL FINAL bridgegovernancefold surface-ledger override.
_prior_entries_for_revision_rev0048_actual_final_bridgegovernance = entries_for_revision

def rev0048_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0047_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/bridgeshadow.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/506-bridge-shadow-side-effect-dryrun.md", "bridge shadow dry-run side-effect boundary after publication/ledger/quench"),
        SurfaceLedgerEntry("src/i2p_dht_lab/auditquorum.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/507-audit-quorum-is-local-evidence.md", "local audit receipt diversity for public bridge shadows"),
        SurfaceLedgerEntry("src/i2p_dht_lab/redressgc.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/508-redress-gc-hard-negative-retention.md", "redress/moderation evidence GC preserving hard negatives and appeals"),
        SurfaceLedgerEntry("src/i2p_dht_lab/bridgegovernancefold.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/509-bridgegovernancefold-audit-refactor.md", "rev0048 bridge governance fold audit preserving rev0047 predecessor"),
    )

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0048":
        return rev0048_entries()
    return _prior_entries_for_revision_rev0048_actual_final_bridgegovernance(revision)

def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0048_entries()

# rev0048 ABSOLUTE FINAL ACTIVE surface-ledger override: shadowauditfold active.
_prior_entries_for_revision_rev0048_absolute_shadowaudit = entries_for_revision

def rev0048_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0047_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/bridgeshadow.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/506-bridge-shadow-publication-side-effect.md", "bridge shadow publication side-effect boundary after publication/ledger/quench"),
        SurfaceLedgerEntry("src/i2p_dht_lab/auditquorum.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/507-audit-quorum-local-evidence.md", "local audit receipt diversity for public bridge publication shadows"),
        SurfaceLedgerEntry("src/i2p_dht_lab/redressgc.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/508-redress-gc-retention-boundary.md", "redress/moderation evidence GC preserving hard negatives and active appeals"),
        SurfaceLedgerEntry("src/i2p_dht_lab/shadowauditfold.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/509-shadowauditfold-audit-refactor.md", "rev0048 shadow/audit/redress-GC fold audit preserving rev0047 predecessor"),
    )

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0048":
        return rev0048_entries()
    return _prior_entries_for_revision_rev0048_absolute_shadowaudit(revision)

def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0048_entries()

# rev0048 final bridgegovernancefold surface-ledger override after JSON/doc repair.
_prior_entries_for_revision_rev0048_bridgegovernance_repaired = entries_for_revision

def rev0048_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0047_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/bridgeshadow.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/506-bridge-shadow-publication-side-effect.md", "bridge shadow public side-effect dry-run boundary after publication/ledger/quench"),
        SurfaceLedgerEntry("src/i2p_dht_lab/auditquorum.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/507-audit-quorum-local-evidence.md", "audit quorum local evidence for public bridge shadow boundaries"),
        SurfaceLedgerEntry("src/i2p_dht_lab/redressgc.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/508-redress-gc-retention-boundary.md", "redress/evidence GC preserving hard negatives and active appeals"),
        SurfaceLedgerEntry("src/i2p_dht_lab/bridgegovernancefold.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/509-shadowauditfold-audit-refactor.md", "rev0048 bridgegovernancefold audit preserving shadowauditfold branchlet history"),
        SurfaceLedgerEntry("src/i2p_dht_lab/shadowauditfold.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/509-shadowauditfold-audit-refactor.md", "rev0048 shadowauditfold compatibility audit retained as branchlet history"),
    )

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0048":
        return rev0048_entries()
    return _prior_entries_for_revision_rev0048_bridgegovernance_repaired(revision)

def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0048_entries()

# rev0048 TRUE FINAL shadowauditfold surface-ledger override after bridgegovernance branchlet quarantine.
_prior_entries_for_revision_rev0048_true_final_shadowaudit_latest = entries_for_revision

def rev0048_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0047_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/bridgeshadow.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/506-bridge-shadow-publication-side-effect.md", "bridge shadow public side-effect boundary after publication/ledger/quench"),
        SurfaceLedgerEntry("src/i2p_dht_lab/auditquorum.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/507-audit-quorum-local-evidence.md", "local audit receipt diversity for public bridge publication shadows"),
        SurfaceLedgerEntry("src/i2p_dht_lab/redressgc.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/508-redress-gc-retention-boundary.md", "redress/moderation evidence GC preserving hard negatives and active appeals"),
        SurfaceLedgerEntry("src/i2p_dht_lab/shadowauditfold.py", "tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py", "docs/509-shadowauditfold-audit-refactor.md", "rev0048 shadow/audit/redress-GC fold audit preserving rev0047 predecessor"),
    )

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0048":
        return rev0048_entries()
    return _prior_entries_for_revision_rev0048_true_final_shadowaudit_latest(revision)

def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0048_entries()

# rev0049 active publish dry-run / witness compaction / scope-journal surface ledger.
_prior_entries_for_revision_rev0049_publish = entries_for_revision

def rev0049_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0048_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/publishdryrun.py", "tests/test_rev0049_publishdryrun_witnesscompact_scopejournal.py", "docs/511-publish-dryrun-side-effect-boundary.md", "no-network publication dry-run before public bridge side effects"),
        SurfaceLedgerEntry("src/i2p_dht_lab/witnesscompact.py", "tests/test_rev0049_publishdryrun_witnesscompact_scopejournal.py", "docs/512-witness-compaction-memory-pressure.md", "witness/evidence compaction preserving hard negatives and active redress"),
        SurfaceLedgerEntry("src/i2p_dht_lab/scopejournal.py", "tests/test_rev0049_publishdryrun_witnesscompact_scopejournal.py", "docs/513-scope-journal-restart-boundary.md", "scoped signed restart journal for publish/witness memory"),
        SurfaceLedgerEntry("src/i2p_dht_lab/publishfold.py", "tests/test_rev0049_publishdryrun_witnesscompact_scopejournal.py", "docs/514-publishfold-audit-refactor.md", "rev0049 publishfold audit preserving rev0048 predecessor"),
    )

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0049":
        return rev0049_entries()
    return _prior_entries_for_revision_rev0049_publish(revision)

def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0049_entries()

# rev0049 public outbox / audit-gap surface ledger override.
_prior_entries_for_revision_rev0049_outbox = entries_for_revision

def rev0049_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0048_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/publicoutbox.py", "tests/test_rev0049_publicoutbox_auditgap_fold.py", "docs/515-public-outbox-side-effect-staging.md", "signed exact-scope idempotent public side-effect staging before live publication"),
        SurfaceLedgerEntry("src/i2p_dht_lab/auditgap.py", "tests/test_rev0049_publicoutbox_auditgap_fold.py", "docs/516-audit-gap-repair-planning.md", "audit-gap repair/withdraw planning without making audits DHT truth"),
        SurfaceLedgerEntry("src/i2p_dht_lab/outboxfold.py", "tests/test_rev0049_publicoutbox_auditgap_fold.py", "docs/517-outboxfold-audit-refactor.md", "rev0049 publicoutbox/auditgap fold audit preserving rev0048 shadowauditfold predecessor"),
    )

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0049":
        return rev0049_entries()
    return _prior_entries_for_revision_rev0049_outbox(revision)

def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0049_entries()

# rev0049 integrated publish/outbox/auditcompact surface-ledger override.
_prior_entries_for_revision_rev0049_integrated = entries_for_revision

def rev0049_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0048_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/publishdryrun.py", "tests/test_rev0049_publishdryrun_witnesscompact_scopejournal.py", "docs/515-publish-dry-run-public-edge.md", "no-network public-edge dry-run after bridge shadow/audit/redress components"),
        SurfaceLedgerEntry("src/i2p_dht_lab/witnesscompact.py", "tests/test_rev0049_publishdryrun_witnesscompact_scopejournal.py", "docs/516-witness-compact-hard-evidence.md", "witness/evidence compaction preserving hard negatives and redress gaps"),
        SurfaceLedgerEntry("src/i2p_dht_lab/scopejournal.py", "tests/test_rev0049_publishdryrun_witnesscompact_scopejournal.py", "docs/517-scope-journal-restart-memory.md", "signed previous-linked restart journal for public side-effect attempts"),
        SurfaceLedgerEntry("src/i2p_dht_lab/publishdryrunfold.py", "tests/test_rev0049_publishdryrun_witnesscompact_scopejournal.py", "docs/518-publishdryrunfold-audit-refactor.md", "publishdryrun/witnesscompact/scopejournal fold audit"),
        SurfaceLedgerEntry("src/i2p_dht_lab/publicoutbox.py", "tests/test_rev0049_publicoutbox_auditgap_fold.py", "docs/515-public-outbox-side-effect-staging.md", "signed exact-scope idempotent public side-effect staging before live publication"),
        SurfaceLedgerEntry("src/i2p_dht_lab/auditgap.py", "tests/test_rev0049_publicoutbox_auditgap_fold.py", "docs/516-audit-gap-repair-planning.md", "audit-gap repair/withdraw planning without making audits DHT truth"),
        SurfaceLedgerEntry("src/i2p_dht_lab/outboxfold.py", "tests/test_rev0049_publicoutbox_auditgap_fold.py", "docs/517-outboxfold-audit-refactor.md", "publicoutbox/auditgap fold audit preserving rev0048 predecessor"),
        SurfaceLedgerEntry("src/i2p_dht_lab/auditcompact.py", "tests/test_rev0049_publishdryrun_auditcompact_scopejournal.py", "docs/523-auditcompact-refute-fork-preservation.md", "raw audit receipt compaction preserving refute and same-family fork evidence"),
    )

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0049":
        return rev0049_entries()
    return _prior_entries_for_revision_rev0049_integrated(revision)

def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0049_entries()

# rev0050 outbox-drain / SAM-canary / compact-join surface ledger.
_prior_entries_for_revision_rev0050_drain = entries_for_revision

def rev0050_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0049_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/outboxdrain.py", "tests/test_rev0050_outboxdrain_samcanary_compactjoin.py", "docs/525-outbox-drain-commit-receipts.md", "no-network public outbox drain prepare/commit receipts"),
        SurfaceLedgerEntry("src/i2p_dht_lab/samcanary.py", "tests/test_rev0050_outboxdrain_samcanary_compactjoin.py", "docs/526-sam-canary-before-live-send.md", "SAM-shadow canary before future live send"),
        SurfaceLedgerEntry("src/i2p_dht_lab/compactjoin.py", "tests/test_rev0050_outboxdrain_samcanary_compactjoin.py", "docs/527-compact-join-negative-evidence.md", "witness/audit/redress/scope compaction join preserving hard negatives"),
        SurfaceLedgerEntry("src/i2p_dht_lab/drainfold.py", "tests/test_rev0050_outboxdrain_samcanary_compactjoin.py", "docs/528-drainfold-audit-refactor.md", "rev0050 drain/canary/compact fold audit preserving rev0049 predecessors"),
    )

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0050":
        return rev0050_entries()
    return _prior_entries_for_revision_rev0050_drain(revision)

def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0050_entries()

# rev0051 send-valve / effect-ledger / commit-barrier fold-merge surface ledger.
_prior_entries_for_revision_rev0051_send = entries_for_revision

def rev0051_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0050_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/commitbarrier.py", "tests/test_rev0051_sendvalve_effectledger_foldmerge.py", "docs/537-foldmerge-commitbarrier-branchlet.md", "folded public commit barrier branchlet from sibling rev0050"),
        SurfaceLedgerEntry("src/i2p_dht_lab/sendvalve.py", "tests/test_rev0051_sendvalve_effectledger_foldmerge.py", "docs/535-send-valve-joined-boundary.md", "send valve joining commit, drain, SAM canary, and compaction evidence before live send"),
        SurfaceLedgerEntry("src/i2p_dht_lab/effectledger.py", "tests/test_rev0051_sendvalve_effectledger_foldmerge.py", "docs/536-effect-ledger-idempotent-memory.md", "idempotent public-effect restart memory after send valve acceptance"),
        SurfaceLedgerEntry("src/i2p_dht_lab/sendfold.py", "tests/test_rev0051_sendvalve_effectledger_foldmerge.py", "docs/538-sendfold-audit-refactor.md", "rev0051 sendfold audit preserving rev0050 drainfold predecessor and folded branchlet history"),
    )

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0051":
        return rev0051_entries()
    return _prior_entries_for_revision_rev0051_send(revision)

def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0051_entries()

# rev0051 ingress-drain / router-canary / red-team surface ledger.
_prior_entries_for_revision_rev0051_redteam = entries_for_revision

def rev0051_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0050_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/routercanary.py", "tests/test_rev0051_ingressdrain_routercanary_redteamfold.py", "docs/535-router-canary-public-edge.md", "no-network router/session canary before public-edge side effects"),
        SurfaceLedgerEntry("src/i2p_dht_lab/ingressdrain.py", "tests/test_rev0051_ingressdrain_routercanary_redteamfold.py", "docs/536-ingress-drain-public-bridge.md", "public bridge ingress drain before handler work and refusal laundering"),
        SurfaceLedgerEntry("src/i2p_dht_lab/redteamfold.py", "tests/test_rev0051_ingressdrain_routercanary_redteamfold.py", "docs/537-redteamfold-audit-refactor.md", "rev0051 red-team fold audit preserving rev0050 drainfold predecessor"),
    )

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0051":
        return rev0051_entries()
    return _prior_entries_for_revision_rev0051_redteam(revision)

def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0051_entries()

# rev0052 live-adapter / backpressure / profile-edge surface ledger.
_prior_entries_for_revision_rev0052_edge = entries_for_revision

def rev0052_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0051_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/liveadapter.py", "tests/test_rev0052_liveadapter_backpressure_profileedge.py", "docs/549-live-adapter-no-network-boundary.md", "no-network live adapter seam joining router, ingress, backpressure, and effect evidence"),
        SurfaceLedgerEntry("src/i2p_dht_lab/backpressuremesh.py", "tests/test_rev0052_liveadapter_backpressure_profileedge.py", "docs/550-backpressure-mesh-shared-edge.md", "shared inbound/outbound/router public-edge backpressure and metadata budget"),
        SurfaceLedgerEntry("src/i2p_dht_lab/profileedge.py", "tests/test_rev0052_liveadapter_backpressure_profileedge.py", "docs/551-profile-edge-joined-boundary.md", "profile-edge join across live adapter, pressure, profile budget, and hard-negative scan"),
        SurfaceLedgerEntry("src/i2p_dht_lab/edgefold.py", "tests/test_rev0052_liveadapter_backpressure_profileedge.py", "docs/552-edgefold-audit-refactor.md", "rev0052 edgefold audit preserving rev0051 redteamfold predecessor"),
    )

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0052":
        return rev0052_entries()
    return _prior_entries_for_revision_rev0052_edge(revision)

def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0052_entries()

# rev0053 handler-capsule / side-effect journal / adapter-fuzz surface ledger.
_prior_entries_for_revision_rev0053_handler = entries_for_revision

def rev0053_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0052_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/handlercapsule.py", "tests/test_rev0053_handlercapsule_sideeffect_adapterfuzz.py", "docs/560-handler-capsule-boundary.md", "handler capsules joining profile-edge, live-adapter, ingress, backpressure, caller, handler, payload, budget, and hard-negative pressure"),
        SurfaceLedgerEntry("src/i2p_dht_lab/sideeffectjournal.py", "tests/test_rev0053_handlercapsule_sideeffect_adapterfuzz.py", "docs/561-side-effect-journal-boundary.md", "local prepare/commit/abort side-effect journal with idempotency and previous-link pressure"),
        SurfaceLedgerEntry("src/i2p_dht_lab/adapterfuzz.py", "tests/test_rev0053_handlercapsule_sideeffect_adapterfuzz.py", "docs/562-adapter-fuzz-coverage.md", "deterministic adapter/profile-edge mismatch coverage summary"),
        SurfaceLedgerEntry("src/i2p_dht_lab/handlerfold.py", "tests/test_rev0053_handlercapsule_sideeffect_adapterfuzz.py", "docs/563-handlerfold-audit-refactor.md", "rev0053 handlerfold audit preserving rev0052 edgefold predecessor"),
    )

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0053":
        return rev0053_entries()
    return _prior_entries_for_revision_rev0053_handler(revision)

def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0053_entries()

# rev0054 replay-lab / handler-quench / fuzz-ledger surface ledger.
_prior_entries_for_revision_rev0054_replay = entries_for_revision

def rev0054_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0053_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/handlerreplay.py", "tests/test_rev0054_replay_quench_fuzzledger.py", "docs/570-handler-replay-restart-boundary.md", "restart replay window for handler and side-effect reports before sticky state advances"),
        SurfaceLedgerEntry("src/i2p_dht_lab/handlerquench.py", "tests/test_rev0054_replay_quench_fuzzledger.py", "docs/571-handler-quench-cooldown.md", "cooldown/quench pressure for repeated near-miss inbound handler traffic"),
        SurfaceLedgerEntry("src/i2p_dht_lab/fuzzledger.py", "tests/test_rev0054_replay_quench_fuzzledger.py", "docs/572-fuzz-ledger-persistent-coverage.md", "persistent adapter fuzz coverage ledger with replay/fork/coverage pressure"),
        SurfaceLedgerEntry("src/i2p_dht_lab/replayfold.py", "tests/test_rev0054_replay_quench_fuzzledger.py", "docs/573-replayfold-audit-refactor.md", "rev0054 replay/quench/fuzzledger fold audit preserving rev0053 predecessor"),
    )

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0054":
        return rev0054_entries()
    return _prior_entries_for_revision_rev0054_replay(revision)

def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0054_entries()

# rev0055 restart-chaos / effect-seal / fuzz-shrink surface ledger.
_prior_entries_for_revision_rev0055_restart = entries_for_revision

def rev0055_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0054_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/restartchaos.py", "tests/test_rev0055_restartchaos_effectseal_fuzzshrink.py", "docs/581-restart-chaos-crash-cut-boundary.md", "signed crash-cut restart lane joining replay, journal, quench, and fuzz evidence"),
        SurfaceLedgerEntry("src/i2p_dht_lab/effectseal.py", "tests/test_rev0055_restartchaos_effectseal_fuzzshrink.py", "docs/582-effect-seal-joined-boundary.md", "effect seal across handler replay, quench, side-effect journal, restart chaos, fuzz ledger, and shrink evidence"),
        SurfaceLedgerEntry("src/i2p_dht_lab/fuzzshrink.py", "tests/test_rev0055_restartchaos_effectseal_fuzzshrink.py", "docs/583-fuzz-shrink-coverage-compaction.md", "coverage shrink/compaction preserving required mutation evidence and diversity"),
        SurfaceLedgerEntry("src/i2p_dht_lab/restartfold.py", "tests/test_rev0055_restartchaos_effectseal_fuzzshrink.py", "docs/584-restartfold-audit-refactor.md", "rev0055 restart/effect/fuzz-shrink fold audit preserving rev0054 replayfold predecessor"),
    )

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0055":
        return rev0055_entries()
    return _prior_entries_for_revision_rev0055_restart(revision)

def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0055_entries()

# rev0056 recovery-mesh / safe-cleanup / chaos-budget surface ledger.
_prior_entries_for_revision_rev0056_recovery = entries_for_revision

def rev0056_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0055_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/recoverymesh.py", "tests/test_rev0056_recovery_cleanup_chaosbudget.py", "docs/591-recovery-mesh-after-effect-seal.md", "recovery mesh joining effect seal, seal replay, restart chaos, and corpus witness evidence"),
        SurfaceLedgerEntry("src/i2p_dht_lab/safecleanup.py", "tests/test_rev0056_recovery_cleanup_chaosbudget.py", "docs/592-safe-cleanup-hard-negative-boundary.md", "signed cleanup tickets preserving hard negatives and accepted effect seals"),
        SurfaceLedgerEntry("src/i2p_dht_lab/chaosbudget.py", "tests/test_rev0056_recovery_cleanup_chaosbudget.py", "docs/593-chaos-budget-post-effect-pressure.md", "post-effect chaos budget for retry, cleanup, fuzz, and canary pressure"),
        SurfaceLedgerEntry("src/i2p_dht_lab/recoveryfold.py", "tests/test_rev0056_recovery_cleanup_chaosbudget.py", "docs/594-recoveryfold-audit-refactor.md", "rev0056 recoveryfold audit preserving rev0055 restartfold predecessor"),
    )

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0056":
        return rev0056_entries()
    return _prior_entries_for_revision_rev0056_recovery(revision)

def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0056_entries()

# rev0056 recovery mesh / safe cleanup / chaos budget surface ledger.
_prior_entries_for_revision_rev0056_recovery = entries_for_revision

def rev0056_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0055_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/sealreplay.py", "tests/test_rev0056_recovery_cleanup_chaosbudget.py", "docs/591-recovery-mesh-after-effect-seal.md", "signed restart-generation observations preventing effect-seal reinterpretation"),
        SurfaceLedgerEntry("src/i2p_dht_lab/corpuswitness.py", "tests/test_rev0056_recovery_cleanup_chaosbudget.py", "docs/591-recovery-mesh-after-effect-seal.md", "fuzz-shrink corpus witness receipts preserving compact coverage evidence"),
        SurfaceLedgerEntry("src/i2p_dht_lab/recoverymesh.py", "tests/test_rev0056_recovery_cleanup_chaosbudget.py", "docs/591-recovery-mesh-after-effect-seal.md", "joined post-effect recovery mesh across seal replay, restart chaos, and corpus witnesses"),
        SurfaceLedgerEntry("src/i2p_dht_lab/safecleanup.py", "tests/test_rev0056_recovery_cleanup_chaosbudget.py", "docs/592-safe-cleanup-hard-negative-boundary.md", "cleanup tickets that preserve hard negatives and accepted effect seals"),
        SurfaceLedgerEntry("src/i2p_dht_lab/chaosbudget.py", "tests/test_rev0056_recovery_cleanup_chaosbudget.py", "docs/593-chaos-budget-post-effect-pressure.md", "bounded post-effect chaos/fuzz/retry budget bound to recovered public-edge state"),
        SurfaceLedgerEntry("src/i2p_dht_lab/recoveryfold.py", "tests/test_rev0056_recovery_cleanup_chaosbudget.py", "docs/594-recoveryfold-audit-refactor.md", "rev0056 recovery/cleanup/chaosbudget fold audit preserving rev0055 restartfold predecessor"),
    )

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0056":
        return rev0056_entries()
    return _prior_entries_for_revision_rev0056_recovery(revision)

def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0056_entries()

# rev0056 final recovery surface-ledger override after branchlet fold reconciliation.
def rev0056_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0055_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/sealreplay.py", "tests/test_rev0056_recovery_cleanup_chaosbudget.py", "docs/591-recovery-mesh-after-effect-seal.md", "signed restart-generation seal replay evidence before recovery mesh"),
        SurfaceLedgerEntry("src/i2p_dht_lab/corpuswitness.py", "tests/test_rev0056_recovery_cleanup_chaosbudget.py", "docs/591-recovery-mesh-after-effect-seal.md", "corpus witness receipts preserving fuzz-shrink coverage evidence"),
        SurfaceLedgerEntry("src/i2p_dht_lab/recoverymesh.py", "tests/test_rev0056_recovery_cleanup_chaosbudget.py", "docs/591-recovery-mesh-after-effect-seal.md", "recovery mesh joining effect seal, seal replay, restart chaos, and corpus witness evidence"),
        SurfaceLedgerEntry("src/i2p_dht_lab/safecleanup.py", "tests/test_rev0056_recovery_cleanup_chaosbudget.py", "docs/592-safe-cleanup-hard-negative-boundary.md", "signed cleanup tickets preserving hard negatives and accepted effect seals"),
        SurfaceLedgerEntry("src/i2p_dht_lab/chaosbudget.py", "tests/test_rev0056_recovery_cleanup_chaosbudget.py", "docs/593-chaos-budget-post-effect-pressure.md", "post-effect chaos budget for retry, cleanup, fuzz, and canary pressure"),
        SurfaceLedgerEntry("src/i2p_dht_lab/recoveryfold.py", "tests/test_rev0056_recovery_cleanup_chaosbudget.py", "docs/594-recoveryfold-audit-refactor.md", "rev0056 recoveryfold audit preserving rev0055 restartfold predecessor"),
    )

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0056":
        return rev0056_entries()
    if revision == "rev0055":
        return rev0055_entries()
    return _prior_entries_for_revision_rev0055_restart(revision)

def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0056_entries()

# rev0057 dead-letter / retry-quorum / effect-reconcile surface ledger.
_prior_entries_for_revision_rev0057_reconcile = entries_for_revision


def rev0057_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0056_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/deadletter.py", "tests/test_rev0057_deadletter_retry_reconcile.py", "docs/601-dead-letter-lane-prepared-only.md", "signed dead-letter memory for prepared-only and ambiguous post-restart effects"),
        SurfaceLedgerEntry("src/i2p_dht_lab/retryquorum.py", "tests/test_rev0057_deadletter_retry_reconcile.py", "docs/602-retry-quorum-after-recovery-watch.md", "retry quorum with budget-lane and diversity pressure after dead-letter watch"),
        SurfaceLedgerEntry("src/i2p_dht_lab/effectreconcile.py", "tests/test_rev0057_deadletter_retry_reconcile.py", "docs/603-effect-reconcile-boundary.md", "exact-boundary effect reconciliation across recovery, dead-letter, retry, and journal evidence"),
        SurfaceLedgerEntry("src/i2p_dht_lab/reconcilefold.py", "tests/test_rev0057_deadletter_retry_reconcile.py", "docs/604-reconcilefold-audit-refactor.md", "rev0057 reconcilefold audit preserving rev0056 recoveryfold predecessor"),
    )


def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0057":
        return rev0057_entries()
    if revision == "rev0056":
        return rev0056_entries()
    return _prior_entries_for_revision_rev0057_reconcile(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0057_entries()

# rev0058 finality-ledger / retry-escrow / prune-guard surface ledger.
_prior_entries_for_revision_rev0058_finality = entries_for_revision


def rev0058_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0057_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/finalityledger.py", "tests/test_rev0058_finality_retryescrow_pruneguard.py", "docs/611-finality-ledger-after-reconcile.md", "signed finality markers preventing unresolved reconcile from becoming terminal authority"),
        SurfaceLedgerEntry("src/i2p_dht_lab/retryescrow.py", "tests/test_rev0058_finality_retryescrow_pruneguard.py", "docs/612-retry-escrow-deadletter-carry.md", "retry escrow preserving dead-letter lineage and idempotency across attempts"),
        SurfaceLedgerEntry("src/i2p_dht_lab/pruneguard.py", "tests/test_rev0058_finality_retryescrow_pruneguard.py", "docs/613-prune-guard-terminal-pending.md", "evidence prune guard for terminal soft prune versus pending dead-letter/retry hold"),
        SurfaceLedgerEntry("src/i2p_dht_lab/finalityfold.py", "tests/test_rev0058_finality_retryescrow_pruneguard.py", "docs/614-finalityfold-audit-refactor.md", "rev0058 finalityfold audit preserving rev0057 reconcilefold predecessor"),
    )


def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0058":
        return rev0058_entries()
    if revision == "rev0057":
        return rev0057_entries()
    return _prior_entries_for_revision_rev0058_finality(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0058_entries()

# rev0059 settlement/attestation/tombstone-repair branchlet fold.
_prior_entries_for_revision_rev0059_settlement = entries_for_revision


def rev0059_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0058_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/attestationpack.py", "tests/test_rev0059_settlement_attestation_tombrepair.py", "docs/622-attestation-pack-typed-evidence.md", "typed signed component evidence bundles after finality/reconcile"),
        SurfaceLedgerEntry("src/i2p_dht_lab/settlementlane.py", "tests/test_rev0059_settlement_attestation_tombrepair.py", "docs/621-settlement-lane-after-finality.md", "sticky settlement memory that refuses retry/dead-letter laundering"),
        SurfaceLedgerEntry("src/i2p_dht_lab/tombstonerepair.py", "tests/test_rev0059_settlement_attestation_tombrepair.py", "docs/623-tombstone-repair-after-settlement.md", "tombstone repair and resurrection-pressure evidence after settlement"),
        SurfaceLedgerEntry("src/i2p_dht_lab/settlementfold.py", "tests/test_rev0059_settlement_attestation_tombrepair.py", "docs/624-settlementfold-audit-refactor.md", "rev0059 settlementfold audit preserving finalityfold predecessor history"),
    )


def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0059":
        return rev0059_entries()
    if revision == "rev0058":
        return rev0058_entries()
    return _prior_entries_for_revision_rev0059_settlement(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0059_entries()


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0059_entries()

# rev0059 settlement-store / tomb-repair / canary-join surface ledger.
_prior_entries_for_revision_rev0059_settlementstore = entries_for_revision


def rev0059_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0058_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/settlementlane.py", "tests/test_rev0058_settlement_attestation_tombrepair.py", "docs/611-settlement-lane-after-reconcile.md", "folded rev0058 branchlet settlement lane"),
        SurfaceLedgerEntry("src/i2p_dht_lab/attestationpack.py", "tests/test_rev0058_settlement_attestation_tombrepair.py", "docs/612-attestation-pack-not-oracle.md", "folded rev0058 branchlet attestation pack"),
        SurfaceLedgerEntry("src/i2p_dht_lab/tombstonerepair.py", "tests/test_rev0058_settlement_attestation_tombrepair.py", "docs/613-tombstone-repair-after-settlement.md", "folded rev0058 branchlet tombstone repair"),
        SurfaceLedgerEntry("src/i2p_dht_lab/settlementfold.py", "tests/test_rev0058_settlement_attestation_tombrepair.py", "docs/614-settlementfold-audit-refactor.md", "folded rev0058 branchlet settlementfold audit"),
        SurfaceLedgerEntry("src/i2p_dht_lab/settlementstore.py", "tests/test_rev0059_settlementstore_tombmesh_canaryjoin.py", "docs/621-settlement-store-branch-join.md", "joined settlement store requiring finality and folded settlement branch to agree"),
        SurfaceLedgerEntry("src/i2p_dht_lab/tombrepairjoin.py", "tests/test_rev0059_settlementstore_tombmesh_canaryjoin.py", "docs/622-tomb-repair-join-after-prune.md", "tombstone repair/prune join after settlement store"),
        SurfaceLedgerEntry("src/i2p_dht_lab/canaryjoin.py", "tests/test_rev0059_settlementstore_tombmesh_canaryjoin.py", "docs/623-canary-join-after-settlement.md", "SAM/router canary join after settlement and tomb repair"),
        SurfaceLedgerEntry("src/i2p_dht_lab/settlementstorefold.py", "tests/test_rev0059_settlementstore_tombmesh_canaryjoin.py", "docs/624-settlementstorefold-audit-refactor.md", "rev0059 settlementstorefold audit preserving both rev0058 predecessors"),
    )


def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0059":
        return rev0059_entries()
    if revision == "rev0058":
        return rev0058_entries()
    return _prior_entries_for_revision_rev0059_settlementstore(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0059_entries()

# rev0059 final active surface-ledger override after settlement-store/terminal-receipt tests.
def rev0059_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0058_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/attestationpack.py", "tests/test_rev0059_settlement_attestation_tombrepair.py", "docs/622-attestation-pack-typed-evidence.md", "typed signed component evidence bundles after finality/reconcile"),
        SurfaceLedgerEntry("src/i2p_dht_lab/settlementlane.py", "tests/test_rev0059_settlement_attestation_tombrepair.py", "docs/621-settlement-lane-after-finality.md", "sticky settlement memory that refuses retry/dead-letter laundering"),
        SurfaceLedgerEntry("src/i2p_dht_lab/tombstonerepair.py", "tests/test_rev0059_settlement_attestation_tombrepair.py", "docs/623-tombstone-repair-after-settlement.md", "tombstone repair and resurrection-pressure evidence after settlement"),
        SurfaceLedgerEntry("src/i2p_dht_lab/settlementstore.py", "tests/test_rev0059_settlementstore_terminalreceipt.py", "docs/625-settlement-store-branch-join.md", "joined finality/settlement/prune/attestation/tombstone boundary after branch split"),
        SurfaceLedgerEntry("src/i2p_dht_lab/terminalreceipt.py", "tests/test_rev0059_settlementstore_terminalreceipt.py", "docs/626-terminal-receipt-after-finality.md", "terminal receipt after finality and prune agree at exact boundary"),
        SurfaceLedgerEntry("src/i2p_dht_lab/settlementfold.py", "tests/test_rev0059_settlement_attestation_tombrepair.py", "docs/624-settlementfold-audit-refactor.md", "rev0059 settlementfold audit preserving finalityfold predecessor history"),
    )

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0059":
        return rev0059_entries()
    if revision == "rev0058":
        return rev0058_entries()
    return _prior_entries_for_revision_rev0059_settlement(revision)

def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0059_entries()

def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0059_entries()

# rev0059 terminal receipt / idempotency repair / compaction audit final surface-ledger override.
def rev0059_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0058_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/terminalreceipt.py", "tests/test_rev0059_terminalreceipt_idemrepair_compactionaudit.py", "docs/621-terminal-receipt-after-finality.md", "terminal receipt after finality and prune agree at exact boundary"),
        SurfaceLedgerEntry("src/i2p_dht_lab/idempotencyrepair.py", "tests/test_rev0059_terminalreceipt_idemrepair_compactionaudit.py", "docs/622-idempotency-repair-lineage.md", "idempotency repair carrying retry/dead-letter lineage across terminal settlement"),
        SurfaceLedgerEntry("src/i2p_dht_lab/compactionaudit.py", "tests/test_rev0059_terminalreceipt_idemrepair_compactionaudit.py", "docs/623-compaction-audit-hard-negatives.md", "compaction audit preserving terminal receipt, repair, finality, prune, and hard negatives"),
        SurfaceLedgerEntry("src/i2p_dht_lab/settlementstore.py", "tests/test_rev0059_settlement_attestation_tombrepair.py", "docs/620-rev0059-terminalreceipt-idemrepair-compactionaudit.md", "folded settlement branch join after finality/prune split"),
        SurfaceLedgerEntry("src/i2p_dht_lab/terminalfold.py", "tests/test_rev0059_terminalreceipt_idemrepair_compactionaudit.py", "docs/624-terminalfold-audit-refactor.md", "rev0059 terminalfold audit preserving rev0058 finalityfold predecessor"),
        SurfaceLedgerEntry("src/i2p_dht_lab/settlementfold.py", "tests/test_rev0059_settlement_attestation_tombrepair.py", "docs/624-terminalfold-audit-refactor.md", "folded settlementfold audit kept visible under rev0059"),
    )

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0059":
        return rev0059_entries()
    if revision == "rev0058":
        return rev0058_entries()
    return _prior_entries_for_revision_rev0059_settlement(revision)

def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0059_entries()

def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0059_entries()


# rev0059 unified settlement-store / terminal-receipt active surface-ledger override.
def rev0059_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0058_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/settlementstore.py", "tests/test_rev0059_settlementstore_tombmesh_canaryjoin.py", "docs/621-settlement-store-branch-join.md", "settlement store joins terminal/retry finality, settlement, prune, attestation, tombstone, and escrow signals"),
        SurfaceLedgerEntry("src/i2p_dht_lab/tombrepairjoin.py", "tests/test_rev0059_settlementstore_tombmesh_canaryjoin.py", "docs/622-tomb-repair-join-after-prune.md", "tombstone repair and prune evidence joined after settlement store"),
        SurfaceLedgerEntry("src/i2p_dht_lab/canaryjoin.py", "tests/test_rev0059_settlementstore_tombmesh_canaryjoin.py", "docs/623-canary-join-after-settlement.md", "SAM/router canary readiness after settlement and tomb repair"),
        SurfaceLedgerEntry("src/i2p_dht_lab/settlementstorefold.py", "tests/test_rev0059_settlementstore_tombmesh_canaryjoin.py", "docs/624-settlementstorefold-audit-refactor.md", "rev0059 settlementstorefold current audit"),
        SurfaceLedgerEntry("src/i2p_dht_lab/settlementlane.py", "tests/test_rev0059_settlement_attestation_tombrepair.py", "docs/621-settlement-lane-after-finality.md", "folded settlement lane preserving retry/dead-letter holds"),
        SurfaceLedgerEntry("src/i2p_dht_lab/attestationpack.py", "tests/test_rev0059_settlement_attestation_tombrepair.py", "docs/622-attestation-pack-typed-evidence.md", "typed signed component evidence bundles"),
        SurfaceLedgerEntry("src/i2p_dht_lab/tombstonerepair.py", "tests/test_rev0059_settlement_attestation_tombrepair.py", "docs/623-tombstone-repair-after-settlement.md", "tombstone repair and resurrection-pressure evidence"),
        SurfaceLedgerEntry("src/i2p_dht_lab/settlementfold.py", "tests/test_rev0059_settlement_attestation_tombrepair.py", "docs/624-settlementfold-audit-refactor.md", "settlementfold branch audit kept visible"),
        SurfaceLedgerEntry("src/i2p_dht_lab/terminalreceipt.py", "tests/test_rev0059_terminalreceipt_idemrepair_compactionaudit.py", "docs/621-terminal-receipt-after-finality.md", "terminal receipt after finality and prune agree"),
        SurfaceLedgerEntry("src/i2p_dht_lab/idempotencyrepair.py", "tests/test_rev0059_terminalreceipt_idemrepair_compactionaudit.py", "docs/622-idempotency-repair-lineage.md", "idempotency repair carrying retry/dead-letter lineage"),
        SurfaceLedgerEntry("src/i2p_dht_lab/compactionaudit.py", "tests/test_rev0059_terminalreceipt_idemrepair_compactionaudit.py", "docs/623-compaction-audit-hard-negatives.md", "compaction audit preserving terminal and hard-negative evidence"),
        SurfaceLedgerEntry("src/i2p_dht_lab/terminalfold.py", "tests/test_rev0059_terminalreceipt_idemrepair_compactionaudit.py", "docs/624-terminalfold-audit-refactor.md", "terminalfold current audit"),
    )

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0059":
        return rev0059_entries()
    if revision == "rev0058":
        return rev0058_entries()
    return _prior_entries_for_revision_rev0059_settlement(revision)

def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0059_entries()

def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0059_entries()

# rev0060 live-send gate / delivery witness / send fence surface-ledger override.
def rev0060_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0059_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/livesendgate.py", "tests/test_rev0060_livesend_delivery_fence.py", "docs/638-live-send-gate-before-network-write.md", "no-network live-send gate after settlement/tomb/canary readiness"),
        SurfaceLedgerEntry("src/i2p_dht_lab/deliverywitness.py", "tests/test_rev0060_livesend_delivery_fence.py", "docs/639-delivery-witness-after-send.md", "delivery witness evidence after a future outbound public send"),
        SurfaceLedgerEntry("src/i2p_dht_lab/sendfence.py", "tests/test_rev0060_livesend_delivery_fence.py", "docs/640-send-fence-restart-memory.md", "local monotonic send fence preventing permission/delivery laundering after restart"),
        SurfaceLedgerEntry("src/i2p_dht_lab/fenceaudit.py", "tests/test_rev0060_livesend_delivery_fence.py", "docs/641-fenceaudit-audit-refactor.md", "rev0060 fenceaudit preserving rev0059 settlementstorefold predecessor history"),
    )


def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0060":
        return rev0060_entries()
    if revision == "rev0059":
        return rev0059_entries()
    if revision == "rev0058":
        return rev0058_entries()
    return _prior_entries_for_revision_rev0059_settlement(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0060_entries()


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0060_entries()

# rev0061 delivery settlement / ack archive / ack prune join surface-ledger override.
def rev0061_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0060_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/deliverysettlement.py", "tests/test_rev0061_deliverysettlement_ackarchive_prunejoin.py", "docs/648-delivery-settlement-after-fence.md", "delivery settlement after live-send/delivery/fence agree at one boundary"),
        SurfaceLedgerEntry("src/i2p_dht_lab/ackarchive.py", "tests/test_rev0061_deliverysettlement_ackarchive_prunejoin.py", "docs/649-ack-archive-restart-memory.md", "ack archive restart memory for settled delivered public-edge sends"),
        SurfaceLedgerEntry("src/i2p_dht_lab/ackprunejoin.py", "tests/test_rev0061_deliverysettlement_ackarchive_prunejoin.py", "docs/650-ack-prune-join-boundary.md", "ack prune join preventing delivered-send evidence laundering"),
        SurfaceLedgerEntry("src/i2p_dht_lab/ackfold.py", "tests/test_rev0061_deliverysettlement_ackarchive_prunejoin.py", "docs/651-ackfold-audit-refactor.md", "rev0061 ackfold preserving rev0060 fenceaudit predecessor history"),
    )


def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0061":
        return rev0061_entries()
    if revision == "rev0060":
        return rev0060_entries()
    if revision == "rev0059":
        return rev0059_entries()
    if revision == "rev0058":
        return rev0058_entries()
    return _prior_entries_for_revision_rev0059_settlement(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0061_entries()


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0061_entries()

# rev0062 ACK/repair live-egress fold surface-ledger override.
def rev0062_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0061_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/deliveryrepair.py", "tests/test_rev0062_ackrepair_liveegress_retryfence.py", "docs/658-delivery-repair-live-egress-branchfold.md", "folded delivery-repair branchlet for missing ACK public-edge writes"),
        SurfaceLedgerEntry("src/i2p_dht_lab/rollbackprobe.py", "tests/test_rev0062_ackrepair_liveegress_retryfence.py", "docs/658-delivery-repair-live-egress-branchfold.md", "rollback probe before retry or withdraw repair is permitted"),
        SurfaceLedgerEntry("src/i2p_dht_lab/liveegress.py", "tests/test_rev0062_ackrepair_liveegress_retryfence.py", "docs/658-delivery-repair-live-egress-branchfold.md", "live egress retry/withdraw readiness without network IO"),
        SurfaceLedgerEntry("src/i2p_dht_lab/ackrepairjoin.py", "tests/test_rev0062_ackrepair_liveegress_retryfence.py", "docs/659-ack-repair-join-boundary.md", "joined boundary between terminal ACK path and repair retry path"),
        SurfaceLedgerEntry("src/i2p_dht_lab/retryfence.py", "tests/test_rev0062_ackrepair_liveegress_retryfence.py", "docs/660-retry-fence-restart-memory.md", "previous-linked restart memory for retry and withdraw readiness"),
        SurfaceLedgerEntry("src/i2p_dht_lab/repairpruneguard.py", "tests/test_rev0062_ackrepair_liveegress_retryfence.py", "docs/661-repair-prune-guard.md", "guard preventing ACK prune from deleting repair debt"),
        SurfaceLedgerEntry("src/i2p_dht_lab/egressrepairfold.py", "tests/test_rev0062_ackrepair_liveegress_retryfence.py", "docs/662-egressrepairfold-audit-refactor.md", "rev0062 egressrepairfold preserving rev0061 ackfold and branchlet ancestry"),
    )


def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0062":
        return rev0062_entries()
    if revision == "rev0061":
        return rev0061_entries()
    if revision == "rev0060":
        return rev0060_entries()
    if revision == "rev0059":
        return rev0059_entries()
    if revision == "rev0058":
        return rev0058_entries()
    return _prior_entries_for_revision_rev0059_settlement(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0062_entries()


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0062_entries()

# rev0063 late ACK / retry settlement / egress journal surface-ledger override.
def rev0063_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0062_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/lateack.py", "tests/test_rev0063_lateack_retrysettle_egressjournal.py", "docs/669-late-ack-after-retry-fence.md", "late original ACK evidence after retry/withdraw fence"),
        SurfaceLedgerEntry("src/i2p_dht_lab/retrysettlement.py", "tests/test_rev0063_lateack_retrysettle_egressjournal.py", "docs/670-retry-settlement-and-withdraw-repair.md", "retry and withdraw settlement independent from original send"),
        SurfaceLedgerEntry("src/i2p_dht_lab/withdrawrepair.py", "tests/test_rev0063_lateack_retrysettle_egressjournal.py", "docs/670-retry-settlement-and-withdraw-repair.md", "withdraw repair publication memory after settlement"),
        SurfaceLedgerEntry("src/i2p_dht_lab/egressjournal.py", "tests/test_rev0063_lateack_retrysettle_egressjournal.py", "docs/671-egress-journal-compaction.md", "egress journal compaction preserving late ACK / retry contradictions"),
        SurfaceLedgerEntry("src/i2p_dht_lab/lateackfold.py", "tests/test_rev0063_lateack_retrysettle_egressjournal.py", "docs/672-lateackfold-audit-refactor.md", "rev0063 lateackfold audit preserving rev0062 predecessor"),
    )


def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0063":
        return rev0063_entries()
    if revision == "rev0062":
        return rev0062_entries()
    if revision == "rev0061":
        return rev0061_entries()
    if revision == "rev0060":
        return rev0060_entries()
    if revision == "rev0059":
        return rev0059_entries()
    if revision == "rev0058":
        return rev0058_entries()
    return _prior_entries_for_revision_rev0059_settlement(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0063_entries()


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0063_entries()

# rev0064 retry-publication / idempotency mesh / delivery-repair surface-ledger override.
def rev0064_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0063_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/retrypublish.py", "tests/test_rev0064_retrypublish_idempotencymesh_deliveryrepair.py", "docs/679-retry-publication-outbox.md", "retry-publication staging after retry/withdraw settlement and egress journal agreement"),
        SurfaceLedgerEntry("src/i2p_dht_lab/idempotencymesh.py", "tests/test_rev0064_retrypublish_idempotencymesh_deliveryrepair.py", "docs/680-idempotency-mesh-lineage.md", "idempotency lineage joining original ACK, retry settlement, publication, and contradiction pressure"),
        SurfaceLedgerEntry("src/i2p_dht_lab/deliveryrepairmesh.py", "tests/test_rev0064_retrypublish_idempotencymesh_deliveryrepair.py", "docs/681-delivery-repair-remote-witness.md", "delivery repair mesh requiring remote witness pressure for duplicate delivery ambiguity"),
        SurfaceLedgerEntry("src/i2p_dht_lab/retrypublishfold.py", "tests/test_rev0064_retrypublish_idempotencymesh_deliveryrepair.py", "docs/682-retrypublishfold-audit-refactor.md", "rev0064 retrypublishfold audit preserving rev0063 predecessor"),
    )

_prior_entries_for_revision_rev0064 = entries_for_revision

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0064":
        return rev0064_entries()
    if revision == "rev0063":
        return rev0063_entries()
    return _prior_entries_for_revision_rev0064(revision)

def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0064_entries()

def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0064_entries()

# rev0065 remote witness / repair outbox / conflict cooldown surface-ledger override.
def rev0065_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0064_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/remotewitnessledger.py", "tests/test_rev0065_remotewitness_repairoutbox_conflictcooldown.py", "docs/689-remote-witness-ledger-rounds.md", "remote witness replay and contradiction-carrying ledger across duplicate-delivery rounds"),
        SurfaceLedgerEntry("src/i2p_dht_lab/repairoutbox.py", "tests/test_rev0065_remotewitness_repairoutbox_conflictcooldown.py", "docs/690-repair-outbox-after-duplicate-conflict.md", "repair-outbox staging after remote duplicate conflict without live network side effects"),
        SurfaceLedgerEntry("src/i2p_dht_lab/conflictcooldown.py", "tests/test_rev0065_remotewitness_repairoutbox_conflictcooldown.py", "docs/691-conflict-cooldown-duplicate-pressure.md", "local cooldown pressure for repeated duplicate-delivery conflict evidence"),
        SurfaceLedgerEntry("src/i2p_dht_lab/remoterepairfold.py", "tests/test_rev0065_remotewitness_repairoutbox_conflictcooldown.py", "docs/692-remoterepairfold-audit-refactor.md", "rev0065 remote repair fold preserving rev0064 retrypublishfold predecessor"),
    )

_prior_entries_for_revision_rev0065 = entries_for_revision

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0065":
        return rev0065_entries()
    if revision == "rev0064":
        return rev0064_entries()
    return _prior_entries_for_revision_rev0065(revision)

def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0065_entries()

def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0065_entries()

# rev0066 repair-publish / ACK-ledger / duplicate-closure surface-ledger override.
def rev0066_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0065_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/repairpublishgate.py", "tests/test_rev0066_repairpublish_ackclosure.py", "docs/699-repair-publish-gate-after-cooldown.md", "repair-publication gate after repair outbox and conflict cooldown agree"),
        SurfaceLedgerEntry("src/i2p_dht_lab/repairackledger.py", "tests/test_rev0066_repairpublish_ackclosure.py", "docs/700-repair-ack-ledger.md", "repair ACK ledger for remote/local repair-publication observations"),
        SurfaceLedgerEntry("src/i2p_dht_lab/duplicateclosure.py", "tests/test_rev0066_repairpublish_ackclosure.py", "docs/701-duplicate-closure-finality.md", "duplicate-conflict closure after repair ACK while preserving contradiction memory"),
        SurfaceLedgerEntry("src/i2p_dht_lab/repairpublishfold.py", "tests/test_rev0066_repairpublish_ackclosure.py", "docs/702-repairpublishfold-audit-refactor.md", "rev0066 repairpublishfold preserving rev0065 remote-repair predecessor history"),
    )


def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0066":
        return rev0066_entries()
    if revision == "rev0065":
        return rev0065_entries()
    if revision == "rev0064":
        return rev0064_entries()
    if revision == "rev0063":
        return rev0063_entries()
    if revision == "rev0062":
        return rev0062_entries()
    if revision == "rev0061":
        return rev0061_entries()
    if revision == "rev0060":
        return rev0060_entries()
    if revision == "rev0059":
        return rev0059_entries()
    if revision == "rev0058":
        return rev0058_entries()
    return _prior_entries_for_revision_rev0059_settlement(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0066_entries()


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0066_entries()

# rev0067 repair-settlement / closure-archive / repair-prune surface-ledger override.
def rev0067_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0066_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/repairsettlement.py", "tests/test_rev0067_repairsettlement_archive_prune.py", "docs/709-repair-settlement-after-duplicate-closure.md", "repair settlement after duplicate closure while preserving contradiction memory"),
        SurfaceLedgerEntry("src/i2p_dht_lab/closurearchive.py", "tests/test_rev0067_repairsettlement_archive_prune.py", "docs/710-closure-archive-restart-memory.md", "closure archive restart memory for settlement and contradiction evidence"),
        SurfaceLedgerEntry("src/i2p_dht_lab/repairprune.py", "tests/test_rev0067_repairsettlement_archive_prune.py", "docs/711-repair-prune-protected-memory.md", "repair prune gate that allows soft pruning only while protected evidence remains"),
        SurfaceLedgerEntry("src/i2p_dht_lab/repairsettlementfold.py", "tests/test_rev0067_repairsettlement_archive_prune.py", "docs/712-repairsettlementfold-audit-refactor.md", "rev0067 repairsettlementfold preserving rev0066 repairpublishfold predecessor history"),
    )


def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0067":
        return rev0067_entries()
    if revision == "rev0066":
        return rev0066_entries()
    if revision == "rev0065":
        return rev0065_entries()
    if revision == "rev0064":
        return rev0064_entries()
    if revision == "rev0063":
        return rev0063_entries()
    if revision == "rev0062":
        return rev0062_entries()
    if revision == "rev0061":
        return rev0061_entries()
    if revision == "rev0060":
        return rev0060_entries()
    if revision == "rev0059":
        return rev0059_entries()
    if revision == "rev0058":
        return rev0058_entries()
    return _prior_entries_for_revision_rev0059_settlement(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0067_entries()


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0067_entries()

# rev0068 archive-journal / prune-replay / closure-audit surface-ledger override.
def rev0068_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0067_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/archivejournal.py", "tests/test_rev0068_archivejournal_prunereplay_closureaudit.py", "docs/719-archive-journal-after-prune.md", "archive journal restart memory after repair prune while preserving contradiction/prune memory"),
        SurfaceLedgerEntry("src/i2p_dht_lab/prunereplay.py", "tests/test_rev0068_archivejournal_prunereplay_closureaudit.py", "docs/720-prune-replay-resistance.md", "prune replay resistance across restart generations after archive journal acceptance"),
        SurfaceLedgerEntry("src/i2p_dht_lab/closureaudit.py", "tests/test_rev0068_archivejournal_prunereplay_closureaudit.py", "docs/721-closure-audit-restart-boundary.md", "closure audit joining settlement/archive/prune/journal/replay at one exact boundary"),
        SurfaceLedgerEntry("src/i2p_dht_lab/archivejournalfold.py", "tests/test_rev0068_archivejournal_prunereplay_closureaudit.py", "docs/722-archivejournalfold-audit-refactor.md", "rev0068 archivejournalfold preserving rev0067 repairsettlementfold predecessor history"),
    )


def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0068":
        return rev0068_entries()
    if revision == "rev0067":
        return rev0067_entries()
    if revision == "rev0066":
        return rev0066_entries()
    if revision == "rev0065":
        return rev0065_entries()
    if revision == "rev0064":
        return rev0064_entries()
    if revision == "rev0063":
        return rev0063_entries()
    if revision == "rev0062":
        return rev0062_entries()
    if revision == "rev0061":
        return rev0061_entries()
    if revision == "rev0060":
        return rev0060_entries()
    if revision == "rev0059":
        return rev0059_entries()
    if revision == "rev0058":
        return rev0058_entries()
    return _prior_entries_for_revision_rev0059_settlement(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0068_entries()


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0068_entries()

# rev0069 closure seal / retention proof / audit export surface-ledger override.
def rev0069_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0068_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/closureseal.py", "tests/test_rev0069_closureseal_retention_export.py", "docs/729-closure-seal-after-audit.md", "closure seal after closure audit while preserving contradiction memory"),
        SurfaceLedgerEntry("src/i2p_dht_lab/retentionproof.py", "tests/test_rev0069_closureseal_retention_export.py", "docs/730-retention-proof-hard-negative-carry.md", "retention proof preserving required evidence classes and hard-negative memory"),
        SurfaceLedgerEntry("src/i2p_dht_lab/auditexport.py", "tests/test_rev0069_closureseal_retention_export.py", "docs/731-audit-export-redacted-boundary.md", "redacted audit export bundle before any live publication"),
        SurfaceLedgerEntry("src/i2p_dht_lab/closuresealfold.py", "tests/test_rev0069_closureseal_retention_export.py", "docs/732-closuresealfold-audit-refactor.md", "rev0069 closuresealfold preserving rev0068 archivejournalfold predecessor history"),
    )


def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0069":
        return rev0069_entries()
    if revision == "rev0068":
        return rev0068_entries()
    if revision == "rev0067":
        return rev0067_entries()
    if revision == "rev0066":
        return rev0066_entries()
    if revision == "rev0065":
        return rev0065_entries()
    if revision == "rev0064":
        return rev0064_entries()
    if revision == "rev0063":
        return rev0063_entries()
    if revision == "rev0062":
        return rev0062_entries()
    if revision == "rev0061":
        return rev0061_entries()
    if revision == "rev0060":
        return rev0060_entries()
    if revision == "rev0059":
        return rev0059_entries()
    if revision == "rev0058":
        return rev0058_entries()
    return _prior_entries_for_revision_rev0059_settlement(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0069_entries()


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0069_entries()

# rev0070 export receipt / retention GC / closure handoff surface-ledger override.
def rev0070_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0069_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/exportreceipt.py", "tests/test_rev0070_exportreceipt_retentiongc_handoff.py", "docs/739-export-receipt-restart-memory.md", "export receipt restart memory after redacted audit export"),
        SurfaceLedgerEntry("src/i2p_dht_lab/retentiongc.py", "tests/test_rev0070_exportreceipt_retentiongc_handoff.py", "docs/740-retention-gc-after-export.md", "retention GC preserving contradiction/hard-negative memory after export"),
        SurfaceLedgerEntry("src/i2p_dht_lab/closurehandoff.py", "tests/test_rev0070_exportreceipt_retentiongc_handoff.py", "docs/741-closure-handoff-redacted-boundary.md", "redacted closure handoff after receipt and retention GC"),
        SurfaceLedgerEntry("src/i2p_dht_lab/exporthandofffold.py", "tests/test_rev0070_exportreceipt_retentiongc_handoff.py", "docs/742-exporthandofffold-audit-refactor.md", "rev0070 exporthandofffold preserving rev0069 closuresealfold predecessor history"),
    )


def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0070":
        return rev0070_entries()
    if revision == "rev0069":
        return rev0069_entries()
    if revision == "rev0068":
        return rev0068_entries()
    if revision == "rev0067":
        return rev0067_entries()
    if revision == "rev0066":
        return rev0066_entries()
    if revision == "rev0065":
        return rev0065_entries()
    if revision == "rev0064":
        return rev0064_entries()
    if revision == "rev0063":
        return rev0063_entries()
    if revision == "rev0062":
        return rev0062_entries()
    if revision == "rev0061":
        return rev0061_entries()
    if revision == "rev0060":
        return rev0060_entries()
    if revision == "rev0059":
        return rev0059_entries()
    if revision == "rev0058":
        return rev0058_entries()
    return _prior_entries_for_revision_rev0059_settlement(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0070_entries()


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0070_entries()

# rev0071 handoff receipt / import / summary lineage surface-ledger override.
def rev0071_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0070_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/handoffreceipt.py", "tests/test_rev0071_handoffreceipt_import_summarylineage.py", "docs/749-handoff-receipt-recipient-boundary.md", "recipient receipt memory after redacted closure handoff"),
        SurfaceLedgerEntry("src/i2p_dht_lab/handoffimport.py", "tests/test_rev0071_handoffreceipt_import_summarylineage.py", "docs/750-handoff-import-redacted-state.md", "redacted import markers after accepted handoff receipt"),
        SurfaceLedgerEntry("src/i2p_dht_lab/summarylineage.py", "tests/test_rev0071_handoffreceipt_import_summarylineage.py", "docs/751-summary-lineage-redacted-boundary.md", "redacted summary lineage after accepted import"),
        SurfaceLedgerEntry("src/i2p_dht_lab/handoffreceiptfold.py", "tests/test_rev0071_handoffreceipt_import_summarylineage.py", "docs/752-handoffreceiptfold-audit-refactor.md", "rev0071 handoffreceiptfold preserving rev0070 exporthandofffold predecessor history"),
    )


def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0071":
        return rev0071_entries()
    if revision == "rev0070":
        return rev0070_entries()
    if revision == "rev0069":
        return rev0069_entries()
    if revision == "rev0068":
        return rev0068_entries()
    if revision == "rev0067":
        return rev0067_entries()
    if revision == "rev0066":
        return rev0066_entries()
    if revision == "rev0065":
        return rev0065_entries()
    if revision == "rev0064":
        return rev0064_entries()
    if revision == "rev0063":
        return rev0063_entries()
    if revision == "rev0062":
        return rev0062_entries()
    if revision == "rev0061":
        return rev0061_entries()
    if revision == "rev0060":
        return rev0060_entries()
    if revision == "rev0059":
        return rev0059_entries()
    if revision == "rev0058":
        return rev0058_entries()
    return _prior_entries_for_revision_rev0059_settlement(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0071_entries()


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0071_entries()

# rev0072 summary receipt / import archive / lineage prune surface-ledger override.
def rev0072_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0071_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/summaryreceipt.py", "tests/test_rev0072_summaryreceipt_importarchive_lineageprune.py", "docs/759-summary-receipt-after-lineage.md", "recipient summary receipt memory after redacted summary lineage"),
        SurfaceLedgerEntry("src/i2p_dht_lab/importarchive.py", "tests/test_rev0072_summaryreceipt_importarchive_lineageprune.py", "docs/760-import-archive-after-summary-receipt.md", "restart-sticky import archive after accepted summary receipt"),
        SurfaceLedgerEntry("src/i2p_dht_lab/lineageprune.py", "tests/test_rev0072_summaryreceipt_importarchive_lineageprune.py", "docs/761-lineage-prune-guard.md", "lineage prune guard preserving contradiction/import/archive memory"),
        SurfaceLedgerEntry("src/i2p_dht_lab/summaryreceiptfold.py", "tests/test_rev0072_summaryreceipt_importarchive_lineageprune.py", "docs/762-summaryreceiptfold-audit-refactor.md", "rev0072 summaryreceiptfold preserving rev0071 handoffreceiptfold predecessor history"),
    )


def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0072":
        return rev0072_entries()
    if revision == "rev0071":
        return rev0071_entries()
    if revision == "rev0070":
        return rev0070_entries()
    if revision == "rev0069":
        return rev0069_entries()
    if revision == "rev0068":
        return rev0068_entries()
    if revision == "rev0067":
        return rev0067_entries()
    if revision == "rev0066":
        return rev0066_entries()
    if revision == "rev0065":
        return rev0065_entries()
    if revision == "rev0064":
        return rev0064_entries()
    if revision == "rev0063":
        return rev0063_entries()
    if revision == "rev0062":
        return rev0062_entries()
    if revision == "rev0061":
        return rev0061_entries()
    if revision == "rev0060":
        return rev0060_entries()
    if revision == "rev0059":
        return rev0059_entries()
    if revision == "rev0058":
        return rev0058_entries()
    return _prior_entries_for_revision_rev0059_settlement(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0072_entries()


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0072_entries()

# rev0073 summary publication / redaction witness / import-prune audit surface-ledger override.
def rev0073_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0072_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/summarypublish.py", "tests/test_rev0073_summarypublish_redactionwitness_importpruneaudit.py", "docs/769-summary-publication-after-lineage-prune.md", "summary publication after receipt/archive/lineage-prune agreement"),
        SurfaceLedgerEntry("src/i2p_dht_lab/redactionwitness.py", "tests/test_rev0073_summarypublish_redactionwitness_importpruneaudit.py", "docs/770-redaction-witness-receipts.md", "redaction witness receipts for redacted summary publication"),
        SurfaceLedgerEntry("src/i2p_dht_lab/importpruneaudit.py", "tests/test_rev0073_summarypublish_redactionwitness_importpruneaudit.py", "docs/771-import-prune-audit-after-restart.md", "import-prune audit joining publication, redaction witness, archive, and prune"),
        SurfaceLedgerEntry("src/i2p_dht_lab/summarypublishfold.py", "tests/test_rev0073_summarypublish_redactionwitness_importpruneaudit.py", "docs/772-summarypublishfold-audit-refactor.md", "rev0073 summarypublishfold preserving rev0072 summaryreceiptfold predecessor history"),
    )


def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0073":
        return rev0073_entries()
    if revision == "rev0072":
        return rev0072_entries()
    if revision == "rev0071":
        return rev0071_entries()
    if revision == "rev0070":
        return rev0070_entries()
    if revision == "rev0069":
        return rev0069_entries()
    if revision == "rev0068":
        return rev0068_entries()
    if revision == "rev0067":
        return rev0067_entries()
    if revision == "rev0066":
        return rev0066_entries()
    if revision == "rev0065":
        return rev0065_entries()
    if revision == "rev0064":
        return rev0064_entries()
    if revision == "rev0063":
        return rev0063_entries()
    if revision == "rev0062":
        return rev0062_entries()
    if revision == "rev0061":
        return rev0061_entries()
    if revision == "rev0060":
        return rev0060_entries()
    if revision == "rev0059":
        return rev0059_entries()
    if revision == "rev0058":
        return rev0058_entries()
    return _prior_entries_for_revision_rev0059_settlement(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0073_entries()


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0073_entries()

# rev0074 summary outbox / redaction archive / publish fence surface-ledger override.
def rev0074_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0073_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/summaryoutbox.py", "tests/test_rev0074_summaryoutbox_redactionarchive_publishfence.py", "docs/779-summary-outbox-after-publication.md", "summary outbox staging after publication/redaction/audit agreement"),
        SurfaceLedgerEntry("src/i2p_dht_lab/redactionarchive.py", "tests/test_rev0074_summaryoutbox_redactionarchive_publishfence.py", "docs/780-redaction-archive-restart-memory.md", "redaction archive restart memory after witness acceptance"),
        SurfaceLedgerEntry("src/i2p_dht_lab/publishfence.py", "tests/test_rev0074_summaryoutbox_redactionarchive_publishfence.py", "docs/781-publish-fence-before-summary-write.md", "summary publish fence before future live/public write"),
        SurfaceLedgerEntry("src/i2p_dht_lab/summaryoutboxfold.py", "tests/test_rev0074_summaryoutbox_redactionarchive_publishfence.py", "docs/782-summaryoutboxfold-audit-refactor.md", "rev0074 summaryoutboxfold preserving rev0073 summarypublishfold predecessor history"),
    )


def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0074":
        return rev0074_entries()
    if revision == "rev0073":
        return rev0073_entries()
    if revision == "rev0072":
        return rev0072_entries()
    if revision == "rev0071":
        return rev0071_entries()
    if revision == "rev0070":
        return rev0070_entries()
    if revision == "rev0069":
        return rev0069_entries()
    if revision == "rev0068":
        return rev0068_entries()
    if revision == "rev0067":
        return rev0067_entries()
    if revision == "rev0066":
        return rev0066_entries()
    if revision == "rev0065":
        return rev0065_entries()
    if revision == "rev0064":
        return rev0064_entries()
    if revision == "rev0063":
        return rev0063_entries()
    if revision == "rev0062":
        return rev0062_entries()
    if revision == "rev0061":
        return rev0061_entries()
    if revision == "rev0060":
        return rev0060_entries()
    if revision == "rev0059":
        return rev0059_entries()
    if revision == "rev0058":
        return rev0058_entries()
    return _prior_entries_for_revision_rev0059_settlement(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0074_entries()


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0074_entries()

# rev0075 summary send canary / redaction GC / outbox settlement surface-ledger override.
def rev0075_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0074_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/summarysendcanary.py", "tests/test_rev0075_summarysendcanary_redactiongc_outboxsettlement.py", "docs/789-summary-send-canary-before-live-write.md", "no-network summary-send canary after publish fence"),
        SurfaceLedgerEntry("src/i2p_dht_lab/redactiongc.py", "tests/test_rev0075_summarysendcanary_redactiongc_outboxsettlement.py", "docs/790-redaction-gc-join-after-archive.md", "redaction GC preserving archive/fence/contradiction memory"),
        SurfaceLedgerEntry("src/i2p_dht_lab/outboxsettlement.py", "tests/test_rev0075_summarysendcanary_redactiongc_outboxsettlement.py", "docs/791-outbox-settlement-prepared-aborted-suppressed.md", "summary outbox settlement markers after canary/GC"),
        SurfaceLedgerEntry("src/i2p_dht_lab/summarysendfold.py", "tests/test_rev0075_summarysendcanary_redactiongc_outboxsettlement.py", "docs/792-summarysendfold-audit-refactor.md", "rev0075 summarysendfold preserving rev0074 summaryoutboxfold predecessor history"),
    )


def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0075":
        return rev0075_entries()
    if revision == "rev0074":
        return rev0074_entries()
    if revision == "rev0073":
        return rev0073_entries()
    if revision == "rev0072":
        return rev0072_entries()
    if revision == "rev0071":
        return rev0071_entries()
    if revision == "rev0070":
        return rev0070_entries()
    if revision == "rev0069":
        return rev0069_entries()
    if revision == "rev0068":
        return rev0068_entries()
    if revision == "rev0067":
        return rev0067_entries()
    if revision == "rev0066":
        return rev0066_entries()
    if revision == "rev0065":
        return rev0065_entries()
    if revision == "rev0064":
        return rev0064_entries()
    if revision == "rev0063":
        return rev0063_entries()
    if revision == "rev0062":
        return rev0062_entries()
    if revision == "rev0061":
        return rev0061_entries()
    if revision == "rev0060":
        return rev0060_entries()
    if revision == "rev0059":
        return rev0059_entries()
    if revision == "rev0058":
        return rev0058_entries()
    return _prior_entries_for_revision_rev0059_settlement(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0075_entries()


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0075_entries()

# rev0075 summary send canary / redaction GC / outbox settlement surface-ledger override.
def rev0075_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0074_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/summarysendcanary.py", "tests/test_rev0075_summarysendcanary_redactiongc_outboxsettlement.py", "docs/789-summary-send-canary-before-live-write.md", "no-network summary-send canary after outbox/archive/fence agreement"),
        SurfaceLedgerEntry("src/i2p_dht_lab/redactiongc.py", "tests/test_rev0075_summarysendcanary_redactiongc_outboxsettlement.py", "docs/790-redaction-gc-join-after-archive.md", "redaction GC join preserving contradiction memory"),
        SurfaceLedgerEntry("src/i2p_dht_lab/outboxsettlement.py", "tests/test_rev0075_summarysendcanary_redactiongc_outboxsettlement.py", "docs/791-outbox-settlement-prepared-aborted-suppressed.md", "prepared/aborted/suppressed outbox settlement markers"),
        SurfaceLedgerEntry("src/i2p_dht_lab/summarysendfold.py", "tests/test_rev0075_summarysendcanary_redactiongc_outboxsettlement.py", "docs/792-summarysendfold-audit-refactor.md", "rev0075 summarysendfold preserving rev0074 summaryoutboxfold predecessor history"),
    )


def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0075":
        return rev0075_entries()
    if revision == "rev0074":
        return rev0074_entries()
    if revision == "rev0073":
        return rev0073_entries()
    if revision == "rev0072":
        return rev0072_entries()
    if revision == "rev0071":
        return rev0071_entries()
    if revision == "rev0070":
        return rev0070_entries()
    if revision == "rev0069":
        return rev0069_entries()
    if revision == "rev0068":
        return rev0068_entries()
    if revision == "rev0067":
        return rev0067_entries()
    if revision == "rev0066":
        return rev0066_entries()
    if revision == "rev0065":
        return rev0065_entries()
    if revision == "rev0064":
        return rev0064_entries()
    if revision == "rev0063":
        return rev0063_entries()
    if revision == "rev0062":
        return rev0062_entries()
    if revision == "rev0061":
        return rev0061_entries()
    if revision == "rev0060":
        return rev0060_entries()
    if revision == "rev0059":
        return rev0059_entries()
    if revision == "rev0058":
        return rev0058_entries()
    return _prior_entries_for_revision_rev0059_settlement(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0075_entries()


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0075_entries()

# rev0075 corrected active surface-ledger override after branchlet fold.
def rev0075_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0074_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/outboxsettlement.py", "tests/test_rev0075_summarysendcanary_redactiongc_outboxsettlement.py", "docs/791-outbox-settlement-prepared-aborted-suppressed.md", "joined active summary-outbox path with folded settlement/ledger/GC branch"),
        SurfaceLedgerEntry("src/i2p_dht_lab/summarysendcanary.py", "tests/test_rev0075_summarysendcanary_redactiongc_outboxsettlement.py", "docs/789-summary-send-canary-before-live-write.md", "no-network summary-send canary after outbox settlement"),
        SurfaceLedgerEntry("src/i2p_dht_lab/summarysettlement.py", "tests/test_rev0074_summarysettlement_publicledger_redactiongc.py", "docs/790-redaction-gc-join-after-archive.md", "folded summary-settlement branchlet source"),
        SurfaceLedgerEntry("src/i2p_dht_lab/publicledger.py", "tests/test_rev0074_summarysettlement_publicledger_redactiongc.py", "docs/790-redaction-gc-join-after-archive.md", "folded public-ledger branchlet source"),
        SurfaceLedgerEntry("src/i2p_dht_lab/redactiongc.py", "tests/test_rev0074_summarysettlement_publicledger_redactiongc.py", "docs/790-redaction-gc-join-after-archive.md", "folded redaction-GC branchlet source"),
        SurfaceLedgerEntry("src/i2p_dht_lab/summarysendfold.py", "tests/test_rev0075_summarysendcanary_redactiongc_outboxsettlement.py", "docs/792-summarysendfold-audit-refactor.md", "rev0075 summarysendfold preserving rev0074 predecessor and sibling branchlet history"),
    )


def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0075":
        return rev0075_entries()
    if revision == "rev0074":
        return rev0074_entries()
    if revision == "rev0073":
        return rev0073_entries()
    if revision == "rev0072":
        return rev0072_entries()
    if revision == "rev0071":
        return rev0071_entries()
    if revision == "rev0070":
        return rev0070_entries()
    if revision == "rev0069":
        return rev0069_entries()
    if revision == "rev0068":
        return rev0068_entries()
    if revision == "rev0067":
        return rev0067_entries()
    if revision == "rev0066":
        return rev0066_entries()
    if revision == "rev0065":
        return rev0065_entries()
    if revision == "rev0064":
        return rev0064_entries()
    if revision == "rev0063":
        return rev0063_entries()
    if revision == "rev0062":
        return rev0062_entries()
    if revision == "rev0061":
        return rev0061_entries()
    if revision == "rev0060":
        return rev0060_entries()
    if revision == "rev0059":
        return rev0059_entries()
    if revision == "rev0058":
        return rev0058_entries()
    return _prior_entries_for_revision_rev0059_settlement(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0075_entries()


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0075_entries()

# rev0076 summary drain / delivery witness / settlement fence surface-ledger override.
def rev0076_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0075_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/summarydrain.py", "tests/test_rev0076_summarydrain_deliverywitness_settlementfence.py", "docs/799-summary-drain-after-canary.md", "summary drain after no-network summary-send canary"),
        SurfaceLedgerEntry("src/i2p_dht_lab/summarydeliverywitness.py", "tests/test_rev0076_summarydrain_deliverywitness_settlementfence.py", "docs/800-summary-delivery-witness.md", "typed delivery ACK/refusal/missing-ACK evidence after summary drain"),
        SurfaceLedgerEntry("src/i2p_dht_lab/settlementfence.py", "tests/test_rev0076_summarydrain_deliverywitness_settlementfence.py", "docs/801-settlement-fence-after-delivery.md", "settlement fence carrying redaction and contradiction memory"),
        SurfaceLedgerEntry("src/i2p_dht_lab/summarydeliveryfold.py", "tests/test_rev0076_summarydrain_deliverywitness_settlementfence.py", "docs/802-summarydeliveryfold-audit-refactor.md", "rev0076 summarydeliveryfold preserving rev0075 summarysendfold predecessor history"),
    )


def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0076":
        return rev0076_entries()
    if revision == "rev0075":
        return rev0075_entries()
    if revision == "rev0074":
        return rev0074_entries()
    if revision == "rev0073":
        return rev0073_entries()
    if revision == "rev0072":
        return rev0072_entries()
    if revision == "rev0071":
        return rev0071_entries()
    if revision == "rev0070":
        return rev0070_entries()
    if revision == "rev0069":
        return rev0069_entries()
    if revision == "rev0068":
        return rev0068_entries()
    if revision == "rev0067":
        return rev0067_entries()
    if revision == "rev0066":
        return rev0066_entries()
    if revision == "rev0065":
        return rev0065_entries()
    if revision == "rev0064":
        return rev0064_entries()
    if revision == "rev0063":
        return rev0063_entries()
    if revision == "rev0062":
        return rev0062_entries()
    if revision == "rev0061":
        return rev0061_entries()
    if revision == "rev0060":
        return rev0060_entries()
    if revision == "rev0059":
        return rev0059_entries()
    if revision == "rev0058":
        return rev0058_entries()
    return _prior_entries_for_revision_rev0059_settlement(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0076_entries()


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0076_entries()

# rev0077 summary ACK ledger / delivery archive / prune fence surface-ledger override.
def rev0077_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0076_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/summaryackledger.py", "tests/test_rev0077_summaryackledger_deliveryarchive_prunefence.py", "docs/809-summary-ack-ledger-after-settlement-fence.md", "ACK settlement ledger after settlement fence"),
        SurfaceLedgerEntry("src/i2p_dht_lab/deliveryarchive.py", "tests/test_rev0077_summaryackledger_deliveryarchive_prunefence.py", "docs/810-delivery-archive-restart-memory.md", "restart-sticky delivery archive after ACK settlement"),
        SurfaceLedgerEntry("src/i2p_dht_lab/summaryprunefence.py", "tests/test_rev0077_summaryackledger_deliveryarchive_prunefence.py", "docs/811-summary-prune-fence.md", "soft prune fence preserving ACK/archive/redaction/contradiction memory"),
        SurfaceLedgerEntry("src/i2p_dht_lab/summaryackfold.py", "tests/test_rev0077_summaryackledger_deliveryarchive_prunefence.py", "docs/812-summaryackfold-audit-refactor.md", "rev0077 summaryackfold preserving rev0076 summarydeliveryfold predecessor history"),
    )


def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0077":
        return rev0077_entries()
    if revision == "rev0076":
        return rev0076_entries()
    if revision == "rev0075":
        return rev0075_entries()
    if revision == "rev0074":
        return rev0074_entries()
    if revision == "rev0073":
        return rev0073_entries()
    if revision == "rev0072":
        return rev0072_entries()
    if revision == "rev0071":
        return rev0071_entries()
    if revision == "rev0070":
        return rev0070_entries()
    if revision == "rev0069":
        return rev0069_entries()
    if revision == "rev0068":
        return rev0068_entries()
    if revision == "rev0067":
        return rev0067_entries()
    if revision == "rev0066":
        return rev0066_entries()
    if revision == "rev0065":
        return rev0065_entries()
    if revision == "rev0064":
        return rev0064_entries()
    if revision == "rev0063":
        return rev0063_entries()
    if revision == "rev0062":
        return rev0062_entries()
    if revision == "rev0061":
        return rev0061_entries()
    if revision == "rev0060":
        return rev0060_entries()
    if revision == "rev0059":
        return rev0059_entries()
    if revision == "rev0058":
        return rev0058_entries()
    return _prior_entries_for_revision_rev0059_settlement(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0077_entries()


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0077_entries()

# rev0078 summary replay / ACK closure / export fence surface-ledger override.
def rev0078_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0077_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/summaryreplay.py", "tests/test_rev0078_summaryreplay_ackclosure_exportfence.py", "docs/819-summary-replay-after-prune-fence.md", "restart replay after summary ACK/archive/prune fence"),
        SurfaceLedgerEntry("src/i2p_dht_lab/ackclosure.py", "tests/test_rev0078_summaryreplay_ackclosure_exportfence.py", "docs/820-ack-closure-after-restart-replay.md", "ACK closure after replay-safe summary delivery memory"),
        SurfaceLedgerEntry("src/i2p_dht_lab/summaryexportfence.py", "tests/test_rev0078_summaryreplay_ackclosure_exportfence.py", "docs/821-summary-export-fence.md", "no-network redacted summary export fence"),
        SurfaceLedgerEntry("src/i2p_dht_lab/summaryreplayfold.py", "tests/test_rev0078_summaryreplay_ackclosure_exportfence.py", "docs/822-summaryreplayfold-audit-refactor.md", "rev0078 summaryreplayfold preserving rev0077 summaryackfold predecessor history"),
    )


def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0078":
        return rev0078_entries()
    if revision == "rev0077":
        return rev0077_entries()
    if revision == "rev0076":
        return rev0076_entries()
    if revision == "rev0075":
        return rev0075_entries()
    if revision == "rev0074":
        return rev0074_entries()
    if revision == "rev0073":
        return rev0073_entries()
    if revision == "rev0072":
        return rev0072_entries()
    if revision == "rev0071":
        return rev0071_entries()
    if revision == "rev0070":
        return rev0070_entries()
    if revision == "rev0069":
        return rev0069_entries()
    if revision == "rev0068":
        return rev0068_entries()
    if revision == "rev0067":
        return rev0067_entries()
    if revision == "rev0066":
        return rev0066_entries()
    if revision == "rev0065":
        return rev0065_entries()
    if revision == "rev0064":
        return rev0064_entries()
    if revision == "rev0063":
        return rev0063_entries()
    if revision == "rev0062":
        return rev0062_entries()
    if revision == "rev0061":
        return rev0061_entries()
    if revision == "rev0060":
        return rev0060_entries()
    if revision == "rev0059":
        return rev0059_entries()
    if revision == "rev0058":
        return rev0058_entries()
    return _prior_entries_for_revision_rev0059_settlement(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0078_entries()


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0078_entries()

# rev0079 summary export receipt / import gate / retention audit surface-ledger override.
def rev0079_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0078_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/summaryexportreceipt.py", "tests/test_rev0079_summaryexportreceipt_importgate_retentionaudit.py", "docs/829-summary-export-receipt-after-export-fence.md", "recipient receipt after redacted summary export fence"),
        SurfaceLedgerEntry("src/i2p_dht_lab/summaryimportgate.py", "tests/test_rev0079_summaryexportreceipt_importgate_retentionaudit.py", "docs/830-summary-import-gate-after-receipt.md", "import gate after recipient receipt"),
        SurfaceLedgerEntry("src/i2p_dht_lab/exportretentionaudit.py", "tests/test_rev0079_summaryexportreceipt_importgate_retentionaudit.py", "docs/831-export-retention-audit.md", "retention audit preserving redaction and contradiction memory"),
        SurfaceLedgerEntry("src/i2p_dht_lab/summaryexportreceiptfold.py", "tests/test_rev0079_summaryexportreceipt_importgate_retentionaudit.py", "docs/832-summaryexportreceiptfold-audit-refactor.md", "rev0079 summaryexportreceiptfold preserving rev0078 summaryreplayfold predecessor history"),
    )


def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0079":
        return rev0079_entries()
    if revision == "rev0078":
        return rev0078_entries()
    if revision == "rev0077":
        return rev0077_entries()
    if revision == "rev0076":
        return rev0076_entries()
    if revision == "rev0075":
        return rev0075_entries()
    if revision == "rev0074":
        return rev0074_entries()
    if revision == "rev0073":
        return rev0073_entries()
    if revision == "rev0072":
        return rev0072_entries()
    if revision == "rev0071":
        return rev0071_entries()
    if revision == "rev0070":
        return rev0070_entries()
    if revision == "rev0069":
        return rev0069_entries()
    if revision == "rev0068":
        return rev0068_entries()
    if revision == "rev0067":
        return rev0067_entries()
    if revision == "rev0066":
        return rev0066_entries()
    if revision == "rev0065":
        return rev0065_entries()
    if revision == "rev0064":
        return rev0064_entries()
    if revision == "rev0063":
        return rev0063_entries()
    if revision == "rev0062":
        return rev0062_entries()
    if revision == "rev0061":
        return rev0061_entries()
    if revision == "rev0060":
        return rev0060_entries()
    if revision == "rev0059":
        return rev0059_entries()
    if revision == "rev0058":
        return rev0058_entries()
    return _prior_entries_for_revision_rev0059_settlement(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0079_entries()


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0079_entries()

# rev0080 import settlement / archive / retention seal surface-ledger override.
def rev0080_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0079_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/summaryimportsettlement.py", "tests/test_rev0080_importsettlement_archive_retentionseal.py", "docs/839-summary-import-settlement-after-gate.md", "summary import settlement after gate/receipt/retention agreement"),
        SurfaceLedgerEntry("src/i2p_dht_lab/importarchiveledger.py", "tests/test_rev0080_importsettlement_archive_retentionseal.py", "docs/840-import-archive-ledger.md", "restart-sticky import archive ledger"),
        SurfaceLedgerEntry("src/i2p_dht_lab/importretentionseal.py", "tests/test_rev0080_importsettlement_archive_retentionseal.py", "docs/841-import-retention-seal.md", "import retention seal preserving redaction and contradiction memory"),
        SurfaceLedgerEntry("src/i2p_dht_lab/importsettlementfold.py", "tests/test_rev0080_importsettlement_archive_retentionseal.py", "docs/842-importsettlementfold-audit-refactor.md", "rev0080 importsettlementfold preserving rev0079 predecessor history"),
    )


def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0080":
        return rev0080_entries()
    if revision == "rev0079":
        return rev0079_entries()
    if revision == "rev0078":
        return rev0078_entries()
    if revision == "rev0077":
        return rev0077_entries()
    if revision == "rev0076":
        return rev0076_entries()
    if revision == "rev0075":
        return rev0075_entries()
    if revision == "rev0074":
        return rev0074_entries()
    if revision == "rev0073":
        return rev0073_entries()
    if revision == "rev0072":
        return rev0072_entries()
    if revision == "rev0071":
        return rev0071_entries()
    if revision == "rev0070":
        return rev0070_entries()
    if revision == "rev0069":
        return rev0069_entries()
    if revision == "rev0068":
        return rev0068_entries()
    if revision == "rev0067":
        return rev0067_entries()
    if revision == "rev0066":
        return rev0066_entries()
    if revision == "rev0065":
        return rev0065_entries()
    if revision == "rev0064":
        return rev0064_entries()
    if revision == "rev0063":
        return rev0063_entries()
    if revision == "rev0062":
        return rev0062_entries()
    if revision == "rev0061":
        return rev0061_entries()
    if revision == "rev0060":
        return rev0060_entries()
    if revision == "rev0059":
        return rev0059_entries()
    if revision == "rev0058":
        return rev0058_entries()
    return _prior_entries_for_revision_rev0059_settlement(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0080_entries()


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0080_entries()

# rev0081 Python-first / GCC leaf-kernel surface-ledger override.
def rev0081_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0080_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/nativeboundary.py", "tests/test_rev0081_nativeboundary_gccffi_hotpath.py", "docs/849-python-first-native-leaf-boundary.md", "Python-first semantics with narrow GCC-native leaf-kernel allowance"),
        SurfaceLedgerEntry("src/i2p_dht_lab/gccffi.py", "tests/test_rev0081_nativeboundary_gccffi_hotpath.py", "docs/850-gcc-ffi-contract.md", "GCC/FFI contract guard: no heap ownership, stable ABI, Python fallback"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativehotpaths.py", "tests/test_rev0081_nativeboundary_gccffi_hotpath.py", "docs/851-native-hotpath-xor-kernel.md", "portable Python reference for optional native hotpaths"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativeboundaryfold.py", "tests/test_rev0081_nativeboundary_gccffi_hotpath.py", "docs/852-nativeboundaryfold-audit-refactor.md", "rev0081 nativeboundaryfold preserving rev0080 predecessor history"),
    )


def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0081":
        return rev0081_entries()
    if revision == "rev0080":
        return rev0080_entries()
    if revision == "rev0079":
        return rev0079_entries()
    if revision == "rev0078":
        return rev0078_entries()
    if revision == "rev0077":
        return rev0077_entries()
    if revision == "rev0076":
        return rev0076_entries()
    if revision == "rev0075":
        return rev0075_entries()
    if revision == "rev0074":
        return rev0074_entries()
    if revision == "rev0073":
        return rev0073_entries()
    if revision == "rev0072":
        return rev0072_entries()
    if revision == "rev0071":
        return rev0071_entries()
    if revision == "rev0070":
        return rev0070_entries()
    if revision == "rev0069":
        return rev0069_entries()
    if revision == "rev0068":
        return rev0068_entries()
    if revision == "rev0067":
        return rev0067_entries()
    if revision == "rev0066":
        return rev0066_entries()
    if revision == "rev0065":
        return rev0065_entries()
    if revision == "rev0064":
        return rev0064_entries()
    if revision == "rev0063":
        return rev0063_entries()
    if revision == "rev0062":
        return rev0062_entries()
    if revision == "rev0061":
        return rev0061_entries()
    if revision == "rev0060":
        return rev0060_entries()
    if revision == "rev0059":
        return rev0059_entries()
    if revision == "rev0058":
        return rev0058_entries()
    return _prior_entries_for_revision_rev0059_settlement(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0081_entries()


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0081_entries()

# rev0082 native parity / ABI guard / fallback seal surface-ledger override.
def rev0082_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0081_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/nativeparity.py", "tests/test_rev0082_nativeparity_abiguard_fallbackseal.py", "docs/859-native-parity-before-selection.md", "native/Python differential parity before optional native selection"),
        SurfaceLedgerEntry("src/i2p_dht_lab/abiguard.py", "tests/test_rev0082_nativeparity_abiguard_fallbackseal.py", "docs/860-abi-guard-load-boundary.md", "native artifact ABI guard: symbols, version, source/object/flags digest, input limit"),
        SurfaceLedgerEntry("src/i2p_dht_lab/fallbackseal.py", "tests/test_rev0082_nativeparity_abiguard_fallbackseal.py", "docs/861-fallback-seal-native-quarantine.md", "fallback seal routes missing/quarantined native artifacts to Python reference"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativeparityfold.py", "tests/test_rev0082_nativeparity_abiguard_fallbackseal.py", "docs/862-nativeparityfold-audit-refactor.md", "rev0082 nativeparityfold preserving rev0081 predecessor history"),
    )


def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0082":
        return rev0082_entries()
    if revision == "rev0081":
        return rev0081_entries()
    if revision == "rev0080":
        return rev0080_entries()
    if revision == "rev0079":
        return rev0079_entries()
    if revision == "rev0078":
        return rev0078_entries()
    if revision == "rev0077":
        return rev0077_entries()
    if revision == "rev0076":
        return rev0076_entries()
    if revision == "rev0075":
        return rev0075_entries()
    if revision == "rev0074":
        return rev0074_entries()
    if revision == "rev0073":
        return rev0073_entries()
    if revision == "rev0072":
        return rev0072_entries()
    if revision == "rev0071":
        return rev0071_entries()
    if revision == "rev0070":
        return rev0070_entries()
    if revision == "rev0069":
        return rev0069_entries()
    if revision == "rev0068":
        return rev0068_entries()
    if revision == "rev0067":
        return rev0067_entries()
    if revision == "rev0066":
        return rev0066_entries()
    if revision == "rev0065":
        return rev0065_entries()
    if revision == "rev0064":
        return rev0064_entries()
    if revision == "rev0063":
        return rev0063_entries()
    if revision == "rev0062":
        return rev0062_entries()
    if revision == "rev0061":
        return rev0061_entries()
    if revision == "rev0060":
        return rev0060_entries()
    if revision == "rev0059":
        return rev0059_entries()
    if revision == "rev0058":
        return rev0058_entries()
    return _prior_entries_for_revision_rev0059_settlement(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0082_entries()


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0082_entries()

# rev0083 native runtime / dispatch seal / source audit surface-ledger override.
def rev0083_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0082_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/nativeruntime.py", "tests/test_rev0083_nativeruntime_dispatchaudit_fallbackbudget.py", "docs/869-native-runtime-drift-guard.md", "runtime drift guard after parity/ABI/fallback seal"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativedispatch.py", "tests/test_rev0083_nativeruntime_dispatchaudit_fallbackbudget.py", "docs/870-native-dispatch-seal.md", "exact-boundary dispatch seal for optional native XOR calls"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativeaudit.py", "tests/test_rev0083_nativeruntime_dispatchaudit_fallbackbudget.py", "docs/871-native-source-audit.md", "textual source audit for tiny GCC leaf sources"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativedispatchfold.py", "tests/test_rev0083_nativeruntime_dispatchaudit_fallbackbudget.py", "docs/872-nativedispatchfold-audit-refactor.md", "rev0083 nativedispatchfold preserving rev0082 predecessor history"),
    )


def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0083":
        return rev0083_entries()
    if revision == "rev0082":
        return rev0082_entries()
    if revision == "rev0081":
        return rev0081_entries()
    if revision == "rev0080":
        return rev0080_entries()
    if revision == "rev0079":
        return rev0079_entries()
    if revision == "rev0078":
        return rev0078_entries()
    if revision == "rev0077":
        return rev0077_entries()
    if revision == "rev0076":
        return rev0076_entries()
    if revision == "rev0075":
        return rev0075_entries()
    if revision == "rev0074":
        return rev0074_entries()
    if revision == "rev0073":
        return rev0073_entries()
    if revision == "rev0072":
        return rev0072_entries()
    if revision == "rev0071":
        return rev0071_entries()
    if revision == "rev0070":
        return rev0070_entries()
    if revision == "rev0069":
        return rev0069_entries()
    if revision == "rev0068":
        return rev0068_entries()
    if revision == "rev0067":
        return rev0067_entries()
    if revision == "rev0066":
        return rev0066_entries()
    if revision == "rev0065":
        return rev0065_entries()
    if revision == "rev0064":
        return rev0064_entries()
    if revision == "rev0063":
        return rev0063_entries()
    if revision == "rev0062":
        return rev0062_entries()
    if revision == "rev0061":
        return rev0061_entries()
    if revision == "rev0060":
        return rev0060_entries()
    if revision == "rev0059":
        return rev0059_entries()
    if revision == "rev0058":
        return rev0058_entries()
    return _prior_entries_for_revision_rev0059_settlement(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0083_entries()


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0083_entries()

# rev0084 parser hold / sanitizer plan / native budget surface-ledger override.
def rev0084_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0083_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/parserhold.py", "tests/test_rev0084_parserhold_sanitizer_nativebudget.py", "docs/879-parser-hold-python-owned.md", "parser hold keeps hostile-byte parsing Python-owned"),
        SurfaceLedgerEntry("src/i2p_dht_lab/sanitizerplan.py", "tests/test_rev0084_parserhold_sanitizer_nativebudget.py", "docs/880-sanitizer-plan-before-native-expansion.md", "sanitizer/fuzz posture before native expansion"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativebudget.py", "tests/test_rev0084_parserhold_sanitizer_nativebudget.py", "docs/881-native-optimization-budget.md", "native optimization budget for leaf kernels and fallbacks"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativebudgetfold.py", "tests/test_rev0084_parserhold_sanitizer_nativebudget.py", "docs/882-nativebudgetfold-audit-refactor.md", "rev0084 nativebudgetfold preserving rev0083 predecessor history"),
    )


_prior_entries_for_revision_rev0084_nativebudget = entries_for_revision

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0084":
        return rev0084_entries()
    return _prior_entries_for_revision_rev0084_nativebudget(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0084_entries()


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0084_entries()

# rev0085 native provenance / corpus / quarantine surface-ledger override.
def rev0085_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0084_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/nativeprovenance.py", "tests/test_rev0085_nativeprovenance_corpus_quarantine.py", "docs/889-native-build-provenance.md", "native build provenance before artifact selection"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativecorpus.py", "tests/test_rev0085_nativeprovenance_corpus_quarantine.py", "docs/890-differential-native-corpus.md", "differential native corpus against Python oracle"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativequarantine.py", "tests/test_rev0085_nativeprovenance_corpus_quarantine.py", "docs/891-native-quarantine-store.md", "sticky native quarantine memory and fallback routing"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativeprovenancefold.py", "tests/test_rev0085_nativeprovenance_corpus_quarantine.py", "docs/892-nativeprovenancefold-audit-refactor.md", "rev0085 nativeprovenancefold preserving rev0084 predecessor history"),
    )


_prior_entries_for_revision_rev0085_nativeprovenance = entries_for_revision

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0085":
        return rev0085_entries()
    return _prior_entries_for_revision_rev0085_nativeprovenance(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0085_entries()


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0085_entries()

# rev0086 native selection / fallback journal / promotion hold surface-ledger override.
def rev0086_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0085_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/nativeselection.py", "tests/test_rev0086_nativeselection_fallbackjournal_promotehold.py", "docs/899-native-selection-exact-boundary.md", "native selection gate after provenance/corpus/quarantine"),
        SurfaceLedgerEntry("src/i2p_dht_lab/fallbackjournal.py", "tests/test_rev0086_nativeselection_fallbackjournal_promotehold.py", "docs/900-fallback-journal-restart-memory.md", "fallback journal restart memory for native selection"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativepromotion.py", "tests/test_rev0086_nativeselection_fallbackjournal_promotehold.py", "docs/901-native-promotion-hold.md", "native promotion hold preserving quarantine/fallback memory"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativeselectionfold.py", "tests/test_rev0086_nativeselection_fallbackjournal_promotehold.py", "docs/902-nativeselectionfold-audit-refactor.md", "rev0086 nativeselectionfold preserving rev0085 predecessor history"),
    )


_prior_entries_for_revision_rev0086_nativeselection = entries_for_revision

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0086":
        return rev0086_entries()
    return _prior_entries_for_revision_rev0086_nativeselection(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0086_entries()


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0086_entries()

# rev0087 native load / crash ledger / performance guard surface-ledger override.
def rev0087_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0086_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/nativeload.py", "tests/test_rev0087_nativeload_crashledger_perfguard.py", "docs/909-native-load-lifecycle-boundary.md", "native load lifecycle gate after selection/promotion"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativecrashledger.py", "tests/test_rev0087_nativeload_crashledger_perfguard.py", "docs/910-native-crash-ledger.md", "sticky native crash/fault memory and fallback pressure"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativeperfguard.py", "tests/test_rev0087_nativeload_crashledger_perfguard.py", "docs/911-native-performance-guard.md", "performance guard is operator hint, not selection authority"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativelifecyclefold.py", "tests/test_rev0087_nativeload_crashledger_perfguard.py", "docs/912-nativelifecyclefold-audit-refactor.md", "rev0087 nativelifecyclefold preserving rev0086 predecessor history"),
    )


_prior_entries_for_revision_rev0087_nativelifecycle = entries_for_revision

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0087":
        return rev0087_entries()
    return _prior_entries_for_revision_rev0087_nativelifecycle(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0087_entries()


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0087_entries()

# rev0088 native unload / sandbox-stub / crash-GC surface-ledger override.
def rev0088_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0087_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/nativeunload.py", "tests/test_rev0088_nativeunload_sandboxstub_crashgc.py", "docs/919-native-unload-quarantine-boundary.md", "native unload/quarantine after load and crash pressure"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativesandboxstub.py", "tests/test_rev0088_nativeunload_sandboxstub_crashgc.py", "docs/920-native-sandbox-stub.md", "native sandbox-stub no-network boundary without production isolation claims"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativecrashgc.py", "tests/test_rev0088_nativeunload_sandboxstub_crashgc.py", "docs/921-native-crash-gc.md", "native crash-ledger GC preserving hard faults"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativecontrolfold.py", "tests/test_rev0088_nativeunload_sandboxstub_crashgc.py", "docs/922-nativecontrolfold-audit-refactor.md", "rev0088 nativecontrolfold preserving rev0087 predecessor history"),
    )


_prior_entries_for_revision_rev0088_nativecontrol = entries_for_revision

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0088":
        return rev0088_entries()
    return _prior_entries_for_revision_rev0088_nativecontrol(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0088_entries()


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0088_entries()

# rev0089 native cold-start / probe corpus / loader-GC surface-ledger override.
def rev0089_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0088_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/nativecoldstart.py", "tests/test_rev0089_nativecoldstart_probecorpus_loadergc.py", "docs/929-native-cold-start-after-unload.md", "native cold-start after unload/sandbox/crash-GC without dynamic load"),
        SurfaceLedgerEntry("src/i2p_dht_lab/probecorpus.py", "tests/test_rev0089_nativecoldstart_probecorpus_loadergc.py", "docs/930-probe-corpus-refresh.md", "probe corpus refresh against Python oracle before native reconsideration"),
        SurfaceLedgerEntry("src/i2p_dht_lab/loadergc.py", "tests/test_rev0089_nativecoldstart_probecorpus_loadergc.py", "docs/931-loader-gc-after-cold-start.md", "loader-GC preserving tombstones/fallback/quarantine memory"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativecoldfold.py", "tests/test_rev0089_nativecoldstart_probecorpus_loadergc.py", "docs/932-nativecoldfold-audit-refactor.md", "rev0089 nativecoldfold preserving rev0088 predecessor history"),
    )


_prior_entries_for_revision_rev0089_nativecold = entries_for_revision

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0089":
        return rev0089_entries()
    return _prior_entries_for_revision_rev0089_nativecold(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0089_entries()


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0089_entries()

# rev0090 native handoff / relaunch gate / loader seal surface-ledger override.
def rev0090_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0089_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/nativehandoff.py", "tests/test_rev0090_nativehandoff_relaunchgate_loaderseal.py", "docs/939-native-handoff-relaunch-candidate.md", "native handoff to fallback-active relaunch candidate only"),
        SurfaceLedgerEntry("src/i2p_dht_lab/relaunchgate.py", "tests/test_rev0090_nativehandoff_relaunchgate_loaderseal.py", "docs/940-relaunch-gate-prior-lanes.md", "relaunch gate requiring prior native lane revalidation"),
        SurfaceLedgerEntry("src/i2p_dht_lab/loaderseal.py", "tests/test_rev0090_nativehandoff_relaunchgate_loaderseal.py", "docs/941-loader-seal-restart-memory.md", "loader seal preserving tombstone/fallback/quarantine/crash memory"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativefoldspine.py", "tests/test_rev0090_nativehandoff_relaunchgate_loaderseal.py", "docs/942-native-fold-spine-audit-refactor.md", "native branch fold-spine audit refactor"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativehandofffold.py", "tests/test_rev0090_nativehandoff_relaunchgate_loaderseal.py", "docs/942-native-fold-spine-audit-refactor.md", "rev0090 nativehandofffold preserving rev0089 predecessor history"),
    )


_prior_entries_for_revision_rev0090_nativehandoff = entries_for_revision

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0090":
        return rev0090_entries()
    return _prior_entries_for_revision_rev0090_nativehandoff(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0090_entries()


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0090_entries()


# rev0091 native oracle seal / preflight / re-entry journal surface-ledger override.
def rev0091_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0090_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/nativeoracleseal.py", "tests/test_rev0091_nativereentry_oracleseal_preflight.py", "docs/949-native-oracle-seal.md", "Python oracle seal before native re-entry"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativepreflight.py", "tests/test_rev0091_nativereentry_oracleseal_preflight.py", "docs/950-native-preflight-route-to-load-gate.md", "route-to-load-gate-only native preflight"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativereentryjournal.py", "tests/test_rev0091_nativereentry_oracleseal_preflight.py", "docs/951-native-reentry-journal.md", "restart-sticky native re-entry journal"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativereentryfold.py", "tests/test_rev0091_nativereentry_oracleseal_preflight.py", "docs/952-nativereentryfold-audit-refactor.md", "rev0091 nativereentryfold preserving rev0090 predecessor history"),
    )

_prior_entries_for_revision_rev0091_nativereentry = entries_for_revision

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0091":
        return rev0091_entries()
    return _prior_entries_for_revision_rev0091_nativereentry(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0091_entries()


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0091_entries()

# rev0092 native load re-entry / revalidation seal / call-hold surface-ledger override.
def rev0092_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0091_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/nativeloadreentry.py", "tests/test_rev0092_nativeloadreentry_revalidationseal_callhold.py", "docs/959-native-load-reentry-request.md", "native load re-entry requests load-gate evaluation only"),
        SurfaceLedgerEntry("src/i2p_dht_lab/revalidationseal.py", "tests/test_rev0092_nativeloadreentry_revalidationseal_callhold.py", "docs/960-revalidation-seal-prior-lanes.md", "prior native lanes are freshness-checked before load-gate re-entry"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativecallhold.py", "tests/test_rev0092_nativeloadreentry_revalidationseal_callhold.py", "docs/961-native-call-hold.md", "native call remains held on Python fallback oracle"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativeloadreentryfold.py", "tests/test_rev0092_nativeloadreentry_revalidationseal_callhold.py", "docs/962-nativeloadreentryfold-audit-refactor.md", "rev0092 nativeloadreentryfold preserving rev0091 predecessor history"),
    )

_prior_entries_for_revision_rev0092_nativeloadreentry = entries_for_revision

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0092":
        return rev0092_entries()
    return _prior_entries_for_revision_rev0092_nativeloadreentry(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0092_entries()


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0092_entries()

# rev0093 native load loop / call canary / dispatch fence surface-ledger override.
def rev0093_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0092_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/nativeloadloop.py", "tests/test_rev0093_nativeloadloop_callcanary_dispatchfence.py", "docs/969-native-load-loopback.md", "native load loopback held on Python fallback"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativecallcanary.py", "tests/test_rev0093_nativeloadloop_callcanary_dispatchfence.py", "docs/970-native-call-canary.md", "native call canary carrying Python result only"),
        SurfaceLedgerEntry("src/i2p_dht_lab/dispatchfence.py", "tests/test_rev0093_nativeloadloop_callcanary_dispatchfence.py", "docs/971-dispatch-fence.md", "native dispatch fence before any native call release"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativeloadloopfold.py", "tests/test_rev0093_nativeloadloop_callcanary_dispatchfence.py", "docs/972-nativeloadloopfold-audit-refactor.md", "rev0093 nativeloadloopfold preserving rev0092 predecessor history"),
    )

_prior_entries_for_revision_rev0093_nativeloadloop = entries_for_revision

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0093":
        return rev0093_entries()
    return _prior_entries_for_revision_rev0093_nativeloadloop(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0093_entries()


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0093_entries()

# rev0094 native shadow-call / result-diff / fault-seal surface-ledger override.
def rev0094_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0093_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/nativeshadowcall.py", "tests/test_rev0094_nativeshadowcall_resultdiff_faultseal.py", "docs/979-native-shadow-call.md", "native shadow-call evidence with Python fallback still authoritative"),
        SurfaceLedgerEntry("src/i2p_dht_lab/resultdiff.py", "tests/test_rev0094_nativeshadowcall_resultdiff_faultseal.py", "docs/980-native-result-diff.md", "native-vs-Python result diff with mismatch fault pressure"),
        SurfaceLedgerEntry("src/i2p_dht_lab/faultseal.py", "tests/test_rev0094_nativeshadowcall_resultdiff_faultseal.py", "docs/981-native-fault-seal.md", "restart-sticky native fault seal denying native authority"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativeshadowfold.py", "tests/test_rev0094_nativeshadowcall_resultdiff_faultseal.py", "docs/982-nativeshadowfold-audit-refactor.md", "rev0094 nativeshadowfold preserving rev0093 predecessor history"),
    )

_prior_entries_for_revision_rev0094_nativeshadow = entries_for_revision

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0094":
        return rev0094_entries()
    return _prior_entries_for_revision_rev0094_nativeshadow(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0094_entries()


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0094_entries()

# rev0095 native shadow-settlement / admission / call ledger surface-ledger override.
def rev0095_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0094_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/nativeshadowsettlement.py", "tests/test_rev0095_shadowsettlement_admission_callledger.py", "docs/989-native-shadow-settlement.md", "settle matching native shadow output as evidence only"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativeadmission.py", "tests/test_rev0095_shadowsettlement_admission_callledger.py", "docs/990-native-admission-held.md", "admit only held shadow slots without native call permission"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativecallledger.py", "tests/test_rev0095_shadowsettlement_admission_callledger.py", "docs/991-native-call-ledger.md", "restart-sticky ledger preserving Python route"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativesettlementfold.py", "tests/test_rev0095_shadowsettlement_admission_callledger.py", "docs/992-nativesettlementfold-audit-refactor.md", "rev0095 nativesettlementfold preserving rev0094 predecessor history"),
    )

_prior_entries_for_revision_rev0095_nativesettlement = entries_for_revision

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0095":
        return rev0095_entries()
    return _prior_entries_for_revision_rev0095_nativesettlement(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0095_entries()


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0095_entries()

# rev0096 native call-archive / promotion-denial / shadow-GC surface-ledger override.
def rev0096_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0095_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/nativecallarchive.py", "tests/test_rev0096_callarchive_promotedeny_shadowgc.py", "docs/999-native-call-archive.md", "archive Python-route call ledger after matching native shadow settlement"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativepromotiondeny.py", "tests/test_rev0096_callarchive_promotedeny_shadowgc.py", "docs/1000-native-promotion-denial.md", "deny promotion even after repeated matching shadow results"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativeshadowgc.py", "tests/test_rev0096_callarchive_promotedeny_shadowgc.py", "docs/1001-native-shadow-gc.md", "compact soft shadow evidence while preserving denial/fallback hard memory"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativearchivefold.py", "tests/test_rev0096_callarchive_promotedeny_shadowgc.py", "docs/1002-nativearchivefold-audit-refactor.md", "rev0096 nativearchivefold preserving rev0095 predecessor history"),
    )

_prior_entries_for_revision_rev0096_nativearchive = entries_for_revision

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0096":
        return rev0096_entries()
    return _prior_entries_for_revision_rev0096_nativearchive(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0096_entries()


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0096_entries()

# rev0097 native archive-replay / promotion-review / spine compact surface-ledger override.
def rev0097_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0096_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/nativearchivereplay.py", "tests/test_rev0097_nativearchivereplay_promotereview_spinecompact.py", "docs/1009-native-archive-replay.md", "replay rev0096 archive memory after restart without native permission"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativepromotereview.py", "tests/test_rev0097_nativearchivereplay_promotereview_spinecompact.py", "docs/1010-native-promotion-review-held.md", "hold human/operator review while Python fallback remains authoritative"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativearchivereplayfold.py", "tests/test_rev0097_nativearchivereplay_promotereview_spinecompact.py", "docs/1012-nativearchivereplayfold-audit-refactor.md", "rev0097 native archive replay fold preserving rev0096 predecessor history"),
    )

_prior_entries_for_revision_rev0097_nativearchivereplay = entries_for_revision

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0097":
        return rev0097_entries()
    return _prior_entries_for_revision_rev0097_nativearchivereplay(revision)


def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0097_entries()


def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0097_entries()

# rev0098 native branch-close / promotion archive / policy surface-ledger override.
def rev0098_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0097_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/nativepromotearchive.py", "tests/test_rev0098_nativebranchclose_promotearchive_policy.py", "docs/1019-native-promotion-archive.md", "archive held promotion review as non-permission restart memory"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativepromotionpolicy.py", "tests/test_rev0098_nativebranchclose_promotearchive_policy.py", "docs/1020-native-promotion-policy-shadow-only.md", "enforce shadow-only native policy and deny forbidden semantic surfaces"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativebranchclose.py", "tests/test_rev0098_nativebranchclose_promotearchive_policy.py", "docs/1021-native-branch-close.md", "close native branch shadow-only while Python fallback remains authoritative"),
        SurfaceLedgerEntry("src/i2p_dht_lab/nativebranchclosefold.py", "tests/test_rev0098_nativebranchclose_promotearchive_policy.py", "docs/1022-nativebranchclosefold-audit-refactor.md", "rev0098 branch close fold preserving rev0097 predecessor history"),
    )

_prior_entries_for_revision_rev0098_nativebranchclose = entries_for_revision

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0098":
        return rev0098_entries()
    return _prior_entries_for_revision_rev0098_nativebranchclose(revision)

def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0098_entries()

def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0098_entries()

def rev0099_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0098_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/recordplaneoracle.py", "tests/test_rev0099_substratereturn_recordoracle_spineaudit.py", "docs/1029-record-plane-oracle-after-native-close.md", "Python-owned record-plane oracle after closing native branch"),
        SurfaceLedgerEntry("src/i2p_dht_lab/substratereentry.py", "tests/test_rev0099_substratereturn_recordoracle_spineaudit.py", "docs/1030-substrate-reentry-after-native-close.md", "return to generic DHT substrate only after native close and record oracle agree"),
        SurfaceLedgerEntry("src/i2p_dht_lab/substratereturnfold.py", "tests/test_rev0099_substratereturn_recordoracle_spineaudit.py", "docs/1031-substratereturnfold-audit-refactor.md", "rev0099 substrate-return fold preserving rev0098 native branch-close predecessor"),
    )

_prior_entries_for_revision_rev0099_substratereturn = entries_for_revision

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0099":
        return rev0099_entries()
    return _prior_entries_for_revision_rev0099_substratereturn(revision)

def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0099_entries()

def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0099_entries()

# rev0100 substrate record ingress / provider semantics / routing anchor surface-ledger override.
def rev0100_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0099_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/recordingress.py", "tests/test_rev0100_recordingress_providersemantics_routingspine.py", "docs/1039-record-ingress-after-substrate-return.md", "Python-owned record ingress after substrate return"),
        SurfaceLedgerEntry("src/i2p_dht_lab/providersemantics.py", "tests/test_rev0100_recordingress_providersemantics_routingspine.py", "docs/1040-provider-semantics-after-record-ingress.md", "provider semantic proof join after provider record ingress"),
        SurfaceLedgerEntry("src/i2p_dht_lab/routinganchor.py", "tests/test_rev0100_recordingress_providersemantics_routingspine.py", "docs/1041-routing-anchor-after-record-ingress.md", "I2P routing anchor for contact records"),
        SurfaceLedgerEntry("src/i2p_dht_lab/substratespine.py", "tests/test_rev0100_recordingress_providersemantics_routingspine.py", "docs/1042-substrate-spine-century-audit.md", "substrate spine after native branch return"),
        SurfaceLedgerEntry("src/i2p_dht_lab/substratecenturyfold.py", "tests/test_rev0100_recordingress_providersemantics_routingspine.py", "docs/1042-substrate-spine-century-audit.md", "rev0100 substrate-century fold preserving rev0099 predecessor history"),
    )

_prior_entries_for_revision_rev0100_substratecentury = entries_for_revision

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0100":
        return rev0100_entries()
    return _prior_entries_for_revision_rev0100_substratecentury(revision)

def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0100_entries()

def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0100_entries()

# rev0101 mutable placement / provider bucket / route storage surface-ledger override.
def rev0101_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0100_entries() + (
        SurfaceLedgerEntry("src/i2p_dht_lab/mutableplacement.py", "tests/test_rev0101_mutableplace_providerbucket_routestorage.py", "docs/1049-mutable-placement-after-record-ingress.md", "mutable-head placement after Python-owned record ingress"),
        SurfaceLedgerEntry("src/i2p_dht_lab/providerbucket.py", "tests/test_rev0101_mutableplace_providerbucket_routestorage.py", "docs/1050-provider-bucket-after-provider-semantics.md", "provider-index bucket admission after semantic proof"),
        SurfaceLedgerEntry("src/i2p_dht_lab/routestorage.py", "tests/test_rev0101_mutableplace_providerbucket_routestorage.py", "docs/1051-route-storage-after-routing-anchor.md", "routing-table storage after I2P route anchor"),
        SurfaceLedgerEntry("src/i2p_dht_lab/substrateplacementfold.py", "tests/test_rev0101_mutableplace_providerbucket_routestorage.py", "docs/1052-substrate-placementfold-audit.md", "rev0101 substrate-placement fold preserving rev0100 predecessor history"),
    )

_prior_entries_for_revision_rev0101_substrateplacement = entries_for_revision

def entries_for_revision(revision: str) -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    if revision == "rev0101":
        return rev0101_entries()
    return _prior_entries_for_revision_rev0101_substrateplacement(revision)

def current_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0101_entries()

def active_entries() -> tuple[SurfaceLedgerEntry, ...]:  # type: ignore[override]
    return rev0101_entries()
