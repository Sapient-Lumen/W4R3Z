# Answer-packet obligation audit and runtime refactor — rev0321

Rev0321 works on the next riskiest unfinished layer after route coverage. Rev0320 proved that every current route can be recovered by golden-case facts. The remaining danger was that `tools/answer_case.py` could still become a thin candidate-ID wrapper: useful for routing, but not yet a real handoff toward an answer.

## Priority changes made

1. Refactored `tools/answer_case.py` around a reusable `AnswerRuntime` that loads the cube, source table, remedy profiles, policy-action profiles, actor-accountability profiles, and prepared route text once per invocation.
2. Replaced the thin answer skeleton with a profile-backed answer packet. Each selected candidate now carries routing evidence, precedence label, policy-action duties, accountable actors, remedy moves, guardrails, source IDs, source-currentness claims, review triggers, blocked shortcuts, must-not-answer warnings, and explicit unknowns.
3. Added `tools/audit_answer_skeletons.py`. The audit invokes the answer emitter over all active golden cases and compares emitted packets to the existing contracts without letting the emitter read those contracts.
4. Wired the answer audit into `tools/run_semantic_audits.py`, so `make package` now blocks answer-emission regressions as part of the semantic suite.
5. Kept the change substantive rather than bureaucratic: no new policy registry was added. The new surface is an executable audit and a richer runtime output packet derived from existing live profiles.

## Runtime result

- Answer runtime status: `profile_backed_answer_packet_emitted`
- Answer packets: 122
- Route limit: 5
- Expected route obligations recovered in answer packets: 166/166
- Candidate misses: 0
- Must-not-answer warnings carried forward: 241/241
- Blocked-shortcut obligations carried forward: 1220/1220
- Profile obligations carried forward: 1830/1830
- Source obligations carried forward: 7663/7663
- Currentness obligations carried forward: 295/295
- Complete answer-step packets: 122/122
- Complete source packets: 122/122
- Complete profile packets: 122/122

## What this catches now

The archive now fails release if an answer packet:

- drops an expected route from the top-5 answer candidates,
- omits a golden-case must-not-answer warning,
- fails to expose a selected route's blocked remedy move or policy category error,
- loses the route's default remedy, policy-action family, or primary accountable actor,
- cites a source ID that is not in `SOURCES.json`,
- fails to include selected-route primary sources in the source packet,
- loses a route-level source-currentness claim, or
- removes one of the five minimum answer steps.

## Refactor target

The refactor target was answer emission itself. Before this pass, the answer emitter loaded profile JSON repeatedly and returned a shallow skeleton. After this pass, one runtime context produces profile-backed packets and the audit proves the packet has not collapsed back into decorative routing output.

## Remaining riskiest gap

The next high-risk boundary is still final answer quality. The cube now emits checked answer packets, but it does not yet resolve conflicts among co-equal routes, generate jurisdiction-specific current-law citations, estimate revenue or incidence quantitatively, or produce a final user-facing advisory answer. The next revision should either add a precedence resolver over the emitted packets or attach a small quantitative-estimate interface for the most important fiscal routes.
