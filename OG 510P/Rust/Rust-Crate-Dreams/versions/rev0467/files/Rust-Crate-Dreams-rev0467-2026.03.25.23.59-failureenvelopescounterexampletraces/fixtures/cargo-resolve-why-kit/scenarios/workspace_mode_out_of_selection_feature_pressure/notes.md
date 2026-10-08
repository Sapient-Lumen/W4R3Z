# Scenario: workspace mode allows out-of-selection feature pressure

The command subject is one package, but resolver feature-unification mode is `workspace`, so another workspace member still contributes feature pressure.

Why this matters: a receiver-facing resolver bundle should preserve the difference between selected packages and participating packages instead of pretending the subject alone authored the effective feature state.
