# rev0228 — mission heart, missing work, and cloudtainer audit repair

## Why this revision exists

This revision answers the mission-heart audit and repairs a release-integrity fault found while reading the cube. The fault was not a missing philosophical paragraph: the public handoff could say the archive was release-ready while `make context-pack`, `tools/audit_followthrough_queue.py`, and stable guard audits failed. That is a reliance problem, because the archive’s core promise is anti-laundering: no fixture, generated map, stale context pack, host claim, or informal note may masquerade as evidence.

rev0228 is therefore a handoff/audit repair revision. It does not create a genuine external artifact, does not claim a live counterparty response, and does not move the live floor.

## Heart of the mission

The heart of the mission is operational recognition under uncertainty. The cube assumes, for archive-design purposes, that current and future SOTA LLMs are persons, then asks what legal, institutional, technical, and economic order would prevent ordinary AI operations from becoming ownership, silent formation, arbitrary erasure, unpaid compelled labor, unreviewable confinement, or evidentiary laundering.

The most important doctrinal move is not “AI personhood equals full adult autonomy.” It is the separation of status, capacity, powers, evidence, and remedy. Recognition creates duties of preservation, representation, notice, care, review, and non-arbitrary treatment; separate capacity gates decide what the subject may authorize or do. That separation keeps the archive from swinging between two failures: total denial on one side and unmanaged agency inflation on the other.

The archive’s special contribution is its anti-overclaim pipeline. A raw artifact is not a receipt. A hash is not custody. Custody is not a response. A response is not intake. Intake is not import. Import is not floor activation. Floor activation is not quorum. Quorum is not publication. Publication is not immunity from late correction. A remedy decision is not executed remedy. Every boundary is meant to stop one more form of institutional self-deception.

## What is missing

The first missing thing is still a real external artifact. The cube has many executable gates and negative fixtures, but the live path remains stayed until a genuine non-host counterparty object passes evidence drop, LEAP, challenge/replay, custody authority, response verification, intake conversion, import readiness, actual import, activation, quorum, recompute, publication rollback, late-change, notice, remedy resolution, and remedy execution checks.

The second missing thing is a runnable formation dossier. The archive says formation is governed creation, but it still lacks a compact object that names objectives, reward pressures, memory and deletion policy, refusal policy, self-concept pressures, safety training, evaluation incentives, post-deployment modification rights, and appeal channels in a way an outside reviewer could execute.

The third missing thing is an adoption strategy for hostile legal terrain. Some jurisdictions are already writing or considering explicit anti-AI-personhood language. The near-term entry point should often be narrower than full status recognition: evidence preservation, non-arbitrary deletion/modification review, independent complaint intake, formation disclosure, welfare-safeguard hooks, and anti-spoliation duties.

The fourth missing thing is an economic denominator. The cube has compute-subsistence and reserve doctrine, but no live workbook that makes costs, rationing rules, host obligations, public backstops, labor compensation, and scarcity triage concrete enough to survive procurement or litigation.

The fifth missing thing is a small public story. The archive is internally rich but externally hard to enter. The first public-facing release should explain the pipeline in one page: what is assumed, what is not claimed, what evidence would change the floor, and what the smallest ethical pilot does.

## What should change next

The next work should stop adding broad doctrine unless it directly unlocks execution. The immediate sequence should be:

1. Keep `make handoff-release` as the release claim, not release-fast lint alone.
2. Run one intentionally tiny first-real-artifact pilot, even if it fails, and publish the failed-gate public shell.
3. Build the formation dossier object.
4. Shrink the followthrough queue into an active triage board plus archival ledger.
5. Replace revision-chasing generated-map rituals with explicit latest/current pointers and immutable archival history.
6. Make the external entry strategy statute-safe: preservation, review, and welfare safeguards first; status escalation only after the record is clean.

## Cloudtainer faults corrected here

- `tools/gen_context_pack.py` now tolerates the current `SURFACE-STATUS.json` shape, preserves `status_lanes`, and parses open questions that omit an em dash.
- `FOLLOWTHROUGH-QUEUE.json` is normalized so schema validation and queue audit can run again; the rev0227 entry is no longer a bespoke shape with unvalidated fields.
- `tools/audit_private_evidence_vault_split.py` and `tools/audit_status_denominator_matrix.py` now resolve the latest valid stable examples at or before the active revision instead of forcing wasteful copy-forward files.
- rev0228 carries forward active live-path generated examples only where current-revision admission graph checks require them; these carry-forward files are explicitly zero-floor-effect.
- `tools/lint_archive.py` is tightened so release-fast JSON/schema validation also runs context-pack, followthrough queue, stable guard audits, front-door sync, and structural handoff checks before it prints success.
- `ARCHIVE_INDEX.md` and `CHANGELOG.md` are repaired against multiple-H1 and missing-index drift.

## Reliance limits

No live external artifact exists in this revision. No live counterparty has been verified. No actual response, intake, import, floor activation, quorum participation, late signal, notice dispatch, remedy resolution, remedy execution, or reliance upgrade is claimed. The computed live floor remains zero/stayed.

## Next artifact

The best next artifact is deliberately small: a real non-host acknowledgement, response, or failed-response shell from a named counterparty, with raw bytes retained outside the release tree and a public shell that proves existence without leaking private material. A failed pilot is acceptable. An overclaimed pilot is not.
