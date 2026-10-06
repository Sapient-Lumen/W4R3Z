# DelayBasin priority repair and execution audit — rev0377 working overlay

Source working overlay: `DelayBasin-rev0376-2026.06.17.16.22-missiondeepread-lintmutates-hotcuefreeze.zip`  
Canonical state still named inside the cube: `rev0374` / `DelayBasin-rev0374-2026.06.16.13.45-preanswerclamp-scoretime-leakcut.zip`  
Status: **tested cloudtainer working overlay, not a canonical DelayBasin promotion**.

## Result

This pass spent its effort on four runnable defects rather than adding a new governance layer:

1. failed generated-surface validation could rewrite the tree it was judging;
2. the compact landing cue had regrown from 18 mission-bearing supports to the full 50-surface trace;
3. the OQ-0266 scorer lane still contained stale OQ-0264 → OQ-0265 routing and its standalone ZIP could not run its documented verification command;
4. live-ledger risk reporting was unreachable because lint capped each live set at 180 while the archive audit warned only above 200.

All four defects now have executable repairs. The full `215/215` lint suite passes, and SHA-256 snapshots of every working-tree file are identical before and after lint.

## 1. Lint now fails without repairing evidence

### Defect

`tools/generated_surface_lib.py#generated_surface_drift()` regenerated the target tree in place before reporting drift. A dirty first lint could fail after rewriting generated evidence; the rewritten tree could then pass on a second run.

### Repair

- regeneration now happens only in a temporary copy;
- the target generated surfaces are read once and compared byte-for-byte with the temporary result;
- the temporary tree is removed on success or generator failure;
- `tools/check_generated_surface_nonmutation_canary.py` deliberately corrupts a generated surface in a copied fixture, proves drift is detected, and proves every target-tree byte is unchanged;
- the canary is part of the normal validation toolchain;
- lint-idempotence and archive-economy audits now describe the actual temporary-copy mode.

### Evidence

- `check_generated_surface_nonmutation_canary: OK`
- `check_generated_surface_drift: OK`
- complete lint: `215/215`
- full-tree hash diff before/after lint: `0` lines

A temporary false alarm during this audit was traced to `__pycache__` files created by an ad hoc compile probe. After removing those probe artifacts and using `python -S` / `PYTHONDONTWRITEBYTECODE=1`, explicit generation reached a clean fixed point and the read-only drift check passed. No generator-loop workaround was added.

## 2. The hot path is separate from the trace again

### Defect

`canon_additions`, `touched_surfaces`, and all four landing `Current additions` cues had converged on the same 50-item list. The rev0362 burden-gate result—18 current supports—had become historical documentation rather than a live invariant. The old alignment checks also used substring membership, allowing certain partial/path-collision false passes.

### Repair

- `REVISION-RECEIPT.json` now has a distinct, ordered `hot_current_supports` field with exactly 18 mission-bearing surfaces;
- `canon_additions` and `touched_surfaces` retain the full 50-item trace;
- `README.md`, `START_HERE.md`, `AGENTS.md`, and both current-cue lines in `docs/README.md` match the 18-item list exactly and in order;
- `tools/hot_current_supports_lib.py` is the shared parser and policy source;
- landing alignment checks now compare parsed lists exactly rather than searching substrings;
- schema, receipt contract, current-receipt, currentness audit, and innovation packet were refreshed;
- the exact-restoration receipt coldstore was updated to keep the new current key hot and to refresh order, hashes, and byte accounting.

### Evidence

- landing counts: `18 / 18 / 18 / 18`
- trace counts: `canon_additions=50`, `touched_surfaces=50`
- `check_hot_current_supports_contract: OK (18/18)`
- receipt coldstore round trip: `125` cold keys, `55,680` net plaintext bytes saved
- context pack remains `6,305` bytes—the same footprint as the source overlay—because the exact hot list and rich debt audit were not redundantly copied into it.

## 3. The OQ-0266 scorer kit is now actually runnable

### Defects

The current scorer intake named OQ-0266 in its answer key but still contained a required check saying OQ-0264 must import a response and a metric routing OQ-0264 to OQ-0265. Separately, the scorer ZIP's README command could not run after extraction because the scoring program hashes the responder-only packet and response template, but the ZIP omitted both files.

