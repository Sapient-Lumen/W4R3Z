# DeriveBSD archival evidence map

This map distinguishes source observations from carried engineering claims. Paths resolve within the proposed preserved layout. Line ranges describe the reviewed supplied files; SHA-256 values pin those bytes. Original ZIP identities are in [ARCHIVE-MANIFEST.json](ARCHIVE-MANIFEST.json).

## Shared project framing

- The early [README](versions/rev0185/contents/README.md), lines 3–23, calls this a FreeBSD-first design archive and states its pipeline and intended invariants.
- The early [vision](versions/rev0185/contents/docs/00-vision.md), lines 3–23, describes the intended BSD substrate. These are design goals, not deployment evidence.
- The [Derive core](versions/rev0185/contents/docs/02-derive-core.md), lines 3–50, describes an immutable identity chain and typed operational evidence.

## Snapshot claims

### rev0185 → 2026-03-04r185

Thin wrapper schemas pin force-stop and denied-stop examples while referring back to the shared microVM stop contracts.

CHANGELOG.md lines 3–6; wrapper schemas lines 3–20 and 3–33. Observed: both wrapper files refer to the common schema and pin example values. Not independently established: the historical validation result implied by the filename.

- [README.md](versions/rev0185/contents/README.md) · SHA-256 `8f3f5f5dd7c59d6af159dd4551d719b038eb25f091b3c1567d4eb7e6c1ca16a0`
- [CHANGELOG.md](versions/rev0185/contents/CHANGELOG.md) · SHA-256 `f91602252acb6e294e338de59501c9a42a389e98104a9d74fd985486c896436f`
- [spec/microvm.stop.plan.force.schema.json](versions/rev0185/contents/spec/microvm.stop.plan.force.schema.json) · SHA-256 `5962568f7901c5c46cbe54f5b9b67d4bc22ca29dac74c9c448238d8b758ebeaa`
- [spec/microvm.stop.receipt.denied.schema.json](versions/rev0185/contents/spec/microvm.stop.receipt.denied.schema.json) · SHA-256 `d265780f637fe4357c5246573ba7ebcea6d500a515a15907d827585b7a040482`
- [spec/examples/microvm.stop.plan.force.json](versions/rev0185/contents/spec/examples/microvm.stop.plan.force.json) · SHA-256 `88b79163ad83e7ad094a04ff43dded987efe44a0953228f2fab90145e7e32a11`
- [spec/examples/microvm.stop.receipt.denied.json](versions/rev0185/contents/spec/examples/microvm.stop.receipt.denied.json) · SHA-256 `c2ea40cd2b7192603cfe4d733a243776d6cf48cfdf2903ffa4bff0ab1d1278b5`

### rev0251 → 2026-03-09r254

A typed follow-up receipt describes metadata-only reverification of the same accepted stronger packet-capture export, preserving its remote identity and protection context.

README.md line 124 and CHANGELOG.md lines 1–5 identify r254. The focused document lines 34–71 defines metadata-first reverification of the same accepted packet object. Not independently established: an actual export or remote probe.

- [README.md](versions/rev0251/contents/DeriveBSD-rev0251-2026.03.09.17.32-metadataprobereverification/README.md) · SHA-256 `d7173f913912ed76f2360e3d4f322e8e29c06e20f581c04934ad6e0f54189ae6`
- [CHANGELOG.md](versions/rev0251/contents/DeriveBSD-rev0251-2026.03.09.17.32-metadataprobereverification/CHANGELOG.md) · SHA-256 `dd0eac6ce315a63729ef39c4622dfccb08f1250904d7441a779d67f112100257`
- [docs/525-packet-capture-strong-export-remote-reverification-boundary.md](versions/rev0251/contents/DeriveBSD-rev0251-2026.03.09.17.32-metadataprobereverification/docs/525-packet-capture-strong-export-remote-reverification-boundary.md) · SHA-256 `7934bb4f77c3627e6af2518e3a925c067d65411395fe22ba77c6302331d4cd49`
- [spec/transport.reverification.receipt.schema.json](versions/rev0251/contents/DeriveBSD-rev0251-2026.03.09.17.32-metadataprobereverification/spec/transport.reverification.receipt.schema.json) · SHA-256 `17d82ef92dbf81aa4284830f6c3789353e5913c7cb1a60f150af53ff9af06f07`
- [spec/examples/packet.capture.export.transport.reverification.receipt.profile.json](versions/rev0251/contents/DeriveBSD-rev0251-2026.03.09.17.32-metadataprobereverification/spec/examples/packet.capture.export.transport.reverification.receipt.profile.json) · SHA-256 `8fefe112eb2759b50a8450f7b18c8e08c1804dc95aa98ba572fb797f715457c0`

