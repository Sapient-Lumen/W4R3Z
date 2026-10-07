# Conservative Release Policy

This repository uses a deliberately conservative publication policy.

## Default answer

The default answer to "is this ready to publish?" is **no**.
A draft must positively earn publication.

## A paper is publishable only if all of the following are true

1. **Claim stability**
   - the central claim is unlikely to change in substance.

2. **Boundary stability**
   - the paper no longer appears to be in the middle of being split, merged, renamed, or re-owned by a neighboring note.

3. **Terminology stability**
   - notation and naming appear consistent with the current spine.

4. **Dependency containment**
   - the paper can stand publicly without requiring several still-moving unpublished siblings to make sense.

5. **Narrative sufficiency**
   - an outside reader can understand what is being claimed, why it matters, and what assumptions it uses.

6. **Frozen source path**
   - there is a clearly identified `.tex` source file to freeze.

7. **Low regret test**
   - if this exact version were cited six months from now, the maintainers would still be comfortable defending it as the public record.

## Reasons to hold

A paper should be held if any of the following are true:

- the draft is being actively decomposed into finer notes,
- the title or scope is still moving,
- a neighboring synthesis note is likely to absorb or redefine part of it,
- the public entry point is unclear,
- the current wording exposes internal process more than stable result,
- the note mostly serves local bookkeeping inside a still-moving research spine.

## Gentle release queue rule

Even after a paper is judged publishable, it does not need to be released immediately.
It may sit in the Published-ready queue until the release cadence is appropriate.

## Cadence rule

A slow queue is preferred over a fixed daily obligation.
The queue exists to protect judgment from schedule pressure.

## Execution guard

For new post-policy Anonymity releases, publishability is not enough. The publication execution step also requires a source-bound evidence pack, clean compile witness, non-public freeze packet, explicit publication decision, and a passing published-boundary audit. Use `publishing/create_published_entry.py`; do not manually copy a new release into `published/`.


rev0824 adds three conservative blockers: `reports/manifest_canonicality.json`, `reports/freeze_warning_resolution.json`, and `reports/toolchain_fingerprint.json`. They do not authorize publication.


rev0825 adds `reports/unicode_control_hygiene.json` as a conservative blocker. Hidden control characters, bidi controls, invisible format controls, noncharacters, or surrogates in text surfaces must be repaired before publication can be considered.
