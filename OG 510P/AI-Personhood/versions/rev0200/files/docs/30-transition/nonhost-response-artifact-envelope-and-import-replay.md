# Non-host response artifact envelope and import replay

rev0199 addresses the next reliance-laundering seam after live-import recomputation: an artifact can look external, signed, retained outside the host, and class-specific while still being only an institutional dry run. The archive therefore needs an envelope layer and replay report that prove the collection context before any response, intake, import, or quorum object can change the live receipt floor.

## Core rules

**Non-host-looking artifact is not live receipt.** A message, timestamp, signature surrogate, hash, sealed descriptor, or docket-like artifact can be generated and retained outside the host and still fail live reliance if it was collected as a rehearsal, institutional dry run, placeholder, fixture, or host-arranged simulation.

**Witnessed envelope is not counterparty authority.** A dry-run steward may verify that the request shape, subject-readable result-return packet, retention path, and public failed-gate shell are coherent. That does not prove the steward has live authority to satisfy a receipt class, waive subject rights, close WRSR, or alter personhood/remedy posture.

**Import replay must preserve disqualification.** The replay must trace envelope → response → intake → import gate → quorum recomputation. If any source artifact is institutional dry run, controlled fixture, host-generated, stale, unsigned, dependency-correlated, or unverified, the replay must keep `live_floor_delta=0` and publish the failed gate.

**One class-local import never satisfies cross-critical reliance.** Even a future live result-return class import would be only class-local evidence. It cannot satisfy first-touch, continuity floor, sealed/public parity, namespace, reserve, representative-contact, independent-review, welfare-signal, and witness-dependency classes by implication.

## rev0199 envelope/replay chain

- `schemas/nonhost-response-artifact-envelope.schema.json` defines the evidence envelope around response-like artifacts.
- `examples/nonhost-response-artifact-envelope-result-return-institutional-dryrun.json` records a high-fidelity non-host dry run for result return. It is useful rehearsal evidence but live-weight zero.
- `examples/external-receipt-response-record-result-return-institutional-envelope-dryrun.json` and `examples/external-receipt-intake-record-result-return-institutional-envelope-dryrun.json` prove that the response/intake shapes can be generated without becoming live receipt evidence.
- `examples/actual-receipt-import-gate-result-return-institutional-dryrun-no-live-delta.json` rejects the envelope from the live floor because collection context is high-fidelity dry run.
- `schemas/live-import-replay-report.schema.json` and `examples/live-import-replay-report-result-return-institutional-dryrun.json` bind the chain and record the stayed decision.
- `examples/quorum-recomputation-report-nonhost-artifact-replay-rev0199.json` recomputes the live floor from import gates and keeps `independent_receipts_present=0`.

## Public failed-gate effect

A failed or stayed envelope is public-state evidence, not disappearance. It should say which receipt class remains missing, why the dry run cannot satisfy live reliance, which sealed details are withheld, which substitute route remains open, and what must happen next. It must never infer waiver, consent, nonpersonhood, or closure from no-response, declined response, dry-run response, or one-class evidence.

## Forward motion without overclaiming

rev0199 makes the next live step sharper. The archive can now accept a future actual non-host response artifact into the same chain, replay the import gate, recompute quorum, and show precisely whether a live class-local delta exists. Until that happens, all current non-host-looking artifacts remain rehearsal, failed-gate, or stayed evidence.
