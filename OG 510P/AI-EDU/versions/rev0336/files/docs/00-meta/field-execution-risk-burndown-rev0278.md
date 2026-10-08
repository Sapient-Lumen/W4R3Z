# Field execution risk burndown rev0278

## Burned down in this pass

| Risk | Rev0278 response | Status |
|---|---|---|
| Change ticket falls into prose-only live-window work | Added `owner-live-window-card` recorder and router route | Reduced |
| Live-window card copies ticket prose or owner details | Recorder and guard store only window state, counts, hashes, controls, and routes | Reduced |
| Ticket becomes live-service authorization | Guard requires a separate card with source-ticket validation, no-expansion, human-pause, and fallback confirmations | Reduced |
| Live window outruns source truth | Live/staged cards require `SRC2`/`SRC3`/`SRC4` on the card and source ticket | Reduced |
| Card becomes readout, service mutation, or closure | Guard requires `NOT_ACCEPTED`, `not_evidence`, no custody, no closure, no public-claim effect, and readout-only routing | Reduced |

## Still live

| Risk | Why it remains | Next practical move |
|---|---|---|
| No real owner packet exists | External contact has not happened inside the archive | Send/adapt packet, record send log, then status clock |
| Live-window card cannot authorize closure | It only records controls for a bounded window | Add or use a bounded end-of-window readout artifact/gate after terminal card state |
| Public claims could still creep after a clean window | Public language is outside the local card artifact | Keep the public claim lexicon and readout claim-family effects active |
| Closure pressure remains | `FT-0181` is live and the archive is ready-but-not-closed | Require acceptance, readout, post-readout action, closeout, and signoff before closure |

## Do not compensate with bureaucracy

Do not add a branch, schema field, or registry row unless a real packet or a broken
local artifact shows the current router, contact, intake, seed, review, decision,
ticket, live-window card, readout, or closure path cannot represent the problem.
