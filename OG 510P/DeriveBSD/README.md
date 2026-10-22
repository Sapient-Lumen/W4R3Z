# DeriveBSD

## Make a system change understandable before and after it happens

DeriveBSD asks how a computer could be assembled, changed and recovered without losing the reasons for its present state. Its proposed FreeBSD-based system starts with declared intent, pins the inputs needed to realize it, plans the work, produces an artifact, and records what activation actually changed. The aim is not merely a repeatable installation: it is a system in which “why is this here?”, “what authority permitted that?” and “what can I safely undo?” have connected answers.

The collection contains both a broad operating-system design and a narrower Python implementation of that chain. The latest supplied package, **rev0605**, carries internal cut **r630**: an executable local dry-run that resolves a finite set of fixture packages, builds a sealed directory, changes a local generation pointer and can restore its predecessor. The intended FreeBSD package resolver, boot-environment activation and bhyve workload launcher remain future backends. Understanding the implemented chain makes the larger design more concrete without mistaking the prototype for a deployed OS. [Runtime walkthrough][runtime-doc]

## Intent, identity, execution and authority are different stages

The [early Derive core][core] gives each transition its own job:

- **Spec → Lock:** turn requests into pinned sources, dependency choices and toolchain identities.
- **Lock → Plan:** make the dependency graph, environment and policy decisions explicit before execution.
- **Plan → Artifact:** realize outputs and retain their connection to the plan.
- **Artifact → activation:** admit a runtime dependency closure and select a generation rather than silently modifying an unexplained live installation.

In the [architectural vision][vision], FreeBSD supplies different mechanisms for different boundaries: jails for builds, bhyve microVMs for workloads, ZFS boot environments for generation changes, pf anchors for instance networking, and capability-oriented interfaces to reduce ambient authority. These are design assignments, not interchangeable names for isolation. In particular, an immutable build output does not by itself explain who may activate it, what mutable state survives a rollback, or which services are healthy afterward.

That is why DeriveBSD treats **operations as artifacts too**. A plan describes an intended change; a receipt records an outcome; snapshots and events supply observations. Digest references join them into an evidence graph, so an incident can lead back to the exact change, dependency closure and authority involved rather than a filename or an operator's recollection. The extensive schemas are an attempt to make these questions composable across subsystems, not themselves evidence that all those subsystems have been implemented. [Evidence architecture][evidence]

## A concrete example: what does asking for nginx actually select?

The current [microVM specification][example] asks for `nginx` and describes an `edge-nginx` instance with a digest-pinned image reference, one CPU, 256 MiB of memory and NAT networking. The runtime does not launch it. It uses the request to exercise the path from an intention to accountable local artifacts.

The [repository snapshot][snapshot] contains four fixture packages on one named platform. Their `.pkg` files are small JSON materials, not installable FreeBSD packages: the [nginx payload][payload] itself declares dependencies on `openssl` and `pcre2`. This makes a surprisingly important distinction executable: a catalog saying that a package has no dependencies must not outweigh the bytes it is supposed to describe.

The [resolver code][resolver] checks the snapshot's byte hash and canonical digest, its fixture/offline declarations and cut identity, then compares catalog platform and package sets against that snapshot. It checks package material sizes and hashes, decodes the JSON payloads, and requires agreement on the relevant identity and dependency fields. The catalog is therefore a checked projection, not an independent story about the payload. Dependency traversal includes the transitive closure, rejects missing targets and cycles, and records which packages were requested and which were pulled in as dependencies.

For this example, the build carries the fixture bytes for nginx, OpenSSL and PCRE2 into its output directory, together with a material manifest, an rc.conf-style fragment and a non-executed launch-intent document. This is useful for examining whether resolution, explanation and output agree. It is not a SAT solver, an authenticated upstream repository or a completed nginx deployment.

The development sequence makes the problem legible: r627 bound consumed fixture bytes; r628 included dependencies; r629 stopped catalog metadata from contradicting payload metadata; r630 admitted the repository snapshot before accepting its catalog projection. Each step closes a different way an apparently convincing lock could describe less than the build actually needs. [Carried development account][latest]

The [negative-case checker][regressions] also distinguishes broken metadata from a broken dependency graph. Its missing-dependency and cycle cases update the associated payload and snapshot/catalog bindings so that rejection must reach the graph problem rather than merely notice an old hash. These cases make the intended distinction inspectable in source; the carried run records remain historical evidence.

