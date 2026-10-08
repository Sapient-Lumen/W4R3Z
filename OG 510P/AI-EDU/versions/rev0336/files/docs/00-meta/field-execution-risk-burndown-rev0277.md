# Field execution risk burndown rev0277

## Burned down in this pass

| Risk | Rev0277 response | Status |
|---|---|---|
| First-packet decision falls into prose-only change-ticket work | Added `owner-post-decision-change-ticket` recorder and router route | Reduced |
| Change ticket copies decision prose or owner details | Recorder and guard store only change classes, counts, hashes, and routes | Reduced |
| Change ticket becomes service authorization or acceptance | Guard requires `NOT_ACCEPTED`, `not_evidence`, no custody, no closure, no public-claim effect, and live-window-only routing | Reduced |
| Active change starts without stop/rollback boundary | Guard blocks `active_change` and bounded pilot classes unless `live_window_required=true` | Reduced |
| Pilot pressure outruns source truth | Guard requires `SRC2`/`SRC3`/`SRC4` source truth requirement for `PCT-D-bounded-pilot` | Reduced |

## Still live

| Risk | Why it remains | Next practical move |
|---|---|---|
| No real owner packet exists | External contact has not happened inside the archive | Send/adapt packet, record send log, then status clock |
| Post-decision ticket cannot authorize live use | It only records change class and boundaries | Add bounded live-window stop/rollback-card recorder |
| Public claims could still creep after ticketing | Public language is outside the local ticket artifact | Keep public claim lexicon and live-window freeze active |
| Closure pressure remains | `FT-0181` is live and the archive is ready-but-not-closed | Require acceptance, live window, readout, closeout, and signoff before closure |

## Do not compensate with bureaucracy

Do not add a branch, schema field, or registry row unless a real packet or a broken local artifact shows the current router, contact, intake, seed, review, decision-board, change-ticket, live-window, or closure path cannot represent the problem.
