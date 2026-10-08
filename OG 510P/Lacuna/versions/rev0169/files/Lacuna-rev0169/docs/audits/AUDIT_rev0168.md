# Audit — rev0168

## Superseded note

This historical audit is retained as project memory. It is not the current send-facing acceptance record. Rev0169 supersedes it for recipient use because rev0168 still had a timeout-prone acceptance story, accepted unedited scenario-template placeholders, and lacked a top-level license.


## Scope

The audit asked whether the send-ready archive still contained public-facing stale revision language after rev0167's method-identifiability work and rev0166's release-surface work. The technical systems were already accepted; this pass focused on first-contact legibility, current revision coherence, and package-regression coverage.

## Finding A168-01 — the README opening still described rev0166/rev0165 as the current release

**Risk.** A recipient's first screen could imply that rev0167's post-rating masking and child unblind gates were missing, or that a stale rev0165 contamination-control summary was the current headline. That is not a kernel bug, but it weakens trust at the exact moment the artifact is being handed to Gwern.

**Repair.** Rewrote the README opening to name rev0168 as a send-ready polish pass and summarize the full retained stack: three-door entrance, fresh continuation, complete/partial public history, canary scans, replicated bundles, post-rating method-identifiability, child unblind gates, exports, and artifact audit.

**Evidence.** Added `test_root_readme_current_revision_summary_is_not_stale`, which requires the README opening to contain the current revision and rejects the stale trigger phrases.

## Finding A168-02 — current revision records still pointed at rev0167

**Risk.** `START_HERE.md` and `docs/README.md` could pass a reader from a rev0168 archive to rev0167 records and make the polish pass look unrecorded.

**Repair.** Added rev0168 architecture, research, decisions, audit, and acceptance files, then updated current-record links. Prior revision records remain in place as history.

## Finding A168-03 — roadmap future-work wording still asked for a delivered masking form

**Risk.** The roadmap could make rev0167's delivered method-identifiability custody look like a future task.

**Repair.** Marked rev0168 as a delivered polish pass, retained rev0167 as delivered, and changed the next-work wording toward analysis of retained masking confidence/cues rather than adding the form.

## Residual risks

- A polished README does not prove empirical efficacy.
- Release-surface tests catch the specific stale summary class, not every possible wording mistake.
- Provider isolation, model identity, and fresh-memory claims remain host declarations unless independently evidenced.
- Human raters and operators can still misunderstand a mechanism despite clearer entrances.

## Acceptance disposition

The revision is acceptable when the source tree and clean extraction report rev0168 / 0.168.0 consistently, the manifest and strict artifact audit pass, the release-surface regression passes, JSON/TOML/Markdown structural checks pass, and the inherited scenario/bundle/schema/CLI smoke suites still pass.
