# ADR-0342: Removable-media local fallback post-detach worker lifecycle stays launcher-supervised and daemon-free

- Status: accepted
- Date: 2026-05-18
- Deciders: archive maintainers
- Consulted: `docs/235-process-contracts-and-service-ownership.md`, `docs/239-service-lifecycle-restarters-and-repo.md`, `docs/294-oblivious-sandboxing-launchers.md`, `docs/349-supervision-trees-and-restart-strategies.md`, `docs/746-removable-media-local-fallback-post-detach-later-tool-code-enters-capability-mode-before-mainline-and-stays-there.md`, `docs/752-removable-media-local-fallback-post-detach-credential-envelope-stays-launcher-fixed-and-non-elevating.md`, `spec/preopen.map.schema.json`

## Context

ADR-0337 through ADR-0341 made the post-detach removable-media later worker closed-world across descriptors, launch context, executable identity, runtime dependency closure, and credentials. That still leaves a process-lifetime seam: the worker can be non-root and digest-pinned while still daemonizing, double-forking, spawning unreviewed helpers, or leaving descendants behind after the launcher has already collected bytes and emitted derivative evidence.

For the first removable-media local fallback, the post-detach worker is not a service supervisor and not a background job system. It is a bounded disposable execution step over one preserved subject and one declared derivative sink. Its process tree must therefore be launcher-supervised, daemon-free, and fully reaped before any derivative receipt becomes authoritative.

## Decision

For the first host-local removable-media fallback lane, post-detach later workers now use `launcher-supervised-no-daemon-or-orphan-descendants`, `no-background-descendants-or-unreviewed-subprocesses`, and `launcher-reaps-entire-worker-tree-before-receipt`.

1. **The launcher owns the worker lifecycle.**
   - The launcher starts, observes, and terminates the reviewed worker process tree for the single post-detach operation.
   - The worker does not become a daemon, service, detached session, or long-lived helper.
   - Parent-death, supervision, or equivalent jail/process-group cleanup is implementation detail; the portable contract is that no reviewed worker descendant survives as hidden authority.

2. **Background descendants and unreviewed subprocesses stay out.**
   - The later worker records `no-background-descendants-or-unreviewed-subprocesses`.
   - Double-fork, session detachment, service activation, shell helper fanout, late plugin helper launch, and unreviewed subprocess execution stay out of the first lane.
   - A future compatibility lane that needs helper processes must declare the wrapper/broker relationship explicitly and receipt that process tree.

3. **The launcher reaps before derivative evidence becomes authoritative.**
   - The later worker records `launcher-reaps-entire-worker-tree-before-receipt`.
   - `content.import.receipt` only names the derivative authoritatively after worker exit is observed and the entire worker tree is reaped.
   - This keeps post-detach evidence from racing with still-running code that holds the declared sink or observation descriptors.

4. **Receipts expose lifecycle posture rather than trusting process folklore.**
   - Plans and receipts carry `post_detach_process_lifecycle_posture`, `post_detach_descendant_posture`, and `post_detach_reap_posture`.
   - The receipt also records `post_detach_worker_exit_posture = worker-exit-observed-before-derivative-receipt`.
   - The attach grant carries `post_detach_lifecycle_receipt_posture = receipt-records-worker-exit-and-descendant-reap` and `post_detach_process_lifecycle_required = true`.
   - The preopen map carries the same lifecycle posture as launcher-owned execution metadata.

## Consequences

- A sanitizer cannot quietly leave a background helper, orphan, daemon, or process-group survivor behind after the receipt claims the import is finished.
- The declared derivative sink remains a bounded handoff rather than a live rendezvous with still-running code.
- Support can distinguish a completed post-detach import from a launcher crash or unfinished worker tree without reconstructing process history from host-local logs.
- Tools that need subprocess helpers remain possible only through a later explicit wrapper/broker contract that admits and receipts the helper process tree.

## Alternatives considered

- **Rely on disposable jail teardown only.** Rejected because receipts should expose the lifecycle fact directly instead of depending on implementation-local cleanup folklore.
- **Allow helper subprocesses because capability mode and credentials are already narrow.** Rejected for the first lane because subprocess admission still changes code identity, lifetime, resource pressure, and receipt timing.
- **Emit derivative receipts before worker-tree reap and trust the sink bytes.** Rejected because a still-running descendant can race the broker's collection window or keep observation/egress descriptors alive.
- **Make the first lane a small service supervisor.** Rejected; service supervision belongs to explicit service/process contracts, not the first one-shot removable-media ingest lane.

## Follow-up

- Update the canonical removable-media local-ingest examples so they record post-detach worker lifecycle, descendant, reaping, and worker-exit posture.
- Add a drift check that fails if the first lane slides back to daemonization, orphan descendants, unreviewed subprocesses, or derivative receipts emitted before worker-tree reap.

## Links

- boundary doc: `docs/753-removable-media-local-fallback-post-detach-worker-lifecycle-stays-launcher-supervised-and-daemon-free.md`
- previous cut: `adrs/ADR-0341-removable-media-local-fallback-post-detach-credential-envelope-stays-launcher-fixed-and-non-elevating.md`
