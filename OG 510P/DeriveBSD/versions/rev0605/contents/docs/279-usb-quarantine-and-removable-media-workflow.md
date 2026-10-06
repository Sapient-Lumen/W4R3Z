# USB quarantine + removable media workflow (Qubes USB-qubes lessons)

Removable media is the universal footgun:
- a hostile USB device can attack the USB stack and drivers
- a “normal” USB stick is an untrusted file container (malicious PDFs, exploit documents, weird filesystem images)
- automount makes it all ambient and invisible

DeriveBSD should ship a *boring, safe default*:
- **no automount into the trusted domain**
- USB controller stacks are **quarantined** (device isolation domain)
- using a device requires an explicit **lease grant** + evidence
- opening files from removable media should route through the **sanitization portal** (`docs/267-sanitization-portal-and-disposable-sandboxes.md`)
- imported files should carry **origin labels + quarantine metadata** (`docs/280-origin-labels-and-quarantine-attributes.md`)

See also the accepted profile baseline: `adrs/ADR-0048-removable-media-and-usb-posture-by-profile.md`, `docs/458-removable-media-and-usb-posture-by-profile.md`.

Prior art worth stealing:
- Qubes OS: isolate USB stacks/drivers in an unprivileged VM (`sys-usb`) and attach devices to other domains on demand.  
  References:
  - https://doc.qubes-os.org/en/latest/user/how-to-guides/how-to-use-usb-devices.html
  - https://doc.qubes-os.org/en/latest/developer/system/architecture.html

## Default posture ("greenfield win")

### 1) USB controllers belong to a device domain
- Create one (or more) **USB quarantine domains** that own USB controllers (passthrough).
- The trusted domain never loads USB device drivers.
- Device domains have *no secrets* and minimal connectivity.

See also: `docs/204-device-isolation-domains.md`.

### 2) “Attach” is a lease with constraints
When a USB device appears:
- it is classified (`device.profile`) with risk tags: removable, hid, firmware-opaque, etc.
- it is not usable elsewhere until a `device.attach.grant` exists

This keeps “who had the device when” answerable in incident bundles.

### 3) Default workflow for files: sanitize, then import
For USB sticks and other file media:

1) Attach device **read-only** to a disposable “media-scan” domain.
2) Use the sanitization portal to export a sanitized copy into a safe staging area.
3) Only then import into a persistent domain, emitting a `content.import.receipt` that records whether provenance metadata was preserved, rehydrated, or laundering-suspected.

This is the “dangerous documents” workflow made first-class.

### 4) Default workflow for block use: constrained and visible
For “I need to copy files / do a backup”:
- attach partitions (not whole disk) when possible
- prefer read-only by default
- require explicit writable grants + TTL
- emit attach/detach receipts and include them in support bundles

### 5) Airgap updates: removable media feeds quarantine→promote
USB is a common airgap transport. DeriveBSD already has:
- signed mirror kits + quarantine→promote (`docs/273-airgap-mirror-kits-and-sneakernet-updates.md`)

The USB posture should make the safe path easy:
- mount kit media in a quarantine domain
- import kit into quarantine store
- verify signatures + freshness
- then promote into the trusted update channel

## Imperfect-hardware fallback stays storage-only and session-scoped

Not every B/C machine will have clean controller isolation.
The archive now fixes the first honest fallback in `adrs/ADR-0313-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md` and `docs/723-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md`:

- the fallback is **storage-only** for removable-media ingest/export,
- it is **session-scoped** with fresh authorization and receipts rather than remembered ambient allow,
- it remains **read-only-first** and **quarantine-first**,
- it allows **no raw HID** in the fallback lane,
- and it does **not** reopen generic USB passthrough, network dongles, smart-card/FIDO, serial/debug, webcam, or microphone handling under the same local-policy lane.

The first implementation target is therefore small and spec-shaped already:
`device.profile` → `device.attach.grant` / `device.attach.receipt` → **host-side `fstyp` probe against a finite allowlist** → **host-controlled read-only mount** → minimal/block-empty `devfs.view.plan` plus read-only `mount.view` for a **disposable no-network jail** → **selected-subject capture + digest verification** → `device.detach.receipt` → `content.import.receipt` or verified offline-kit ingest.

