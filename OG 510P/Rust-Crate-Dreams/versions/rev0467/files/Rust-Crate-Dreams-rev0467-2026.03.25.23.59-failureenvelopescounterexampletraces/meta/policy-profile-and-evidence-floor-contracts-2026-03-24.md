# Policy profile and evidence-floor contracts — 2026-03-24

## The problem this note solves

The archive already had:
- task profiles,
- basis locks,
- adjudication sessions,
- exception receipts,
- carry-forward receipts,
- and recheck tickets.

What it did **not** yet preserve cleanly was the difference between:

1. **the task** being solved,
2. **the adopter profile** asking,
3. **the evidence floor** that profile requires,
4. **the current satisfaction report** for that floor,
5. and **the non-claims** that survive even after the report says “pass”.

Without that separation, future passes will drift into fake universality.

## Contract vocabulary

### Task profile
A statement of:
- problem shape,
- constraints,
- target/runtime/interop needs,
- lock-in tolerance,
- and role priorities.

Question answered:
> “What kind of work are we trying to do?”

### Policy profile pack
A statement of:
- adopter class,
- required evidence floors,
- allowed exception budget,
- escalation requirements,
- and explicit non-claims.

Question answered:
> “What standard should this adopter hold the packet to?”

### Evidence floor
A specific minimum requirement such as:
- basis lock required,
- docs visibility required,
- target-support truth required,
- audit-policy evidence required,
- source-parity evidence required,
- or manual review forbidden/allowed.

Question answered:
> “What evidence must exist before we can say yes here?”

### Profile satisfaction report
A report that says:
- which floors are satisfied,
- which are conditional,
- which are missing,
- which exceptions are spending the budget,
- and what next action is required.

Question answered:
> “Under this profile, what is the honest answer right now?”

### Non-claim
A statement the crate refuses to imply even when the report says `pass`.

Question answered:
> “What should nobody read into this result?”

## Design rules

1. **Do not let task and profile collapse together.**
   The same task can have multiple legitimate profile answers.

2. **Do not let profile and certification collapse together.**
   A profile pack can be a reusable review standard without being a legal or regulatory certification.

3. **Do not let support visibility collapse into evidence sufficiency.**
   docs.rs visibility, crate popularity, Security-tab posture, and publishing trust can improve confidence without satisfying hard-domain floors by themselves.

4. **Do not let exceptions silently satisfy floors.**
   An exception can keep a posture temporarily workable.
   It should not masquerade as evidence that the floor is met.

5. **Do not let a `pass` result erase the ceiling.**
   Some profiles still end in `pass_with_manual_judgment` or `conditional`.

## Suggested profile families for the front-door stack

### `explore-default`
For:
- newcomers,
- experiments,
- prototyping,
- early internal comparisons.

Typical floor:
- task profile,
- candidate basis,
- docs visibility,
- basic lock-in notes.

### `team-default`
For:
- shared internal defaults,
- onboarding docs,
- common starter sets.

Typical floor:
- basis lock,
- knowledge pack,
- recheck trigger policy,
- explicit exclusions/runner-ups.

### `enterprise-offline`
For:
- mirror/vendoring users,
- restricted CI,
- air-gapped review.

Typical floor:
- basis lock,
- source-parity or restricted-delivery evidence,
- materialization plan,
- explicit missing-network assumptions,
- trusted publishing / provenance facts where relevant.

### `safety-onramp`
For:
- teams moving toward higher-assurance use,
- target-sensitive or certification-adjacent adopters.

Typical floor:
- target-support truth,
- MSRV / toolchain story,
- dependency-lifecycle posture,
- strong non-claims,
- likely manual-review requirement.

## Report status guidance

Preferred `0.1` statuses:
- `pass`
- `conditional`
- `manual_review_required`
- `fail`

Interpretation:
- `pass` — every required floor exists and no open exception exceeds profile policy.
- `conditional` — usable, but one or more missing floors are covered only by bounded exceptions or incomplete evidence.
- `manual_review_required` — the crate cannot honestly flatten the result into a simple approval/rejection yet.
- `fail` — the profile’s required floors are not met and no allowed exception path keeps the posture acceptable.

## What should count as a worthy crate contribution here

A worthy crate should provide:
- stable profile IDs,
- explainable floor evaluation,
- portable profile packets,
- profile-aware status reports,
- and profile-aware refusal boundaries.

It should **not** merely provide:
- one flat trust score,
- one rank list,
- or one universal recommendation string.

## Archive consequence

Future passes that touch the front-door stack should ask:
- which adopter profile is being served,
- whether that profile already exists,
- whether its floors are explicit,
- whether a profile satisfaction report could be emitted,
- and whether the crate’s non-claims stayed visible.

If the answer is “no,” then the pass should deepen profile discipline before inventing more crate ideas.
