# Assumption ledger triage rev0230

Rev0230 made the context pack compact, but the underlying assumption ledger still marked every
assumption as `active`. That made the archive honest about history but dishonest about priority:
old branch-history judgments, completed tooling repairs, current import blockers, and live
substantive education bets were all wearing the same state.

## New state meanings

| State | Meaning | Startup treatment |
|---|---|---|
| `active` | Can change a current `FT-0181`, public-claim, pilot-import, action-authority, evidence, access, or release-boundary decision. | Appears in `context-pack.json` as a compact ID. |
| `watch` | Still plausible and worth monitoring, but not needed for the next import or release decision. | Counted, not embedded. |
| `archived_context` | Historical branch, compression, or implemented-control rationale. Retrieve only when editing that family. | Counted, not embedded. |
| `superseded` | Replaced by a later surface or narrower assumption; kept only so old references resolve. | Counted, not embedded. |

## What changed

The active set is now deliberately small enough to be a decision surface rather than a memory dump.
It keeps the core education bets, the current action-authority/evidence/construct safety spine, and
the `FT-0181` import and closeout gates. Historical hot-exam, after-hours, packet-maintenance,
portable relapse, and repeated repair-cycle assumptions now remain retrievable through
`BRANCH_FAMILY_INDEX.json` and the archive detail, but they no longer dominate startup.

The change is not a claim that archived assumptions were wrong. It is a claim that they are not the
next decision. If a future pass edits a branch family, the relevant archived assumptions should be
opened deliberately from the ledger or branch-family index.

## Active decision families retained

| Family | Representative assumptions | Why retained |
|---|---|---|
| education value and construct | `AS-0001` through `AS-0006`, `AS-0022`, `AS-0204`, `AS-0208` | They can change whether the first real pilot is allowed to make learning, validity, access, or disclosure claims. |
| deployment and authority | `AS-0024` through `AS-0026`, `AS-0196`, `AS-0200`, `AS-0201`, `AS-0203` | They govern service boundaries, action ceilings, security, and staged rollout. |
| evidence and service-record import | `AS-0202`, `AS-0206`, `AS-0217`, `AS-0224` through `AS-0234` | They decide what counts as real evidence and which fields survive import. |
| ready-but-not-closed release boundary | `AS-0235` through `AS-0255` | They keep controls from being misread as pilot evidence. |
| first sprint unblocker | `AS-0274` through `AS-0278` | They focus the next session on acquiring a minimized real packet and converting any board result into a bounded, reversible change rather than adding another control shell. |

## Future audit rule

When adding or changing an assumption, assign its state in the same change. The default for a new
idea is **not** `active`. It is `watch` unless the assumption can change a decision in the current
release, and `archived_context` if it merely explains a branch-history or completed refactor move.

This triage is intentionally lighter than a new schema or validator. It corrects the immediate
waste: a live-startup surface that treated all historical assumptions as equally urgent.


## Rev0233 addition

`AS-0277` is active because the first owner packet must produce explicit authority, evidence, construct, public-summary, and lifecycle before/after decisions before acceptance, public-claim, schema, or lifecycle changes.


## rev0235 assumption delta

`AS-0278` is active because it changes the current `FT-0181` execution path: after a first-packet decision board, the archive still needs a bounded post-decision change ticket before service, public-summary, schema, validator, lifecycle, or closeout changes. This is not a new theory family; it is an overreach brake for the first real packet.
