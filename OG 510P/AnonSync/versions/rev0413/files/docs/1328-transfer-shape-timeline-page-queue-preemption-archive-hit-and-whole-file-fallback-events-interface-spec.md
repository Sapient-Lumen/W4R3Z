## Transfer-shape timeline page

Render the operator-visible history as movement-shape events, not just generic progress.

### Event classes
- file entered queue
- queue priority changed
- lower-priority transfer suspended
- piecewise delta lane selected
- whole-file fallback triggered
- Archive hash hit found
- rename reuse completed
- queue rebuilt
- active-file ceiling blocked entry
- stronger efficiency claim revoked

### Timeline rules
- queue events and byte-cost events must remain separate
- Archive-hit events stay visibly separate from remote delta events
- splittability ceiling stays visible whenever strict priority cannot be promised
- the first event that forced whole-file fallback must remain easy to read later
