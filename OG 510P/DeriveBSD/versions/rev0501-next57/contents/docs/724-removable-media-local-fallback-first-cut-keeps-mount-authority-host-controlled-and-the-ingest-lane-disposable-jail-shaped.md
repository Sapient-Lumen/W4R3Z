# Removable-media local fallback first cut keeps mount authority host-controlled and the ingest lane disposable-jail-shaped

**Tier:** B (Implementation floor)  
**Profiles:** B, C  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Plan→Apply→Receipt

`docs/723-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md` already fixed what the imperfect-hardware fallback is allowed to be.
This page closes the next smaller implementation seam:

> what is the first buildable execution boundary for that fallback without pretending a jail is the same thing as a device domain or microVM?

The answer is intentionally pragmatic and narrow:

> **host-controlled explicit read-only mount, feeding a disposable no-network ingest jail through a read-only `mount.view`, with no raw block device nodes exposed inside the jail.**

See also:
- ADR: `adrs/ADR-0314-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md`
- previous fallback boundary: `docs/723-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md`
- workflow doc: `docs/279-usb-quarantine-and-removable-media-workflow.md`
- device authority: `docs/278-device-grants-and-devfs-rulesets.md`
- mount views: `docs/264-mount-namespaces-and-union-views.md`
- sanitization portal: `docs/267-sanitization-portal-and-disposable-sandboxes.md`

## Accepted boundary

### 1) The host keeps attach and mount authority in the first cut

The first local fallback does **not** hand raw storage authority to the disposable ingest lane.
Instead, the host remains the control/evidence point for:

- device classification,
- trusted-UI or explicit local-admin authorization,
- `device.attach.grant` / `device.attach.receipt`,
- explicit read-only-first mount,
- and `device.detach.receipt` when the session ends, including the new first honest early-end point where verified capture lets the host end the medium session early before later work continues.

This keeps the first implementation small and makes the high-risk storage session stay visible on the host side where policy, receipts, and support tooling already live.

### 2) The first disposable ingest lane is a no-network jail

The initial B/C compatibility floor is a disposable jail with:

- `network = none`,
- a fresh `mount.view`,
- a minimal `devfs.view.plan`,
- and scratch space that is separate from the read-only ingest tree.

This is the smallest host-local compartment DeriveBSD can already describe crisply with existing artifacts.
It is deliberately not a claim that jails are the final or strongest answer.

### 3) The ingest jail gets a mounted tree, not raw block-device nodes

This is the key hard decision in this page.
The ingest jail should see:

- a read-only mounted tree such as `/ingest`,
- scratch/output space such as `/work`,
- and no raw `da*` / `ada*` / `nvd*` / `pass*` authority.

That means the first-cut split is:

- host: attach + explicit read-only mount + receipt boundary,
- jail: inspect/classify/scan/sanitize/import on the mounted tree.

So even though `devfs.view.plan` remains part of the evidence stack, the first-cut plan is **block-empty** for this lane.
The storage session is still real, but raw device authority does not spread into the disposable worker.

### 4) This is a compatibility floor, not an end-state equivalence claim

The archive should stay honest here:

- a device domain with controller isolation is still stronger,
- a microVM-backed ingest lane can still become the better answer later,
- and D still prefers device-domain or ingest-station posture for production/regulatory work.

This page only says what the **first buildable** B/C fallback should be.
It does not say the archive is done with removable-media isolation.

## Canonical first-cut example stack

The first spec-shaped example stack is now explicit:

- `spec/examples/device.attach.grant.removable-media-local-ingest.json`
- `spec/examples/device.attach.receipt.removable-media-local-ingest.json`
- `spec/examples/devfs.view.plan.removable-media-local-ingest.json`
- `spec/examples/mount.view.removable-media-local-ingest.json`
- `spec/examples/content.import.plan.removable-media-local-ingest.json`

Together they say:

