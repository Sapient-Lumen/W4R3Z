# Live Counterparty Import Attempt and Quorum Recompute

Revision: `rev0198`  
Status: active transition control.  
Owner: receipt and reliance steward.

## Rule

Live counterparty attempt is not live counterparty receipt.

Quorum recomputation overrides hand-edited quorum ledgers.

No-response clock does not start before non-host dispatch.

One imported class is not cross-critical reliance.

## Why this exists

The previous release correctly blocked actual-shaped fixture state from changing the live receipt floor. The next risk is subtler: a request packet, counterparty preflight, hand-edited quorum ledger, or single class-specific import could be treated as enough evidence to raise `independent_receipts_present`.

This surface adds two operational controls. `live-counterparty-import-attempt` records whether a real external import attempt has actually reached a counterparty. `quorum-recomputation-report` recomputes the live floor from import gates rather than trusting ledger assertions.

## rev0198 posture

`LCIA-2026-result-return-counterparty-preflight` is planned and pre-dispatch only. It has no sent request, no response, no intake, no import, no class credit, and no live-floor delta.

`QRR-2026-live-floor-zero-recompute-rev0198` reads the current request, response, intake, import-gate, quorum-ledger, and live-drill references and recomputes the live floor as zero. That means the archive now has a reusable no-overclaim audit path before any future edit to `independent_receipts_present`.

## Failed gates preserved

The failed-gate public summary remains mandatory for defective, declined, expired, fixture-disqualified, or not-yet-dispatched branches. Declination and no-response are failed-gate evidence and cure triggers; they are never waiver, consent, nonpersonhood proof, or WRSR closure.

## Closure condition

This lane closes only when a genuinely external response is collected, verified into intake, passed through the actual import gate, and then recomputed into class-local live credit without satisfying cross-critical quorum by itself.


## rev0199 non-host artifact replay

**Non-host-looking artifact is not live receipt.** rev0199 adds `docs/30-transition/nonhost-response-artifact-envelope-and-import-replay.md` plus NHRAE/LIRR objects so the archive can accept response-like artifacts without trusting their appearance. The result-return dry-run artifact is non-host retained and signed/timestamped for rehearsal, but recomputation still keeps `independent_receipts_present=0` because the envelope is institutional dry run rather than live counterparty evidence.

The live floor may change only after a future artifact passes envelope provenance, response verification, intake checks, actual import gate, and quorum recomputation. One result-return class remains class-local and cannot satisfy cross-critical reliance.

## rev0200 class-local replay firewall

rev0200 adds a live-class-local import replay scenario. This is not a live receipt. It is the positive-path firewall that proves a future valid result-return class import must remain class-local and cannot satisfy cross-critical quorum by itself.

Actual live counterparty response remains absent. The archive live floor remains zero until a provenance gate imports a real non-host artifact and recomputation confirms the class-local effect.

