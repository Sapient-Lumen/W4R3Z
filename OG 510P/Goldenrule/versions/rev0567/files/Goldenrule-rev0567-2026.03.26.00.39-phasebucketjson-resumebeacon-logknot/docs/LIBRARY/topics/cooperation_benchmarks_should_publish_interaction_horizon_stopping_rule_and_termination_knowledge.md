# Cooperation benchmarks should publish interaction horizon, stopping rule, and termination knowledge

Cooperation results are not only about the policy, partner, language, or communication lane.
They also depend on **how long interaction can last**, **how termination happens**, and **what participants or agents know about that stopping rule while they play**.
Three standing sources now support a compact archive rule:

- `RS-GR-055` studies human–AI cooperation in an **indefinitely repeated** Prisoner's Dilemma, making clear that benchmark conclusions can rest on a supergame-style horizon rather than a fixed finite script.
- `RS-GR-061` reports that cooperation is more likely in indefinite games with a longer expected horizon, and that **indefiniteness itself** matters rather than raw length alone.
- `RS-GR-062` shows that the **realized length** of early matches in indefinitely repeated games can materially affect cooperation in later matches.

## Minimum contract

Whenever a cooperation benchmark uses repeated interaction, publish:

1. whether the lane is **one-shot**, **fixed finite horizon**, **indefinite / continuation-probability**, or another stopping regime;
2. the exact **round cap, continuation probability, or termination distribution**;
3. whether the stopping rule is **common knowledge**, partially hidden, or only bounded by a known upper limit;
4. whether the realized horizon is **drawn once per match**, evolves period by period, or depends on endogenous events;
5. whether headline results are pooled across **different horizon regimes**, **different realized match lengths**, or **different match indices**;
6. and any **belief / comprehension protocol** around the stopping rule when humans are involved.

## Implementor consequence

Do not compare or pool cooperation scores across studies if the interaction horizon or stopping-rule knowledge differs.
A policy can look more or less cooperative partly because the benchmark changed the shadow of the future, the realized match lengths people experienced, or what they believed about when interaction might end.

## Archive consequence

Keep the retained object tiny.
One benchmark-card row is enough: horizon regime, stopping-rule parameters, and participant knowledge of termination.
That prevents future sessions from laundering a horizon artifact into a policy-generalization claim.
