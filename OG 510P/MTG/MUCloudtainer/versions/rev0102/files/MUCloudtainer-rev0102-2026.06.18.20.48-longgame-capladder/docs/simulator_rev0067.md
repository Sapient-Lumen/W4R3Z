# rev0067 simulator note

rev0067 changes public policy scoring and response-matrix experiment plumbing only.  It does not change game rules, legal-action generation, hidden-information boundaries, replay format, C++ shadow semantics, or terminal scoring.

The new `threat_surge` policy is an audit/control profile, not a promoted solver.  It is useful because it stresses the live `counter_guard` candidate from a different tactical angle: protecting threats in stack fights and forcing safe player-damage closure.

The key simulator-facing audit remains unchanged from rev0066: selected Counterspell/Force actions are checked for target-controller ownership.  rev0067 observed zero selected own-spell counters across 348 audited games.