The bundle builder also refreshed handoff-kit hashes without refreshing all copies embedded in the material-clamp assay scorecard.

### Repair

- scorer routing now treats OQ-0265 as closed and sends OQ-0266 to the actual clean response + distinct-custodian record + separate post-response score sheet;
- stale OQ-0264 routing strings are rejected by the material-clamp contract;
- the scorer kit now contains the responder-only packet and blank response template as post-freeze verification inputs;
- its README states that these inputs are included for hash verification, not responder exposure;
- the bundle builder synchronizes the assay scorecard's packet/template/bundle/manifest hashes after rebuild;
- the main contract extracts the scorer ZIP, creates a synthetic chronology-valid sheet, and runs the documented CLI end to end with `python -S`.

### Evidence

- `check_priority_zero_preanswer_material_clamp_contract: OK`
- scorer-kit SHA-256: `58575ae33ce84e377631d1658c86ffa353db19287f2c743e46b6eca4696e13c0`
- scorer ZIP contains nine files, including the two formerly missing verification inputs.

This removes an execution blocker; it does **not** manufacture the missing clean replay result.

## 4. Ledger debt is now visible where it can be acted on

### Defect

All four live debt families sit exactly at the lint budget of 180 rows. The archive-economy audit previously warned only above 200, so those risk branches could never execute in any lint-passing tree.

### Repair

- `tools/ledger_debt_policy_lib.py` is now the one source for state keys, live states, budgets, transition rules, risk IDs, and repair language;
- the ledger guard and archive-economy audit consume the same policy;
- the archive audit emits live count, budget, headroom, oldest live ID/revision, and age for all four families;
- risk flags fire at the budget, not at an unreachable threshold;
- the compact context pack retains its backward-compatible 12-field queue summary rather than absorbing another large registry.

### Current exposure

| Surface | Live | Headroom | Oldest live row |
|---|---:|---:|---|
| `FOLLOWTHROUGH-QUEUE.json` | 180/180 | 0 | `FT-0080` / `rev0178` |
| `ASSUMPTION-LEDGER.json` | 180/180 | 0 | `AS-0077` / `rev0178` |
| `OBLIGATION-LEDGER.json` | 180/180 | 0 | `OB-0072` / `rev0177` |
| `RETROSPECTIVE-QUEUE.json` | 180/180 | 0 | `RT-0058` / `rev0166` |

I did not mass-retire rows by heuristic. That would create the appearance of progress while risking destruction of unresolved obligations. The next debt pass should take a bounded oldest-first slice, classify rows against current evidence, and retire only rows with an explicit supersession, satisfaction, expiry, or duplicate witness.

## Remaining highest-risk work

The central missing object remains unchanged: a genuinely clean OQ-0266 response, followed by chronology-valid custody from a distinct custodian, followed by a separate post-response score sheet. The tooling is now more credible and the scorer kit is runnable, but no internal repair can substitute for that external triplet.

The second risk is zero live-debt headroom plus three overdue decay-watch rows. This now appears as an actionable audit failure pressure rather than an unreachable warning, but it still requires semantic review.

## Verification run

The final tested sequence for this overlay was:

```text
python -S tools/gen_all_generated_surfaces.py
python -S tools/check_generated_surface_drift.py
python -S tools/check_generated_surface_nonmutation_canary.py
python -S tools/check_priority_zero_preanswer_material_clamp_contract.py
python -S tools/check_receipt_coldstore_roundtrip_contract.py
make lint
python -S cloudtainer/tools/check_cloudtainer_mission_preflight.py
```

Observed: generation wrote 36 governed surfaces; drift and mutation canary passed; scorer and coldstore contracts passed; lint passed `215/215` with no tree mutation; cloudtainer preflight reported zero failures and only the intentionally unresolved debt/decay/OQ-0266 warnings.

## Non-claim

This overlay is not a clean external replay, not independent certification, not a canonical DelayBasin release, not proof that the 18-item support core is minimal, and not authority to delete or mass-retire historical evidence.
