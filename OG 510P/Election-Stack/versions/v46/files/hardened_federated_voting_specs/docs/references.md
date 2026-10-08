# References (annotated, selected)

This pack prioritizes **primary sources**: government guidance, standards/RFCs, and peer‑reviewed papers.

## Public guidance: election security, ballot return risk, certification
- **EAC — End‑to‑End (E2E) Protocol Evaluation Process** (public process to solicit/evaluate/approve E2E verifiable voting protocols intended for VVSG 2.0 certification):  
  https://www.eac.gov/voting-equipment/end-end-e2e-protocol-evaluation-process
- **EAC — VVSG 2.0 Test Assertions v1.4** (Jan 30, 2026):  
  https://www.eac.gov/sites/default/files/2026-01/VVSG_2.0_Test_Assertions_v1.4.pdf
- **CISA / EAC / FBI / NSA — Risk Management for Electronic Ballot Delivery, Marking, and Return** (May 8, 2020; electronic return rated High risk even with safeguards):  
  https://www.cisa.gov/sites/default/files/2024-02/Final_%20Risk_Management_for_Electronic-Ballot_05082020_508c.pdf
- **NIST — Voting security recommendations** (includes warnings about internet exposure of election management components):  
  https://www.nist.gov/itl/voting/security-recommendations
- **EAC — Checklist for Securing Election Night Results Reporting (ENR)**:  
  https://www.eac.gov/sites/default/files/electionofficials/postelection/Checklist_for_Securing_Election_Results_FINAL_EAC.pdf
- **NIST — Election Night Reporting (ENR) use case / security discussion**:  
  https://www.nist.gov/itl/voting/security-election-night-reporting
- **IFES — Briefing Paper: Cybersecurity of Election Results Management Systems**:  
  https://www.ifes.org/sites/default/files/2023-06/Briefing_paper_2_Election_Results_Management.pdf

- **National Academies — Securing the Vote: Protecting American Democracy** (highlights; emphasizes human‑readable paper ballots + RLAs):  
  https://nap.nationalacademies.org/resource/25120/Securing%20the%20Vote%20ReportHighlights.pdf

## E2E verifiability: implementations and research
- **ElectionGuard — official specifications**:  
  https://electionguard.vote/spec/
- **Benaloh et al. (USENIX Security 2024) — ElectionGuard toolkit paper**:  
  https://www.usenix.org/system/files/usenixsecurity24-benaloh.pdf
- **Jensen et al. (2024) — Verifying ElectionGuard: a theoretical and empirical analysis** (verification ergonomics and auditability concerns):  
  https://dl.gi.de/bitstreams/3ccf93da-be4b-4626-9e8c-5c2d9dcfd0ea/download
- **Adida (USENIX Security 2008) — Helios: Web‑based Open‑Audit Voting**:  
  https://www.usenix.org/event/sec08/tech/full_papers/adida/adida.pdf
- **Real‑World E‑Voting book** (chapters with practical notes; Helios chapter):  
  https://realworldevoting.com/files/Chapter11.pdf

## Coercion resistance / revoting
- **Lueks et al. (USENIX Security 2020) — VoteAgain** (revoting paradigm; explicit assumptions):  
  https://www.usenix.org/system/files/sec20-lueks.pdf

## Remote voting case studies and security analyses
- **Specter & Halderman (MIT, 2020) — OmniBallot analysis**:  
  https://internetpolicy.mit.edu/wp-content/uploads/2020/06/OmniBallot.pdf
- **Specter & Halderman (USENIX Security 2021) — Democracy Live online voting system analysis**:  
  https://www.usenix.org/system/files/sec21-specter-security.pdf
- **Springall et al. (ACM CCS 2014) — Estonian i‑voting security analysis**:  
  https://jhalderm.com/pub/papers/ivoting-ccs14.pdf
- **Swiss Federal Chancellery (2019) — Swiss Post universal‑verifiability flaw disclosure** (illustrates complexity):  
  https://www.news.admin.ch/en/nsb?id=74307
- **Park, Specter, Narula, et al. (OUP Cybersecurity, 2021) — “Going from bad to worse: from Internet voting to blockchain voting”**:  
  https://academic.oup.com/cybersecurity/article/7/1/tyaa025/6137886

## Transparency log patterns
- **RFC 9162 — Certificate Transparency v2** (Merkle inclusion/consistency proofs; Signed Tree Heads):  
  https://www.rfc-editor.org/rfc/rfc9162.html
- **Transparent Logs for Skeptical Clients** (design notes on verifiable tamper‑evident logs):  
  https://research.swtch.com/tlog

