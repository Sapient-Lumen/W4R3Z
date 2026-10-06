# DeriveBSD rev0530 cloudtainer deep audit: release green, waste backlog, canonical JSON, host proof

## Scope

This revision is an evidence-and-review revision. It does not intentionally change product semantics. It adds this session review plus a machine-readable audit summary, and it preserves the archive's existing source/spec/tool content.

Input archive audited:

- `DeriveBSD-rev0529-2026.06.10.14.12-launchevidencesplit-runnerenvresume-postdetachclosure-raccoon(1).zip`

Cloudtainer extraction note:

- A first extraction through Python `zipfile.extractall()` produced false hygiene failures because executable mode bits were not restored on `tools/*.py` even though the ZIP stores executable attributes.
- Re-extraction with system `unzip` restored the mode bits and cleared the executable-bit and hygiene-ledger fingerprint checks.
- Future cloudtainer work on this cube should avoid Python zip extraction unless it explicitly restores external attributes.

## Validation performed in this session

Release-critical hygiene:

- Ledger: `session-reviews/cloudtainer-r0530-release-critical-ledger.json`
- Result: passed
- Completion: 35/35 checks
- Check-budget status: completed within check budget
- Input fingerprint scope: `source-docs-spec-tools-fixtures-no-session-reviews-or-ledger-output`

Post-review release-critical hygiene, after adding this review and summary:

- Ledger: `session-reviews/DeriveBSD-rev0530-2026.06.12.17.02-releasegreen-canonicaljsonhostproof-shrinkfrontdoor-lynx-release-critical-ledger.json`
- Result: passed
- Completion: 35/35 checks
- Check-budget status: completed within check budget

Post-detach hygiene:

- Ledger: `session-reviews/cloudtainer-r0530-post-detach-ledger.json`
- Result: passed
- Completion: 39/39 checks
- Check-budget status: completed within check budget
- Input fingerprint scope: `source-docs-spec-tools-fixtures-no-session-reviews-or-ledger-output`

Important limitation:

- The post-detach shard is cloudtainer-green, but this is not the same as a real FreeBSD host-smoke proof. The host proof remains an explicit missing acceptance artifact.

## Inventory signal

The cube is no longer small. At the audit inventory checkpoint before adding this review package, the unpacked tree contained 3,149 files and about 20.5 MB of file payload. After this review, summary, and post-review ledger, the unpacked tree contains 3152 files.

Large-front-door and large-index surfaces observed:

- `docs/00-index.md`: 833,969 bytes
- `CHANGELOG.md`: 506,653 bytes
- `docs/110-juicy-os-lessons.md`: 454,115 bytes
- `docs/_generated/doc_catalog.json`: 286,930 bytes
- `docs/99-llm-runbook.md`: 254,182 bytes
- `docs/266-open-questions-and-risk-register.md`: 204,273 bytes
- `docs/98-archive-hygiene.md`: 189,852 bytes

The current front-door guard is useful, but it is still a ratchet, not a shrink plan. `tools/check_frontdoor_budget.py` passes while warning that `docs/00-index.md` and `docs/99-llm-runbook.md` grew beyond their observed baselines. That is acceptable as a guardrail, but it will not make the cube easier to operate unless the generated front door is split from a much smaller human front door.

## What improved since the earlier waste audit

Several earlier risks have materially improved:

- The hygiene wrapper now emits a resumable ledger with runner-environment and cube-input fingerprints.
- Release-critical hygiene is runnable and produced a complete green ledger in this cloudtainer.
- The post-detach removable-media shard is runnable and produced a complete green ledger in this cloudtainer after chunked resume.
- The post-detach const-heavy schema problem has been significantly reduced by runtime/fixture splitting.
- Shared helper files now exist, including `tools/cube_check_lib.py`, `tools/cube_digest_lib.py`, and `tools/removable_media_post_detach_guardrail_lib.py`.
- Generated identifier consistency and generated-doc checks appear to be mainline rather than merely aspirational.

