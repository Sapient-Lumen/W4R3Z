# Rematch worlds should publish sanction and restoration graphs as a world contract

In rematch or repeated-interaction worlds with explicit enforcement, outcomes depend not only on payoff structure and monitoring but also on **what legal states exist**, **what evidence triggers a transition**, and **what sanctions or restorative paths follow**.
If those pieces are left implicit, an inheritor can mistake a change in governance plumbing for a change in reciprocity itself.

Recent external work makes this explicit in a nearby setting.
`RS-GR-043` treats the governance layer as a public manifest of legal states, transitions, sanctions, and restorative paths rather than as a hidden runtime convention.
For Concord, the compact lesson is that once the institution can move agents between states or impose consequences, those transition rules belong to the world contract.

## Minimum contract

If a rematch or benchmark world enforces norms through sanctions, suspensions, throttles, or equivalent controller-mediated transitions, publish at least:

1. the **legal states** the world recognizes,
2. the **evidence predicates** that trigger state transitions,
3. the **sanctions / costs** attached to each transition,
4. the **restoration path** back to ordinary play,
5. the **timing / persistence rule** for sanctions and restoration,
6. and the **audit-log commitment** that records which evidence caused which transition.

## Implementor consequence

Do not compare two rematch worlds as if they share one institution when one changes suspension timing, restoration conditions, or sanction severity.
That is a world-contract change, not merely a policy-quality delta.

## Archive consequence

Keep this compact.
When a benchmark lane adds enforcement, prefer one retained governance-contract note or receipt field over another bulky sanctions report pair.
