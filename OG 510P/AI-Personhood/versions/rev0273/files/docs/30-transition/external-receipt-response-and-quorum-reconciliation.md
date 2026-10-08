# External receipt response and quorum reconciliation

rev0195 targets the next live-evidence laundering seam after rev0194's request kit. The archive can now assemble a request packet, return subject-readable results, and intake external receipt artifacts. The remaining risk is that a response-looking object gets counted as receipt satisfaction, or that one good response is treated as full live quorum.

## Core rules

**Response received is not quorum.** A counterparty response can be actual, high-fidelity dry-run, declined, stale, defective, quarantined, or superseded. The response record only becomes live receipt evidence when verification creates an eligible external intake record, and even then it satisfies only its own class.

**One verified class is not live reliance.** A valid response for result return, representative contact, independent review, or a technical measurement cannot close cross-critical reliance by itself. Live reliance still requires class coverage, dependency separation, sealed/public parity, and failed-gate disclosure for missing classes.

**Declined or no-response is evidence, not satisfaction.** A declined response, expired request, or defective artifact must be preserved as a public failed gate and may trigger cure duties. It cannot be converted into a satisfied receipt floor.

**Response reconciliation preserves no-go outcomes.** The reconciliation ledger may advance readiness, explain defects, and narrow remaining collection work, but it must leave reliance stayed when any required live receipt class is missing.

## New objects

The response object is `schemas/external-receipt-response-record.schema.json`.

Current examples:

- `examples/external-receipt-response-record-result-return-steward-dryrun.json`
- `examples/external-receipt-response-record-continuity-witness-defective.json`
- `examples/external-receipt-quorum-ledger-response-reconciliation-dryrun.json`
- `examples/wrsr-live-exercise-outcome-response-reconciliation-stayed.json`

The first response is high-fidelity and non-host, but still dry-run. It can support rehearsal accounting only. The second response is defective and preserved as a failed gate. Neither can upgrade `independent_receipts_present` or close live quorum.

## Reconciliation lane

The response record links the request packet to response artifacts and to any intake record generated after verification. It forces four separations:

1. request sent versus response received;
2. response received versus verified intake;
3. verified intake versus class-specific receipt satisfaction;
4. class-specific satisfaction versus cross-critical live quorum.

This is deliberately more operational than another doctrine layer. It lets a steward see exactly what is still missing: which classes remain absent, which dependencies are correlated, which receipts are only dry-run, and which failed gates must remain public.

## Blocking fixtures

rev0195 adds two fixtures:

- `fixtures/negative-tests/external-receipt-response-unverified-counted-as-intake.json`
- `fixtures/negative-tests/external-receipt-single-class-counted-as-quorum.json`

The first blocks an unverified, defective, or stale response from generating actual intake. The second blocks one receipt class from becoming cross-critical live quorum.

## Refactor effect

This surface consolidates the receipt-response step between request packets, intake records, quorum ledgers, WRSR exercise outcomes, and live drill packets. It does not reopen the research tail and does not create a new theory of personhood. It removes a practical ambiguity in the evidence chain.

## Live posture

rev0195 still has no actual live external receipts. It has a response record shape, a high-fidelity dry-run response, a defective-response failed gate, a reconciliation ledger, and blocking fixtures. That is forward motion in the evidence plumbing, not a reliance upgrade.


## rev0196 response-to-intake conversion

rev0196 adds `docs/30-transition/response-to-intake-conversion-drill-and-failed-gate-ledger.md` as the conversion spine after response reconciliation. **Conversion eligibility is branch-specific.** A response can only create intake after full verification; declined, expired, defective, dry-run, and fixture-only paths remain failed-gate or rehearsal evidence.

The response record layer now feeds `examples/response-to-intake-conversion-drill-result-return-fixture.json`, which proves one eligible-shaped branch can generate an intake candidate while the declined, expired, and defective branches cannot. Live quorum remains stayed.

## rev0197 import-gate and failed-gate public shell

rev0197 response handling adds a provenance gate between actual-shaped records and live receipt-floor import. Response, intake, import, class credit, public failed-gate disclosure, and cross-critical quorum remain separate gates.

## rev0198 response-to-import guard

Response records now feed the import-attempt and recomputation lane. A response can be useful evidence, but only a passed import gate plus recomputation can change live receipt class credit.