- the storage session is explicit and read-only-first,
- the attach receipt keeps a finite current-presence hint bundle without turning it into durable authority,
- once one selected regular file is chosen, the first non-browsing step is capture-first into disposable `/work` staging rather than later operations consuming the live mounted path,
- once that verified capture completes, the preserved subject commits into authoritative quarantine store before detach,
- the host then ends the removable-medium session and emits `device.detach.receipt` before later operations continue,
- later work then restarts in a fresh worker after detach with `/ingest` absent (/ingest absent), must read a read-only projection of the stored preserved capture, specifically a single-object projection of the stored preserved capture, rather than quietly reusing the pre-capture worker or its scratch path, and it receives not a browseable authoritative-store subtree, the synthetic delivery path must stay digest-bound to the preserved capture because the synthetic delivery path is only plumbing, keeps that later execution object launcher-preopened read-only (or equivalent) so the worker does not reacquire the subject through broader path or store lookup, later worker derivative bytes leave only through launcher-prepared disposable sink objects, the first lane narrows that to one declared launcher-prepared disposable sink slot, more specifically one declared launcher-prepared empty sink slot with no readback or truncate, and on FreeBSD seekable-file delivery that sink is handed over append-open and append-only-protected while any `CAP_SEEK` remains ballast rather than rewrite authority, the launcher or its approved shim enters capability mode before handing control to later tool code, ambient absolute-path opens stay out after `cap_enter()`, tools that cannot run on the preopened capability set stay out unless a later explicit wrapper/broker contract earns them, keeps the reviewed post-detach descriptor set closed-world by closing or spawn-closefroming every non-reviewed descriptor before handoff, keeps stdin inert null/empty input only, keeps stdout/stderr launcher-owned observation channels or reviewed append-only log sinks rather than inherited parent-session surfaces (see `docs/747-removable-media-local-fallback-post-detach-reviewed-descriptor-set-stays-closed-world-and-stdio-is-launcher-owned.md`), keeps worker outbox paths non-authoritative execution plumbing, and the launcher/broker collects + remeasures those bytes, more specifically it must collect + remeasure the bytes from that declared slot before a derivative becomes receipt authority,
- the authoritative stored capture remains preserved exact evidence and later outputs stay separate derivatives from that preserved capture rather than rewriting it in place,
- the jail is disposable and no-network,
- the ingest tree is projected by `mount.view`,
- and the jail does not receive raw block device nodes.

## Why this cut is worth making now

Without this choice, the archive keeps paying the same decision tax repeatedly:

- implementation work cannot tell whether to start with raw device-in-jail, microVM-or-bust, or host-local mount helpers,
- review surfaces cannot tell whether `devfs.view.plan` or `mount.view` is the real authority carrier for the first cut,
- and B/C viability keeps depending on an implementation story that is too vague to test.

This page makes the first coding target finite while keeping the stronger long-term lanes open.

## What remains open

Still intentionally open:

- exact filesystem support/deny matrix for the first cut,
- whether later B/C releases should switch to a microVM-backed ingest lane when practical,
- exact trusted-UI prompt wording and policy-review affordances,
- and integrated-device families that are still outside the storage-only fallback lane.


## Reviewed post-detach process launch context

The next first-lane removable-media cut is now accepted in `adrs/ADR-0338-removable-media-local-fallback-post-detach-process-launch-context-stays-reviewed-and-ambient-free.md` and `docs/749-removable-media-local-fallback-post-detach-process-launch-context-stays-reviewed-and-ambient-free.md`.
After the descriptor set is closed-world, the later worker must also start with `reviewed-minimal-env-no-inherited-parent-env`, `launcher-reviewed-argv-no-media-derived-args`, and `launcher-owned-empty-workdir-no-ingest-store-cwd`.
That means parent environment is not inherited wholesale, media-derived names do not become worker arguments, and cwd is launcher-owned empty scratch rather than `/ingest`, the authoritative store, or the parent cwd.

## Pinned post-detach executable identity

The next first-lane removable-media cut is now accepted in `adrs/ADR-0339-removable-media-local-fallback-post-detach-executable-identity-stays-launcher-pinned-and-path-search-free.md` and `docs/750-removable-media-local-fallback-post-detach-executable-identity-stays-launcher-pinned-and-path-search-free.md`.
After reviewed descriptors plus reviewed env/argv/cwd, the later worker must also use `launcher-resolved-executable-digest-no-path-search` and `receipt-records-executable-and-wrapper-digests`.
That means `PATH`, cwd, mutable package state, media-derived executable names, and implicit helper/plugin discovery do not choose the code that processes the preserved subject; helper/plugin discovery stays `no-implicit-helper-or-plugin-discovery` unless a later explicit wrapper/broker contract admits it.

## Pinned post-detach runtime dependency closure

