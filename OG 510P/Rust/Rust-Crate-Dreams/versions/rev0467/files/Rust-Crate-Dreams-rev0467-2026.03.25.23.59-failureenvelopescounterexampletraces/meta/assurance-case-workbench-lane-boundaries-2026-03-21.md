# assurance-case-workbench lane boundaries — 2026-03-21

This note keeps **P-0503 Assurance Case Workbench Kit** from collapsing into adjacent lanes.

## What this lane is for

This lane is for a **reviewable assurance-pack contract** over imported Rust-native evidence, explicit claims, assumptions, conservative status, review gates, and standards-shaped exports.
It should answer:

- what claims are being made,
- what evidence currently supports them,
- what assumptions or manual reviews remain,
- why the current review gate is green/yellow/red/blocked,
- and what an export preserves or loses.

## Keep this distinct from nearby lanes

### Distinct from `P-0485 Verification Campaign Workbench Kit`

`P-0485` is the lower-layer campaign contract for obligations, lane semantics, trust ledgers, and policy.
`P-0503` is the higher-layer claim/evidence assembly and review-pack contract that may consume those campaigns.

### Distinct from `P-0256 Evidence Bundle Core Kit`

`P-0256` is the generic portable-bundle substrate.
`P-0503` is the assurance-specific vocabulary above that substrate.

### Distinct from raw GSN / SACM editors or assurance-case authoring suites

Those tools are diagramming or standards-native authoring environments.
`P-0503` is the boring Rust-facing import / status / diff / export contract above today's evidence crates.

### Distinct from `P-0197 Safety Contract Consumer Kit`

Safety-contract consumer work is about contract/spec exports and checks.
`P-0503` is about broader claim/evidence assembly, assumptions, and review packs.

### Distinct from certification workflow ownership

`P-0503` is not a regulator submission platform, hazard-log system, or organizational approval router.
It is the compact review artifact one layer below those workflows.

## Five truths this lane must keep separate

1. **claim-library basis** — what argument/profile basis is in force;
2. **import policy** — what evidence is admissible and under what freshness/trust rules;
3. **assumption ledger** — what unresolved assumptions remain and what they block;
4. **review gate** — why the current pack is green/yellow/red/blocked;
5. **export projection** — what GSN/SACM-shaped exports preserve, omit, or redact.

## Ordinary mistakes future passes must resist

Do not let the archive treat any of the following as interchangeable:

- a verification campaign bundle and an assurance case,
- a green-looking diagram and a green review gate,
- a standards-shaped export and a lossless round trip,
- an imported spec reference and an argument already linked to claims,
- or one unresolved assumption and a harmless footnote.

## Preferred artifact vocabulary

- `assurance-profile`
- `claim-graph`
- `evidence-index`
- `import-policy.receipt`
- `assumption-ledger.report`
- `claim-status.report`
- `review-gate.report`
- `export-projection.receipt`
- `assurance-diff.report`
- `review-pack-manifest`

If a future pass adds more detail, extend one of those objects before inventing a vague new umbrella.
