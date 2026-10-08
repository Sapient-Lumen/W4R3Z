# Mission heart, missing controls, and cloudtainer waste audit

Revision: `rev0364`

## Scope

This audit deep-reads the rev0363 datacube as a self-contained cloudtainer. It asks what the archive is really trying to do, what is still missing, what should change, and which waste or severe failure modes can be corrected over time without promoting a scientific route.

## Heart of the mission

The archive is not trying to publish a final theory. Its heart is an anti-laundering, salience-preserving machine for a future salient theory of everything: keep a compact bridge atlas across QFT, gravity, entropy, information, observer / record structure, and cosmology; force every route to declare its denominator, public record, recovery burden, failure mode, and authority ceiling; and prevent source prestige, benchmark success, generated summaries, or package identity from masquerading as candidate-native evidence.

The best one-line mission is: **find the minimal generative spine by making every proposed bridge pay its recovery, witness, and rollback debts before it can climb.**

## What is missing

1. **Interoperable package metadata.** The bundle has a strong custom manifest and smoke packaging path, but it is not yet expressed as an RO-Crate / W3C PROV-style research object. Add a minimal `ro-crate-metadata.json` or equivalent provenance export only if it points at existing ledgers rather than duplicating them.
2. **Signed or attestable release provenance.** The archive has deterministic packaging, but not SLSA-like provenance or signed build attestations. A future pass should record builder identity, command transcript digest, source-tree digest, and output digest in a small release-attestation file.
3. **Software-source persistent identifiers.** Several source/software surfaces name repositories or code, but Software Heritage / SWHID style identifiers are not yet first-class. Add them only where they reduce moving-repository drift.
4. **Progress and timeout instrumentation for replay.** In this cloudtainer, individual lint, negative-replay, and schema-validation commands pass when run separately, but combined `make lint` showed timeout-prone behavior under long captured execution. Add per-step elapsed-time reporting and bounded subprocess ownership so humans know whether a check is slow, hung, or actually failed.
5. **Durable-ledger revision-stamp decoupling.** Many durable ledgers still mutate top-level `revision` fields when only release-control state changes. `FT-0356-002` already identifies this; it remains one of the highest leverage waste reductions.
6. **Template extraction for candidate-native docket families.** The candidate-native identifiability docket stack contains repeated export / reimport / lineage / release-seal language. Treat shared boilerplate as a generated or referenced policy block so substantive deltas stand out.
7. **A source-custody priority rule.** The compact payload-custody lane is now productive, but it needs a priority function: prefer small official checksum/control/inventory files, exact-version identity pins, and public release manifests over raw payload warehousing or prose inventories.

## What should change next

- Add a tiny provenance/interoperability layer that maps existing package, manifest, receipt, source-snapshot, and tool surfaces to external standards without creating a second truth source.
- Split `make lint` into observable subtargets with elapsed times and fail-fast progress markers; keep the current aggregate target as a convenience wrapper.
- Convert the largest generated/read-only artifacts into clearly derived products with digests and expansion instructions, so humans do not treat `AUTHORITY-DEPENDENCY-GRAPH.json` or all-pass generated audits as narrative surfaces.
- Continue compact source custody, but only when a local retained file makes future replay fail closed. Do not vendor bulky maps, chains, likelihood tarballs, notebooks, or code checkouts unless a route earns a new retention burden.
- Make the next scientific move a discriminator-pressure move, not another archive-control flourish: a route should climb only by changing a denominator, forecast, negative control, or observed-sector recovery burden.

## What went wrong and is now being corrected over time

- **Stale current-head drift** was severe. Earlier bundles let human-facing currentness wording disagree with manifest/status truth. Later lint and mirror rules correctly made this a first-class failure mode.
- **Per-revision note fields became an informal schema.** The rev0346-rev0350 source-role event migration corrected the worst form by turning source and authority semantics into typed events.
- **Locator-only public-data custody was too weak.** rev0357-rev0363 corrected this by adding source snapshots, compact manifests, exact-version pins, local hashes, and inventory-control JSON while avoiding raw data warehousing.
- **Generated proof of safety became too bulky for human restart.** The archive has the right instinct—keep executable checks—but must keep all-pass generated surfaces compressed and push exhaustive state into replayable machine surfaces.
- **Router/docket proliferation risks becoming the thing it was built to prevent.** The archive explicitly knows this through router-economy rules; the next correction is to demote or template families whose common scaffolding now dominates their unique signal.

## Speculative readout

The archive's strongest scientific posture is not a favored framework; it is a wager that candidate-native identifiability, public record structure, and cross-family bridge pressure will eventually squeeze the viable theory space. Family C / holographic inverse-interface work looks like the strongest partial readout, but the archive is right to cap it: reconstruction is not candidate identity, public code is not public evidence, and agreement among methods is not convergence unless target grain, record denominator, observer map, and validity regime align.

The biggest latent opportunity is to turn the archive from a defensive anti-laundering machine into a **positive discriminator factory**: every future source-custody or theoretical bridge pass should output one sharper question, one admissible negative control, or one public-record burden that a rival family cannot easily borrow.

## Non-promotion boundary

This audit changes archive-control guidance only. It does not promote any route, evidence unit, forecast, decision outcome, public-record credit, observed-sector recovery state, or current-head scientific authority.
