# Police Misconduct Records Normalized Across Jurisdictions — A Seed Document for Corpus Construction

This is a briefing for what the corpus could become. It is the unlikely-to-be-considered seed, not the build plan. Treat each section as a prompt for further research.

---

## 1. The premise

The United States has roughly 18,000 law enforcement agencies. There is **no national database of police misconduct**. Officers fired for cause in one jurisdiction routinely get hired in another ("wandering officers"). State laws governing disclosure vary wildly. Settlement agreements often include nondisclosure provisions. Internal affairs records are often sealed by statute. Police union contracts often require destruction of discipline records after a fixed period. Many states have Law Enforcement Officer Bill of Rights statutes that impede disclosure.

The corpus would be: **a normalized, jurisdiction-spanning, longitudinal record of police misconduct, lawsuits, settlements, discipline, decertification, and officer mobility — built from public records, court filings, news reports, FOIA releases, and civil society datasets.**

The audience is everyone with stake in policing: journalists, litigators, public defenders, prosecutors (for Brady/Giglio purposes), researchers, community members deciding where to live, accountability boards, oversight legislators, and the federal monitors who run consent-decree compliance.

---

## 2. Why capitalists will not build this

- The customer base (community members, public defenders, accountability orgs) cannot pay
- The opponents (police unions, FOPs, sheriff's associations) are politically powerful
- The legal liability is high (defamation, civil rights of named officers)
- The data is fragmented to the point of requiring extraordinary patient labor
- The most valuable work is normalization, which has zero direct revenue
- Existing commercial entrants (TransUnion's risk products, CLEAR by Thomson Reuters, Lexis) work *for* law enforcement, not against
- Police accountability has a political polarity that makes most institutional investors nervous

The closest existing efforts (Invisible Institute, Mapping Police Violence, Stanford's Big Local News, Reuters, USA Today's wandering officers project) are civic, journalistic, or academic. None has the resources for the comprehensive build. That's the gap.

---

## 3. The fragmentation problem — mapped

This is the central challenge. Document it carefully.

### 3.1 Jurisdictional fragmentation

- ~18,000 state and local law enforcement agencies in the US
- Plus federal agencies (FBI, DEA, ATF, USMS, ICE, CBP, USCG, USPP, DSS, Secret Service, others)
- Plus tribal police
- Plus university/transit/housing/school police
- Plus state highway patrols
- Plus county sheriffs (elected, with different rules than chief-led departments)
- Plus jail and prison guards (often a separate corpus but adjacent)
- Plus private police forces (railroad police, port authority, others)

### 3.2 Legal fragmentation

- 50 states' public records laws
- 50 states' civil service / discipline laws
- 50 states' Law Enforcement Officers Bill of Rights statutes (or absences)
- 50 states' POST (Peace Officer Standards and Training) commissions — some decertify, some don't, some publish, some don't
- 50 states' criminal codes (so "what charge an officer faced" is heterogeneous)
- Federal civil rights law (42 USC §1983) with qualified immunity overlay
- Federal criminal civil rights statutes (18 USC §242)
- Garrity v. New Jersey (statements under compulsion can't be used criminally — affects discipline records' usability)
- Brady v. Maryland and Giglio v. United States (prosecutors' disclosure duties; "Brady lists" exist in many counties, are usually secret)
- Marsy's Law expansion in some states has been used to shield officer identities

### 3.3 Records fragmentation

These records exist in different places, formats, and accessibilities:

- **Federal court records** (PACER, partially mirrored to RECAP by Free Law Project)
- **State court records** (variable; some online, some paper-only, some require in-person visits)
- **Civil settlement databases** (some cities publish; most don't)
- **Internal affairs files** (often sealed, sometimes by union contract)
- **Discipline records** (often destroyed on a schedule; NY 50-a sealed until 2020 repeal)
- **POST decertification lists** (state-by-state; some public, some not; aggregator: NDI database, IADLEST)
- **Use of force reports** (some departments publish; most don't)
- **Civilian complaint databases** (some independent boards publish; most don't)
- **DOJ pattern-and-practice reports** (public, but only ~60 departments have been investigated)
- **Federal consent decree monitor reports** (public, scattered)
- **State attorney general investigations** (variable disclosure)
- **Inspector general reports** (city-level, variable)
- **News archives** (paywalls, dead links, local newspaper collapse)
- **Court of appeals decisions** (public, but only the appealed cases)
- **Bar association complaints against prosecutors** (adjacent; for the Brady list logic)
- **Officer-involved shooting investigations** (variable; some states require independent investigation, some don't)
- **Body and dashboard camera footage** (release policies vary; some states require, some allow, some forbid)
- **911 call recordings** (variable)
- **Coroner / medical examiner reports** (death-in-custody cases; variable)
- **Asset forfeiture records** (variable)
- **Personnel files** (almost always sealed)
- **Polygraph and psychological screening records** (sealed)
- **Background investigation files** (sealed in most jurisdictions)
- **Officer training records** (sealed in most jurisdictions)
- **Off-duty employment records** (sealed)
- **Union arbitration awards** (some states publish, some don't)
- **Police union contracts** (mostly public; project to map them: Campaign Zero's Police Union Contract Project)
- **Fire-and-rehire records** (officers terminated and reinstated by arbitration)

### 3.4 Identity fragmentation

The hardest technical problem: **identifying which officer is which**.

- Officers in different departments may share names
- Officers move between departments
- Officers sometimes change legal names
- Spelling variations in source documents
- Misspellings in news reports
- Badge numbers are department-specific
- State POST IDs exist in some states, not others
- Court records use various forms of officer naming
- News reports rarely include badge numbers
- Officers' faces in video are not always identified by name
- Social media accounts (Plain View Project's terrain) often don't carry official identifiers

### 3.5 Temporal fragmentation

- Records destruction schedules vary
- Some states have mandatory expungement of older discipline
- News archive paywalls limit historical access
- Older records often paper-only
- Many departments have only recently begun systematic discipline tracking

---

## 4. Categories of misconduct the corpus should document

Not all "misconduct" — capture this with care. The corpus should be **descriptive** (what happened, by whose finding) rather than **categorical** (this is bad, this is good).

### 4.1 Use of force

- Fatal officer-involved shootings
- Non-fatal officer-involved shootings
- Officer-involved deaths in custody (asphyxiation, positional, in-custody medical neglect, "excited delirium" interventions)
- Taser deployments and Taser-associated deaths
- Less-lethal deployments (rubber bullets, beanbag rounds, foam batons, pepper spray, CS gas, flashbangs, sound cannons)
- K-9 deployments (especially non-bite escalations and bite injuries to bystanders)
- Vehicle pursuits and pursuit fatalities
- Vehicle intentional contact (PIT maneuvers, ramming)
- Strikes (with hands, knees, elbows, batons, flashlights)
- Chokeholds (formal and "incidental" carotid pressure)
- Knee-on-neck restraints
- Hogtying and prone restraints
- "Rough rides" / nickel rides in transport vehicles
- Strip searches (especially roadside, especially of minors)
- Body cavity searches
- Restraint asphyxia
- Hospital restraints (officers compelling forced medical procedures)

### 4.2 Investigative misconduct

- Coerced confessions
- False testimony (perjury) at trial or in warrants
- Fabricated evidence
- Suppressed exculpatory evidence (Brady violations)
- Forensic misconduct (when officers shape forensic narratives)
- Lying in police reports
- Improper interrogation of minors (Reid technique abuses, ignored requests for counsel)
- "Stash" planting (drugs, weapons)
- Falsified search warrants
- "Test cases" intentionally selected for harassment

### 4.3 Civil rights / equity patterns

- Traffic stop demographic disparities
- Stop-and-frisk demographic patterns
- Pretextual stops
- Consent search demographic disparities
- Bail recommendation patterns
- Patrol deployment by neighborhood
- Marijuana enforcement disparities pre/post-legalization
- DUI checkpoint placement
- Civil asset forfeiture by demographic
- Charges filed vs. dismissed by demographic
- Disability and mental health crisis response failures
- LGBTQ+ targeting (vice / public lewdness charges, ID checks)
- Religious profiling (post-9/11 surveillance, mosque surveillance)
- Immigration enforcement collaboration

### 4.4 Off-duty and personal conduct

- Domestic violence by officers (very high rates, very low conviction rates)
- DUI by officers (frequent dismissal)
- Off-duty discharge of firearms
- Off-duty fights / assaults
- Drug use (particularly steroids in some departments)
- Fraud and theft (sometimes from evidence rooms)
- Membership in extremist organizations (documented at FBI level)
- Public social media (the Plain View Project surface; also racist Facebook groups documented by various investigations)

### 4.5 Sexual misconduct

- On-duty sexual assault (a specific epidemic; the Cato Institute police misconduct project documented patterns)
- Coerced sexual contact under threat of arrest
- Sexual misconduct with minors
- Sexual misconduct with confidential informants
- Sexual misconduct with detainees
- Sexual harassment within departments
- The "rapist in uniform" pattern (Daniel Holtzclaw and others)
- The role of stops on women, sex workers, and trans women

### 4.6 Theft and corruption

- Drug evidence theft and resale
- Money skimming during raids
- Civil asset forfeiture conversion
- Time fraud / overtime fraud
- Off-duty work-conflict fraud
- Protection payments (organized historical patterns)
- Tip jar / extortion patterns

### 4.7 Failure to intervene

- Officers present at misconduct who did not stop it
- "Code of silence" / "blue wall" enforcement
- Retaliation against officers who broke the silence
- Whistleblower stories

### 4.8 Patterns at the department level

Not just individual officers. Departments themselves may have patterns:

- Discriminatory hiring or promotion
- Discriminatory training content
- Failure to discipline (the same officer repeatedly cleared)
- "Constitutional policing" failures (DOJ findings)
- Use of force policy weakness
- Failure to track / data integrity problems
- Failure to investigate complaints
- Failure to cooperate with civilian oversight
- Patterns of cover-up
- Patterns of pursuit-related deaths
- Patterns of in-custody deaths
- Patterns of suicide-by-cop fatal encounters
- Resistance to body camera requirements

### 4.9 Death in custody (its own category)

- In the cell (jail, prison, lockup)
- During arrest
- During transport
- In the hospital under custody
- Medical neglect cases
- Withdrawal-related deaths (alcohol, opioid withdrawal in jails)
- Mental health crisis deaths
- Suicide in custody (often disputed)
- The specific issue of restraint deaths
- Hot cell / cold cell deaths
- Failure to provide insulin / medication

### 4.10 Wandering officers

The pattern of officers moving between departments after misconduct, often termination or forced resignation, only to be hired elsewhere. USA Today's project documented many; the IADLEST National Decertification Index partially addresses this but participation is incomplete.

---

## 5. Existing efforts — to know, learn from, and not duplicate

### 5.1 The civic / nonprofit ecosystem

- **Invisible Institute (Chicago)** — the gold standard. Their work on CPDP (Citizens Police Data Project), the long-running Police Accountability Lawsuits docket, and FOIA litigation. Study their data model carefully.
- **Mapping Police Violence (Sam Sinyangwe and team)** — fatal police violence database, with extensive demographic data.
- **Fatal Encounters (D. Brian Burghart)** — long-running fatal incident database.
- **The Washington Post Fatal Force database** — fatal police shootings since 2015.
- **The Guardian's "The Counted"** (2015–2016) — paused but data persists.
- **The National Police Misconduct Reporting Project (Cato Institute)** — historical aggregation.
- **Plain View Project** — racist/violent social media posts by police, by department.
- **The Citizens Police Data Project** — Chicago, by Invisible Institute.
- **Lucy Parsons Labs** — surveillance and accountability work.
- **Open Police Project** — various municipal data work.
- **MuckRock** — FOIA infrastructure; many police records are FOIA'd here.
- **DocumentCloud** — where many released records get posted.
- **NCRP / National Police Accountability Project (NLG)** — civil rights litigators.
- **National Association of Police Accountability Boards** — coordinating civilian oversight.
- **Police Data Initiative** — federal-era initiative; partial participation.
- **Reveal from CIR** — investigative reporting.
- **Stanford's Big Local News and Stanford Open Policing Project** — traffic stops, especially.
- **The Marshall Project** — investigative coverage with structured reporting.
- **ProPublica** — including the NYPD personnel file database.

### 5.2 The academic ecosystem

- **Phil Stinson, Bowling Green State University, Henry A. Wallace Police Crime Database** — officers arrested for crimes
- **Stinson's lab also tracks decertification**
- **George Mason Center for Evidence-Based Crime Policy (CEBCP)**
- **John Jay College of Criminal Justice — Misconduct Database Project**
- **Stanford Computational Policy Lab**
- **University of Chicago Crime Lab**
- **NYU Policing Project**
- **The Policing Project / Yale Justice Collaboratory**
- **Vera Institute of Justice**
- **Urban Institute**
- **RAND Corporation policing research**

### 5.3 Government and quasi-government

- **DOJ Civil Rights Division pattern-and-practice investigations** (about 70 departments since 1994)
- **Federal consent decree monitors' reports**
- **IADLEST National Decertification Index (NDI)** — partial coverage; not all states participate
- **State POST commissions** (varies by state)
- **Civilian oversight boards** (city-by-city; coordination via NACOLE)
- **DOJ Office of Community Oriented Policing Services (COPS) reports**
- **Bureau of Justice Statistics**
- **FBI Uniform Crime Reports / NIBRS** (the *crime* side, but department-level)
- **Federal Bureau of Investigation Use-of-Force Data Collection** (the new system; participation incomplete)

### 5.4 The journalistic ecosystem

- **USA Today's "Wandering Officers" / Justice Watch**
- **Reuters' "Shielded by the Law"** (qualified immunity)
- **WNYC's NYPD files**
- **The New York Times' policing coverage and database work**
- **Local investigative newsrooms** (Texas Tribune, Cal Matters, Mississippi Today, etc.)
- **The Appeal**
- **Bolts magazine**
- **The Trace** (gun violence and policing overlap)
- **In These Times labor coverage of police unions**
- **Local newspaper archives** (more important than national for this corpus; many local stories are the only record)

### 5.5 International equivalents

- **UK: Independent Office for Police Conduct (IOPC)**, INQUEST (deaths in custody), Crest Advisory research
- **Canada: SIU (Ontario), IIO (BC)**, others by province
- **Australia: LECC (NSW)**, similar in other states; IBAC in Victoria
- **Northern Ireland: Police Ombudsman of NI** (excellent model)
- **Brazil: Fórum Brasileiro de Segurança Pública** documents police killings
- **Mexico: Causa en Común** and Article 19 document police violence
- **Nigeria: Network on Police Reform in Nigeria**
- **South Africa: IPID (Independent Police Investigative Directorate)**

The corpus could eventually be international, with US as anchor.

---

## 6. The normalization problem

This is the technical heart of the project. After 10,000 turns, you should have:

### 6.1 Officer-level entity resolution

A canonical record per officer, linked across:

- All employments (department, dates, rank, badge number, POST ID)
- All known names and aliases
- All known incident appearances
- All known lawsuits as defendant
- All known lawsuits as witness officer
- All known commendations
- All known discipline
- All known training
- All known criminal charges (against or by them)
- All known certifications and decertifications

### 6.2 Incident-level normalization

A canonical record per incident, linked to:

- All officers involved (and their roles)
- All civilians involved (with privacy protections appropriate to status)
- All weapons / force used
- All injuries / deaths
- All locations
- All subsequent processes (administrative review, criminal charges, civil suits)
- All settlements / outcomes
- All news coverage
- All body / dash camera footage references
- All medical examiner / coroner reports
- All public statements by department

### 6.3 Department-level normalization

A canonical record per department:

- Jurisdiction (geographic, legal)
- Size (officers, civilian staff, budget)
- Leadership history
- Union contracts (versions, terms)
- Use of force policy (versions, terms)
- Discipline procedures
- Civilian oversight (or absence)
- Pattern-and-practice findings
- Consent decree status
- Federal monitor reports
- All officers (current and historical)
- All incidents
- All lawsuits
- All settlements (with totals)
- All officer-involved deaths
- All decertification cases
- All wandering officers (inbound and outbound)

### 6.4 The lawsuit corpus

Federal civil rights cases (§1983) are public via PACER/RECAP. The corpus should:

- Map every officer named as defendant
- Map every allegation
- Map every claim type (excessive force, false arrest, malicious prosecution, denial of medical care, due process, retaliation, etc.)
- Map disposition (dismissed, summary judgment for defendant, settled, trial verdict, qualified immunity granted/denied)
- Map settlement amounts where public
- Map appellate history
- Map subsequent disciplinary action (or absence)
- Map subsequent employment for the officer

### 6.5 The settlement ledger

A normalized ledger of settlements:

- Date
- Plaintiff (anonymized as appropriate)
- Defendant officers
- Defendant department
- Underlying incident
- Amount
- Funding source (general fund, insurance, special fund)
- Conditions (NDA, no admission, etc.)
- Subsequent officer status
- Subsequent department response

A specific finding the corpus would enable: **the cost of an officer over time**, in actual dollars. The corpus could surface that a single officer cost their city $4M in settlements across nine cases. This finding is currently extraordinarily difficult to surface and is exactly the kind of fact accountability requires.

### 6.6 The Brady/Giglio dimension

In many counties, prosecutors maintain a list of officers whose credibility issues require disclosure to defense in any case they testify in. These lists are usually secret. Some have been forced public (San Francisco, Philadelphia, others) by litigation. The corpus should:

- Identify officers known to be on Brady lists
- Cross-reference with subsequent testimony
- Identify cases where Brady disclosure was demanded
- Identify cases where it appears to have been withheld

### 6.7 The temporal dimension

- Officer career timelines visualized
- Department incident timelines
- Reform timelines (when did this department adopt body cameras; when did the use-of-force policy change; when did the consent decree end)
- Comparison: officers' careers across reform periods

---

## 7. Specific projects ChatGPT might not consider

### 7.1 The recursive officer search

Given any officer's name and department, the corpus should return:
- All other names they've used in any record
- All other departments
- All known incidents
- All lawsuits
- All discipline
- All news coverage
- Risk indicators (multiple departments in short period, multiple uses of force, multiple lawsuits, etc.)

This is what no current product offers comprehensively.

### 7.2 The "wandering" detector

An automated alerting system: given a recent hiring announcement (often published in local news), check whether the hired officer has a record of misconduct in any prior department. This is the value proposition behind IADLEST NDI but is incomplete because participation is voluntary.

### 7.3 The settlement-per-department aggregator

For any department, total settlement dollars per year, per officer, per incident type. This is currently knowable only with massive FOIA effort city by city.

### 7.4 The repeat-defendant tracker

The pattern of the same officer or officers being repeatedly sued. The corpus should make this visible.

### 7.5 The federal monitor archive

Many departments are or have been under federal monitoring. Monitor reports are public but scattered. The corpus should archive all of them, mapped to the cited departments and officers.

### 7.6 Use of force policy archive

Department policies on use of force have evolved enormously. The corpus should:
- Archive policies as they existed at specific dates
- Map incidents to the policy in effect at the time
- Track policy changes after notable incidents
- Compare across departments (the Campaign Zero "8 Can't Wait" work was a partial start)

### 7.7 Union contract archive

Police union contracts often contain provisions that limit accountability (mandatory waiting periods, record destruction schedules, arbitration rights, mandatory unionizing of supervisors). Campaign Zero's Police Union Contract Project started this work. The corpus should:
- Archive all police union contracts as they evolve
- Tag specific provisions
- Cross-reference with discipline outcomes

### 7.8 The arbitration tracker

When officers are terminated, they often appeal to arbitration. Arbitrators frequently reinstate them. The Washington Post and others have documented this. The corpus should:
- Track all reinstatements by arbitration
- Identify arbitrators who repeatedly reinstate
- Map subsequent officer conduct after reinstatement

### 7.9 The "officer killed" corpus

Officers killed in the line of duty are tracked relatively well (Officer Down Memorial Page, FBI Law Enforcement Officers Killed and Assaulted). The corpus should integrate this for full picture:
- Genuine line-of-duty deaths
- Officers killed by other officers (mistaken identity, friendly fire, intentional)
- Officer suicides (often categorized separately, often higher than line-of-duty deaths)
- The causes (gunfire, vehicular, medical, etc.)

This matters because honest accountability includes context, and the violence officers face is part of the system.

### 7.10 The civil society linkage

The corpus should be connected to:
- Active investigations by accountability orgs
- Active litigation by civil rights firms
- Active campaigns by community organizations
- Ongoing journalism

So that any new entry can flow to the people who can use it.

### 7.11 The cross-system view

Police misconduct intersects with:
- Prosecutorial misconduct (National Registry of Exonerations)
- Judicial misconduct
- Public defender failures
- Jail/prison guard misconduct
- ICE/CBP misconduct
- School resource officer misconduct
- Court bailiff misconduct
- Private security misconduct
- Federal agency misconduct (DEA agents, FBI agents, etc.)

A truly powerful corpus would extend; the police corpus could be the wedge.

---

## 8. Edge cases the builder should plan for explicitly

- **Officers in small departments.** Most academic and journalistic attention goes to large departments. Most US officers are in small departments. The corpus needs to reach Sheriff's departments with 8 deputies in rural counties.
- **Sheriff vs. police chief structures.** Sheriffs are elected; they have different accountability dynamics than appointed chiefs.
- **Constables.** In some states, constables are elected with arrest powers and minimal training.
- **Reserve officers and auxiliaries.** Often part-time, often less trained.
- **Campus police.** Often armed, often empowered, often opaque.
- **Tribal police.** Federal/tribal/state jurisdictional complications.
- **Federal officers.** ICE, CBP, Border Patrol, USMS, others — often outside state oversight entirely.
- **Privatized law enforcement.** Mall cops, port authority, railroad police — varying powers and accountability.
- **Off-duty officers working as security.** Their conduct is often informally policed.
- **The "deputized" private actors.** Citizen's arrest, deputized contractors, etc.

### 8.1 The civilian side of incidents

The corpus must be deeply thoughtful about the civilians involved:

- **Victims' families have ownership of their stories.** Don't extract.
- **Witnesses sometimes face retaliation.** Identification matters.
- **People who were arrested for non-criminal reasons.** Often their record persists even when the arrest was unlawful.
- **The dead can't consent but the living can decide what to share about them.**
- **Minors should rarely be named.**
- **People in mental health crisis.** Their dignity should be preserved.
- **Sex workers, undocumented people, others structurally vulnerable.** Their stories deserve documentation; their identities deserve protection.

### 8.2 Cases of exoneration

The corpus should distinguish:
- Sustained complaints (department found misconduct)
- Unsustained complaints (insufficient evidence either way)
- Exonerated (department found officer acted lawfully)
- Unfounded (department found incident didn't happen)
- Settled (no admission of wrongdoing)
- Reversed on appeal
- Cleared by grand jury
- Charged but acquitted

Each of these has different epistemic weight and the corpus should make that visible.

### 8.3 Officer due process

The corpus must respect:
- Officers under investigation but not adjudicated
- Officers cleared after investigation
- Officers exonerated at trial
- Officers whose records were sealed by statute

There is a tension between accountability (which requires visibility) and due process (which requires care). The corpus should make this tension explicit, not pretend it doesn't exist.

---

## 9. Schema (illustrative)

### 9.1 Officer record

- Canonical name
- Aliases / spelling variants
- Date of birth (year only for privacy)
- Race/gender (self-reported when available)
- Employment history (department, dates, rank, badge, POST ID, separation reason)
- Education / training
- Certifications and decertifications
- Commendations
- Discipline (date, type, outcome, basis)
- Incidents involved in
- Lawsuits named in
- Settlements involving them
- Criminal charges (against)
- Brady/Giglio status (where known)
- Social media (Plain View Project style, where public)

### 9.2 Incident record

- Date, time, location
- Type (use of force, search, arrest, traffic stop, custody death, etc.)
- Officers involved (linked to officer records)
- Civilians involved (anonymized as appropriate)
- Injuries / fatalities
- Weapons / force used
- Body camera / dash camera (yes/no/released)
- 911 audio (yes/no/released)
- Subsequent administrative review (outcome)
- Criminal investigation (outcome)
- Civil lawsuit (linked)
- Settlement (linked)
- Department public statement (linked)
- News coverage (linked)
- Initial coding date and updates

### 9.3 Department record

- Name, jurisdiction, size, budget
- Leadership history
- Union contract (versions linked)
- Use of force policy (versions linked)
- Discipline procedures
- Civilian oversight body (linked)
- Pattern-and-practice investigations (linked)
- Consent decrees (linked)
- All officers (linked)
- All incidents (linked)
- All settlements (linked, with running total)
- Decertifications associated

### 9.4 Lawsuit record

- Case number (PACER / state equivalent)
- Court
- Filing date
- Plaintiffs (anonymized as appropriate)
- Defendant officers (linked)
- Defendant department (linked)
- Claim types
- Underlying incident (linked)
- Procedural history
- Disposition
- Settlement amount (if applicable)
- Appellate history
- Counsel (plaintiff and defendant)

### 9.5 News coverage

- Article URL
- Publication
- Date
- Reporter
- Officers mentioned (linked)
- Departments mentioned (linked)
- Incidents mentioned (linked)
- Source citations

---

## 10. Ethical foundations

The corpus must be built on:

- **Verifiability.** Every claim traces to a primary source.
- **Distinction between allegation, finding, settlement, and adjudication.** Never collapse these.
- **Officer due process.** Pending investigations are marked as such.
- **Civilian privacy.** Especially for minors, mental-health-crisis subjects, sexual assault survivors, the dead's family wishes.
- **Update obligations.** When records are amended (sustained → unsustained on appeal, etc.), the corpus must update.
- **Right of reply.** Officers and departments should have a process to contest entries.
- **Open access to the underlying data wherever law allows.** The corpus should not become a paywalled tool.
- **No use by police themselves to target individuals.** Access models matter.
- **Indigenous and immigrant communities consulted on their own data.** They are most often the subjects; they should not just be the data.
- **Family member ownership of incident narratives.** The corpus records what happened publicly; it does not own the narrative of any loss.
- **The corpus is for accountability, not for revenge.** The tone must hold.

---

## 11. What "done well" looks like at scale

After 10,000 turns:

- A renter in any US city can look up the department covering their address and see settlement history per capita.
- A defense lawyer can look up any officer testifying in their case and see all prior credibility issues.
- A journalist can map any officer's career across departments.
- A community organizer can identify the 1% of officers responsible for the disproportionate share of force or complaints in their city.
- A federal monitor can compare baseline against current state across the consent decree population.
- A researcher can study the diffusion of policy changes across departments after notable incidents.
- A city council member can compare their department's discipline outcomes to peer departments.
- A POST commissioner can identify officers seeking certification in their state who were decertified elsewhere.
- A bereaved family can locate every reference to their loved one's death across news, court records, and official reports — in one place.

The most important thing the corpus does: **make wandering impossible.** A national, normalized, accessible record of misconduct means there is nowhere for an officer who has demonstrated serious misconduct to disappear to and re-emerge unobserved. The corpus's *existence* changes hiring behavior, even before any specific lookup.

---

## 12. Concrete adversarial considerations

The corpus will face:

- **FOIA denial campaigns.** Departments and unions actively contest disclosure.
- **Defamation suits.** Officers and unions sue records-keepers and journalists. Insurance exists for this; legal infrastructure must.
- **Doxing concerns.** Officers and families have been targeted by people misusing public records. The corpus should not enable this; access and presentation choices matter.
- **Manipulation attempts.** Officers under investigation may try to seed corrections to the corpus.
- **Politicization.** The corpus will be attacked from both ends; both attacks should be expected.
- **Sustainability.** Most accountability projects collapse under cost. Funding model matters; civic, foundation, and possibly academic hosting is more viable than commercial.
- **Volunteer burnout.** This is grim work. The team needs to be paced.
- **Cross-jurisdictional FOIA tactics.** Different states yield to different pressures.

---

## 13. The corpus as infrastructure

Done well, this is not a database. It is the public-records substrate that *every* downstream accountability project should be able to use. Mapping Police Violence, Invisible Institute, USA Today, ACLU, local newsrooms — they should all be able to ingest from and contribute back to the same canonical corpus. That is the realistic ambition: not to replace the existing ecosystem, but to give it the spine it does not currently have.

---

## 14. Specific things ChatGPT (or any builder) might miss

- **Constable courts and justices of the peace** still operate in parts of the US with arrest powers and minimal accountability.
- **The polygraph/CVSA market** that some departments use for pre-employment screening is itself a fraud-prone industry.
- **Officer suicide** is higher than line-of-duty deaths; relevant context and a sobering moral fact.
- **The "deconfliction" databases** that exist among federal agencies and some local task forces (e.g., RISS, HIDTA) operate with minimal civilian oversight.
- **The fusion center system** post-9/11 — a parallel intelligence apparatus with thin accountability.
- **License plate readers, Stingrays, Ring partnerships, facial recognition contracts** — surveillance infrastructure that interacts with misconduct in subtle ways.
- **The "list system"** — gang databases, watch lists, focused-deterrence lists — often racially skewed, often opaque.
- **Forensic units** in some departments (especially crime labs, sometimes separately governed) have their own misconduct corpora (Houston Crime Lab, Massachusetts state lab Dookhan/Farak, Annie Dookhan and Sonja Farak cases). These belong adjacent to the police corpus.
- **The role of police informants** in misconduct (Rachel Hoffman, Confidential Informant deaths).
- **Officer-on-officer abuse.** Departments are also workplaces; harassment, retaliation, racism, and sexism within departments are part of the picture and often visible only in EEOC complaints, internal lawsuits, and arbitration awards.
- **Pension implications.** Some discipline outcomes turn on pension protection. Following the money — pension records — sometimes reveals what discipline records will not.
- **Death notification practices.** How families are told of a relative's death by police is itself a documented site of harm.
- **Property released to "next of kin"** practices are often opaque; missing personal effects from in-custody death incidents have generated lawsuits.
- **The role of the medical examiner** in shaping the official narrative. ME independence varies; some are part of the police department.

---

## 15. A note on language

The corpus should use **the most precise available language** for everything:

- "Officer-involved shooting" is a phrase the corpus might examine but probably shouldn't reproduce, since "involved" obscures who shot whom.
- "Police-involved" obscures agency.
- "Resisting arrest" is a charge sometimes added when force was used to justify it; the corpus should flag this pattern.
- "Excited delirium" is a contested term; the corpus should document its use without endorsing it.
- "Less-lethal" is an industry term; "less-than-lethal" is sometimes more honest; the corpus should be specific about what was deployed.
- "Use of force continuum" terminology varies by department; the corpus should not flatten.
- "Code of silence" / "blue wall" — useful descriptors when documented behavior matches.
- "Bad apples" — a defensive trope the corpus exists to interrogate.

The corpus is a record. It is not an argument. The data, well-presented, makes the argument.

---

## 16. The corpus as a possibility space

At scale, this corpus would unlock:

- Empirical study of qualified immunity (cases where it was granted vs. denied, with full incident records)
- Empirical study of consent decree effectiveness
- Empirical study of body camera adoption effects
- Empirical study of police union contract provisions and their downstream effects
- Empirical study of civilian oversight effectiveness
- Identification of the *small percentage of officers* responsible for the large percentage of force/complaints (this finding is robust across many cities; the corpus would make it universal)
- Identification of the small percentage of *neighborhoods, intersections, and times* where most misconduct occurs
- Identification of the small percentage of *supervisors* under whom misconduct concentrates
- Honest cost accounting of policing including the externalities of litigation and settlement

The corpus answers an old question: **if you actually had the data, what would change?**

The answer is: everything that was already known anecdotally becomes provable, contestable, addressable. The corpus is a tool for democracy.
