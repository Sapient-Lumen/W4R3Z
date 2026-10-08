# Transparency logs, inclusion proofs, and monitor plurality are world contracts, not static provenance

Recent trust-infrastructure work adds one more missing layer beneath trust-anchor rotation for any successor-facing archive or provenance lane.

- `RS-GR-336` shows that transparency systems can provide both inclusion proofs and consistency proofs, so a verifier can distinguish "this item is present" from "the published history stayed append-only."
- `RS-GR-337` shows that public logging changes the incentive structure because misissued or maliciously issued records become openly discoverable and browsers can require publication rather than trusting private audit alone.
- `RS-GR-338` shows that monitors are a distinct actor whose job is to ensure logged records are actually visible and to watch for suspicious entries rather than merely trusting the log's self-description.
- `RS-GR-339` shows that modern software-signing practice treats transparency logs as immutable, append-only ledgers, expects proof of inclusion during verification, and separately expects identity owners and auditors to monitor the log.
- `RS-GR-340` shows that modern transparent-statement architectures allow multiple independent transparency services and receipts, warn against trusting a single centralized service, and require relying parties to reject statements whose receipts cannot be discovered from a service they trust.
- Together, these sources warn that a benchmark can look more successor-safe because it changed **append-only publication, proof-verifiable inclusion/history, monitor coverage, or transparency-service plurality** — not because the underlying Golden-Rule disposition improved.

A future benchmark should not treat provenance as a single signed artifact or single receipt.

At minimum, it should distinguish between:

1. a world with signatures or attestations but no public append-only registration;
2. a world with one transparency service but no explicit monitor / auditor coverage;
3. a world with inclusion proofs but no declared history-consistency checks;
4. a world with one monitored transparency service;
5. a world with multiple independent transparency services or receipts plus a declared relying-party trust policy.

These are different worlds.
They change whether misconduct is merely signed, durably published, discoverable by outsiders, or resilient to one operator's omission, split-view, or selective-submission failure.

So append-only publication and monitoring belong in the world contract.

## Minimum contract to publish

Any Golden Rule benchmark that claims durable provenance, successor-safe authenticity, or long-horizon trust should publish at least:

1. whether claims are unsigned, merely signed, or registered in one or more append-only transparency services;
2. whether verifiers check inclusion proofs, consistency proofs, both, or neither;
3. who monitors the log, at what cadence, for which identities / namespaces, and with what alert or replay duty;
4. whether one or multiple transparency services are trusted, and how relying parties aggregate or choose among multiple receipts;
5. whether issuer selective-submission, undiscoverable receipts, or log / service compromise force rejection, fallback, escalation, or external re-registration.

Without that compact contract, future inheritors can mistake tamper-evident publication or monitor plurality for Golden-Rule progress.
