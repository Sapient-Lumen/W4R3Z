# 015 — Relay surfaces and the end of bilateral trust

**Status:** canon

## Thesis

As interoperable digital-governance stacks spread, more institutions will stop trusting bilateral integrations, ad hoc vendor onboarding, and self-asserted endpoints as sufficient carriers of high-trust transactions, signatures, or evidence.
The operative question shifts from “can you send the right data?” to “through which authorised relay, trust service, or registered intermediary did it arrive?”

## Why it matters

A surprising amount of digital administration still assumes that each institution can evaluate each endpoint for itself.
That works poorly once cross-border exchange, machine-verifiable signatures, structured invoicing, wallet-based credentials, and source-to-source evidence retrieval all expand at once.
Institutions do not want to assess every software stack, every sender, every signing device, and every data-sharing operator separately.
They increasingly want governed middle layers.

That changes where leverage sits.
The scarce asset is no longer only the proof, the query, or the transaction format.
It is the status of the relay operator that is allowed to carry, validate, or route it.
Access-point providers, qualified trust service providers, and registered data intermediaries become hidden but powerful infrastructure.

This note is not the same as transaction rails or query surfaces.
Those notes ask what kind of event or evidence moves through the system.
This note asks **who is trusted to operate the connective tissue**.
A relay surface appears when institutions do not trust every edge directly and instead govern admission to the network of admissible carriers.

## Mechanism sketch

- OpenPeppol now distinguishes sharply between candidate and certified service providers. Candidate providers are not authorised to offer live services in service domains, while certified providers are authorised to offer Access Point or SMP services and must meet mandatory Peppol dataset and network requirements.
- OpenPeppol also maintains a live public list of certified service providers across many jurisdictions. That means the network is not only standardised; it is operator-governed.
- The Once-Only Technical System architecture treats eDelivery Access Points as core architectural elements and explicitly allows interfaces to be implemented by independent software products or third-party services. The technical design documents define the Access Point itself as the standardised secure relay implementing the eDelivery AS4 profile.
- In the eIDAS world, qualified trust service providers are legally entitled to provide qualified trust services across all Member States once they meet the applicable requirements. The new 2026 implementing acts further formalise how supervisory notification, annual reporting, and identity-and-attribute verification by qualified trust service providers should work.
- The practical EUDI Wallet signature flow makes the relay logic visible. A wallet may sign directly only if it is itself certified as a secure device; otherwise it interfaces with a remote qualified signature device managed by a qualified trust service provider, and verification relies on trusted lists and certificate paths.
- The Data Governance Act shows the same move in data sharing. Notified data intermediation service providers may offer services across all Member States, can be confirmed against the Regulation’s requirements, and can then use the label “data intermediation services provider recognised in the Union”. The Commission now maintains a public Union register of those providers.

The deeper pattern is that many systems are no longer satisfied with compliant content alone.
They increasingly want compliant **carriers**.
Once proofs, queries, signatures, and structured transactions become routine governance objects, institutions start asking not just whether the message is well formed, but whether it moved through a recognised relay layer whose operator can be supervised, audited, listed, suspended, or replaced.

## What this speculation predicts

1. More high-trust digital procedures will require submission, routing, or verification through certified, listed, or registered intermediary operators rather than through arbitrary direct endpoints.
2. Economic power will concentrate in trust lists, provider registries, access-point operators, and compliance middleware that can sell “admissibility as a service” across multiple regimes.
3. Outages, de-authorisations, certification failures, or trust-list fragmentation at relay providers will increasingly become first-order governance incidents rather than back-office nuisances.
4. Policy conflict will move toward certification criteria, portability, fallback paths, market concentration, supervisory scope, and whether smaller actors can participate without buying access from a small relay class.

## Watchpoints

- more public trust lists, certified-provider directories, or mandatory access-point models appearing in identity, invoicing, evidence exchange, or data-sharing regimes
- mergers, concentration, or gatekeeping complaints involving access-point operators, qualified trust service providers, or registered intermediaries
- official fallback, portability, or outage-handling rules for when a required relay provider fails or loses status
- signs that the same relay operators or relay logic are being reused across signatures, invoices, evidence exchange, wallets, or regulated data-sharing systems
- evidence that direct API trust, self-hosted endpoints, or end-to-end validation without governed intermediaries is regaining favour in high-trust workflows

## What would weaken this

- direct standards-based verification remaining sufficient in practice, with institutions continuing to trust senders or endpoints without requiring governed relay operators
- relay certification or registration staying optional and commercially marginal rather than becoming a real condition of admissibility
- fragmentation across jurisdictions and sectors remaining so strong that relay status never becomes a reusable cross-domain advantage
- successful policy pushback treating mandatory intermediary layers as excessive lock-in, surveillance, or anti-competitive infrastructure

## Source anchors

- [SRC-070](../00-meta/bibliography.md#src-070)
- [SRC-071](../00-meta/bibliography.md#src-071)
- [SRC-072](../00-meta/bibliography.md#src-072)
- [SRC-073](../00-meta/bibliography.md#src-073)
- [SRC-074](../00-meta/bibliography.md#src-074)
- [SRC-075](../00-meta/bibliography.md#src-075)
- [SRC-076](../00-meta/bibliography.md#src-076)
- [SRC-077](../00-meta/bibliography.md#src-077)
- [SRC-078](../00-meta/bibliography.md#src-078)
