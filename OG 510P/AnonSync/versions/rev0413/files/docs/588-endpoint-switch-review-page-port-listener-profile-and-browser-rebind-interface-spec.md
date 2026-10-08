# Endpoint switch review page — port, listener, profile, and browser rebind interface spec

## Purpose

Review any action that could make the browser point at a different control world.
This page answers:

- is this change just exposure hardening, or a real control-world switch
- what runtime / storage / audience facts will change
- will existing tabs, bookmarks, cookies, or handlers become ambiguous afterward
- what post-change claims remain safe

## Inputs

- current endpoint attestation object
- proposed change set (port, scheme, bind scope, storage path, config path, runtime kind, principal, service/app lane)
- predicted browser / handler consequences
- predicted seat-lineage verdict after apply
- predicted claim ceiling after apply
- rollback route

## Primary questions this page must answer

1. What exactly is changing?
2. Does the endpoint stay in the same control world?
3. What browser artifacts become stale afterward?
4. What must the operator verify after apply?
5. What stronger claim becomes forbidden unless re-attested?

## Layout

### A. Switch verdict strip

Fields:

- current endpoint
- proposed endpoint/world summary
- switch class (`same-world-rebind`, `same-world-grade-change`, `sibling-world-switch`, `fresh-world-launch`, `uncertain`)
- strongest safe summary

### B. Before / after matrix

Rows:

- runtime watermark
- principal / service account
- storage root
- config path
- bind scope / host / port
- auth posture
- transport posture
- browser-target confidence
- claim ceiling

### C. Browser rebind consequences

Show:

- which existing tabs become stale
- which bookmarks / deep links become ambiguous
- whether cookies remain valid, invalid, or misleading
- whether browser trust residue must be cleared or re-evaluated

### D. Post-apply verification checklist

Require:

- open re-attested endpoint
- verify runtime watermark
- verify storage lineage
- verify expected roster / identity surface
- verify new claim ceiling

### E. Rollback and fallback

Show:

- rollback lane
- whether rollback preserves same runtime world
- what residue remains even after rollback

## Behavior rules

- Any change that can alter runtime watermark or storage lineage must be classified as a control-world switch, not merely a preference edit.
- Browser residue from the old endpoint must be treated as potentially misleading until post-apply attestation completes.
- The page must never collapse `same hostname` or `same port family` into `same control world`.

## Output object

```text
endpoint_switch_review {
  current_endpoint_id,
  proposed_change_set,
  switch_class,
  before_after_matrix,
  browser_rebind_effects,
  verification_steps[],
  rollback_path,
  strongest_safe_sentence,
  stronger_forbidden_sentence
}
```