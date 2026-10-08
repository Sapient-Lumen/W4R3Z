# CT-policy-inspired admission and removal

**Track:** A (Deployable core)


Public transparency ecosystems (e.g., Certificate Transparency) evolved **operator admission policies** to keep logs operating in the public interest. This document adapts that approach for voting transparency witnesses and monitors.

## Admission requirements (minimum)

* public documentation of operations, endpoints, and policies
* availability and latency targets
* independent monitoring hooks
* incident reporting process
* key management and rotation process



## Automated / AI-run operators (allowed, but accountable)

A witness/monitor may use automation (including AI systems) to process evidence and publish reports.
This is permitted **only** if there is a clearly accountable controlling party.

Minimum additional requirements:
* disclose the controlling legal entity / operator and any material affiliations
* disclose the automation surface (service/model family, versioning policy, and who can update it)
* publish a signed charter + COI/funding disclosures (see `artifacts/templates/witness-profile.md`, `artifacts/templates/witness-charter-template.md`)
* treat undisclosed operator/control changes as an incident (revise profile + charter; publish a PublicNotice)

## Removal triggers

* equivocation or refusal to provide consistency proofs
* refusal to publish COI/funding disclosures
* sustained SLA failures
* evidence of collusion or selective signing

## Governance process

* application → public comment → probation → approval
* annual re-evaluation
* emergency suspension process