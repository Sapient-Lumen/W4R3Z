# rev0214 — candidate challenge replay and downstream lock refactor

rev0214 closes the next live-risk seam after the first-artifact pilot: a real artifact candidate could be hash-staged and then socially treated as "basically admitted" before anyone rereads the private vault bytes, opens a challenge window, or blocks downstream object creation in a checkable way.

The change is deliberately operational rather than doctrinal. A pilot candidate now has a required pre-custody challenge/replay step: private-vault bytes must be reread, hash/size parity must be recomputed from the vault rather than trusted from the first staging event, a challenge window must stay reliance, and custody/response/intake/import/live-floor objects remain locked.

## What is new

- `tools/prepare_candidate_challenge_packet.py` consumes a first-real-artifact pilot report and the external private vault root, rereads the raw vault bytes, recomputes hash and size, and emits a public challenge report.
- `schemas/live-artifact-candidate-challenge-report.schema.json` defines the public challenge report object.
- `examples/live-artifact-candidate-challenge-report-rev0214-synthetic-pending.json` shows the allowed state: hash reverified, challenge pending, no custody release.
- `tools/audit_candidate_challenge_replay.py` proves the happy path and the hash-mismatch path with synthetic private bytes outside the release tree.
- `fixtures/negative-tests/candidate-challenge-hash-trust-without-vault-read.json` blocks the trust-me shortcut where a public shell hash is accepted without vault reread.
- `fixtures/negative-tests/candidate-challenge-releases-custody-while-pending.json` blocks the procedural shortcut where a pending challenge is treated as custody or response authority.

## New rule

Evidence drop may open a LEAP candidate, but **LEAP candidate state is not custody**. Before any custody handoff, the candidate must survive candidate challenge/replay:

1. read private-vault raw bytes from outside the release tree;
2. recompute hash and size;
3. bind reread results to the public shell and LEAP candidate;
4. open or record the challenge route;
5. treat counterparty silence as non-waiver;
6. keep reliance stayed unless and until the later custody, verifier, authority, response, intake, import, replay, and computed-floor gates independently pass.

A successful rev0214 challenge report is still not a live receipt. It only proves that a candidate remained challengeable without leaking raw bytes. The live receipt floor therefore remains zero.

## Refactor effect

rev0214 refactors the pilot route from a single staging command into a two-step minimum:

- `prepare_first_real_artifact_pilot.py` stages raw bytes and may emit a locked LEAP candidate.
- `prepare_candidate_challenge_packet.py` rereads the external private vault and emits a public challenge report before custody review.

This removes a wasteful and dangerous ambiguity: the same hash shell no longer has to carry staging, challengeability, custody readiness, and public disclosure functions at once. Each stage now has a narrower object and a separate audit.

## Still not done

No genuine external artifact is present in this archive. The next high-risk work item remains a deliberately small real-world artifact pilot, followed immediately by candidate challenge/replay and then only by custody/verifier/response/intake/import/recompute if each gate passes.
