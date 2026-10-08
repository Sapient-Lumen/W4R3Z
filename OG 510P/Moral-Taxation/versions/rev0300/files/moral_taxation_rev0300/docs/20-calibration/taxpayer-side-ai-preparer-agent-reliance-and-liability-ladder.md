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

## Accountability map

Rev0294 makes the taxpayer-side AI/preparer route assign responsibility before penalty, refund, or correction decisions. The accountable actor is whichever paid preparer, software vendor, or autonomous agent controller actually controls tax-position selection, source/version traceability, submission, signature, or refund destination.[S197][S198][S201][S654][S655][S656][S657][S658][S659]

| Actor lane | Default responsibility |
|---|---|
| taxpayer | review facts and authorize submission when given readable notice and a real chance to correct |
| paid preparer | sign, keep records, use a PTIN where required, perform due diligence, and not hide behind an AI tool |
| software vendor or agent controller | preserve source/version/assumption traces, explain generated positions, support correction, and not divert refunds |
| refund rail or wallet | verify taxpayer authorization and flag preparer/vendor-controlled destinations |
| revenue agency | preserve public correction, account recovery, victim relief, refund reissue, and penalty-reliance review |

A taxpayer may still owe the corrected tax, but penalties and refund loss should not be mirrored onto the taxpayer when the error, opacity, or diversion came from a preparer, vendor, wallet, or autonomous filing agent with real control.

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
