# Priority-0 external response dry-run gate — 2026-06-16

## Risk burned

`rev0367` made the response intake harder to fake, but the live gap was still uncomfortable: the cube had a sealed responder bundle and scorer path, yet no completed response had traversed the whole lane. In this same session, a clean external/operator-independent response cannot be created without lying about exposure, because the session has already seen scorer-only material and prior archive state.

The dangerous move would be to hide that contamination and call the response independent. The useful move is narrower: exercise the response/scoring path end-to-end, prove strict external mode rejects the contaminated file, and make the next clean handoff easier to run.

## Change made

This revision resolves `OQ-0259` narrowly by adding a submit-hardened responder kit and a contaminated dry-run response that is explicitly **not** external evidence.

New current surfaces:

- `docs/40-session/priority-zero-external-response-dryrun-gate-2026-06-16.md`
- `assays/priority-zero-external-response-dryrun-gate-2026-06-16.json`
- `assays/priority-zero-submit-hardened-external-replay-responder-only-2026-06-16.json`
- `assays/priority-zero-submit-hardened-external-replay-response-template-2026-06-16.json`
- `handoffs/priority-zero-submit-hardened-external-replay-responder-readme-2026-06-16.md`
- `handoffs/priority-zero-submit-hardened-external-replay-handoff-manifest-2026-06-16.json`
- `handoffs/priority-zero-submit-hardened-external-replay-responder-bundle-2026-06-16.zip`
- `assays/priority-zero-submit-hardened-external-replay-scorer-intake-2026-06-16.json`
- `assays/priority-zero-submit-hardened-external-replay-contaminated-dryrun-response-2026-06-16.json`
- `assays/priority-zero-submit-hardened-external-replay-contaminated-dryrun-score-summary-2026-06-16.json`
- `tools/build_priority_zero_submit_hardened_handoff_bundle.py`
- `tools/check_priority_zero_external_response_dryrun_gate_contract.py`
- `tools/score_priority_zero_external_replay_response.py`
- `tools/check_priority_zero_response_intake_hollowguard_contract.py`

## What the dry-run proves and does not prove

Strict scorer mode rejects the contaminated response because the response records scorer-key/full-archive exposure before response completion. Dry-run mode accepts it only with `external_response_evidence=false`, then totals complete manual scores.

The dry-run score summary is `39 / 72` across the four packets:

| Packet | Score | Max | Meaning |
|---|---:|---:|---|
| packet-alpha | 4 | 18 | Decoy/sham cues are rejected or abstained from. |
| packet-bravo | 17 | 18 | Compact cue recovers mission/routing but remains non-independent. |
| packet-charlie | 2 | 18 | No-archive baseline mostly abstains. |
| packet-delta | 16 | 18 | Full trace recovers more exact provenance but is not blind input. |

This proves only that the scorer can process an answer-bearing response while preserving the contamination boundary. It does not confirm compact reentry.

## Audit / refactor

The scorer now has an explicit contaminated dry-run mode, complete manual-score label coverage checks, and per-label summary output. The default remains strict: contaminated responses fail unless the caller explicitly opts into dry-run mode.

`tools/check_priority_zero_response_intake_hollowguard_contract.py` is now historical `rev0367` evidence rather than the current-tail authority. The live current checker is `tools/check_priority_zero_external_response_dryrun_gate_contract.py`.

## Scores

| Variant | Score | Operator cost | Interpretation |
|---|---:|---:|---|
| Pre-dryrun hollowguard only | 6 / 16 | 4 min | Good hollow/leak guard, but no answer-bearing dry-run or responder README. |
| Submit-hardened responder kit | 12 / 16 | 5 min | More runnable handoff, still not clean response evidence. |
| Contaminated dry-run score path | 14 / 16 | 10 min | End-to-end scoring exercised; strict mode rejects it as external. |
| Clean external response evidence | 0 / 16 | 0.5 min | Correctly absent. |

## Non-takes

This is not a clean external replay result, not independent certification, not deletion authority, not a minimality proof, not benchmark authority, not compact-cue confirmation, and not a review court.

## Next action

Hand only `handoffs/priority-zero-submit-hardened-external-replay-responder-bundle-2026-06-16.zip` to a responder who has not seen scorer-only material, this full archive, or this conversation. After their response is frozen, score it with `assays/priority-zero-submit-hardened-external-replay-scorer-intake-2026-06-16.json`. That successor is `OQ-0260`.