### Gossip, witness cosigning, and split-view resistance
- **Chuat et al. (2015)** — *Efficient Gossip Protocols for Verifying the Consistency of Certificate Transparency Logs*:  
  https://arxiv.org/pdf/1511.01514
- **Oxford et al. (2020/2021)** — Quantitative verification of CT gossip protocols (model checking / split-world analysis):  
  https://www.prismmodelchecker.org/papers/spc20.pdf
- **Syta et al. (2015)** — *Keeping Authorities “Honest or Bust” with Decentralized Witness Cosigning* (CoSi):  
  https://arxiv.org/pdf/1503.08768
- **Sigsum** — Design notes: proactive gossip + witness cosigning; cosigned tree heads:  
  https://git.sigsum.org/sigsum/plain/doc/design.md?id=bb118ec24bea9de70ea0b3858e8f89badfe12023
- **Transparency.dev (2024)** — “Can I Get a Witness (Network)?” (witness cosigning deployment considerations):  
  https://blog.transparency.dev/can-i-get-a-witness-network
- **Parakeet (NDSS 2023)** — consensus-less non-equivocation + censorship resistance/read-freshness for key transparency:  
  https://www.ndss-symposium.org/wp-content/uploads/2023-545-paper.pdf
- **Apple Security Blog (2023)** — iMessage Contact Key Verification (gossiping log hashes to detect split views):  
  https://security.apple.com/blog/imessage-contact-key-verification/

## Software + supply‑chain integrity
- **NIST SP 800‑218 (SSDF) — Secure Software Development Framework v1.1**:  
  https://csrc.nist.gov/pubs/sp/800/218/final
- **NIST SP 800‑218r1 (IPD) — SSDF v1.2 draft** (in progress):  
  https://csrc.nist.gov/pubs/sp/800/218/r1/ipd
- **NIST SP 800‑161r1 — Cybersecurity Supply Chain Risk Management Practices**:  
  https://csrc.nist.gov/pubs/sp/800/161/r1/final
- **TUF specification (latest)** (secure updates even if repo/keys compromised):  
  https://theupdateframework.github.io/specification/latest/
- **in‑toto (USENIX Security 2019)** — end‑to‑end supply‑chain integrity framework:  
  https://www.usenix.org/system/files/sec19-torres-arias.pdf
- **SLSA v1.0 spec** (levels + provenance; see status notes on the site):  
  https://slsa.dev/spec/v1.0/

## Post-quantum cryptography (PQC)
- **NIST FIPS 203 — ML-KEM** (final):
  https://csrc.nist.gov/pubs/fips/203/final
- **NIST FIPS 204 — ML-DSA** (final):
  https://csrc.nist.gov/pubs/fips/204/final
- **NIST FIPS 205 — SLH-DSA** (final):
  https://csrc.nist.gov/pubs/fips/205/final
- **NIST News (Aug 13, 2024; updated Aug 29, 2025)** — first three finalized PQC standards:
  https://www.nist.gov/news-events/news/2024/08/nist-releases-first-3-finalized-post-quantum-encryption-standards

## Coercion-resistance research (fake credentials, definitions, critiques)
- **Cortier et al. (IEEE CSF 2024)** — *Is the JCJ voting system really coercion-resistant?* (analyzes coercion-resistance limits and leakages):
  https://members.loria.fr/VCortier/files/Papers/CSF2024.pdf
- **Juels, Catalano, Jakobsson (WPES 2005)** — *Coercion-Resistant Electronic Elections* (foundational definition; many descendants):
  https://www.cs.rice.edu/~scrosby/pubs/voting/jcj.pdf
- **Haines & Smyth (2019)** — *SoK: Surveying definitions of coercion resistance*:
  https://publications.bensmyth.com/files/Smyth19-surveying-coercion-resistance.pdf
- **Clarkson et al. (Cornell, 2008)** — *Civitas: Toward a Secure Voting System* (remote voting with coercion-resistance; heavy machinery):
  https://www.cs.cornell.edu/projects/civitas/papers/clarkson_civitas.pdf
- **Iovino et al. (2017)** — *Using Selene to Verify your Vote in JCJ*:
  https://fc17.ifca.ai/voting/papers/voting17_MainJCJ-Selene.pdf

## International standards / observation guidance
- **OSCE/ODIHR (2025)** — *Opinion on the regulation of internet voting, Estonia*:
  https://www.osce.org/sites/default/files/f/documents/e/a/593435.pdf
- **OSCE/ODIHR (2024)** — *Handbook for the Observation of ICT in Elections*:
  https://www.osce.org/sites/default/files/f/documents/c/9/558318_0.pdf
