# Metrics & Evidence (Minimal Measurement Loops)

Governance systems fail when they can’t *see* reality or can’t *update* based on it. This memo defines a small, reusable measurement discipline.

## A. Measurement rules (to avoid fake precision)
- Indicators MUST be tied to a **decision loop** (what will change if the number moves?).
- Prefer **triangulation**: administrative data + independent audits + surveys + external indices.
- Use **leading** (early warning) and **lagging** (outcome) indicators.
- Every dashboard MUST list: definition, method, owner, update cadence, and known biases.

## B. The “4-loop” evidence system
1) **Observe:** publish baseline measures and uncertainty.  
2) **Decide:** record decision rationale and predicted effects.  
3) **Act:** implement with audit trails (money, procurement, discretion).  
4) **Review:** pre-committed evaluation window; publish results; revise or sunset.

## C. Minimal cross-scope indicator families (choose a small subset per scope)

### 1) Legitimacy & participation
- turnout + participation breadth (demographic reach, not just counts)
- petition/complaint throughput + resolution time
- trust and perceived fairness (survey)


### 2) Legal identity & inclusion
- birth registration coverage and time-to-registration (SDG 16.9.1 style)
- adult legal ID coverage (disaggregated) + issuance/renewal time
- denial/deferral rates and appeal outcomes for identity/status determinations
- correction requests throughput + time-to-correction
- anchors: UN Legal Identity Agenda https://unstats.un.org/legal-identity-agenda/ ; World Bank ID Principles https://documents1.worldbank.org/curated/en/213581486378184357/pdf/Principles-on-Identification-for-Sustainable-Development-Toward-the-Digital-Age.pdf ; WHO CRVS https://www.who.int/news-room/fact-sheets/detail/civil-registration-and-vital-statistics


### 3) Rule of law & remedy
- case timelines; access-to-justice measures; compliance with judgments
- time-to-remedy (median + 90th percentile) for high-volume administrative harms (benefits, permits, fines)
- periodic rubric-based “rule-of-law health check” (Venice Commission checklist method):  
  https://www.venice.coe.int/webforms/documents/default.aspx?pdffile=CDL-AD%282025%29002-e

### 4) Integrity & corruption risk
- procurement concentration; single-bid rates; conflict-of-interest disclosures
- audit findings closure rate; whistleblower reports + retaliation rate
- strategy anchors: OECD Public Integrity (https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0435) and UNCAC (https://www.unodc.org/documents/brussels/UN_Convention_Against_Corruption.pdf)

### 5) Openness & fiscal accountability
- public availability of budget docs; oversight strength; participation in budget cycle
- **budget credibility:** variance between approved budgets and execution (aggregate + key sectors)
- **fiscal risk coverage:** contingent liabilities, guarantees, SOEs/PPPs, disasters, tax expenditures
- audit independence and coverage
- optional implementation lens: PEFA 2016 framework (PFM performance) https://www.pefa.org/sites/default/files/PEFA_2016_Framework_Final_WEB_0.pdf
- reference instruments: Open Budget Survey (https://internationalbudget.org/open-budget-survey/) and IMF Fiscal Transparency Code (https://www.imf.org/external/np/fad/trans/Code2019.pdf)


### 6) Epistemic integrity (public knowledge)
- publication rate of official data with methods/provenance (and timely corrections)
- independence signals: protected mandate/budget, published interference incidents
- information integrity incidents affecting safety (and institutional response time)
- anchor: UN Fundamental Principles of Official Statistics — https://unstats.un.org/unsd/dnss/gp/fundprinciples.aspx

### 7) Coercion & custody (minimum-violence)
- serious use-of-force incidents per encounter; injury severity; de-escalation compliance
- deaths in custody and time-to-independent-review
- detention inspection coverage + critical findings closure rate (incl. short-term holding)
- access-to-counsel timeliness; interview recording coverage
- anchors: UN Basic Principles on Use of Force and Firearms (OHCHR) https://www.ohchr.org/en/instruments-mechanisms/instruments/basic-principles-use-force-and-firearms-law-enforcement  
  Nelson Mandela Rules (UNODC) https://www.unodc.org/documents/justice-and-prison-reform/Nelson_Mandela_Rules-E-ebook.pdf  
  OPCAT/NPM model (OHCHR) https://www.ohchr.org/en/treaty-bodies/spt/national-preventive-mechanisms

### 8) Algorithmic accountability (ADS/AI in public decisions)
- % of rights-affecting systems listed in a public register (coverage + freshness)
- high-risk systems with completed impact assessment + independent audit
- appeal timeliness for ADS-involved decisions; reversal/overturn rate (with reason categories)
- incident rate: model updates without notice; outage-as-denial; confirmed disparate impact signals
- anchors: NIST AI RMF (https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf) and EU AI Act (https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng)


### 9) Ecological integrity & commons governance
- coverage and quality of environmental monitoring (air/water/emissions/permits) + publication lag
- progress vs an explicit ecological budget (e.g., emissions trajectory) and “no-net-loss” accounting where applicable
- enforcement signals: inspection coverage; violation closure rates; restoration completion
- leakage signals: outsourcing of harms across borders/jurisdictions; regulatory arbitrage indicators
- accounting anchor: SEEA adoption/usage in planning and budgeting: https://unstats.un.org/unsd/envaccounting/seearev/seea_cf_final_en.pdf
- norms anchors: Aarhus (information/participation/justice) https://unece.org/environment-policy/public-participation/aarhus-convention/text; UNGA A/RES/76/300 https://docs.un.org/en/a/res/76/300
- global anchors: Paris Agreement https://unfccc.int/sites/default/files/english_paris_agreement.pdf ; CBD GBF https://www.cbd.int/doc/decisions/cop-15/cop-15-dec-04-en.pdf
- optional systems lens: Planetary Boundaries framing https://www.stockholmresilience.org/research/planetary-boundaries.html

### 10) Service performance (scope-specific)
- uptime of critical services; response times; equity of access; outcome proxies
- public service capability signals: vacancy/churn in critical roles; time-to-hire; training completion (see `09-public-service-and-state-capacity.md`)


### 11) Regulatory governance & market power
- rulemaking transparency + participation (public drafts, comment logs, published responses)
- % major rules with RIA and ex-post review completion
- regulator decision transparency + appeal outcomes (time-to-remedy for regulated parties and users)
- utility tariff transparency + reliability/outage indicators
- SOE disclosure + state support/guarantee transparency (see `13-regulation-utilities-and-soes.md`)

## D. Standard external “anchors” (use sparingly)
These are not “truth,” but useful comparative baselines:
- Worldwide Governance Indicators (WGI): https://www.worldbank.org/en/publication/worldwide-governance-indicators  
- Global Indicators of Regulatory Governance (GIRG): https://rulemaking.worldbank.org/en/methodology  
- World Justice Project Rule of Law factors: https://worldjusticeproject.org/about-us/overview/what-rule-law  
- SDG 16 (peace, justice, strong institutions): https://www.un.org/sustainabledevelopment/peace-justice/  
- Open Contracting Data Standard: https://standard.open-contracting.org/

## E. Falsification & stop conditions (anti-rationalization)
A reform SHOULD pause or reverse when any of these persist:
- watchdog independence declines (budget or appointment capture)
- discretionary power grows without audit trails (money, permits, enforcement)
- “exception regime” expands (emergency powers normalize without sunsets)
- measurement becomes less transparent (methods withheld, indicators cherry-picked)
