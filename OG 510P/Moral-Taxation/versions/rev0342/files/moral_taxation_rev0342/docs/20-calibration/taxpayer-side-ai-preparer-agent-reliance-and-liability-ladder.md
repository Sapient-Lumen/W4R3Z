# Taxpayer-side AI preparer, agent, reliance, and liability ladder

## Question in one sentence

When a taxpayer, preparer, or software vendor uses an AI system to answer tax questions or prepare a return, who must keep identity, source, refund, correction, and reliance accountability?[S197][S198][S201][S654][S655][S656][S657][S658][S659]

## Companion routes

Use this memo with:

- [`../10-framework/taxpayer-side-ai-agent-preparer-reliance-and-liability-routing.md`](../10-framework/taxpayer-side-ai-agent-preparer-reliance-and-liability-routing.md)
- [`compliance-cost-assisted-filing-and-preparer-dependence-ladder.md`](compliance-cost-assisted-filing-and-preparer-dependence-ladder.md)
- [`model-assisted-enforcement-red-team-standard.md`](model-assisted-enforcement-red-team-standard.md)

## Option scan

| Option | Shape | Archive verdict |
|---|---|---|
| A — self-help AI explanation | taxpayer uses AI like a calculator or guide and independently reviews official forms | Low-risk only for simple questions with source links and no automated filing. |
| B — software-embedded AI | commercial or public filing software suggests entries, credits, or risk flags | Requires logs, source/version traceability, user review, and correction support. |
| C — paid AI-assisted preparer | human preparer uses AI but signs, reviews, and keeps records | Treat as preparer practice; AI is a tool, not a liability escape. |
| D — autonomous filing agent | system drafts, signs, submits, or communicates with agency with limited human review | High-risk; require explicit authorization, accountable controller, audit trail, and narrow scope. |
| E — ghost AI/preparer stack | paid tool or person prepares without signature, PTIN/accountability, or refund control safeguards | Reject and route to preparer-misconduct/victim relief. |

## Parameter ladder

Rev0286 current-source note: ghost-preparer, PTIN/signature, and credit-scam warnings make identity and refund-control fields mandatory for AI-assisted paid preparation.[S659]

1. **role map** — Record whether AI gave advice, classified facts, drafted forms, selected positions, signed, submitted, or routed refunds.
2. **accountable actor** — Name taxpayer, paid preparer, firm, vendor, and representative; do not let model identity replace legal accountability.
3. **authority trace** — Store rule versions, forms, official publications, assumptions, citations, and generated explanation at filing time.
4. **taxpayer review** — Require a readable summary and opportunity to correct facts before signature or submission.
5. **preparer compliance** — Apply PTIN, signature, due diligence, copy/retention, and misconduct rules to AI-assisted paid preparation.
6. **refund destination control** — Verify refund account/wallet belongs to or is authorized by taxpayer; flag changes and preparer-controlled accounts.
7. **reasonable-reliance screen** — Separate tax correction from penalties where taxpayer reasonably relied on official/public tools or accountable preparers.
8. **hallucination/stale-law guard** — Block unsupported citations, stale effective dates, and fake forms; link to source-currentness registry for volatile law.
9. **victim relief** — Use complaint, affidavit, freeze release, refund reissue, and account recovery where preparer/tool misconduct diverted funds or altered returns.
10. **review trigger** — Reopen after AI error pattern, refund diversion complaint, fake-source detection, agency form change, or vendor model update.

## Default settings

| Parameter | Default | Redesign trigger |
|---|---|---|
| Identity | Accountable signer/vendor/preparer recorded | No signer or only model/persona name. |
| Traceability | Sources, versions, assumptions, and prompts retained | Black-box answer with no authority trail. |
| Refund control | Taxpayer-owned or expressly authorized rail | Preparer/vendor/model-controlled refund destination. |
| Reliance | Good-faith shelter for penalties, tax correction preserved | All automation error shifted to taxpayer. |
| Review cadence | Model/form/source updates trigger retesting | Tool continues after stale-law or hallucination failures. |

## Anti-pattern definitions

- **AI ghost preparer** — paid preparation occurs without accountable signer, PTIN, or vendor responsibility.
- **prompt opacity** — the filing position cannot be reconstructed from facts, assumptions, sources, and model output.
- **refund rail capture** — the preparer or tool directs payment to an account or wallet outside taxpayer control.
- **liability mirror trick** — vendor or preparer automation creates the error but the taxpayer alone absorbs penalties.
- **official-looking hallucination** — fake citations, stale rules, or invented forms are presented as binding tax authority.

## Accountability capsule

Profile: `taxpayer_side_ai_preparer_agent_reliance_and_liability` in `docs/00-meta/actor-accountability-profiles.json`. Duty owner: `paid_preparer_software_vendor_or_autonomous_agent_controller_with_return_or_refund_control`. Benefit/rent trace: `preparer_vendor_wallet_or_agent_benefiting_from_prompt_opacity_refund_rail_capture_or_liability_shift`.
Bottleneck/evidence start: `tax_software_channel`; `preparer_or_agent_submission_channel`; `refund_wallet_or_deposit_rail`; `ptin_signature_vendor_identity_and_notice_record`; `prompt_source_version_assumption_and_model_output_trace_record`; `taxpayer_review_authorization_and_submission_control_record`. Fallback: `public_body_must_preserve_no_rent_fallback_notice_cure_and_nonforfeiture_for_ai_preparer_correction_victim_relief_and_public_filing_access`.
Source continuity: [S197][S198][S201][S654][S655][S656][S657][S658][S659]

## Source IDs only

[S197][S198][S201][S654][S655][S656][S657][S658][S659]

[S197]: ../../SOURCES.md#S197
[S198]: ../../SOURCES.md#S198
[S201]: ../../SOURCES.md#S201
[S654]: ../../SOURCES.md#S654
[S655]: ../../SOURCES.md#S655
[S656]: ../../SOURCES.md#S656
[S657]: ../../SOURCES.md#S657
[S658]: ../../SOURCES.md#S658
[S659]: ../../SOURCES.md#S659
