# Task queue

- Await live `GLASSTTY_USER_SURFACE_DRILL_JSON=` from the Tampermonkey oracle.
- Use the after-write strict send selector to finalize send scoring.
- Run optional `GLASSTTY_PAGEWORLD_REST_JSON=` only if userscript output has a
  page-world/global gap.
- Capture live checkpoint proof bundle.
- Complete ledger/schema/audit/evaluator/privacy-review chain.


- Validate `proof-autopilot --execute-live` against the first real downloaded proof JSON.

- rev0352 follow-up: test recovery-vault behavior with a real live screenshot-sized proof capture and surface storage quota failure in operator status.


## rev0352 note

Added static extension readiness (`proof-extension-readiness`) plus side-panel attempt readiness evidence (`proof.operator_readiness`) so the live browser attempt is guided before any download/ingest step.

- Live operator: after downloading proof JSON, run `proof-attempt-audit --require-ready-to-download`, then `proof-autopilot --execute-live`.

- [rev0352] Preserve evidence-pack integrity as a required pre-publish check; do not publish a pack after editing privacy review without rerunning `proof-pack-integrity`.

## rev0353

- [done] Conversation engine, `ask`/`chat`/`run`/`mock-tab`, generation lifecycle.
- [next] File attachment (`--attach`) — blocks the auto-recovery loop.
- [next] Download-completion witness, then the T1/T2 auto-recovery loop.
- [next] Model / tier / version pinning from the queuer's v6.45 menu capture.
- [standing] A turn that did not settle is never reported as a success.
