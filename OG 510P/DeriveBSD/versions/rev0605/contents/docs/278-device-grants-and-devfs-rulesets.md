# Device grants + devfs rulesets: treat `/dev` as authority (v0)

Most “sandboxed” systems accidentally smuggle ambient authority through **device nodes**.

On FreeBSD, the jail man page is blunt: exposing inappropriate device nodes can let a jailed process bypass sandboxing, and recommends using **devfs rules** to limit what appears in a per-jail `/dev`.  
References:
- https://man.freebsd.org/cgi/man.cgi?query=jail&sektion=8
- https://man.freebsd.org/cgi/man.cgi?query=devfs&sektion=8
- https://man.freebsd.org/cgi/man.cgi?query=devfs.rules&sektion=5

DeriveBSD should make device access:
- **explicit** (no “whatever /dev happens to contain”)
- **lease-based** (revocable, TTL'd, logged)
- **reviewable** (diffable, linted)
- **evidenced** (attach/detach receipts + inventory bindings)

This doc tightens the device story by connecting the accepted product default in `docs/476-device-authority-posture-by-profile.md` with the lower-level grant/rendering machinery.

This doc tightens the device story by connecting:
- device isolation domains (`docs/204-device-isolation-domains.md`)
- lease registry (`docs/249-lease-registry-and-cross-lane-revocation.md`)
- promise profiles (`docs/232-service-promise-profiles.md`, `docs/271-promise-profile-vocabulary-and-lint.md`)
- existing device artifacts (`spec/device.profile.schema.json`, `spec/device.attach.grant.schema.json`, `spec/device.attach.receipt.schema.json`, `spec/device.detach.receipt.schema.json`)

## Product-shape default now fixed

The archive now treats device authority as profile-shaped instead of assuming one raw-`/dev` posture for every deployment:

- **A** keeps service compartments compiled-minimal and lease-expanded
- **B** keeps raw sensitive devices host-owned and general interactive apps portal-first
- **C** keeps compiled-minimal/mediated access preferred with an explicit compatibility fallback
- **D** keeps production/factory device authority compiled-minimal and sealed, with stronger expansion in offline or strongly approved maintenance lanes

See `adrs/ADR-0066-device-authority-posture-by-profile.md`, `docs/476-device-authority-posture-by-profile.md`.

## Design principle: "device nodes are capability handles"

A device node is effectively a *handle to privileged kernel surface* (ioctl spaces, DMA setup, raw disk access, keystroke injection, etc.).
If a sandbox has access to the node, it often has access to the authority.

Therefore DeriveBSD should treat `/dev` exposure as **first-class authority**, not a filesystem detail.

## The three-layer model

### 1) Device identity + risk classification (inventory lane)

All devices that may ever be attached cross-domain should have a `device.profile`:
- stable device_id (derived from transport address + serial where possible)
- class (block/audio/video/usb-controller/net/tpm/...)
- risk tags (hid, dma, firmware-opaque, removable, untrusted-bus, etc.)

Schema + example:
- `spec/device.profile.schema.json`
- `spec/examples/device.profile.json`

### 2) Attachment is a lease (authority lane)

Cross-domain attachment is **never implicit**:
- `device.attach.grant` (lease, permissions, constraints)
- `device.attach.receipt` (what actually happened at runtime)
- `device.detach.receipt` (cleanup and revocation evidence)

Schemas + examples:
- `spec/device.attach.grant.schema.json`, `spec/examples/device.attach.grant.json`
- `spec/device.attach.receipt.schema.json`, `spec/examples/device.attach.receipt.json`, `spec/examples/device.attach.receipt.removable-media-local-ingest.json`
- `spec/device.detach.receipt.schema.json`, `spec/examples/device.detach.receipt.json`, `spec/examples/device.detach.receipt.removable-media-local-ingest.json`

### 3) Inside-domain visibility is a compiled view (enforcement lane)

Even after a device is “attached”, *visibility* inside a jail/VM should be a compiled, minimal **device view**:

- For **service jails**, default `/dev` should be near-empty:
  - `null`, `zero`, `random`/`urandom` (or a brokered RNG handle), `log` (or a logging socket)
  - no raw disk, no `usb*`, no `bpf`, no `mem`/`kmem`, no gpu nodes by default

- A promise profile + attach grant should compile into:
  - a **devfs view plan** (`devfs.view.plan`) and rendered ruleset (for jails)
  - an apply receipt (`devfs.view.receipt`) and drift/deny events (`devfs.view.event`)
  - (optionally) portal/broker endpoints instead of direct nodes

See: `docs/323-devfs-views-plans-and-receipts.md`, `spec/devfs.view.plan.schema.json`.

This is where DeriveBSD earns “pledge ergonomics” on BSD primitives:
**profiles describe intent; compilation selects concrete primitives**.

## Removable-media local fallback now has a narrower first-cut authority shape

`docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md` closes the next practical seam for imperfect B/C hardware:

- the storage session remains host-controlled and receipted through `device.attach.*`,
- the disposable ingest worker is a **no-network jail**,
- `mount.view` carries the read-only mounted ingest tree into that jail,
- and `devfs.view.plan` stays **block-empty** there so the jail receives **no raw block-device nodes** in the first cut.

That keeps the fallback narrower and more reviewable without pretending a jail is the same isolation story as a device domain or microVM, and keeps mount authority on the host.
The next hard decisions are now explicit too: the host must probe the medium with `fstyp` before mount and the first local-fallback admission table stays finite (`msdosfs`, `exfat`, `ufs`, `cd9660`) rather than inheriting every host-visible filesystem helper or pool/provider import path; once admitted, the host-side mount must keep the reviewed tuple `ro,nosuid,noexec,nosymfollow,untrusted` and treat the mounted tree as inert input only rather than a direct runtime source. The ingest walk itself is now fixed too: it stays physical and root-pinned beneath `/ingest`, admits only regular files plus explicit directories only, fails closed on symlink/device/FIFO/socket semantics, and hardlink topology stays out of scope in the first cut. The next naming cut is fixed too: member paths normalize to relative-clean Unicode NFC text, normalization collisions fail closed, and the first cut performs no silent auto-rename or source-prefix repair. The next metadata cut is fixed too: reviewed/import identity stays path/kind/payload-first, owner/mode/mtime/xattr fidelity out of scope in the first cut, and any receiver-local metadata outcomes stay receiver-local realization detail rather than portable reviewed state. The next selection-width cut is fixed too: this first lane stays single-selected-subject only, and any direct multi-member review/import must return as a later explicit lane instead of widening `content.import.*`. The next selected-subject-kind cut is fixed too: the selected subject stays regular-file-only in the first cut, and directories are not selectable import subjects in this lane. The next approval-continuity cut is fixed too: approval stays present-device-instance-only in the first cut, physical detach or lease end revokes it, and reattach requires a fresh grant even when serial or disk-ident hints look the same. The next attach-evidence cut is fixed too: the canonical `device.attach.receipt` for this lane carries a finite observed current-presence hint bundle (`ugen`/provider plus disk-ident or physical-path hints when available), explicitly marks those hints evidence-only, and keeps same-hints-on-reattach non-authoritative. The next capture-first cut is fixed too: once one selected regular file is chosen, the first non-browsing step captures that exact subject into `/work`, later operations consume the captured file rather than the live mounted path, and the canonical `spec/examples/content.import.receipt.removable-media-local-ingest.json` records that capture-first posture explicitly. The next detach-early cut is fixed too: once capture verifies against the planned subject digest, the host should end the removable-medium session, emit `device.detach.receipt`, and let later classify/scan/sanitize work continue without live device presence; the canonical `spec/examples/device.detach.receipt.removable-media-local-ingest.json` now records that authority boundary explicitly. The next post-detach worker-reset cut is fixed too: later work restarts in a fresh disposable worker with `/ingest` absent and without inherited cwd/root/fd references to the old mount rather than quietly reusing the pre-detach worker (`docs/736-removable-media-local-fallback-post-detach-later-ops-require-a-fresh-worker-with-no-live-ingest-references.md`). The next preserved-capture cut is fixed too: once capture verifies and detach completes, that capture remains preserved exact evidence and later sanitize/convert work must emit separate derivatives rather than rewriting the capture in place (`docs/737-removable-media-local-fallback-preserves-the-verified-capture-and-forbids-in-place-rewrite-by-later-ops.md`). The next authoritative-store cut is fixed too: the verified capture may not remain authoritative only under disposable `/work`; before detach it must commit into authoritative quarantine store, and later work must read the stored preserved capture or a read-only projection of it (`docs/738-removable-media-local-fallback-verified-capture-commits-into-authoritative-quarantine-store-before-detach.md`). The next single-object projection cut is fixed too: after detach, later work may receive only one synthetic single-object projection or equivalent brokered read handle for the preserved capture, and it may not browse the authoritative quarantine-store namespace (`docs/739-removable-media-local-fallback-post-detach-preserved-capture-delivery-stays-single-object-and-store-opaque.md`). The next digest-bound delivery cut is fixed too: that synthetic later-worker delivery is only plumbing, must match the preserved selected subject digest before later operations begin, and is now wired through `docs/740-removable-media-local-fallback-post-detach-single-object-delivery-stays-digest-bound-and-receipt-evidenced.md`. The next launcher-preopened delivery cut is fixed too: after that binding, later execution must stay on one launcher-preopened read-only object (or equivalent), any worker-visible path stays compatibility-only plumbing, and the later worker may not reacquire the subject through broader path or authoritative-store lookup (`docs/741-removable-media-local-fallback-post-detach-delivery-stays-launcher-preopened-read-only-and-path-reopen-stays-out.md`). The next broker-collected derivative-egress cut is fixed too: later worker output must leave through launcher-prepared disposable sink objects, worker outbox paths stay non-authoritative, and the launcher/broker must collect + remeasure those bytes before the receipt names an authoritative derivative locator (`docs/742-removable-media-local-fallback-post-detach-derivative-egress-stays-broker-collected-and-worker-outbox-paths-stay-nonauthoritative.md`). The next single-declared-slot cut is fixed too: the later worker now gets only one declared writable derivative slot, any receipt-visible derivative must come from that slot, and extra worker result surface stays out in the first lane (`docs/743-removable-media-local-fallback-post-detach-derivative-egress-stays-single-declared-slot-and-no-extra-worker-result-surface.md`). The next empty-write-only-slot cut is fixed too: that declared slot starts as a launcher-precreated empty regular file and keeps worker readback/truncate out (see `adrs/ADR-0334-removable-media-local-fallback-post-detach-derivative-slot-stays-empty-writeonly-and-no-readback-or-truncate.md`, `docs/744-removable-media-local-fallback-post-detach-derivative-slot-stays-empty-writeonly-and-no-readback-or-truncate.md`). The next append-open-derivative-slot cut is fixed too: because the first lane still uses a seekable regular-file sink on FreeBSD, the launcher now hands that sink over already opened `O_APPEND`, keeps it append-only-protected while the worker runs, omits `CAP_READ`/`CAP_FTRUNCATE`/`CAP_FCNTL`, and treats any `CAP_SEEK` there as implementation ballast rather than rewrite authority (`adrs/ADR-0335-removable-media-local-fallback-post-detach-derivative-slot-stays-append-open-and-append-only-protected-on-seekable-file-delivery.md`, `docs/745-removable-media-local-fallback-post-detach-derivative-slot-stays-append-open-and-append-only-protected-on-seekable-file-delivery.md`). The next capability-mode-entry cut is fixed too: the launcher or its approved shim enters capability mode before handing control to later tool mainline code, descendants inherit that mode and may not clear it, ambient absolute-path opens stay out after `cap_enter()`, and tools that cannot run on the preopened capability set stay out unless a later explicit wrapper/broker contract earns them. The next closed-world-descriptor-set cut is fixed too: after that boundary, the later worker inherits only the reviewed descriptor set, the launcher closes or spawn-closefroms every non-reviewed descriptor before handoff, `stdin` stays inert null/empty input only, and `stdout`/`stderr` stay launcher-owned observation channels or reviewed append-only log sinks instead of inherited parent-session surfaces (see `adrs/ADR-0337-removable-media-local-fallback-post-detach-reviewed-descriptor-set-stays-closed-world-and-stdio-is-launcher-owned.md`, `docs/747-removable-media-local-fallback-post-detach-reviewed-descriptor-set-stays-closed-world-and-stdio-is-launcher-owned.md`).

## Compilation sketch (what the system does)

Inputs:
- `sandbox-profile` (what the service says it needs)
- `device.profile` (what the hardware *is*)
- `device.attach.grant` (what authority is allowed right now)
- host policy (global constraints, “never allow X in jail Y”)

Outputs:
- `devfs.view.plan` compiled intent + rendered ruleset applied to the jail's devfs mount (when jailed)
- `devfs.view.receipt` emitted after apply (ruleset id + observed node digest)
- `devfs.view.event` for drift/deny incidents
- portal routes for dangerous classes (HID, raw block, GPU control surfaces)
- evidence receipts bound into the incident bundle lane (`docs/216-…`, `spec/incident.bundle.schema.json`)

## Lint rules we should enforce

- **No silent device expansion**: a profile that requests any device class beyond the curated “safe pseudo-dev set” must name it explicitly.
- **HID is special-danger**: input device grants should require secure attention / interactive consent (`docs/207-input-authority-secure-attention-and-hid-risk.md`).
- **Block devices default read-only** unless an explicit `writable` constraint exists in the lease grant.
- **Raw disk implies breakglass**: profiles requesting raw block access should be flagged as high-risk and require a policy decision record.
- **DMA-capable devices must not land in the “trusted” domain** unless explicitly allowed (prefer device isolation domains).

## Open questions (push into an ADR when decided)

- Should “device portals” be mandatory for certain classes (HID, webcam, microphone), even when a node exists?
- How do we express “this service may use *a* webcam” without creating ambient authority (device selection + consent UX)?


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

## Removable-media backend evidence joins

Device grants and detach receipts for the local removable-media fallback now include the post-detach contract closure posture: `schema-backed-positive-and-negative-fixture-guarded`. A successful lane must bind FreeBSD launch evidence with `receipt-must-bind-freebsd-launch-evidence-to-contract` rather than relying on a remembered jail/devfs template.

## r505 devfs / launch-evidence join

The removable-media post-detach lane now requires `typed-freebsd-launch-evidence-positive-and-negative-fixture-guarded`. The evidence object records the devfs ruleset digest and `no-worker-visible-device-nodes` posture alongside Capsicum, Casper, pf, and fd-table evidence, so devfs hardening is tied to a validated launch proof rather than an attach-time hint only.


## r506 recovery-evidence join

The removable-media post-detach lane now requires `typed-post-detach-recovery-evidence-positive-and-negative-fixture-guarded` after launch evidence. Device grants and devfs views remain attach-time constraints, but recovery evidence decides whether interruption left any device/media path, worker fd, or scratch namespace reachable before derivative receipt visibility.

Last updated: 2026-05-21r506
