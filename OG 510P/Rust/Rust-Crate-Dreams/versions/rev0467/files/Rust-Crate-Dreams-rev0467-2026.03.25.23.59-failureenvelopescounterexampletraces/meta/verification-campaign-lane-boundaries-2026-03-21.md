# verification-campaign lane boundaries — 2026-03-21

This note keeps **P-0485 Verification Campaign Workbench Kit** from collapsing into adjacent lanes.

## What this lane is for

This lane is for a **reviewable verification campaign contract** over one bundle of obligations, imported tool lanes, trust assumptions, policy, and drift analysis.
It should answer:

- what obligations existed,
- what each lane actually meant,
- what trust surface existed,
- why policy said green/yellow/red,
- and whether two campaigns are comparable.

## Keep this distinct from nearby lanes

### Distinct from raw Miri / Kani / Creusot / Prusti / Flux / Verus work

Those are tool lanes.
`P-0485` is the support contract above them.

### Distinct from `P-0256 Evidence Bundle Core Kit`

`P-0256` is the generic bundle substrate.
`P-0485` is the verification-specific vocabulary above that substrate.

### Distinct from `P-0503 Assurance Case Workbench Kit`

`P-0503` is the higher-layer claim / evidence / review-import lane.
`P-0485` is the lower-layer campaign bundle that assurance tooling may later consume.

### Distinct from `P-0197 Safety Contract Consumer Kit`

`P-0197` is the contract export / consumer lane for specifications and safety interfaces.
`P-0485` is the campaign-evidence and policy-evaluation lane.

### Distinct from sanitizer or UB-specific evidence lanes

BorrowSanitizer, Miri-only, projection-semantics, or sanitizer evidence kits stay tool- or phenomenon-specific.
`P-0485` is the cross-tool campaign layer.

## Five truths this lane must keep separate

1. **obligation inventory** — what needed to be checked and what evidence classes count;
2. **lane semantics** — what each imported lane actually means;
3. **trust ledger** — what trusted items, assumptions, stubs, or waivers exist;
4. **policy evaluation** — why the campaign verdict was green, yellow, or red;
5. **comparability / drift** — whether a comparison is full, partial, or not comparable.

## Ordinary mistakes future passes must resist

Do not let the archive treat any of the following as interchangeable:

- a passing Miri run and a proof,
- a Kani contract stub and zero trust cost,
- a Creusot replay and a fully comparable campaign,
- a Prusti trusted function and an invisible local implementation detail,
- a Flux refinement result and whole-crate proof closure,
- or a Verus proof result and an assurance-case verdict.

## Preferred artifact vocabulary

- `campaign-manifest`
- `obligation-record`
- `lane-result`
- `trust-ledger`
- `policy-evaluation.report`
- `campaign-diff.report`
- `verify-campaign`

If a future pass adds more detail, extend one of those objects before inventing a vague new umbrella.
