# Publishing and Release Governance

This repository now uses a **slow, conservative publication flow**.

The governing idea is simple:

- the research process may continue to evolve,
- but public releases must be frozen only when a draft has clearly stopped moving in substance,
- and the default decision is **do not publish yet**.

## Two naming regimes

This repository now distinguishes between:

- **legacy already-published work**, which keeps its existing **Mathematics** wiki links, and
- **new releases**, which must use the **Anonymity** naming regime.

The canonical legacy link set is recorded in `published/LEGACY_PUBLISHED_LINKS.md`.
Do not casually rename those old public links.

## What counts as published

For new releases, a paper counts as published only when it has been copied into `published/` by the guarded publication helper under the portable target convention:

`published/YYYY-MM-DD_slug_title/paper.tex`

For a published paper:

- the **directory name** must be a portable slug such as `2026-05-24_certified_menus_for_anonymous_dht_lookups`,
- the canonical `.tex` file inside that directory must be `paper.tex`,
- human-facing metadata may still display the title as `Anonymity: The Foobar Title Goes Here Please`,
- all wiki references must target the portable basename in wikilink form, for example:
  - `[[2026-05-24_certified_menus_for_anonymous_dht_lookups]]`

## Current policy

This repo is intentionally biased toward:

- delayed release,
- written release decisions,
- explicit hold decisions,
- small release queue movement,
- and reversible staging before irreversible public publication.

## Operator rule for future turns

A future LLM-in-charge should be allowed to spend many turns making **no release decision**.
A turn is successful if it makes the repository better structured, narrows uncertainty, records a hold, or advances one candidate by a single cautious step.

See:

- `publishing/OPERATOR_STARTUP.md`
- `publishing/RELEASE_FLOW.md`
- `publishing/CONSERVATIVE_RELEASE_POLICY.md`
- `publishing/TURN_DECISION_PROTOCOL.md`
- `published/LEGACY_PUBLISHED_LINKS.md`
- `release_queue/STATUS.md`

## Additional control surfaces

For future cautious turns, also use:

- `published/PUBLICATION_CLASSIFICATION.md`
- `published/CITATION_HEADS.md`
- `published/PUBLIC_SURFACE.json`
- `release_queue/QUEUE_INDEX.json`
- `release_queue/LATEST_DECISION.json`
- `release_queue/DECISION_INDEX.md`
- `release_queue/DECISION_INDEX.json`
- `release_queue/REVIEW_INVENTORY.md`
- `publishing/REVIEW_ORDER.md`
- `publishing/REVIEW_RUBRIC.md`
- `VERSION`
- `START_HERE.md`
- `CONTEXT_PACK.json`
- `publishing/CONTROL_SURFACES.md`
- `publishing/control_surfaces.json`
- `publishing/build_decision_index.py`
- `publishing/check_archive_coherence.py`
- `publishing/check_context_pack_contract.py`
- `publishing/check_transient_surface.py`
- `publishing/verify_manifest_sha256.py`
- `publishing/check_manifest_coverage.py`
- `publishing/release_preflight.py`
- `publishing/check_release_readiness.py`
- `reports/release_readiness_audit.json`
- `publishing/check_evidence_pack_policy.py`
- `reports/evidence_pack_audit.json`
- `publishing/build_release_freeze_plan.py`
- `release_queue/NEXT_RELEASE_FREEZE_PLAN.md`

## Paper-family layout

The moving paper-family trees now live under `series/`.
Keep new family-level source trees there rather than adding fresh top-level siblings.
The top level should preferentially expose only the public/archive surfaces (`published/`, `publishing/`, `release_queue/`) plus generated-audit homes (`build/`, `reports/`, `index/`).

## Repo-shape default

Keep generated artifacts out of the shipped root unless there is a strong reason otherwise.

Use:

- `build/` for transient compile outputs and render batches,
- `reports/` for persistent generated review/preflight reports, and
- `index/` for generated series-index source/output.


Additional operator helpers:

