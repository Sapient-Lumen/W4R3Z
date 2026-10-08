# Cooperation benchmarks should publish role assignment and side-switch policy

In many cooperation tasks, the two sides are not scientifically interchangeable.
One side may initiate, plan, delegate, verify, explain, observe different state, or bear different responsibility.
Even when the payoff headline looks symmetric, the **interaction role** can still change trust, expectations, and the path to coordination.

The recent human-AI literature makes the same point from two directions:

- `RS-GR-071` shows that humans apply different cooperative norms to AI depending on the relationship type (for example teammate vs boss/employee), so role context changes what “good cooperation” even means.
- `RS-GR-072` shows that changing the human-LLM interaction archetype and role assignment can change outputs and decision outcomes, so apparent performance gains may come from the chosen role split rather than from a generally better collaborator.

So a cooperation benchmark should publish, at minimum:

1. the available **roles / seats** in the task,
2. the **assignment rule** (fixed seat, random seat, alternating seat, balanced block design, or equivalent),
3. whether the reported score is pooled across seats or is **seat-conditional**,
4. whether a **side-swapped companion lane** was run when roles are asymmetric,
5. whether any role carries different observation rights, communication rights, veto rights, or final-action authority,
6. and the pooling / comparison rule used when seat-specific performance differs.

Without that card row, a benchmark can silently promote a **seat artifact** into a cooperation claim.
A system can look patient, fair, or highly helpful only because it was always evaluated in the easier or more trusted role.

This is distinct from counterpart class.
Two lanes can use the same human or model partner class but still differ materially because one evaluates the system as planner, supervisor, explainer, or subordinate while the other does not.

One benchmark-card row is enough: role taxonomy, assignment rule, seat pooling rule, and whether a side-swapped companion lane exists.
Keep the retained object tiny, but do not hide role asymmetry inside the benchmark plumbing.
