# Audit — rev0166

## Scope

This audit treated the linked rev0165 preliminary ZIP and the later unshipped continuation/history branch as competing release inputs. It asked whether the combined artifact actually serves two intended recipients: a player who should be able to start without protocol study, and a researcher who should be able to run the clean comparison without silently weakening its denominator or contamination controls.

The audit covered archive membership, entrypoint claims, package self-checking, complete public-history custody, continuation modes, whole-tree canary coverage, large-file scan behavior, source/clean-extraction parity, and current documentation. It did not treat model identity, provider isolation, creative quality, or comparative efficacy as kernel properties.

## Finding A166-01 — claimed player entrance absent from the linked archive

**Observation.** The rev0165 revision record claimed a player-only `PLAY_NOW.md`, but the linked preliminary ZIP contained neither that file nor a manifest entry for it.

**Risk.** Code, schemas, links, and the manifest could all pass while the daughter-facing onboarding claim was false. The recipient would enter through long operator material.

**Repair.** Added `PLAY_NOW.md`, routed it before reference material, required it in `MANIFEST.sha256`, and added release-surface tests.

## Finding A166-02 — the researcher entrance was implicit

**Observation.** The detailed Gwern design note existed, but there was no concise top-level statement of the implemented six-stage mapping, the context-window confound, the nonclaims, and the shortest executable appraisal path.

**Risk.** A recipient would need to reconstruct the gift thesis from several long manuals—the exact onboarding burden Lacuna is intended to reduce for weaker coordinators.

**Repair.** Added `FOR_GWERN.md` and made player, researcher, and operator routes distinct.

## Finding A166-03 — source acceptance did not close package acceptance

**Observation.** The preliminary acceptance record left final manifest/member/clean-extraction checks pending, and the archive filename itself remained preliminary.

**Risk.** A passing source suite could be mistaken for a final send receipt. A manifest can also faithfully describe the wrong member set.

**Repair.** Added `artifact check`, final package fields, an exact archive member comparison, executable-mode inspection, clean-extraction smoke, and clean-extraction test groups. The launcher disables bytecode writes so checking a pristine tree does not make it non-pristine.

## Finding A166-04 — explicit transcript lists were easy to overdescribe as complete

**Observation.** Public-history v1 authenticated the turns supplied by the parent but had no ledger-defined denominator. A valid ordered list could omit an earlier durable public turn.

**Risk.** A fresh-narrator condition could receive less public context than its control while being described as parity, confounding the bottleneck experiment.

**Repair.** Retained and integrated public-history/view v2 plus `history complete`. Explicit lists now say `not-claimed`; checkpoint-bound censuses say `complete` only after one-to-one ledger/run matching. Continuation dispatch v2 exposes `typed-only`, `bound-public-history`, or `complete-bound-public-history` rather than hiding the difference.

## Finding A166-05 — the later branch reintroduced a contamination blind spot

**Observation.** The later onboarding/history candidate excluded cloned cube subtrees from canary scanning and narrowed the scan to selected experiment artifacts. It also stopped treating relative pathnames as a search surface.

**Risk.** Private bytes could be committed into a perfectly valid SQLite cube, placed in a database sidecar or lock, or encoded in a retained pathname and still receive a clean scan. Cube verification proves ledger/projection consistency; it does not prove absence of a canary.

**Repair.** Restored rev0165’s complete retained-tree content/path policy and merged it with the newer history/onboarding work. The scan now has no cube, sidecar, lock, basename, or suffix exemption and fails closed on traversal omissions.

## Finding A166-06 — whole-file buffering was unnecessary for large retained members

**Observation.** The strongest scan coverage can include SQLite databases large enough that reading each member wholesale is avoidable pressure. The existing bounded read helper also mixed opening/authentication mechanics with body materialization.

**Risk.** Memory use scaled with the largest retained file, and duplicating descriptor checks in a separate scanner would invite security drift.

**Repair.** Extracted shared open/post-read descriptor-authentication helpers and added `scan_sidecar_member_exact_tokens`. It computes SHA-256 and exact-token counts incrementally, retains only the overlap needed to detect boundary-spanning tokens, and reauthenticates the pathname and descriptor after EOF.

## Finding A166-07 — scan prose had drifted from executable coverage

**Observation.** Living guides and glossary text still described “experiment-artifact” scope, excluded cube subtrees, or separately verified SQLite state even after the stronger implementation existed.

**Risk.** A careful operator could follow documentation and intentionally reproduce the weaker blind spot.

**Repair.** Updated the operator, scenario, glossary, roadmap, architecture, gift, and release notes to state the complete retained regular-file content/path boundary and its exact nonclaims.

## Finding A166-08 — current release records described only the onboarding subset

**Observation.** Early rev0166 records claimed no new exchange schemas and “unchanged rev0165 experiment semantics,” which became false after merging public-history/continuation v2 and the streaming scanner.

**Risk.** The archive could be internally correct while its own revision, decision, research, and acceptance records understated what changed.

**Repair.** Rewrote the current records around the actual integrated revision and made final counts/digests package-derived.

## Regression and adversarial coverage

The acceptance path includes positive and negative checks for:

- complete versus explicit public history, zero-turn census, missing/duplicate/stateless/wrong-boundary records, and rehashed prose forgery;
- continuation mode binding and fresh-turn/head/profile restrictions;
- canaries in committed cube state, SQLite sidecar names, lock names, relative pathnames, same-cell/cross-cell outputs, and chunk-boundary content;
- traversal errors, links, multiple links, nonregular members, size/race/tree-drift refusal;
- package member/version/link/parse mismatches; and
- source-tree versus clean-extraction behavior.

## Residual risks

- The three entrances are tested release members, not evidence from a usability study.
- The complete history census cannot include uncommitted chat or recover prose whose managed sidecar was lost.
- Exact canaries do not detect paraphrase, semantic leakage, unretained channels, or hidden memory that never emits the token.
- Provider routes, model/context IDs, timing, tool denial, and fresh-context claims remain host declarations unless independently attested.
- A hostile distributor can replace archive and verifier together unless a recipient independently retains a trusted digest.
- The comparative experiment still needs real provider calls/subagents, fixed budgets, all failed/refused cells, and blind human ratings.

## Disposition

Rev0166 is suitable to send only when its final `REVISION.json`, acceptance record, manifest, ZIP exact member set, SHA-256, executable mode, clean artifact check, and complete clean-extraction tests all agree. That establishes a send-ready instrument, not a positive scientific result.