- **OSCE/ODIHR (2013)** — *Handbook for the Observation of New Voting Technologies*:
  https://www.osce.org/odihr/elections/new_voting_technologies
- **Council of Europe (2017)** — Recommendation **CM/Rec(2017)5** on standards for e-voting:
  https://search.coe.int/cm/Pages/result_details.aspx?ObjectId=0900001680726f6f
- **European Commission (2023)** — *Compendium of e-voting and other ICT practices*:
  https://commission.europa.eu/system/files/2023-12/compendium.pdf

## Risk-limiting audits (RLA)
- **NIST (Lindeman & Stark)** — *A Gentle Introduction to Risk-Limiting Audits*:
  https://www.nist.gov/document/gentle-introduction-risk-limiting-audits
- **Democracy Fund (Morrell, 2019)** — *Knowing It's Right: A Practical Guide to RLAs*:
  https://democracyfund.org/wp-content/uploads/2020/06/2019_DF_KnowingItsRight_Part1.pdf
- **American Statistical Association (2018)** — *Principles and Best Practices for Post-Election Tabulation Audits*:
  https://www.amstat.org/docs/default-source/amstat-documents/audit-principles-and-best-practices-2018.pdf


## Secure time, ordering, and public randomness
- **IETF draft — Roughtime (secure rough time synchronization)** (Dec 17, 2025):  
  https://www.ietf.org/archive/id/draft-ietf-ntp-roughtime-15.html
- **Roughtime (reference implementation / docs)**:  
  https://roughtime.googlesource.com/roughtime
- **NIST — Interoperable Randomness Beacons / Beacon 2.0** (service overview):  
  https://csrc.nist.gov/projects/interoperable-randomness-beacons  
  https://csrc.nist.gov/projects/interoperable-randomness-beacons/beacon-20
- **NIST news — revise key establishment recommendations (SP 800-56A/56C)** (Jan 6, 2026):  
  https://csrc.nist.gov/News/2026/nist-to-revise-key-establishment-recommendations

## Traffic analysis and metadata leakage in online voting
- **Belousova et al. — Inference Attacks on Encrypted Online Voting via Traffic Analysis** (arXiv, Sep 2025):  
  https://arxiv.org/abs/2509.15694
- **Brunet et al. — When Confirmation Pages Break Ballot Secrecy in Online Voting** (2022):  
  https://link.springer.com/chapter/10.1007/978-3-031-15911-4_3

## Coercion / vote buying attacks and mitigations
- **Kelsey et al. (NIST et al.) — Attacking Paper-Based E2E Voting Systems**:  
  https://csrc.nist.rip/staff/jkelsey/attacking-e2e-voting-systems.pdf
- **Ryan — Risk-Limiting Tallies / masking approaches**:  
  https://orbilu.uni.lu/bitstream/10993/57235/1/RLT_Rvisited.pdf

## Case studies: real internet voting systems
- **Debant et al. — Reversing, Breaking, and Fixing the French Legislative Internet Voting System** (USENIX Security 2023):  
  https://www.usenix.org/system/files/usenixsecurity23-debant.pdf

## Verification usability
- **Jensen et al. — Verifying ElectionGuard: a theoretical and empirical analysis** (2024):  
  https://dl.gi.de/bitstreams/3ccf93da-be4b-4626-9e8c-5c2d9dcfd0ea/download

## Transparency logs (general)
- **RFC 9162 — Certificate Transparency Version 2.0**:  
  https://datatracker.ietf.org/doc/html/rfc9162

## Digital credentials / authenticators (citizen keys)
- **W3C — Web Authentication: An API for accessing Public Key Credentials (WebAuthn) Level 3** (Jan 13, 2026):  
  https://www.w3.org/TR/webauthn-3/
- **FIDO Alliance — Specifications** (overview and links to FIDO2/WebAuthn-related standards):  
  https://fidoalliance.org/specifications/

## Deployed internet voting: Estonia verification (official guidance)
- **Elections in Estonia — Stages of i-voting in voter application** (official step-by-step):  
  https://www.valimised.ee/en/internet-voting/guidelines/stages-i-voting-voter-application
- **Elections in Estonia — Checking of an i-vote** (verification app guidance):  
  https://www.valimised.ee/en/internet-voting/guidelines/checking-i-vote

