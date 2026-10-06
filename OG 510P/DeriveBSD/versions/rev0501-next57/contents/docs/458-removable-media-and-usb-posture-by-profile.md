# Removable media and USB posture by profile

**Tier:** B (Cross-cutting product-shape decision)
**Profiles:** A, B, C, D
**Pillars:** isolation, supply-chain, operability
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate

Removable media is one of the easiest ways for an archive like this to become incoherent:
USB convenience pressures product **B**, air-gap workflows pressure **D**, break-glass habits pressure **A**, and consumer hardware constraints pressure **C**.

This doc records the smallest durable answer:

> no profile gets ambient automount into its most trusted plane, and removable media stays quarantine-first even when hardware support differs.

See `adrs/ADR-0048-removable-media-and-usb-posture-by-profile.md`.

## Baseline rule

Across all profiles:

- removable media is **never** ambient by default,
- discovery/classification may be automatic, but **mount/use is explicit**,
- untrusted files prefer **sanitize → import**,
- block devices prefer **read-only first**,
- and attach/import activity is receipted so “who had the device?” stays answerable.

This keeps USB/removable-media behavior aligned with DeriveBSD’s wider model: authority is leased, explained, and evidenced.

## Profile defaults

| Profile | `removable_media` default | `usb_isolation` default | Practical meaning |
|---|---|---|---|
| **A fleet_host** | `deny-or-quarantine-only` | `prefer-device-domain-no-host-automount` | Fleet hosts should not normalize local USB workflows; if media is used at all, it stays explicit, receipted, and ideally isolated from the core host. |
| **B workstation** | `quarantine-first-no-automount` | `device-domain-required-when-supported` | The host keeps trusted UI/HID authority; storage/media flows go through quarantine/device domains and sanitize/import paths, not direct automount into the trusted desktop plane. On imperfect hardware, the only local fallback is the new storage-only, session-scoped, quarantine-first ingest lane from `docs/723-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md`. |
| **C general_os** | `quarantine-first-local-fallback` | `prefer-device-domain-fallback-to-local-policy` | General-purpose installs still prefer isolated controllers, but imperfect consumer hardware may use the same bounded storage-only local authorization fallback instead of ambient automount or generic USB passthrough. |
| **D appliance_factory** | `offline-ingest-quarantine-first` | `device-domain-or-ingest-station` | Regulatory/offline ingest should happen through a quarantined path or dedicated ingest station, then quarantine→promote into trusted update/evidence lanes. |

These values live in `spec/examples/product.profiles.json` and are guarded by `tools/check_product_profiles.py`.

## The fallback is now narrower than “USB with prompts”

The archive now makes the first local fallback concrete in `docs/723-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md`:

- **storage-only local fallback** for removable-media ingest/export,
- **session-scoped** fresh authorization and receipts,
- **read-only-first** and **quarantine-first** execution,
- first-cut execution as a **host-controlled read-only mount** feeding a **disposable no-network jail** via `mount.view`,
- **no raw HID**, **no network/debug gadgets**, **no generic USB passthrough**, and **no raw block-device nodes in the ingest jail** inside this lane.

That is the key hard decision that keeps B/C viable on imperfect hardware without weakening A/B/D around trusted UI, HID, or production ingest posture.

## The hard decision hidden inside the table

The archive is now choosing **against** a universal “USB is just storage” mental model.
That means:

- no trusted-plane automount as the default convenience path,
- no requirement that every laptop magically support perfect controller isolation,
- but also no excuse for returning to ambient local attach semantics.

Instead, profiles **B** (on imperfect hardware) and **C** get the only explicit storage-shaped fallback:

- classify the device,
- apply a local authorization policy,
- default block/deny unknown devices until the user or policy engine authorizes them,
- keep mounts explicit and read-only-first,
- and route imported content through origin/quarantine handling.

That fallback should look like a **policy engine**, not like an automounter with a scary dialog.
The next implementation floor is now finite too: host-local B/C ingest must probe with `fstyp` before mount and admit only `msdosfs`, `exfat`, `ufs`, and `cd9660` in this first lane; `ext2fs`, `ntfs`, `zfs`, `geli`, and unknown probe results fail closed until a later explicit lane earns them.
The useful lesson from USBGuard is the posture, not the Linux implementation: explicit allow/block/reject decisions against stable device attributes, with a default that blocks until a decision is made.

