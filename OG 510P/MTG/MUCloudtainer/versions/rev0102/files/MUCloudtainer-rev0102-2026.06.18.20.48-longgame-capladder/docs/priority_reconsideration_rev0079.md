# rev0079 priority reconsideration

The next riskiest item was not more games. The current conclusion already says `public_counter_guard` should not be promoted. The risk was that the machinery could later promote a different candidate from an attractive global row while size or life strata remained imprecise.

Priority therefore shifted to a mandatory hierarchy around the familywise gate:

1. Global broad-pool familywise gate.
2. By-life familywise gates.
3. By-size familywise gates.
4. Fine size/life diagnostics, retained as underpowered until enough evidence exists.

The other at-risk item was solver drift when the policy population expands from two counter policies to three or more. rev0079 adds exact support enumeration for small rectangular games so future expansion does not immediately fall back to approximate fictitious play.

Next substantive priorities:

1. Add new non-adaptive complete panels only if they are designed to lift the by-size precision blockers.
2. Keep adaptive challenge evidence outside broad pools unless it is explicitly labelled and analyzed separately.
3. Treat any global-only promotion as invalid unless mandatory hierarchical layers also pass.
