## Transfer-cost contract sheet

### Purpose
Make the product say **how bytes will really move and why** before it says `syncs only changed data`, `high priority`, `rename without re-download`, `fast`, or `efficient`.

### The contract object
Each serious movement sentence renders these fields together:

- **Byte-cost class**: metadata-only, piecewise delta, archive-assisted local reuse, whole-file resend, mixed, or unknown.
- **Reuse basis**: remote delta proof, local Archive hash hit, no reuse basis, feature-gated diff-delta lane, or unknown.
- **Splittability class**: splittable, nonsplittable, mixed queue, or unknown.
- **Queue order class**: default order, mtime-priority, size-priority, manually elevated elsewhere, suspended by higher priority, or unknown.
- **Cost witness**: current send/receive evidence, rule-only expectation, post-hoc byte counters, or unknown.
- **Fallback trigger**: piece shift, Archive absent, queue saturation, active-file cap, feature lane missing, or unknown.
- **Efficiency floor**: no honest byte-saving claim, some bytes avoided, full local rename reuse plausible, or unknown.
- **Blocked stronger sentence**: the next stronger efficiency claim the product refuses to make.

### Default language rules
- `higher priority` is intentionally weaker than `less data will move`.
- `same content under a new name` is intentionally weaker than `rename reuse is proven`.
- `delta sync` is intentionally weaker than `piecewise delta on this case`.
- `suspended` is intentionally weaker than `cancelled`.
- `fast` is intentionally weaker than `low byte cost`.

### Required persistent receipts
Any serious movement, performance, or prioritization sentence stores one durable receipt preserving byte-cost class, reuse basis, splittability class, queue order class, fallback trigger, and the blocked stronger sentence.
