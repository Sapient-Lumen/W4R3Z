# ADR-0348: Removable-media local fallback post-detach contract closure is schema-backed and negative-tested

- Status: accepted
- Date: 2026-05-21
- Deciders: archive maintainers
- Consulted: `adrs/ADR-0347-removable-media-local-fallback-post-detach-persistent-state-stays-absent-and-scratch-stays-ephemeral.md`, `docs/758-removable-media-local-fallback-post-detach-persistent-state-stays-absent-and-scratch-stays-ephemeral.md`, `spec/removable.media.local.post_detach.contract.schema.json`

## Context

ADR-0336 through ADR-0347 narrowed the post-detach removable-media later worker across capability-mode entry, descriptors, launch context, executable identity, runtime dependency closure, credentials, lifecycle, resources, peer interaction, ambient inputs, network absence, persistent-state absence, and ephemeral scratch. That sequence made the policy small enough to implement, but it still left a review problem: several essential guarantees were carried as posture strings spread across `content.import.plan`, `content.import.receipt`, `preopen.map`, attach grants, and detach receipts.

The next implementation risk is not a missing sentence. It is that the first lane can look closed while a future edit admits a home preopen, reusable scratch, a Casper network service, path reopen, best-effort cleanup, or an undeclared output surface without a deliberately failing fixture.

## Decision

For the first host-local removable-media fallback lane, the post-detach later-worker contract is now represented by `spec/removable.media.local.post_detach.contract.schema.json` and the canonical positive example `spec/examples/removable.media.local.post_detach.contract.json`.

The canonical stack now records `schema-backed-positive-and-negative-fixture-guarded`, `receipt-must-bind-freebsd-launch-evidence-to-contract`, `known-bad-authority-shapes-must-fail-validation`, and the contract digest `sha256:4848484848484848484848484848484848484848484848484848484848484848`. The same posture appears in `content.import.plan`, `content.import.receipt`, `preopen.map`, `device.attach.grant`, and `device.detach.receipt` examples.

Negative fixtures under `spec/examples/invalid/removable-media/post-detach-contract/` must fail validation for the ordinary lane. The initial red corpus covers home preopens, reusable scratch, Casper network service authority, path reopen after capability entry, best-effort scratch cleanup, and undeclared worker output surface.

## Consequences

- The first removable-media post-detach worker is no longer only a prose bundle of posture strings; it has one typed contract object that can be validated.
- A release cannot accidentally treat invalid authority shapes as compatible examples. The red corpus becomes part of the contract, not an external review suggestion.
- Backend enforcement remains explicit: receipts must bind FreeBSD jail/Capsicum/devfs/pf/fd/scratch/output-slot evidence to the contract instead of merely asserting that the worker was disposable.
- Mount flags remain useful defense-in-depth evidence, but they are not the primary execution boundary. The primary boundary remains descriptor-only launch, capability-mode entry, no path reopen, closed runtime closure, no ambient loader/plugin search, and receipt-bound backend evidence.

## Alternatives considered

- **Keep only the existing posture strings.** Rejected because strings are easy to copy without preserving the implied backend evidence and failure cases.
- **Wait for a full runtime implementation before adding schema.** Rejected because the schema is the implementation target; delaying it would keep the next code path underspecified.
- **Test only the canonical positive example.** Rejected because positive fixtures do not prove that known-bad authority shapes are excluded.

## Follow-up

- Add generated malicious-media filesystem fixtures for FAT/exFAT/UFS/CD9660 once the walker/parser implementation exists.
- Split backend evidence into a richer receipt object when the first launcher prototype can report concrete fd rights, jail id, devfs ruleset, pf posture, and scratch teardown facts.
- Keep disk-backed scratch out of the ordinary lane unless it is memory-backed or cryptographically discarded with receipt-visible destruction evidence.

## Links

- boundary doc: `docs/759-removable-media-local-fallback-post-detach-contract-closure-is-schema-backed-and-negative-tested.md`
- schema: `spec/removable.media.local.post_detach.contract.schema.json`
- positive example: `spec/examples/removable.media.local.post_detach.contract.json`
- red corpus: `spec/examples/invalid/removable-media/post-detach-contract/`
- previous cut: `adrs/ADR-0347-removable-media-local-fallback-post-detach-persistent-state-stays-absent-and-scratch-stays-ephemeral.md`
