# Testing facility long-run audit

Revision: rev0028

## Findings

The test facility is directionally sound: tests are manifest-addressable, timed, artifact-producing, and sliceable by tier, id, tag, shard, and changed file impact. The main risk is not too few tests; it is incoherent growth that makes later sessions unable to know which proof earned which claim.

Rev0022 therefore keeps release browser-light, preserves explicit browser/CDP tiers, and adds audit surfaces that check currentness, artifact hygiene, impact coverage, and non-claim legibility.

## Testing optimization posture

Use `make turn-start` first. Use `--id` during slice development. Use `--changed --only-affected` when refactoring a narrow surface. Use `--tier browser --jobs 1` for browser/CDP work. Keep package-time validation browser-light unless timing evidence justifies a narrower exception.

The facility should optimize for fast feedback without hiding evidence: every proof should leave timing and artifact output, and every expensive surface should have a cheaper fake/model rung first.

## Refactoring signals

Refactor or split the testing facility when release estimates keep climbing, browser code starts launching inside release by accident, one task produces multiple independent claims, impact selection stops selecting obvious proofs, or a future provider lacks a fake/model test before browser/OPFS/WebGPU spending.

Also refactor when `check_cube.py` becomes a blocker that reports no useful failures; strictness is valuable only while it catches real drift.

## Remaining risks

Browser/CDP artifacts can go stale if explicit browser tier runs are not periodically refreshed. Timing estimates are cloudtainer-specific. The audit tools guard coherence, not runtime semantics. Future sessions must not confuse a passing release with a production-runtime claim.

## Rev0023 recovery-slice amendment

Findings: persisted-spill recovery is cheap enough to keep in release because it is Node/fake-provider only. Browser/OPFS recovery must remain explicit-tier until the fake/provider semantics are stable.

Testing optimization posture: add semantic model/fake proofs before browser proofs. `ipc:persisted-spill-recovery-proof` and `facility:recovery-contract-audit` are examples of the pattern.

Refactoring signals: if new provider proofs repeat checkpoint/journal/pending/ack assertions, extract a shared recovery oracle rather than duplicating long probes.

Remaining risks: fake-provider success can seduce future sessions into overclaiming durability. Keep OPFS, reload/crash, quota, eviction, fsync, and exactly-once as non-claims until separately earned.

## Rev0023 estimate recalibration amendment

The release estimate budget check fired once during rev0028 because several estimates still reflected older, slower assumptions. Rather than raising the budget, the manifest was recalibrated against observed release timings with conservative headroom. Future sessions should repeat that pattern: timing metadata is part of the facility and should be maintained like source code.

## Rev0036 release-facility refactor

Broad release now keeps the current admission-history proof/audit plus the new admission-model proof/audit in release, while older detailed contract audits remain runnable by explicit id or `audit`/`full` tier. This keeps future-session release windows cheaper without deleting carry-forward surfaces.

