# Reputation scope must say whether failures attach to agents, families, or all AIs

Recent human–AI interaction work adds a compact warning for any Concord world that allows reputation spillover across agent types.

- `RS-GR-144` reports a double standard in which one AI's moral transgression can spill over to perceptions of **all AIs**, whereas analogous spillover can disappear in the comparable human case.
- `RS-GR-145` reports that in human–bot reciprocity settings, people can become less generous not only toward bots but also toward humans who help bots.

## Why this matters for Concord

A future reputation lane should not assume that reputations live only on individual agents.

In hybrid settings, a failure can attach at several different scopes:

1. the single agent,
2. the agent's model family,
3. the provider or institution behind that agent,
4. or the whole category "AI".

Those are different institutions.
A world where one bad bot hurts only that bot is not the same as a world where one bad bot poisons trust in every bot.
Likewise, a world where helping bots harms a human's reputation is not the same as one where cross-type help is morally neutral.

So **reputation scope** belongs in the world contract.
It should be published explicitly rather than smuggled in through participant intuitions or UI framing.

## Minimal implementor handoff

If Concord adds a hybrid reputation lane, publish at least:

1. the scope at which reputational updates apply (individual, family, provider, or all-AI category),
2. whether spillover can cross from one agent to another without direct interaction,
3. whether helping an outgroup or machine alter changes the helper's reputation differently than helping a human,
4. whether negative and positive spillovers use the same scope,
5. one no-class-spillover baseline before generalizing from hybrid reputation results.

Without that compact contract, future sessions can mistake category-level stigma or halo effects for stable reciprocity.