## Deployed internet voting: Norway pilots (observation / analysis)
- **The Carter Center — Internet Voting Pilot: Norway’s 2013 Parliamentary Elections (Expert Study Mission Report)** (Mar 19, 2014):  
  https://www.regjeringen.no/globalassets/upload/KRD/Kampanjer/valgportal/valgobservatorer/2013/Rapport_Cartersenteret2013.pdf
- **Puigallí Allepuz et al. — Cast-as-Intended Verification in Norway** (analysis of verification design):  
  https://dl.gi.de/bitstreams/41b49dc3-7192-4d21-9371-c190472e7662/download

## Internet routing / BGP hijack resilience
- **NRO — RPKI best practices and lessons learned** (Sep 2025):  
  https://www.nro.net/technical-coordination/nro-rpki-program/rpki-best-practices-and-lessons-learned/
- **IETF SIDROPS draft — Risk of Stealthy BGP Hijacking under Incomplete Adoption of ROV** (work in progress):  
  https://datatracker.ietf.org/doc/draft-li-sidrops-stealthy-hijacking/

## Privacy-preserving submission (metadata reduction)
- **RFC 9458 — Oblivious HTTP (OHTTP)** (Jan 2024):  
  https://www.ietf.org/rfc/rfc9458.html
- **RFC 9230 — Oblivious DNS over HTTPS (ODoH)** (Jun 2022):  
  https://www.rfc-editor.org/rfc/rfc9230.html

## Anonymous rate limiting / anti-abuse
- **RFC 9577 — Privacy Pass HTTP Authentication Scheme** (Jun 2024):  
  https://www.rfc-editor.org/info/rfc9577
- **IETF draft — Privacy Pass ARC (Anonymous Rate-Limited Credentials)** (work in progress):  
  https://datatracker.ietf.org/doc/draft-privacypass-arc-protocol/

## Web authentication / phishing-resistant credentials
- **W3C — Web Authentication: An API for accessing Public Key Credentials (Level 3)** (Jan 13, 2026):  
  https://www.w3.org/TR/webauthn-3/

## Key / Parameter transparency (key distribution patterns)
- **IETF draft — Key Transparency Protocol** (Oct 2025):
  https://datatracker.ietf.org/doc/draft-ietf-keytrans-protocol/
- **IETF draft — Key Transparency Architecture** (Jul 2025):
  https://datatracker.ietf.org/doc/draft-ietf-keytrans-architecture/

## External transparency logs / notarization
- **Sigstore Rekor — transparency log overview**:
  https://docs.sigstore.dev/logging/overview/
- **OpenSSF — Sigstore transparency log research dataset (2025)**:
  https://openssf.org/blog/2025/10/15/announcing-the-sigstore-transparency-log-research-dataset/

## Threshold cryptography (standardization/validation guidance)
- **NIST IR 8214 — Threshold Schemes for Cryptographic Primitives** (Mar 2019):
  https://nvlpubs.nist.gov/nistpubs/ir/2019/NIST.IR.8214.pdf

## Standards and specs: canonicalization, common data formats
- **RFC 8785 — JSON Canonicalization Scheme (JCS)** (deterministic, hashable JSON representation):  
  https://www.rfc-editor.org/rfc/rfc8785
- **NIST SP 1500-20 — Ballot Definition Common Data Format Specification** (BD CDF):  
  https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.1500-20.pdf
- **NIST GCR 24-058 — Implementation Guidance for Common Data Formats** (BD/CVR/VRI/ERR processing and cross-referencing):  
  https://nvlpubs.nist.gov/nistpubs/gcr/2024/24-058/NIST.GCR.24-058.html
- **NIST SP 1500-100r2 — Election Results Reporting Common Data Format** (ERR CDF):  
  https://doi.org/10.6028/NIST.SP.1500-100r2
- **NIST SP 1500-101 — Election Event Logging Common Data Format** (EEL CDF):  
  https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.1500-101.pdf

## Results privacy / tally hiding / disclosure

- **Huber et al. (ACM CCS 2022 / IACR) — Kryvos: Publicly Tally-Hiding Verifiable E-Voting** (discusses Italian/pattern attacks and tally hiding):  
  https://publ.sec.uni-stuttgart.de/huberkuesterskripsliedtkemuellerrauschreisert-ccs-2022.pdf

## Registration / credentialing coercion resistance

- **Merino et al. (ACM CCS 2025) — TRIP: Coercion-resistant Registration for E-Voting with ...**:  
  https://www.cydcampus.admin.ch/dam/fr/sd-web/zfXK8IOdglF5/3731569.3764837.pdf

## Differential privacy evaluation guidance (for election-adjacent data)

