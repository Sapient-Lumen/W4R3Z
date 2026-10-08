# 021 — Permit-ready models and the end of plan-packet review

**Status:** canon

## Thesis

As building approval systems move onto BIM- and GIS-aware portals, open schemas, automated rule checks, and interoperable permitting stacks, the practical ability to build, retrofit, or expand will increasingly depend on submitting a machine-checkable project model rather than mainly on assembling a packet of drawings, narratives, and ad hoc clarifications for serial human review.

The scarce asset is no longer only land, financing, or a willing builder.
It is increasingly the ability to produce a **permit-ready model** that can survive schema validation, rule formalisation, cross-agency routing, and software-assisted compliance screening before scarce reviewer time is spent.

## Why it matters

This changes where control sits in the built environment.
The decisive bottleneck is no longer only the planning board, plan examiner, or code official as a human reader of static documents.
It is increasingly the earlier workflow in which a project team has to encode geometry, materials, uses, setbacks, and related properties into forms and models that multiple systems can interpret consistently enough to admit the project into an approval pipeline at all.

That matters because housing supply, infrastructure delivery, climate retrofit, public-works acceleration, and resilience upgrades all depend on permitting throughput.
If the admissible unit of action becomes a machine-checkable model, then schema maintainers, software vendors, rule-formalisation teams, municipal digital-capacity gaps, and open-standard governance become more important choke points in whether projects move quickly, stall, or become too expensive to submit.

This is related to `010`, `014`, `015`, `016`, `017`, and `019`, but it is not reducible to them.
`010` is about machine-readable goods.
`014` is about authoritative-source retrieval.
`015` is about trusted relay operators.
`016` is about runtime standing.
`017` is about differentiated access to scarce infrastructure.
`019` is about episode-specific adjudication loops in healthcare.
This note is about a different shift: the built environment moving from narrative plan packets toward **model-governed admissibility**.

## Mechanism sketch

- Singapore’s CORENET X already states the logic clearly. It is a one-stop integrated digital shopfront for regulatory approval of building works that uses Building Information Modelling and automation to streamline submissions, reduce fragmented agency interaction, and replace the older practice of producing multiple plan versions for separate agencies.
- The same stack is no longer experimental. Official implementation material says that from 1 October 2026 submission via CORENET X will be mandatory for all new projects regardless of size, with all ongoing projects to be onboarded from 1 October 2027.
- In the United States, the federal Permitting Technology Action Plan now pushes agencies toward digitised applications, interoperable permitting systems, shared services, automation of application and review processes, and a unified interagency environmental-review and permitting data system.
- That U.S. stack is not just about nicer portals. The official NEPA and Permitting Data and Technology Standard says agencies should structure software around shared entities such as projects, processes, and documents so different systems can exchange and reuse data consistently, improving transparency, integrity, and decision-making.
- Europe is building the same direction of travel in the municipal and standards layer. OGC’s CHEK initiative is explicitly aimed at digital building permit procedures and automated compliance checks using geodata and three-dimensional building representations, together with a modular reference process and interoperable reference architecture.
- The European BUILD UP toolkit for municipalities describes a maturity ladder from paper-based permitting toward BIM integrated with GIS, emphasises open standards to avoid vendor lock-in, and treats digital building permits as part of a more efficient, transparent, and sustainable construction sector.
- Put together, these moves suggest a deeper shift: the practical front door to building approval is becoming less about submitting a readable packet and more about delivering a **machine-legible project object** that can be validated, routed, compared, and partially checked before traditional discretionary review begins.

## What this speculation predicts

1. More jurisdictions will require project teams to submit structured BIM/GIS artefacts or equivalent machine-readable data as the primary approval substrate rather than treating them as optional supplements to PDFs and narrative plans.
2. Code-writing and permit administration will increasingly invest in rule formalisation, schema design, validation tooling, and reference architectures because those become decisive for throughput, consistency, and applicant admissibility.
3. Firms that can generate permit-ready models cheaply will gain a structural speed advantage in housing, retrofit, logistics, and infrastructure pipelines over firms that still treat digital modelling mainly as an internal design convenience.
4. Municipalities with weak digital capacity will increasingly depend on external platforms, standards bodies, or shared-service intermediaries, creating new vendor-power and interoperability fights around the approval stack.
5. Disputes over what is encoded, machine-checkable, or omitted from the model will become a more important part of planning and code politics, because the model increasingly shapes what the system can notice and approve quickly.

## Watchpoints

- more jurisdictions moving from voluntary or pilot model-based submissions to mandatory BIM/GIS-aware submission paths for ordinary projects
- public permitting programs publishing common data standards, reference architectures, rule libraries, or validation tools rather than only process guidance for human reviewers
- architecture, engineering, and construction firms marketing permit-ready modelling, schema compliance, or automated pre-check capability as a core permitting advantage
- evidence that housing, retrofit, infrastructure, or resilience projects move materially faster where interoperable digital permit systems and rule-formalised checks are deployed
- evidence that most authorities continue to rely mainly on narrative packets, static PDFs, and bespoke human review, with model-based permitting remaining niche or cosmetic

## What would weaken this

- major jurisdictions failing to move beyond pilots, leaving model-based permitting as a showcase layer with little effect on ordinary approvals
- open standards and interoperability efforts proving too weak, fragmented, or vendor-captured to support broad reuse across agencies and municipalities
- automated compliance checks staying too shallow to matter, so the real bottleneck remains essentially unchanged human interpretation of narrative materials
- applicants, reviewers, and courts continuing to treat the packet of drawings and written explanation as the only truly authoritative approval object for most projects

## Source anchors

- [SRC-113](../00-meta/bibliography.md#src-113)
- [SRC-114](../00-meta/bibliography.md#src-114)
- [SRC-115](../00-meta/bibliography.md#src-115)
- [SRC-116](../00-meta/bibliography.md#src-116)
- [SRC-117](../00-meta/bibliography.md#src-117)
- [SRC-118](../00-meta/bibliography.md#src-118)
