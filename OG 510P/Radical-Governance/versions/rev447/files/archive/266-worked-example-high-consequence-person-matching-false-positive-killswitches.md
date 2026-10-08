# Worked Example High-Consequence Person Matching, False Positives, and Killswitch Overrides

**Purpose:** design hard safety rails for person-matching decisions that can instantly cut off liberty, money, mobility, or basic services when the system attaches the wrong severe state to the wrong person.

**Person served:** someone treated as dead, departed, detained, sanctioned, duplicated, or otherwise disqualified because a high-consequence match fired without enough proof.

**From-below:** a false positive in a severe registry can unperson someone faster than almost any other bureaucratic move, so these matches need stricter proof and faster reversal than ordinary data corrections.

---

## Use this memo when
- a death, incarceration, removal, sanctions, or watchlist match suspends a live person;
- the institution wants to use severe third-party or cross-jurisdiction status feeds against a person;
- a mismatch or duplicate state is being treated as evidence of fraud or ineligibility.

---

## Required artifacts

### 1) High-consequence match receipt (`HMR-*`)
Before severe downstream action, emit a receipt naming:
- the source system and match class;
- whether the match is tentative or confirmed;
- what second source or human verification is required;
- what the person can carry immediately if the match is wrong.

### 2) False-positive killswitch
High-consequence systems MUST have a same-day override that:
- freezes downstream enforcement, extraction, or cutoff;
- marks the severe state as contested everywhere it has already propagated;
- records who invoked the override and on what basis.

### 3) Restoration propagation proof
If a false positive is cleared, the institution MUST prove:
- which downstream systems consumed the original state;
- when each consumer received the override;
- whether any make-good, back pay, or apology/aftercare is required.

---

## Safe defaults
- **Two-source rule for severe states.** One unverified feed or weak match is not enough for rights-destroying action.
- **No fraud inference from ambiguity alone.**
- **Portable override proof now, merits review later.**
- **Every false positive becomes an audit incident, not just a corrected row.**

---

## Minimum tests
- Can the institution show what evidence confirmed the severe match?
- Is there a same-day kill switch that a real operator can invoke?
- Does override proof propagate to every known consumer of the bad state?
- Are false positives counted and independently reviewed?

---

## Companion cases and memos
Use `WX-37`, `WX-39`, `WX-43`, `WX-53`, and `WX-55` in `235-worked-examples-and-trace-walkthroughs.md`. Pair with `252-worked-example-halt-authority-stop-rules-and-escalation-ladders.md`, `253-worked-example-reversal-propagation-reinstatement-and-restoration-proof.md`, `254-worked-example-harm-accounting-back-pay-and-aftercare.md`, `257-worked-example-independent-verification-sampling-and-replay-packets.md`, and `264-worked-example-identity-resolution-aliases-and-transliteration-safe-defaults.md`.
