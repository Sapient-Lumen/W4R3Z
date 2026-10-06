# Kernel Kit demo polish roadmap — rev0044

The demo should keep getting more useful without becoming an unbounded app.

Earned rev0044 rung:

```txt
trace/export receipt
```

Next rungs, in order:

1. Native User Timing marks around each stage.
2. Download/copy buttons for the BrowserRT receipt and Chrome-trace-shaped JSON.
3. Small trace table grouped by lane and event kind.
4. Scenario toggles: happy path, admission rejection, OPFS unavailable fallback.
5. Side-by-side run comparison.
6. Browser Worker OPFS storage-lane provider proof only after the page remains understandable.

Do not turn the demo into a dashboard before it remains easy to test.


## Kernel Kit demo contract carry-forward

Interactive Kernel Kit Demo. facility:kernel-kit-demo-audit. facility:kernel-kit-page-contract-audit. No browser performance claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.


Kernel Kit Demo Observatory. demo:kernel-kit-observatory-proof. facility:kernel-kit-observatory-audit. No production observability claim. No browser performance claim. No OPFS durability.

## Rev0045 carry-forward observatory non-claims

No browser download UX claim. No failure recovery automation claim.

## rev0047 diagnostic runbook carry-forward

Kernel Kit diagnostic runbook. `demo:kernel-kit-diagnostic-runbook-proof`. `facility:kernel-kit-diagnostic-runbook-audit`.

The diagnostic runbook is a future-session handoff that turns success/failure trace comparison into exact next commands. It is not root-cause automation.

No production runtime claim. No production observability claim. No product-market-fit claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim. No root-cause analysis claim. No automated failure recovery claim. Broad release remains browser-light.

