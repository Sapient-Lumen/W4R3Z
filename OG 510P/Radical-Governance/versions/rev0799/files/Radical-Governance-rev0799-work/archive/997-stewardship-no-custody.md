# 997 — Stewardship no custody

## One-line thesis

A ZIP is not a custodian.

## Why this matters

The cube has spent many revisions preventing public-administration theater: no outcome by receipt row, no closure by sampling plan, no fieldwork by gate, no collection by control, no outcome by operating log, no closure forever. The archive now needs the same discipline for itself.

A release file is not a custodian. A manifest is not a maintainer. A schema is not a license. A generated source-health row is not a source-preservation steward. A route-demotion pilot is not a retirement policy. A public note saying that security contact is needed is not a monitored inbox, safe-harbor posture, or response clock.

The high-risk live gap is `GAP-032`: license, maintainer, contribution, security, citation, and succession governance. It is not safe to pretend that the archive can be reused or extended just because it is readable. Without owner-approved stewardship, downstream users do not know what rights they have, contributors do not know who can accept changes, reporters do not know where to send security problems, and future maintainers do not know who can reopen a gap, demote a route, refresh a source, or freeze the archive.

Rev0799 adds `metadata/archive_stewardship_handoff_controls.json`. It does not make any owner or legal decision. It makes the missing decisions harder to hide.

The governing rule is **no custody by ZIP**.

## Pattern pack

1. **A release artifact is not an institution.** A preserved archive can still lack a lawful owner decision, maintainer authority, security channel, and succession path.
2. **License ambiguity is operational risk.** Reuse, quotation, contribution, and derivative work rules must be explicit before the archive can invite downstream reliance.
3. **Maintainer authority must be named or classed.** Someone must be able to merge, reject, sign, retire, reopen, freeze, or hand off; otherwise every future decision is theater.
4. **Security reporting needs a real channel.** A `SECURITY.md` placeholder is not enough if no inbox, triage owner, scope, acknowledgment posture, or private-report boundary exists.
5. **Succession is a continuity control.** If the primary steward disappears, the archive needs a public-safe trigger for inactivity, backup authority, source-refresh continuity, and freeze/read-only posture.
6. **Route retirement needs authority.** A note can be historically preserved only if somebody is allowed to decide what leaves active circulation and what remains only for lineage/search.
7. **Source refresh needs an owner.** Locator decay, passage drift, and hash/capture failures cannot be managed by a generated table alone.
8. **Handoff controls are not handoff.** A control can list required documents, roles, clocks, and blockers. It cannot grant rights, accept a maintainer, monitor security mail, or preserve private evidence.

## What changed

### Archive stewardship handoff controls

Rev0799 adds three non-approved controls.

`ASH-ARCHIVE-001` covers license, rights, maintainers, contribution rules, citation, release signing, route retirement, source preservation, and gap-closure authority. It requires owner decisions and public documents such as `LICENSE` or `RIGHTS`, `GOVERNANCE`, `MAINTAINERS`, `CONTRIBUTING`, `CITATION`, release process, retirement policy, and source-preservation policy.

`ASH-SECURITY-001` covers security contact, vulnerability disclosure, private-report routing, covered scope, response clocks, advisory release, and embargo boundaries. It explicitly keeps private vulnerability reports, credentials, exploit details, private remediation branches, and private incident logs outside the cube.

`ASH-SUCCESSION-001` covers succession, source-refresh, post-closure monitoring, route-retirement, gap-reopen authority, and archive freeze/read-only policy. It requires a successor or stewardship body, inactivity trigger, source-refresh owner, post-closure monitoring owner, route-demotion authority, and gap-reopen authority.

All three controls are non-closing. They block stewardship closure; they do not complete it.

### Source and receipt additions

Rev0799 adds source keys, source-health rows, and source-claim receipts for open-source reuse, agency implementation, vulnerability disclosure, machine-readable licensing, content-license obligations, and governance roles.

These are method floors. They do not choose a license, name a maintainer, establish a monitored security channel, authorize reuse, or prove succession.

### Audit/refactor

The bounded refactor adds `tools/build_archive_stewardship_handoff_controls.py`, schema validation, generated reader surfaces, Makefile/build-step ordering, and lint for the new stewardship surface. It also adds `validate_archive_stewardship_handoff_control` to `tools/fieldwork_lint_helpers.py`, using the existing control-helper file as a common cross-surface guard rather than adding another isolated lint island.

The refactor is deliberately small. It does not attempt to rewrite all fieldwork control validators. It adds just enough enforcement to prevent the new stewardship surface from becoming decorative.

## What this still does not do

It does not choose a license.

It does not grant rights, publish legal advice, appoint maintainers, establish contribution acceptance rules, create a security contact, monitor a vulnerability inbox, approve safe harbor, transfer custody, assign a successor, approve route retirement, preserve source snapshots, verify affected-person outcomes, or close any live gap.

It does not add private owner contact details, private legal advice, private security reports, credentials, tokens, exploit details, or private evidence to the cube.

## Anti-theater tests

1. Pick `ASH-ARCHIVE-001`. Does it require concrete documents and owner decisions, rather than saying the current ZIP is enough?
2. Pick `ASH-SECURITY-001`. Does it distinguish a required security policy from a real monitored channel and private-report custody?
3. Pick `ASH-SUCCESSION-001`. Does it define inactivity, backup, source-refresh, route-retirement, gap-reopen, and freeze/read-only decisions without pretending they are approved?
4. Pick `generated/ARCHIVE_STEWARDSHIP_HANDOFF_CONTROLS.md`. Does every control remain non-approved?
5. Pick `GAP-032`. Does it remain live or in progress rather than closing because a handoff matrix exists?
6. Pick the new source receipts. Do they support stewardship floors without granting a license, appointing maintainers, or preserving source snapshots?
7. Pick `tools/lint_archive.py`. Does lint enforce required documents, role classes, source receipts, prohibited private artifacts, generated parity, and blockers?
8. Pick note `465`. Does its historical-preserved demotion still remain a pilot rather than a general retirement policy?

## Source posture

Use OMB M-16-21 and the Digital.gov explainer as reuse-rights and source-code stewardship floors. Use the GSA OSS policy as an implementation example for working groups, public repository posture, secure pipeline, and metadata. Use CISA BOD 20-01 and the CISA VDP template as security-reporting floors, but keep them locator-limited because direct page fetches were blocked in this environment. Use REUSE and Creative Commons materials as license-declaration and license-obligation floors, not legal advice. Use Open Source Guides governance material as a practical maintainer-role prompt, not as authority over this archive.

The practical rule is: **the cube can say what is missing. It cannot become its own owner.**
