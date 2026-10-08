# Field execution risk burndown rev0280

## Burned down in this pass

| Risk | Rev0280 response | Status |
|---|---|---|
| Freshly generated packet looks old | Packet manifests now stamp the current release revision and the packet validator enforces it | Reduced |
| Field-next docket looks old | Router dockets now stamp the current release revision and the field-next validator enforces it | Reduced |
| Duplicate packet manifest key hides source drift | Removed the duplicate `evidence_state` source literal | Reduced |
| Pre-send friction becomes more doctrine | Send-now brief now centers the only pre-send judgment: owner route exists or route block is recorded locally | Reduced |
| Local executable artifacts become evidence by freshness | Audit and kernel restate that current-version local artifacts remain non-evidence | Watch |

## Still live

| Risk | Why it remains | Next practical move |
|---|---|---|
| No owner packet has been sent from this archive | The cloudtainer has no real owner route or permission to send | Human identifies owner route, sends/adapts packet, records send log |
| Real CSV may arrive outside source clock | Intake must remain router-first and source-contact-status gated | Use `make owner-field-next CSV=...` before intake |
| Operator may keep editing controls instead of field action | More doctrine feels safer than external contact | Treat new controls as suspect unless a real packet exposes a gap |
| Branch/history plane still consumes attention | 100 branch-family surfaces remain indexed in place | Read through the family index only when needed; do not spawn siblings |
| Live-window/readout path can tempt public claims later | A clean bounded window is not an outcome proof | Keep readout claim-family effects and public claim lexicon active |

## Current best next action

Run the router on a clean scratch root, prepare the packet if needed, perform the
external human send/adaptation only if a real owner route exists, and record the
send log. No new archive surface should outrank that.
