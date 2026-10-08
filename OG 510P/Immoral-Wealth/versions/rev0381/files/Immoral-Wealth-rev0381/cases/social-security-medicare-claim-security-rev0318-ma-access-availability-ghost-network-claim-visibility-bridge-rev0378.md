---
revision_current: rev0378
generated_at: 2026-06-18T20:46:00Z
title: MA access availability, ghost-network, and denied-claim visibility bridge
status: not_certified_current
---

# MA access availability, ghost-network, and denied-claim visibility bridge — rev0378

Rev0378 closes the access-availability seam in the Medicare Advantage claim-security branch. A denial, appeal, or clinical-correctness row is still incomplete if the plan's provider network is only nominal, if listed providers are inactive, if behavioral-health access is measured only by workforce or directory counts, or if MA encounter data cannot definitively identify denied claims.

## Required row contract

At least one current MA contract/service/provider-month row must join HSD/ACC pass-fail or exception, MPF/API/directory listing, provider active/accepting/appointment status, access complaint or failed ZIP/specialty marker, definitive denied-claim status, payment/service restoration, clinical correctness, subgroup denominator, and source lineage.

## False-pass blocks

- No HSD/ACC pass: a network-adequacy table or automated criteria check is an access predicate, not proof that care was available.
- No exception pass: an approved network exception must preserve the exception reason, provider supply file, alternative access pattern, and beneficiary burden.
- No provider-directory pass: MPF/API presence does not prove the provider is active, accepts the enrollee, or can offer a timely appointment.
- No ghost-network pass: inactive providers and non-serving listed providers must be visible at provider-location level.
- No behavioral-health workforce pass: nominal workforce or specialty counts do not prove active Medicare/MA managed-care access.
- No complaint-only pass: complaints trigger review but do not measure the denominator of silent access failure.
- No encounter-adjustment pass: adjustment codes without a definitive denied-claim indicator cannot certify payment-denial incidence.
- No paid-claims pass: paid encounter volume cannot substitute for denied, abandoned, out-of-network, or never-scheduled care.
- No API/MPF pass: directory publication/update timing does not prove real-time accuracy or appointment capacity.
- No remedy pass: access restoration requires an actual provider appointment/service/payment restoration date.

## Required source ids

- S609
- S610
- S611
- S612
- S613
- S614

Certification remains **not certified current** because no current acquired row yet joins network availability, directory accuracy, denied-claim visibility, clinical correctness, and restoration.
