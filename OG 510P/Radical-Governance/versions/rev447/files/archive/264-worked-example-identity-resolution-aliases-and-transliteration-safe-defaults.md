# Worked Example Identity Resolution, Alias Maps, and Transliteration Safe Defaults

**Purpose:** make “same person, different rendering” governable so script changes, transliteration drift, name-order differences, date-format mismatches, and duplicate-person seams do not silently turn into denial, delay, or fraud suspicion.

**Person served:** a person whose identity is already real enough to live with, but not legible enough for the institution’s matching rules.

**From-below:** identity resolution must not require the governed to re-prove their existence from zero every time a record crosses a script, vendor, or jurisdiction seam.

---

## Use this memo when
- a person’s record no longer matches after moving across jurisdictions, scripts, or naming conventions;
- the system says “cannot verify” but the mismatch is mostly formatting, transliteration, or alias drift;
- duplicate-person cleanup risks merging the wrong people or splitting one person into several administrative selves.

---

## Required artifacts

### 1) Identity discrepancy receipt (`IDR-*`)
When identity matching fails or becomes ambiguous, emit a person-usable receipt that states:
- the compared records and their owners;
- which fields diverged (script, transliteration, name order, date format, identifier, household reference);
- what the system is still willing to treat as safely continuous while review runs;
- who owns the resolution clock and how to contest or supplement the record.

### 2) Alias and transliteration map
High-volume systems SHOULD maintain a governed alias/transliteration table:
- source script and normalized rendering;
- known historical names or legal-name changes;
- date-format and identifier normalization rules;
- confidence class and human-review threshold.

### 3) Duplicate-resolution packet (`DRP-ID-*`)
When a person may have duplicate records, produce a packet that names:
- candidate record IDs;
- why the system thinks they may be the same person;
- the harm of a false merge versus a false split;
- which downstream systems will be notified if a merge/split is approved.

---

## Safe defaults
- **No punitive escalation from unresolved identity ambiguity alone.** A duplicate or mismatch state MUST NOT itself trigger fraud, abandonment, or enforcement without additional proof.
- **Continuity before tidiness.** For essential services and already-verified protections, preserve the last safe state while identity review runs.
- **Human review for high-consequence merges.** If merging could erase claims, payments, or protective flags, require accountable human sign-off.
- **Prove the match, not just the mismatch.** If the institution wants to collapse two records into one adverse outcome, it bears the burden to show why.

---

## Minimum tests
- Can the person see what fields actually failed to match?
- Does the system preserve the last safe continuity state while review runs?
- Is there a replayable record of why a merge or split happened?
- Can downstream systems prove they received the corrected identity state?

---

## Companion cases and memos
Use `WX-31`, `WX-52`, `WX-53`, and `WX-55` in `235-worked-examples-and-trace-walkthroughs.md`. Pair with `125-identity-membership-and-civil-status.md`, `44-identity-credential-and-eligibility-systems-register.md`, `109-portability-and-cross-jurisdiction-continuity.md`, `128-interoperability-interfaces-and-standards.md`, `255-worked-example-missing-records-adverse-inference-and-proof-failures.md`, and `266-worked-example-high-consequence-person-matching-false-positive-killswitches.md`.