The next first-lane removable-media cut is now accepted in `adrs/ADR-0340-removable-media-local-fallback-post-detach-runtime-dependency-closure-stays-launcher-pinned-and-loader-path-free.md` and `docs/751-removable-media-local-fallback-post-detach-runtime-dependency-closure-stays-launcher-pinned-and-loader-path-free.md`.
After executable identity is pinned, the later worker must also use `launcher-pinned-runtime-dependency-closure-no-ambient-loader-search` and `receipt-records-runtime-dependency-closure-digest`.
That means `LD_LIBRARY_PATH`, cwd-relative library lookup, `/ingest` or media-derived library paths, host-global loader hints, and mutable package state do not choose runtime code; dynamic-loader posture stays `no-ld-library-path-cwd-or-media-derived-loader-inputs` unless a later explicit wrapper/broker contract admits richer dependency discovery.

## Launcher-fixed post-detach credential envelope

The next first-lane removable-media cut is now accepted in `adrs/ADR-0341-removable-media-local-fallback-post-detach-credential-envelope-stays-launcher-fixed-and-non-elevating.md` and `docs/752-removable-media-local-fallback-post-detach-credential-envelope-stays-launcher-fixed-and-non-elevating.md`.
After executable and runtime dependency identity are pinned, the later worker must also use `launcher-fixed-unprivileged-credential-envelope-no-supplementary-groups` and `receipt-records-worker-credential-envelope`.
That means the worker runs as the reviewed `derive-rm-worker:derive-rm-worker` envelope, supplementary groups stay `no-supplementary-groups`, and setuid/setgid/saved-ID or ambient privilege regain stays `no-setuid-setgid-saved-id-or-ambient-privilege-regain` unless a later explicit broker/helper lane admits and receipts privileged behavior.

## Launcher-supervised post-detach worker lifecycle

The next first-lane removable-media cut is now accepted in `adrs/ADR-0342-removable-media-local-fallback-post-detach-worker-lifecycle-stays-launcher-supervised-and-daemon-free.md` and `docs/753-removable-media-local-fallback-post-detach-worker-lifecycle-stays-launcher-supervised-and-daemon-free.md`.
After credentials are launcher-fixed and non-elevating, the later worker must also use `launcher-supervised-no-daemon-or-orphan-descendants` and `receipt-records-worker-exit-and-descendant-reap`.
That means background descendants and unreviewed subprocesses stay `no-background-descendants-or-unreviewed-subprocesses`, and the launcher must `launcher-reaps-entire-worker-tree-before-receipt` so derivative receipt authority does not race a still-running helper or orphaned process tree.

## Launcher-enforced post-detach resource envelope

The next first-lane removable-media cut is now accepted in `adrs/ADR-0343-removable-media-local-fallback-post-detach-resource-envelope-stays-launcher-enforced-and-receipt-visible.md` and `docs/754-removable-media-local-fallback-post-detach-resource-envelope-stays-launcher-enforced-and-receipt-visible.md`.
After worker lifecycle is launcher-supervised and daemon-free, the later worker must also use `launcher-enforced-resource-envelope-no-unbounded-worker-consumption` and `receipt-records-resource-envelope-and-observed-usage`.
That means CPU time, wall clock, memory, open-file count, process count, scratch bytes, and declared derivative-output bytes are launcher-fixed before tool mainline starts; `declared-derivative-output-size-bound-before-receipt` keeps the single declared sink bounded, and `resource-limit-hit-fails-closed-no-derivative-authority` keeps partial output from becoming authoritative after a limit hit.

The next first-lane removable-media cut is now accepted in `adrs/ADR-0344-removable-media-local-fallback-post-detach-peer-interaction-stays-launcher-isolated-and-ambient-ipc-free.md` and `docs/755-removable-media-local-fallback-post-detach-peer-interaction-stays-launcher-isolated-and-ambient-ipc-free.md`.
After the resource envelope is launcher-enforced and receipt-visible, peer interaction must also be explicit: `launcher-isolated-peer-envelope-no-ambient-ptrace-signal-or-ipc` and `receipt-records-peer-isolation-and-signal-policy` keep same-UID peer control, parent-session signals, procfs/ptrace/ktrace visibility, and unreviewed IPC out of the ordinary post-detach derivative path.
Signal authority stays `launcher-only-signal-control-no-peer-or-session-control`, IPC stays `no-unreviewed-ipc-sockets-shm-pipes-or-procfs`, and process-observation surfaces stay `procfs-ptrace-and-ktrace-unavailable-to-worker-and-peers`.