- `publishing/LIFECYCLE_GATES.md` / `reports/lifecycle_gate_status.json` answer which compact surface matters at each stage.
- `DATACUBE_TRANSFER_LEDGER.md` records which patterns from other datacubes were adopted or rejected.
- `publishing/rebuild_archive_surfaces.py` and `Makefile` provide a one-command rebuild/verification path for the compact surfaces.
- `TRANSFER_SOURCES.md` / `TRANSFER_SOURCES.json` / `TRANSFER_INPUTS.sha256` record the exact external datacube bundles reviewed during transfer passes.
- `ASSURANCE_ARTIFACTS.md` / `ASSURANCE_ARTIFACTS.json` group the trust surfaces so a future operator can inspect them as a set.


## Compact trust stack

Before relying on queue / citation / public-boundary JSON alone, check: `reports/surface_schema_validation.json`, `reports/archive_invariants.json`, `reports/archive_surface_coherence.json`, and only then the narrower audits like context-pack budget, manifest coverage, and transient-surface status.


Queue-facing markdown under `release_queue/` is now regenerated from compact machine state using `publishing/render_queue_surfaces.py`; prefer rerendering over hand-editing those summaries.

- Run the integrity and drift checks before any publication move.
- Treat shipped `series/.../renderNNN/` review-render directories as a packaging failure, not as moving-source truth.

## rev0805 release-hardening rules

New releases are still source-first, but not source-only when a paper makes artifact-governance, receipt, resolver, replay, validation, or support-bundle claims. In those cases, the release candidate must carry a minimal evidence pack beside the frozen `.tex` source: the relevant local support manifest, artifact inventory, validation report, resolver/support-bundle map, validator script, and a manifest or checksum excerpt binding those files.

Before any freeze, run `python3 -B publishing/release_preflight.py --root . --date YYYY.MM.DD --title "Title" --source path/to/paper.tex --compile` when the local LaTeX toolchain is available. The preflight now records the source hash, checks that the source is represented in the Published-ready queue, performs static citation/reference closure, rejects unallowlisted placeholder markers, and can compile in a temporary directory so the archive tree is not mutated.

Nested manifests are part of the publication boundary. `reports/support_manifest_integrity.json` must pass; a top-level `MANIFEST.sha256` pass is not sufficient if an artifact-local `support_manifest.json` contains stale file digests or ambiguous path bases.


## rev0806 release-readiness rules

The Published-ready queue is now statically audited before it is treated as a release lane. Run `python3 -B publishing/check_release_readiness.py --root . --write-report reports/release_readiness_audit.json` before selecting a release target. The audit must bind each source by exact `release_queue/QUEUE_INDEX.json` `source_tex`, compute source SHA-256 values, separate warnings from blockers, and report corpus-level citation/malformed-bibliography closure.

`reports/release_readiness_audit.json` is advisory and fail-closed: it records static readiness, but it never authorizes publication. A single selected source must still pass `publishing/release_preflight.py`, receive a written decision note, be frozen into `published/`, and then survive manifest/coherence regeneration.

## Queue-bound source hashes

Candidate and Published-ready notes must carry `Queue-bound source SHA-256` for their `Source paper` path. `publishing/check_release_readiness.py` and `publishing/release_preflight.py` fail closed if the note no longer names the current source bytes. Refreshing this hash is a maintenance action only; it does not authorize publication.

Maintenance helper: after an intentional edit to a Candidate or Published-ready source, run `python3 -B publishing/refresh_queue_source_hashes.py --root .` and record why the queued source remains in that state. Then rerun `make verify-surfaces`.

## Review-inventory source identity

Before moving a paper or selecting a freeze target, `reports/review_inventory_integrity.json` should pass. The review inventory is rebuilt from current `series/**/paper.tex` bytes, and stale `sha256_prefix` rows are treated as a queue-trust problem rather than cosmetic metadata.


## rev0808 evidence and freeze-plan rules

The release lane now has two additional non-authorizing surfaces:

- `reports/evidence_pack_audit.json` checks that Candidate and Published-ready sources which likely make artifact-governance claims carry an explicit freeze-time evidence obligation.
- `release_queue/NEXT_RELEASE_FREEZE_PLAN.md` identifies the lowest-friction static-pass source for a dry-run freeze plan, records the current source hash, and lists unresolved manual gates.

Neither surface publishes anything. A selected source remains blocked until the evidence-pack gate is resolved by attached evidence or a written waiver, a clean compile is performed when available, and a new explicit publication decision is recorded.