The first concrete execution floor is now narrower too: keep mount authority on the host, project the mounted tree into a disposable no-network jail, keep raw block-device nodes out of that jail in the first cut, require the host-side mount tuple `ro,nodev,nosuid,noexec,nosymfollow`, and keep the mounted tree inert so side-effect launch metadata stays bytes only instead of ambient instructions. The next ingest-walk cut is now fixed too: traversal stays physical and root-pinned beneath `/ingest`, the first admitted member kinds are regular files plus explicit directories only, symlink/device/FIFO/socket semantics fail closed, and hardlink topology stays out of scope in the first cut. The next naming cut is fixed too: admitted member paths normalize to relative-clean Unicode NFC text, normalization collisions fail closed, and the first cut performs no silent auto-rename or source-prefix repair. The next metadata cut is fixed too: reviewed/import identity stays path/kind/payload-first, owner/mode/mtime/xattr fidelity out of scope in the first cut, and any receiver-local metadata outcomes stay receiver-local realization detail rather than portable reviewed state. The next selection-width cut is fixed too: this first lane stays single-selected-subject only, direct multi-member review/import is out of scope in the first cut, and multiple outputs only arise as a deterministic consequence of processing that one selected subject. The next selected-subject-kind cut is fixed too: the selected subject stays regular-file-only in the first cut, and directories are not selectable import subjects in this lane. The next approval-continuity cut is fixed too: approval stays present-device-instance-only in the first cut, physical detach or lease end revokes it, and reattach requires a fresh grant even when serial or disk-ident hints look the same. The next attach-evidence cut is fixed too: the canonical `device.attach.receipt` for this lane carries a finite observed current-presence hint bundle (`ugen`/provider plus disk-ident or physical-path hints when available), explicitly marks those hints evidence-only and non-authoritative on reattach. The next capture-first cut is fixed too: once one selected regular file is chosen, the first non-browsing step is capture-first into `/work`, later operations consume the captured file rather than the live mounted path, and capture failure or digest mismatch fails closed. The next detach-early cut is fixed too: once that capture verifies, the host should end the removable-medium session and emit device.detach.receipt before later classify/scan/sanitize work continues, so later work no longer keeps live device authority around out of convenience. The next post-detach worker-reset cut is fixed too: later work then restarts in a fresh disposable worker with /ingest absent rather than reusing a worker that could still hold hidden references to the old mount. The next preserved-capture cut is fixed too: the verified capture remains exact evidence and sanitize output becomes a separate derivative from the preserved capture rather than an in-place rewrite of the captured subject. The next authoritative-store cut is fixed too: once that capture verifies, the exact preserved subject must commit into authoritative quarantine store before detach, and later work reads a read-only projection of the stored preserved capture rather than depending on disposable `/work` scratch authority. The next single-object projection cut is fixed too: after detach, later work receives only one preserved selected subject through a synthetic single-object projection or equivalent brokered handle and may not browse the authoritative quarantine-store namespace. The next digest-bound delivery cut is fixed too: that synthetic delivery must bind to the preserved selected subject digest before later operations begin, and the canonical receipt must record the binding rather than trusting the path alone. The next launcher-preopened delivery cut is fixed too: after that binding, later execution must stay on one launcher-preopened read-only object (or equivalent), the worker path stays compatibility-only plumbing, and the later worker may not reacquire the subject through broader path or authoritative-store lookup. The next broker-collected derivative-egress cut is fixed too: later worker output must leave through launcher-prepared disposable sink objects, worker outbox paths stay non-authoritative, and the launcher/broker must collect + remeasure those bytes before the canonical receipt names an authoritative derivative locator. The next single-declared-slot cut is fixed too: the later output surface now stays on one declared writable derivative slot, any receipt-visible derivative must come from that slot, and extra worker result surface stays out in the first lane. The next empty-write-only-slot cut is fixed too: that declared slot starts as a launcher-precreated empty regular file and keeps worker readback/truncate out. The next append-open-derivative-slot cut is fixed too: on FreeBSD seekable-file delivery, the launcher hands that sink over `O_APPEND`, keeps it append-only-protected while the worker runs, omits `CAP_READ`/`CAP_FTRUNCATE`/`CAP_FCNTL`, and treats any `CAP_SEEK` there as ballast rather than rewrite authority. The next capability-mode-entry cut is fixed too: the launcher or its approved shim enters capability mode before handing control to later tool mainline code, descendants inherit that mode and may not clear it, ambient absolute-path opens stay out after `cap_enter()`, and tools that cannot run on the preopened capability set stay out unless a later explicit wrapper/broker contract earns them. The next closed-world-descriptor-set cut is fixed too: after that boundary, the later worker inherits only the reviewed descriptor set, the launcher closes or spawn-closefroms every non-reviewed descriptor before handoff, `stdin` stays inert null/empty input only, and `stdout`/`stderr` stay launcher-owned observation channels or reviewed append-only log sinks instead of inherited parent-session surfaces (see `adrs/ADR-0337-removable-media-local-fallback-post-detach-reviewed-descriptor-set-stays-closed-world-and-stdio-is-launcher-owned.md`, `docs/747-removable-media-local-fallback-post-detach-reviewed-descriptor-set-stays-closed-world-and-stdio-is-launcher-owned.md`).

