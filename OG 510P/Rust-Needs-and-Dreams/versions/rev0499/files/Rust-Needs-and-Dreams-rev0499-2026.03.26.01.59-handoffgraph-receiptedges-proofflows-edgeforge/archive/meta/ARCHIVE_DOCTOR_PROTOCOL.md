## rev0499 doctor addendum — handoff graph is now first-class maintenance terrain
The archive doctor now also checks the shared **handoff graph ledger**.
A passing doctor run should therefore mean not only that the archive can rank, wedge, journey-map, and shipset strong seams, but that it still keeps a machine-readable answer to **what receipt-bearing edges should connect them**.

## rev0498 doctor addendum — kernel shipset ledger is now first-class maintenance terrain
The archive doctor now also checks the shared **kernel shipset ledger**.
A passing doctor run should therefore mean not only that the archive can rank, watch, falsify, wedge, and compose strong seams, but that it still keeps a machine-readable answer to **what exact first shipsets the currently kernelized seams should take**.

## rev0497 doctor addendum — decision journeys are now first-class maintenance terrain
The archive doctor now also checks the shared **decision-journey ledger**.
A passing doctor run should therefore mean not only that the archive can rank, watch, falsify, and wedge strong seams, but that it still keeps a machine-readable answer to **which repeated operator moments those seams should compose inside**.


## rev0496 doctor addendum — launch-wedge ledger is now first-class maintenance terrain
The archive doctor now also checks the shared **launch-wedge ledger**.
A passing doctor run should therefore mean not only that the archive can rank, watch, and falsify strong seams, but that it still keeps a machine-readable answer to **how those seams first become real for users**.

## rev0488 doctor addendum — schema packs are now first-class maintenance terrain
The archive doctor now also checks the first top-band **artifact schema pack**.
A passing doctor run should therefore mean not only that witness and fixture corpora exist, but that bound specimen payloads still validate against their schema families.

## Kernel-fixture doctor addendum (rev0487)
If the repo now keeps a **shared kernel-fixture corpus** for replayable top-band scenario inputs, the doctor pass must treat that corpus as part of archive health rather than optional prose.

Minimum additions:
- require `meta/KERNEL_FIXTURE_PACK_PROTOCOL.md`, `fixtures/README.md`, `fixtures/top-band-v0/README.md`, `fixtures/top-band-v0/fixture-pack-hygiene-checks.json`, and `tools/check_kernel_fixture_packs.py`;
- run `python tools/check_kernel_fixture_packs.py` as a required machine check;
- include a `kernel_fixture_cards` corpus count;
- and keep the non-claim explicit: a passing kernel-fixture check proves structure, coverage, and linked-asset existence, not that the replay scenarios are strategically sufficient or semantically correct.

## Exemplar-federation doctor addendum (rev0466)
If the repo now keeps a **shared exemplar federation** for maintained proving worlds, the doctor pass must treat that federation as part of archive health rather than optional prose.

Minimum additions:
- require `meta/EXEMPLAR_FEDERATION_PROTOCOL.md`, `proofgrounds/portfolio-exemplar-federation-v0/README.md`, `proofgrounds/portfolio-exemplar-federation-v0/exemplars.json`, `design/portfolio-exemplar-federation-2026Q1.md`, and `tools/check_exemplar_federation.py`;
- run `python tools/check_exemplar_federation.py` as a required machine check;
- include a `federated_exemplars` corpus count;
- and keep the non-claim explicit: a passing exemplar-federation check proves structure, binding coverage, and linked-asset existence, not that the exemplar worlds are fresh or institutionally sufficient.

## Contribution-shape doctor addendum (rev0437)
If the repo now keeps a **shared contribution-shape atlas** for choosing intervention forms, the doctor pass must treat that atlas as part of archive health rather than optional prose.

Minimum additions:
- require `meta/CONTRIBUTION_SHAPE_PROTOCOL.md`, `morphologies/README.md`, `morphologies/portfolio-contribution-shapes-v0/shapes.json`, `design/portfolio-contribution-shapes-2026Q1.md`, and `tools/check_contribution_shapes.py`;
- run `python tools/check_contribution_shapes.py` as a required machine check;
- include a `contribution_shape_cards` corpus count;
- and keep the non-claim explicit: a passing contribution-shape check proves structure, coverage, and linked-asset existence, not that the archive picked the strategically best shape for every seam.

## Source-atlas doctor addendum (rev0436)
If the repo now keeps a **shared source atlas** for recurring authority lanes, the doctor pass must treat that atlas as part of archive health rather than optional prose.

