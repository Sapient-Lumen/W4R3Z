# Proof obligation — rev0031

Before this design becomes real protocol work, these must be answered:

- Which scopes are stable enough to persist across restart?
- Which obligations are created by each accept-with-watch decision?
- What evidence kinds clear which obligations?
- Which hard-negative evidence is pinned despite byte pressure?
- Which soft evidence should decay fastest under garden capture?

The cube implements toy versions first so tests can punish bad joins before live transport arrives.
