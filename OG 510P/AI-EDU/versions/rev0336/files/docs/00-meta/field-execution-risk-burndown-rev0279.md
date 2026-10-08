# Field execution risk burndown rev0279

## Burned down in this pass

| Risk | Rev0279 response | Status |
|---|---|---|
| Live queue points at an obsolete gate | Refreshed `FT-0181` to the current live-window/readout route | Reduced |
| Generated context repeats stale live work | Regenerated `context-pack.json` from the corrected queue | Reduced |
| Future active followthrough can drift silently | Extended `check_followthrough_receipt.py` to require current-revision live text and an existing current next surface | Reduced |
| Registry labels carry stale rev0276 purpose text | Updated registry IDs/purposes to rev0279 mission/waste repair posture | Reduced |
| Control work becomes a proxy for field work | Added mission/waste audit with a compression-first operating rule | Watch |

## Still live

| Risk | Why it remains | Next practical move |
|---|---|---|
| No real owner packet exists | External contact has not happened inside the archive | Send/adapt packet, record send log, then status clock |
| Live-window card cannot authorize closure | It only records controls for a bounded window | Use the bounded end-of-window readout gate after terminal card state |
| Public claims could creep after a clean window | Public language lives outside the local card artifact | Keep the public claim lexicon and readout claim-family effects active |
| Control-plane sprawl drains attention | 100 branch surfaces and 67 lint tools can feel like progress without evidence | Freeze new branches; compress or summarize stale families only after preserving index memory |
| Evidence/security pressure is increasing externally | AI data provenance, model drift, and education high-risk rules are becoming more salient | Keep provenance/security gates, but do not add fields until a real packet exposes a gap |

## Do not compensate with bureaucracy

Do not add a branch, schema field, or registry row unless a real packet or a broken
local artifact shows the current router, contact, intake, seed, review, decision,
ticket, live-window card, readout, or closure path cannot represent the problem.
Prefer deleting, compressing, or refreshing stale surfaces over inventing new
ones.
