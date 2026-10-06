# ADR-0088: Safe-open support-bundle intake and incident-reproduction boundary

Date: 2026-03-07
Status: Accepted

## Context

DeriveBSD already has most of the pieces needed for a sane human-scale debugging flow:
`docs/481-support-bundle-contract-and-timeline-first-handoff.md` fixes the official support handoff,
`docs/267-sanitization-portal-and-disposable-sandboxes.md` makes hostile-file opening a first-class lane,
`docs/421-disposable-workspaces-and-template-microvms.md` defines the disposable workspace shape,
and `docs/220-operational-time-travel-debugging.md` shows how replay capsules fit into incident response.

What remained fuzzy was the **import/open boundary** for foreign support bundles and other investigation artifacts.
Without a hard decision here, the archive quietly drifts back toward unsafe folklore:

- support bundles become “just tarballs” that humans open directly on the host,
- imported bundle contents can be mistaken for host authority instead of foreign evidence,
- reproduction gets conflated with “run whatever was in the archive”,
- and safe-open becomes a workstation nicety rather than the system’s official intake path.

The existing `content.import.plan` / `content.import.receipt` lane is already the right place to pin this boundary.
It just needed a small execution contract that says *where* import/open work runs.

## Decision

DeriveBSD accepts a narrow **safe-open intake boundary**:

1. **Foreign support bundles and other risky imported artifacts enter through `content.import.plan` / `content.import.receipt`.**
   The import lane, not ad-hoc host opening, is the authoritative way to inspect foreign bytes.

2. **`content.import.plan.execution` is the reviewed execution boundary for import/open work.**
   It records:
   - `isolation` (`microvm`, `jail`, or `host-adapter`)
   - `network` (`none`, `brokered`, or `full`)
   - `lifetime` (`disposable` or `persistent`)

3. **The official support-bundle intake path is `microvm` + `network = none` + `lifetime = disposable`.**
   A `jail` fallback is an explicit bounded adapter, not the canonical default.

4. **`incident.bundle`, `incident.timeline`, `bundle.payload.manifest`, and payload members remain foreign evidence, not host authority.**
   They may orient or drive review, but they do not silently become policy, build inputs, or executable host commands.

5. **Incident reproduction uses existing authoritative lanes inside a disposable workspace.**
   Failed build / boot / activation reproduction may replay imported digests, plans, receipts, or replay capsules inside a disposable workspace, but the support bundle itself never becomes authority.

## Meaning in practice

### Bundle preview

A responder may preview a bundle’s timeline and metadata after import, but the preview still comes from imported foreign evidence.
The host does not “trust” the bundle just because it was received through the support path.

### Safe-open

Complex bundle members (archives, documents, traces, payload blobs) are opened through the same safe-open discipline as other quarantined imports:
no-network disposable environment first, explicit promotion/export later.

### Reproduction

Reproduction is a **derived** step.
If the bundle points at a build plan, activation receipt, or replay capsule, tooling stages those imported objects into a disposable workspace and replays the corresponding authoritative lane there.
The workflow is “import → inspect → stage → reproduce”, not “untar on the host and hope”.

## Consequences

### Positive

- The support-bundle story now has a clear intake path instead of stopping at export.
- Safe-open becomes a cross-profile default rather than a workstation-only habit.
- Imported evidence stays evidence; authoritative policy/build/apply objects stay authoritative.
- Future implementation can add polish without re-deciding the safety boundary.

### Negative / trade-offs

- This adds one more stable field set to `content.import.plan` / `content.import.receipt`.
- Some compatibility tools will need an explicit `host-adapter` escape hatch instead of pretending to be the default path.
- Exact UI/backend details for bundle preview and replay remain implementation work.

## Non-goals

This ADR does **not** decide:

- the final GUI/CLI for timeline preview,
- the final “one click reproduce” UX,
- whether the canonical disposable backend is implemented first as microVM or jail,
- or the exact redaction policy for every imported bundle member.

Those remain implementation or future RFC material.

## Why this shape

The coherence win is not inventing a new sandbox subsystem.
It is deciding that the archive’s existing import, sandbox, and replay lanes already suffice,
provided the archive says one clear thing:

**foreign support artifacts are imported and inspected in a disposable no-network lane first, and reproduction replays authoritative digests inside that lane rather than treating a support archive as ambient host authority.**