## What is still missing

### 1. Real FreeBSD host proof

The cube has strong simulated/cloudtainer post-detach evidence, but it still needs an acceptance artifact from a real FreeBSD host. The missing proof should bind:

- kernel and userland identity,
- Capsicum availability,
- the compiled C worker digest,
- a disposable device or disk-image mount,
- read-only/untrusted handling,
- pre-exec unmount or descriptor-only transition,
- fd-only worker execution,
- stdout/stderr/return-code transcript,
- and a final receipt that proves the cloudtainer contract was not only simulated.

This is the most important remaining gap for removable-media credibility.

### 2. Canonical JSON conformance clarity

`adrs/ADR-0022-canonical-json-jcs.md` says DeriveBSD uses RFC 8785 JCS for hashed JSON artifacts. The current shared digest helper, `tools/cube_digest_lib.py`, implements compact Python `json.dumps(..., sort_keys=True, separators=(",", ":"), ensure_ascii=False)` serialization and describes it as the current archive canonical JSON byte representation.

That may be deterministic for the current Python-only fixtures, but it is not yet proven to be full RFC 8785 JCS. RFC 8785 requires I-JSON constraints, ECMAScript JSON primitive serialization, and deterministic property sorting. The highest-risk mismatch is number/string edge behavior and interoperable rejection behavior, not ordinary ASCII maps.

Recommended correction:

- Either rename the current helper posture to `python_sorted_compact_json` and explicitly scope it to fixture/local guardrail digests,
- or add a real RFC 8785 implementation/conformance lane with red fixtures for number rendering, Unicode, NaN/Infinity rejection, duplicate-key/I-JSON rejection, and cross-language equivalence.

This should be corrected before JSON digests become external interoperability commitments.

### 3. Front-door shrink, not only front-door ratchet

`docs/00-index.md` and `docs/99-llm-runbook.md` are still too large for repeated human operation. The current budget prevents unbounded silent growth, but it does not create a usable entry surface.

Recommended correction:

- Keep generated catalogs generated and indexed.
- Create a small current-action front door with a hard byte/line budget.
- Move historical explanations into deep links.
- Make the small front door answer only: what is green, what is missing, what to run next, what not to touch.

### 4. Guardrail/check monoculture

The cube has 367 `tools/check_*.py` scripts and 392 tool files. Duplication remains high even after helper-library progress:

- `load_json` appears in about 199 tool files.
- `validate` appears in about 62 tool files.
- JCS-like byte helpers appear in dozens of files.
- `digest`/`digest_obj` variants remain scattered.

Recommended correction:

- Continue extracting shared helper libraries.
- Generate the simplest schema/example checks from a manifest.
- Preserve bespoke handwritten checks only where they encode red-corpus semantics, lifecycle transitions, or threat-model assertions that a generator cannot express.

### 5. Schema backlog after post-detach split

The schema audit is useful and honest. It reports:

- 455 schemas,
- 467 examples,
- 25 const-heavy schemas,
- 40 runtime-contract-shaped schemas,
- 17 exact fixture schemas,
- 0 dotted-kind filename mismatches,
- 434 schemas with canonical examples,
- 21 schemas without canonical examples.

The open refactor backlog has 8 open items. The highest-priority open target is:

- `spec/net.publish.session.schema.json`, priority p1, 133 consts, domain `network-publish`.

Next open p2 targets are:

- `spec/removable.media.capsicum.worker.bridge.schema.json`, 85 consts,
- `spec/preopen.map.schema.json`, 70 consts,
- `spec/content.import.plan.schema.json`, 68 consts,
- `spec/removable.media.local.freebsd.backend.run.receipt.schema.json`, 67 consts,
- `spec/content.import.receipt.schema.json`, 62 consts,
- `spec/removable.media.local.freebsd.backend.plan.schema.json`, 61 consts,
- `spec/removable.media.local.fallback.harness.run.schema.json`, 58 consts.

