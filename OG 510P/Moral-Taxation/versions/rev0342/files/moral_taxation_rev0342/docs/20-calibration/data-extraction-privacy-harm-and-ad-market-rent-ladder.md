# Data-extraction, privacy-harm, and ad-market-rent ladder

## Question in one sentence

What ladder should distinguish non-tax privacy/competition remedies from taxes, levies, fees, proceeds-repair rules, or data-rent charges in personal-data, behavioral-advertising, and platform-gatekeeper cases?[S459][S460][S461]

## Companion routes

Use this memo with:

- [`../10-framework/data-extraction-privacy-and-ad-market-rent-routing.md`](../10-framework/data-extraction-privacy-and-ad-market-rent-routing.md)
- [`../10-framework/data-minimization-and-purpose-bounded-verification-routing.md`](../10-framework/data-minimization-and-purpose-bounded-verification-routing.md)
- [`../10-framework/public-input-reciprocity-and-commons-maintenance-routing.md`](../10-framework/public-input-reciprocity-and-commons-maintenance-routing.md)
- [`../10-framework/anti-discrimination-and-status-proxy-routing.md`](../10-framework/anti-discrimination-and-status-proxy-routing.md)
- [`../10-framework/beneficiary-gain-and-windfall-routing.md`](../10-framework/beneficiary-gain-and-windfall-routing.md)

## Option scan

| Option | Shape | Archive verdict |
|---|---|---|
| A — no data-specific rule | ordinary income and consumption taxes only. | Correct for low-risk, low-rent, genuinely consensual processing. |
| B — data volume tax | tax records, users, clicks, or impressions. | Usually reject: becomes a proxy head tax or small-actor burden. |
| C — extraction-rent levy | tax surplus from gatekeeper data combination, behavioral targeting, or ad-tech bottlenecks. | Adopt when rent is measurable. |
| D — privacy-harm fee | charge harmful processing and route proceeds to repair. | Use only for compensable harms; prohibit non-compensable uses. |
| E — competition/privacy rule | restrict data combination, self-preferencing, opacity, or targeting. | Prefer where tax would sell permission. |

## Ten-gate ladder

1. **data-kind gate** — distinguish volunteered, observed, inferred, sensitive, children's, biometric, location, health, financial, workplace, and public-record data.
2. **consent-quality gate** — test meaningful choice, refusal cost, dark patterns, bundling, pay-or-consent pressure, and ability to withdraw.
3. **purpose-boundary gate** — compare collection purpose with later processing, sharing, profiling, model training, targeting, or resale.
4. **market-power gate** — identify gatekeeper status, user lock-in, business-user dependence, ad-exchange control, and cross-service combination.[S460]
5. **ad-market-rent gate** — measure auction spread, intermediation take rate, targeting surplus, exclusionary advantage, and publisher/user bargaining power.[S461]
6. **harm gate** — separate compensable privacy/security harms from discriminatory, manipulative, or autonomy harms that require prohibition.
7. **valuation gate** — estimate rent or harm with revenue share, excess return, auction spread, broker fee, or avoided compliance cost; avoid taxing each person-record by default.[S459]
8. **instrument gate** — choose non-tax rule, transparency duty, data separation, levy, fee, public-input charge, disgorgement, or private remedy.
9. **floor gate** — prevent pass-through to low-income users, small publishers, small merchants, or workers whose data dependence is not voluntary.
10. **proceeds gate** — route proceeds to privacy enforcement, public-interest data infrastructure, affected-user remedies, anti-discrimination testing, or digital public capacity.

## Default settings

| Posture | Instrument | Guardrail |
|---|---|---|
| low-risk processing | ordinary tax and privacy compliance | no special data toll. |
| gatekeeper data-combination rent | rent levy or competition remedy | do not charge users for being locked in. |
| non-compensable surveillance harm | prohibition or strict rule | do not sell permission through tax. |
| measurable compensable harm | fee/disgorgement plus remedy | proceeds to affected users or public enforcement. |
| ad-tech bottleneck | rent charge or structural remedy | protect publishers, small businesses, and users. |

## Accountability capsule

Authoritative assignment: route `data_extraction_privacy_ad_market_rent` in [`actor-accountability-profiles.json`](../00-meta/actor-accountability-profiles.json).

- Duty owner: `platform_gatekeeper_or_adtech_operator_controlling_data_extraction_and_ad_market_monetization`.
- Rent/benefit trace: `platform_gatekeeper_data_broker_or_ad_network_capturing_attention_data_and_ad_auction_rent`.
- Bottleneck/evidence: `consent_interface; ad_exchange +3 more`; evidence starts with `data_collection_category_consent_and_dark_pattern_record; ad_auction_take_rate_targeting_and_revenue_record +2 more`.
- Fallback duty: `public_body_must_preserve_privacy_notice_opt_out_and_non_surveillance_access_to_essential_channels_with_fallback_channel`.


## Source IDs only

[S459][S460][S461]

[S459]: ../../SOURCES.md#S459
[S460]: ../../SOURCES.md#S460
[S461]: ../../SOURCES.md#S461