- **NIST (2025) — Finalized guidelines for evaluating differential privacy guarantees** (DP claims evaluation):  
  https://www.nist.gov/news-events/news/2025/03/nist-finalizes-guidelines-evaluating-differential-privacy-guarantees-de

## Post-quantum cryptography (PQC) — direct standards

- **NIST FIPS 204 (final) — ML-DSA**:  
  https://csrc.nist.gov/pubs/fips/204/final
- **NIST FIPS 205 (final) — SLH-DSA**:  
  https://csrc.nist.gov/pubs/fips/205/final


## Registration / VRDB / supply chain / identity / privacy partitioning
- NIST: Security of Voter Registration Databases — https://www.nist.gov/itl/voting/security-voter-registration-databases
- CISA: Securing Voter Registration Data (Dec 2023) — https://www.cisa.gov/sites/default/files/2023-12/securing_voter_registration_data_508_12.20.23_tz.pdf
- NIST: Cybersecurity Framework Election Infrastructure Profile (NIST VTS 200-1, 2024) — https://nvlpubs.nist.gov/nistpubs/vts/NIST.VTS.200-1.pdf
- CISA: Supply Chain Risks to Election Infrastructure — https://www.cisa.gov/sites/default/files/publications/supply-chain-risks-to-election-infrastructure_508.pdf
- NIST: SP 800-161r1 — Cybersecurity Supply Chain Risk Management Practices for Systems and Organizations (final) — https://csrc.nist.gov/pubs/sp/800/161/r1/final
- NIST: Digital Identity Guidelines (SP 800-63-4, 2025) — https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-63-4.pdf
- RFC 9458: Oblivious HTTP — https://www.ietf.org/rfc/rfc9458.html
- RFC 9230: Oblivious DNS over HTTPS — https://www.rfc-editor.org/rfc/rfc9230.html
- RFC 9577: Privacy Pass HTTP Authentication Scheme — https://datatracker.ietf.org/doc/rfc9577/
- RFC 8785: JSON Canonicalization Scheme — https://www.rfc-editor.org/rfc/rfc8785

## Exercises / incident response / communications
- CISA: Election Security — CISA Tabletop Exercise Packages (CTEPs) — https://www.cisa.gov/resources-tools/resources/election-security-cisa-tabletop-exercise-packages-cteps
- EAC: Incident Response Checklist (Clearinghouse) — https://www.eac.gov/sites/default/files/electionofficials/security/Incident_Response_Checklist_508.pdf
- CISA/EAC: Election Infrastructure Incident Response Communications Guide (Oct 2024) — https://www.eac.gov/sites/default/files/2024-10/Election_Infrastructure_Incident_Response_Comms_Guide_508.pdf
- Belfer Center: Election Cyber Incident Communications Plan Template — https://www.belfercenter.org/publication/election-cyber-incident-communications-plan-template

## WebAuthn / passkeys / authenticators
- W3C Web Authentication (WebAuthn) Level 3 (TR) — https://www.w3.org/TR/webauthn-3/
- FIDO Alliance: Passkeys overview — https://fidoalliance.org/passkeys/
- FIDO Alliance (2025): Passkeys white paper series (phishing prevention journey) — https://fidoalliance.org/white-paper-passkeys-the-journey-to-prevent-phishing-attacks/

## Mobile Driver’s License (mDL)
- ISO/IEC 18013-5:2021 (mDL interfaces) — https://www.iso.org/standard/69084.html


## Verification / observer guidance
- RFC 6962: Certificate Transparency (original) — https://www.rfc-editor.org/rfc/rfc6962.html
- OSCE/ODIHR (2013): Handbook for the Observation of New Voting Technologies (PDF) — https://www.osce.org/sites/default/files/f/documents/0/6/104939.pdf
- OSCE/ODIHR (2024): Handbook for the Observation of ICT in Elections (PDF) — https://www.osce.org/sites/default/files/f/documents/c/9/558318_0.pdf
- ElectionGuard: Election Record documentation — https://electionguard.vote/develop/Election_Record/
- ElectionGuard: Official specifications — https://electionguard.vote/spec/
- ElectionGuard Verifier (reference implementation) — https://github.com/Election-Tech-Initiative/electionguard-verifier
- MITRE ElectionGuard Verifier (Julia) — https://mitre.github.io/ElectionGuardVerifier.jl/
- NIST SP 1500-101: Election Event Logging CDF (PDF) — https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.1500-101.pdf


