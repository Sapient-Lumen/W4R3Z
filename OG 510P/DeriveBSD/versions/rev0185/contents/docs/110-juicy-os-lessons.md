# Juicy lessons from other OSes (and bespoke ecosystem ideas)

DeriveBSD is greenfield enough to **bake in operational ergonomics** that older ecosystems only bolted on later.

This file is a *high-signal index* of ideas worth stealing. Each item is intentionally short, with deeper discussion in RFCs.

## 1) Packaged base system ("pkgbase") as explicit sets

FreeBSD **15.0-RELEASE** (2025-12-02) added a *packaged base system* option (“pkgbase”): the base system can be installed and managed via `pkg(8)`.
This suggests a DeriveBSD-native equivalent: **base as derivable sets** (kernel/userland/toolchain split) with signatures and rollback.

See: `docs/111-packaged-base-pkgbase.md`, RFC-0079.

## 2) Health-gated updates and automatic rollback

Atomic switch is necessary but not sufficient: the system must confirm a new generation is *healthy* before committing.

See: `docs/112-health-gated-updates.md`, `docs/241-boot-try-counters-and-boot-assessment.md`, `docs/335-boot-assessment-greenboot-and-health-gated-rollback.md`, `spec/boot.health.gate.policy.schema.json`, RFC-0080.

## 3) Signed, revertible patchsets (syspatch-style)

OpenBSD’s `syspatch` is a model for **small, signed, revertible base patches** that are operationally simple.
DeriveBSD can provide a similar “patchset artifact” lane that remains explainable and policy-bound.

See: `docs/113-syspatch-style-patchsets.md`, RFC-0081.

## 4) Services as a derived dependency graph (SMF lessons)

Illumos SMF treats services as first-class objects with explicit dependencies and introspection.
DeriveBSD can keep `rc.d` as an activation backend but still derive a **service graph manifest** for explainability and review.

See: `docs/114-service-manifests-smf-lessons.md`, RFC-0082.

Also steal the *ops* part: explicit service states (`online/offline/degraded/maintenance`) and restart ownership, exposed as evidence (`svc.snapshot`/`svc.event`).
See: `docs/214-service-supervision-health-as-evidence.md`, RFC-0149.

## 5) Compartmentalize privileged subsystems (Qubes lessons)

MicroVM-first makes it cheap to isolate not just workloads, but *privileged subsystems* (networking, fetch, update, secrets delivery).

See: `docs/115-compartmentalized-control-planes.md`, RFC-0083.
## 5.1) Disposable workspaces (TemplateVM / DisposableVM lessons)

Qubes’ TemplateVM/DisposableVM model makes “do risky work in a disposable compartment” the default.
Translate this into DeriveBSD as **template digests + leased disposable activations + receipted exports**, so sessions are isolated *and* explainable.

See: `docs/421-disposable-workspaces-and-template-microvms.md`.


## 5.2) Split secrets brokers (Split GPG / Split SSH lessons)

Keep long-lived private keys in a **more trusted, network-isolated compartment** and let risky app compartments request *bounded* crypto operations via a policy-governed broker (receipts everywhere).

Translate this into DeriveBSD as a Tier C optional lane: vault compartment + broker leases + `crypto.op.request/receipt`, with interop via Adapter→Shadow→Replace.

See: `docs/437-split-secrets-brokers.md`.


## 6) Witness rebuilders and deep diffs (repro-builds practice)

Treat builders as hostile by default. Optionally require independent rebuild attestations (“witnesses”) and use deep diffs to explain divergence.

See: `docs/116-witness-rebuilders-diffoscope.md`, RFC-0084.

## 6.1) Standard attestations as a killable adapter lane (in-toto / SLSA provenance)

Many downstream ecosystems now expect *standard* attestations (in-toto Statements, often DSSE wrapped) and SLSA provenance predicates.
DeriveBSD already emits richer receipts; the high-leverage move is **interop without forking**: export a conservative projection behind `export.policy` and a killable adapter lane, while keeping DeriveBSD evidence as the source of truth.

DeriveBSD translation: treat in-toto/SLSA as an **Adapter→Shadow→Replace** lane, record exports as a typed report (`attestation.adapter.intoto.report`), and keep the adapter killable via `adapter.kill.policy`.

See: `docs/454-intoto-slsa-adapter-lane.md`, `spec/attestation.adapter.intoto.report.schema.json`.


## 7) "Pledge/unveil" as a mindset (API ergonomics matter)

## 7.1) Promise profiles as first-class derived artifacts

The missing piece is a **single review surface** that compiles into jails + Capsicum rights + portals.
Make it a typed artifact and wire it into svcdb so authority changes show up in diffs.

See: `docs/232-service-promise-profiles.md`, `docs/271-promise-profile-vocabulary-and-lint.md`, RFC-0166.

OpenBSD’s pledge/unveil are notable less for novelty and more for how easy they are to apply everywhere.
DeriveBSD should aim for similarly low-friction **capsicum-first profiles** and “preopened handle” workflows.

See: `docs/117-pledge-unveil-mindset.md`, RFC-0085.

## 7.2) “Complain mode” learning loops (make least-authority cheap)

Pledge/unveil’s biggest operational win is not only that profiles are small — it’s that they’re *iterable*.
Other ecosystems leaned into this with explicit learn→review→enforce tooling:

- AppArmor: `aa-genprof` / `aa-logprof` propose profile updates from audit logs.
- SELinux: `audit2allow` generates candidate rules from denials.
- Seccomp: trace syscalls and generate a whitelist profile (OCI hooks exist).

DeriveBSD should bake in the equivalent: **run a service in observation mode and emit a candidate promise-profile patch** as a diffable artifact.

See: `docs/326-learned-promise-profiles-and-observation-mode.md`.

## 8) Unprivileged + distributed bulk builds (pkgsrc pbulk lessons)

Pkgsrc’s bulk build tooling supports unprivileged builds and distributed workers.
This maps well to DeriveBSD builder pools, action caching, and witness rebuilders.

See: `docs/118-distributed-builds-pbulk.md`, RFC-0086.

## 9) Store/image distribution beyond binary caches (casync, CernVM-FS)

Some ecosystems distribute *filesystems* rather than “packages” or “layers”, with content-addressed chunking and HTTP/CDN friendliness.
These ideas fit DeriveBSD’s CAS-first posture.

See: `docs/119-casync-cvmfs-distribution.md`, RFC-0087.

## 10) “Image first” updates + client anti-rollback (OSTree / Bottlerocket / TUF)

Several production OSes avoid “mutate packages in place” and instead **deploy whole filesystem trees** with atomic boot-time switching and rollback.

DeriveBSD already has ZFS BEs and atomic generation switching; the extra lesson is:
- clients must defend against **freeze/rollback attacks** even when artifacts are signed (TUF-style expiry + monotonic versions)
- updates should be **health-gated** and can auto-rollback on boot failure

References:
- OSTree atomic upgrades/rollback: https://ostreedev.github.io/ostree/atomic-upgrades/
- Bottlerocket update system uses TUF and supports rollback: https://github.com/bottlerocket-os/bottlerocket
- TUF spec (freeze/rollback defenses): https://theupdateframework.github.io/specification/latest/

See: `docs/61-channel-metadata-tuf-inspired.md`, `docs/62-replay-rollback-freeze.md`, `docs/112-health-gated-updates.md`.

## 10.1) Stateless roots + explicit persistence sets (impermanence)

Immutable generations stay explainable only if **persistence is declared**.
NixOS’ “impermanence” and OSTree’s `/etc` drift tooling both point at the same discipline: keep the root discardable, and list exactly what survives.

Translate this into DeriveBSD as a small, diffable registry: `persist.set.registry` (what mounts and paths are allowed to persist), optionally enabling an **ephemeral root** mode per profile.

References:
- NixOS impermanence module: https://github.com/nix-community/impermanence
- “Erase your darlings” (stateless ZFS roots): https://grahamc.com/blog/erase-your-darlings
- OSTree `config-diff` (diff /etc vs defaults): https://ostreedev.github.io/ostree/man/ostree-admin-config-diff.html
- systemd-tmpfiles (declared path lifecycles): https://www.freedesktop.org/software/systemd/man/latest/systemd-tmpfiles.html

See: `docs/423-persist-sets-and-ephemeral-root.md`, `docs/217-state-datasets-and-migrations-as-evidence.md`.


## 10.2) /etc drift diffs as a stable review surface (OSTree config-diff + etcupdate)

Even when the base system is derived, `/etc` tends to become the place operators patch during incidents.
If those edits are not made visible as a **diffable surface**, reproducibility and provenance erode quietly over time.

Steal the shape: treat `/etc` drift as a first-class diff artifact that can be attached to drift bundles, promotion gates, and support bundles.

References:
- OSTree `ostree admin config-diff` (diff /etc vs defaults): https://ostreedev.github.io/ostree/man/ostree-admin-config-diff.html
- FreeBSD `etcupdate(8)` (disciplined /etc merge during base upgrades): https://man.freebsd.org/cgi/man.cgi?query=etcupdate&sektion=8

See: `docs/427-etc-config-diff-as-a-drift-surface.md`.


## 11) Kernel-enforced “verified execution” as a hard stop (NetBSD veriexec / FreeBSD MAC/veriexec)

Immutable intent gets stronger if the kernel refuses to execute or load **unexpected bytes**.
NetBSD’s Veriexec and FreeBSD’s MAC/veriexec work in this direction.

References:
- NetBSD Veriexec guide chapter: https://www.netbsd.org/docs/guide/en/chap-veriexec.html
- FreeBSD MAC/veriexec review trail: https://reviews.freebsd.org/D8554
- Linux fs-verity docs (Merkle-tree per-file authenticity, similar goal): https://docs.kernel.org/filesystems/fsverity.html

See: `docs/103-runtime-verified-execution.md`, `docs/233-verified-execution-as-evidence.md`, `docs/53-verified-exec-mac-veriexec.md`, `docs/442-exec-verify-policy-diff-as-review-surface.md`.

DeriveBSD translation: treat verified-exec posture as a typed policy object and make drift mechanically reviewable via `exec.verify.policy.diff` (Registry→Diff→Gate), so disabling/relaxing enforcement or adding exceptions can be policy-gated without forks.

## 12) Observability as part of “explainability” (DTrace)

“Why did this change?” and “what executed?” sometimes requires runtime evidence.
FreeBSD ships DTrace for production-safe dynamic tracing.

Reference:
- FreeBSD Handbook: DTrace: https://docs.freebsd.org/en/books/handbook/dtrace/

See: `docs/120-observability-explainability-dtrace.md`, `docs/52-host-auditing-openbsm.md`.

## 13) Jailed hypervisor workers (defense in depth)

Running bhyve itself inside a jail is an underused but powerful pattern: even if the VMM process is compromised, its **ambient authority** can be sharply reduced (filesystem view, network view, sysctls, device nodes).

See: `docs/121-jailed-hypervisor-workers.md`.

## 14) “System extensions” for immutable bases (debuggability without drift)

Immutable OSes tend to grow a “how do I debug this without mutating it?” problem.
systemd’s *system extension images* are a clean answer: attach a signed, read-only extension image to temporarily extend `/usr` without changing the base.

See: `docs/122-system-extensions.md`.

## 15) Ignition-style *first boot* provisioning (disk mutations happen once)

Instead of rerunning config management forever, Ignition provisions disk state once (initramfs), then hands off to the immutable runtime.
This pattern fits DeriveBSD’s “images are immutable; injection is explicit” contract.

See: `docs/123-ignition-style-firstboot.md`.

## 16) virtio-9p as a *restricted* host↔guest file channel (optional)

bhyve supports virtio-9p (VirtFS), which can provide a deterministic read-only config channel or a controlled “debug view” into host artifacts.
Guest support can be uneven, so it must remain optional and policy-gated.

See: `docs/124-virtio-9p-injection-channel.md`.

## 17) Per-jail hardening knobs (HardenedBSD secadm mindset)

HardenedBSD’s approach to controlling exploit-mitigation knobs *per jail* is a good fit for DeriveBSD’s policy engine: apply hardening settings as a policy result, scoped to a compartment.

See: `docs/125-hardening-knobs-per-jail.md`.

## 18) ZFS send/recv as a distribution lane (dataset-native transport)

ZFS-native systems can ship complete boot environments or base datasets as replication streams.
If treated as signed artifacts and applied via a quarantine/promote flow, this becomes a clean “whole-tree” transport.

Reference:
- FreeBSD `poudriere-image` supports `zfs+send` streams including boot environments: https://man.freebsd.org/poudriere-image

See: `docs/126-zfs-send-distribution.md`.

### 18.1) Resumable receives + continuous replication (resume tokens)

ZFS has a surprisingly good story for *resuming* interrupted replication: `zfs receive -s` saves partial state and exposes a `receive_resume_token`, and `zfs send -t <token>` can resume without restarting from zero (and `zfs receive -A` can abort saved partial state).

See: `docs/413-zfs-replication-resume-bookmarks-and-receipted-backups.md`.

## 19) Uptane’s “director” role (bytes vs deployment decisions)

TUF answers “are these bytes authentic?”; Uptane adds a separate signed role that answers “what should *this node* install?”.
That separation matches DeriveBSD’s Plan+policy model and helps limit blast radius during staged rollouts and incidents.

Reference:
- Uptane standard: https://uptane.org/docs/2.1.0/standard/uptane-standard

See: `docs/127-uptane-director-targets.md`.

## 20) SmartOS imgadm/IMGAPI image ecosystem (templates + metadata)

SmartOS treats images as first-class templates with metadata, managed with `imgadm` and backed by an Image API.
DeriveBSD should similarly standardize a signed “image descriptor” schema that binds bytes to runtime/policy metadata.

References:
- SmartOS “Managing Images”: https://docs.smartos.org/managing-images/
- IMGAPI docs: https://images.smartos.org/docs/

See: `docs/128-image-registry-imgadm-lessons.md`.


## 21) Template microVMs and disposable instances (Qubes disk model)

Qubes' “template + private + volatile” pattern is a strong fit for microVM-first systems:
- centralized updates (update template → many VMs inherit)
- cheap disposables (no private disk)
- clearer blast radius between base bytes vs state bytes

References:
- Qubes template implementation (multiple block devices): https://doc.qubes-os.org/en/latest/developer/system/template-implementation.html
- Qubes templates overview (centralized updates): https://doc.qubes-os.org/en/latest/user/templates/templates.html

See: `docs/129-template-microvms-and-disposables.md`.

## 22) ZFS bookmarks + redaction bookmarks (obscure but useful)

OpenZFS bookmarks let incremental replication continue even after snapshot GC, and redaction bookmarks enable a controlled “sanitized send” stream that omits specific blocks.

References:
- zfs-bookmark(8): https://openzfs.github.io/openzfs-docs/man/master/8/zfs-bookmark.8.html
- zfs-redact(8): https://openzfs.github.io/openzfs-docs/man/master/8/zfs-redact.8.html

See: `docs/130-zfs-bookmarks-and-redaction.md`.


## 23) Lightweight transparency logs (Sigsum)

Rekor-style transparency is powerful but can be heavyweight.
Sigsum is a more minimal “key-usage transparency” system: clients accept signatures only when they
can prove the signature is **logged** (so monitors can detect unexpected signing events).

References:
- Sigsum overview: https://www.sigsum.org/

See: `docs/131-sigsum-lightweight-transparency.md`.

Also consider using transparency logs for **export events** (what left the system), not just signing events.
See: `docs/254-export-transparency-logs.md`.

## 24) Supply-chain ledger receipts (SCITT)

If DeriveBSD provenance/attestations are published into transparent registries and clients can require
receipts, targeted distribution and after-the-fact tampering become harder to hide.
The IETF SCITT effort defines an architecture for this interoperability.

References:
- IETF SCITT WG: https://datatracker.ietf.org/group/scitt/about/

See: `docs/132-scitt-ledger-receipts.md`.

## 25) “Bootable containers” as a host transport (bootc)

Bootc applies transactional updates to host OS trees using OCI images as a transport.
DeriveBSD can adopt the best part: **host generations import/export over OCI** while keeping
ZFS boot environments and DeriveBSD verification semantics.

References:
- bootc overview: https://bootc-dev.github.io/bootc/

See: `docs/133-bootable-oci-host-images-bootc-lessons.md`.

## 26) Declarative build pipelines for high-assurance images (apko/melange)

To keep the build TCB small, it can be valuable to offer a “restricted recipe lane” where build steps are
typed, explicit, and policy-checkable, instead of “arbitrary shell”. apko/melange/Wolfi are strong prior art.

References:
- apko repo (reproducible-by-default image builder): https://github.com/chainguard-dev/apko
- Wolfi overview: https://edu.chainguard.dev/open-source/wolfi/overview/

See: `docs/134-declarative-image-pipelines-apko-melange.md`.


## 27) Policy-governed cross-compartment RPC (qrexec lessons)

Qubes uses qrexec to enable strictly mediated RPC between isolated domains, with a deny-by-default policy language.
This is strong prior art for DeriveBSD control-plane crossings (host↔microVM, compartment↔compartment).

References:
- qrexec overview: https://doc.qubes-os.org/en/latest/developer/services/qrexec.html
- qrexec policy docs: https://dev.qubes-os.org/projects/qubes-core-qrexec/en/stable/qrexec-policy.html

See: `docs/135-qrexec-style-rpc-policy.md`.

## 28) Standardized builder pools + CAS (Remote Execution API lessons)

Build ecosystems converged on a useful split: content-addressed blobs/trees (CAS) + action-result caching + remote execution.
This aligns directly with DeriveBSD's hostile-builder posture and witness rebuilding.

References:
- Remote Execution API: https://github.com/bazelbuild/remote-apis
- REAPI v2 proto: https://github.com/bazelbuild/remote-apis/blob/main/build/bazel/remote/execution/v2/remote_execution.proto

See: `docs/136-remote-execution-api-builder-pools.md`.

## 29) Anti-rollback at activation time (Verified Boot rollback indices)

TUF-style metadata reduces freeze/rollback attacks at the repo layer; some OSes also harden the boot/slot layer with monotonic rollback indices, preventing downgrade to known-vulnerable images.

References:
- Verified Boot + rollback protection: https://source.android.com/docs/security/features/verifiedboot
- Boot flow note: https://source.android.com/docs/security/features/verifiedboot/boot-flow

See: `docs/137-anti-rollback-rollback-index.md`.

## 30) Offline signed update bundles (RAUC/fwup lessons)

A single-file, signed update bundle is a practical lane for air-gapped or constrained environments, without weakening the local verification story.

References:
- RAUC basics: https://rauc.readthedocs.io/en/latest/basic.html
- fwup overview (signed ZIP update archives; A/B scenarios): https://github.com/fwup-home/fwup

See: `docs/138-offline-signed-update-bundles.md`.

## 31) Precomputed deltas for bandwidth + offline update (OSTree static deltas)

OSTree's static deltas are precomputed, self-contained delta artifacts between commits that improve network efficiency and support offline transport. This is a useful pattern to map onto DeriveBSD's CAS/ZFS/OCI transports.

References:
- OSTree static deltas: https://ostreedev.github.io/ostree/copying-deltas/
- RHEL for Edge note on static deltas: https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/composing_installing_and_managing_rhel_for_edge_images/creating-and-managing-ostree-image-updates_composing-installing-managing-rhel-for-edge-images

See: `docs/139-bandwidth-efficient-deltas.md`.

## 32) Capability routing as access control (Fuchsia lessons)

Fuchsia’s component model treats **capability routing** as the primary access-control mechanism:
components are sandboxed, and access is granted only through explicit routes.
This maps cleanly onto DeriveBSD’s goal of making authority **diffable** and **explainable**.

References:
- Fuchsia capabilities concept: https://fuchsia.dev/fuchsia-src/concepts/components/v2/capabilities
- Fuchsia principles (explicit routing): https://fuchsia.dev/fuchsia-src/contribute/contributing-to-cf/original_principles

See: `docs/140-capability-routing-manifests.md`, RFC-0092.

## 33) Build records (`.buildinfo`) to make witness rebuilding tractable

Debian’s `.buildinfo` files are a concrete mechanism for recording build environment details so
independent rebuilders can attempt bit-for-bit reproduction.

References:
- Debian buildinfo files: https://wiki.debian.org/ReproducibleBuilds/BuildinfoFiles
- reproduce.debian.net: https://reproduce.debian.net/

See: `docs/141-build-records-buildinfo-and-rebuilders.md`, RFC-0093.

## 34) Trustworthy time as an input (Roughtime lessons)

Update systems that use expiry/validity windows need *time* — and time is a common attacker lever (freeze/rollback-by-clock).
Roughtime provides verifiable “rough time” samples, useful as a policy-governed input for high-assurance channels.

Reference:
- IETF Roughtime draft: https://datatracker.ietf.org/doc/draft-ietf-ntp-roughtime/

See: `docs/142-trustworthy-time-roughtime.md`.

Drift control (DeriveBSD wiring):
- Treat `time-source-policy` as a signed posture object and make changes mechanically reviewable via `time.source.policy.diff` (attach to `drift.bundle` when the active policy digest changes).

## 35) Resource controls as a blast-radius boundary (rctl/racct/cpuset)

DoS-by-resource-exhaustion is part of the hostile-builder threat model.
FreeBSD provides `rctl` (including per-jail constraints) and `cpuset` for CPU/memory-domain isolation.
DeriveBSD should derive budgets from policy and treat them as evidence-bearing facts.

References:
- FreeBSD Handbook (resource limits; rctl supports jails): https://docs.freebsd.org/en/books/handbook/security/
- rctl(8): https://man.freebsd.org/rctl
- cpuset(1): https://man.freebsd.org/cpuset

See: `docs/143-resource-controls-rctl-racct-cpuset.md`.

## 36) Routing isolation with multiple FIBs (setfib)

Filtering (pf) and routing are different levers.
FreeBSD FIBs allow separate routing tables per process, making it easy to force high-risk subsystems (fetch/build/update) to egress through dedicated gateways or blackholes.

References:
- setfib(1): https://man.freebsd.org/setfib
- setfib(2): https://man.freebsd.org/setfib.2

See: `docs/144-routing-isolation-fibs-setfib.md`.

## 37) Optional unikernel lane (Solo5/rump lessons)

Some workloads benefit from *smaller-than-a-full-OS* payloads: unikernels/library-OS images that declare exactly what resources they need.
Solo5's “tender” concept (explicit resource declaration + host-side loader/mediator) and NetBSD's rump-kernel tooling (kernel components in userspace) are strong prior art.

References:
- Solo5 architecture: https://github.com/Solo5/solo5/blob/main/docs/architecture.md
- NetBSD rump tutorial/sysproxy: https://www.netbsd.org/docs/rump/sptut.html , https://www.netbsd.org/docs/rump/sysproxy.html

See: `docs/145-unikernel-lane-rump-solo5.md`.

