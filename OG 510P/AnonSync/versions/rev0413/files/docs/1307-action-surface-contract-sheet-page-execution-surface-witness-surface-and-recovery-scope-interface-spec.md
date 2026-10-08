## Action-surface contract sheet

### Purpose
Make the product say **where an action can actually be executed, witnessed, and recovered** before it says `available`, `open`, `restore`, `share`, or `supported`.

### The contract object
Each serious action-bearing subject renders these fields together:

- **Requested verb family**: restore, inspect, change settings, share, hydrate, clear local bytes, recover control, update, or another typed action.
- **Execution surface**: desktop app, WebUI, mobile app, file browser / shell, config file, service manager, browser handoff, or unknown.
- **Witness surface**: where success or failure can actually be seen with adequate evidence.
- **Recovery surface**: where the strongest honest remediation still lives.
- **Surface locality class**: here, elsewhere in-product, outside-product, or absent.
- **Runtime / platform basis**: desktop interactive, Linux/NAS WebUI-only, Windows service, Android, iOS, or mixed / unknown.
- **Blocking basis**: platform restriction, surface omission, runtime class, permissions, browser/OS handoff, or unknown.
- **Fallback class**: semantically equivalent here, weaker elsewhere, out-of-band filesystem action, or no truthful fallback.
- **Semantic loss boundary**: what truth is lost when the operator takes the fallback.
- **Blocked stronger sentence**: the next stronger statement the product refuses to make.

### Default language rules
- `feature exists` is intentionally weaker than `this surface can execute it now`.
- `can open` is intentionally weaker than `can review and restore safely from here`.
- `available elsewhere` is intentionally weaker than `same semantic lane`.
- `visible here` is intentionally weaker than `recoverable here`.
- `browser fallback` is intentionally weaker than `same reviewed action continued`.

### Required persistent receipts
Any serious action request, failed affordance, surface handoff, or out-of-band recovery stores one durable receipt preserving requested verb family, execution surface, witness surface, recovery surface, fallback class, semantic loss boundary, and the blocked stronger sentence.