That is the new first-cut execution floor from `docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md` and `docs/725-removable-media-local-fallback-fstyp-probed-filesystem-admission-stays-finite.md`: the ingest jail works on a mounted tree, not on raw block-device nodes, and the host admits only `msdosfs`, `exfat`, `ufs`, and `cd9660` in this first local-fallback lane. `ext2fs`, `ntfs`, `zfs`, `geli`, and unknown probe results fail closed until a later explicit lane earns them. The next cut is now explicit too: the host-side mount must realize the required hardening tuple `ro,nosuid,noexec,nosymfollow,untrusted`, the mounted tree stays inert input only, and side-effect launch metadata on the medium stays bytes rather than ambient instructions (`docs/726-removable-media-local-fallback-mounted-trees-stay-inert-and-mount-hardening-is-fail-closed.md`). The next ingest-walk cut is now explicit too: traversal stays physical and root-pinned beneath `/ingest`, the first admitted member kinds are regular files plus explicit directories only, symlink/device/FIFO/socket semantics fail closed, and hardlink topology stays out of scope in the first cut (`docs/727-removable-media-local-fallback-ingest-walk-stays-physical-root-pinned-and-regular-files-plus-explicit-directories-only.md`). The next naming cut is explicit too: admitted member paths normalize to relative-clean Unicode NFC text, normalization collisions fail closed, and the first cut performs no silent auto-rename or source-prefix repair (`docs/728-removable-media-local-fallback-member-paths-stay-relative-clean-nfc-and-collision-fail-closed.md`). The next metadata cut is explicit too: reviewed/import identity stays path/kind/payload-first, owner/mode/mtime/xattr fidelity out of scope in the first cut, and any receiver-local metadata outcomes stay receiver-local realization detail rather than portable reviewed state (`docs/729-removable-media-local-fallback-keeps-owner-mode-mtime-xattr-fidelity-out-of-the-first-lane.md`). The next selection-width cut is explicit too: this first lane stays single-selected-subject only, direct multi-member review/import is out of scope in the first cut, and multiple outputs only arise as a deterministic consequence of processing that one selected subject (`docs/730-removable-media-local-fallback-first-lane-stays-single-selected-subject-only.md`). The next selected-subject-kind cut is explicit too: the selected subject stays regular-file-only in the first cut, and directories are not selectable import subjects in this lane (`docs/731-removable-media-local-fallback-selected-subject-stays-regular-file-only-in-the-first-cut.md`). The next approval-continuity cut is explicit too: approval stays present-device-instance-only in the first cut, physical detach or lease end revokes it, and reattach requires a fresh grant even when serial or disk-ident hints look the same (`docs/732-removable-media-local-fallback-approval-stays-present-device-instance-only-and-reattach-requires-fresh-grant.md`). The next attach-evidence cut is explicit too: the canonical `device.attach.receipt` for this lane carries a finite observed current-presence hint bundle (`ugen`/provider plus disk-ident or physical-path hints when available), marks those hints evidence-only, and keeps same-hints-on-reattach non-authoritative (`docs/733-removable-media-local-fallback-attach-receipts-carry-observed-hints-and-keep-them-evidence-only.md`). The next capture-first cut is explicit too: once one selected regular file is chosen, the first non-browsing step captures that exact subject into `/work`, later operations consume the captured file rather than the live mounted path, and capture failure or digest mismatch fails closed (`docs/734-removable-media-local-fallback-selected-subject-processing-stays-capture-first-and-later-ops-consume-the-capture.md`). The next detach-early cut is explicit too: once that capture verifies against the planned subject digest, the host should end the removable-medium session and emit `device.detach.receipt` before later classify/scan/sanitize work continues (`docs/735-removable-media-local-fallback-verified-capture-allows-early-detach-and-later-ops-stay-device-independent.md`). The next post-detach execution cut is explicit too: later classify/scan/sanitize work must restart in a fresh disposable worker after verified capture and detach, with `/ingest` absent and no inherited live medium references carried over from the pre-detach worker (`docs/736-removable-media-local-fallback-post-detach-later-ops-require-a-fresh-worker-with-no-live-ingest-references.md`). The next preserved-capture cut is explicit too: after that restart, the verified capture remains exact evidence, later operations may not rewrite it in place, and sanitize output is a separate derivative from the preserved capture (`docs/737-removable-media-local-fallback-preserves-the-verified-capture-and-forbids-in-place-rewrite-by-later-ops.md`). The next authoritative-store cut is explicit too: once capture verifies, that exact captured subject must commit into authoritative quarantine store before detach, and later work must read a read-only projection of the stored preserved capture rather than keep `/work/capture/...` as hidden lasting authority (`docs/738-removable-media-local-fallback-verified-capture-commits-into-authoritative-quarantine-store-before-detach.md`). The next single-object projection cut is explicit too: after detach, later work may receive only a synthetic single-object projection or equivalent brokered handle for that preserved capture, and it must not receive a browseable authoritative-store mount or namespace (`docs/739-removable-media-local-fallback-post-detach-preserved-capture-delivery-stays-single-object-and-store-opaque.md`). The next digest-bound projection cut is explicit too: that later worker-visible delivery must match the preserved selected subject digest before later ops begin, and the canonical receipt must say so rather than treating the synthetic path as self-authenticating (`docs/740-removable-media-local-fallback-post-detach-single-object-delivery-stays-digest-bound-and-receipt-evidenced.md`). The next launcher-preopened delivery cut is explicit too: after that binding, later execution must stay on one launcher-preopened read-only object (or equivalent), any worker-visible path stays compatibility-only plumbing, and the later worker may not reacquire the subject through broader path or authoritative-store lookup (`docs/741-removable-media-local-fallback-post-detach-delivery-stays-launcher-preopened-read-only-and-path-reopen-stays-out.md`). The next broker-collected derivative-egress cut is explicit too: later worker output must leave through launcher-prepared disposable sink objects, `/work/output/...` stays non-authoritative execution plumbing, and the launcher/broker must collect + remeasure those bytes before the canonical receipt names the derivative authoritatively (`docs/742-removable-media-local-fallback-post-detach-derivative-egress-stays-broker-collected-and-worker-outbox-paths-stay-nonauthoritative.md`). The next single-declared-slot cut is explicit too: the later worker now gets only one declared writable derivative slot, any receipt-visible derivative must come from that slot, and extra worker result surface stays out in the first lane (`docs/743-removable-media-local-fallback-post-detach-derivative-egress-stays-single-declared-slot-and-no-extra-worker-result-surface.md`). The next empty-write-only-slot cut is explicit too: that declared slot starts as a launcher-precreated empty regular file and keeps worker readback/truncate out (`docs/744-removable-media-local-fallback-post-detach-derivative-slot-stays-empty-writeonly-and-no-readback-or-truncate.md`). The next append-open-derivative-slot cut is explicit too: because this first lane still uses a seekable regular-file sink on FreeBSD, the launcher now hands that sink over already opened `O_APPEND`, keeps it append-only-protected while the worker runs, omits `CAP_READ`/`CAP_FTRUNCATE`/`CAP_FCNTL`, and treats any `CAP_SEEK` there as seekable-file ballast rather than rewrite authority (`docs/745-removable-media-local-fallback-post-detach-derivative-slot-stays-append-open-and-append-only-protected-on-seekable-file-delivery.md`). The next capability-mode-entry cut is explicit too: the launcher or its approved shim enters capability mode before handing control to later tool mainline code, descendants inherit that mode and may not clear it, ambient absolute-path opens stay out after `cap_enter()`, and tools that cannot run on the preopened capability set stay out unless a later explicit wrapper/broker contract earns them (`docs/746-removable-media-local-fallback-post-detach-later-tool-code-enters-capability-mode-before-mainline-and-stays-there.md`). The next closed-world-descriptor-set cut is explicit too: after that boundary, the later worker inherits only the reviewed descriptor set, the launcher closes or spawn-closefroms every non-reviewed descriptor before handoff, `stdin` stays inert null/empty input only, and `stdout`/`stderr` stay launcher-owned observation channels or reviewed append-only log sinks instead of inherited parent-session surfaces (`docs/747-removable-media-local-fallback-post-detach-reviewed-descriptor-set-stays-closed-world-and-stdio-is-launcher-owned.md`).

