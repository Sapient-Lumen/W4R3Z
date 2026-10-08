# Scenario — enterprise offline stage turns open gaps into campaign without rewriting basis

This scenario proves that a worthy front-door crate should be able to:

1. inherit a previously frozen basis and profile/stage packet;
2. extract specific missing evidence into an `evidence-gap.report`;
3. turn only those gaps into a bounded `evidence-campaign.plan`;
4. close one gap with a `gap-closure.receipt` without pretending all other gaps are solved.

The concrete story here is:

- a starter set already passed exploratory review;
- the team is attempting the `enterprise_offline_gate` stage;
- docs.rs download material was imported, but offline materialization still has static-asset caveats;
- source-parity evidence for mirrored/vendor delivery is still missing;
- and one Cargo Vet backlog item remains explicitly visible instead of getting silently regenerated away.

The key property is **non-rewrite**:
the closure receipt inherits the older basis refs and changes only the named gap.
