# Archive trigger register — 2026-03-23

This note is repo hygiene.
It is not a crate proposal.

It exists to make future passes say **what opened review** instead of silently acting as though every broad refresh is just “latest research”.

## Main judgment

Future passes should classify their triggering reason before they revise practical queue guidance or reopen a frozen packet.

Without that, later work too easily confuses:
- a new public fact,
- a real packet-opening event,
- and a full posture change.

## Minimal trigger classes for future passes

Use one or more of these classes when writing a new entry:

1. **new_release**
   - a crate release appeared, especially if `pubtime` or replay windows matter.

2. **advisory_or_trust_signal**
   - RustSec advisory, security tab change, malicious-crate notice, or similar trust surface movement.

3. **docs_or_support_surface_shift**
   - docs.rs target/default-target/build result change, rustdoc JSON availability shift, or support visibility change.

4. **cargo_or_toolchain_substrate_change**
   - build-dir layout change, Cargo JSON/schema evolution, package/provenance behavior change, or similar substrate event.

5. **local_incident_or_regression**
   - CI break, local repro, drift in a previously green path, or other operator-discovered evidence.

6. **manual_architectural_recheck**
   - a human intentionally reopened review because policy, criticality, or product scope changed.

## Entry discipline

Each future entry that changes a practical queue or reopens a top-lane packet should say:

1. which trigger class opened the pass,
2. which packet family it affected,
3. whether the result is:
   - intake only,
   - ticket opened,
   - revalidation result,
   - or transition posture.

## Anti-drift rule

Do not let future passes silently compress this chain:

`signal -> trigger intake -> ticket -> revalidation -> transition`

into this shorter and less honest chain:

`signal -> new answer`

## LLM guardrail

Before rephrasing a frozen answer, future LLM passes should explicitly ask:
- what trigger class opened review,
- whether the old task/policy still stand,
- and whether the pass is changing intake, ticketing, revalidation, or transition.

If those are not clear, append lightly or do not rewrite.

## Default register for broad Rust ecosystem passes

When rechecking official sources, classify fresh facts under this watch register:
- crates.io release timing / trust surfaces,
- RustSec / advisory changes,
- docs.rs build / metadata / rustdoc JSON shifts,
- Cargo machine surfaces and schema notes,
- Cargo build-dir / build-analysis / plumbing evolution,
- official challenge / survey / flagship signals,
- and restricted-delivery / alternate-registry incidents.

## Why this matters

The repo is now rich enough that forgetting **why** a packet was reopened is nearly as dangerous as forgetting **what** the old answer was.
