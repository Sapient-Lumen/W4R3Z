# Lab GIE/BMV protocol-noise-classical split audit

Revision: rev0335  
Bundle: `Theory-of-Everything-rev0335-2026.06.05.10.30-lab-gie-protocol-noise-classical-split-audit.zip`

## Risk targeted

The low-energy lab GIE/BMV route is attractive because it promises public laboratory records rather than purely formal support. That also makes it easy to overcredit. Protocol-relaxation papers, shielding/stability calculations, thermal-noise bounds, and classical/nonlocal comparator debates can be rhetorically compressed into “GIE proves quantum gravity.” This revision prevents that compression.

The route remains current `S2`. It retains only the already declared conditional `S3` pocket for a future direct, clean, public two-body record that survives nuisance, noise, subsystem, and comparator controls. No current source added here is a direct acquired GIE/BMV record.

## Source-role split

`REF-0209` and `REF-0695` through `REF-0698` are route-local pressure only:

- `REF-0209` expands feasible protocol geometry through constrained dynamics, but remains a protocol-realization source.
- `REF-0695` makes shielding, magnetic, and stability budgets explicit public-record denominators.
- `REF-0696` makes thermal-noise thresholds explicit: amplification or mediator tricks cannot erase a separability-preserving noise bound.
- `REF-0697` sharpens locality/collapse-model comparator assumptions for witness interpretation.
- `REF-0698` moves quantum-channel language into an explicit noise and entanglement-breaking threshold rather than direct evidence.

`REF-0695` through `REF-0698` are deliberately **excluded** from `EU-0008-LAB-GIE-MEDIATOR.source_refs`; existing `REF-0209` remains an older feasibility source already carried by the evidence cluster. They are visible in forecast, empirical-delta, decision, carrier, protocol, and control rows where they define future direct-record conditions.

## Ledger changes

New route-facing rows:

- `DF-0023-LAB-GIE-PROTOCOL-NOISE-CLASSICAL-SPLIT`
- `ED-0029-LAB-GIE-PROTOCOL-NOISE-CLASSICAL-SPLIT-PRESSURE`
- `DX-0016-LAB-GIE-PROTOCOL-NOISE-CLASSICAL-SPLIT`

Updated rows include:

- `R-OQ0057-LAB-GIE-BMV`
- `DX-0001-DIRECT-GIE-BMV-ENTANGLEMENT`
- `EU-0008-LAB-GIE-MEDIATOR`
- `PRC-GIE-LAB-CUSTODY`
- `AP-GIE-LAB-CUSTODY-CHAIN`
- `MM-0008-LAB-GIE-BMV`
- `SYS-0008-LAB-GIE-BMV`
- `CAL-0008-LAB-GIE-BMV`
- `DRESP-0008-LAB-GIE-BMV`
- `DECOH-0008-LAB-GIE-BMV`
- `SPREP-0008-LAB-GIE-BMV`
- `IV-0008-LAB-GIE-BMV`
- `CF-0008-LAB-GIE-BMV`
- `SV-0003-DIRECT-GIE-BMV-SEVERITY`

## Executable enforcement

Added `tools/lab_gie_bmv_source_role_policy.py` and wired it into both generated-surface sync and archive lint. The policy checks that:

- the route remains `S2` with only an `S3` conditional pocket;
- the new forecast, delta, and decision rows exist and are route-local;
- the direct decision row sees the new delta and refs;
- `EU-0008` reciprocally names the new delta but does not carry `REF-0695` through `REF-0698` as acquired evidence-unit source refs;
- core carrier/protocol/noise/calibration/state-preparation rows carry the new refs as future-record denominators;
- generated audit output matches the policy evaluation.

## Refactor note

This is intentionally not a new abstract doctrine layer. It closes an executable source-role seam in a route with a real conditional-promotion pocket. The new policy is hot-path guarded like the other source-role policies: if it stops being imported by sync or lint, release lint fails.

## Non-promotion rule

No route is promoted. The revision increases the burden on a future GIE/BMV claim: clean direct acquisition must now expose constrained-dynamics assumptions, shielding and magnetic-stability budgets, thermal-noise thresholds, subsystem/factorization assumptions, and classical/nonlocal comparator logic before any conditional `S3` language is spendable.