### rev0307 → 2026-03-19r307

Relay locator values are constrained by their declared kind: URI hints remain URI-shaped, while portal-object, object-path and opaque values remain non-URI-shaped.

CHANGELOG.md lines 3–7 and the focused document lines 23–41 describe locator-kind/value coherence. The document leaves provider-specific syntax open. Not independently established: a working relay backend.

- [README.md](versions/rev0307/contents/DeriveBSD-rev0307-2026.03.19.14.32-relaylocatorkindvaluegrammar/README.md) · SHA-256 `cf9eb0ca4c85787ad649275ce2e305344226ce617b2449ef0bcfe1bdfef9c76b`
- [CHANGELOG.md](versions/rev0307/contents/DeriveBSD-rev0307-2026.03.19.14.32-relaylocatorkindvaluegrammar/CHANGELOG.md) · SHA-256 `9441b022715e6ca58a75ef98ab1b9d0fadf2c2de8508b5e54a07a032c9f8791f`
- [docs/577-publish-session-relay-remote-locator-values-follow-locator-kind.md](versions/rev0307/contents/DeriveBSD-rev0307-2026.03.19.14.32-relaylocatorkindvaluegrammar/docs/577-publish-session-relay-remote-locator-values-follow-locator-kind.md) · SHA-256 `ea7da45f78f651e64b5e0bf149f8fc71310b0f1393f8717372a07ce4742233ad`
- [spec/net.publish.session.schema.json](versions/rev0307/contents/DeriveBSD-rev0307-2026.03.19.14.32-relaylocatorkindvaluegrammar/spec/net.publish.session.schema.json) · SHA-256 `4573dbc3639efd77f9bdd7766a98167d5891041a11168eb0809b3d30d36679f3`
- [spec/examples/net.publish.session.json](versions/rev0307/contents/DeriveBSD-rev0307-2026.03.19.14.32-relaylocatorkindvaluegrammar/spec/examples/net.publish.session.json) · SHA-256 `9d256f2e69628f284941fc74abdd7e722205078d45962e40b5273c06da1bf0ce`

### rev0359 → 2026-03-21r359

Incident/support bundles name the exact emergency-access authority receipt by digest when breakglass access materially participated in the incident.

CHANGELOG.md lines 3–7 and the focused document lines 47–77 explain exact breakglass-receipt joins and their conditional inclusion. Not independently established: a real emergency session or support export.

- [README.md](versions/rev0359/contents/README.md) · SHA-256 `93e4df770d68e2215be8d2000078050bf810fdb2a08c2c902b74a0390dcda815`
- [CHANGELOG.md](versions/rev0359/contents/CHANGELOG.md) · SHA-256 `8069c658eb658903b79a94c5b3e79d7b3d565e4fd0cd27c5118a8938485dd4ae`
- [docs/629-incident-bundles-carry-breakglass-proof-by-digest.md](versions/rev0359/contents/docs/629-incident-bundles-carry-breakglass-proof-by-digest.md) · SHA-256 `dcbb39f5f7d869ffacd81e2f14d18829b360389fb53af9744ad81d742754b506`
- [spec/incident.bundle.schema.json](versions/rev0359/contents/spec/incident.bundle.schema.json) · SHA-256 `7e526c0f7b0af6e6e32153e3440ddf7c33e31dbe8c39acbc743bf268360b3d55`
- [spec/examples/incident.bundle.json](versions/rev0359/contents/spec/examples/incident.bundle.json) · SHA-256 `7f720c8f426a277e3bb409375046623db6f548f4e65e1a2249ad3e7934f37901`
- [spec/examples/bundle.plan.json](versions/rev0359/contents/spec/examples/bundle.plan.json) · SHA-256 `5d05152d4d226ac0f32f9a20ee24c76b16997403bfb6e5d4654476f72c56fd63`

### rev0409 → 2026-03-22r409

A reviewed finite-collection handoff is shaped around normalized member paths and kinds, plus payload digests and byte lengths for regular files.

CHANGELOG.md lines 3–7 and the focused document lines 33–65 define the manifest floor and unresolved questions. RFC-0194 line 3 is explicitly draft; its lines 40–66 state goals/non-goals. Not established: a finalized schema family or shipped handoff implementation.

- [README.md](versions/rev0409/contents/README.md) · SHA-256 `06a3b606ccfc6ac6d87bd50d04d3578b65988fd92f5897e021f929c889df6f2d`
- [CHANGELOG.md](versions/rev0409/contents/CHANGELOG.md) · SHA-256 `ac3562b064333d1bc3c837112390fac40055675ddc038c8c7cf8a9452d93c86d`
- [docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md](versions/rev0409/contents/docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md) · SHA-256 `0e7c6d8642769813babe2e5c3ae50e8bb203b0dba367da2a3f1ec3ab327f2fa3`
- [rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md](versions/rev0409/contents/rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md) · SHA-256 `2d1374785156ab74ee75bad3c4eb8b3435453214caafc26f5a819920424437b9`

