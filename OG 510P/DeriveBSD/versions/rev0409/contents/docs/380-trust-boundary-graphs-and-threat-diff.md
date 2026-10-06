# Trust boundary graphs + threat diffs (make boundary changes reviewable artifacts)

Most security failures are not “crypto broke”; they’re “a boundary changed and nobody noticed”.

OS ecosystems usually treat threat modeling as a document exercise.
DeriveBSD can do better: treat **trust boundaries** as *compiled, diffable artifacts*.

## The core idea

Add two derived objects:

- `trust.boundary.graph` (compiled): the authoritative map of **who talks to whom** and where control changes.
- `trust.boundary.diff` (derived): boundary additions/removals/changes between two generations.

Then wire these into the existing review surfaces:
- blast-radius diffs (`docs/106-blast-radius-diff.md`) add a `trust_boundaries` section
- authority drift (`authority.diff`) references boundary ids where relevant
- parser drift (`parser.diff`) references boundary ids when new untrusted-input edges appear

This makes “new trust boundary” as obvious as “new kernel syscall”.

## What counts as a trust boundary

A trust boundary is any crossing where:
- a different party is in control (tenant ↔ host, guest ↔ hypervisor)
- **untrusted inputs** become structured objects (bytes → parse)
- privilege level changes (unprivileged ↔ broker ↔ kernel)
- confidentiality/integrity assumptions change (TEE ↔ non-TEE, encrypted ↔ plaintext)
- humans intervene (operator action / breakglass)

DeriveBSD’s mantra applies:
> crossings are contracts

Boundaries should link to the contract/UAPI/parser surfaces that implement the crossing.

## Why compile this (instead of drawing diagrams)

DFDs are useful, but they rot.
The compiled graph approach keeps the diagram *derived from the system description*:

Inputs (examples):
- `derive.unit` manifests (component topology + offered/used capabilities)
- caproute database / broker wiring
- network topology plans (host substrate)
- hypervisor plans (microVM topology, attach points)

Outputs:
- stable boundary ids, so reviews can key on diffs
- explicit linkages to the mitigations (policy ids, fuzz harness ids, receipt digests)

## The boundary object (minimal fields)

A boundary entry should capture:
- **id**: stable, reviewer-facing (namespaced; see `docs/383-surface-ids-namespacing-and-stability.md`)
- **from/to**: node ids (components/domains)
- **kind**: untrusted-input / privilege-gap / confidentiality-gap / operator-action / etc
- **assets**: what’s at stake (secrets, keys, integrity of state)
- **mitigations**: which policies/receipts constrain it
- **surface links**: contract ids, UAPI surface ids, parser ids

See schema + example:
- `spec/trust.boundary.graph.schema.json`
- `spec/examples/trust.boundary.graph.json`

## Threat diffs as a gateable surface

A `trust.boundary.diff` should support simple policy checks:
- “no new `untrusted-input` boundary without a parser registry entry + fuzz plan”
- “no new boundary that crosses into `kernel` trust tier without a security review receipt”
- “no new `operator-action` boundary without consent UX + audit receipts”

See schema + example:
- `spec/trust.boundary.diff.schema.json`
- `spec/examples/trust.boundary.diff.json`

## Prior art worth stealing

- Microsoft SDL/STRIDE style threat modeling explicitly uses **trust boundaries** on DFDs.
  - Threat Modeling Tool getting started (trust boundaries in diagrams): https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-getting-started
- OWASP threat modeling guidance (DFDs + STRIDE): https://owasp.org/www-community/Threat_Modeling_Process

We’re not adopting STRIDE as dogma; we’re stealing the *shape*: boundaries are first-class.

## Where this plugs in

- Design review rubric: require a boundary diff for features that add new crossings.
  - `docs/348-design-review-rubric-and-feature-intake.md`
- Parser registry: new untrusted-input edges must point at parser ids.
  - `docs/376-parser-surface-registry-and-fuzz-gates.md`
- Authority diffs: new authority edges should reference which boundary they cross.
  - `docs/366-capability-graphs-and-authority-diff-surfaces.md`