## 38) ZFS native encryption with key-use evidence (dataset-level at-rest protection)

OpenZFS dataset encryption is a useful primitive for per-workload state and secret-bearing datasets: keys can be loaded/unloaded explicitly, and encryption roots create a clear authority boundary.
This fits DeriveBSD's “explicit injection + evidence” posture if key-use events are recorded.

References:
- zfs-change-key/encryption roots: https://openzfs.github.io/openzfs-docs/man/master/8/zfs-change-key.8.html
- zfs-load-key: https://openzfs.github.io/openzfs-docs/man/master/8/zfs-load-key.8.html
- FreeBSD Foundation overview: https://freebsdfoundation.org/our-work/journal/browser-based-edition/storage-and-filesystems/protecting-data-with-zfs-native-encryption

See: `docs/146-zfs-native-encryption-for-generations.md`.

## 39) Minimal privilege escalation rules (doas-style)

Privilege escalation is unavoidable, but it should be small, explicit, and reviewable.
OpenBSD's doas is a good example of a compact, deny-by-default rule language that can be **derived** from policy decisions.

References:
- doas(1): https://man.openbsd.org/doas.1
- doas.conf(5): https://man.openbsd.org/doas.conf

See: `docs/147-doas-minimal-privilege-escalation.md`.


## 40) Variation testing + deep diffs + optional stabilization (reprotest/diffoscope/OSS-Rebuild)

Pure reproducibility is the gold standard, but ecosystems also benefit from *systematic variation testing* and high-quality diffs.
DeriveBSD can run a reprotest-like variation harness, store diffoscope reports as evidence objects, and optionally use stabilizers to test functional equivalence for low-risk classes.

References:
- reprotest repo: https://salsa.debian.org/reproducible-builds/reprotest
- diffoscope: https://diffoscope.org/
- OSS-Rebuild stabilization docs: https://docs.oss-rebuild.dev/stabilizers/

See: `docs/148-reproducibility-variation-harness-reprotest.md`, `docs/431-build-stabilizers-and-determinism-normalizers.md`.

## 41) Human-editable policy sources (HuJSON) with canonical signing

Operators want comments and readable diffs; verifiers want stable canonical bytes to hash and sign.
Using a HuJSON/JWCC “human JSON” source compiled into JCS-canonical JSON keeps policy comfortable and cryptographically solid.

References:
- Tailnet policy file (HuJSON) syntax: https://tailscale.com/docs/reference/syntax/policy-file
- HuJSON (JWCC) library: https://github.com/tailscale/hujson
- RFC 8785 (JCS): https://www.rfc-editor.org/rfc/rfc8785

See: `docs/149-human-policy-hujson-and-canonicalization.md`.

## 42) Jail profiles as derived allowlists (FreeBSD jail knobs as policy outputs)

FreeBSD jails expose many opt-in capabilities (`allow.*`). Treating these as named, derived profiles (builder/fetcher/hypervisor-worker) makes blast radius explicit and reviewable.

References:
- jail(8) parameters (allowlist knobs): https://man.freebsd.org/jail
- FreeBSD Handbook: Jails chapter: https://docs.freebsd.org/en/books/handbook/jails/

See: `docs/150-jail-profiles-and-allowlist-knobs.md`.


## 43) Protocol-agnostic credential agents (Plan 9 factotum lesson)

Plan 9’s factotum pattern centralizes secret handling into a small agent that mediates authentication on behalf of programs.
That aligns with DeriveBSD’s core stance: **builders are hostile** and secrets should be used through explicit, policy-scoped operations.

References:
- factotum manual (agent + key attributes): https://9fans.github.io/plan9port/man/man4/factotum.html
- “Security in Plan 9” (factotum + secstore roles): https://www.usenix.org/conference/11th-usenix-security-symposium/security-plan-9
- Plan 9 secstore manual: https://9fans.github.io/plan9port/man/man1/secstore.html

See: `docs/151-factotum-style-credential-broker.md`.

## 44) Hide non-required store paths from builders (Bazel hermeticity lesson)

Hermetic build systems treat undeclared inputs as a correctness and security failure. Bazel’s sandbox model makes this explicit: only declared inputs enter the sandbox boundary.
DeriveBSD can apply the same idea to the store: builders should only see the store objects in their declared input closure.

References:
- Bazel sandboxing: https://bazel.build/docs/sandboxing
- Bazel remote sandbox boundaries: https://bazel.build/remote/sandbox
- Nix community discussion on hiding non-required store paths from builds: https://discourse.nixos.org/t/nix-build-hide-non-required-path-in-nix-store/65313

See: `docs/152-store-view-minimization.md`.

## 45) Enforce store immutability as a primitive (TOCTOU lesson)

“Store paths are immutable” must be enforced, not assumed.
If store objects can be mutated after verification, privileged tooling can be tricked by time-of-check/time-of-use gaps.
DeriveBSD should use read-only datasets/snapshots and edge-verification so immutability is an auditable fact.

Reference:
- Snyk deep dive discussing immutability-assumption pitfalls in Nix-style stores: https://labs.snyk.io/resources/nixos-deep-dive/

See: `docs/153-store-immutability-and-toc-tou.md`.


## 46) CHERI capability hardware as a hardening lane (memory safety + compartmentation)

CHERI adds hardware capabilities that can enable fine-grained memory protection and scalable compartmentalization. CheriBSD (FreeBSD-derived) demonstrates this stack. DeriveBSD can treat CHERI as an **optional hardening lane** for select components and guest images, without compromising FreeBSD-first scope.

References:
- CheriBSD: https://www.cheribsd.org/
- CHERI overview: https://www.cl.cam.ac.uk/research/security/ctsrd/cheri/

See: `docs/163-cheri-capability-lane.md`.

## 47) “Split GPG” as a concrete key-isolation pattern (Qubes lesson)

Qubes’s split-GPG pattern keeps private keys in a more-trusted, network-isolated domain and exposes only narrow crypto operations to less-trusted domains. This directly matches DeriveBSD’s “no secrets in builders” posture and can be standardized as a crypto-domain + receipts.

References:
- Qubes split GPG: https://doc.qubes-os.org/en/latest/user/security-in-qubes/split-gpg.html
- Qubes split GPG-2: https://doc.qubes-os.org/en/latest/user/security-in-qubes/split-gpg-2.html

See: `docs/164-split-crypto-domains.md`.

## 48) Compatibility adapters are adoption accelerators (FreeBSD pkg repo adapter)

Greenfield systems win faster when they can “speak” existing ecosystem distribution formats as **adapters**. On FreeBSD, pkg repositories are the incumbent. DeriveBSD can export verified artifacts into pkg-shaped repos while keeping Derive digests + attestations as the true verification root.

References:
- pkg.conf(5) signature types: https://man.freebsd.org/cgi/man.cgi?query=pkg.conf
- pkg-repo(8): https://man.freebsd.org/pkg-repo%288%29

See: `docs/165-freebsd-pkg-repo-adapter.md`.

## 49) Tests as evidence objects (promotion gates without “trust CI”)

BSD-native tooling (Kyua/ATF) can run tests, but DeriveBSD’s key addition is to standardize **test receipts** as digest-bound evidence that policy can require for promotion or activation.

References:
- kyua(1): https://man.freebsd.org/cgi/man.cgi?query=kyua
- FreeBSD TestSuite: https://wiki.freebsd.org/TestSuite

See: `docs/166-test-receipts-and-promotion-gates.md`.

## 50) sandboxfs-style virtual views (fast hermetic sandboxes)

Large build graphs make “mount N inputs” expensive.
Bazel introduced **sandboxfs**, a FUSE filesystem that can project an arbitrary virtual view quickly, and FreeBSD has a port.
This is a strong fit for DeriveBSD’s storeview minimization, as an optional performance optimization.

References:
- Bazel sandboxing (sandboxfs note): https://bazel.build/docs/sandboxing
- sandboxfs repo: https://github.com/bazelbuild/sandboxfs
- FreeBSD port: https://www.freshports.org/filesystems/sandboxfs/

See: `docs/167-sandboxfs-accelerated-storeviews.md`.

## 51) SBOM + VEX as policy-bound evidence (inventory is not exploitability)

SBOM inventory is necessary but not sufficient once vuln data is in play.
VEX exists to convey exploitability status in context. CycloneDX supports VEX shapes, and OpenVEX provides a minimal, attestation-friendly interchange.

References:
- CycloneDX VEX capability: https://cyclonedx.org/capabilities/vex/
- OpenVEX spec: https://github.com/openvex/spec
- CISA VEX minimum requirements: https://www.cisa.gov/sites/default/files/2023-04/minimum-requirements-for-vex-508c.pdf

See: `docs/168-sboms-and-vex-as-evidence.md`.

## 52) Jobsets as the operational unit of “continuous derivation” (Hydra lesson)

Hydra’s jobset abstraction (what to repeatedly evaluate/build/test for a channel) is a clean way to operationalize a Nix-like ecosystem.
DeriveBSD can steal the abstraction while keeping evaluation schema-driven.

References:
- Hydra repo docs (projects/jobsets): https://github.com/NixOS/hydra
- Hydra overview: https://wiki.nixos.org/wiki/Hydra

See: `docs/169-jobsets-and-build-farms.md`.

## 53) Remote cache poisoning is real (verify outputs; caches aren’t authorities)

Remote caches speed up builds, but they add poisoning/replay risks if the trust model is underspecified.
Treat caches as untrusted performance layers; verify by digest + signatures before accepting.

References:
- Bazel remote caching: https://bazel.build/remote/caching
- Remote caching security deep dive: https://blogsystem5.substack.com/p/bazel-remote-caching

See: `docs/170-remote-cache-threat-model.md`.

## 54) VNET jails give compartments their own network reality (FreeBSD superpower)

Filtering is good; **separate stacks** are better when you can get them.
FreeBSD VNET jails provide a per-jail network stack (routes, neighbor caches, interfaces), which makes “no network” and “restricted egress” claims structurally enforceable.

See: `docs/171-vnet-jails-network-compartments.md`, RFC-0106.

## 55) Isolate hypervisor device backends (reduce VM escape blast radius)

VM escapes often target emulated devices. OpenBSD’s work hardening `vmd(8)` device emulation via privilege separation suggests a useful direction: **split device backends out of the core VMM worker**.

See: `docs/172-device-backend-isolation-bhyve.md`, RFC-0107.

## 56) “Compiled service DB” improves explainability without importing Linux init (s6-rc lesson)

Even if `rc.d` remains the executor, derive a compiled database of services, dependencies, and bundles so operators can diff and reason about machine state.

See: `docs/173-compiled-service-database-bundles.md`, RFC-0108.

## 57) Specialisations/variants are a lifesaver (safe-mode, role-mode, debug-mode)

NixOS specialisations let you define variations *within* a generation. DeriveBSD should adopt this as named, policy-governed variant activations.

See: `docs/174-specialisations-and-variants.md`, RFC-0109.

## 58) GC roots and pins are essential ergonomics (Nix pros will expect this)

Nix’s “GC roots” model makes retention predictable and explainable. DeriveBSD should provide explicit roots/pins for BEs, store objects, microVM images, and DevShell artifacts.

See: `docs/175-pins-roots-and-garbage-collection.md`, RFC-0110.


## 58.1) Receipted GC runs (retention as evidence)

The high-leverage missing piece in many immutable/derivation-first systems is making GC itself **explainable**: a dry-run plan, a policy gate, and a receipt.
DeriveBSD can standardize this as typed artifacts so “why did we lose rollback coverage?” has a one-object answer.

See: `docs/426-store-gc-plans-and-receipts.md`, `spec/store.gc.plan.schema.json`, `spec/store.gc.receipt.schema.json`.


## 59) Measured boot + attestation should be first-class evidence (RATS/Keylime lessons)

Secure Boot can block untrusted code, but measured boot produces evidence about *what actually ran*.
For high-assurance channels, it's worth defining evidence objects early (even if enforcement is optional): PCR quotes + event-log digests bound to DeriveBSD deployments.

References:
- IETF RATS Architecture (RFC 9334): https://datatracker.ietf.org/doc/rfc9334/
- Keylime measured boot guide: https://keylime.readthedocs.io/en/latest/user_guide/use_measured_boot.html
- systemd-measure (PCR pre-calculation reference point): https://www.freedesktop.org/software/systemd/man/systemd-measure.html

See: `docs/176-measured-boot-attestation.md`, RFC-0111.

## 59.1) TPM-sealed secrets as an optional lane (PCR policies)

Sealing secrets to measured boot state is a high-leverage hardening lane for fleet hosts and regulated appliances, but it must be upgrade-safe and evidence-bearing.
DeriveBSD can express this as typed PCR policies (diffable) plus secret unseal receipts (queryable), without forcing TPM on every product shape.

References:
- systemd-cryptenroll (TPM2 enrollment): https://www.freedesktop.org/software/systemd/man/systemd-cryptenroll.html
- systemd-pcrphase.service (boot phase measurements): https://www.freedesktop.org/software/systemd/man/systemd-pcrphase.service.html
- tpm2_policypcr(1) + tpm2_policyauthorize(1): https://tpm2-tools.readthedocs.io/en/latest/man/tpm2_policypcr.1/ , https://tpm2-tools.readthedocs.io/en/latest/man/tpm2_policyauthorize.1/

See: `docs/425-tpm-sealed-secrets-and-pcr-policies.md`.


## 60) Fleet rollouts are a first-class OS feature (Cincinnati/Zincati + wave schedules)

If the OS is immutable and atomic, *rollout orchestration* becomes the next ecosystem primitive:
represent allowed transitions as signed data, stage updates under policy, reboot under windows/locks, and finalize only after health gates.

References:
- Cincinnati protocol (update graph): https://coreos.github.io/zincati/development/cincinnati/protocol/
- Fedora CoreOS auto-updates (wariness): https://docs.fedoraproject.org/en-US/fedora-coreos/auto-updates/
- Zincati auto-updates overview: https://coreos.github.io/zincati/usage/auto-updates/
- Bottlerocket wave schedule discussion (example of rollout waves as data): https://github.com/bottlerocket-os/bottlerocket/discussions/3755

See: `docs/177-fleet-coordinated-rollouts.md`, RFC-0112.

## 61) Keyless signing can lower adoption friction (Sigstore/Cosign adapter lane)

A greenfield ecosystem can still benefit from existing distribution tooling: cosign can store signatures and in-toto attestations alongside OCI artifacts, and supports keyless signing flows.
DeriveBSD can treat these as an *adapter lane* while keeping its own trust policy as the authority.

References:
- Cosign README (keyless signing + OCI signatures): https://github.com/sigstore/cosign
- Sigstore cosign signing overview (keyless): https://docs.sigstore.dev/cosign/signing/overview/
- Cosign verifying attestations (in-toto): https://docs.sigstore.dev/cosign/verifying/attestation/

See: `docs/178-sigstore-keyless-signing-adapter.md`, RFC-0113.

## 62) Portals / “powerbox” keep capability sandboxes usable (dynamic grants without ambient authority)

Capability modes (Capsicum), jails, and microVMs are strongest when programs can be fully described up-front.
But real systems need dynamic access: user-chosen files, emergency exports, and narrowly scoped “ask/allow” exceptions.

Ecosystems like Flatpak converged on **portals**: a trusted broker mediates requests and returns specific capabilities, often with user confirmation.
Capsicum research describes a similar “powerbox” UI for sandboxed applications.

References:
- XDG Desktop Portal overview: https://flatpak.github.io/xdg-desktop-portal/
- Flatpak portals model: https://docs.flatpak.org/en/latest/sandbox-permissions.html
- Towards oblivious sandboxing with Capsicum (powerbox concept): https://www.engr.mun.ca/~anderson/publications/2017/towards-oblivious-sandboxing.pdf

See: `docs/179-portals-and-powerbox.md`, RFC-0114.

## 63) Capability mode + dynamic linking needs a first-class pattern (avoid backsliding)

Dynamic linking and late `dlopen()` are one of the most common reasons teams keep ambient filesystem access.
Defining a clear “link-then-cap” pattern (and a brokered-open approach for plugins) keeps Capsicum viable.

References:
- Towards oblivious sandboxing (dynamic linking friction): https://papers.freebsd.org/2017/vbsdcon/anderson-Towards_Oblivious_SandBoxing.files/anderson-Towards_Oblivious_SandBoxing.pdf
- libcasper(3) (brokered services inside capability mode): https://man.freebsd.org/cgi/man.cgi?query=libcasper&sektion=3

See: `docs/180-capability-mode-dynamic-linking.md`, RFC-0115.

## 64) Workload identity should be an OS primitive (secretless by default)

Static secrets are the easiest way for immutable systems to regress:
tokens creep into images, credentials get shared across compartments, and the control plane becomes a universal decryptor.

Ecosystems converged on **workload identity** (SPIFFE/SPIRE): workloads obtain short-lived identity documents (SVIDs) via a local API, then use that identity to fetch scoped capabilities/tokens.
DeriveBSD can anchor this unusually well because its plan/closure/runtime digests already define “what the workload is”.

References:
- SPIFFE overview (workload identity framework + SVIDs): https://spiffe.io/docs/latest/spiffe-about/overview/
- SPIRE concepts (node + workload attestation plugins): https://spiffe.io/docs/latest/spire-about/spire-concepts/
- Working with SVIDs (X.509-SVID + trust bundle): https://spiffe.io/docs/latest/deploying/svids/

See: `docs/181-workload-identity-and-secretless-deploys.md`, RFC-0116.

## 65) Object-capability RPC keeps crossings least-authority (Cap'n Proto / OCapN)

A capability-first OS wants its RPC substrate to be capability-bearing too: hand out *object references* and brokered handles rather than depending on ambient naming and per-service ACL logic. This makes authority edges explicit, routable, and naturally compatible with portal grants.

References:
- Cap'n Proto RPC (capability-based; promise pipelining): https://capnproto.org/rpc.html
- OCapN overview (interoperable networked capabilities): https://ocapn.org/

See: `docs/183-object-capability-rpc.md`, RFC-0118.

## 66) Leases + revocation keep dynamic grants bounded (revocable capabilities)

Dynamic grants (portals, debug exports, emergency operations) should default to **time-bounded leases** with explicit revocation, otherwise least-authority systems silently accrete privilege. Revocation is easiest when grants are delivered through proxies/agents (fail-safe).

References:
- UCAN revocation notes (proxy-agent revocation framing): https://github.com/ucan-wg/revocation
- Revokable capabilities (pattern index): https://wiki.c2.com/?RevokableCapabilities

See: `docs/182-capability-leases-and-revocation.md`, RFC-0117.


## 67) Attenuating delegation tokens reduce confused-deputy risk (Macaroons/Biscuit)

When authority must pass through multiple helpers/compartments, identity-based ACLs tend to explode ("service A can do X"), creating confused-deputy and overbroad-permission failures.

Token formats that support **offline attenuation** let the holder add restrictions before forwarding ("capability mail"). This makes delegation naturally shrink over a call chain.

References:
- Macaroons paper (NDSS 2014): https://theory.stanford.edu/~ataly/Papers/macaroons.pdf
- Biscuit docs (offline attenuation): https://doc.biscuitsec.org/getting-started/introduction.html

See: `docs/184-attenuating-delegation-tokens.md`, RFC-0119.

## 68) Interactive portal approvals must be receipt-quality evidence (consent receipts)

Once you add an interactive "ask" path (development/workstations), that path becomes one of the most privileged flows in the system.
If approvals aren’t recorded as structured evidence, you lose explainability: *who approved what*, *with which constraints*, and *under what prompt wording*.

Treat "ask" decisions as first-class receipts (`portal.consent`) and bind them to grants/leases.

References:
- XDG Desktop Portal overview (broker API pattern): https://flatpak.github.io/xdg-desktop-portal/

See: `docs/185-portal-consent-and-audit-receipts.md`, RFC-0120.


## 69) Policy extensibility should compile to a sandboxable artifact (policy-as-Wasm)

Rich org policy is inevitable, but embedding a full evaluator language in core tends to leak ambient authority.
A compile-to-Wasm lane keeps policy as a **digest-pinned artifact** and the runtime small and sandboxable.

References:
- OPA Wasm docs (compile Rego to Wasm modules): https://openpolicyagent.org/docs/wasm

See: `docs/186-policy-modules-wasm.md`, RFC-0121.

Review surface (policy-code drift as a gateable diff): `docs/451-policy-module-diff-as-review-surface.md`.

## 70) Transparency logs need split-view defenses (witness cosigning / gossip)

Append-only logs can still equivocate by presenting different trees to different clients.
High-assurance consumption should require checkpoints with **witness signatures** (or equivalent gossip evidence)
so split views become detectable.

References:
- Sigsum design notes (gossip/witnessing): https://git.sigsum.org/sigsum/tree/doc/design.md
- Witness networks discussion: https://blog.transparency.dev/can-i-get-a-witness-network

See: `docs/187-witnessed-transparency-checkpoints.md`, RFC-0122.


## 71) VM-orchestrated scenario tests prevent fleet regressions (NixOS VM tests lesson)

NixOS treats integration tests as a first-class framework: tests run in VMs and can orchestrate multi-machine scenarios.
DeriveBSD should make *scenario tests* digestable artifacts so promotion gates are objective and repeatable.

References:
- NixOS VM tests overview: https://wiki.nixos.org/wiki/NixOS_VM_tests
- Nixpkgs manual note on VM-based NixOS tests: https://nixos.org/nixpkgs/manual/

See: `docs/188-scenario-tests-multimachine.md`, RFC-0123.

## 72) Authority graphs need tooling, not heroics (lint + viz from caproute)

Once the capability routing graph gets large, review breaks unless the ecosystem has **linting, visualization, and diff summaries**.
Bake in `capability.graph` as a normalized view so policy can gate changes (“no new danger edges”) and PR review can be graph-based.

References:
- Fuchsia capability routing concepts: https://fuchsia.dev/fuchsia-src/concepts/components/v2/introduction

See: `docs/189-capability-graph-lint-and-viz.md`, RFC-0124.


## 73) Quorum-based substitution makes binary caches safer (Trustix lesson)

“Untrusted caches, trusted verification” is correct, but ecosystems still need a way to:

- detect non-reproducible builds early
- reduce cache poisoning blast radius
- let high-assurance consumers require corroboration

Trustix’s model (“input hash → output hash across independent providers”) is a practical pattern:
make witness statements first-class and let policy require **N matching witnesses** before accepting substitution.

References:
- Trustix docs: https://nix-community.github.io/trustix/
- Trustix announcement: https://tweag.io/blog/2020-12-16-trustix-announcement/

See: `docs/190-cache-witness-quorums-trustix.md`, RFC-0125.


## 74) Toolchain trust needs dedicated evidence (DDC + bootstrappable chains)

Toolchains are uniquely dangerous: a compromised compiler can perpetuate its compromise.
High-assurance channels should have a way to require additional evidence.