## Footguns to design around (be explicit)

- “My system boots from USB”: do not isolate the boot media controller into a device domain that would break boot.
- “I need a keyboard at early boot”: HID/input is special-danger; handle via secure attention / trusted path (`docs/207-input-authority-secure-attention-and-hid-risk.md`) and avoid making early-boot input depend on untrusted USB domains.

## Suggested cross-links
- device grants + /dev authority: `docs/278-device-grants-and-devfs-rulesets.md`
- device domains: `docs/204-device-isolation-domains.md`
- safe untrusted files: `docs/267-sanitization-portal-and-disposable-sandboxes.md`
- airgap kits: `docs/273-airgap-mirror-kits-and-sneakernet-updates.md`


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

## Post-detach contract closure

The first local removable-media fallback now carries `schema-backed-positive-and-negative-fixture-guarded` in addition to the earlier persistent-state and no-network posture strings. The user-visible workflow should treat a derivative as ordinary-lane eligible only when the post-detach worker contract digest is present, backend evidence is `receipt-must-bind-freebsd-launch-evidence-to-contract`, and known-bad shapes from the red corpus remain rejected.

## r505 post-detach launch evidence

The local fallback now carries `typed-freebsd-launch-evidence-positive-and-negative-fixture-guarded` and `sha256:4949494949494949494949494949494949494949494949494949494949494949` after the r504 contract closes. A post-detach derivative receipt is not visible until the FreeBSD launch evidence validates against `spec/removable.media.local.post_detach.launch.evidence.schema.json` and binds the fd table, Capsicum entry, Casper absence, network absence, scratch cleanup, and output-slot identity back to the reviewed contract.


## r506 post-detach recovery evidence

The local fallback now carries `typed-post-detach-recovery-evidence-positive-and-negative-fixture-guarded` and `sha256:5050505050505050505050505050505050505050505050505050505050505050` after the r505 launch evidence. A post-detach derivative receipt is not visible until recovery evidence validates against `spec/removable.media.local.post_detach.recovery.evidence.schema.json` and proves cleanup/key-discard, worker-tree reap, output-slot sealing, and no media path reopen after interruption.

Last updated: 2026-05-21r506
