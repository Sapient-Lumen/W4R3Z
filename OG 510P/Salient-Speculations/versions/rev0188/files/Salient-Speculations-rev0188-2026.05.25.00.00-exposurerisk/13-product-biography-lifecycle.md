# Product-Biography Lifecycle

The archive has many product-adjacent dossiers: product passports, proof of place, destruction certificates, repair-right evidence, small-supplier evidence brokers, compliance-object forgery, resolver capture, recall propagation, and digital waste routing. rev0182 consolidates these into a lifecycle model parallel to `06-reliance-object-lifecycle.md`.

## Core claim

> Products are becoming governed biographies rather than static units of sale.

The hard object is no longer only the product. It is the evolving, queryable, disputed, privacy-scoped, repairable, recallable, resellable, and eventually retired record attached to the product, batch, component, facility, operator, and material lineage.

## State sequence

| Stage | State question | Typical artifacts | Failure mode |
|---|---|---|---|
| 1. Identity binding | What exact product, batch, model, component, facility, or operator is this? | GTIN, serial, batch ID, operator ID, facility ID, passport identifier, QR/data carrier | subject mismatch, duplicate ID, reused ID, missing carrier |
| 2. Passport creation | Which required data fields exist, and who issued them? | digital product passport, due-diligence statement, conformity documents, sustainability fields | forgery, issuer compromise, incomplete passport |
| 3. Resolver lookup | Where does a verifier go to retrieve current state? | resolver, registry, service provider, data carrier, URL, API, wallet/pointer | resolver capture, outage, successor failure, stale redirect |
| 4. Market entry | May the product be placed, imported, procured, insured, financed, or sold? | customs check, compliance status, restricted-market flag, authorization record | false clearance, jurisdiction mismatch, small-supplier exclusion |
| 5. Use and service | What happens after sale? | repair event, diagnostic log, parts record, warranty record, firmware update, refusal reason | event forgery, repair lockout, data over-collection, independent-repair exclusion |
| 6. Incident / recall | Has a defect, hazard, nonconformity, or safety action changed the product's status? | recall notice, Safety Gate alert, defect report, withdrawal state, remedy plan | nonpropagation, stale resale listing, weak subject binding |
| 7. Resale / transfer | What biography travels to the next owner, buyer, lender, insurer, platform, or recycler? | transfer attestation, repair history, recall-clearance proof, warranty continuity, privacy-filtered history | over-disclosure, missing repair history, market chilling |
| 8. Refurbish / remanufacture | Is this still the same product for passport, safety, warranty, and recall purposes? | refurbished-state label, component replacement record, re-certification, new subject relation | identity split/merge errors, status laundering |
| 9. Destruction / recycling | Has the product exited use, and what materials or liabilities remain? | destruction certificate, recycling record, waste routing proof, material recovery claim | fake retirement, double-counted recycling, residual-risk opacity |
| 10. Archive / afterlife | How long must past states remain queryable? | historical passport view, recall archive, repair-history retention, audit log | erased evidence, unverifiable old state, privacy conflict |

## Relationship to existing dossiers

- `repair-right-evidence` occupies stage 5.
- `small-supplier-evidence-brokers` spans stages 1 through 4.
- `compliance-object-forgery` is an attack layer across all stages.
- `data-minimization-proofs` is a privacy layer across stages 5 through 8.
- `resolver-capture` occupies stage 3 but can compromise every later stage.
- `recall-state-propagation` occupies stage 6 and becomes critical at stages 7 and 8.
- `destruction-certificates`, `retirement-proof`, and `digital-waste-routing` occupy stages 9 and 10.

## What should not be collapsed

Product biography is not the same as supply-chain traceability.

Traceability asks: where did the product and its components come from?

Biography asks: what governed states has this product passed through, which of them are still live, which are disputed, which must be hidden, which must be transferred, and which make the product non-reliant for a purpose?

A mature product biography includes supply-chain traceability but also repair, recall, resale, warranty, software update, restriction, end-of-life, and privacy-filtered transfer states.

## Privacy tension

A product biography can easily become a surveillance object. Repair logs, location histories, ownership transfers, warranty claims, diagnostic records, and resale disclosures may reveal household behavior, business relationships, or commercially sensitive supplier links.

Therefore the lifecycle requires proof profiles:

- prove recall status without exposing prior owner identity;
- prove authorized repair without exposing diagnostic details;
- prove compliance without exposing supplier trade secrets beyond the legally necessary fields;
- prove end-of-life processing without revealing customer relationships;
- prove warranty continuity without revealing unrelated service history.

## Adversarial tension

The strongest attacks are not limited to fake passports. They include:

- forged repair events;
- washed recall histories;
- resolver redirects to stale records;
- batch-level status attached to individual items incorrectly;
- refurbished goods re-entering markets under clean identities;
- fake destruction certificates;
- small-supplier data laundering through intermediaries;
- deliberate omission of software-update or battery-state histories;
- coercive proof requests at resale.

## Falsifiers

The product-biography thesis weakens if:

- product passports remain static compliance snapshots;
- repair-right regimes do not produce event records;
- recall systems stay disconnected from passports and resale platforms;
- consumers reject persistent product histories because of privacy concerns;
- enforcement agencies accept broad manufacturer claims rather than item/batch-level state;
- service-provider and resolver governance stays too fragmented for downstream reliance.

## Next dossiers suggested by this lifecycle

- repair-event privacy profiles become resale infrastructure;
- refurbished-identity splits become passport disputes;
- software-update histories become used-product diligence;
- battery-state attestations become resale price infrastructure;
- recall-clearance proofs become marketplace listing conditions;
- destruction-certificate replay becomes circularity-fraud control.