DDC (Diverse Double-Compiling) is a practical technique to detect “trusting trust” style attacks by demonstrating
that a compiler binary corresponds to its purported source.
Bootstrappable-build work reduces dependence on opaque binary seeds by shrinking the bootstrap base.

References:
- Wheeler’s DDC dissertation site: https://dwheeler.com/trusting-trust/
- ACSAC DDC paper abstract: https://www.acsac.org/2005/abstracts/47.html
- Bootstrappable Builds (Mes): https://www.bootstrappable.org/projects/mes.html
- Guix full-source bootstrap writeup: https://guix.gnu.org/blog/2023/the-full-source-bootstrap-building-from-source-all-the-way-down/

See: `docs/191-diverse-double-compiling-and-bootstrappable-toolchains.md`, RFC-0126.


## 75) Diagnostics should be routed authority, not ambient root (Fuchsia diagnostics lesson)

Many OSes treat observability as “whoever has root can see everything”.
Fuchsia’s diagnostics model is a useful counterexample: logs/Inspect are mediated and treated as routed capabilities.

DeriveBSD should treat “debug/tracing” as leased, digest-pinned grants:

- brokers own the privileged power tools
- access is explicit, time-bounded, and auditable
- capability-graph tooling can lint “cross-compartment observability” edges

References:
- Fuchsia diagnostics: https://fuchsia.dev/fuchsia-src/concepts/components/diagnostics
- OpenTelemetry spec overview (interop layer): https://opentelemetry.io/docs/specs/otel/overview/

See: `docs/192-observability-as-capability.md`, RFC-0127.


## 76) Resource limits need delegation semantics (cgroup v2 mindset)

“Set limits” isn’t enough for real systems. Ecosystems need a way to express:

- a parent gets a budget and safely subdivides it among children
- budget changes are reviewable like other authority changes

Linux cgroup v2 documents delegation as a first-class concept. DeriveBSD can steal the mindset
while mapping enforcement to FreeBSD primitives (rctl/racct, cpuset, ZFS quotas).

References:
- cgroup v2 delegation model: https://docs.kernel.org/admin-guide/cgroup-v2.html
- FreeBSD rctl(8): https://man.freebsd.org/rctl

See: `docs/193-resource-budget-capabilities.md`, RFC-0128.


## 77) Privacy filters should be deterministic artifacts (redaction transforms)

Telemetry and incident artifacts often contain secrets.
Ad-hoc scrubbing scripts are hard to audit and easy to bypass.

Treat redaction as a signed, digestable transform:

- `redaction.transform` defines the allowlist/mask rules (or a sandboxed module)
- `redaction.receipt` proves which transform was applied (input digest → output digest)

References:
- OpenTelemetry guidance: handling sensitive data: https://opentelemetry.io/docs/security/handling-sensitive-data/
- Kubernetes audit policy knobs (showing the need for explicit filtering controls): https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/

See: `docs/195-deterministic-redaction-transforms.md`, RFC-0130.


## 78) Time-travel debugging should be shareable (record/replay capsules)

Record/replay debugging (rr-shaped) is one of the strongest ways to turn nondeterminism
into a deterministic reproduction, enabling reverse execution and better triage workflows.

DeriveBSD can make it safe-by-default by requiring explicit recording grants and emitting
portable replay capsules (digests + bounded attachments) rather than “ship the whole machine”.

References:
- rr project site: https://rr-project.org/
- rr repository: https://github.com/rr-debugger/rr

See: `docs/194-debugging-by-lease-and-replay-capsules.md`, `docs/220-operational-time-travel-debugging.md`, RFC-0129, RFC-0155.


## 79) On-demand services need escrowed endpoints (socket activation generalized)

Socket activation is a pragmatic ecosystem trick: a supervisor owns the listening socket and hands it to a service when needed.
It helps with:

- on-demand startup
- crash-only restarts
- stable client endpoints

The deeper lesson for DeriveBSD is to generalize this beyond sockets:

- treat "endpoint/handle acquisition" as *derived authority* owned by an activation broker
- pass rights-minimized handles to services at start
- escrow broker-owned handles across restarts so clients don't rediscover via ambient namespaces

References:
- systemd socket activation docs: https://www.freedesktop.org/software/systemd/man/systemd.socket.html
- systemd-socket-activate(1) overview: https://man7.org/linux/man-pages/man1/systemd-socket-activate.1.html
- launchd socket retrieval and restart semantics: https://www.manpagez.com/man/3/launch_activate_socket/

See: `docs/196-capability-activation-and-escrow.md`, `docs/238-portal-activated-services-and-socket-activation.md`, RFC-0131, RFC-0170.


## 80) Time and entropy should be policy-governed inputs (virtual clocks for determinism)

"Reading wall clock" and "getting entropy" are hidden dependencies.
They cause reproducibility drift, flaky tests, and ambiguous policy decisions.

Other ecosystems show useful patterns:

- **Fuchsia** models clocks as objects; a privileged maintainer adjusts UTC while clients observe it.
- **Linux** time namespaces provide per-namespace offsets for certain clocks.

DeriveBSD should treat wall clock and entropy as explicit authority:

- deterministic profiles for builds/tests
- virtual clocks per compartment (jail/microVM) when needed
- receipts that bind a run to its time/entropy profile

References:
- Fuchsia UTC architecture: https://fuchsia.dev/fuchsia-src/concepts/kernel/time/utc/architecture
- Fuchsia monotonic time: https://fuchsia.dev/fuchsia-src/concepts/kernel/time/monotonic
- Linux time namespaces: https://man7.org/linux/man-pages/man7/time_namespaces.7.html

See: `docs/197-time-and-rng-authority.md`, RFC-0132.


## 81) Sandboxes need persistable file grants (security-scoped bookmarks / document portals)

Capability mode and portals solve one-shot file access, but users expect "recent documents" and apps need to reopen previously approved files after restart.

Two patterns are worth stealing:

- macOS security-scoped bookmarks (persist opaque user-approved access tokens; re-open later via scoped access calls)
- XDG document portal (export selected files into a restricted view for sandboxed apps)

DeriveBSD can bake this in as `fs.bookmark`: a signed, revocable claim ticket that is exchanged via the portal for a fresh rights-minimized FD.

References:
- Apple App Sandbox file access: https://developer.apple.com/documentation/security/accessing-files-from-the-macos-app-sandbox
- startAccessingSecurityScopedResource(): https://developer.apple.com/documentation/Foundation/URL/startAccessingSecurityScopedResource%28%29
- XDG Documents portal: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Documents.html

See: `docs/198-persistent-file-capabilities-bookmarks.md`, RFC-0133.


## 82) "Open with…" is a policy problem (Plan 9 plumber / Android intents)

Inter-app integration is where sandboxes usually leak:
"just call xdg-open" becomes "spawn arbitrary handlers" which reintroduces ambient authority.

Plan 9 and Android converge on a better model:

- a central resolver (plumber / intent resolver)
- declarative rules/filters
- optional interactive chooser and defaults

DeriveBSD can implement this as an intent router that:
- receives typed `intent.request`
- resolves to a handler using policy + rules
- brokers handoff via portals + capability-carrying RPC
- emits `intent.route.receipt` evidence

References:
- Plan 9 plumbing: https://9p.io/sys/doc/plumb.html
- plumb(7) rules: https://9fans.github.io/plan9port/man/man7/plumb.html
- Android intents and intent filters: https://developer.android.com/guide/components/intents-filters

See: `docs/199-intent-routing-and-plumbing.md`, RFC-0134.


## 83) Secure time as evidence (NTS + Roughtime)

Many security mechanisms rely on “roughly correct” time, but classic NTP is not cryptographically protected.
A greenfield OS can treat time sources as policy-governed and evidence-bearing:

- authenticate time sync (NTS for NTP client/server mode)
- use quorum-friendly authenticated rough time (Roughtime) for fast sanity checks and misbehavior proofs
- attach a proof bundle digest to `time-snapshot` receipts

References:
- NTS (RFC 8915): https://datatracker.ietf.org/doc/html/rfc8915
- Roughtime overview: https://roughtime.googlesource.com/roughtime
- IETF Roughtime draft: https://www.ietf.org/archive/id/draft-ietf-ntp-roughtime-08.html

See: `docs/200-secure-time-bootstrapping.md`, RFC-0135.

## 84) Network access as an explicit capability (deny-by-default egress)

UNIX networking tends to be ambient authority. “No network by default” becomes much easier if egress is mediated:

- broker outbound connections via `system.net` under `net-egress-grant`
- mediate DNS explicitly (Casper’s `system.dns` is a practical adapter in FreeBSD capability mode)
- emit `net-flow-receipt` evidence for audit/explainability

References:
- FreeBSD `cap_dns` / `system.dns`: https://man.freebsd.org/cgi/man.cgi?query=cap_dns&sektion=3
- Casper broker API: https://man.freebsd.org/cgi/man.cgi?query=libcasper&sektion=3
- Fuchsia capability concept: https://fuchsia.dev/fuchsia-src/concepts/components/v2/capabilities

See: `docs/201-network-egress-as-capability.md`, RFC-0136.


## 85) Supply chain workflows need a *layout*, not just attestations (in-toto)

Provenance is per-artifact; ecosystems still need a way to state:
- which steps must exist (build/test/sign/publish)
- who is allowed to perform each step
- what inputs/outputs are allowed to chain across steps

in-toto’s answer is a **signed layout** describing the expected workflow and authorized functionaries.
If DeriveBSD makes layouts an optional but first-class lane, teams avoid re-encoding workflow policy in bespoke CI.

References:
- in-toto spec (layout + link model): https://github.com/in-toto/docs/blob/master/in-toto-spec.md
- in-toto getting started (layout concept): https://in-toto.io/docs/getting-started/

See: `docs/202-in-toto-layouts-and-step-policy.md`, RFC-0137.


## 86) Community repositories want delegations (full TUF as an optional interop lane)

DeriveBSD can keep a minimal TUF-inspired client invariant set.
But when repositories become community-run (ports-like trees, multi-team ownership), **delegations** become the cleanest way to split trust without sharing keys.

Keeping an optional “full TUF metadata adapter” lane means:
- DeriveBSD channels can publish TUF role files for compatibility
- DeriveBSD can ingest upstream TUF repos and translate them into channel views
- delegations can map cleanly onto subtree ownership (e.g., categories or namespace segments)

References:
- TUF spec: https://theupdateframework.github.io/specification/latest/
- TUF delegations FAQ: https://theupdateframework.io/docs/faq/

See: `docs/203-full-tuf-metadata-adapter.md`, RFC-0138.


## 87) Isolate risky hardware with “device domains” (Qubes sys-usb lesson)

A lot of “sandboxing” falls over because the most trusted plane still owns:
- USB stacks
- device firmware interaction
- huge driver attack surfaces

Qubes OS shows a pragmatic pattern: attach risky controllers to a dedicated domain (e.g., `sys-usb`) and broker access to other domains.
DeriveBSD can bake this in as an optional lane: **device isolation domains** (“driver VMs”) plus evidence-bearing attach/detach leases.

References:
- Qubes USB handling guide: https://doc.qubes-os.org/en/latest/user/how-to-guides/how-to-use-usb-devices.html

See: `docs/204-device-isolation-domains.md`, RFC-0139.


## 88) Clipboard / drag&drop must be portal-shaped (Wayland/XDG lesson)

Clipboard is a high-value exfil channel.
On X11 it is effectively ambient; Wayland intentionally restricts clipboard access to reduce passive sniffing, and sandboxed desktops use portal brokers.

A greenfield OS can treat data transfer as:
- **leased capability grants** (read/write offers, not global state)
- optionally evidence-bearing transfers
- redaction-profile binding by digest (so “safe paste paths” are reviewable)

References:
- XDG Desktop Portal Clipboard interface: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Clipboard.html
- Wayland data-control protocol note (privileged/opt-in clipboard manager surface): https://wayland.app/protocols/wlr-data-control-unstable-v1

See: `docs/205-data-transfer-portals-clipboard-and-dnd.md`, RFC-0140.


## 89) Notifications must be non-observing (XDG portal lesson)

Notifications are a convenience feature, but also an information channel.
If an app can observe whether you saw/clicked/dismissed a notification, it becomes a side-channel.
A greenfield OS can make notifications explicitly **non-observing**: apps can publish/withdraw, but cannot learn if the notification was presented.

References:
- XDG Desktop Portal Notification interface (non-observing): https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Notification.html
- Notification interface XML note (outlasts process; can activate later): https://sources.debian.org/src/xdg-desktop-portal/1.2.0-1/data/org.freedesktop.portal.Notification.xml

See: `docs/206-notification-portal-non-observing.md`, RFC-0141.


## 90) Input is authority (HID danger classes + secure attention key)

If an untrusted domain gets raw keyboard/mouse, it can often control the whole session and sniff secrets.
DeriveBSD should treat input as capability-routed authority, and reserve a Secure Attention Key to enter a host-controlled trusted prompt mode.

References:
- Qubes device handling security warning (USB input devices): https://doc.qubes-os.org/en/latest/user/security-in-qubes/device-handling-security.html
- Microsoft secure logon trusted path (CTRL+ALT+DEL): https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/interactive-logon-do-not-require-ctrl-alt-del

See: `docs/207-input-authority-secure-attention-and-hid-risk.md`, RFC-0142.


## 91) Screen sharing must be portal-shaped (ScreenCast + PipeWire lesson)

Screen capture is a classic “sandbox breaker”.
Modern Wayland/sandboxed desktops route it through a portal:
- the user selects a monitor/window
- the app receives a scoped stream handle (not ambient display authority)

References:
- XDG Desktop Portal ScreenCast: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.ScreenCast.html
- libportal screencast overview (PipeWire stream transport): https://libportal.org/libportal.html
- PipeWire portal access control notes: https://docs.pipewire.org/page_portal.html

See: `docs/208-screencast-and-remote-desktop-portals.md`, RFC-0143.


## 92) Remote control is input injection (RemoteDesktop + secure attention)

Remote desktop is not “screen sharing plus convenience”.
It is *input injection*.
If you don’t model it explicitly, you eventually leak raw keyboard/mouse authority.

References:
- XDG Desktop Portal RemoteDesktop: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.RemoteDesktop.html

See:
- `docs/208-screencast-and-remote-desktop-portals.md`, RFC-0143
- `docs/207-input-authority-secure-attention-and-hid-risk.md`, RFC-0142


## 93) AV capture wants on-demand portals (camera exists; audio is still emerging)

Camera and microphone access should be:
- on-demand
- brokered with user-visible selection
- leased/revocable

The Linux portal ecosystem has a Camera portal, but microphone/audio mediation is still evolving; a greenfield OS can bake in a coherent audio capture portal early.

References:
- XDG Desktop Portal Camera: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Camera.html
- Microphone portal request: https://github.com/flatpak/xdg-desktop-portal/issues/615
- Audio portal discussion: https://github.com/flatpak/xdg-desktop-portal/issues/1129
- Mozilla notes no microphone portal yet: https://bugzilla.mozilla.org/show_bug.cgi?id=1726218

See: `docs/209-camera-and-audio-capture-portals.md`, RFC-0144.


## 94) Have policy kill-switches for portal families (lockdown)

Even with least-authority design, hardened deployments need an explicit “nope” switch.
A simple lockdown interface that can disable whole portal classes (screen capture, printing, location, etc.) prevents accidental enablement and simplifies compliance profiles.

Reference (prior art):
- XDG Desktop Portal Lockdown backend interface: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.impl.portal.Lockdown.html


## 95) Standardize portal session handles + permission storage early

Portals tend to grow “session handles” (long-lived streams) and “remember my choice” state.
If you don’t standardize these, every portal family invents its own semantics and revocation story.

Steal:
- shared Request/Session conventions
- a PermissionStore-like interface for persistent grants

See: `docs/210-portal-sessions-and-permission-store.md`, RFC-0145.

## 96) Location + printing are privacy/exfil surfaces and should be portals, not ambient services

Location and printing look “utility-ish”, so ecosystems often make them ambient.
In practice they are privacy and exfiltration cliffs.
Bake them in as brokered, leased, receipted portals from day 1.

See: `docs/211-location-portal.md`, RFC-0146 and `docs/212-printing-portal.md`, RFC-0147.


## 97) Fault management as a first-class subsystem (Solaris/illumos FMA lessons)

Older systems often treat “hardware is failing” as a pile of logs and ad-hoc scripts.
Solaris/illumos FMA treated it as an architecture: structured event reports, diagnosis engines, response agents, and a persistent log.

DeriveBSD can make this *evidence-native* so health-gated activation and fleet promotion can safely reason about host health.

See: `docs/213-fault-management-architecture.md`, RFC-0148.

## 98) Structured event logs as evidence (ETW / journal / OTEL lessons)

Treat logs as **typed events** with capability-gated access and integrity metadata (segments + hash chains), so ops signals can participate in health gates and exports cleanly to OpenTelemetry.

See: `docs/215-structured-event-log-as-evidence.md`, RFC-0150.

## 99) Incident snapshots as first-class artifacts (support bundles without secret leaks)

Most OSes eventually invent a “support bundle” (`sosreport`, crash reporters, vendor scripts).
If this isn’t standardized early, it turns into:
- ad-hoc root scripts
- inconsistent content
- accidental secret exfiltration

DeriveBSD already has the missing primitive: **typed evidence** (svc snapshots, fault snapshots, event segments, policy decisions).
Bake in a first-class `incident.bundle` artifact so operators can capture bounded context safely and share it (optionally encrypted) without giving away ambient log access.

See: `docs/216-incident-snapshots-and-support-bundles.md`, RFC-0151.

Tighten this further by making the *bundle-min selection and build step* first-class evidence: a `bundle.plan` (selection+transforms) plus a `bundle.build.receipt` (plan→bytes binding) makes support bundles reproducible and explainable. When bundle plan templates drift, attach a `bundle.plan.diff` as the stable review surface.

See: `docs/253-bundle-plans-and-deterministic-exports.md`.

## 100) State migrations as first-class artifacts (versioned steps + receipts)

Atomic host rollback is great until *state* changes underneath you.
Many failures in the field are not “the new binary won’t start”, but:
- schema migrations that partially ran
- config/state merges that drifted across upgrades
- rollbacks that boot but leave persistent state incompatible

Steal two lessons early:
- **run migrations sequentially** even if versions are skipped (Bottlerocket-style), and
- treat state transitions as **evidence** with rollbackable snapshots (ZFS holds help).

DeriveBSD should standardize:
- a compiled state inventory (`statedb`)
- an explicit `state-migration-plan`
- per-volume `state-migration-receipt` objects
- a runtime `state-snapshot` that health gating and incident bundles can include

See: `docs/217-state-datasets-and-migrations-as-evidence.md`, RFC-0152.


## 101) Transactional configuration with confirm windows + receipts (Junos / OpenWrt UCI)

Remote lockouts and partial config writes are self-inflicted wounds.
Steal:
- “commit-confirmed” (auto-rollback unless confirmed) for riskful changes (network/auth)
- staged change sets committed atomically

DeriveBSD direction: make config changes a first-class plan/receipt lane (`docs/218-configuration-transactions-and-receipts.md`, RFC-0153).

## 102) Change sets beat ad-hoc rollout scripts (compose plans + emit receipts)

Even when an OS has good primitives, operators end up with scripts that:
- apply config
- run migrations
- restart services
- pray

Greenfield advantage: define a *thin* orchestration object that references existing plans (config, migrations, service intents) and produces a single receipt.
This makes ordering explicit, keeps rollback honest (snapshots + holds), and gives a clean query surface: “what changes failed?”

DeriveBSD direction: `change-set` + `change-receipt` as compositional glue.

See: `docs/219-change-sets-and-apply-engine.md`, RFC-0154.

## 103) Firmware updates are part of the OS supply chain (treat as plans + receipts)

Fleets don’t just ship “OS updates”. They ship:
- BIOS/UEFI updates
- SSD/NIC/BMC firmware
- microcode and security revocations

When this is out-of-band, the outcomes are predictable:
- vendor tools and boot media
- unclear provenance and approvals
- no query surface (“which hosts are on vulnerable firmware?”)
- postmortems with missing context (“did firmware change?”)

DeriveBSD already has the right pattern:
**inventory → explicit plans → receipts → policy gates**.
Bake firmware in early as:
- `fw-device-inventory` (privacy-safe inventory)
- `fw-update-plan` / `fw-update-receipt`
- integration into `change-set`, incident bundles, and health gating

See: `docs/221-firmware-updates-as-artifacts.md`, RFC-0156.


## 104) Resource governance as evidence (limits + pressure)

Resource limits are usually a mess of:
- daemon flags
- unit files
- emergency `ulimit` and `sysctl` edits

But mature systems have real primitives:
- FreeBSD / Solaris `rctl`: a rule database that can be updated at runtime
- Linux cgroup v2: resource domains + explicit delegation
- PSI (pressure stall info): measures “time waiting on resources”, not just utilization

DeriveBSD should bake this into the ops spine as:
- `resource-policy` (desired budgets/caps/shares per subject)
- `resource-receipt` (what was applied, by which backend)
- `resource-snapshot` (effective limits + coarse usage + pressure summary)
- `resource-event` (violations + actions)

Wire it into change sets, health gating, incident bundles, and fault management.

See: `docs/222-resource-governance-as-evidence.md`, RFC-0157.


## 105) Secrets/credentials should not be a side-channel (treat as policies + grants + receipts)

Secrets are where systems usually regress to:
- plaintext config drift
- bespoke secret injection wrappers
- incident artifacts that leak credentials

Greenfield advantage: make secrets boring and explicit.
Bake in a lane where:
- configs reference secret ids/refs (never inline values)
- access is brokered via time-bounded grants
- rotation and materialization emit receipts
- the system can produce a safe secret snapshot for gates/bundles

DeriveBSD direction: `secret-policy` + `secret-grant` + `secret-snapshot` + `secret-receipt` + `secret-event`.

See: `docs/223-secrets-and-key-management-as-evidence.md`, RFC-0158.
## 106) Crash handling should be reproducible and policy-safe (build-id symbols + crash reports)

Crashes are one of the highest-signal “truth sources” in ops, but most systems treat them as:
- a blob file (core dump) with unknown contents
- a manual symbol hunt
- a privacy hazard
- impossible to correlate cleanly with rollouts

Greenfield advantage: make crashes **typed evidence**.

DeriveBSD should bake in:
- `crash-report`: metadata-first crash evidence object with digests for core/minidump/kernel dumps
- `crash-event`: typed journal event for correlation and fleet queries
- build-id keyed debug symbol distribution (debuginfod-like) so symbolication is reproducible
- policy gates for dump capture/export; default-safe sharing

See: `docs/224-crash-artifacts-and-symbolication-as-evidence.md`, RFC-0159.


## 107) Storage integrity should be explicit and receipted (scrubs + health snapshots)