## Building again should not replace an object underneath its readers

The [artifact builder][builder] writes a fresh staging directory, copies the selected fixture materials, makes the tree read-only, and records member paths, modes, sizes and hashes. Its verification rejects symlink members, writable entries and hardlink aliases. The final artifact address depends on the plan and tree manifest. If that address already exists, the runtime checks the existing tree and reuses it in place instead of deleting and republishing it.

Local filenames and workspace locations remain useful locators, but the runtime's identity view excludes designated local-path and created-at fields while retaining semantic material and upstream digests. Artifact member paths still count, and activation generation IDs incorporate the timestamp: the checked-in path-stability regression holds the input and timestamp fixed across different workspaces, not across every later activation. The useful distinction is between where an object can be found and the material that defines it. This does not turn a digest into an external signature or an assurance that the policy behind a build is correct. [Identity implementation][identity]

## Rollback is conditional, and an interrupted change needs an interpretation

Dry-run activation selects a generation in a local state directory. The [state transition code][state] takes an exclusive mutation lock, writes a digest-bound precommit journal before creating the generation and changing the pointer, reads the pointer back, and only then clears the journal. Lock cleanup checks the device/inode identity it acquired, so an old owner does not unlink a replacement lock.

Rollback verifies its activation receipt and requires the current generation to equal that receipt's recorded result before restoring the previous pointer. An old receipt is not permission to undo a newer change. If a journal remains, further activation and rollback stop. The read-only `state-status` command compares the current pointer with the journal's before/after digests and distinguishes an applied change, an unapplied change, divergence and a malformed journal. It reports an operator-review path rather than silently choosing a recovery action.

These are substantive local state semantics, not a claim of whole-machine atomicity. The output activation receipt is written after the pointer commit and journal cleanup, so committing local state and delivering that receipt are not one indivisible operation. And even an admitted host preflight and matching imported proof reach an explicit “backend not implemented” refusal in `freebsd-real` activation. The missing backend cannot be supplied by a more elaborate receipt.

## Evidence need not mean ambient surveillance

The wider design also asks who the evidence is for. Its [four product profiles][profiles] share one proposed architecture rather than four forks. The [collection policy][collection] distinguishes bounded always-on local evidence for fleet hosts, visible user-controlled export on workstations, local retention with explicit export for general-purpose systems, and redacted bundles for appliances. Collection, access and external transport are separate decisions. A useful incident record should not quietly imply a permanent remote support channel.

This gives the work value beyond its immediate prototype: it develops an account of system change in which reproducibility, operational explanation and limits on authority have to fit together. Read the early core for that ambition, the executable walkthrough and source for the narrower mechanism, and the selected history below for the many contracts explored between them. [Monsternix](../../guides/Monsternix.md) is a useful neighboring work on exact system candidates; [BrowserRT](../BrowserRT/README.md) offers a different-scale comparison about retained bytes and failed operations. Neither shares DeriveBSD's implementation or establishes its claims.

[core]: versions/rev0185/contents/docs/02-derive-core.md
[vision]: versions/rev0185/contents/docs/00-vision.md
[evidence]: versions/rev0605/contents/docs/229-evidence-spine-overview.md
[runtime-doc]: versions/rev0605/contents/docs/current/runtime-golden-thread.md
[example]: versions/rev0605/contents/spec/examples/microvm.spec.json
[snapshot]: versions/rev0605/contents/validation/runtime-package-repository/current/snapshot.json
[payload]: versions/rev0605/contents/validation/runtime-materials/current/packages/nginx-1.26.3_1-fixture.pkg
[resolver]: versions/rev0605/contents/tools/derive_runtime.py#L724-L1145
[builder]: versions/rev0605/contents/tools/derive_runtime.py#L1390-L1672
[identity]: versions/rev0605/contents/tools/derive_runtime.py#L210-L295
[state]: versions/rev0605/contents/tools/derive_runtime.py#L1699-L2074
[regressions]: versions/rev0605/contents/tools/check_runtime_golden_thread.py#L1000-L1143
[latest]: versions/rev0605/contents/README.md
[profiles]: versions/rev0605/contents/docs/411-product-profiles-as-compilation-target.md
[collection]: versions/rev0605/contents/docs/478-evidence-collection-posture-by-profile.md

## Version shelf and preservation

### Start here

