# Information commons & public media governance (pluralism without censorship)

**Cross-stack note:** use `295-public-information-media-and-access-routing-guide.md` for the canonical route across the public-information / media / access cluster. This memo remains the media / platform / pluralism specialization; `129` is the public-sphere integrity front door; `61` is the official-communication specialization; `200` is the requester-side access-to-documents neighbor; `77` is the secrecy-boundary neighbor.

**Purpose:** keep the *information ecosystem* (news, platforms, ads, broadcasters, messengers) plural, inspectable, and resistant to capture—**without** handing any faction a censorship lever.

**Person served:** a person trying to understand what’s true enough to act on (vote, safety, health, livelihood) while facing manipulation, harassment, or opaque amplification.

**Design stance:** regulate **systems and incentives** (distribution, targeting, monetization, ownership) more than individual posts; keep any restrictions **receipt‑bound, contestable, and sunset‑controlled** (`106`, `112`, `118`, `129`).

## Failure modes (what goes wrong in practice)
- **Ownership opacity → covert capture:** who controls outlets, ad networks, or “local” pages is hidden.
- **Attention markets reward fraud:** outrage and scams outcompete verification.
- **Opaque distribution is power:** ranking/recommendation choices decide what’s visible (`129`).
- **Safety collapse:** targeted harassment/doxxing drives speakers out (`129`).
- **State censorship-by-proxy:** governments pressure platforms/broadcasters without due process.
- **Commercial censorship-by-default:** revenue/brand safety rules quietly erase unpopular groups.
- **Emergency drift:** “temporary” controls never end (`112`).

## Minimal primitives (portable across regimes)

### IM-1 Media ownership & control transparency (anti‑covert capture)
- MUST maintain a **Media Ownership & Control Register (MOCR-*)** covering:
 - beneficial ownership; controlling interests; board/exec roles; major financiers; cross‑ownership links;
 - outlet identifiers + jurisdiction + licensing status (if applicable);
 - change receipts: `MOCR-CHANGE-*` (who/what changed, effective date, rationale, conflicts joins).
- MUST make the register **queryable** and exportable; publish **coverage** (what is excluded and why).
- SHOULD attach conflicts joins to `120` (influence/COI joins) and procurement joins where public advertising is a material funding channel (`110`).

**Why:** transparency is a *floor* for pluralism enforcement and for “follow the money” accountability. (See Council of Europe media pluralism guidance.)

### IM-2 Platform systemic risk governance (design choices, not single posts)
For “large” distribution intermediaries (platforms, app stores, ad exchanges):
- MUST publish a **Systemic Risk Assessment** and mitigation plan (updated on a fixed cadence) covering:
 - election integrity, public health, fraud/scams, harassment/doxxing, child safety, and manipulation;
 - the role of **recommender design**, friction/virality, and monetization.
- MUST support **independent audit** with a published audit scope, methods, and limitations.
- SHOULD provide **researcher access** and a safe data‑sharing path consistent with privacy (`127`).

**Implementation note:** the EU Digital Services Act (DSA) is an example of a legal regime that operationalizes “systemic risk assessments + audits + transparency” for very large platforms.

### IM-3 Advertising & monetization legibility (treat ads as governance)
- MUST run an **Ad Transparency Repository (ATR-*)**:
 - who paid; what targeting criteria were used (high‑level, privacy‑safe);
 - creatives + spend bands + delivery dates;
 - special handling for political/issue ads (additional fields + stricter retention).
- MUST publish **fraud/abuse metrics** for the ad marketplace (scams, impersonation, coordinated inauthentic behavior) and response times.
- SHOULD require “Know Your Business Customer” style checks for high‑risk ad buyers and sellers, with receipts (KYBC-*) (aligned with platform obligations in modern regimes like the DSA).

### IM-4 Due process for moderation and amplification (no silent swap)
- MUST provide contestable decisions for takedown/downrank/label/verification actions, with **decision receipts** that join to `DRR-*` / `RCR-*` patterns and the correction discipline in `129`.
- MUST prohibit **unlogged** policy changes that affect reach at scale: treat as rule changes with `118` change‑control + `129` Amplification Register.
- SHOULD provide an **appeal lane** that is usable without a lawyer and without retaliatory exposure (`98`).

### IM-5 Safety-to-speak floor (pluralism requires protection)
- MUST maintain enforceable anti‑doxxing and anti‑harassment controls; publish closure times and retaliation handling (joins to `121`).
- SHOULD provide protected participation options for high‑risk speakers (journalists, witnesses, election workers, clinicians).

### IM-6 Public-interest media capacity (pluralism requires production)
- MUST ensure *plural production* doesn’t collapse to a handful of owners or “AI sludge”:
 - baseline support for local investigative/public-interest reporting can be routed through arms‑length funds with transparent criteria and audit (`110`, `130`).
- SHOULD diversify support tools: matching grants, vouchers, public interest ad credits with strict ATR transparency, newsroom cooperative supports.

## Guardrails (to avoid the censorship trap)
- **Human-rights baseline:** restrictions must be lawful, necessary, proportionate, and contestable; avoid “truth ministries.” (`106`, `[BIB-UNESCO-PLATFORM-GUIDELINES]`)
- **Independence:** regulators need revolving-door restrictions and open decision dockets (`79`, `77`).
- **Sunsets + post‑mortems:** extraordinary measures require explicit end dates and review (`112`).
- **Jurisdiction seams:** cross-border takedown requests and mutual legal assistance must be logged as requests with outcomes (join to `114`).

## Minimal metrics (publishable without bloat)
- MOCR coverage rate (share of audience/revenue covered by ownership transparency).
- Correction propagation ratio and takedown appeal resolution time (`129`).
- Ad repository completeness (share of spend captured) + scam/ad fraud closure time.
- Researcher access availability (requests granted/denied with reasons).
- Safety-to-speak: doxxing/harassment incident closure times and retaliation substantiation rate.

## Cross-links
- Public sphere interfaces and correction discipline: `129-public-sphere-and-epistemic-infrastructure.md`.
- Rule change control (platform policies are rules): `118-rulemaking-and-change-control.md`.
- Conflicts/influence joins: `120-conflicts-of-interest-and-influence-integrity.md`.
- Data governance + privacy-safe access: `127-data-governance-and-privacy-interfaces.md`.

## Citations
- `[BIB-UNESCO-PLATFORM-GUIDELINES]` (platform governance baseline; systems focus).
- `[BIB-EU-DSA-VLOPS]` (systemic risk assessment/audit/transparency example regime).
- `[BIB-OECD-DISINFO-2020]` (governance responses to disinformation framing).
- `[BIB-COE-MEDIA-PLURALISM-2018]` (media pluralism + ownership transparency guidance).
