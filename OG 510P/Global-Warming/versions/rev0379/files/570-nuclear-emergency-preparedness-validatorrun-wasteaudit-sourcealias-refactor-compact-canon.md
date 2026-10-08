# 570 — Nuclear emergency preparedness: validator-run audit, waste burn-down, and source-alias control

Revision: **rev0363**  
Base: **rev0362**  
Status: package hygiene and validator-truthfulness control; public-context-only; no real-site readiness claim.

## Why this file exists

Rev0362 correctly built the watchdog pager and exception bridge, but the package around it had begun to confuse three different things: a generated report, an executable validator result, and an archive-hygiene plan. That is dangerous in a claim-frozen emergency-preparedness cube because a false green package signal can become a false green public claim.

Rev0363 therefore adds a validator-run audit and a cloudtainer waste audit. The success state is not readiness. The success state is **capture-ready / claim-frozen / executable-validation-honest / source-alias-aware / waste-burn-down-started**.

## Severe correction

The uploaded rev0362 watchpager validator treated any `actual_state` containing the substring `closure` as an automatic closure unless it was exactly `candidate_for_adjudication_not_closure`. That accidentally flags the intended negative-control state `rejected_closure_attempt`. The rev0362 validation report said the validator passed, but direct execution of the uploaded validator returned `FAIL bad=0 auto=16`.

Rev0363 patches the validator to use exact forbidden closure-state matching. `rejected_closure_attempt` remains allowed. A closure state must be an explicit forbidden value such as `auto_closure`, `accepted_closure`, or `local_readiness_closure`; text substrings are not sufficient.

## Hard rule

A validation report row, README pointer, source ID, duplicate URL, archive filename, planned output name, pending check, reserved check, generated table catalog, SQLite mirror, zip namelist, or fixture extension can support package hygiene. It cannot automatically prove readiness, close a local emergency-preparedness gap, or override the claim freeze.

## What is missing

1. **Real or anonymized exercise evidence packet.** The cube still has public-context scaffolding, not local readiness proof.
2. **Executed-check ledger discipline.** Historical reports include rows that were planned, pending, or reserved but marked pass. Future revisions need an executed command/output ledger.
3. **Source alias normalization.** Many source IDs point to the same canonical URL. That can be useful provenance, but duplicate source IDs must never be counted as independent corroboration.
4. **Archive burn-down policy.** Large historical SQLite mirrors and repeated traceability matrices dominate the package. The next cleanup should decide what is canonical current-state data, what is historical audit data, and what should move to an external evidence bag.
5. **Inert fixture policy.** Synthetic malware-looking fixture extensions are text markers, but they create avoidable operator/security noise. The next cleanup should rename them inertly or require an explicit fixture manifest.

## What should change next

- Every validation report row gets one of: `executed_pass`, `executed_fail`, `static_pass`, `info`, or `pending`. Plain `pass` should be reserved for checks that actually ran or were actually measured.
- The README is a current front door, not a historical fossil. Rev0363 updates it to point to the latest file and the corrected validator.
- New source registration prefers canonical URL reuse. New source IDs are allowed for genuinely new sources, but duplicate URLs become aliases and are cluster-counted once.
- The package should stop carrying every old SQLite mirror in every linked revision unless the mirror is required for current validation or a historical reconstruction task.
- The table/resource manifest regeneration step should be invoked only after all content mutations, and post-zip checks should be recorded separately from pre-zip validation.

## Speculative outside pressure

Current public context makes this worth tightening. FEMA had a Beaver Valley evaluated exercise window in the week of June 8, 2026 and a public meeting clock for June 12, 2026. NRC/FEMA guidance and role boundaries still make state/local offsite preparedness and licensee onsite responsibilities separate, and the NRC's 2026 Reactor Oversight Process changes may make public readers more sensitive to whether an inspection reduction is being overread as a readiness claim. The cube should therefore become more conservative, not less: public pages and oversight-efficiency claims route questions; they do not close evidence.

## Correct successful outcome

Rev0363 proves only that this package now catches the rev0362 validator bug, records the waste/source-alias debt, patches the current validator path, and preserves the no-automatic-closure invariant. It does not prove Beaver Valley, any county, any ORO, any controller, any evaluator, any siren/alert system, any EOC/EOF/JIC, any facility, or any public protective action pathway is ready, sufficient, safe, passed, demonstrated, certified, released, or closed.
