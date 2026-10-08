# Research — rev0164

## Research question

Can Lacuna make the strongest retcon-planning treatment both experimentally cleaner and easier for a human or weaker model to operate, without silently depriving the fresh narrator of public facts that persistent-context controls remember for free?

## Result in this revision

Operationally, yes.

Rev0163 authenticated a compact post-checkpoint narrator capsule. It still required a parent to informally combine that capsule with the next player input, create the correct kind of turn, and convert the narrator output into the exact proposal eventually committed. It also left transcript parity as prose guidance because the cube intentionally stores narration digests rather than all transcript bodies.

Rev0164 supplies three exact artifacts:

1. a continuation dispatch joining one committed checkpoint to one fresh source-bound ordinary turn;
2. a full public-history artifact carrying exact visible prose plus parent/auditor source custody; and
3. a least-context public-history view carrying only the ordered prose needed by the fresh narrator.

The full history is authenticated against immutable request sources, narration sources, proposal changesets, and ledger positions before its view can enter a continuation.

## Why the extra bridge matters

A clean context reset can fail in two opposite directions:

- **too much information:** the old narrator remembers rejected candidates, score rationale, parent analysis, and desired treatment behavior;
- **too little information:** a new narrator receives only sparse typed state and loses visible facts that existed in earlier accepted prose.

The continuation dispatch blocks the first failure by construction. Optional public history addresses the second without handing the narrator the parent transcript, full source custody, or private sidecars.

## Exact treatment surface

For the strongest treatment:

```bash
./lacuna checkpoint run next-turn CHECKPOINT_RUN \
  --player-input-file NEXT_INPUT \
  --public-history PUBLIC_HISTORY.json \
  --provider PROVIDER \
  --format markdown
```

The resulting worker sees one complete input. It does not need to infer:

- which checkpoint or state card won;
- whether the next text is session control or a play turn;
- which audience/actor/cube/head apply;
- whether planner context or anchor authority should exist;
- how to construct the proposal identity;
- where to save the result; or
- which parent command accepts it.

This should especially reduce protocol failure for weaker coordinators while preserving the same kernel boundary used by ordinary play.

## Public-context policies

The artifact supports two preregisterable conditions.

### Typed-only

Every condition receives the same typed audience projection. This is the narrowest information bottleneck. It requires a strong material-observation policy because narration-only facts are not mechanically reconstructed.

### Bound public history

Every condition receives equivalent exact player-visible text coverage. `history build` audits retained committed turns, records exact text plus parent-side source custody, and authenticates the text digests back to durable cube sources. The continuation sends only `lacuna.public-history-view.v1`: exact ordered `player_input` and accepted `narration`, not run IDs, proposal IDs, receipt hashes, or event positions.

This policy improves fairness of the comparison, but it does not prove that the operator included every turn. A study should preregister the run-list or coverage rule, retain the full parent artifact, and use the same coverage policy in all conditions.

## Why ledger authentication matters

Canonical hashes inside one artifact prove self-consistency, not historical truth. A host can replace prose and recompute every dependent digest. Rev0164 therefore separates:

- `validate_public_history`: strict shape, digest, scope, and chronology self-consistency; from
- `authenticate_public_history`: durable request/input/proposal/narration-source verification against the cube.

A dedicated negative test demonstrates the distinction by constructing a fully rehashed narration forgery that validates internally and then fails ledger authentication. This is useful beyond fiction: research artifacts should not treat rehashing a rewritten report as provenance.

## New mechanical endpoints

Rev0164 makes these outcomes inspectable:

- whether a continuation was opened directly at the accepted checkpoint head;
- whether the ordinary continuation packet was audience-only, solo, play-turn, and no-anchor;
- exact checkpoint/capsule/turn/input/dispatch digests;
- whether optional public history matched cube, audience, canonical content, durable request/narration custody, and ledger order;
- whether the worker received only the least-context prose view;
- whether history ended before checkpoint opening;
- whether invalid or forged history produced no new turn directory;
- whether a stale/different-cube/director/non-solo/session-control turn was refused;
- whether the fresh-narrator return passed the ordinary turn preparation and commit boundary; and
- which provider alias/context requirement the host declared.

## Experimental use

The primary causal comparison remains:

- forward-only persistent context;
- prompt-only retcon persistent context;
- Lacuna serial persistent context;
- Lacuna role-separated fresh checkpoint workers plus fresh continuation narrator.

Rev0164 does not change the scenario condition identities. It makes the final treatment implementation harder to fake accidentally and lets the study preregister public-context parity. Scenario invocation custody can continue to record the exact checkpoint and capsule digest embedded in the continuation dispatch.

## Usability and security hypotheses

H8. A single checkpoint-to-turn dispatch will reduce operator errors relative to “capsule + next input + manually opened turn” instructions, especially for weaker models and human paste bridges.

H9. Bound public history will reduce fresh-narrator continuity errors relative to typed-only operation when earlier material facts were not typed, but may weaken the compression bottleneck by increasing supplied context.

H10. A prose-only worker view will improve schema adherence and narrative focus relative to sending the full audit artifact, especially for weaker narrators.

H11. Durable source authentication will detect transcript substitution that artifact-local hashing alone cannot detect.

These are hypotheses, not findings. The next evidence-bearing step is a live study retaining both protocol failures and narrative ratings.

## Remaining confounds

- The provider may preserve hidden memory despite a declared fresh context.
- A parent may supply extra bytes outside the dispatch.
- Public-history coverage can be incomplete or selectively chosen.
- Same-model workers share weights and correlated preferences.
- The selected state card may be poor even when its custody is exact.
- A longer public history changes context length and may itself improve or degrade output.
- Run IDs and packet/receipt digests remain sidecar custody rather than ledger-authenticated facts.
- Scenario ratings remain human judgments; checkpoint scores are part of the treatment and must not be reused as outcome evidence.

## Recommended pilot refinement

For each shared scenario/checkpoint, branch the accepted cube into:

1. persistent full-context continuation;
2. fresh typed-only dispatch;
3. fresh bound-history dispatch; and
4. fresh transcript-only control without private state card.

Use identical next player inputs. Measure rejected-future canary leakage, public-fact continuity, contradiction rate, agency, seam visibility, context size, latency, schema adherence, and blind preference. Keep mechanical custody outcomes separate from aesthetic ratings.