Storage is where systems quietly lose data over time: latent corruption, degraded redundancy, and months without verification.

Greenfield advantage: make integrity verification and pool health **first-class evidence**:
- inventory (pool topology + feature flags) as a safe snapshot
- scrubs as explicit plans with receipts (when, what was found, what was repaired)
- typed storage events (scrub/resilver milestones; pool degrade/fault transitions) routed into the structured journal
- health gates that can block committing a new generation on a degraded pool

DeriveBSD direction: `storage-pool-inventory` + `storage-scrub-plan` + `storage-scrub-receipt` + `storage-health-snapshot` + `storage-event`.

See: `docs/225-storage-health-and-scrubbing-as-evidence.md`, RFC-0160.


## 108) Attestation results as artifacts (not just TPM quotes)

Most platforms that adopt measured boot stop at “we can produce a quote.”
The operational win comes from **typed verifier receipts** that can be reused across:
- secret release
- change/activation gates
- incident bundles
- admission control

Bake in a small set of RATS-shaped objects (`attestation.reference`, `attestation.receipt`, `attestation.requirement`) so posture becomes auditable and composable.
Also: treat PCR meaning as published semantics (a “PCR registry”), not folklore.
(See `docs/226-platform-posture-and-attestation-results-as-evidence.md` and the UAPI Group PCR registry: https://github.com/uapi-group/specifications/blob/main/specs/linux_tpm_pcr_registry.md.)


## 109) Time sync should be evidence, not folklore (NTS/PTP + receipts)

Time is a hidden dependency for security and operations:
- token expiry, certificate validation, and attestation freshness
- incident timelines and rollout correlation
- rate limiters and metrics that assume monotonic clocks

Most systems leave time discipline to an unaudited daemon and string logs.
Greenfield advantage: model trustworthy time as a first-class lane:
- time source inventory (what sources exist; what auth modes)
- explicit requirements for workflows that need trustworthy timestamps
- snapshots for health gates and incident bundles
- receipts for steps/slews/source changes
- typed time events in the structured journal

DeriveBSD direction: `time-source-inventory` + `time-sync-plan` + `time-sync-snapshot` + `time-sync-receipt` + `time-requirement` + `time-event`.

See: `docs/227-time-discipline-and-trustworthy-timestamps-as-evidence.md`, RFC-0162.


## 110) Treat trust roots + certificates as governed artifacts (trust bundles + issuance receipts)

Certificates are where many systems silently abandon discipline:
- trust stores drift across hosts
- renewals fail silently until an outage
- key material ends up in random files under `/etc`
- incident response can't answer what identity a host presented at the time

Greenfield advantage: make PKI boring and auditable:
- trust anchors as a signed, versioned `pki-trust-bundle`
- optional drift review surface: `pki.trust.bundle.diff` (anchors/constraints/distribution become gateable)
- desired issuance/renewal as `pki-issue-plan`
- outcomes as `pki-issue-receipt` (serial, validity window, chain digests)
- typed `pki-event` milestones in the structured journal

This composes cleanly with secrets (private keys are brokered) and time discipline (validity + freshness).

See: `docs/228-pki-and-identity-lifecycle-as-evidence.md`, `docs/434-pki-trust-bundle-diff-as-review-surface.md`, RFC-0163.


## 111) Lockdown levels should be a policy output (securelevel lessons)

Many systems have “hardening guides” but no *monotonic* way to reduce what the system can do after it reaches steady-state.
BSD securelevel is blunt but instructive:
- raise the level after bootstrapping
- enforce immutable flags and restrict raw device writes / kernel mutation
- make “unlocking” require an explicit reboot path

Greenfield advantage: treat lockdown as a **receipted posture transition**, not an ad-hoc sysctl tweak.

See: `docs/230-lockdown-levels-and-securelevel.md`, RFC-0164.


## 112) A/B updates need an explicit lifecycle contract (update_engine mindset)

Health-gated updates are easiest to implement badly if lifecycle semantics are implicit.
ChromeOS/Android’s update_engine docs are unusually explicit about:
- staging to an inactive slot
- recording boot success as an explicit fact
- bounded retries and automatic rollback
- keeping updater policy separate and formats stable

DeriveBSD direction: treat ZFS boot environments like slots and formalize the lifecycle as evidence objects (`boot.health.report`, `boot.commit.record`, attempt receipts).

See: `docs/231-ab-updates-and-recovery-semantics.md`, RFC-0165.


## 113) Boot assessment should be bootloader-visible (try-counters lesson)

Many systems attempt rollback in userland, *after* a failed boot has already created an outage.
A stronger primitive is bootloader-visible boot assessment:
- candidate entry gets a bounded number of tries
- a “good boot” must be explicitly blessed
- otherwise the bootloader automatically falls back

Greenfield advantage: standardize this early so every platform has deterministic “boot loop” behavior and every rollback produces explainable evidence.

See: `docs/241-boot-try-counters-and-boot-assessment.md`, RFC-0173.


## 114) Generalize “commit confirmed” beyond config (Junos lesson)

“Commit confirmed” is an operator superpower: apply a risky change, but automatically revert unless it is confirmed within a window.

Most OS ecosystems implement this ad-hoc (only for network config, only via scripts). DeriveBSD already has the ingredients (change-sets, receipts, boot environments, health gates).

Greenfield advantage: make confirmation + auto-revert a first-class, typed primitive for *any* risky transition.

See: `docs/242-confirmable-change-sets-and-auto-revert.md`, RFC-0174.

## 115) Targeted boot revocation beats key burning (SBAT lesson)

Secure Boot answers “was it signed by a trusted key?” but operations needs “is this signed component *still allowed today*?”

SBAT’s key insight is generation-based revocation: components carry a stable identity and a monotonic generation counter, so policy can revoke *specific generations/builds* without revoking an entire signing key.

Greenfield advantage: bake in a bootchain allowlist/revocation policy object and make verifier decisions cite it.

See: `docs/244-bootchain-revocation-and-allowlists.md`, RFC-0176.


## 116) Measured boot becomes usable with phase markers (PCR separation lesson)

Attestation is too brittle when a single PCR value encodes “everything that happened”.

Phase markers (measuring milestones into a dedicated PCR) make failures debuggable and enable least-authority gating (e.g., unlock portals/secrets only after `services`).

See: `docs/245-boot-measurement-phases-and-pcr-separation.md`, RFC-0177.


## 117) Standardize a causality graph for incident explainability

Receipts and event segments are powerful, but incident response often fails at “prove what caused what” quickly.

A compact `causality.graph` makes bundles navigable and enables deterministic “bundle-min” exports that include only the evidence required for the story.

See: `docs/246-causality-graphs-and-minimal-evidence-bundles.md`, RFC-0178.


## 118) Resource controls as first-class policy outputs (rctl / projects)

FreeBSD’s `rctl(8)` makes it possible to enforce resource limits with configured actions, but most ecosystems never make the limits a **reviewable service surface**.
DeriveBSD should treat budgets as typed artifacts + receipts + violation events so outages are mechanically explainable.

See: `docs/247-resource-budgets-and-limits-as-evidence.md`, RFC-0179.


## 119) Tracing sessions as evidence (DTrace done safely)

Dynamic tracing is powerful enough to require the same discipline as secrets: explicit scope, timeboxed leases, receipts, and deterministic export/redaction.
Treat tracing requests as typed session artifacts and outputs as evidence objects.

See: `docs/248-tracing-observability-as-evidence.md`, RFC-0180.


## 120) Unify temporary authority as leases (Vault lease lesson)

Most systems grow one-off "temporary power" mechanisms: sudo tickets, debug toggles, ad-hoc breakglass, and secret fetch scripts.

Vault's lease model (TTL + renew + revoke) is a sharp mental model: all temporary authority should look like a lease with clear expiry and revocation.
Greenfield advantage: standardize `lease_id` across lanes and make revocation evidence cross-lane.

See: `docs/249-lease-registry-and-cross-lane-revocation.md`, RFC-0181.


## 121) Keep authority revocation separate from CHERI pointer revocation

Capability systems love the word "revocation", but CHERI temporal safety uses revocation to mean "revoke dangling pointers", which can involve sweeping/epoch mechanisms.

Greenfield advantage: keep authority revocation cheap via indirection (leases + brokers) and treat CHERI temporal revocation as a separate, budgeted runtime concern.

See: `docs/250-cheri-temporal-revocation-and-indirection.md`, RFC-0182.


## 122) Export diagnostics as a portal (user-mediated sharing)

Most ecosystems treat “generate a support bundle” as one step and “send it” as an unstructured follow-up.
That’s where secrets leak.

Greenfield advantage: make exporting a distinct, lease-backed capability that is governed by an explicit policy object and produces an export receipt.

Optional follow-through: make export boundary drift mechanically reviewable by attaching `export.policy.diff` to drift bundles when policy posture changes (consent, recipients, encryption, raw blob rules).

Ecosystem anchor: sosreport upstream (support bundle baseline): https://github.com/sosreport/sos

See: `docs/251-export-policies-and-support-bundle-portal.md`, `docs/433-export-policy-diff-as-review-surface.md`, RFC-0183.


## 123) Standardize cross-lane lease joins early (envelope lesson)

A lease model only pays off if tooling can join “who has temporary authority” across *all* lanes.
If each lane invents its own metadata shape, correlation dies.

Greenfield advantage: bake in a small cross-lane `lease.envelope` join object early and make it cheap to synthesize from legacy grants.

See: `docs/252-lease-envelope-and-cross-lane-joins.md`, RFC-0184.


## 124) Make bundle-min selection decisions first-class (plan lesson)

Causality graphs make incident stories navigable, but the *selection decisions* (“why these digests?”) still tend to become scripts.

Greenfield advantage: treat selection + transform decisions as a typed `bundle.plan` artifact and bind exports to it; review template drift mechanically via `bundle.plan.diff`.

See: `docs/253-bundle-plans-and-deterministic-exports.md`, RFC-0185.


## 125) Ship a single verifiable release handle (capsule lesson)

Most ecosystems eventually invent an implicit “release manifest” (Release files, commits, tags, image descriptors).
If it is not a first-class artifact, incident response becomes archaeology: which digests, policies, and evidence actually applied?

Greenfield advantage: define a tiny `release.capsule` object early and make the capsule digest the thing channels point at.
Make publication optionally transparent via `release.transparency.entry`.

See: `docs/257-release-capsules-and-transparency.md`, RFC-0189.


## 126) Treat rollout decisions as evidence (cohort lesson)

Staged rollouts and cohorts are operationally mandatory, but they tend to be implemented as server-side config with no audit trail.

Greenfield advantage: standardize `rollout.policy` and emit a `rollout.receipt` on every update check so “offer vs hold” decisions are inspectable and attachable to incident bundles. For large fleets, add a signed `rollout.graph` for multi-hop upgrade constraints (barriers, dead-ends, prerequisites) and emit `rollout.traversal.receipt` when choosing edges.

See: `docs/258-staged-rollouts-and-cohorts.md`, RFC-0190.


## 127) Transparency needs monitors, not just logs (monitor lesson)

Append-only logs are only useful if someone continuously verifies checkpoints, consistency proofs, and policy invariants.
Greenfield advantage: standardize monitor policies, monitor snapshots, and typed alert events as attachable evidence.

See: `docs/259-transparency-monitors-and-witness-gossip.md`, RFC-0191.


## 128) Threshold publishing + emergency halts should be artifacts (release authority lesson)

Most ecosystems bury release authority in CI scripts and human ceremony, which makes halts and key rotations unaudited.
Greenfield advantage: make `release.authority.policy` and `release.halt.event` first-class objects with thresholds and receipts.

See: `docs/260-release-authority-policy-and-key-management.md`, RFC-0192.


## 129) Cohorts are tracking IDs unless constrained (rollout privacy lesson)

Cohorts are operationally mandatory, but unconstrained cohort spaces and hints can become long-lived identifiers.
Greenfield advantage: explicitly budget cohort entropy, require minimum bucket sizes, and treat salt rotation as an epoch boundary.

See: `docs/261-rollout-privacy-and-cohort-hygiene.md`, RFC-0193.

## 130) Feature flags should be typed inputs, not folklore (Gentoo USE lesson)

Optional build features are where ecosystems devolve into overlays and forks.
Greenfield advantage: treat feature selection as a typed input flowing through Spec→Lock→Plan, so it becomes reviewable and cache-keyed.

See: `docs/262-feature-flags-and-constraints.md`.


## 131) Input graph composition needs a boring standard (flakes/registry lesson)

Most “from-source” ecosystems eventually invent a project boundary + lockfile + discovery scheme.
Greenfield advantage: standardise a flake-like input graph and scoped registries early so composition stays deterministic and policy-governed.

See: `docs/263-flake-style-input-graphs-and-registries.md`.


## 132) Filesystem views are a capability surface (Plan 9 namespace + union view lesson)

Immutable bases inevitably need temporary overlays (compat shims, incident tooling, dev sandboxes).
Greenfield advantage: make view composition a derived, hashable object that shows up in diffs and receipts.

See: `docs/264-mount-namespaces-and-union-views.md`.


## 133) Ops tooling should be an attach/detach lane, not “SSH artifacts” (portable services lesson)

If there is no official “ops bundle” lane, operators invent one by hand and the base grows forever.
Greenfield advantage: portable service bundles that can be attached timeboxed with strong sandbox defaults and full evidence.

See: `docs/265-portable-service-bundles.md`.


## 134) Sanitizing untrusted docs should be a first-class workflow (Dangerzone lesson)

Opening untrusted PDFs/office docs is a human-scale security failure mode.
Greenfield advantage: bake in a sanitize portal that runs converters inside disposable sandboxes and emits explainable receipts.

See: `docs/267-sanitization-portal-and-disposable-sandboxes.md`.


## 135) Desktop apps should be compartments by default (Qubes/Flatpak lesson)

If interactive workloads are allowed to sprawl onto the host, the system will accumulate ad-hoc exceptions and unreviewable sharing channels.
Greenfield advantage: define AppVM artifacts + portal-only host integration early, and make disposables the easy default.

See: `docs/268-desktop-appvms-and-portalized-apps.md`.


## 136) Make human accounts portable by binding identity to storage (systemd-homed lesson)

Moving laptops, recovering from disk restores, and operating multi-machine personal workflows all get cleaner if
“user accounts” are not just host config.
Greenfield advantage: standardize a portable `home.area` concept that embeds a signed `user.record`, and make
unlock/attach operations policy-bound and receipted.

See: `docs/269-portable-home-areas-and-user-records.md`.


## 137) Disposables only work if persistence is predictable (Qubes storage layout lesson)

Template/disposable VMs stay usable because they make persistence explicit:
immutable base + persistent private + disposable volatile.
Greenfield advantage: bake a standard AppVM storage contract into the runtime manifest so “did this persist?” is answerable.

See: `docs/270-appvm-storage-private-volatile-and-home-areas.md`.


## 138) Sealing to PCRs is brittle unless policies can evolve (TPM policy-authorize lesson)

The temptation: seal disk/home keys directly to “these PCR values”. The reality: firmware and boot-chain updates change those values and you lock yourself out.
Greenfield advantage: treat PCR binding as a *policy object* that can be updated via an explicit signing authority, and emit receipts for every unseal attempt (success or failure).

See: `docs/272-sealed-secrets-attested-unsealing.md`.


## 139) Offline updates need a first-class carrier workflow (mirror kit lesson)

Air-gapped ops shouldn't mean “copy random tarballs to a USB stick”.
Greenfield advantage: define mirror kits with quarantine→promote semantics, strict verification, and receipts — and optionally carry delta packs for large updates.

See: `docs/273-airgap-mirror-kits-and-sneakernet-updates.md`.


## 140) Continuous fuzzing needs corpora + crash cases as artifacts (syzbot lesson)

Kernel fuzzing succeeds at scale when it is **continuous**, crash cases are minimized, and corpora are treated as persistent state.
Greenfield advantage: make fuzz runs emit receipts, store minimized crash cases as replayable bundles, and promote corpus snapshots as first-class artifacts that can gate releases.

See: `docs/274-continuous-fuzzing-farm.md`, `docs/234-anykernel-and-rump-kernels.md`.


## 141) Regression localization should be automatic and evidence-backed (bisect + ddmin lesson)

Most OS ecosystems rely on heroic humans to localize regressions.
Greenfield advantage: automatically bisect over Plan digests, optionally ddmin the difference, and emit a signed root-cause certificate that can drive rollback/graft decisions.

See: `docs/275-root-cause-certificates-and-bisection.md`.



## 142) Kernel modules must be planned and lockable (kld/securelevel + loader verification lesson)

Kernel modules are a privileged escape hatch unless the system treats them as first-class artifacts.
A greenfield OS can make this boring:

- express an allowlist as policy (by digest, not by name)
- preload required modules during activation
- raise lockdown/securelevel and deny runtime loads by default
- emit receipts so incidents can answer “what code was in the kernel?”

See: `docs/276-kernel-module-policy-and-loading-as-evidence.md`, `docs/439-kmod-policy-diff-as-review-surface.md`, `docs/277-loader-verification-and-boot-config-constraints.md`.
## 143) `/dev` as authority: devfs rulesets + device grants

Containers and jails often fail by accidentally exposing powerful device nodes (raw disk, usb, input, gpu control).
FreeBSD jails explicitly recommend using devfs rules to limit per-jail `/dev`.

DeriveBSD should treat device visibility as first-class authority:
- classify devices (`device.profile`)
- attach as leases (`device.attach.grant` + receipts)
- compile minimal `/dev` views (devfs rulesets for jails)

See: `docs/278-device-grants-and-devfs-rulesets.md`.

## 144) USB quarantine domains + “no automount” workflows

Qubes OS isolates USB stacks/drivers in a dedicated domain (`sys-usb`) and attaches devices to other domains only on demand.
This turns a universal attack surface into an explicit, logged workflow.

DeriveBSD should bake in:
- quarantine device domains for USB controllers
- attach as leases with constraints
- sanitize portal as the default path for untrusted files from removable media

See: `docs/279-usb-quarantine-and-removable-media-workflow.md`, `docs/204-device-isolation-domains.md`, `docs/267-sanitization-portal-and-disposable-sandboxes.md`.

## 145) Quarantine metadata must be a system primitive (macOS/Windows “origin label” lesson)

Many systems have a weak, easy-to-strip provenance label for inbound content:
- macOS quarantine xattrs for downloaded files
- Windows “Mark of the Web” Zone.Identifier streams

Greenfield advantage: standardize an import pipeline that emits origin evidence objects and receipts, and make “open safely” the default
through portalized ingest, sanitize-first flows, and label-preserving transfers.

See: `docs/280-origin-labels-and-quarantine-attributes.md`, `docs/267-sanitization-portal-and-disposable-sandboxes.md`, `docs/279-usb-quarantine-and-removable-media-workflow.md`.


## 146) Outbound networking needs a first-class consent+policy lane (Little Snitch lesson)

Most sandboxes fail at the network boundary. Greenfield advantage: make outbound networking lease-based (grants with TTL), compile enforcement to PF anchors, and emit flow receipts so incidents can answer “what left the system?”

See: `docs/281-network-egress-broker-and-consent.md`, `spec/net.egress.grant.schema.json`, `spec/net.flow.receipt.schema.json`.


## 147) Split-view defense should be a tunable quorum, not folklore (witness cosigning lesson)

Append-only logs can still lie by forking views unless there is gossip or witnessing. Greenfield advantage: treat witness cosigning as a policy parameter, store checkpoint receipts as first-class artifacts, and make offline verification the default.

See: `docs/282-witness-cosigning-checkpoints-and-witness-networks.md`, `docs/187-witnessed-transparency-checkpoints.md`, `spec/log.checkpoint.receipt.schema.json`.


## 148) Treat time rollback as a real attack surface (NTS + Roughtime + LKGT)

Signed metadata still fails if the clock lies. Greenfield advantage: allowlist secure sources (NTS/Roughtime), capture proof bundles, and maintain LKGT monotonicity so “expiry” remains meaningful even under attacker-controlled clocks.

See: `docs/142-trustworthy-time-roughtime.md`, `docs/283-trustworthy-time-nts-roughtime-and-lkgt.md`, `spec/time.proof.bundle.schema.json`.


## 149) Make “switching boots” an evidencable operation (ZFS BE + try-counters)

Many systems can *build* a new OS image, but the act of choosing “next boot” and “automatic fallback” is often informal.
Bake in a switch plan + receipt so incident response can answer what changed, and the bootloader can safely auto-revert after failures.

See: `docs/284-bootenv-switching-as-evidence.md`, `spec/bootenv.switch.plan.schema.json`, `spec/bootenv.switch.receipt.schema.json`,
and `docs/241-boot-try-counters-and-boot-assessment.md`.


## 150) Treat hierarchical resource limits as a compiled, linted policy (rctl/racct)

FreeBSD’s `rctl` + `racct` are unusually strong primitives, but admins rarely get a uniform, explainable workflow.
Make a typed `resource.policy` compile into backend rulesets with receipts and violation events, and keep budgets lease-based (grants), not permanent exemptions.

Also bake in an **observation-mode learning loop** that proposes right-sized budgets from real usage (VPA-style), emitting `policy.suggestion` artifacts for review. See: `docs/329-learned-resource-budgets-and-observation-mode.md`.

See: `docs/247-resource-budgets-and-limits-as-evidence.md`, `docs/285-hierarchical-resource-limits-compilation.md`,
`spec/resource.policy.schema.json`, `spec/resource.budget.receipt.schema.json`, `spec/resource.violation.event.schema.json`.


## 151) Treat listening sockets + firewall holes as leased authority (inetd/socket-activation + PF anchors)

In most systems, exposing a port is ambient authority: daemons bind directly and admins separately edit firewall rules.
Greenfield advantage: make inbound exposure a policy-defined *lease* (timeboxed grants), compile enforcement to PF anchors, and emit receipts so incidents can answer **what was exposed and why**.

This also enables a sane default for low-traffic services: socket activation / inetd-style on-demand activation with tight promise profiles per instance.

See: `docs/286-inbound-listen-broker-and-firewall-leases.md`, `docs/238-portal-activated-services-and-socket-activation.md`, `docs/67-pf-anchors-per-instance.md`, `spec/net.listen.grant.schema.json`.


## 152) Model-check the scary state machines (TLA+ lane)

Greenfield projects can normalize a practice that older OS ecosystems treat as exotic: **design-level model checking** of the critical state machines.

DeriveBSD already has: tests, fuzzing, and replay capsules as evidence. Add a parallel lane: tiny finite models + receipts.

See: `docs/287-formal-model-checking-and-invariants.md` (starter model: `docs/models/bootenv_switch.tla`).


## 153) Make quorum approvals portable and digest-bound (four-eyes + separation of duties)

Many ecosystems treat “two-person integrity” as a social process (code review rules, offline ceremonies, tribal knowledge).
Bake it into the OS: approvals are first-class receipts bound to policy/plan/artifact digests, with explicit quorum and role separation (decide vs ship).

See: `docs/107-two-person-integrity.md`, `docs/288-multiparty-approvals-and-separation-of-duties.md`, `docs/256-consent-ux-contract.md`, and `docs/260-release-authority-policy-and-key-management.md`.


## 154) Make service-to-service auth boring (workload identity + mTLS)

Per-app firewalls and port leases help, but services still end up authenticating with long-lived API tokens.
Greenfield advantage: bake in short-lived **workload identities** (SPIFFE-style) issued as leases, bind issuance to what is actually running (digest/attestation), and treat mTLS as a compiled constraint.

See: `docs/181-workload-identity-and-secretless-deploys.md`, `spec/workload.identity.lease.schema.json`, `spec/workload.identity.issue.receipt.schema.json`.


## 155) Make "what can execute" a first-class policy (verified execution as a compile target)

Immutable stores and signed artifacts help, but incidents still go sideways when arbitrary bytes can execute from writable areas or temporary paths.
Greenfield advantage: define an exec integrity policy, compile it from the closure, and emit receipts showing what enforcement backend was active.

BSD ecosystems have real primitives here: FreeBSD's MAC framework can host mac_veriexec (verified execution), and HardenedBSD explored hash-enforced integrity rulesets (Integriforce).

See: `docs/289-exec-integrity-policy-and-verified-execution.md`, `spec/exec.integrity.policy.schema.json`, `docs/280-origin-labels-and-quarantine-attributes.md`, `docs/276-kernel-module-policy-and-loading-as-evidence.md`.


## 156) Make identity evidence cheap, but keep authority separate (Sigstore-shaped keyless signing)

Many ecosystems fail at universal signing because key management is hard. Keyless signing (OIDC identity + short-lived cert + transparency log) makes "who published this?" much easier to answer.

Greenfield advantage: treat keyless signatures as identity evidence (a receipt bound to a digest), but keep real promotion authority in the threshold publish lane (TUF-like metadata + publish receipts).

See: `docs/290-keyless-signing-and-publisher-identity-receipts.md`, `spec/publisher.identity.receipt.schema.json`, `docs/260-release-authority-policy-and-key-management.md`, `docs/282-witness-cosigning-checkpoints-and-witness-networks.md`.


## 157) Remote assistance must be a capability lane, not a backdoor

Every ecosystem ends up needing remote support.
If it isn’t a blessed, constrained workflow, it becomes a shadow workflow (permanent agents, tunnels, “just run this script”),
and incidents can’t answer what access existed or what happened during support.

Greenfield advantage: treat remote assistance as a composition of **existing capability lanes** (ScreenCast, RemoteDesktop, data transfer, networking),
all mediated by consent/quorum approvals and expressed as **leases + receipts**.
Make a single session envelope (`support.session`) that points at the receipts and optional recordings, so support events naturally fit into incident bundles.

See: `docs/291-remote-assistance-sessions-as-evidence.md`, `docs/208-screencast-and-remote-desktop-portals.md`, `docs/256-consent-ux-contract.md`, `spec/support.session.schema.json`.


## 158) Session recording is useful — but only if it is explicit, bounded, and privacy-aware

Terminal/session recording is widely deployed in high-assurance environments, but it becomes toxic if it is ambient surveillance.
The default must be: **output-only**, **timeboxed**, **budgeted**, **revocable**, and exported only through deterministic redaction + export policies.

Treat recordings as typed evidence objects that can be replayed, redacted, and attached to incident/support bundles, rather than ad-hoc log files.

See: `docs/292-terminal-session-recording-as-evidence.md`, `docs/195-deterministic-redaction-transforms.md`, `docs/251-export-policies-and-support-bundle-portal.md`, `spec/tty.session.recording.schema.json`.



## 159) Treat human authoring as a compiler problem (CUE/Nickel/Pkl frontends)

Every declarative OS eventually grows an ad-hoc DSL ecosystem.
If authoring isn’t treated explicitly as “frontend → canonical IR”, you end up with:
- unreviewable diffs
- hidden evaluation effects
- config languages that become the real product

Greenfield advantage: make “spec as data” real.
Standardize a single canonical Spec IR (schema-versioned JSON), then allow optional authoring frontends as *compiler lanes* with pinned compiler digests and explainable traces.

See: `docs/79-derive-spec-frontends.md`, ADR-0023, `docs/149-human-policy-hujson-and-canonicalization.md`, `docs/83-evaluator-minimalism.md`.


## 160) Attribute-indexed metadata + live queries are a UX superpower (Haiku/BeOS BFS lesson)

DeriveBSD already needs metadata primitives (origin labels, quarantine state, capability bookmarks, evidence pointers).
The BFS lesson is: if you don’t make metadata queryable and subscribe-able early, people reinvent brittle scanners and the labels get laundered.

Greenfield advantage: design a capability-gated metadata query substrate (index snapshots as evidence; queries as leases/portals) so “show me all unsafe imports” and “what needs sanitization?” are first-class operations.

See: `docs/293-attribute-indexed-metadata-and-live-queries.md`, `docs/280-origin-labels-and-quarantine-attributes.md`, `docs/198-persistent-file-capabilities-bookmarks.md`, `docs/229-evidence-spine-overview.md`.


## 161) Oblivious sandboxing makes Capsicum practical at scale (libpreopen/capsh lesson)

Capsicum is powerful but adoption dies on ergonomics: dynamic linking, plugin opens, and path-based discovery tempt teams into keeping ambient authority.

Greenfield advantage: ship a tiny *launcher* that constructs a pre-opened capability set (directory FDs + rights masks), performs any required early linking, enters capability mode, and only then runs the service. Treat the preopen map as a derived artifact so authority changes are diffable and explainable.

See: `docs/294-oblivious-sandboxing-launchers.md`, `docs/453-preopen-map-diff-as-review-surface.md`, `docs/180-capability-mode-dynamic-linking.md`, `docs/49-capsicum-casper-hardening.md`.


## 162) Multi-origin userlands need explicit composition (Bedrock strata lesson)

Adoption often requires mixing ecosystems (base sets + pkg adapters + vendor runtimes + foreign userlands). If composition is not explicit, systems accrete ad-hoc chroots and silent library leakage.

Greenfield advantage: introduce a first-class *stratum* concept (signed, digest-bound userland trees) and require an explicit stratum stack per process/view, recorded into evidence. This turns “where did this come from?” into a query, not folklore.

See: `docs/295-strata-and-multi-origin-userlands.md`, `docs/105-compat-view-foreign-binaries.md`, `docs/264-mount-namespaces-and-union-views.md`.


## 163) Keep the archive ambitious without drifting (feature-harvest rubric)

If we can’t express a feature as (1) an input, (2) a plan, and (3) a receipt, it’s not ready to bake in. Use a tight rubric to prevent “design tourism” while still harvesting rare ecosystem wins.

See: `docs/296-feature-harvest-rubric.md`.



## 164) Component descriptors compiled to canonical runtime manifests (Fuchsia/Flatpak ergonomic win)

Mechanisms aren’t enough; adoption requires one place to declare “how this component runs” and to compile that into
the canonical runtime artifacts (service graphs, capability routing, preopen maps, mount views, state footprints, health checks).

Greenfield advantage: make this a first-class, typed *source* that compiles to IR, so authority diffs are reviewable and drift is detectable.

See: `docs/297-component-descriptors-and-compiled-runtime-manifests.md`, `docs/140-capability-routing-manifests.md`, `docs/294-oblivious-sandboxing-launchers.md`.


## 165) Authority budgets + permission drift alarms (Flathub linter lesson, generalized)

Even “explicit grants” ecosystems suffer permission creep unless they add budgets + linting that fail fast.
Bake in authority budgets as policy objects evaluated against compiled IR, with exceptions as timeboxed receipts.

See: `docs/298-authority-budgets-and-permission-drift-alarms.md`, `docs/106-blast-radius-diff.md`, `docs/271-promise-profile-vocabulary-and-lint.md`.



## 166) Verified lazy rootfs mounts drastically improve cold-start (composefs/eStargz/Nydus lesson)

Large images often spend most of their startup time downloading data that never gets read.
Greenfield advantage: define an **optional** lane where a signed tree digest can be satisfied by a verified, on-demand mount (range fetch or chunk fetch), with the transport path recorded into evidence and diffable in review workflows.

See: `docs/299-verified-lazy-rootfs-and-on-demand-mounts.md`, `docs/119-casync-cvmfs-distribution.md`, `docs/139-bandwidth-efficient-deltas.md`.


## 167) “Previous versions” must not become a snapshot exfiltration surface (Fossil lesson + ZFS pitfalls)

Time-travel UX is a must-have for recovery and incident response, but exposing snapshot directories ambiently can leak old bytes after permissions change or secrets rotate.
Greenfield advantage: ship a portalized **time-travel snapshot lease** interface (filtered views + policy re-check), and treat snapshot access as an evidence-bearing event.

See: `docs/300-time-travel-snapshots-as-leases.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/251-export-policies-and-support-bundle-portal.md`.


## 168) P2P swarm distribution is worth baking in early (Dragonfly lesson)

At fleet scale, single-origin pull models create hotspots and long-tail rollout delays. P2P distribution systems turn each node into a verified partial mirror, *as long as peers are treated as untrusted and bytes are always verified by digest*.
Greenfield advantage: define P2P as a transport adapter lane (policy-bound, compartmented, receipted) so “speed up pulls” doesn't become an evidence-free side channel.

See: `docs/301-p2p-distribution-and-swarm-caches.md`, `docs/299-verified-lazy-rootfs-and-on-demand-mounts.md`.




## 169) Structured diagnostics trees beat log-grep (Fuchsia Inspect lesson)

Logs are necessary but lossy and privacy-dangerous. Systems get dramatically more operable when components expose **queryable structured state** (a typed tree) that tools can snapshot, diff, and bundle during incidents.

Greenfield advantage: bake in an Inspect-style diagnostics tree with an archivist that attributes data to component identity, enforces retention/redaction, and serves a single query surface.

See: `docs/302-structured-diagnostics-inspect-trees.md`, `docs/215-structured-event-log-as-evidence.md`, `docs/192-observability-as-capability.md`.


## 170) Always-on flight recorders (bounded circular buffers) turn incidents into receipts, not folklore (ETW lesson)

The best incident tooling has a **flight recorder**: bounded in-memory circular buffers that keep the last N seconds of high-signal context, promoted to an evidence bundle when a crash/watchdog/breakglass event triggers.

Greenfield advantage: treat flight recorders as a capability with budgets, leases, and export receipts—so “always-on debug” doesn’t become ambient surveillance.

See: `docs/303-flight-recorder-tracing-and-budgeted-diagnostics.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/298-authority-budgets-and-permission-drift-alarms.md`.




## 171) Trust stores drift unless they are explicit, versioned artifacts (p11-kit + SPIFFE bundle lesson)

In most OSes, "the trust store" is an ambient pile of files that different libraries interpret differently, leading to silent drift and incident ambiguity.
Greenfield advantage: make trust bundles **signed store objects**, compile deterministic CA views for interop (OpenSSL/NSS/PKCS#11), and inject trust handles into sandboxes by digest (FDs / preopen maps), with receipts on updates.

See: `docs/228-pki-and-identity-lifecycle-as-evidence.md`, `docs/304-trust-bundles-and-ca-injection-as-artifacts.md`, `docs/327-shadow-trust-and-system-ca-governance.md`.


## 172) Hostname-based network policy is fake without brokered DNS + receipts (Casper system.dns lesson)

If policy says "allow api.example.com" but enforcement sees only IP addresses, you get TOCTOU and folklore unless the system owns name resolution.
Greenfield advantage: make DNS a mediated capability (Casper adapter), bind hostname flows to evidenced resolutions, and optionally emit DNS query receipts (budgeted + redactable) so incidents can answer *what name resolved to what when*.

See: `docs/201-network-egress-as-capability.md`, `docs/305-dns-mediation-and-hostname-binding.md`.



## 173) Split-key crypto operations beat key files (Qubes Split GPG + platform keystore lesson)

Private keys are the most valuable "secrets" and should be **non-exportable by default**. Qubes showed the power of delegating crypto operations to a more-trusted compartment ("smart card as a VM"), while modern platform keystores show the value of API-level usage restrictions and user-presence gates.

Greenfield advantage: make crypto operations a portalized authority (sign/decrypt by lease), emit per-op receipts (digests, not plaintext), and wire the lane into budgets + separation-of-duties so release signing doesn’t become an ambient background capability.

See: `docs/306-crypto-operations-portal-and-split-keys.md`, `docs/223-secrets-and-key-management-as-evidence.md`, `docs/288-multiparty-approvals-and-separation-of-duties.md`.





## 174) Expiry-based security is fake without trustworthy time (NTS/Roughtime + LKGT + monitors)

Signed metadata with expiry is only safe if clients have time they can trust. If an attacker can roll the clock back or freeze it, anti-freeze/expiry checks become a bypass.

Greenfield advantage: make time a first-class, policy-governed input with evidence (inventories, source policy, proof bundles, LKGT monotonicity), and treat time divergence like a transparency problem (monitors + typed alerts).

See: `docs/283-trustworthy-time-nts-roughtime-and-lkgt.md`, `docs/307-time-sources-in-practice-chrony-nts-and-roughtime.md`, `docs/308-time-monitors-and-lie-detection.md`, `docs/61-channel-metadata-tuf-inspired.md`.





## 175) Installation is part of the product (declarative disk layouts + recovery images)

Most projects eventually reinvent install/recovery automation: ad-hoc partitioning scripts, mutable live images, and “follow this wiki” rituals.
Systems that feel *operable* treat provisioning as a first-class, repeatable input: declarative disk layouts (systemd-repart/Nix disko) and atomic multi-deployment models (OSTree) reduce both operator toil and incident archaeology.

Greenfield advantage: make disk mutation a typed, receipted lane from day 0 (plans/receipts), and ship recovery media as a derived artifact so "repair" uses the same verification and policy posture as normal operation.

See: `docs/309-installation-and-recovery-as-derived-operations.md`, `docs/310-disk-layout-plans-and-receipts.md`, `docs/69-host-generations-bectl.md`, `docs/284-bootenv-switching-as-evidence.md`.


## 176) Operator access should be certificate-based and leased (no static SSH keys)

Static SSH keys and permanent bastion accounts are a universal footgun: they’re hard to rotate, easy to copy, and rarely tied to a clear authorization record.
“Boring PKI that ships” (OpenSSH certificates) plus lease-bound session admission and (optional) recording gives fleets a safer default.

Greenfield advantage: make operator access a first-class capability lane:
short-lived SSH certs (issued by policy), session leases registered for revoke, and typed `operator.session` evidence objects that can point at TTY recordings when enabled.

See: `docs/311-operator-access-leases-and-ssh-certs.md`, `docs/292-terminal-session-recording-as-evidence.md`, `docs/242-confirmable-change-sets-and-auto-revert.md`, `docs/306-crypto-operations-portal-and-split-keys.md`.


## 177) Policy must be replayable and give counterfactuals (or it becomes bypassed “magic”)

Policy engines that can’t explain denials in actionable terms get bypassed during incidents.
Likewise, policy that depends on external datasets can silently drift unless replay and drift reports exist as a first-class workflow.

Greenfield advantage: bake in `derive policy replay` and bounded “what would make this allowed?” counterfactuals, scoped by authority and export-governed when detailed traces would leak sensitive structure.

See: `docs/312-policy-replay-and-counterfactual-explanations.md`, `docs/93-policy-decision-records.md`, `docs/95-explainability-contract.md`, `docs/237-lint-reports-and-contract-testing.md`.


## 178) Attestation identity is a lifecycle (capture provisioning/rotation as evidence)

Remote attestation stacks often fail for a boring reason: nobody can explain where the attestation key came from, whether endorsements were verified, or when the key rotated.
The result is either “trust it blindly” or “disable attestation when it breaks”.

Greenfield advantage: treat attester provisioning like any other derived, receipted operation.
Ship a typed `attester.provision.receipt` that records enrollment mode, AK identity, endorsement verification outcome, and correlation to bootstrap/change-sets.
This makes incident response and fleet operations *operable* instead of mystical.

See: `docs/314-attester-provisioning-and-key-lifecycle-receipts.md`, `docs/155-trust-bootstrap.md`, `docs/176-measured-boot-attestation.md`, `spec/attester.provision.receipt.schema.json`.


## 179) Measured boot should be explainable (boot manifests + event-log replay beat golden PCRs)

The “golden PCR values everywhere” posture is brittle and un-debuggable.
What fleets actually need is: a small boot-critical manifest and a deterministic way to replay the boot event log to explain PCR divergence.

Greenfield advantage: define a first-class `boot.manifest` object and bake in replay tooling and reason codes.
This supports variance (firmware drift) without devolving into per-host allowlists, and gives operators crisp answers (“unexpected loader digest”, “phase marker missing”).

See: `docs/313-boot-manifests-and-eventlog-replay.md`, `docs/245-boot-measurement-phases-and-pcr-separation.md`, `docs/226-platform-posture-and-attestation-results-as-evidence.md`, `docs/443-boot-eventlog-canon-as-evidence-artifact.md`, `spec/boot.manifest.schema.json`, `spec/boot.attestation.schema.json`, `spec/boot.eventlog.canon.schema.json`.

Add a mechanical drift surface for upgrades: attach `boot.manifest.diff` when the boot manifest digest changes (reviewable loader/kernel/cmdline drift).
See: `docs/436-boot-manifest-diff-as-review-surface.md`, `spec/boot.manifest.diff.schema.json`.



## 180) Durable attestation: make posture a time series (audit, not spot checks)

Attestation that only tells you “current state” is hard to use in real incidents.
What teams want is retroactive audit: *when did posture change, what did the verifier see, and what did we allow based on that?*

Greenfield advantage: treat attestation receipts as a bounded, queryable timeline (receipt chaining + typed transition events), with explicit retention/export budgets so durability doesn’t become privacy-toxic.

See: `docs/315-durable-attestation-and-posture-timelines.md`, `docs/226-platform-posture-and-attestation-results-as-evidence.md`, `docs/215-structured-event-log-as-evidence.md`, `spec/attestation.receipt.schema.json`.





## 181) Backups should be receipted and policy-governed (state replication is not an afterthought)

Most systems treat backups as external scripts and vendor products. That breaks incident archaeology: nobody can answer what was backed up, where it went, whether it was encrypted, or whether retention was actually applied.

Greenfield advantage: treat backups as derived operations that produce typed plans and receipts. Join backup receipts to transport/export receipts so “what left the system” and “what can we restore” are concrete, reviewable facts.

See: `docs/316-backups-and-restores-as-derived-operations.md`, `spec/backup.plan.schema.json`, `spec/backup.receipt.schema.json`, `docs/255-policy-constrained-transports.md`, `docs/306-crypto-operations-portal-and-split-keys.md`.


## 182) Backups are worthless without restore drills (continuous recovery testing as evidence)

Backups that have never been restored are an untested hypothesis. The restore path is where fleets usually fail: missing keys, undocumented steps, broken services, or unrealistic RTO/RPO expectations.

Greenfield advantage: make restore drills cheap and safe (quarantine microVMs; no ambient secrets; no outbound network by default) and emit typed drill receipts. During incidents, you can answer: “when was this backup last restored successfully, and what checks ran?”

See: `docs/317-restore-drills-and-continuous-recovery-testing.md`, `spec/restore.drill.receipt.schema.json`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/298-authority-budgets-and-permission-drift-alarms.md`.


## 183) Kernel knobs must be derived + receipted (sysctls and boot tunables are not folklore)

Every mature OS ends up with “mystery knobs”: sysctl values, loader tunables, `kenv` variables, and defaults applied by scripts. During incidents these become un-debuggable: nobody can answer what was set, when it changed, or whether it drifted.

Greenfield advantage: treat kernel tuning as a **derived operation** with typed plans/receipts and explicit drift events. When drift is detected, capture a bounded `sysctl.snapshot` and link it from `sysctl.event` so responders can see exactly what was observed (without shipping a full `sysctl -a`). Boot-time tunables belong in the generation closure (and boot manifests when used), and runtime sysctl writes are scoped, budgeted authority.

For reviewable upgrades, emit `sysctl.diff` between planned keysets and attach it to the drift bundle.

See: `docs/318-kernel-tunables-and-sysctls-as-evidence.md`, `docs/452-sysctl-snapshot-as-evidence-artifact.md`, `spec/sysctl.plan.schema.json`, `spec/sysctl.receipt.schema.json`, `spec/sysctl.snapshot.schema.json`, `spec/sysctl.event.schema.json`, `docs/429-sysctl-diff-as-drift-surface.md`, `spec/sysctl.diff.schema.json`, `docs/395-drift-bundles-and-review-summaries.md`, `docs/218-configuration-transactions-and-receipts.md`.


## 184) Kernel modules are supply-chain code injection (plan them, lock them down, alarm on drift)

Runtime module loading is convenient — and also one of the cleanest ways to inject new privileged code into a running system. If module mutability is ambient, measured boot and verified execution lose meaning.

Greenfield advantage: declare allowed modules by policy, preload required modules during activation, then raise lockdown/securelevel to block runtime loads. Emit receipts for planned loads and typed events for live monitoring and drift detection.

See: `docs/276-kernel-module-policy-and-loading-as-evidence.md`, `spec/kmod.policy.schema.json`, `spec/kmod.policy.diff.schema.json`, `docs/439-kmod-policy-diff-as-review-surface.md`, `spec/kmod.load.plan.schema.json`, `spec/kmod.load.receipt.schema.json`, `spec/kmod.event.schema.json`, `docs/230-lockdown-levels-and-securelevel.md`, `docs/395-drift-bundles-and-review-summaries.md`.



## 185) Hardware inventory should be an evidence object (supportability without fingerprint leaks)

Fleet operators always end up needing hardware truth: which NIC family, which storage controller, whether TPM exists, what USB/HID devices were attached.
If this lives only in ad-hoc scripts and log scraping, it becomes both unreliable *and* privacy-toxic (serials leak everywhere).

Greenfield advantage: emit a privacy-safe `hw.inventory.receipt` by default (digest-first, serials hashed at most), treat inventory access and export as budgeted authority, and include the receipt digest in support bundles so “what hardware is this?” never requires SSH.

See: `docs/319-hardware-inventory-and-driver-binding-as-evidence.md`, `spec/hw.inventory.receipt.schema.json`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/298-authority-budgets-and-permission-drift-alarms.md`.


## 186) Don't switch generations blind: preflight hardware compatibility gates prevent remote bricks

Atomic upgrades and rollbacks help only if you can still reach the box. The common failure mode is a driver/firmware regression that drops networking or storage on reboot.

Greenfield advantage: make “hardware compatibility” a typed preflight gate (`hw.compat.report`) and block activation when it would likely strand the host, unless an explicit breakglass policy grants an override. The report also becomes the postmortem artifact: “we knew this was risky and why.”

See: `docs/320-hardware-compatibility-gates-and-safe-upgrades.md`, `spec/hw.compat.report.schema.json`, `docs/112-health-gated-updates.md`, `docs/69-host-generations-bectl.md`.



## 187) Firmware updates and UEFI variables must be derived + receipted (no platform drift folklore)

Firmware and UEFI variable mutation is one of the longest-lived drift sources in real fleets: BIOS/UEFI updates performed with vendor tools, silent Secure Boot db/dbx edits, BootOrder drift, and “it updated on reboot” uncertainty. These changes are high-impact (trust roots, device stability) and are often the root cause of remote bricks.

Greenfield advantage: treat firmware as part of the platform contract. Emit a privacy-safe `fw.inventory.receipt`, model firmware updates as a typed plan/receipt that spans reboot stages, and treat UEFI variable writes (especially Secure Boot databases) as policy-gated, approval-bound operations with digest-first receipts.

Operational forcing function: Secure Boot ecosystems **rotate certificates and CAs** (e.g. 2011→2023 refreshes; certificate expiry windows) and some Linux install media have been impacted by shim signing key transitions. If DeriveBSD bakes the lane in from day‑0, key refresh becomes a normal rollout (planned UEFI var updates + inventory verification) instead of a panic incident.

See: `docs/321-firmware-updates-and-uefi-variables-as-evidence.md`, `docs/336-uefi-capsules-esrt-and-fwupd-practice-notes.md`, `docs/337-secure-boot-certificate-rotation-and-fleet-trust.md`, `spec/fw.inventory.receipt.schema.json`, `spec/fw.update.plan.schema.json`, `spec/fw.update.receipt.schema.json`, `spec/uefi.var.set.plan.schema.json`, `spec/uefi.var.set.receipt.schema.json`, `docs/428-fw-inventory-diff-as-drift-surface.md`, `spec/fw.inventory.diff.schema.json`.



## 187.1) Firmware posture diffs are a required review surface (no silent platform drift)

Inventory receipts tell you what firmware is present *now*; they do not make change reviewable by themselves.

Greenfield advantage: add a small, deterministic diff artifact (`fw.inventory.diff`) that compares two inventory receipts and emits a compact change surface with a few risk flags (bootchain changed, trust roots changed, etc.).
This makes firmware/UEFI posture drift gateable and exportable, and prevents Secure Boot database edits and BIOS updates from becoming “it changed at some point” incidents.

See: `docs/428-fw-inventory-diff-as-drift-surface.md`, `spec/fw.inventory.diff.schema.json`, `spec/fw.inventory.receipt.schema.json`, `docs/395-drift-bundles-and-review-summaries.md`.


## 188) Network topology must be derived + receipted (routes and pf are not folklore)

Most fleets accumulate networking folklore:

- emergency `ifconfig`/route changes that never make it back into configuration
- pf hotfixes applied by hand and later overwritten
- “it worked until reboot” mysteries (DHCP/RA/WiFi side effects)
- remote bricks caused by unconfirmed topology changes

Greenfield advantage: treat host networking substrate as a **derived operation** with typed plans/receipts and explicit drift events. Keep the FreeBSD primitives (ifconfig, routing, pf anchors), but make the lifecycle auditable and rollbackable.

See: `docs/322-network-topology-and-firewall-as-derived-operations.md`, `spec/net.topology.plan.schema.json`, `spec/net.topology.receipt.schema.json`, `spec/net.topology.event.schema.json`, `docs/67-pf-anchors-per-instance.md`, `docs/281-network-egress-broker-and-consent.md`, `docs/286-inbound-listen-broker-and-firewall-leases.md`.



## 189) `/dev` views must be derived + receipted (devfs rulesets are not folklore)

Many sandbox escapes and least-privilege failures come from **ambient device nodes**: the jail or VM was “locked down”, but `/dev` still contained handles into privileged kernel surfaces (packet capture, raw disks, HID injection, GPU control ioctls). FreeBSD’s `jail(8)` is explicit: devfs exposure determines whether jail isolation is meaningful, and devfs rulesets exist to constrain it.

Greenfield advantage: treat `/dev` visibility as a **compiled artifact** and make it auditable. Compile promise profiles + device grants into a `devfs.view.plan`, emit a `devfs.view.receipt` on apply, and treat drift (unexpected nodes) as incident-grade via `devfs.view.event`. This turns “what device nodes did this service actually have?” from log folklore into a stable, reviewable receipt.

See: `docs/323-devfs-views-plans-and-receipts.md`, `docs/278-device-grants-and-devfs-rulesets.md`, `spec/devfs.view.plan.schema.json`, `spec/devfs.view.receipt.schema.json`, `spec/devfs.view.event.schema.json`.



## 190) Key distribution is a transparency problem (key directories + minimal tlogs)

Even if artifact bytes are perfectly signed and verified, the system can still be subverted if **key material and key metadata** can change silently (release authority keys, witness rosters, trust bundles, publisher identity bindings).

Greenfield advantage: treat key directories as first-class, signed artifacts and (optionally) require they be **logged** in a minimal transparency system so monitors can detect unexpected key changes.

See: `docs/324-transparent-key-directories-and-minimal-tlogs.md`, `docs/260-release-authority-policy-and-key-management.md`, `docs/304-trust-bundles-and-ca-injection-as-artifacts.md`, `docs/131-sigsum-lightweight-transparency.md`.



## 191) Rootless jails (unprivileged compartments without user namespaces)

Linux rootless containers made “sandbox as a normal user” boring and safe-by-default.
FreeBSD jails are a stronger primitive than chroot, but jail creation is ordinarily a privileged operation.
However, **hierarchical jails** (`children.max`) and the “child jails can’t be less restrictive than their parents” rule provide an underused shape for *delegation-by-confinement*.

Greenfield advantage: bake in a **lease-backed jail broker** that can hand unprivileged users a bounded compartment namespace (strict profile + budgets + devfs view), so developers can spawn disposable child jails without host-root and without turning jails into an ambient escape hatch.

See: `docs/325-rootless-jails-and-unprivileged-compartments.md`, `docs/150-jail-profiles-and-allowlist-knobs.md`, `docs/232-service-promise-profiles.md`, `docs/281-network-egress-broker-and-consent.md`, `docs/323-devfs-views-plans-and-receipts.md`.




## 192) Learn network policy by observing real flows (audit mode → reviewable diffs)

Deny-by-default networking only becomes usable if operators can cheaply discover what a workload *actually needs* (without permanently running in a permissive mode).

Other ecosystems converged on an observe→summarize→generate workflow:
- Cilium supports a policy **audit mode** that logs connections that would have been dropped by policy.
- Kubescape captures a “network neighborhood” summary and generates Kubernetes NetworkPolicy from it.
- Calico can add log rules to reveal unhandled traffic patterns.

Greenfield advantage: DeriveBSD already emits `net.flow.receipt` evidence for brokered egress. Bake in a `derive learn net` workflow that aggregates flow receipts (and optional DNS query receipts) into a compact `net.flow.summary`, then emits a **candidate `net.egress.policy` patch** expressed in *named classes* (not brittle IP allowlists). Require review before enforcement, and feed the deltas into drift alarms (“this unit started talking to a new hostname”).

See: `docs/328-learned-network-policies-from-flow-receipts.md`, `docs/281-network-egress-broker-and-consent.md`, `spec/net.flow.receipt.schema.json`, `docs/305-dns-mediation-and-hostname-binding.md`, `spec/net.dns.query.receipt.schema.json`.

## 193) Confidential microVMs that can *prove* what they are (TEE attestation as a first-class lane)

Confidential-computing TEEs (AMD SEV‑SNP, Intel TDX, Arm CCA) are increasingly the real-world way to run workloads in an environment where the host/hypervisor isn't fully trusted.

Most systems bolt this on as vendor-specific plumbing. Greenfield advantage: model TEEs as another **evidence lane**. Define reference values, accept raw evidence as digests, and emit verifier receipts that policy can reason about (identity issuance, secret release, rollout gates).

See: `docs/330-confidential-microvms-and-tee-attestation-as-evidence.md`, `docs/331-tee-attestation-in-practice-snp-tdx-and-verifier-services.md`, `spec/tee.attestation.receipt.schema.json`.





## 194) Keyless signing must be bundle-first (offline verification is an operability requirement)

Keyless signing reduces key-management pain by binding ephemeral signing keys to OIDC identities (Fulcio) and logging signing events (Rekor). But many "modern" verification flows quietly depend on online lookups for trust roots, log keys, or inclusion details.

Greenfield advantage: treat verification material as content. Bake a **bundle-first** posture where portable artifacts can carry the verification bundle and a pinned trusted-root digest, so offline fleets can still verify deterministically.

See: `docs/290-keyless-signing-and-publisher-identity-receipts.md`, `docs/333-sigstore-bundles-and-offline-verification.md`, `spec/publisher.identity.receipt.schema.json`, `spec/sigstore.bundle.schema.json`.



## 195) Supply-chain metadata needs a queryable knowledge graph (GUAC-style)

SBOMs, VEX, provenance, test receipts, and identity receipts are only useful if operators can ask: "where is this deployed?" and get a fast, explainable answer.

Greenfield advantage: bake in a **local-first artifact knowledge graph** derived from verified evidence objects. This becomes a stable `derive query ...` surface and prevents the common outcome where security metadata exists but no one can operationalize it.

See: `docs/334-artifact-knowledge-graph-and-supply-chain-queries.md`, `docs/168-sboms-and-vex-as-evidence.md`, `docs/246-causality-graphs-and-minimal-evidence-bundles.md`.



## 196) Treat RPC surfaces as digest-bound contracts (Singularity lesson)

Most systems let RPC surfaces drift silently: a new method lands, policy doesn’t notice, and ambient authority grows.

Greenfield advantage: treat each cross-compartment interface as a **contract** (schema/IDL digest) included in the compiled runtime manifest, and make policy key on that digest. This makes “what new calls became possible?” a first-class diff surface.

See: `docs/339-singularity-manifests-and-contract-channels.md`, `docs/183-object-capability-rpc.md`, `docs/106-blast-radius-diff.md`.


## 197) Capability IPC is simplest when the endpoint *is a handle* (Doors lesson)

The cleanest local authority story is “if you don’t have the handle, you can’t call.” Solaris/illumos Doors are an underused example: the RPC endpoint is literally a **file descriptor**.

Greenfield advantage: standardize FD-first broker interfaces (portals, leases, crypto ops) so capability handoff uses the existing OS primitive: pass a handle.

See: `docs/341-doors-lightweight-capability-rpc.md`, `docs/179-portals-and-powerbox.md`, `docs/196-capability-activation-and-escrow.md`.


## 198) File-shaped control planes stay debuggable (Inferno lesson)

Inferno’s “resources as files + namespaces” framing highlights a practical win: a file-like API surface is debuggable with ordinary tools and composes naturally with capability handles.

Greenfield advantage: prefer **file-shaped broker APIs** for privileged control planes (introspection, leases, policy query/explain) and keep them local-first, with explicit transports only when needed.

See: `docs/340-inferno-styx-and-distributed-namespaces.md`, `docs/215-structured-event-log-as-evidence.md`, `docs/229-evidence-spine-overview.md`.


## 199) Self-healing must be measurable: restart budgets + restart receipts (MINIX lesson)

Systems that “auto-restart” without evidence often just hide flapping. MINIX 3’s reincarnation idea is better read as a discipline: components should be restartable because their state boundaries are explicit.

Greenfield advantage: bake in restart budgets and restart receipts for critical subsystems (hypervisor workers, brokers, update appliers), then use that evidence in health gates and incident bundles.

See: `docs/342-minix-self-healing-and-reincarnation.md`, `docs/214-service-supervision-health-as-evidence.md`, `docs/112-health-gated-updates.md`.



## 200) Capability kernels show how to make delegation mechanically checkable (KeyKOS/EROS)

KeyKOS and EROS are “capabilities all the way down” systems. Their practical lesson for DeriveBSD isn’t to become a microkernel — it’s that confinement/revocation/delegation become *operationally simpler* when there’s a single blessed packaging + launch mechanism and revocation happens through indirection.

Greenfield advantage: keep DeriveBSD’s authority model intentionally capability-shaped (leases, portals, attenuating tokens), and make authority graphs diffable artifacts (“what new delegation edges appeared?”).

See: `docs/343-keykos-eros-capability-kernel-lessons.md`, `docs/182-capability-leases-and-revocation.md`, `docs/140-capability-routing-manifests.md`.

## 201) Component manifests make least-authority operable (Fuchsia lesson)

Fuchsia’s Component Framework treats the “unit manifest” as the main authority boundary: components declare what they use/expose/offer, and the system routes capabilities explicitly.

Greenfield advantage: treat `derive.unit` as the single declaration surface for service authority and compile it into caproute + contract digests, so authority changes stop hiding in side-config.

See: `docs/344-derive-unit-manifests-and-capability-routing.md`, `docs/140-capability-routing-manifests.md`, `spec/derive.unit.schema.json`.


## 202) Immutable object stores + revocable name indirection scale surprisingly well (Amoeba lesson)

Amoeba’s Bullet server stored immutable files and handed out capabilities; its directory server mapped names to *sets* of capabilities (replicas).

Greenfield advantage: treat names (channels, aliases, “current release”) as indirections over digest-bound objects, and model redundancy explicitly (capability sets / multi-origin) so replication and revocation are explainable.

See: `docs/345-amoeba-bullet-server-and-capability-directories.md`, `docs/46-cache-trust-model.md`, `docs/182-capability-leases-and-revocation.md`.


## 203) “Isolation + exposure + responsibility” is the real resource story (Nemesis lesson)

Limiting resources is not enough. The important discipline is:
- isolate contention
- expose usage
- charge it to a declared budget/lease

Greenfield advantage: make resource spend a policy-visible capability, and treat un-attributable resource use as a design bug.

See: `docs/346-nemesis-isolation-exposure-responsibility.md`, `docs/247-resource-budgets-and-limits-as-evidence.md`.


## 204) Checkpointable systems make recovery normal (orthogonal persistence lessons)

Orthogonally persistent systems show that “recovery” stops being a special case when consistent checkpoints and durable identities are built in.

Greenfield advantage: tighten DeriveBSD’s state-dataset model so privileged brokers have explicit checkpoint boundaries, migration receipts, and retention budgets.

See: `docs/347-orthogonal-persistence-and-checkpointed-systems.md`, `docs/217-state-datasets-and-migrations-as-evidence.md`.


## 205) Meta-engineering is an ecosystem feature: enforce small, typed, revocable surfaces

Lots of systems rot because features land as ad-hoc knobs and ambient authority.
DeriveBSD can bake in the opposite: every major feature must identify its contract surface, authority deltas, evidence outputs, and rollback story.

Greenfield advantage: use a uniform rubric for RFCs so “operable, explainable, least-authority by default” stays true as the archive grows.

See: `docs/348-design-review-rubric-and-feature-intake.md`, `docs/98-archive-hygiene.md`.



## 206) Write-once content-addressed evidence vault (Venti/Fossil lessons)

Plan 9’s Venti/Fossil model shows how to make rollback history and forensics *structurally hard to destroy*:
hash-addressed blocks, cheap snapshots, and retention via name indirection.

Greenfield advantage: make “support bundles, trace slices, apply receipts” live in an explicit WORM-ish lane instead of ad-hoc log files.

See: `docs/350-venti-fossil-write-once-archive-store.md`, `docs/229-evidence-spine-overview.md`.


## 207) Supervision trees + restart intensity as a shared vocabulary (Erlang/OTP lessons)

Reliability needs a *small, lintable vocabulary* for restart behavior.
OTP’s supervision tree semantics (strategy + restart intensity) map cleanly onto DeriveBSD’s restarter model.

Greenfield advantage: avoid bespoke restarter folklore and make flapping measurable (and policy-gated).

See: `docs/349-supervision-trees-and-restart-strategies.md`, `docs/239-service-lifecycle-restarters-and-repo.md`.


## 208) Crash-only services + MTTR-first operations (Crash-only / ROC lessons)

Operators do better when “recover” is the default action and is designed-in:
one way down, one way up; micro-reboots; explicit durable state.

Greenfield advantage: bake “recovery semantics + recovery receipts” into every privileged service contract.

See: `docs/352-crash-only-and-roc-for-system-services.md`, `docs/217-state-datasets-and-migrations-as-evidence.md`.


## 209) Remote object capabilities without bearer-token drift (CapTP / OCapN lessons)

If DeriveBSD ever grows cluster control planes or remote portals, we should not regress into “god APIs + copied tokens.”
CapTP/OCapN-style transport treats remote authority as object references with explicit attenuation and revocation.

Greenfield advantage: define a safe remote authority lane early, so the ecosystem doesn’t backslide into ambient naming.

See: `docs/353-captp-ocapn-remote-capabilities.md`, `docs/183-object-capability-rpc.md`.


## 210) Fix broken links aggressively (meta-engineering: trust the archive)

The archive is only useful if references remain valid.
Broken links create false confidence and rot.

Greenfield advantage: treat broken internal references as CI failures (and keep external links curated).

See: `tools/check_consistency.py`, `docs/98-archive-hygiene.md`.

## 211) Hermetic integration tests as routed capabilities (Fuchsia Realm Builder lessons)

Fuchsia’s Realm Builder shows a clean model: tests build topologies in code, then **route capabilities explicitly**
to children. Dependency injection becomes a normal, reviewable part of capability routing.

Greenfield advantage: treat integration tests as a first-class **derived artifact lane** (test realm plans + receipts),
so tests don’t devolve into ambient network scripts.

See: `docs/354-realm-builder-style-hermetic-component-tests.md`.


## 212) Userspace driver/kernel-subsystem testing (NetBSD rump kernels)

NetBSD’s rump kernel work is an under-copied ecosystem win: run unmodified kernel subsystems in userspace for fast
debugging, CI, and fuzzing. It turns “kernel testing” into a normal developer workflow.

Greenfield advantage: bake a userspace harness lane into DeriveBSD’s evidence model so kernel confidence is **receipted**.

See: `docs/355-rump-kernels-and-userspace-driver-testing.md`.


## 213) Standard contract IDL for polyglot components (WIT / Wasm component model)

DeriveBSD wants “crossings are contracts” to be mechanical. WIT offers a small, diffable IDL and canonical ABI that can
be used even when the implementation is not Wasm. This keeps interface drift visible as **digest drift**.

Greenfield advantage: pick one native contract language early so the ecosystem doesn’t fragment.

See: `docs/356-wasm-component-model-and-wit-contracts.md`.

## 214) Capability attenuation + revocation as a first-class vocabulary (membranes, indirection)

Capability-based systems only stay coherent if the ecosystem has a small set of repeatable patterns:
faceted handles, attenuating proxies, revocation-by-indirection, leases, and membranes for deep attenuation.

Greenfield advantage: require an attenuation/revocation story *at design time* so “ambient authority” can’t creep back in.

See: `docs/357-capability-attenuation-revocation-and-membranes.md`, `docs/348-design-review-rubric-and-feature-intake.md`.


## 215) Single-hash boot payloads (Unified Kernel Image / “Unified Boot Capsule”)

Bundling the boot payload into one signed/measurable object makes “what booted?” a single digest and makes TPM failures debuggable.

Greenfield advantage: treat the boot payload as a normal artifact with explicit measurement semantics and eventlog replay.

See: `docs/358-unified-boot-capsules-and-measured-boot-receipts.md`, `docs/245-boot-measurement-phases-and-pcr-separation.md`.


## 216) A/B slots as an operational discipline (even when using ZFS boot environments)

Android/ChromeOS A/B systems enforce a key discipline: updates are staged into an inactive slot and only committed after boot assessment.

Greenfield advantage: keep rollback automatic and non-negotiable, regardless of the storage substrate.

See: `docs/359-slot-based-updates-and-boot-assessment-lessons.md`, `docs/241-boot-try-counters-and-boot-assessment.md`.


## 217) Recovery environments as derived artifacts (LinuxBoot/u-root ergonomics)

Treat installer and recovery userspaces as build outputs derived from the same inputs as the host.
This keeps repair tooling from becoming a drifting, snowflake ISO.

Greenfield advantage: make “repair” a normal, receipted workflow.

See: `docs/360-derived-recovery-images-and-minimal-userspace.md`, `docs/309-installation-and-recovery-as-derived-operations.md`.


## 218) Small, synchronous boundary calls + boundary fuzzing (Tock syscall lessons)

Keeping boundary calls simple and synchronous reduces hidden kernel complexity, but the syscall boundary remains a risk surface.

Greenfield advantage: treat boundary interfaces like any other contract surface: typed, conformance-tested, and fuzzed (rump harness lane).

See: `docs/361-safe-crossing-apis-and-boundary-bugs-lessons-from-tock.md`, `docs/355-rump-kernels-and-userspace-driver-testing.md`.


## 219) Kernel UAPI as a first-class contract surface (syscalls/ioctls must be registered + diffed)

“ABI stability” arguments usually stop at syscalls, but real-world breakage and security drift also lives in:
- ioctl families
- sysctl nodes
- device nodes that expose authority
- pseudo-filesystems / magic files

Greenfield advantage: treat kernel UAPI like any other contract surface:
- register it
- digest it
- diff it
- gate “new authority” changes
- require conformance + fuzz harness plans

See: `docs/362-uapi-surface-registry-and-compat-gates.md`, `docs/106-blast-radius-diff.md`, `docs/237-lint-reports-and-contract-testing.md`.

## 220) Driver risk should be an explicit tier choice (user-mode by default; safe-language in-kernel when needed)

Drivers are the dominant source of kernel crashes and kernel-shaped exploitability.
Some ecosystems are finally converging on a practical compromise:
- keep the kernel driver core small
- push drivers to user mode when possible
- use memory-safe languages for the in-kernel subset you cannot escape
- isolate legacy blobs in driver domains

Greenfield advantage: make this an enforced, lintable posture so “it’s just easier in-kernel” stops being the default.

See: `docs/363-driver-safety-tiering-rust-and-user-mode.md`, `docs/172-device-backend-isolation-bhyve.md`, `docs/355-rump-kernels-and-userspace-driver-testing.md`.

## 221) Live patching should be a *derived artifact lane* (hotpatch capsules + receipts + expiry)

Live patching is useful for shrinking exposure windows, but it often becomes a bespoke operator art.
Greenfield advantage: if we support it, support it like Derive supports everything:
- a derived capsule
- explicit policy enablement
- timeboxed expiry
- receipts for apply/remove
- promotion gates requiring tests

See: `docs/364-live-patching-lane-hotpatch-capsules.md`, `docs/102-emergency-grafts.md`, `docs/229-evidence-spine-overview.md`.

## 222) Filesystems are “driver-shaped” risk; push them into supervised user-space servers when possible

In-kernel filesystem complexity is a reliability and security tax.
Userspace filesystem frameworks (puffs/FUSE-style) show a workable pattern:
- kernel keeps a small, bounded adapter
- filesystem logic runs in a supervised userspace server
- authority is explicit and restartable

Greenfield advantage: make filesystem servers first-class components with cap routing, budgets, and restart receipts.

See: `docs/365-userspace-filesystems-puffs-fuse.md`, `docs/349-supervision-trees-and-restart-strategies.md`, `docs/362-uapi-surface-registry-and-compat-gates.md`.

## 223) Authority graphs make “new authority” reviewable (capability graph diffs)

When authority is expressed as capabilities, drift is easiest to fight with a boring derived artifact:
an authority graph snapshot per generation, and a graph diff between generations.

Greenfield advantage: make “who can do what?” a queryable, gateable surface, not a folklore exercise.

See: `docs/366-capability-graphs-and-authority-diff-surfaces.md`, `docs/106-blast-radius-diff.md`, `docs/95-explainability-contract.md`.


## 224) System generations should be reproducible (not just packages)

Package reproducibility is table-stakes; system assemblies still drift via initrds, boot capsules, image composition, and metadata.

Greenfield advantage: add an optional determinism-check lane that produces reproducibility receipts and diff artifacts.

Also keep “known impurities” from turning into folklore: treat tolerated nondeterminism as an explicit, time-bounded policy surface (`impurity.waiver.policy` + `impurity.waiver.policy.diff`).

See: `docs/367-reproducible-generations-and-determinism-checks.md`, `docs/445-impurity-waiver-policy-diff-as-review-surface.md`, `docs/166-test-receipts-and-promotion-gates.md`.


## 225) Least-authority needs an ergonomic on-ramp (pledge/unveil → promise profiles)

OpenBSD’s `pledge(2)` / `unveil(2)` worked because the API is small and understandable.
DeriveBSD can steal the ergonomics while compiling to Capsicum-first sandbox profiles.

Also treat sandbox posture changes as a first-class drift surface: `sandbox.profile.diff` makes “new promises/egress/portal surfaces” mechanically reviewable and gateable.

Greenfield advantage: make “doing the right thing” cheaper than ambient authority.

See: `docs/368-pledge-unveil-style-promises-and-derive-profiles.md`, `docs/232-service-promise-profiles.md`, `docs/326-learned-promise-profiles-and-observation-mode.md`.


## 226) Dynamic grants must be reviewable and revocable (consent ledgers)

Portals and brokers avoid ambient authority, but they can still rot into permanent exceptions unless the user/operator can review and revoke them.

Greenfield advantage: a first-class consent ledger (review/revoke/explain/audit) prevents silent permission creep.

See: `docs/369-consent-ledgers-and-permission-review-ui.md`, `docs/210-portal-sessions-and-permission-store.md`, `docs/229-evidence-spine-overview.md`.

## 227) Treat userland contracts like kernel UAPI (registries + diffs + compat gates)

Most ecosystems only learn to manage API drift after they accumulate years of “mysterious breakage”.
The greenfield win is to treat *every stable interface surface* as a registered contract:
- compile a `contract.registry`
- diff it (`contract.diff`) in CI
- classify deltas (compatible / breaking / suspicious)
- gate “new authority” and “new parser” changes by policy

Entropy control: keep a canonical diff registry (`docs/430-diff-surface-registry.md`) and ensure each diff entry points to its primary wiring doc (gates + bundle attachment).
Also: keep `risk_flags` reason codes stable via a canonical registry (`docs/435-risk-flags-registry-and-gate-vocabulary.md`).

See: `docs/370-contract-registries-and-api-diff-gates.md`, `docs/362-uapi-surface-registry-and-compat-gates.md`, `docs/106-blast-radius-diff.md`.


## 228) Permission UX needs an “expiration story” (auto-expire unused grants)

Even with portals, dynamic grants tend to become permanent exceptions.
Android’s “auto-reset unused app permissions” is the key product insight:
**permissions you never use shouldn’t live forever**.

Greenfield advantage: make TTLs + “expire unused” first-class in the consent ledger and permission UI.

See: `docs/371-permission-center-and-authority-introspection.md`, `docs/369-consent-ledgers-and-permission-review-ui.md`, `docs/298-authority-budgets-and-permission-drift-alarms.md`.


## 229) “Blast-radius diffs” should include contracts/UAPI/resources (schema must match the claim)

A blast-radius diff that only covers filesystem/network/devices misses the most important drift:
- new RPC/portal endpoints
- new kernel UAPI surfaces
- new/default resource budgets

Greenfield advantage: keep the blast-radius schema extensible so tooling can treat these as first-class sections.

See: `docs/106-blast-radius-diff.md`, schema `spec/blast_radius.diff.schema.json`.


## 230) API levels are a practical way to freeze expectations without freezing progress

Fuchsia’s API-level framing is a useful compromise:
components target a *snapshot* of the platform surface, and the runtime enforces that the platform still supports it.

Greenfield advantage: treat “target API level” as an input to compatibility views, contract registries, and UAPI gates.

See: `docs/370-contract-registries-and-api-diff-gates.md`, `docs/105-compat-view-foreign-binaries.md`.

## 231) Diagnostics should have a single query plane (Archivist-style selectors + snapshots)

If the platform doesn’t ship a uniform diagnostics plane, ecosystems reinvent it:
- bespoke scrape endpoints
- “run this script with sudo”
- permanent debug backdoors

Greenfield advantage: a capability-gated diagnostics query surface (selectors + leases + receipted snapshots) makes “debuggability without ambient authority” the default.

See: `docs/302-structured-diagnostics-inspect-trees.md`, `docs/372-inspect-style-structured-introspection.md`, `docs/371-permission-center-and-authority-introspection.md`.

## 232) When proofs exist, they should be artifacts (digestable, replayable, policy-gated)

Formal verification is not table-stakes for an OS, but *operationalizing* proofs is.
seL4’s biggest ecosystem lesson is not just “proofs exist,” but that proofs have a clear object boundary and a replay story.

Greenfield advantage: treat proofs like other supply-chain evidence (bundles + receipts) so high-assurance lanes can be enabled without bespoke process.

See: `docs/373-proof-artifacts-and-formal-verification-lanes.md`, `docs/367-reproducible-generations-and-determinism-checks.md`.

## 233) Authority diffs should be machine-checkable (schema, not screenshots)

“Graph diff review” only stays sustainable if the diff object is stable and tooling can key policy on it.

Greenfield advantage: a first-class `authority.diff` schema keeps authority drift gateable and prevents gradual erosion into “manual review only”.

See: `docs/374-authority-diff-schema-and-review-workflows.md`, schema `spec/authority.diff.schema.json`, `docs/366-capability-graphs-and-authority-diff-surfaces.md`.

## 234) Hierarchical capability distribution is undercopied (nested init / scoped subsystems)

Flat capability graphs become unreviewable at scale.
Genode’s nested init model is a practical, under-copied lesson: subsystems should have scoped authority boundaries, not one global routing soup.

Greenfield advantage: make hierarchical subsystems first-class so review and delegation can match org/team boundaries.

See: `docs/375-genode-init-and-capability-routing-lessons.md`, `docs/344-derive-unit-manifests-and-capability-routing.md`, `docs/366-capability-graphs-and-authority-diff-surfaces.md`.

## 235) Parser drift should be its own diff surface (parsers are where bugs cluster)

“New authority” review is necessary but not sufficient: adding a new parser often adds a new high-value attack surface even if authority seems unchanged.

Greenfield advantage: define a first-class `parser.registry` and `parser.diff` so “new parsers” (and “parser broadening”) can be mechanically reviewed and policy-gated.

See: `docs/376-parser-surface-registry-and-fuzz-gates.md`, `docs/106-blast-radius-diff.md`, `docs/274-continuous-fuzzing-farm.md`.

## 236) “Untrusted bytes must be fuzzed” is a usable platform rule (ChromeOS lesson)

Security processes become real when they are *default requirements*, not tribal knowledge.
ChromeOS review guidance is blunt: non-trivial untrusted data handling must be fuzzed.

Greenfield advantage: bind fuzz harnesses to parser ids and require fuzz receipts for `parser.diff` entries tagged `new-parser` or `parser-broadening`.

See: `docs/376-parser-surface-registry-and-fuzz-gates.md`, `docs/274-continuous-fuzzing-farm.md`.

## 237) Formally proven parsers are an underrated “high assurance” wedge (EverParse)

Verified kernels are hard; verified *parsers* are a tractable, high-ROI subproblem.
EverParse demonstrates a practical path: generate binary parsers with machine-checkable safety/correctness properties.

Greenfield advantage: treat “parser proofs” like other supply-chain evidence (proof bundles + receipts) so a high-assurance parser lane can exist without bespoke process.

See: `docs/373-proof-artifacts-and-formal-verification-lanes.md`, `docs/376-parser-surface-registry-and-fuzz-gates.md`.


## 238) Deterministic multithreading is an underrated debugging lever (Dthreads/DMP)

Multithreaded nondeterminism makes bugs expensive:
- failures don't reproduce
- tests get flaky
- record/replay has to capture huge interleaving state

Greenfield advantage: offer an **optional deterministic scheduling lane** (debug/CI) that produces receipts and plugs into replay capsules.

See: `docs/377-deterministic-concurrency-lane.md`, `docs/194-debugging-by-lease-and-replay-capsules.md`.

## 239) Denials are the best policy authoring UX (denial-driven suggestion loops)

People don't converge on least-authority by hand-authoring perfect policies.
They converge by iterating. Denials (with context) are the highest-signal iteration input.

Greenfield advantage: treat denials as structured evidence and generate **reviewable policy patches** (never auto-approve).

See: `docs/378-denial-driven-policy-suggestions.md`, `docs/326-learned-promise-profiles-and-observation-mode.md`, `docs/371-permission-center-and-authority-introspection.md`.

## 240) Unikernel manifests should be treated as contracts (not runtime folklore)

Unikernel ecosystems that scale have explicit manifests declaring required resources and channels.
If those manifests drift, review has to be diffable just like other surfaces.

Greenfield advantage: treat unikernel manifests as contract sources and include them in blast-radius diffs and registry workflows.

See: `docs/145-unikernel-lane-rump-solo5.md`, `docs/94-runtime-blast-radius-contract.md`, `docs/370-contract-registries-and-api-diff-gates.md`.

## 241) Surface registries are a meta-pattern for staying sane at scale

As the system grows, the sustainable trick is not "be careful"; it's to make drift **machine-checkable**.
Registries + diffs + gates + receipts are the reusable pattern behind multiple DeriveBSD surfaces.

Greenfield advantage: require new surface classes to declare how they fit an existing registry, or why they need a new registry/diff.

See: `docs/379-surface-registry-pattern.md`, `docs/348-design-review-rubric-and-feature-intake.md`, `docs/106-blast-radius-diff.md`.


## 242) Trust boundary drift is a first-class security event (DFD / SDL lesson)

Most security failures are “boundary changed, nobody noticed”.
Threat modeling tools make **trust boundaries** explicit; DeriveBSD can go further by compiling boundaries into diffable artifacts.

Greenfield advantage: treat boundary changes as machine-checkable review surfaces (`trust.boundary.graph` + `trust.boundary.diff`) and wire them into blast-radius and parser/authority diffs.

See: `docs/380-trust-boundary-graphs-and-threat-diff.md`, `docs/106-blast-radius-diff.md`, `docs/379-surface-registry-pattern.md`.

## 243) Labels + explicit declassification are a powerful “data leakage” control (Asbestos/HiStar/Flume lesson)

Unix systems make authority explicit (permissions), but data sensitivity is usually implicit.
Asbestos/HiStar/Flume show the leverage of **labels** and **explicit downgrade/declassification**.

Greenfield advantage: adopt an optional lane that attaches `flow.label` metadata at key boundaries (imports, portals, exports) and treats downgrades as receipted transforms (`declass.request`/`declass.receipt`).

See: `docs/381-information-flow-labels-and-declassification.md`, `docs/280-origin-labels-and-quarantine-attributes.md`, `docs/251-export-policies-and-support-bundle-portal.md`.

## 244) Stable ids are the secret sauce of “reviewable drift” (registry lesson)

Registry/diff objects only stay useful when ids are stable and namespaced.
If ids churn, policies and reviewers lose their handles and drift becomes invisible again.

Greenfield advantage: standardize surface-id conventions early and reuse them across contract/UAPI/parser/authority/boundary diffs.

See: `docs/383-surface-ids-namespacing-and-stability.md`, `docs/370-contract-registries-and-api-diff-gates.md`, `docs/376-parser-surface-registry-and-fuzz-gates.md`.


## 245) In-kernel programmable runtimes are an authority + parser hazard (BPF/eBPF lesson)

BPF-style programmability is both powerful and dangerous: it moves complex verification and parsing into the kernel and makes “load a program” a privileged operation.
Many systems end up treating packet capture/tracing as “just tooling”, accidentally granting cross-process visibility and expanding kernel attack surface.

Greenfield advantage: treat BPF-like lanes as **lease-gated broker services**, and wire them into the same drift surfaces as other risky changes (UAPI registry, parser registry, authority diff, trust boundary diff).

See: `docs/384-kernel-extensibility-bpf-and-jit-risk.md`, `docs/376-parser-surface-registry-and-fuzz-gates.md`, `docs/362-uapi-surface-registry-and-compat-gates.md`.

## 246) Deprecation lifecycle is a security/operability feature (no silent removals)

Ecosystems rot when compatibility breaks are discovered by users first. The sustainable pattern is mechanical: **declare deprecation**, run migration/dual-run, then remove with receipts.

Greenfield advantage: represent deprecations as first-class objects (`deprecation.notice`) and make removals show up in the same review surfaces as authority and parser drift.

See: `docs/385-deprecation-policies-and-removal-receipts.md`, `spec/deprecation.notice.schema.json`, `docs/106-blast-radius-diff.md`.

## 247) User environments should be activations with receipts (Nix profile lesson)

The killer UX of Nix profiles is not “package install”; it is **atomic generation switches** via pointer flips, making rollback trivial and failures debuggable.

Greenfield advantage: treat UserEnv activation as a derived operation with a plan/receipt, keeping user UX reversible without expanding system authority.

See: `docs/386-userenv-activation-plans-and-receipts.md`, `docs/162-user-environments.md`, `spec/userenv.activate.plan.schema.json`, `spec/userenv.activate.receipt.schema.json`.


## 248) CHERI shows a credible path to capability-enforced memory safety in a Unix ecosystem

CHERI brings capability thinking to pointers: bounds and permissions become unforgeable hardware-enforced metadata.
For a BSD-native system, this is not just theory — CheriBSD demonstrates real “ports + base system” adaptation.

Greenfield advantage: treat CHERI as an explicit **platform lane** (conventional vs hybrid vs purecap) so compatibility and security expectations stay honest and reviewable.

See: `docs/387-cheri-capability-hardware-and-memory-safety-lane.md`.

## 249) Remote attestation only matters if admission depends on it (Keylime lesson)

Many systems collect measurements and then… do nothing with them.
Keylime’s practical lesson is that attestation becomes valuable when verifiers emit expiring receipts, and other subsystems **gate admission** on those receipts.

Greenfield advantage: make “what is attestation-gated?” a typed, diffable policy artifact.

See: `docs/388-remote-attestation-admission-and-enrollment.md`, `spec/attestation.admission.policy.schema.json`, and the drift review surface: `docs/440-attestation-admission-policy-diff-as-review-surface.md`, `spec/attestation.admission.policy.diff.schema.json`.

## 250) Chaos engineering belongs in the OS as a lease-gated lane, not as SSH folklore

Failure injection improves resilience only when it is controlled, bounded, and observable.
If the OS doesn’t provide a disciplined lane, teams reinvent chaos as ad-hoc root scripts.

Greenfield advantage: treat fault injection as temporary authority: plans are reviewed and receipts are durable evidence.

See: `docs/389-chaos-experiments-and-fault-injection-as-leases.md`, `spec/chaos.experiment.plan.schema.json`, `spec/chaos.experiment.receipt.schema.json`.

## 251) Measured boot is good; measured launch (DRTM) is an optional high-assurance wedge (TrenchBoot lesson)

Static measured boot assumes the firmware chain is good enough to begin measurement.
A DRTM (“late launch”) lane can establish a dynamic root of trust after reset using CPU features, strengthening some threat models (e.g., evil maid / early-boot tampering).

Greenfield advantage: keep it optional, but if supported, make it a first-class lane whose evidence feeds into the same receipt model.

See: `docs/390-measured-launch-and-drtm-trenchboot-lane.md`.


## 252) Crypto choices drift silently unless the OS makes them diffable (crypto registry lesson)

Crypto risk is often not "weak crypto" but **inconsistent crypto**: different defaults, hidden legacy suites, and bespoke crypto invented by apps.

Greenfield advantage: treat protocols/suites/blessed libraries/key policies as a registered surface (`crypto.registry`) and gate drift via `crypto.diff` (and optionally blast-radius diffs).

See: `docs/391-crypto-surface-registry-and-agility-gates.md`, `spec/crypto.registry.schema.json`, `spec/crypto.diff.schema.json`.

## 253) Keys should be policy objects, not secret files (non-exportable-by-default lesson)

If keys live as bytes in files, they will be copied into backups, bundles, and support artifacts.
The platform API should make key use an **operation** (sign/decrypt), not "read key bytes".

Greenfield advantage: standardize `crypto.key.policy` so key purpose, backend binding, subject selectors, and user-presence/quorum constraints are explicit and reviewable.

See: `docs/392-crypto-key-policies-and-nonexportable-handles.md`, `docs/306-crypto-operations-portal-and-split-keys.md`, `spec/crypto.key.policy.schema.json`.

## 254) Crypto agility is an artifact problem, not a code fork problem

Most ecosystems either ossify (cannot upgrade) or churn (breaking changes without discipline).
The survivable posture is: profiles + deprecations + migration windows.

Greenfield advantage: represent "legacy" as an explicit profile, require `deprecation.notice` for downgrades/exceptions, and make removals auditable via receipts.

See: `docs/391-crypto-surface-registry-and-agility-gates.md`, `docs/385-deprecation-policies-and-removal-receipts.md`.

## 255) Crypto changes belong in blast-radius review (downgrades expand authority)

Enabling a legacy suite or weakening verification can expand an attacker's viable options just like opening a firewall rule.
If crypto drift is invisible to review, policy loses.

Greenfield advantage: let the umbrella blast-radius diff include a `crypto` section so reviewers see crypto drift alongside network/parser/authority changes.

See: `docs/106-blast-radius-diff.md`, `spec/blast_radius.diff.schema.json`.


## 256) Policy changes need regression vectors (tests as the long-term memory)

Policies are the “rules of the world”. If policy changes aren’t guarded by regression vectors, every refactor is a potential authority expansion.

Greenfield advantage: make policy test suites first-class artifacts and treat passing reports as promotion evidence.

See: `docs/393-policy-tests-suites-and-mutation.md`, `spec/policy.test.suite.schema.json`, `spec/policy.test.report.schema.json`.

## 257) Mutation testing is a practical way to measure whether policy tests would catch common blunders

Access-control failures often come from tiny edits with huge consequences: widening a selector, flipping allow/deny, deleting a constraint.
Mutation testing generates small “wrong-but-plausible” policy variants and checks whether the test suite kills them.

Greenfield advantage: use mutation scores as a coverage signal for the highest-blast-radius policy surfaces.

See: `docs/393-policy-tests-suites-and-mutation.md`.

## 258) Automated reasoning complements tests for high-assurance authorization lanes

Tests cover known cases. For admission control, secrets unseal, remote assist, and other critical surfaces, it’s valuable to run analyzers that can search for unexpected permission expansions.

Greenfield advantage: treat policy analysis outputs as evidence objects and integrate them into the same diff-and-gate workflow as other drift surfaces.

See: `docs/394-policy-analysis-and-automated-reasoning.md`.

## 259) Review ergonomics is a security feature (one drift bundle beats twelve scattered diffs)

Large systems fail review not because they lack diffs, but because diffs are fragmented across tools and formats.
When security-relevant drift is “somewhere else”, it is eventually missed.

Greenfield advantage: make a **drift bundle** (`drift.bundle`) the default attachment to promotions/releases, summarizing and linking all drift surfaces (authority/UAPI/parser/contracts/trust/crypto/policy).

See: `docs/395-drift-bundles-and-review-summaries.md`, `spec/drift.bundle.schema.json`.

## 260) “New code ingestion” must be reviewable (closure diffs)

A generation update is often a dependency update.
If reviewers can’t answer “what new code exists now?”, they can’t reason about new parsers, new interpreters, or new crypto stacks.

Greenfield advantage: compare generation closures and emit `closure.diff` as a compact “what was added/removed?” artifact.

See: `docs/396-closure-diffs-and-new-code-surfaces.md`, `spec/closure.diff.schema.json`.

## 261) Drift surfaces should compose (bundles are the glue)

Registries/diffs make drift machine-checkable.
But humans still need a single starting point for review and a single object for policy to gate.

Greenfield advantage: treat bundles as the glue that composes drift surfaces into a stable review funnel.

See: `docs/395-drift-bundles-and-review-summaries.md`, `docs/379-surface-registry-pattern.md`.

## 262) Closure diffs + parser diffs form a powerful cross-check

`closure.diff` tells you what new code is present.
`parser.diff` tells you what new “untrusted bytes → structured objects” surfaces exist.
When both exist, review becomes a cross-check instead of guesswork.

Greenfield advantage: require that new untrusted parsing code shows up in *both* places (new library in closure diff; new parser surface in parser diff).

See: `docs/396-closure-diffs-and-new-code-surfaces.md`, `docs/376-parser-surface-registry-and-fuzz-gates.md`.


## 263) Pattern catalogs are a greenfield advantage (meta-engineering wins)

Older systems accumulate features without a shared language for how subsystems should look.
DeriveBSD can bake in a small set of reusable patterns (plan→apply→receipt, broker→lease→receipt, registry→diff→gate) and treat anything else as suspicious.

See: `docs/397-pattern-catalog.md`, `docs/348-design-review-rubric-and-feature-intake.md`.

## 264) Use a toolchain wedge to reduce bespoke cross-toolchains (Zig)

Cross-compilation often fails operationally because every target wants a bespoke toolchain build.
A pinned Zig bundle can act as a drop-in C/C++ toolchain driver for many targets, reducing the number of ad-hoc cross-toolchain lanes.

See: `docs/398-zig-toolchain-wedge-and-cross-compilation.md`, `docs/156-toolchain-bootstrap-rust.md`.

## 265) Make evidence queryable (osquery-shaped ergonomics, but receipted)

Receipts everywhere is only useful if operators can answer questions quickly.
Steal osquery ergonomics (tables + SQL), but prefer derived fact tables backed by evidence digests, with queries themselves emitted as receipts.

See: `docs/399-evidence-queries-and-fact-tables.md`, `docs/371-permission-center-and-authority-introspection.md`.


## 266) Underused FreeBSD networking primitives: netgraph graphs + netmap/VALE fast paths

Most OS networking ends up as a pile of scripts and implicit state. FreeBSD’s **netgraph** is a rare alternative: networking as an explicit **graph** of small nodes, which is inherently introspectable and snapshot-able.

Greenfield advantage: treat “the datapath wiring” as a compiled backend of `net.topology.plan`, and include a graph snapshot digest in receipts so drift is explainable.

If a deployment needs extreme packet rates, add an explicit **default-off** acceleration lane using **netmap/VALE** (still policy-gated and receipted).

See: `docs/400-netgraph-and-netmap-as-derived-network-fabrics.md`, `docs/322-network-topology-and-firewall-as-derived-operations.md`.


## 267) A v0 cutline prevents “design tourism” from killing the project

Greenfield OS projects often die from success: the idea archive grows faster than the shipped surface.
A crisp v0 cutline + feature tiering discipline lets DeriveBSD ship a coherent system while keeping ambitious ideas as explicit optional lanes.

See: `docs/401-v0-cutline-and-feature-tiers.md`, `docs/22-scope-and-direction.md`, `docs/98-archive-hygiene.md`.

## 268) Adapter lanes must be killable (strangler discipline for interop)

Interop is unavoidable (ports/pkg, OCI, full TUF), but “compat forever” is a trap.
Treat adapters as quarantined lanes with receipts and drift surfaces, and require an Adapter → Shadow → Replace plan (bounded deprecation + removal receipts).
Make killability mechanical via an explicit, versioned adapter posture policy (`adapter.kill.policy`) and a gateable diff surface (`adapter.kill.policy.diff`).

See: `docs/402-adapter-lanes-and-strangler-discipline.md`, `docs/444-adapter-kill-policy-diff-as-review-surface.md`, `docs/397-pattern-catalog.md`, `docs/385-deprecation-policies-and-removal-receipts.md`.


## 269) Long-term source availability is a supply-chain feature (SWHID fallback)

Reproducible builds fail in practice when upstream sources disappear. A greenfield Nix-successor should treat URL-rot resilience as first-class: lockfiles can carry archival identities (e.g., **SWHID**) and fetchers can be policy-governed multi-origin resolvers while remaining **hash-first**.

See: `docs/403-swhid-fallback-and-long-term-source-availability.md`, `docs/14-supply-chain.md`.

## 270) Boot environments should be receipt-backed generation artifacts (not just an admin trick)

FreeBSD’s ZFS boot environments are the physical lever for atomic host upgrades. DeriveBSD should make the BE ↔ generation mapping explicit, receipted, health-gated, and GC-aware so “what did we boot?” is answerable in one query.

See: `docs/404-zfs-boot-environments-as-system-generations.md`, `docs/112-health-gated-updates.md`, `docs/175-pins-roots-and-garbage-collection.md`.


## 271) A reproducible, interactive VM test driver turns integration tests into a daily habit

Unit tests are necessary, but OS projects ship quality when integration tests are *easy*: bring up VMs, run the script, and then drop into an interactive session to inspect the world when something fails.

Greenfield advantage: make the test driver itself a digest-pinned artifact, and make artifact capture (serial logs, service logs, snapshots) default.

See: `docs/188-scenario-tests-multimachine.md`, `docs/405-interactive-vm-tests-and-artifact-capture.md`.

## 272) Boot/install/GUI tests need rich artifact capture (openQA-shaped, optional lane)

Some OS failures happen before “normal tests” exist: bootloader, early boot, installer flows, or GUI surfaces. openQA’s big lesson is that these can still be automated if the harness captures the right evidence (serial logs, screenshots, video) and makes replay easy.

Greenfield advantage: treat rich capture as an *optional* lane, but bake the evidence plumbing (content-addressed logs/screenshots, receipts linking them) into the foundation.

See: `docs/405-interactive-vm-tests-and-artifact-capture.md`.

## 273) UAPI fuzz descriptors should be registry-aligned artifacts (syzkaller-shaped)

Kernel fuzzing works best when interface descriptions are explicit and maintained as part of the contract surface. syzkaller’s declarative syscall descriptions are the right shape; DeriveBSD can go further by linking descriptor/harness digests directly from `uapi.registry` entries so drift gates become mechanical.

See: `docs/362-uapi-surface-registry-and-compat-gates.md`, `docs/406-uapi-fuzz-descriptors-and-conformance.md`, `docs/274-continuous-fuzzing-farm.md`.

## 274) ABI compatibility layers are adapters, not ambient (Linuxulator / WSL 1→2 lesson)

FreeBSD’s **Linuxulator** demonstrates that syscall-translation layers can be *very* useful in a narrow band (small utilities, some third-party binaries), but they also accrete a large, subtle “kernel surface” over time.

WSL’s evolution makes the trade visible:
- **WSL 1**: compatibility layer translating syscalls
- **WSL 2**: lightweight VM running a real Linux kernel

DeriveBSD should keep the default posture simple and honest:
- run Linux workloads in **Linux microVMs** by default
- allow ABI translation only as an explicit, policy-gated **adapter lane** with clear tainting, coverage registries, and fuzz evidence

See: `docs/408-abi-compatibility-lanes-linuxulator-vs-microvms.md`.


## 275) Product profiles must be checkable objects (A–D viability without forks)

If DeriveBSD must serve multiple product shapes (fleet host, workstation, general OS, appliance/regulatory),
profile viability cannot be a vague promise. It needs a small, stable **profile artifact** that captures defaults,
required invariants, and forbidden-by-default lanes.

Greenfield advantage: make A–D a compilation target for policy defaults and gates instead of a forked codebase.

See: `docs/411-product-profiles-as-compilation-target.md`, `spec/product.profiles.schema.json`, `spec/examples/product.profiles.json`.


## 276) Data-at-rest must be first-class (key lanes + receipts), not a footnote

Many secure OS designs collapse when encryption is bolted on late: key handling leaks into logs, recovery becomes folklore,
and rollback semantics become ambiguous.

DeriveBSD should treat dataset encryption and key operations as **derived, receipted workflows** with clear lanes
(passphrase, TPM-sealed, remote unlock/breakglass, factory provisioning) so A–D postures remain viable.

See: `docs/409-zfs-encryption-and-key-management.md`, `docs/250-breakglass-and-recovery-workflows.md`.


## 277) Desktop viability requires explicit constraints early (even if desktop ships later)

“Secure workstation” viability dies quietly when core decisions assume ambient authority, direct device passthrough, or
unmediated GUI channels.

A minimal checklist of non-negotiable desktop constraints prevents accidental lock-in and clarifies what must remain
possible (trusted UI boundary, portals, device mediation, UX-safe forensics exports).

See: `docs/410-desktop-viability-checklist.md`, `docs/179-portals-and-powerbox.md`, `docs/207-input-authority-secure-attention-and-hid-risk.md`.


## 278) Context packs + discovery checks prevent archive drift (humans + LLMs)

As the archive grows, the failure mode is not missing ideas; it’s losing the *current truth*.

A compact “context pack” generator and lightweight discovery-surface checks make the archive more toolable and
reduce amnesia drift, especially with automation in the loop.

See: `docs/99-llm-runbook.md`, `tools/gen_context_pack.py`, `tools/check_discovery.py`, `docs/98-archive-hygiene.md`.


## 279) Generated doc catalogs reduce "gravity well" docs and help automation navigate

As the archive grows, a few central pages (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`) become
large “gravity wells.” That’s fine *if* we also maintain a compact, deterministic, machine-readable map.

Bake it in:

- generate a full doc catalog JSON index (`docs/_generated/doc_catalog.json`) and a short summary page (`docs/414-doc-catalog.md`)
- fail hygiene if generated discovery outputs are stale (`tools/check_generated_docs.py`)
- prefer adding metadata and wiring over adding more prose to the gravity wells

See: `docs/414-doc-catalog.md`, `docs/_generated/doc_catalog.json`, `tools/gen_doc_catalog.py`, `tools/check_generated_docs.py`.


## 280) Generated risk register indices keep failure modes explicit and navigable

A long risk register is only useful if each item names the failure mode explicitly and remains easy to scan.

Bake it in:

- generate a compact index (`docs/415-risk-register-index.md`) plus a machine-readable JSON index (`docs/_generated/risk_register.json`)
- fail hygiene if generated indices are stale, and lint that each numeric risk item has a `Risk:` line

See: `docs/266-open-questions-and-risk-register.md`, `docs/415-risk-register-index.md`, `tools/gen_risk_register_index.py`, `tools/check_risk_register.py`.


## 281) Policy must be explainable as a stable artifact (trace schema, no secrets)

Policy is only auditable if we can replay and explain decisions with stable, machine-usable traces.

Bake it in:
- define a small, stable policy trace schema (`spec/policy.trace.schema.json`)
- bind `derive explain-policy --json --trace` to that schema
- allow storing traces as content-addressed objects (`trace_digest`) to avoid bloating decision records

See: `docs/416-policy-trace-format-and-explain-surfaces.md`, `docs/93-policy-decision-records.md`, `docs/87-structured-output-contract.md`.


## 282) Platform provenance + firmware updates must be in the evidence model

If DeriveBSD can receipt packages but not firmware/UEFI state, real fleets will drift outside the model:
BIOS updates via vendor tools, silent Secure Boot db changes, and device firmware regressions become un-auditable.

Bake it in:
- platform provenance as a typed evidence object (`platform-report`)
- firmware updates as digest-first plans + receipts (`fw-update-plan` / `fw-update-receipt`)
- treat update tooling (fwupd/LVFS) as a bounded adapter lane when used

See: `docs/417-platform-provenance-and-firmware-lifecycle-as-derived-ops.md`, `spec/platform.report.schema.json`, `spec/fw.update.plan.schema.json`, `spec/fw.update.receipt.schema.json`, `docs/32-curated-references.md`.


## 283) Schema/artifact discovery surfaces should be first-class (generated indexes)

Large systems stay operable when *interfaces are discoverable*. Kubernetes uses OpenAPI-driven discovery and conventions so tooling can reason about resources mechanically.
DeriveBSD should do the same for its typed outputs: keep a generated **artifact index** mapping `kind` → schema → examples, and treat it as a critical amnesia-resistor.

- OpenAPI specification (API description + generated docs tooling): https://spec.openapis.org/oas/latest.html
- Kubernetes API conventions (mechanical consistency enabling tooling): https://github.com/kubernetes/community/blob/master/contributors/devel/sig-architecture/api-conventions.md

## 284) Profile identifiers must be canonical (aliases are fine, ambiguity is not)

A multi-shape project dies by a thousand tiny mismatches: “A” means one thing in docs, another in tooling, and a third in a spec.

Bake it in:

- define **canonical profile ids** in `spec/examples/product.profiles.json`
- keep **letter aliases** (A–D) in one place (`spec/product.profile_aliases.json`)
- have tools accept either but **normalize** to canonical ids (and detect duplicates like `A` + `fleet_host`)

See: `docs/411-product-profiles-as-compilation-target.md`, `spec/product.profile_aliases.json`, `tools/check_doc_metadata.py`, `tools/gen_product_profile_matrix.py`.


## 285) Incident timelines should be typed artifacts (not ticket comments)

Every ecosystem eventually builds “incident timelines” in spreadsheets, ticket comments, or vendor tooling.
The best versions (DFIR tooling like Plaso/Timesketch) treat a timeline as a structured object that can be searched, annotated, and shared.

DeriveBSD can bake the idea in more safely:
- compute an export-safe `incident.timeline` from bounded `event.segment` ranges (and optionally `causality.graph`)
- include the timeline digest in `incident.bundle` so support bundles ship with a one-page orientation surface
- keep the view reproducible by naming input digests + redaction transforms

See: `docs/419-incident-timelines-as-derived-artifacts.md`, `spec/incident.timeline.schema.json`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/246-causality-graphs-and-minimal-evidence-bundles.md`, `docs/32-curated-references.md`.


## 286) Context packs should be first-class amnesia resistors (generated, deterministic)

Large archives inevitably grow “gravity wells”: a few huge docs become required reading, and change becomes scary.
One antidote is a **generated context pack** that answers “what version is this, what must I read, what are A–D, and what are the top risks?”
in a single deterministic page (plus a machine-readable JSON).

Bake it in:
- generate `docs/420-context-pack.md` and `docs/_generated/context_pack.json`
- wire the pack into discovery surfaces and hygiene checks so it can't silently stale

See: `docs/420-context-pack.md`, `docs/99-llm-runbook.md`, `tools/gen_context_pack.py`, `tools/check_generated_docs.py`.



## 287) Invariants should be a stable diff surface (constitution-level drift control)

Large systems drift because the “must never break” rules get restated differently across docs, tickets, and code.
A lightweight countermeasure is to treat invariants as a **registry**: diffable, gateable, and referenceable.

DeriveBSD can keep this small and practical:
- maintain a typed `invariant.registry`
- cite invariant ids from proposals and reviews instead of rewriting the same rule
- treat changes as RFC/ADR-worthy and gate them like other registries

See: `docs/422-invariant-registry-and-design-invariants.md`, `spec/invariant.registry.schema.json`, `docs/32-curated-references.md`.


## 288) Local evidence logs should be tamper-evident (sealed, chain-verifiable)

Most systems treat local logs as “best effort.”
If an attacker (or a buggy admin script) can truncate or rewrite evidence without leaving a trace, post-incident forensics becomes story-time.

A practical, under-adopted countermeasure is to periodically **seal** logs:
- commit to the log set with hashes
- chain seals so deletion/rewrite becomes detectable
- keep verification keys exportable/pinnable (and sealing keys protected)

DeriveBSD can translate this cleanly because it already stores typed logs as addressable segments (`event.segment`).
Add an optional sealing lane that emits `event.seal.receipt` objects and make verification a first-class UX.

See: `docs/424-forward-secure-event-log-sealing.md`, `spec/event.seal.receipt.schema.json`, `docs/32-curated-references.md`.


## 289) Offline updates should be quarantine-first, promotable, and boring (mirror kits)

Air-gapped and intermittently connected environments are where update systems go to die: people disable freshness checks, trust removable media by ritual, and lose provenance.
Uptane and TUF taught a useful posture: **assume compromise**, force explicit metadata roles, and make rollback/freeze attacks visible.

DeriveBSD can bake an operator-friendly offline path:
- make a portable **mirror kit** (tree or signed bundle) containing channel metadata + required artifacts
- include a typed kit manifest so operators can list/verify contents deterministically: `mirror.kit.manifest`
- **import into quarantine** (never active), verify everything, and emit a typed receipt
- **promote** into a local channel only after policy gates pass (transactional + reversible), and emit a typed receipt

Greenfield advantage: don't leave this as shell scripts. Make the flow Plan→Receipt so it's explainable, exportable, and gateable like other supply-chain operations:
- `mirror.import.plan` → `mirror.import.receipt`
- `mirror.promote.plan` → `mirror.promote.receipt`

Primary references:
- Uptane Standard (Design and Implementation): https://uptane.org/docs/2.1.0/standard/uptane-standard
- TUF specification: https://theupdateframework.github.io/specification/latest/
- RAUC bundles: https://rauc.readthedocs.io/en/latest/basic.html
- OSTree static deltas (offline deltas): https://ostreedev.github.io/ostree/copying-deltas/

See: `docs/273-airgap-mirror-kits-and-sneakernet-updates.md`, `docs/447-mirror-kit-manifest-as-evidence-artifact.md`, `spec/mirror.kit.manifest.schema.json`, `spec/mirror.import.receipt.schema.json`, `spec/mirror.promote.receipt.schema.json`, `docs/32-curated-references.md`.


## 290) Keep microVM control planes host-local (don't build Kubernetes accidentally)

MicroVMs are a great isolation primitive, but the trap is turning "launch a VM" into a distributed system:
schedulers, reconciliation loops, service discovery, identity planes, networking stacks, and state databases.

DeriveBSD's value is the **local authority boundary**:
- verify what is about to run (digests + signatures)
- enforce a policy decision (least authority + bounded interop)
- emit receipts/evidence so incidents are explainable

Fleet-wide orchestration belongs outside the OS as an **adapter lane** that submits digest-bound plans to each host and consumes host receipts as the source of truth.

See: `adrs/ADR-0040-microvm-orchestration-host-local.md`, `docs/402-adapter-lanes-and-strangler-discipline.md`, `docs/229-evidence-spine-overview.md`.



## 291) Make VM launch a first-class evidence join key (Plan→Receipt, even on denial)

Most hypervisors treat “start a VM” as a side effect: mutable state + log lines.
That makes incidents miserable: *who launched what, under which policy, with which bytes?* becomes archaeology.

DeriveBSD can keep the runtime boundary coherent by treating launches like builds:
- take a typed plan (`microvm.launch.plan`) that binds instance id + manifest digest + policy digest
- verify/enforce in `derive-vmmd`
- emit a typed receipt (`microvm.launch.receipt`) **even when denied** (denial is evidence)
- cross-link any temporary authority used during launch via `lease.use.receipt` digests

This small contract makes fleet orchestration safely external: orchestration submits plans; hosts emit receipts as the source of truth.

See: `docs/455-microvm-launch-plans-and-receipts.md`, `docs/29-vm-control-plane.md`, `docs/229-evidence-spine-overview.md`, `spec/microvm.launch.plan.schema.json`, `spec/microvm.launch.receipt.schema.json`.



## 292) Make launch idempotent by identity + plan digest (no surprise restarts)

Retries happen: flaky networks, retried RPCs, “run the command again”, and fleet controllers that reconcile desired state.
If the host control plane treats every submission as “restart”, incidents become chaos and receipts lose meaning.

A small, conservative rule set keeps all product shapes coherent:

- make `instance.instance_id` a stable, namespaced identity string
- make `plan_digest` the content identity (hash JCS-canonical JSON)
- be strict-idempotent on `(instance_id, plan_digest)`:
  - same digest → `already-running` (no restart)
  - different digest → deny (`instance-id-collision`)

Upgrades/replacements become explicit (new identity or a future stop/replace Plan→Receipt), which is cheaper than forking semantics later.

See: `adrs/ADR-0041-microvm-instance-idempotency.md`, `docs/455-microvm-launch-plans-and-receipts.md`, `docs/80-canonical-json-hashing-jcs.md`.




## 293) Make stop a first-class evidence surface (graceful vs force, bounded, no silent kills)

If launch is evidence but stop is an ad-hoc backend command, incidents still turn into archaeology:
*who stopped it, under which policy, and what was actually running then?*

Treat stop the same way as launch:
- take a typed plan (`microvm.stop.plan`)
- authorize it in the host-local control plane (`derive-vmmd`)
- emit a typed receipt (`microvm.stop.receipt`) **even on denial/failure/timeout**

Keep the semantics small and implementable:
- default to `mode: graceful` with a bounded `timeout_ms`
- make `mode: force` explicit (terminate/destroy the backend instance)
- allow an optional safety guard `expect_running_plan_digest` to prevent accidental stops after explicit replacement/identity transitions

This keeps A–D coherent: fleets can reconcile safely, workstations can stop AppVMs reliably, and appliances/regulatory deployments keep the stop surface auditable.

See: `adrs/ADR-0042-microvm-stop-semantics.md`, `docs/455-microvm-launch-plans-and-receipts.md`, `docs/29-vm-control-plane.md`, `docs/229-evidence-spine-overview.md`, `spec/microvm.stop.plan.schema.json`, `spec/microvm.stop.receipt.schema.json`.



## 294) Make content identity mechanically checkable (sha256(JCS(plan)) + guardrails)

"Plan digest" only works as an idempotency key and forensic join key if every implementation computes the *same bytes* and the *same digest*.
If the algorithm is left implicit, drift is inevitable: tools choose different hashes, backends serialize JSON differently, and receipts stop being comparable.

Make the rule explicit and test it:
- canonicalize plan JSON with RFC 8785 JCS
- compute `plan_digest = sha256(utf8(JCS(plan)))`
- require receipts to bind that digest
- add a CI check so examples can't silently drift

See: `adrs/ADR-0043-microvm-plan-digest-sha256.md`, `docs/80-canonical-json-hashing-jcs.md`, `tools/check_microvm_example_plan_digests.py`, `spec/examples/microvm.launch.plan.json`, `spec/examples/microvm.launch.receipt.json`.




## 295) Record host↔guest IO channels as runtime evidence (endpoints are not identity)

MicroVM launches routinely attach host↔guest IO crossings:
- a managed console (nmdm/stdio)
- virtio-console ports (logs/health pings)
- vsock endpoints (control RPC, brokers, guest agents)

If receipts don't record which channels were attached, incidents become guesswork:
- "could someone have accessed a console?"
- "what control channel existed?"
- "were structured logs available?"

Make the crossings explicit and queryable:
- `microvm.launch.receipt` may include `assigned.io_channels` describing attached channels
- keep the list minimal (kind + role + endpoint hints)
- treat endpoints like vsock `cid:port` as **ephemeral evidence**, not stable identity
- stable identity remains `instance.instance_id` (plus `plan_digest` for idempotency)

See: `adrs/ADR-0044-microvm-io-channels-in-receipts.md`, `spec/microvm.launch.receipt.schema.json`, `docs/455-microvm-launch-plans-and-receipts.md`.




## 296) Make denials/failures queryable (reason codes are the spec surface)

Receipts are only useful in incident tooling if they can answer *why* without log archaeology.
A free-form message is not a stable API: automation can’t branch on it and humans can’t reliably search it.

For microVM lifecycle operations:
- when an operation is `denied`, `failed`, or `timeout`, the receipt must include a non-empty `reasons[]` list
- `reasons[].code` is the stable, machine-readable surface (kebab-case; optionally namespaced with dots)
- `reasons[].message` is for humans

This keeps A–D coherent: fleets can reconcile, workstations can explain, and appliances can prove what happened.

See: `adrs/ADR-0045-microvm-receipt-reason-codes.md`, `spec/microvm.launch.receipt.schema.json`, `spec/microvm.stop.receipt.schema.json`.





## 297) Treat reason codes like a registry, not a suggestion

Reason codes are a stable API surface. If new codes are invented ad-hoc, drift is inevitable:

- different product shapes (A–D) end up with different words for the same failure
- automation forks on message strings
- incident tooling becomes non-deterministic

Use a single registry and enforce it mechanically:

- keep the vocabulary in one place: `docs/456-microvm-receipt-reason-code-registry.md`
- require example receipts to only use registered codes (guardrail: `tools/check_microvm_reason_code_registry.py`)
- when you need a new code, update the registry *and* add an example that demonstrates it

See: `adrs/ADR-0046-microvm-reason-code-registry.md`, `docs/456-microvm-receipt-reason-code-registry.md`.


Last updated: 2026-03-04r185
