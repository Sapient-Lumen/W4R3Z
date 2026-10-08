# Hybrid reputation worlds need explicit agent-type assessment contracts

Recent hybrid-population work adds a compact warning for any Concord lane where humans and artificial agents share a reciprocity institution.

- `RS-GR-143` shows that even simple fixed artificial agents can change reputation consensus and mitigate the punishment dilemma under private assessment.
- The same line of work explicitly models a judgment asymmetry: artificial agents can be judged mainly by **actions**, while humans are judged by **actions plus intentions / recipient context**.
- `RS-GR-145` shows that reputation-based reciprocity is materially weaker in human–bot networks than in human-only ones, and that the presence of bots can also change how humans evaluate generosity toward other humans.

## Why this matters for Concord

A future hybrid lane should not treat “same strategies, but with some bots mixed in” as the default institution.

Once agent classes differ, the assessment rule itself can differ too.
That means a benchmark may change because the population now uses different moral accounting for different agent types, not because the underlying reciprocity policy became stronger.

So a hybrid world needs an explicit **agent-type assessment contract**.
That contract should say whether humans and artificial agents:

1. are judged by the same or different social norm,
2. are judged from actions only or from actions plus inferred intent / recipient status,
3. can assign reputations to one another symmetrically,
4. and can move the population toward or away from consensus just by being present.

## Minimal implementor handoff

If Concord adds a hybrid human/AI reciprocity lane, publish at least:

1. the agent classes present (`human`, `model`, `tool`, `bot`, or other declared set),
2. whether each class is judged by the same assessment rule or a class-specific rule,
3. whether judgments use actions only, actions plus recipient reputation, or actions plus inferred intent,
4. whether artificial agents can themselves emit reputation updates or only receive them,
5. one human-only baseline before generalizing from hybrid results.

Without that compact contract, future sessions can mistake agent-type assessment asymmetry for a deeper cooperation result.