Run `python3 -B publishing/check_evidence_pack_policy.py --root . --write-report reports/evidence_pack_audit.json` before relying on a release-readiness recommendation, then run `python3 -B publishing/build_release_freeze_plan.py --root .` to inspect the dry-run plan.


## rev0810 publication-boundary and freeze-packet rules

A clean evidence pack and compile witness are not enough to make a public release. Before any new post-policy Anonymity paper is copied into `published/`, a future operator must also have a source-bound non-public freeze packet and a passing published-boundary audit.

Required execution surfaces:

- `release_queue/FREEZE_PACKET_REGISTRY.json`
- `reports/freeze_packet_integrity.json`
- `reports/publication_boundary.json`
- `publishing/create_published_entry.py`

`publishing/create_published_entry.py` is now fail-closed: it requires an explicit decision note containing `Publication action: publish`, the expected source SHA-256, an evidence-pack manifest, the clean compile witness, and the freeze-packet manifest. A successful helper run must be followed by refreshed citation-head, public-surface, metadata, provenance, manifest, and archive-coherence surfaces.

## rev0811 current-witness, decision-template, and packaging rules

A compile witness is valid only when `release_queue/FREEZE_COMPILE_WITNESS.json` is generated for the current `RELEASE_MANIFEST.json` revision and bundle. `publishing/build_freeze_compile_witness.py` rebuilds the witness; `publishing/check_freeze_compile_witness.py` fails closed if the witness is stale, source-mismatched, or not a clean final compile.

Any future publish decision should start from `release_queue/PUBLICATION_DECISION_TEMPLATE.md`. The completed decision note must name `Publication action: publish`, the exact source path, source SHA-256, target published name, evidence-pack manifest, compile witness, freeze-packet manifest, queue note, citation-head update obligation, and publication receipt obligation.

The final archive zip should be produced with `make package` or `python3 -B publishing/build_archive_zip.py --root . --out-dir <dir>`. The packaging recipe is checked by `publishing/check_archive_packaging_recipe.py` and must agree with `MANIFEST.json` before a zip is treated as canonical. A package build also writes external `.sha256` and `.package.intoto.jsonl` sidecars; `publishing/check_package_attestation.py` verifies that those sidecars bind to the final zip bytes and to the packaged manifest evidence. The sidecar statement is not an identity signature unless a later external signing step signs it.

## Real publication-decision authorization scan

`release_queue/PUBLICATION_DECISION_TEMPLATE.md` is only a template. Real decision notes under `release_queue/decisions/` are scanned by:

```bash
python3 -B publishing/check_publication_decision_authorization.py --root . --write-report reports/publication_decision_authorization.json
```

A note that says `Publication action: publish` is not enough. It must bind the source, source hash, published name, evidence-pack manifest, current deterministic compile witness, freeze-packet manifest, queue note, public citation-head update, publication receipt, and explicit authorization line before the guarded publication helper may execute.

## Source and command-surface safety gates

Before any publication helper may be used, three non-authorizing source-safety gates must pass:

- `reports/tex_source_safety.json` — scans all shipped TeX sources for shell-escape and unsafe external-input primitives.
- `reports/secret_material_quarantine.json` — scans text surfaces for obvious private-key markers and high-confidence token-like secrets without echoing matched secret text.
- `reports/makefile_target_integrity.json` — checks that root Makefile targets remain bytecode-safe, non-mutating for verification, and deterministic for packaging.

These gates never authorize publication by themselves. They only block publication if the source or command surface becomes unsafe.


## rev0824 release-lane guard additions

Before any publication attempt, `reports/manifest_canonicality.json`, `reports/freeze_warning_resolution.json`, and `reports/toolchain_fingerprint.json` must pass. These checks prove that package manifests are canonical, freeze preflight warnings have explicit downstream resolution, and clean-compile evidence is bound to a TeX command fingerprint. They are blockers only and do not authorize publication.

## rev0825 text-control hygiene addition

Before any publication attempt, `reports/unicode_control_hygiene.json` must pass. It is separate from UTF-8/LF normalization: it rejects hidden C0/C1 controls beyond LF/TAB, bidirectional controls, invisible format controls, Unicode noncharacters, and surrogate code points. Passing this guard is necessary but not sufficient for publication.
