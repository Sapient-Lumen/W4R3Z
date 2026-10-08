# Change freshness review page — expected detection latency, rescan cost, and intervention rungs interface spec

## Purpose

The archive already had route divergence and performance hypothesis review.
What it still lacked was the explicit page for the next question:

> given the current detection posture and coverage grade, what freshness claim is actually safe right now, and what is the cheapest intervention rung?

AnonSync should therefore issue a dedicated **change freshness review** before strong language like `stuck`, `late`, or `needs repair` is allowed.

## Review order

1. **Observed symptom and age**
2. **Declared detection budget**
3. **Freshness verdict**
4. **Rescan/probe cost**
5. **Least-strong intervention rung**
6. **Claim ceiling**

## 1) Observed symptom and age

Show:

- what change the operator expected to appear
- when the operator believes the change occurred
- current age of the observation gap
- confidence in the anchor time

## 2) Declared detection budget

Pull in the active posture and coverage review:

- notification-backed immediate/near-immediate expectation
- scheduled rescan window
- zero-rescan / manual-probe-only posture
- widened cadence for power/sleep reasons

## 3) Freshness verdict

Required verdicts:

- `within declared freshness budget`
- `freshness weak; blind window still open`
- `delay exceeds declared budget`
- `cannot judge because anchor or posture changed`

## 4) Rescan/probe cost

Show what a rescan would cost here:

- negligible verification step
- expensive but acceptable probe
- heavyweight enough to change runtime pressure
- semantically risky because it may alter the incident

## 5) Least-strong intervention rung

Offer the cheapest honest next step, such as:

- wait
- manual rescan
- restore notification capacity
- tighten rescan cadence
- restart to reactivate known posture
- escalate only after a bounded proof attempt

## 6) Claim ceiling

The page must publish both:

- strongest allowed sentence
- stronger rejected sentence

Examples:

- allowed: `The change may still be undiscovered until the next scheduled rescan.`
- rejected: `Sync is definitely stuck.`

## Compact rendering obligations

Any compact card must still preserve:

- symptom-age label
- freshness verdict
- latency budget label
- intervention rung
- claim ceiling summary

## Anti-clone rule

Do not clone flows where `rescan now` acts as an unexamined reflex and silently replaces the harder question of whether the product ever had timely observation here.