## Notarization / provenance
- RFC 3161: Time-Stamp Protocol (TSP) — https://www.ietf.org/rfc/rfc3161.txt
- Sigstore Cosign docs: Signing other types / countersigning — https://docs.sigstore.dev/cosign/signing/other_types/
- Sigstore overview — https://docs.sigstore.dev/about/overview/
- in-toto spec (GitHub) — https://github.com/in-toto/docs/blob/master/in-toto-spec.md
- in-toto overview — https://in-toto.io/
- SLSA v1.0 levels — https://slsa.dev/spec/v1.0/levels


## Network measurement, censorship interference, and split-view detection patterns
- **RFC 9162 — Certificate Transparency v2** (Merkle log; consistency proofs; ecosystem relies on monitoring and gossip to detect split views):  
  https://www.rfc-editor.org/rfc/rfc9162.html
- **RIPE Atlas APIs & Status Checks** (multi-vantage active measurements; alerting on health of endpoints):  
  https://atlas.ripe.net/docs/apis/  
  https://atlas.ripe.net/docs/apis/rest-api-manual/measurements/status-checks/
- **OONI data & API** (open data on network interference/censorship; programmatic access via API):  
  https://ooni.org/data/  
  https://docs.ooni.org/data  
  https://api.ooni.io/
- **Tor Onion Services properties** (censorship resistance; onion services stay within Tor network):  
  https://onionservices.torproject.org/technology/properties/  
  https://support.torproject.org/tor-browser/features/onion-services/
- **Apple iMessage Contact Key Verification** (example of gossiping log hashes to detect split-view attacks in key transparency):  
  https://security.apple.com/blog/imessage-contact-key-verification/
- **Open MPIC (multi-perspective corroboration)** (multi-perspective validation pattern to mitigate BGP hijack risks in domain validation):  
  https://www.sectigo.com/blog/open-mpic-open-source-multi-perspective-validation


## Availability and evidence transport additions (v21)

- RFC 9421: HTTP Message Signatures — https://www.rfc-editor.org/rfc/rfc9421
- RFC 9162: Certificate Transparency v2 (for MMD + log proofs) — https://www.rfc-editor.org/rfc/rfc9162.html
- RIPE Atlas REST API reference — https://atlas.ripe.net/docs/apis/rest-api-reference/
- CA/Browser Forum MPIC (Multi-Perspective Issuance Corroboration) ballot — https://cabforum.org/2024/11/07/ballot-smc010-introduction-of-multi-perspective-issuance-corroboration/
- S/MIME Baseline Requirements glossary entry for MPIC — https://cabforum.org/working-groups/smime/requirements/

## Availability witness gossip and split-world detection (v22)

- **Aggregation-Based Certificate Transparency Gossip** (Dahlberg et al., 2018) — network-assisted gossip to detect split views (RIPE Atlas evaluation):  
  https://arxiv.org/abs/1806.08817
- **Quantitative Verification of Certificate Transparency Gossip Protocols** (Oxford et al., 2020) — modeling detection probability under adversarial conditions:  
  https://www.prismmodelchecker.org/papers/spc20.pdf
- **Catena: Efficient Non-equivocation via Bitcoin** (Tomescu & Devadas, 2017) — non-equivocation framing and limits of gossip when messages can be delayed:  
  https://people.csail.mit.edu/devadas/pubs/catena.pdf
- **Apple iMessage Contact Key Verification** (example of piggybacked gossip for split-view detection):  
  https://security.apple.com/blog/imessage-contact-key-verification/

## Measurement platforms and ethics
- **RIPE Atlas — Creating Measurements (REST API)**:  
  https://atlas.ripe.net/docs/apis/rest-api-manual/measurements/creating-measurements/
- **RIPE Atlas — Fetching Measurement Results (start/stop)**:  
  https://atlas.ripe.net/docs/apis/rest-api-manual/measurements/results
- **RIPE Atlas — Service Terms and Conditions**:  
  https://www.ripe.net/about-us/legal/ripe-atlas-service-terms-and-conditions/
- **RIPE Labs — Ethics of RIPE Atlas Measurements**:  
  https://labs.ripe.net/author/kistel/ethics-of-ripe-atlas-measurements/
- **OONI — Interpreting OONI data**:  
  https://ooni.org/support/interpreting-ooni-data/
- **DHS — Menlo Report (ICT research ethics)**:  
  https://www.dhs.gov/sites/default/files/publications/CSD-MenloPrinciplesCORE-20120803_1.pdf

## Probe selection diversity and sampling bias (for multi-vantage evidence)
- **Metis: Better Atlas Vantage Point Selection for Everyone** (Appel et al., TMA 2022) — diversity-aware probe selection to reduce bias:  
  https://tma.ifip.org/2022/wp-content/uploads/sites/11/2022/06/tma2022-paper18.pdf