## How this fits the existing workstation boundary

For profile **B**, this decision composes directly with `ADR-0047`:

- the host owns raw HID, focus, and trusted prompts,
- general interactive apps are AppVM-first,
- and removable-media access is another brokered/device-domain crossing, not a reason to run general apps on the host.

So “open this file from a USB stick” should normally become:

1. detect/classify in the device domain,
2. attach read-only to a scan/import domain,
3. sanitize or import with origin labels,
4. hand the resulting object into the destination AppVM through portals/brokers.

That is more steps internally, but fewer trust ambiguities externally.

## How this fits A and D

### A) Fleet host

A fleet host should not silently become a “sometimes desktop” because a human plugged in a drive.
Local removable-media use is a narrow exception path:

- no automount into the host,
- explicit break-glass or maintenance workflow if policy allows,
- receipts bound into incident/support bundles,
- and preference for signed network paths or mirror kits over ad-hoc local copying.

### D) Appliance factory / regulatory

For regulated or offline factories, removable media is often real, not optional.
The correct move is not pretending it will disappear; it is forcing it into a stable ingest lane:

- quarantine/device domain or dedicated ingest station,
- signed kit / provenance verification,
- quarantine→promote into trusted channels,
- deterministic evidence retention and redaction.

## What remains open

The baseline is decided, but several implementation details remain open:

- how to detect “device-domain supported” hardware robustly,
- what the BSD-native local fallback authorization daemon/UI looks like,
- how remembered local approvals expire/review/revoke,
- and how integrated devices (Bluetooth radios, webcams, FIDO/smart-card readers) map onto the same posture without creating carve-outs.

Those belong in future RFC/ADR work, not in the baseline profile contract.

## Related docs

- `docs/411-product-profiles-as-compilation-target.md`
- `docs/412-product-profile-matrix.md`
- `docs/204-device-isolation-domains.md`
- `docs/207-input-authority-secure-attention-and-hid-risk.md`
- `docs/278-device-grants-and-devfs-rulesets.md`
- `docs/279-usb-quarantine-and-removable-media-workflow.md`
- `docs/280-origin-labels-and-quarantine-attributes.md`
- `docs/273-airgap-mirror-kits-and-sneakernet-updates.md`


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

## Profile posture: contract closure

For B and C local removable-media fallback, the ordinary lane now requires `schema-backed-positive-and-negative-fixture-guarded`. Profile-specific compatibility must not weaken `known-bad-authority-shapes-must-fail-validation`; a broader compatibility lane needs its own schema, red corpus, receipt posture, and backend-evidence downgrade semantics.

## r505 B/C local fallback evidence floor

B/C local fallback posture now includes `typed-freebsd-launch-evidence-positive-and-negative-fixture-guarded` with red-corpus policy `known-bad-freebsd-launch-evidence-shapes-must-fail-validation`. The first admitted worker is still a single-object, post-detach, storage-only lane, but its FreeBSD backend evidence must now be typed and negative-tested before derivative receipt visibility.


## r506 B/C recovery evidence floor

B/C local fallback posture now includes `typed-post-detach-recovery-evidence-positive-and-negative-fixture-guarded` with red-corpus policy `known-bad-recovery-evidence-shapes-must-fail-validation`. The lane remains single-object and post-detach, but ordinary success also requires typed recovery evidence for scratch cleanup, worker-tree reap, output sealing, and no media path reopen after interruption.

Last updated: 2026-05-21r506
