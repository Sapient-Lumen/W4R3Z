# Identity persistence and reputation reset cost are world contracts, not account hygiene

Recent work adds a missing institutional layer for Concord's future reputation and leave/rematch lanes: **reputation only works if bad history sticks long enough to matter**.

- `RS-GR-157` reports that when sellers can erase their rating profile and start over, buyer trust and seller trustworthiness both decrease significantly.
- The paper further reports that trust toward new sellers becomes especially low, because buyers cannot tell truly new entrants from opportunists who just reset after bad behavior.
- `RS-GR-158` adds that whitewashing remains a standard attack class in open trust systems, alongside collusion, ballot stuffing, and on-off attacks.
- That means cheap identity reset is not just an edge case from old online markets. It is a recurring systems problem whenever reputation is attached to a handle more tightly than to a continuing agent.

## Why this matters for Concord

A future benchmark should not treat identity reset as account-management hygiene.

There is a real institutional difference between:
1. durable identity with persistent history;
2. pseudonymous but stable identity;
3. cheap discard-and-reenter identity;
4. resettable identity with probation, newcomer priors, or partial history carryover.

Those worlds do not merely change UX.
They change how much a bad record matters, whether exclusion can be escaped by churn, and whether low trust in newcomers is a rational response or a benchmark artifact.

## Minimal implementor handoff

When Concord adds richer leave/rematch, sanction, or reputation lanes, the world contract should declare:

1. whether an agent can discard identity and re-enter as apparently new;
2. what resetting costs in time, opportunities, stake, or initial trust;
3. whether reputation follows the agent, the handle, neither, or only partially;
4. what newcomer prior or probation rule applies after a reset.

Without that publication layer, future results can mistake whitewashing resistance or newcomer suspicion for moral or strategic superiority.