- **Metis: Selecting Diverse Atlas Vantage Points** (Tashiro et al., 2024) — newer evaluation and selection mechanisms:  
  https://www.iijlab.net/en/members/malte/tashiro_tnsm2024.pdf
- **Lessons Learned from using the RIPE Atlas Platform for Measurement Research** (Bajpai & Schönwälder, 2015) — documents inherent sampling bias and operational pitfalls:  
  https://vaibhavbajpai.com/documents/papers/proceedings/ripeatlas-ccr-2015.pdf
- **Investigating Interdomain Routing Policies in the Wild** (Anwar et al., 2015) — notes Atlas geographic skew and pragmatic stratified selection:  
  https://conferences2.sigcomm.org/imc/2015/papers/p71.pdf

- **Bias in Internet Measurement Platforms (Sermpezis et al., 2023)** — https://arxiv.org/pdf/2307.09958 — discussion and quantification of bias in measurement infrastructures incl. RIPE Atlas

- **Bias in Internet Measurement Infrastructure (RIPE Labs, 2022)** — https://labs.ripe.net/author/pavlos_sermpezis/bias-in-internet-measurement-infrastructure/ — practitioner overview of bias and interpretation pitfalls

- **Quantifying Interference between Measurements on the RIPE Atlas Platform (Holterbach et al., IMC 2015)** — https://conferences.sigcomm.org/imc/2015/papers/p437.pdf — measurement interference impacts precision and synchrony

- **RIPE Atlas Security Disclosures (RIPE NCC)** — https://atlas.ripe.net/docs/security/ — platform security disclosures affecting probe administration and APIs

- **Day in the Life of RIPE Atlas: Operational Insights and Challenges (Nosyk et al., arXiv 2025)** — https://www.arxiv.org/pdf/2511.22474 — operational realities, scale, and process considerations

- **How Effective is Multiple-Vantage-Point Domain Control Validation? (USENIX Security 2023)** — https://www.usenix.org/conference/usenixsecurity23/presentation/cimaszewski — quantifies multi-vantage effectiveness under real routing practices

- **Experiences Deploying Multi-Vantage-Point Domain Control Validation (Birge-Lee et al., USENIX Security 2021)** — https://www.usenix.org/system/files/sec21fall-birge-lee.pdf — deployment notes for multi-vantage validation systems

- **A survey of internet censorship and its measurement (Wendzel et al., 2025)** — https://www.sciencedirect.com/science/article/pii/S0167404825004213 — taxonomy of censorship and measurement methodologies

- **Quack: Scalable Remote Measurement of Application-Layer Censorship (USENIX Security 2018)** — https://amcdon.com/papers/quack-usenix18.pdf — methodology for detecting application-layer blocking
## Network measurement, routing attacks, and probe platforms
- **Holterbach et al. (IMC 2015) — Quantifying Interference between Measurements on the RIPE Atlas platform** (concurrent measurement interference):  
  https://conferences.sigcomm.org/imc/2015/papers/p437.pdf
- **Bajpai et al. (CCR 2015) — Lessons Learned from Using the RIPE Atlas Platform for Measurement Research** (probe distribution skew, platform constraints):  
  https://vaibhavbajpai.com/documents/papers/proceedings/ripeatlas-ccr-2015.pdf
- **Debant et al. (USENIX Security 2023) — Analysis of an Internet Voting System** (case study; operational realities):  
  https://www.usenix.org/system/files/usenixsecurity23-debant.pdf
- **Milolidakis et al. (2023) — On the Effectiveness of BGP Hijackers That Evade Public Route Collectors** (monitor evasion):  
  https://nsg.ee.ethz.ch/fileadmin/user_upload/publications/On_the_Effectiveness_of_BGP_Hijackers_That_Evade_Public_Route_Collectors.pdf
- **Birge-Lee et al. (2024/2025) — Global BGP Attacks that Evade Route Monitoring** (attacks can hide from monitoring systems):  
  https://arxiv.org/pdf/2408.09622
- **Schulmann & Zhao (WOOT 2025) — Stealth BGP Hijacks with uRPF Filtering** (stealthy persistent DoS via BGP/uRPF interaction):  
  https://www.usenix.org/system/files/woot25-schulmann.pdf
- **Kastanakis et al. (2025) — Investigating Location-aware Advertisements in Anycast IP Networks** (selective announcements prevalent in anycast):  
  https://dl.acm.org/doi/10.1145/3673422.3674885
- **PROVE (2023) — Provable remote attestation for public verifiability** (attestation concept reference):  
  https://www.sciencedirect.com/science/article/pii/S2214212623000327


