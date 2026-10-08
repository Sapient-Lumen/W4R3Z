# 184 — Publication trigger vocabulary (deadline semantics without ambiguity)

**Track:** Shared

`PublicationContract.rules[].trigger` is deliberately simple (a string), but that makes it easy to
accidentally create **ambiguous deadline semantics** over time (e.g., “round_end” for different
people means different windows, jurisdictions, or artifact types).

This doc defines a **small, registry-backed trigger vocabulary** and the rules for extending it.

## Why this matters

Attackers can win without changing the tally by corrupting the verification ecosystem via:
- **selective delay** (“we'll publish that later…”) and
- **selective disclosure** (some audiences never see the missing artifacts).

Time-bounded accountability only works if “when does the clock start?” is stable and auditable.

(CT-style ecosystems formalize bounded-delay promises via a Maximum Merge Delay (MMD).)  
See `docs/181` and RFC 9162. https://www.rfc-editor.org/rfc/rfc9162.html

## Registry

Authoritative registry:
- `artifacts/registries/publication-triggers.csv`

A `PublicationContract` SHOULD use only triggers present in the registry.

### Extension rule

If you need a new trigger:
1. Add it to `publication-triggers.csv`.
2. Add/upgrade an ADR documenting why the trigger exists and how it is measured.
3. Update example contracts if helpful.

### Vendor/experiment triggers

For experiments, use a namespaced trigger id:
- `x-<org>.<trigger>` (e.g., `x-acme.pollbook_sync_completed`)

Namespaced triggers SHOULD still be added to the registry once they become used outside a
single experiment.

## Canonical trigger categories

These are *intentional* categories (the registry marks each trigger with one):

- **timepoint:** anchored to a timestamp decided before election day (e.g., `polls_close`)
- **artifact_event:** anchored to the generation of a specific artifact type (e.g., `enr_generated`)
- **monitoring_window:** anchored to a declared window (e.g., `coverage_window_end`)
- **detection_event:** anchored to a detection rule firing (e.g., `deadline_breach_detected`)

A trigger MUST be measurable by at least one independent observer (even if imperfectly).

## Minimal recommended triggers (A2 posture)

Track A should be able to operate with the minimal set:
- `polls_open`
- `polls_close`
- `enr_generated`
- `coverage_window_end`
- `deadline_breach_detected`

This keeps “deadline semantics” small while leaving room to expand toward A3.