The next first-lane removable-media cut is now accepted in `adrs/ADR-0345-removable-media-local-fallback-post-detach-ambient-inputs-stay-launcher-sealed-and-receipt-visible.md` and `docs/756-removable-media-local-fallback-post-detach-ambient-inputs-stay-launcher-sealed-and-receipt-visible.md`.
After peer interaction is launcher-isolated and ambient-IPC-free, ambient host observations must also be explicit: `launcher-sealed-ambient-input-envelope-no-worker-clock-random-or-host-identity` and `receipt-records-ambient-input-envelope-and-launcher-owned-timestamps` keep wall-clock time, timezone state, host entropy, randomness, hostname, kernel/sysctl facts, locale, and machine identity out of ordinary derivative input authority.
Time stays `worker-wall-clock-and-timezone-not-derivative-authority`, randomness stays `no-worker-randomness-or-host-entropy-as-derivative-input`, and host identity stays `hostname-kernel-sysctl-locale-and-machine-identity-not-derivative-authority` unless a later explicit compatibility lane declares and receipts those inputs.

The next first-lane removable-media cut is now accepted in `adrs/ADR-0346-removable-media-local-fallback-post-detach-network-egress-stays-absent-and-receipt-visible.md` and `docs/757-removable-media-local-fallback-post-detach-network-egress-stays-absent-and-receipt-visible.md`.
After ambient host inputs are launcher-sealed, remote authority must also stay explicit: `network-egress-absent-no-socket-dns-or-remote-callbacks` and `receipt-records-network-absent-envelope` keep socket egress, DNS/NSS/name-service lookup, proxy configuration, remote fetches, telemetry, license checks, update checks, safe-browsing lookups, and callbacks out of ordinary derivative authority.
Name resolution stays `no-dns-mdns-nss-or-resolver-host-input`, proxy state stays `no-proxy-or-remote-service-configuration`, and remote dependencies stay `no-remote-fetch-or-callback-derivative-authority` unless a later explicit compatibility lane brokers and receipts network authority.

The next persistent-state cut is fixed too: `persistent-state-absent-no-home-cache-or-host-state-writes` and `receipt-records-persistent-state-absence-and-scratch-cleanup` keep user-home/cache/config/history, crash dumps, lock files, durable tool profiles, and reusable scratch out of the first lane. Scratch is `launcher-created-empty-scratch-nonauthoritative`, cleanup is `scratch-destroyed-before-derivative-receipt`, and `no-user-home-cache-config-or-history-state` means local tool caches or profile stores cannot become ordinary derivative authority unless a later compatibility lane declares and receipts them.

## r504 mount-hardening clarification

The post-detach contract closure records `schema-backed-positive-and-negative-fixture-guarded` and `defense-in-depth-not-primary-exec-boundary`. The host-controlled read-only mount and flags such as `nodev`, `nosuid`, `noexec`, and `nosymfollow` stay important evidence, but the no-execution authority boundary is the later descriptor-only launch, capability-mode entry, no path reopen, pinned executable/runtime closure, no ambient loader/plugin/helper search, and receipt-bound backend evidence.

## r505 disposable jail evidence target

The disposable-jail shape now has a concrete launch-evidence target: `spec/removable.media.local.post_detach.launch.evidence.schema.json` and `typed-freebsd-launch-evidence-positive-and-negative-fixture-guarded`. The ordinary lane must prove the fd table after `closefrom`, Capsicum entry before tool mainline, Casper absence, devfs/pf posture, no inherited parent environment, nonpersistent scratch, and declared output-slot binding instead of relying on jail disposability as a narrative property.


## r506 disposable jail recovery target

The disposable-jail shape now has a recovery-evidence target: `spec/removable.media.local.post_detach.recovery.evidence.schema.json` and `typed-post-detach-recovery-evidence-positive-and-negative-fixture-guarded`. The ordinary lane must prove that cleanup/recovery completed after normal exit, timeout, worker kill, or crash before any derivative receipt becomes visible; jail disposability alone is not the recovery proof.

Last updated: 2026-05-21r506