## Transparency logs, witnessing, key transparency, monitoring
- **RFC 9162 — Certificate Transparency Version 2.0** (Merkle logs; inclusion/consistency proofs; MMD concepts):
  https://www.rfc-editor.org/rfc/rfc9162.html
- **Syta et al. — Keeping Authorities “Honest or Bust” with Decentralized Witness Cosigning (CoSi)** (witness cosigning model):
  https://arxiv.org/pdf/1503.08768
- **Sigsum design notes** (witness-cosigned tree heads; split-view resistance; safe shutdown properties):
  https://git.sigsum.org/sigsum/tree/doc/design.md
- **IETF Keytrans WG — Key Transparency Protocol (draft-ietf-keytrans-protocol)**:
  https://datatracker.ietf.org/doc/draft-ietf-keytrans-protocol/
- **NDSS 2024 — The Public Inspections on Third-party Monitors** (monitor trust model pitfalls in CT-like ecosystems):
  https://www.ndss-symposium.org/wp-content/uploads/2024-834-paper.pdf
- **NIST SP 800-61r3** (Incident Response Recommendations and Considerations for Cybersecurity Risk Management):
  https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-61r3.pdf
- **Sigstore security model** (transparency logs and detectability for supply-chain artifacts):
  https://docs.sigstore.dev/about/security/

## v28 governance and witness ecosystem references

- Chrome Certificate Transparency Log Policy (operator admission/removal expectations): https://googlechrome.github.io/CertificateTransparency/log_policy.html
- CoSi witness cosigning (design motivation and scalability): https://arxiv.org/abs/1503.08768
- Sigsum documentation (witness cosigning formats and trust policy work): https://www.sigsum.org/docs/
- Key Transparency architecture / protocol (witnessing, consistency, deployment guidance): https://datatracker.ietf.org/doc/draft-ietf-keytrans-architecture/ and https://datatracker.ietf.org/doc/draft-ietf-keytrans-protocol/
- Monitor accountability via public inspections (CT ecosystem): https://www.ndss-symposium.org/wp-content/uploads/2024-834-paper.pdf
- Transparent keyserver witnessing policies (operator grouping and monitor implications): https://words.filippo.io/keyserver-tlog/

## v29 monitor inspection + SCITT transparency references

- NDSS 2024 — Certificate Transparency Revisited: The Public Inspections on Third-party Monitors (paper + program page):
  https://www.ndss-symposium.org/wp-content/uploads/2024-834-paper.pdf
  https://www.ndss-symposium.org/ndss-paper/certificate-transparency-revisited-the-public-inspections-on-third-party-monitors/
- IETF SCITT Architecture (draft-ietf-scitt-architecture):
- IETF SCITT Receipts — COSE Receipts with CCF (draft-ietf-scitt-receipts-ccf-profile-00):
  https://datatracker.ietf.org/doc/draft-ietf-scitt-receipts-ccf-profile/

  https://datatracker.ietf.org/doc/draft-ietf-scitt-architecture/
- IETF SCITT Reference APIs (draft-ietf-scitt-scrapi):
  https://datatracker.ietf.org/doc/draft-ietf-scitt-scrapi/
- Sigsum docs (witness cosigning formats; witness network pointer):
  https://www.sigsum.org/docs/
- IETF Key Transparency Architecture (deployment guidance; multi-log policy; tombstones):
  https://datatracker.ietf.org/doc/draft-ietf-keytrans-architecture/

## v30 additions (inspection challenge randomness + gossip)

- RFC 9162 (Certificate Transparency v2) — log auditing and MMD concept: https://www.rfc-editor.org/rfc/rfc9162.html
- Chuat et al. (2015) “Efficient Gossip Protocols for Verifying the Consistency of Certificate Transparency Logs” (arXiv:1511.01514): https://arxiv.org/pdf/1511.01514
- Sun et al. (NDSS 2024) “Certificate Transparency Revisited: The Public Inspections on Third-party Monitors”: https://www.ndss-symposium.org/wp-content/uploads/2024-834-paper.pdf
- Apple security blog (2023) iMessage Contact Key Verification — gossiping log hashes to detect split views: https://security.apple.com/blog/imessage-contact-key-verification/
- NIST CSRC — Interoperable Randomness Beacons project: https://csrc.nist.gov/projects/interoperable-randomness-beacons
- IETF Key Transparency Architecture draft — tombstones prevent accepting stale keys during migrations: https://datatracker.ietf.org/doc/draft-ietf-keytrans-architecture/