### rev0452 → 2026-03-23r452

Supplementary breakglass evidence may carry a typed metadata-only re-check of an exact accepted case-object revision when an adapter can honestly observe it.

CHANGELOG.md lines 3–6 and the focused document lines 22–67 make metadata-only re-checks conditional on what an adapter can observe; scheduled reverification is not required. Not independently established: a live case-system adapter.

- [README.md](versions/rev0452/contents/README.md) · SHA-256 `efa4fe3da3f4287b106b82e3e92d32f7e2f675c802f94d424d2f444cbb11003d`
- [CHANGELOG.md](versions/rev0452/contents/CHANGELOG.md) · SHA-256 `5a6c79aed815066a18a24de8d7dae15223581dd29f17e80cc5ee1b71e8a8f1b9`
- [docs/721-breakglass-supplementary-accepted-case-object-proof-stays-metadata-only-reverifiable-when-visible.md](versions/rev0452/contents/docs/721-breakglass-supplementary-accepted-case-object-proof-stays-metadata-only-reverifiable-when-visible.md) · SHA-256 `2b3c473a774104aa1c4cd951617c484aadbf5d462e63b2da9ba3d7a57b936069`
- [spec/examples/transport.reverification.receipt.breakglass.accepted-case-object.json](versions/rev0452/contents/spec/examples/transport.reverification.receipt.breakglass.accepted-case-object.json) · SHA-256 `325142eda809e5e76c972b18fd68d6874db9e0cd115ef2aaef78ca7e584cf9ed`
- [spec/transport.reverification.receipt.schema.json](versions/rev0452/contents/spec/transport.reverification.receipt.schema.json) · SHA-256 `17d82ef92dbf81aa4284830f6c3789353e5913c7cb1a60f150af53ff9af06f07`

### rev0501-next57 → 2026-05-30r533

A typed terminal-closure successor cutover receipt binds earlier cutover, checkpoint and reader-admission evidence, while the successor-index schema is split into a runtime contract and an exact historical fixture.

README.md final stamps and CHANGELOG.md lines 3–8 identify r533. The focused document lines 14–33 describes receipt bindings, the runtime/fixture schema split and the negative corpus. Observed: both schema files are present. Their validation claims were not rerun.

- [README.md](versions/rev0501-next57/contents/README.md) · SHA-256 `99ffe094672117936fe44e24c07de4877f9c944c6996e2ca98d99ffc17a26ff4`
- [CHANGELOG.md](versions/rev0501-next57/contents/CHANGELOG.md) · SHA-256 `7986b2125982c9718f29b48e857c600a4eddf6694c3412cde5e2a7685f4cba4a`
- [docs/788-removable-media-local-fallback-post-detach-terminal-closure-successor-cutover-and-successor-index-cutover-schema-split.md](versions/rev0501-next57/contents/docs/788-removable-media-local-fallback-post-detach-terminal-closure-successor-cutover-and-successor-index-cutover-schema-split.md) · SHA-256 `3699844a7849ae6b8ecbd5751fe609b03ddb808e46484f0c8eb8fbc587d4ab85`
- [spec/removable.media.local.post_detach.terminal.closure.successor.cutover.receipt.schema.json](versions/rev0501-next57/contents/spec/removable.media.local.post_detach.terminal.closure.successor.cutover.receipt.schema.json) · SHA-256 `c6ea55b97e0a442e0c8d898a7026ef6310f95208b50e850fd8f86825e39d24ab`
- [spec/removable.media.local.post_detach.successor.index.cutover.receipt.schema.json](versions/rev0501-next57/contents/spec/removable.media.local.post_detach.successor.index.cutover.receipt.schema.json) · SHA-256 `b662a09aa987525974216343b72f6b1b6c2c470af5db866eb503507a1966c565`
- [spec/removable.media.local.post_detach.successor.index.cutover.receipt.fixture.schema.json](versions/rev0501-next57/contents/spec/removable.media.local.post_detach.successor.index.cutover.receipt.fixture.schema.json) · SHA-256 `3f26d5eba3ad5602e8336bc91064f316de22efc08cbfe89a1b682c32f08e748f`

### rev0605 → 2026-06-18r630

The latest supplied snapshot describes a dry-run runtime that admits a byte-bound fixture repository snapshot before package catalog projection and dependency closure.