Minimum additions:
- require `meta/SOURCE_ATLAS_PROTOCOL.md`, `atlases/README.md`, `atlases/portfolio-source-atlas-v0/sources.json`, `design/portfolio-source-atlas-2026Q1.md`, and `tools/check_source_atlas.py`;
- run `python tools/check_source_atlas.py` as a required machine check;
- include a `source_atlas_cards` corpus count;
- and keep the non-claim explicit: a passing source-atlas check proves structure, coverage, and linked-asset existence, not source freshness or claim truth.

## Hypothesis-ledger doctor addendum (rev0435)
If the repo now keeps a **shared hypothesis ledger** for live canon claims, the doctor pass must treat that ledger as part of archive health rather than optional prose.

Minimum additions:
- require `meta/HYPOTHESIS_LEDGER_PROTOCOL.md`, `ledgers/README.md`, `ledgers/portfolio-hypothesis-ledger-v0/hypotheses.json`, `design/portfolio-hypothesis-ledger-2026Q1.md`, and `tools/check_hypothesis_ledger.py`;
- run `python tools/check_hypothesis_ledger.py` as a required machine check;
- include a `portfolio_hypotheses` corpus count;
- and keep the non-claim explicit: a passing hypothesis-ledger check proves structure and linked-asset existence, not strategic truth.

# Meta: Archive Doctor Protocol (rev0434)

## Purpose
Use this protocol when the repo needs one repeatable maintainer-facing health pass.
This protocol is **not** the same as:
- evidence renewal,
- candidate triage,
- pilot scoring,
- or seam-local semantic validation.

It exists for the narrower question:
> what minimum structure checks, hard validators, queue pointers, and receipt fields should a serious archive-health pass leave behind?

Read with:
- `design/portfolio-archive-doctor-2026Q1.md`
- `design/portfolio-conformance-validation-2026Q1.md`
- `design/portfolio-evidence-renewal-2026Q1.md`
- `design/portfolio-proving-grounds-2026Q1.md`
- `design/portfolio-anchor-corpus-2026Q1.md`

## Required phases
Every doctor pass should include:

1. **required-file presence**
   - root canon files present
   - core meta files present
   - doctor protocol present
   - required validator scripts present
   - required proving-grounds assets present
   - required anchor-corpus assets present
   - required exemplar-federation assets present

2. **required machine checks**
   - `python tools/check_cargo_report_pack_contract.py`
   - `python tools/check_portfolio_envelope_contract.py`
   - `python tools/check_proving_ground_matrix.py`
   - `python tools/check_anchor_corpus.py`
   - `python tools/check_exemplar_federation.py`

3. **manual-follow-up pointers**
   - `meta/CANONICAL_RENEWAL_QUEUE.md`
   - `meta/DEFAULT_CARD_RENEWAL_QUEUE.md`
   - `meta/ACTIVE_FRONTIER.md`
   - `meta/CANONICAL_WORKING_SET.md`

4. **last-run receipt**
   - machine-readable JSON
   - written to `meta/ARCHIVE_DOCTOR_LAST_RUN.json` by default

## Required receipt fields
Every doctor receipt should include:

1. **identity**
   - schema family
   - tool path
   - repo revision
   - generated-at time

2. **summary**
   - overall status
   - number of required files checked
   - number of checks passed
   - number of checks failed

3. **required files**
   - explicit file list
   - per-file existence status

4. **check results**
   - check name
   - command
   - pass/fail status
   - short output excerpt

5. **small corpus counts**
   - at minimum specimens, invalid fixtures, proving-ground scenarios, anchor profiles, federated exemplars, and design/meta file counts relevant to shared maintenance

6. **manual follow-up queue**
   - named queue or working-set file
   - path
   - short reason why human review is still needed

7. **limitations**
   - what this run did not prove

## Hard failures
A doctor run must fail when:
- a required file is missing;
- a required validator exits non-zero;
- the proving-grounds checker exits non-zero;
- the anchor-corpus checker exits non-zero;
- the exemplar-federation checker exits non-zero;
- the receipt cannot be emitted;
- or the protocol references a required doctor asset that does not exist.

## Required non-claims
A doctor run must **not** claim that it:
- refreshed external evidence;
- reranked seams;
- resolved hot renewal items;
- or validated seam-local payload semantics beyond the wired checks.

## Minimum anti-cheating rules
- A passing doctor run is **not** an evidence-renewal verdict.
- A passing doctor run is **not** a promotion decision.
- A passing doctor run is **not** a substitute for reading the hot queues.
- A passing doctor run is **not** proof that all citations are fresh.
