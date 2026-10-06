# ADR-0084: Authority budget / check / exception boundary

- Status: Accepted
- Date: 2026-03-07

## Context

DeriveBSD already had many lane-specific authority controls:

- compiled runtime manifests (`caproute.json`, `preopen.map`, `mount.view`, `devfs.view.*`, `pki.profile.json`, `diagnostics.profile.json`)
- review surfaces (`authority.diff`, blast-radius diffs, promise-profile lint)
- lane-specific authoritative policy objects for network topology, kernel mutation, firmware / UEFI mutation, reset / reprovision, workload identity issuance, and operator sessions

But `docs/298-authority-budgets-and-permission-drift-alarms.md` still left one expensive ambiguity unresolved:

1. Is `authority.budget` a small component-runtime least-authority policy object, or a generic umbrella for every privileged action in the system?
2. Is `authority.budget.check` itself a gate / authority object, or only evidence that compiled runtime posture was compared to a budget?
3. Are waivers broad narrative exceptions, or narrow authoritative objects that can be diffed and expired?

If left vague, authority budgets would become a second giant policy universe that overlaps existing accepted boundaries.

## Decision

1. `authority.budget` is the authoritative least-authority policy object for the **component-runtime** lane.

2. In v0, the generic authority-budget lane is intentionally limited to dimensions that compile naturally from runtime intent:
   - filesystem
   - network
   - devices
   - trust
   - observability

3. `authority.budget.check` is evidence only.
   It records the comparison between a compiled runtime posture and an authoritative budget.
   The schema carries `authority_semantics = authority-budget-check-evidence-only`.

4. `authority.exception` is authoritative.
   It is a **timeboxed, field-scoped waiver** against a specific failing `authority.budget.check` and a specific `authority.budget` digest.

5. The generic authority-budget lane does **not** absorb already-distinct higher-authority lanes such as:
   - kernel mutation
   - host network-topology mutation
   - firmware / UEFI mutation
   - destructive reprovision / reset
   - workload identity issuance
   - operator-session policy

   Those lanes keep their own authoritative objects and profile-specific posture docs.
   Authority budgets may summarize them in UI/reporting later, but they do not replace those contracts.

## Consequences

- component descriptors can compile to one small least-authority budget surface instead of ad-hoc review folklore
- reviewers get a stable `authority.budget` / `authority.budget.check` / `authority.exception` trilogy that matches existing evidence-vs-authority patterns
- A/B/C/D remain viable without forks because the budget lane covers portable runtime surfaces while higher-authority product-shape decisions remain in their existing posture docs
- future expansion is still possible, but any new budget dimension beyond the five v0 dimensions now needs an RFC/ADR instead of sneaking in as “just another field”

## Why this is narrow enough

This does not redesign permissions everywhere.
It only fixes one cross-cutting least-authority boundary:

- authoritative component-runtime budget
- evidence-only budget check
- authoritative scoped exception

That is a small, high-leverage revision with bounded implementation scope.
