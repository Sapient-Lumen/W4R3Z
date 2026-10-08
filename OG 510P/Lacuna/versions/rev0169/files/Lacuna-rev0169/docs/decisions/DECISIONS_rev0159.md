# Decisions — rev0159

## D159-01 — Give checkpoints a typed request purpose

**Decision.** Advance new issuance to request v4/source protocol v3/grant v2 and distinguish purpose `checkpoint` from purpose `play`.

**Reason.** A backstage comparison and an in-fiction turn can both begin from session-control prose, but they have different authorities, outputs, and visibility.

**Consequence.** Purpose is fixed at source issuance. Historical v2/v3 requests remain playable without rewrite.

## D159-02 — Keep checkpoint policy outside story truth but inside exact custody

**Decision.** Freeze candidate count, rollout horizon, rubric, weights, tie rule, compression budget, operation budget, and protected state in the checkpoint request.

**Reason.** Model policy is external, but an experiment is not reproducible if each worker silently receives a different policy.

**Consequence.** Lacuna validates conformance to the declared policy without claiming the policy is aesthetically correct.

## D159-03 — Require exact rollout beats rather than claimed summaries or optional hashes

**Decision.** Every candidate carries exactly one explicit ordered beat per declared horizon turn plus a summary.

**Reason.** A summary and optional body digest permit a generator to claim that forward simulation occurred without supplying the work that the judge must inspect.

**Consequence.** Candidate artifacts are larger and more sensitive, but rollout existence and cardinality are mechanically checkable. Beats remain noncanon.

## D159-04 — Preallocate cardinality in model output templates

**Decision.** Generator and judge templates contain the exact number of candidate/score objects and exact number of rollout beats.

**Reason.** Less capable models should not infer array cardinality from prose or repair it after the fact.

**Consequence.** Policy changes regenerate a complete concrete template. Missing, extra, duplicate, or relabelled entries refuse.

## D159-05 — Blind declared provenance, not candidate substance

**Decision.** Remove generator provider/model/invocation labels and notes from the judge card while retaining candidate content and exact rollouts.

**Reason.** The judge needs the substance to compare futures, but declared identity is an avoidable bias channel.

**Consequence.** The release calls this provenance-blind, never anonymous or independent; semantic fingerprints and provider memory remain possible.

## D159-06 — Make selection deterministic after authored scores

**Decision.** Use fixed dimensions, integer weights summing to 100, exact arithmetic, declared disqualifiers, and highest-eligible score with lexical candidate-ID tie-breaking.

**Reason.** Aesthetic judgment cannot be made objective, but artifact custody can make the declared decision reproducible.

**Consequence.** Parent validation rejects score drift or winner substitution. Scores must not be relabelled as probabilities or particle likelihoods.

## D159-07 — Give the compressor only the winner

**Decision.** Withhold rejected candidates and generator provenance from the compression card.

**Reason.** The world-state bottleneck should prevent rejected futures from leaking into downstream active context and reduce post-selection rationalization.

**Consequence.** Exact rejected artifacts remain privately auditable but are not copied into the proposal or ordinary turn context.

## D159-08 — Narrow checkpoint mutation authority

**Decision.** Use a dedicated checkpoint grant and operation allowlist rather than a normal unscoped director grant.

**Reason.** Selecting a preferred explanation is not authority to anchor it, harden it, manipulate particle weights, or operate secret custody.

**Consequence.** Assembly and the kernel reject operations outside the checkpoint surface even if a worker’s prose requests them.

## D159-09 — Keep assembly and full selection verification with the parent

**Decision.** Workers return artifacts only. The parent validates the complete candidate → judgment → compression chain and constructs the proposal.

**Reason.** Letting a worker choose its own inputs, winner, or custody digests would collapse the intended separation.

**Consequence.** Provider aliases never confer parent power. A serial fallback may reuse one model context but retains the same artifact boundaries.

## D159-10 — Scope the verifier to what it can actually see

**Decision.** The verifier checks proposal-visible custody consistency and anti-rubber-reality hazards; it does not claim to recompute raw winner selection.

**Reason.** Its least-context card intentionally omits raw rejected candidates and scores.

**Consequence.** Parent assembly owns complete deterministic selection revalidation. Verifier `pass` remains advisory.

## D159-11 — Recompute dispatch exactly from the embedded card

**Decision.** Validate checkpoint dispatch by rebuilding the entire envelope from the card and provider route.

**Reason.** Schema shape alone would permit a correct card paired with a changed role alias, return path, or parent command.

**Consequence.** Any envelope drift refuses. Dispatch still does not attest invocation.

## D159-12 — Centralize provider aliases

**Decision.** Put ordinary-turn and checkpoint role mappings in one provider registry.

**Reason.** Entrance briefs, run dispatch, checkpoint dispatch, and checked-in provider files otherwise risk inconsistent names.

**Consequence.** Provider-specific files remain thin discovery adapters; the generated card remains the exact task contract.

## D159-13 — Reuse exact kernel preparation and historical recovery

**Decision.** Checkpoints assemble an ordinary turn proposal and use the existing rollback preparation, replay, and historical recovery path.

**Reason.** A new commit engine would duplicate the highest-risk authority boundary and could weaken rev0157/rev0158 guarantees.

**Consequence.** Checkpoint commits receive the same stale-head, event-chain, projection, and no-duplicate guarantees as governed turns.

## D159-14 — Preserve exact artifacts privately; “forget” by omission

**Decision.** Keep candidate/judgment/compression artifacts outside the event ledger and omit rejected futures from downstream cards.

**Reason.** Destructive deletion would undermine audit, while repeatedly feeding rejected rollouts forward defeats the intended bottleneck.

**Consequence.** Retention, confidentiality, and eventual deletion are explicit host policy. Lacuna does not claim cryptographic erasure.

## D159-15 — Make the next milestone empirical, not broader authority

**Decision.** Prioritize matched scenario capsules and invocation custody over automatic checkpoint triggers or more worker powers.

**Reason.** The checkpoint exchange is now runnable; the open question is whether it improves outcomes and which topology is worth its cost.

**Consequence.** Rev0159 reports no comparative result and treats live provider conformance as future work.
