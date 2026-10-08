# Exposure Refactor Report

rev0188 audits the cube's overloaded risk-transfer layer and normalizes it into the exposure/liability lifecycle.

## Audit target

The target cluster covered dossiers that were using any of the following as near-synonyms:

- insurance evidence;
- underwriting input;
- liability surface;
- warranty language;
- fault class;
- release evidence;
- reserve / holdback / bond release;
- non-reliance state;
- incident report;
- protection gap;
- market-access risk.

The audit found a recurring problem: the archive was very good at describing proof objects, but less precise about how those objects become money. The missing middle layer was exposure state.

## What was normalized

The refactor tags the relevant existing dossiers with:

- `refactor_cluster: exposure-liability`
- `exposure_role`
- `exposure_stage`
- `state_family: exposure`
- normalized `state_terms`
- `consolidation_status`

The goal is not to collapse every risk-transfer dossier. The goal is to stop promoting new files that merely rename one of the same exposure states.

## Existing dossiers tagged

The audit tagged 32 existing dossiers, including:

- `replay-grade-clearance-logs-become-insurance-evidence`
- `replay-quality-grades-become-underwriting-inputs`
- `extension-frequency-penalties-become-underwriting-inputs`
- `fault-class-scoreboards-become-qualification-filters`
- `source-object-identity-warranties-become-broker-liability-caps`
- `source-snapshot-escrow-becomes-liability-tail-infrastructure`
- `source-drift-warranties-become-contract-language`
- `normalization-loss-warranties-become-diligence-language`
- `readable-structured-divergence-becomes-a-liability-surface`
- `cutover-mismatch-forensics-becomes-a-standing-liability-class`
- `bond-release-evidence-becomes-a-service-tier`
- `supported-version-windows-become-quiet-exclusion-regimes`
- `grandfathering-clauses-become-price-terms`
- `residue-burn-down-covenants-become-contract-language`
- `incident-report-routing-becomes-operational-resilience-infrastructure`
- `custody-break-certificates-become-litigation-and-assurance-artifacts`
- `non-reliance-packet-states-become-version-lifecycle-controls`
- `correction-materiality-thresholds-become-packet-boilerplate`
- `compliance-object-forgery-becomes-organized-fraud-infrastructure`

## New dossiers added because the audit exposed missing states

1. **Coverage-position state labels become operational control planes** — the missing state between incident and payment.
2. **Indemnity pass-through maps become supply-chain risk infrastructure** — the missing chain-of-responsibility object for software, AI, product, and compliance failures.
3. **Subrogation evidence packets become incident-response artifacts** — the missing recovery-rights layer after insurer or guarantor payment.
4. **Reserve-release evidence becomes capital-governance infrastructure** — the missing reserve / holdback / tail-release layer above proof correction.
5. **Self-insured retention thresholds become operational control points** — the missing behavioral threshold where firms manage incidents differently because the first loss layer is their own.

## Consolidation guidance

### Keep as standalone

Keep dossiers standalone when they introduce an enforceable market surface: underwriting, policy wording, indemnity mapping, reserve release, subrogation preservation, or renewal restriction.

### Convert to state-family member

Convert dossiers into lifecycle states when they mainly describe:

- a fault label;
- a notice label;
- a loss-run field;
- a reserve status;
- a coverage caveat;
- a generic proof-quality note.

### Watch for overfit

The archive should avoid turning every contract clause into a dossier. A clause belongs in the cube only if it becomes operational infrastructure: routed, measured, priced, appealed, audited, or embedded in procurement / underwriting workflows.

## Research posture

The refactor is grounded in several live institutional signals:

- The new EU Product Liability Directive expands the product-liability frame to digital products, software, AI systems, updates, and evidence disclosure [S1577].
- SEC cyber-disclosure rules create materiality and timing states for incidents [S1578][S1579].
- Lloyd's cyber-war / state-backed cyber guidance shows how systemic exposure becomes exclusion wording, attribution grammar, and underwriting control [S1580][S1581].
- NAIC and EIOPA materials treat cyber as both an underwriting and resilience problem, not merely an IT problem [S1582][S1584][S1585].
- CIRCIA's proposed reporting grammar turns incident timing, ransom payments, supplemental reports, and similar-reporting exceptions into routed operational states [S1583].

## Next audit target

The next likely refactor target is **market-access capacity and queue state**: notified-body queue position, grid-interconnection position, repair capacity, human-review capacity, cyber-insurance availability, and conformance-lab capacity all look increasingly similar but remain scattered.
