# Safe-open support-bundle intake and incident-reproduction boundary

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability, reproducibility  
**Patterns:** Plan→Apply→Receipt, Broker→Lease→Receipt, Capsule  

DeriveBSD already has an export story for support bundles and an intake story for quarantined content.
This doc makes one small but important decision: **the official way to inspect a foreign support bundle is the safe-open import lane, not direct host opening.**

See also:
- ADR: `adrs/ADR-0088-safe-open-support-bundle-intake-and-repro-boundary.md`
- official support handoff: `docs/481-support-bundle-contract-and-timeline-first-handoff.md`
- origin/quarantine import lane: `docs/280-origin-labels-and-quarantine-attributes.md`
- sanitization portal: `docs/267-sanitization-portal-and-disposable-sandboxes.md`
- disposable workspaces: `docs/421-disposable-workspaces-and-template-microvms.md`
- replay capsules in operations: `docs/220-operational-time-travel-debugging.md`
- typed intake shapes: `docs/502-support-bundle-intake-typed-plan-and-receipt-shapes.md`

## Why this needs a hard decision

The archive already says how to **build** a support bundle.
What it did not say crisply enough was how to **receive and inspect** one.
That gap is expensive:

- operators eventually start opening foreign tarballs directly on the host,
- complex bundle members become “trusted because support sent them”,
- reproduction turns into a shell-session ritual instead of a derived operation,
- and the timeline-first handoff loses its safety advantage because responders still have to poke at raw bytes on the host.

The archive already has the right pieces to avoid this.
We just need to route the official workflow through them.

## The official intake boundary

Foreign support bundles and other risky investigation artifacts should be handled like other quarantined imports:

1. **Import via `content.import.plan`.**
   The plan names the subject digest, origin record, import operations, and now the execution boundary for the work.

2. **Run the import/open work in a disposable, no-network compartment.**
   The canonical shape is:
   - `execution.isolation = microvm`
   - `execution.network = none`
   - `execution.lifetime = disposable`

3. **Emit `content.import.receipt`.**
   The receipt records what happened, which outputs were produced, and the execution boundary actually used.

4. **Preview timeline/manifest metadata first.**
   If a support bundle contains `incident.timeline`, `incident.bundle`, and `bundle.payload.manifest`, those should be the default orientation surfaces before a responder opens payload members.

5. **Stage reproduction in a disposable workspace.**
   If deeper reproduction is needed, tooling stages imported digests/receipts/capsules into a disposable workspace and uses the existing build/activation/debug lanes there.

This keeps the support archive a **foreign evidence package**, not a hidden authority object.

## Minimal artifact changes

The import lane now carries a tiny execution contract:

- `content.import.plan.execution`
- `content.import.receipt.execution`

The official support-bundle path now also has **typed support-bundle plan / receipt profiles**:

- `spec/content.import.support-bundle.plan.schema.json`
- `spec/content.import.support-bundle.receipt.schema.json`

These are constrained shapes of the generic import artifacts, **not a new import authority kind**.
They pin the **canonical `tar.zst` handoff**, the timeline-first preview posture, and the no-network disposable execution contract without widening the design.

The v0 field set is intentionally small:

- `isolation`: `microvm` | `jail` | `host-adapter`
- `network`: `none` | `brokered` | `full`
- `lifetime`: `disposable` | `persistent`

That is enough to say whether a responder followed the official safe-open path, without inventing a giant sandbox schema.

## Support-bundle preview posture

Timeline-first stays the human default:

- preview `incident.timeline` and `incident.bundle` metadata first,
- use `bundle.payload.manifest` to orient before opening members,
- keep imported members quarantined until explicit promotion/export.

This is the same design instinct behind safe document opening:
**show the story and the metadata first; open foreign payloads only in a bounded compartment.**

## Incident reproduction posture

The official reproduction path is deliberately conservative:

- **build failures:** replay imported build inputs/receipts inside a disposable workspace
- **boot or activation failures:** stage imported receipts/manifests/logical plans into a disposable workspace and replay the relevant authoritative lane there
- **heisenbugs or tricky service faults:** use imported `debug.replay.capsule` material when available

The important point is not the exact UI.
It is the boundary:

- the imported support bundle remains **foreign evidence**,
- reproduction remains a **derived operation**,
- and the work happens in a disposable workspace rather than the long-lived host environment.

## Product-shape fit

### A) Secure fleet host

Support import stays explainable and auditable.
Fleet responders do not need ad-hoc shell folklore to inspect a customer or site bundle.

### B) Secure workstation

“Open safely” becomes the default support story, not a special case for suspicious PDFs.
Trusted UI can preview timelines before any deeper open.

### C) General-purpose OS

The path stays locally viable without requiring a central support backend.
`host-adapter` can exist for compatibility, but it is named as such instead of masquerading as the default.

### D) Appliance / factory / regulatory

Offline or approved support intake remains compatible with the bundle/evidence model.
No-network disposable inspection fits well with production and evidence-bound environments.

## What this does not decide

Still open:

- the final GUI/CLI for timeline preview and “reproduce incident”,
- the final backend choice for the default disposable compartment,
- exact resource budgets for heavy replay or archive analysis,
- and exact redaction/detail policy for every imported member class.

Those are implementation questions.
The boundary itself is now fixed.

## Design cues from current systems

The current ecosystem pattern is clear and stable:

- Qubes keeps “open untrusted links and attachments in disposables” as a first-class workflow.
- Dangerzone treats hostile documents as something to render in a hardened sandbox before broader use.
- ReproZip treats reproduction as an explicit captured environment/input bundle instead of “rerun some mystery commands”.

DeriveBSD should keep the same instinct while translating it into its own typed artifact model:
import first, inspect in a disposable lane, then reproduce from authoritative digests if needed.

Last updated: 2026-03-08r231
