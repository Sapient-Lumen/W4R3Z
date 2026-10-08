# Research notes — promotion readiness and Linux constraint matrix

This pass focused on a practical gap in the planner.

The repo could already answer:

- what kind of macro is this?
- which Linux-native lane does it resemble?
- which export surface should the project promote next?

But it still could not answer the more operational question:

- is that promotion actually ready to ship on this Linux posture?

## Product lessons reinforced

### 1. Text automation remains its own lane

Text automation is not just "fake typing faster". Linux-native tools keep showing that snippets/forms/packages/lifecycle matter. That means VHK should continue treating text-tier promotion as a real product surface.

### 2. Remappers and runners should not be collapsed

Low-latency remappers succeed by staying thin, while the richer runtime keeps prompts, waits, diagnostics, and orchestration. VHK should keep learning from that split instead of hiding it behind a single automation abstraction.

### 3. Wayland helper boundaries still need honesty

Portals, helper daemons, virtual keyboard routes, and compositor-specific shortcut handoffs are useful, but they do not erase desktop variance. Promotion work needs a readiness posture so VHK can say "review" or "blocked" instead of overclaiming parity.

## Resulting repo change

The planner now emits `promotion_readiness` and `promotion_readiness_summary`, and the promotion pack renders that posture into review docs. This keeps Linux-native planning grounded in real route ownership plus real shipping readiness.