- For the project's original ambition: [rev0185 vision](versions/rev0185/contents/docs/00-vision.md)
- For the latest supplied status: [rev0605 editorial guide](versions/rev0605/README.md) and [preserved README](versions/rev0605/contents/README.md)
- For the evidence behind these summaries: [source map](ARCHIVAL-EVIDENCE.md)

The latest source explicitly calls the project **pre-product**. It describes a fixture-bound dry-run path and expressly withholds claims of an authoritative FreeBSD package index, actual `bectl` activation, bhyve launch or imported real-host proof. Its carried run summary reports `cloudtainer-local-dry-run` and `no-freebsd-system-mutation`. Those records are historical source material, not tests rerun during this curation.

### Selected history

These are selected uploads, not a complete release history or a reconstructed Git commit chain. The filename label and carried cut are separate identities.

- [rev0185](versions/rev0185/README.md) · carried `2026-03-04r185` · MicroVM example wrappers. Thin wrapper schemas pin force-stop and denied-stop examples while referring back to the shared microVM stop contracts.
- [rev0251](versions/rev0251/README.md) · carried `2026-03-09r254` · Metadata-only packet-export checks. A typed follow-up receipt describes metadata-only reverification of the same accepted stronger packet-capture export, preserving its remote identity and protection context.
- [rev0307](versions/rev0307/README.md) · carried `2026-03-19r307` · Relay locator grammar. Relay locator values are constrained by their declared kind: URI hints remain URI-shaped, while portal-object, object-path and opaque values remain non-URI-shaped.
- [rev0359](versions/rev0359/README.md) · carried `2026-03-21r359` · Breakglass authority in support bundles. Incident/support bundles name the exact emergency-access authority receipt by digest when breakglass access materially participated in the incident.
- [rev0409](versions/rev0409/README.md) · carried `2026-03-22r409` · Finite-collection manifest design. A reviewed finite-collection handoff is shaped around normalized member paths and kinds, plus payload digests and byte lengths for regular files.
- [rev0452](versions/rev0452/README.md) · carried `2026-03-23r452` · Visible case-object reverification. Supplementary breakglass evidence may carry a typed metadata-only re-check of an exact accepted case-object revision when an adapter can honestly observe it.
- [rev0501-next57](versions/rev0501-next57/README.md) · carried `2026-05-30r533` · Post-detach successor cutover. A typed terminal-closure successor cutover receipt binds earlier cutover, checkpoint and reader-admission evidence, while the successor-index schema is split into a runtime contract and an exact historical fixture.
- [rev0605](versions/rev0605/README.md) · carried `2026-06-18r630` · Fixture repository snapshot admission. The latest supplied snapshot describes a dry-run runtime that admits a byte-bound fixture repository snapshot before package catalog projection and dependency closure.

The distinctions are especially important for `rev0251` → `r254`, `rev0501-next57` → `r533`, and `rev0605` → `r630`. Original stale or compatibility metadata remains intact inside each snapshot.

### How preservation works

Each `versions/<label>/` directory contains a later editorial README, the unchanged original ZIP with its original filename, and a `contents/` tree that retains every original file-member path. The original wrapper directories in rev0251 and rev0307 remain visible inside `contents/`.

The selection contains **18,040 extracted files**. Original ZIP hashes, sizes, file counts and path mappings are listed in [ARCHIVE-MANIFEST.json](ARCHIVE-MANIFEST.json). Byte verification establishes that the preserved copies match the supplied archives; it does not authenticate the authorship, dates, correctness or engineering claims of those archives.

### Reading this as an archive

The documents, schemas, fixture examples, checkers, logs and session reviews show how the project framed its ambitions and narrowed its contracts. In particular, rev0409's finite-collection handoff remains an RFC-shaping design, and rev0452's metadata-only reverification is conditional on what an adapter can observe.

Historical runbooks, permissions, shell commands and host-proof work orders are preserved context. They are not current instructions to execute, deploy or resume experiments. No uploaded code or binary was run during this review.

### Rights and review limits

No repository-wide license grant was identified in the supplied snapshots during the bounded review. This collection does not invent a license or represent that public visibility supplies reuse rights. See [archival notes](ARCHIVAL-NOTES.md) for preservation, privacy and validation limits.

For the contributor’s later statement, see the [current owner declaration](../../LEGAL-NOTICE.txt). The observations above describe the supplied historical notices, not a replacement of third-party terms.
