# Research — capability audits as first-class release artifacts

A Linux automation project does not become more trustworthy by hiding capability boundaries behind one generic compatibility badge. The repo already had the right ingredients — session probing, host contracts, readiness checks, and activation fallbacks — but not one explicit artifact that told the truth in one place.

This pass turns that into a product/release surface: one audit that can say which capabilities are blocked, which are degraded, which helpers are part of the install story, and which fallback route should stay visible in docs when the hotter path is not broadly reliable.

That aligns with the practical lesson behind the rest of VHK's Linux-native direction: portable runner semantics are valuable, but desktop/session/helper boundaries still have to be made explicit and reviewable.