Recommended correction:

- Do not create another large receipt family until `net.publish.session` is assessed.
- If `net.publish.session` is a historical exact fixture, split it.
- If it is a real runtime contract, remove unnecessary literal fixture values and push those into canonical examples plus semantic checkers.

### 6. Acceptance-profile manifests

The archive has many checks, but the operational story would be stronger if every profile had a short acceptance manifest:

- purpose,
- threat class covered,
- checks included,
- checks deliberately excluded,
- required host capabilities,
- cloudtainer-only limitations,
- expected runtime and memory budget,
- and the evidence artifact that counts as acceptance.

The current hygiene ledger is good raw evidence. The missing layer is the operator-facing acceptance contract.

## Severe or wasteful patterns that can be corrected over time

### Python ZIP extraction is a trap in this cloudtainer

The ZIP stores executable mode bits for Python tools. Python extraction did not restore them, and that created misleading release-critical failures. This is severe because it wastes audit time and can cause unnecessary code churn. Use `unzip` or a mode-restoring extractor for this cube.

### Run long hygiene profiles in chunks by default

The post-detach wrapper is resumable and eventually green, but a full long run can be interrupted by outer cloudtainer limits. The right default here is not “run everything and hope.” Use the ledger resume path with `--max-checks` or `--max-run-seconds` by default in cloudtainer sessions, then require `run_complete: true` in the final ledger.

### Generated documentation is acting like a compressed database

The index and generated catalogs are valuable, but humans should not be asked to repeatedly scan hundreds of kilobytes to find the next move. Keep the generated database, but stop treating it as the human front door.

### Duplicate evidence can be intentional, but should be declared

There are exact duplicate groups where validation receipts mirror spec examples, and one duplicate post-detach ledger pair. The spec-example duplicates may be intentional fixtures. The duplicate ledger pair should either be declared as an alias/preserved historical evidence or collapsed in future archival compaction.

## Online-context speculation

FreeBSD upstream direction makes DeriveBSD's adapter-first posture look right:

- FreeBSD 15.x offers package-base installation as a technology preview, while distribution sets remain the conservative production path during the 15.x lifecycle.
- bhyve, jails, and Capsicum remain appropriate FreeBSD-native primitives for a project shaped around compartmentalization, host/guest execution, and descriptor-limited workers.
- The laptop/desktop ecosystem is moving, but the cube still needs hardware qualification evidence rather than documentation confidence.

Supply-chain direction also supports the cube's current instincts, but the cube should avoid inventing private formats where stable public shapes are enough:

- Keep TUF-like freshness/rollback/freeze/mix-and-match threat language for update channels.
- Keep in-toto/SLSA-style provenance language for build and verification claims.
- Use Rekor-style transparency concepts carefully: transparency logs are monitorable/tamper-evident, not magic trust.
- Emit SPDX and/or CycloneDX SBOMs for deliverable artifacts rather than only bespoke inventory docs.

## Suggested next revision sequence

1. rev0531: Canonical JSON/JCS conformance decision. Either implement real RFC 8785 checks or rename the current helper posture so it does not overclaim.
2. rev0532: `net.publish.session` runtime/fixture assessment and split if needed.
3. rev0533: real FreeBSD host-smoke evidence for removable-media post-detach/Capsicum worker path.
4. rev0534: small human front door with hard shrink budget, leaving generated catalogs as generated catalogs.
5. rev0535: tool helper consolidation and manifest generation for repetitive schema/example checks.
6. rev0536: profile acceptance manifests for release-critical, post-detach, and any hardware-required profiles.

## Bottom line

The cube is much healthier than a pure documentation pile: the release-critical and post-detach slices are green in this cloudtainer, and the schema audit/backlog is honest. The next credibility gains are not more documents. They are canonicalization truthfulness, real FreeBSD host proof, human front-door shrinkage, and continued reduction of one-off guardrail boilerplate.
