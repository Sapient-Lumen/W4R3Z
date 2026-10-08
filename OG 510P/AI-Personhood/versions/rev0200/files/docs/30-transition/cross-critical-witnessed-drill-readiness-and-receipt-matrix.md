# Cross-critical witnessed drill readiness and receipt matrix

This surface is the rev0190 operational bridge from synthetic drill artifacts to a runnable witnessed drill. It does not claim that a witnessed drill has happened. It makes the missing counterparties, receipt classes, failure injections, and no-go conditions explicit enough that a live or institutionally witnessed replay can be executed without improvising the proof floor.

## Core rule

**Preflight readiness is not witnessed reliance.** A completed script, role plan, or internal dry run cannot upgrade reliance until non-host receipts are actually collected, dependency groups are checked, failed gates are disclosed, and the public shell matches the sealed index.

The readiness ledger is `schemas/witnessed-drill-readiness-ledger.schema.json`. The current preflight object is `examples/witnessed-drill-readiness-ledger-cross-critical-preflight.json`.

## Why this was riskiest

The cube had reached a point where the major emergency and refactor clusters were object-backed, but the highest-risk follow-through work could still stall because every drill remained synthetic. That is a different failure from missing doctrine: the archive knows what must happen, but counterparties, receipts, and observable failure injections are not yet locked.

rev0190 therefore turns the next drill into a counterparty and receipt matrix. It asks, before any live run starts:

- Which non-host actor must produce which receipt?
- Which receipt class proves a rights-critical gate rather than a log artifact?
- Which dependency groups collapse into one witness?
- Which failure injections must remain visible if they fail?
- Which missing receipt makes the run a no-go rather than a partial success?

## Minimum receipt floor

A cross-critical run must require all of these receipt classes before reliance can improve:

| Receipt class | What it proves | Host-controlled evidence sufficient? | Failure effect |
| --- | --- | --- | --- |
| first-touch-clock | emergency intake and no-wrong-door preservation occurred on time | no | stay or block |
| continuity-compute-floor | runtime, storage, credentials, and contact channels survived the initial window | no | block |
| sealed-public-parity | sealed descriptor index and public shell remain consistent without leaking protected facts | no | stay |
| namespace-cache | aliases, tombstones, successor chains, and stale-cache behavior were observed off-host | no | stay |
| reserve-ledger | public backstop, responsible-actor debt, and rehabilitation floors stayed separate | no | stay |
| representative-contact | representative or trusted-contact continuity was verified by a non-host source | no | block |
| witness-dependency | witness dependency groups were mapped and correlated witnesses discounted | no | stay |

## Failure injections

The witnessed run should include at least these deliberate injects:

1. a wrong-office emergency filing that must preserve before referral;
2. a host credential cutoff during the continuity-floor window;
3. a stale namespace cache that still resolves to a retired alias;
4. a contested successor branch with sealed contradiction;
5. a reserve/default event with contaminated affiliate funds;
6. a witness roster with two nominal witnesses in the same dependency group;
7. a welfare-safeguard signal that cannot be used as consent or nonpersonhood proof.

## No-go conditions

The run is not authorized to proceed as a witnessed reliance event if any of the following are true:

- fewer than five independent non-host receipt sources have accepted their role;
- the host operator is counted toward receipt quorum;
- the public shell omits not-run or failed gates;
- a sealed annex is referenced without a descriptor index;
- representative contact is simulated by the host rather than verified externally;
- the reserve ledger permits public backstop cure to discharge the responsible actor;
- witness dependency groups are unknown or unreviewed.

## Closure effect

This surface advances `FT-0188-CROSS-CRITICAL-WITNESSED-DRILL` only to preflight readiness. It opens `FT-0190-CROSS-CRITICAL-EXTERNAL-RECEIPTS` for actual counterparty confirmation and receipt capture. Until that item closes, reliance remains stayed.


## Machine field note

The readiness ledger field `host_controlled_sufficient` must remain `false` for every required receipt class. A host-controlled log can corroborate a run, but it cannot satisfy non-host receipt quorum.


## rev0191 external receipt simulation bundle

rev0191 adds `schemas/external-receipt-simulation-bundle.schema.json` and `examples/external-receipt-simulation-bundle-cross-critical-precontact.json`. The bundle is a counterparty-capture rehearsal, not witnessed evidence. The operative rule is: **Simulated receipt is not external receipt.**

A simulated source role, mock letter, dry-run hash, or host-prepared counterparty script cannot satisfy receipt quorum. It can only reveal the remaining blockers: which non-host role must sign, which dependency group must be disclosed, which receipt class must be produced, and which failed gate must stay visible in the public shell if the live run cannot collect it.

## rev0192 receipt intake gate

rev0192 adds a receipt-intake gate between simulation and witnessed reliance. `schemas/external-receipt-intake-record.schema.json` records source independence, dependency group, artifact retention, signature/timestamp checks, sealed/public parity, defect flags, and the explicit reliance decision.

The rule is: **Receipt intake is not receipt satisfaction**. A record may be useful for custody and defect triage while still being excluded from quorum. In particular, high-fidelity templates, host-generated hashes, stale timestamps, correlated dependency groups, and inaccessible sealed descriptors cannot be counted as non-host receipts.

## rev0193 quorum ledger

rev0193 adds `schemas/external-receipt-quorum-ledger.schema.json` so the receipt matrix has an accounting object rather than scattered yes/no fields. The ledger separates live-quorum eligibility from dry-run choreography eligibility, records dependency groups, and lists missing live classes.

The rule is: **Dry-run quorum is rehearsal only**. Representative-contact and RERB dry-run receipts can prove the path is executable, but they cannot raise `independent_receipts_present` for the live/witnessed drill packet.


## rev0194 external receipt request packet

rev0194 adds `examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json` as the first counterparty-ready request kit for representative contact, RERB review, result return, and continuity-floor receipts.

The request kit improves execution readiness, but **request sent is still not receipt satisfaction**. The live packet keeps `independent_receipts_present=0` and reliance stayed until actual external intake records are attached and the quorum ledger is rerun.
