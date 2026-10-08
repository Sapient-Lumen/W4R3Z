# rev0184 — zone replacement priority-tier seal

rev0184 targets the next risky rule-616 gap after the rev0183 chain validator: replacement rows could prove that a repeated event chain was contiguous, but they still did not prove that the chosen replacement came from the earliest applicable CR 616 priority tier.

The executable scaffold now exposes `ReplacementPriorityTier` on `ZoneChangeReplacementDefinition`:

1. `SelfReplacement`
2. `ControlEntering`
3. `CopyEntering`
4. `BackFaceEntering`
5. `General`

For the supported zone-change replacement slice, candidate collection records every applicable candidate, then selection first chooses the minimum available priority tier. Only candidates in that tier participate in the deterministic `choice_rank` fallback. This keeps the current non-interactive affected-player choice scaffold, but prevents an ordinary high-rank replacement from skipping a self-replacement/control/copy/back-face tier when that tier is represented.

`ZoneChangeReplacementRecord` now carries three audit fields:

- `priority_tier`: the chosen replacement definition's tier;
- `candidate_min_priority_tier`: the earliest applicable tier seen in the pass;
- `eligible_candidate_count`: the number of candidates in that earliest tier.

Validation rejects stale or fabricated rows with `zone_replacement_record.priority_tier_skip`, `zone_replacement_record.zero_eligible_candidates`, and `zone_replacement_record.eligible_candidates_exceed_candidates`. The older `chosen_among_multiple` flag is now bound to same-tier eligible candidates rather than all lower-tier candidates, which matches the supported tier-first selection model.

The focused regression is `test_zone_change_replacement_priority_tier_forces_eligible_choice`: it places a high-rank general exile replacement beside a lower-rank self-tier command replacement. The bear goes to command, the typed record preserves both total and eligible candidate counts, and copied-state corruption proves the validator catches a skipped tier and malformed eligible counts.

This is still not the full rule-616 engine. It does not yet implement interactive choice prompts, APNAP batching for simultaneous event sets, enters-the-battlefield object-shaping replacements, or automatic tier inference from Oracle text. The useful forward motion is that the highest-risk tier-ordering part of the supported replacement chain is now executable and auditable instead of documented as a future caveat.
