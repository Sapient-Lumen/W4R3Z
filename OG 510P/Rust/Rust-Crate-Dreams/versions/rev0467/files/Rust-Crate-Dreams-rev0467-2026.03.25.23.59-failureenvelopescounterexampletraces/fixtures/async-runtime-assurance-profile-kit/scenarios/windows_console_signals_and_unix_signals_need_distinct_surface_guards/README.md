# Scenario — Windows console signals and Unix signals need distinct surface guards

This scenario exists to stop support claims from hiding behind one vague word: “signals”.

Tokio’s docs split these surfaces by platform and feature gate.
The report therefore records explicit guards instead of letting one demo or one module mention stand in for whole-project signal support.
