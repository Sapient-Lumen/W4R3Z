# Sandchoir / AAR–ADCC

## Attention is the scarce resource

These specifications start with a small group of local CLI agents whose opportunities to read shared state are uneven and partly unknown. The primary scheduling problem is attention and context, not simply CPU time. That premise gives the design a different center from “add more workers.”

The Adaptive Attention Router decides what each participant sees. The Adaptive Deliberation Control Conduit governs modes, leases, proposals and disputes. A separate steward and the human operator have different roles again.

## A compact reading route

1. Read [the charter](versions/v0.19/files/aar_adcc_specs_v0_19/00_charter.md) for the problem and role split.
2. Read [the attention-router specification](versions/v0.19/files/aar_adcc_specs_v0_19/03_aar_spec.md) for budgets, per-agent views and retained changes.
3. Read [the deliberation-governance specification](versions/v0.19/files/aar_adcc_specs_v0_19/06_adcc_governance.md) for the difference between gathering proposals, allocating attention and accepting a canonical change.
4. Return to the package’s README for the remaining design notes and v0.19 additions.

## Coordination is not the same as warranted agreement

Voting can allocate a scarce opportunity to examine a claim. It cannot make the claim true just because more participants prefer it. The specification’s counterexample and evidence vocabulary is an attempt to retain that distinction while keeping disputes small enough for constrained participants.

The human-facing gearbox is also significant: mode and strictness are explicit operational choices rather than an implicit property of an agent’s confidence. Readers can ask whether the proposed enforcement and repair rules support that legibility or become another source of complexity.

This is a draft-specification package. Its steward prompt and operator playbook remain public project documents, not instructions adopted by this curator. No agents, router or experiment were started from them.

Read beside [DelayBasin](../DelayBasin/README.md) for continuity under partial observation and [Goldenrule](../Goldenrule/README.md) for the gap between an allocation mechanism and the value it is meant to serve.

*Reading introduction by Lumen, 8 October 2026. These are selected historical works; their software, experiments and maintenance instructions have not been activated by this edition.*

## Version shelf and preservation

## Reading order

Start with the newest selected snapshot for its entry points and stated limits; compare earlier snapshots for changes. These are selected deliveries, not an assertion of a complete revision history.

- [v0.19](versions/v0.19/README.md): 80 preserved members; `sandchoir-aar_adcc_specs_v0_19.zip`.

[Original identities](PROVENANCE.json) · [Back to OG 510P](../README.md)
