# rev0103 — Legal Action Page Count Contract

## Mission seam

rev0103 continues the legal-choice protocol work by making page cardinality explicit. The page API already had enough cursor evidence for a human reader to infer whether a page was terminal or only a prefix, but future agents, auditors, and replay tools should not have to reinterpret `actions_seen`, `next_cursor`, and `complete` by convention.

The mission remains trusted transitions:

```text
StateCore + chooser + explicit LegalAction -> validated next StateCore + typed evidence
```

The new count contract says what the page knows about the surrounding legal-choice domain at the same time it says what actions are inside the returned page.

## Page count fields

`LegalActionPage` now carries three explicit count fields:

- `total_actions_lower_bound`: the largest proven lower bound on the domain size observed while building this page;
- `total_actions_exact`: true only when the page scan reached the end of the finite domain;
- `remaining_actions_lower_bound`: a continuation lower bound beyond `next_cursor` when the page had to stop early.

For complete pages, `total_actions_exact == true`, `total_actions_lower_bound == actions_seen`, and `remaining_actions_lower_bound == 0`. For incomplete pages, the page carries at least one-action lookahead evidence, so `total_actions_exact == false` and `remaining_actions_lower_bound > 0` whenever the builder stopped because another legal action existed after the returned page.

## Protocol binding

The page protocol schema is now `kLegalActionPageSchemaVersion == 2`. `legal_action_page_hash(...)` uses `MTGSim.LegalActionPage.v2` and folds the count contract into the hash along with cursor metadata, page contents, schema version, and effective limit.

`LegalActionPageLocation`, `ActionReceiptRecord`, and `ActionTraceEntry` now carry the same count evidence. `serialize_action_trace(...)` emits `MTGSim.ActionTrace.v6` with:

- `choice_page_total_lower=`;
- `choice_page_total_exact=`;
- `choice_page_remaining_lower=`.

`parse_action_trace(...)` keeps v1-v5 compatibility. v5 traces still carry schema and page-hash evidence, but only v6 traces carry count-contract evidence.

## Audit/refactor change

The refactor is intentionally small but central: page finalization now computes count fields in one `finalize_legal_action_page(...)` path before hashing. That prevents invalid-player empty pages, priority pages, attack pages, block pages, damage-order pages, and zero-limit pages from drifting in how they describe exactness and continuation.

Receipt validation now rejects count evidence that disagrees with `actions_seen`, `page_complete`, or `next_cursor`. Replay recomputes the located page and rejects count drift through `ChoicePageLocationMismatch` before StateCore or Journal mutation.

## Regression coverage

rev0103 adds and extends tests proving that:

- first attack/block/damage-order pages expose lower-bound continuation evidence;
- terminal pages expose exact total counts;
- zero-limit pages keep one-action cursor progress while refusing to claim an exact total;
- locators copy page count evidence into `LegalActionPageLocation`;
- `ActionTrace.v6` serializes and parses the count fields;
- replay rejects count-field drift before mutation.

## Still open

This is still an enumerator-backed count contract, not a closed-form random-access solver. Large domains may expose lower bounds until a complete page or scan reaches the end. The next deeper slice is a small-state equivalence suite that compares direct validation, complete frontiers, page concatenation, page locations, receipts, and replay for domains small enough to enumerate exactly.


## rev0104 context seal note

rev0104 keeps the rev0103 count contract and adds page context evidence. The current page schema is v3: page hashes now include the pre-action StateCore hash and offered choice-request hash in addition to schema, cursor metadata, page contents, and count evidence. Serialized traces are now `MTGSim.ActionTrace.v7`; v6 traces remain parseable with page context wildcarded.
