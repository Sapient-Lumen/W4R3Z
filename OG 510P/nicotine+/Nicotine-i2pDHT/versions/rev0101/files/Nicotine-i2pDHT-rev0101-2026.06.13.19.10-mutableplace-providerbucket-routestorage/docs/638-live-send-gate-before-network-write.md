# Live-send gate before network write

The live-send gate is the final local no-network permission before a future implementation might attempt an outbound public-edge write.

It joins canary readiness, settlement-store terminality, tomb-repair coverage, optional side-effect journal state, optional outbox-drain state, endpoint/session/Destination binding, family/path diversity, and public payload budget.

Watchful retry canaries are deliberately held.  A retry-ready canary can prepare future work, but it cannot become a terminal live send.
