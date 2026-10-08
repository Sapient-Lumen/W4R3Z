# Research — rev0163

## Research question

Can Lacuna test the information-bottleneck claim in retcon planning without letting a long-lived continuing narrator remember the very rejected futures that compression is supposed to remove?

## Result in this revision

Operationally, yes—subject to host-declaration limits.

Rev0160 separated checkpoint roles and made their artifacts exact. Rev0161–rev0162 added serial/separated conditions and preregistered replication. Rev0163 identifies the missing treatment boundary: the narrator after the checkpoint. It now compiles one exact winner-only continuation capsule and requires a new capsule-bound narrator in the separated condition, while controls intentionally retain one context.

This makes the intended intervention falsifiable. It still does not prove that a provider created a fresh context, forgot hidden state, obeyed the handoff, or produced better fiction.

## Why the old separated condition was confounded

A parent or narrator operating in one long conversation may have seen:

- all generated candidates and detailed rollout beats;
- rejected futures;
- score dimensions and judge rationale;
- verifier concerns;
- experiment instructions and desired behavior; and
- the complete pre-checkpoint transcript.

Giving four checkpoint stages different labels or even different workers does not remove that information from the narrator that writes the next turn. A large context can improve continuity while making causal attribution to the compressed state card impossible.

## The rev0163 intervention

After exact checkpoint commit, the parent compiles `lacuna.checkpoint-narrator-capsule.v1`. The capsule contains accepted public custody and selected compact planning guidance and excludes raw search/evaluation history by construction.

The clean host procedure is:

1. use bounded fresh contexts for generator, judge, compressor, and verifier;
2. commit through the long-lived parent;
3. retain the exact capsule bytes and digest;
4. create a new narrator context with no checkpoint sidecar/filesystem access;
5. supply only the capsule plus the next exact player input; and
6. route the proposed continuation through a new ordinary Lacuna turn.

The parent is allowed to remember because it is the accountable coordinator, not the creative continuation treatment. The experiment fails only when the narrator receives more context than its condition permits or the parent injects rejected material into later prompts.

## Sharpened four-condition comparison

| Condition | Context intervention |
|---|---|
| forward-only | one persistent narrator/context; no checkpoint |
| prompt-only-retcon | one persistent context performs monolithic retcon and continuation |
| Lacuna serial | one persistent context executes all managed roles and continuation |
| Lacuna role-separated | four fresh checkpoint contexts plus a new capsule-bound narrator segment after every checkpoint |

This is now a stronger ablation than “one model versus many.” It compares persistent full-history continuation with manufactured context asymmetry and an actual post-checkpoint bottleneck.

## Observable-treatment requirement

A checkpoint must be followed by at least one scripted ordinary turn. The previous one-step default could run a checkpoint after the final narration, leaving no player-visible outcome generated from the compressed state. That measured machinery rather than continuation. Rev0163 refuses such capsules and creates a two-step default.

## Mechanical outcomes now available

- exact capsule identity and source artifact digests;
- state-card and post-commit audience-context continuity;
- absence of raw candidate/judgment/verifier fields from the capsule contract;
- persistent versus fresh continuation mode per condition;
- context reuse/refusal within and across narrator segments;
- managed checkpoint identity per checkpoint group;
- exact capsule/checkpoint linkage on the first subsequent turn;
- checkpoint-before-next-turn ordering;
- refusal of unobservable final-step checkpoints;
- all existing scenario/bundle, commitment, consequence, unknown, verification, cost, failure, rating, sealing, and delayed-unblinding measures.

## Measurements still external

- whether a provider actually created an isolated fresh context;
- whether hidden account, project, tool, filesystem, or model state leaked;
- exact bytes delivered by a human or provider transport unless separately logged;
- candidate quality, missing modes, rollout faithfulness, and compression sufficiency;
- semantic leakage that does not reproduce a planted canary;
- narrative coherence, agency, payoff, fairness, delight, and desire to continue;
- rater masking, independence, calibration, and inferential statistics.

## Falsification pressure

A live study should retain:

- exact role dispatches and capsule bytes;
- provider conversation/thread/request identifiers;
- memory, project, Custom Instructions, tool, and filesystem settings;
- random rejected-candidate, judge-only, parent-only, and unrelated-file canaries;
- all failed calls under a preregistered retry policy;
- transcript-only blind ratings and method-guess/masking checks; and
- null, negative, refused, and failed cells.

Canary appearance is strong evidence of contamination. Canary absence is not proof of isolation.

## Hypotheses, not findings

H1. Fresh capsule-bound continuation reduces exact rejected-future leakage relative to persistent-context Lacuna serial execution.

H2. The fresh narrator condition improves seam invisibility and reduces teleological overfitting when the compact state card is sufficient.

H3. The same bottleneck can hurt local detail continuity when material public facts were never typed or included in the capsule.

H4. Role separation without narrator reset yields smaller effects than the complete fresh-narrator treatment.

H5. Persistent-context controls may produce fluent stories while showing more rollout imitation and experiment-demand behavior.

H6. The stricter treatment increases coordination failures, latency, and cost; these are part of the method outcome rather than ignorable missing data.

None is established by this release.

## Public-context parity

A clean reset is not automatically a fair reset. Lacuna's audience projection contains typed public custody, while narration-only continuity may remain solely in the external transcript. The study must preregister either a typed-canon policy or an identical digest-bound player-visible history supplied across all conditions. Supplying less observed canon only to the fresh-narrator arm would confound forgetting with information loss.

## Immediate next experiment

Run one preregistered two-checkpoint, six-to-ten-turn mystery/departure capsule under all four conditions using the same model family and budget. Put one random canary in a rejected rollout, one in judge-only rationale, and one in a parent-only note. Require fresh API calls or demonstrably new subagent/chat contexts for the separated condition, retain the exact capsule digests, and rate the player-visible transcripts blind. Report custody outcomes, leakage, failures, cost, and human ratings separately.