README.md lines 3–9 and final stamps identify r630 and the pre-product limit. The runtime document lines 12–24 describes the dry-run sequence and local-pointer effects; lines 32–36 reiterate the absence of a real activation backend. run.summary.json lines 12–14, 25–28 and 46 records r630, cloudtainer-local-dry-run, product gaps and no-freebsd-system-mutation. The session review lines 39–50 carries pass counts and the explicit real-host boundary; those are not fresh curator results.

- [README.md](versions/rev0605/contents/README.md) · SHA-256 `af09a2795c0926e4558b8a09e3fca9137c552cca8d7be1dd3c31781b79b1be80`
- [CHANGELOG.md](versions/rev0605/contents/CHANGELOG.md) · SHA-256 `e4d4b16dbf7fe57e3605ef59a8b03b2a803a263c69ac4f99f0b1563f2baa73d8`
- [docs/current/runtime-golden-thread.md](versions/rev0605/contents/docs/current/runtime-golden-thread.md) · SHA-256 `3146c5794ca1f0c24918c43f29972210d5543419b9b147101d8acf243c9af68c`
- [docs/current/start-here-now.md](versions/rev0605/contents/docs/current/start-here-now.md) · SHA-256 `e74c90a491329a07fa39dcd72aaf1401013a795a7de47aa3d1270ac8a11737a4`
- [validation/runtime-golden-thread/current/run.summary.json](versions/rev0605/contents/validation/runtime-golden-thread/current/run.summary.json) · SHA-256 `9501a6e5b23c1d13c0dab32d2434028c0cb9c3c7a3aa248a43bed8e5e80fbadd`
- [validation/runtime-package-repository/current/snapshot.json](versions/rev0605/contents/validation/runtime-package-repository/current/snapshot.json) · SHA-256 `29e3e08ffaf09d2df9e6ea6de4f4c4f9acfd5ec103acb18adc369fedbbdb43c5`
- [session-reviews/DeriveBSD-rev0605-2026.06.18.10.40-snapshotadmission-repositoryguard-marten-review.md](versions/rev0605/contents/session-reviews/DeriveBSD-rev0605-2026.06.18.10.40-snapshotadmission-repositoryguard-marten-review.md) · SHA-256 `3f16bbac4a5fab19ec68cfe89b6c08abde9c4d4314f133ff8f89dd6b27f60719`

## Comparison scope

The counts below compare only adjacent supplied snapshots. For comparison keys only, the single archive-name wrapper in rev0251/rev0307 is ignored; actual preserved member paths are unchanged. Counts describe file-path presence and byte changes, not semantic feature completion or uninterrupted history.

- rev0185 → rev0251: 266 added paths, 0 removed, 226 changed shared paths, 1,129 unchanged shared paths.
- rev0251 → rev0307: 191 added paths, 0 removed, 57 changed shared paths, 1,564 unchanged shared paths.
- rev0307 → rev0359: 328 added paths, 0 removed, 109 changed shared paths, 1,703 unchanged shared paths.
- rev0359 → rev0409: 175 added paths, 0 removed, 97 changed shared paths, 2,043 unchanged shared paths.
- rev0409 → rev0452: 145 added paths, 150 removed, 75 changed shared paths, 2,090 unchanged shared paths.
- rev0452 → rev0501-next57: 718 added paths, 3 removed, 136 changed shared paths, 2,171 unchanged shared paths.
- rev0501-next57 → rev0605: 486 added paths, 49 removed, 203 changed shared paths, 2,773 unchanged shared paths.

## Preservation observations

- Original byte hashes and all 18,040 extracted file hashes were rechecked without executing the supplied code.
- rev0251 and rev0307 include original wrapper directories; the other selected archives have root-level project trees.
- Preserved Python bytecode counts: rev0251 1; rev0307 4; rev0359 149; rev0409 151; rev0452 2. There are 307 carried `.pyc` files in total. Their presence is archival residue, not independent runtime evidence.
- The latest [session review](versions/rev0605/contents/session-reviews/DeriveBSD-rev0605-2026.06.18.10.40-snapshotadmission-repositoryguard-marten-review.md), lines 5–6, expressly names the package revision and semantic cube cut separately.
- The latest [fixture material](versions/rev0605/contents/validation/runtime-materials/current/packages/lighttpd-1.4.76-fixture.pkg) identifies itself as fixture bytes and sets `not_a_real_freebsd_pkg` to true.
- The [tiny PDF](versions/rev0605/contents/fixtures/removable-media/local-fallback/exfat-card/invoice.pdf) contains two harness-fixture text lines. Its embedded objects were inspected statically; it was not treated as an actual invoice.

No blanket license grant or full privacy clearance is inferred from these observations. See [archival notes](ARCHIVAL-NOTES.md).
