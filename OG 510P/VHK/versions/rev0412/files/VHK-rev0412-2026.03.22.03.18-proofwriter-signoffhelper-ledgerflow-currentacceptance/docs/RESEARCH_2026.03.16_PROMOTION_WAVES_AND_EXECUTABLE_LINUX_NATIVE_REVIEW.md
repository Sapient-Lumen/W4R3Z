# Research note — promotion waves and executable Linux-native review

## Core lesson from adjacent Linux tools

The strongest current Linux automation tools still split into distinct product tiers instead of pretending one runtime owns everything:

- text expansion / snippet packaging
- low-latency remapping
- helper/session-bound trigger or capture lanes
- rich runtime orchestration for the flows that truly need it

That is why VHK's promotion work now benefits from staged waves rather than one flat backlog.

## Why promotion waves are useful

A flat promotion list hides two different kinds of work:

1. **specialist exports that are ready to become first-class product surfaces**
2. **helper-sensitive or conditional routes that still need explicit contracts/fallbacks**

VHK should not treat those as equivalent. A text package or remapper export often wants immediate promotion, while helper-boundary flows usually want dossier/review discipline first.

## Repo implication

The planner now emits `promotion_waves`, and `gen-promotion-pack` turns them into docs/JSON/refresh scripts so this research changes repo behavior instead of staying stranded in markdown.
