#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
from archive_meta import current_revision

CURRENT_REV = current_revision()

NEW_NOTE_SOURCES = {
"archive/840-preemption-defaults-for-ideal-governments-of-each-scope-local-headroom-metro-primacy-federal-bargain-locks-national-floors-and-treaty-bounded-override.md": {
    "groups": [
        {"title": "The Division of Powers in Federations", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/division-powers-federations"},
        {"title": "Federalism", "publisher": "International IDEA", "url": "https://www.idea.int/sites/default/files/publications/federalism-primer.pdf"},
        {"title": "Assigning responsibilities across levels of government", "publisher": "OECD", "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2018/09/assigning-responsibilities-across-levels-of-government_d3650b01/f0944eae-en.pdf"},
        {"title": "Multi-Level Regulatory Governance", "publisher": "OECD", "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2009/06/multi-level-regulatory-governance_g17a1cdc/224074617147.pdf"},
        {"title": "European Charter of Local Self-Government", "publisher": "Council of Europe", "url": "https://rm.coe.int/european-charter-of-local-self-government-eng/1680a87cc3"},
        {"title": "Cities, local and regional governments and human rights", "publisher": "OHCHR", "url": "https://www.ohchr.org/en/about-us/what-we-do/partnership/local-governments"},
        {"title": "Chapter XVI: Article 103 — Charter of the United Nations", "publisher": "United Nations", "url": "https://legal.un.org/repertory/art103.shtml"},
        {"title": "Vienna Convention on the Law of Treaties (1969)", "publisher": "United Nations", "url": "https://legal.un.org/ilc/texts/instruments/english/conventions/1_1_1969.pdf"}
    ]
},

"archive/839-amendment-defaults-for-ideal-governments-of-each-scope-local-bylaws-municipal-charters-metro-double-keys-federal-entrenchment-and-treaty-ratification.md": {
    "groups": [
        {"title": "Constitutional Amendment Procedures", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/constitutional-amendment-procedures"},
        {"title": "Report on Constitutional Amendment", "publisher": "Venice Commission / Council of Europe", "url": "https://www.venice.coe.int/webforms/documents/?pdf=cdl-ad%282010%29001-e"},
        {"title": "European Charter of Local Self-Government", "publisher": "Council of Europe", "url": "https://rm.coe.int/european-charter-of-local-self-government-eng/1680a87cc3"},
        {"title": "Federalism", "publisher": "International IDEA", "url": "https://www.idea.int/sites/default/files/publications/federalism-primer.pdf"},
        {"title": "Chapter XVIII: Articles 108 and 109 — Charter of the United Nations", "publisher": "United Nations", "url": "https://legal.un.org/repertory/art108_109.shtml"},
        {"title": "Vienna Convention on the Law of Treaties (1969)", "publisher": "United Nations", "url": "https://legal.un.org/ilc/texts/instruments/english/conventions/1_1_1969.pdf"}
    ]
}
,
"archive/838-guarantee-defaults-for-ideal-governments-of-each-scope-local-dignity-municipal-nondiscrimination-regional-implementation-national-equal-citizenship-and-treaty-backstops.md": {
    "groups": [
        {"title": "Cities, local and regional governments and human rights", "publisher": "OHCHR", "url": "https://www.ohchr.org/en/about-us/what-we-do/partnership/local-governments"},
        {"title": "Human Rights at local and regional levels", "publisher": "Congress of Local and Regional Authorities / Council of Europe", "url": "https://www.coe.int/en/web/congress/human-rights"},
        {"title": "A Practical Guide to Constitution Building", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/practical-guide-constitution-building"},
        {"title": "Federalism", "publisher": "International IDEA", "url": "https://www.idea.int/sites/default/files/publications/federalism-primer.pdf"},
        {"title": "Principles relating to the Status of National Institutions (The Paris Principles)", "publisher": "OHCHR", "url": "https://www.ohchr.org/en/instruments-mechanisms/instruments/principles-relating-status-national-institutions-paris"},
        {"title": "Treaty Bodies", "publisher": "OHCHR", "url": "https://www.ohchr.org/en/treaty-bodies"},
        {"title": "Complaints about human rights violations", "publisher": "OHCHR", "url": "https://www.ohchr.org/en/treaty-bodies/complaints-about-human-rights-violations"},
        {"title": "The European Convention on Human Rights", "publisher": "European Court of Human Rights / Council of Europe", "url": "https://www.echr.coe.int/european-convention-on-human-rights"}
    ]
}
,
"archive/837-adjudication-defaults-for-ideal-governments-of-each-scope-local-pre-legal-entry-municipal-administrative-justice-regional-ordinary-courts-national-apex-review-and-treaty-tribunals.md": {
    "groups": [
        {"title": "Basic Principles on the Independence of the Judiciary", "publisher": "OHCHR / United Nations", "url": "https://www.ohchr.org/en/instruments-mechanisms/instruments/basic-principles-independence-judiciary"},
        {"title": "Access to Justice", "publisher": "United Nations and the Rule of Law", "url": "https://www.un.org/ruleoflaw/thematic-areas/access-to-justice-and-rule-of-law-institutions/access-to-justice/"},
        {"title": "A Practical Guide to Constitution Building: The Design of the Judicial Branch", "publisher": "International IDEA", "url": "https://www.idea.int/sites/default/files/publications/chapters/practical-guide-to-constitution-building/a-practical-guide-to-constitution-building-chapter-6.pdf"},
        {"title": "Courts in Federal Countries", "publisher": "International IDEA", "url": "https://www.idea.int/sites/default/files/publications/courts-in-federal-countries.pdf"},
        {"title": "Federalism", "publisher": "International IDEA", "url": "https://www.idea.int/sites/default/files/publications/federalism-primer.pdf"},
        {"title": "Administrative justice as the interface between people and institutions", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/making-justice-systems-more-effective-and-people-centred_e02fd90b-en/full-report/administrative-justice-as-the-interface-between-people-and-institutions_88464c56.html"},
        {"title": "Judicial maps to support access to justice within a quality judicial system", "publisher": "CEPEJ / Council of Europe", "url": "https://rm.coe.int/european-commission-for-the-efficiency-of-justice-cepej-revised-guidel/168078c492"},
        {"title": "European Charter of Local Self-Government", "publisher": "Council of Europe", "url": "https://rm.coe.int/european-charter-of-local-self-government-eng/1680a87cc3"},
        {"title": "How the Court Works", "publisher": "International Court of Justice", "url": "https://www.icj-cij.org/how-the-court-works"},
        {"title": "Chapter XIV: The International Court of Justice", "publisher": "United Nations", "url": "https://www.un.org/en/about-us/un-charter/chapter-14"}
    ]
}
,
"archive/836-participation-defaults-for-ideal-governments-of-each-scope-local-assembly-municipal-dockets-metro-territorial-hearings-national-petition-ladders-and-treaty-observers.md": {
    "groups": [
        {"title": "Democracy at the Local Level", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/democracy-local-level"},
        {"title": "Direct Democracy", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/direct-democracy"},
        {"title": "Additional Protocol on the right to participate in the affairs of a local authority", "publisher": "Council of Europe", "url": "https://www.coe.int/en/web/congress/additional-protocol-to-the-european-charter-of-local-self-government-on-the-right-to-participate-in-the-affairs-of-a-local-authority"},
        {"title": "Recommendation on the participation of citizens in local public life", "publisher": "Council of Europe", "url": "https://www.coe.int/en/web/youth/-/recommendation-on-the-participation-of-citizens-in-local-public-life"},
        {"title": "OECD Guidelines for Citizen Participation Processes", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/oecd-guidelines-for-citizen-participation-processes_f765caf6-en.html"},
        {"title": "Citizen participation and deliberation: Government at a Glance 2025", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/government-at-a-glance-2025_0efd0bcd-en/full-report/citizen-participation-and-deliberation_52b90285.html"},
        {"title": "Innovative public participation", "publisher": "OECD", "url": "https://www.oecd.org/en/topics/sub-issues/open-government-and-citizen-participation/innovative-public-participation.html"},
        {"title": "A/79/968 General Assembly", "publisher": "United Nations", "url": "https://docs.un.org/en/A/79/968"},
        {"title": "How to obtain observer status", "publisher": "UNFCCC", "url": "https://unfccc.int/process-and-meetings/parties-non-party-stakeholders/non-party-stakeholders/overview/how-to-obtain-observer-status"}
    ]
}
,
"archive/834-information-defaults-for-ideal-governments-of-each-scope-local-ledgers-municipal-record-homes-metro-observatories-national-statistics-and-treaty-registries.md": {
    "groups": [
        {"title": "The Fundamental Principles of Official Statistics", "publisher": "United Nations Statistics Division", "url": "https://unstats.un.org/fpos/"},
        {"title": "Methodology and sources", "publisher": "OECD Local Data Portal", "url": "https://localdataportal.oecd.org/methodology.html"},
        {"title": "Transparency of public information: Government at a Glance 2025", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/government-at-a-glance-2025_0efd0bcd-en/full-report/transparency-of-public-information_60a963c4.html"},
        {"title": "Recommendation of the Council on Open Government", "publisher": "OECD Legal Instruments", "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0438"},
        {"title": "Transparency and open government", "publisher": "Council of Europe", "url": "https://rm.coe.int/transparency-and-open-government/1680932036"},
        {"title": "Convention on Access to Official Documents monitoring materials", "publisher": "Council of Europe", "url": "https://rm.coe.int/council-of-europe-convention-on-access-to-official-documents-cets-no-2/1680b5935b"},
        {"title": "Urban Observatories", "publisher": "UN-Habitat", "url": "https://data.unhabitat.org/pages/urban-observatories"},
        {"title": "A Guide to Setting up an Urban Observatory", "publisher": "UN-Habitat", "url": "https://unhabitat.org/a-guide-to-setting-up-an-urban-observatory"},
        {"title": "The Government Analytics Handbook", "publisher": "World Bank", "url": "https://www.worldbank.org/en/publication/government-analytics"}
    ]
}
,
"archive/835-emergency-defaults-for-ideal-governments-of-each-scope-local-readiness-municipal-incident-command-regional-civil-protection-national-derogation-discipline-and-treaty-alerting.md": {
    "groups": [
        {"title": "Emergency Powers", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/emergency-powers"},
        {"title": "Compilation on states of emergency", "publisher": "Venice Commission / Council of Europe", "url": "https://rm.coe.int/venice-commission-compilation-on-states-of-emergency-eng/16809e85b9"},
        {"title": "Emergency powers - what standards?", "publisher": "Council of Europe", "url": "https://www.coe.int/en/web/human-rights-rule-of-law/venice-commission-covid19"},
        {"title": "Risk governance", "publisher": "OECD", "url": "https://www.oecd.org/en/topics/sub-issues/sustainable-and-resilient-infrastructure/risk-governance.html"},
        {"title": "The Changing Face of Strategic Crisis Management", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/the-changing-face-of-strategic-crisis-management_9789264249127-en.html"},
        {"title": "The territorial impact of COVID-19: Managing the crisis across levels of government", "publisher": "OECD", "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2020/04/the-territorial-impact-of-covid-19-managing-the-crisis-across-levels-of-government_9cfcb95f/d3e314e1-en.pdf"},
        {"title": "Local government powers for disaster risk reduction: A study on local-level authority and capacity for resilience", "publisher": "UNDRR", "url": "https://www.undrr.org/publication/local-government-powers-disaster-risk-reduction-study-local-level-authority-and"},
        {"title": "International Health Regulations", "publisher": "WHO", "url": "https://www.who.int/health-topics/international-health-regulations"},
        {"title": "United Nations Charter (full text)", "publisher": "United Nations", "url": "https://www.un.org/en/about-us/un-charter/full-text"},
        {"title": "United Nations Disaster Assessment and Coordination", "publisher": "OCHA / United Nations", "url": "https://www.unocha.org/united-nations-disaster-assessment-and-coordination"}
    ]
}
,

"archive/833-coercion-defaults-for-ideal-governments-of-each-scope-local-witness-municipal-civil-enforcement-regional-police-platforms-national-force-monopoly-and-treaty-bound-restraint.md": {
    "groups": [
        {"title": "Local Democracy", "publisher": "International IDEA", "url": "https://www.idea.int/sites/default/files/publications/local-democracy-primer.pdf"},
        {"title": "Federalism", "publisher": "International IDEA", "url": "https://www.idea.int/sites/default/files/publications/federalism-primer.pdf"},
        {"title": "Emergency Powers", "publisher": "International IDEA", "url": "https://www.idea.int/sites/default/files/publications/emergency-powers-primer.pdf"},
        {"title": "Assigning responsibilities across levels of government", "publisher": "OECD", "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2018/09/assigning-responsibilities-across-levels-of-government_d3650b01/f0944eae-en.pdf"},
        {"title": "Governing the City", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/governing-the-city_9789264226500-en.html"},
        {"title": "Regional Governance in OECD Countries", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/regional-governance-in-oecd-countries_4d7c6483-en.html"},
        {"title": "Basic Principles on the Use of Force and Firearms by Law Enforcement Officials", "publisher": "OHCHR / United Nations", "url": "https://www.ohchr.org/en/instruments-mechanisms/instruments/basic-principles-use-force-and-firearms-law-enforcement"},
        {"title": "Code of Conduct for Law Enforcement Officials", "publisher": "OHCHR / United Nations", "url": "https://www.ohchr.org/en/instruments-mechanisms/instruments/code-conduct-law-enforcement-officials"},
        {"title": "United Nations Charter (full text)", "publisher": "United Nations", "url": "https://www.un.org/en/about-us/un-charter/full-text"},
        {"title": "Chapter VII: Action with Respect to Threats to the Peace, Breaches of the Peace, and Acts of Aggression", "publisher": "United Nations", "url": "https://www.un.org/en/about-us/un-charter/chapter-7"}
    ]
}
,
"archive/832-oversight-defaults-for-ideal-governments-of-each-scope-local-witness-municipal-scrutiny-metro-audit-national-watchdogs-and-treaty-review.md": {
    "groups": [
        {"title": "Local Democracy", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/local-democracy"},
        {"title": "12 Principles of Good Democratic Governance", "publisher": "Council of Europe", "url": "https://www.coe.int/en/web/congress/12-principles-of-good-governance"},
        {"title": "Independent Institutions: Enhancing Democratic Integrity and Accountability through Constitutional Design", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/independent-institutions-enhancing-democratic-integrity-and-accountability-through-constitutional-design"},
        {"title": "ISSAI 100 – Fundamental Principles of Public-Sector Auditing", "publisher": "INTOSAI", "url": "https://www.intosai.org/fileadmin/downloads/documents/open_access/ISSAI_100_to_400/issai_100/ISSAI_100_EN.pdf"},
        {"title": "Supreme Audit Institutions and Good Governance", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/supreme-audit-institutions-and-good-governance_9789264263871-en.html"},
        {"title": "Governing the City", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/governing-the-city_9789264226500-en.html"},
        {"title": "Recommendation CM/Rec(2022)2 on democratic accountability of elected representatives and elected bodies at local and regional level", "publisher": "Council of Europe", "url": "https://rm.coe.int/0900001680a57739"},
        {"title": "Government at a Glance 2025 — Accountable law making", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/government-at-a-glance-2025_0efd0bcd-en/full-report/accountable-law-making_31319db5.html"},
        {"title": "Office of Internal Oversight Services", "publisher": "United Nations", "url": "https://oios.un.org/"},
        {"title": "Coordination with other UN entities", "publisher": "Office of Internal Oversight Services", "url": "https://oios.un.org/coordination-with-entities"},
        {"title": "United Nations Charter (full text)", "publisher": "United Nations", "url": "https://www.un.org/en/about-us/un-charter/full-text"}
    ]
}
,

"archive/831-fiscal-defaults-for-ideal-governments-of-each-scope-tiny-commons-municipal-own-source-metro-shares-regional-equalization-national-solidarity-and-treaty-dues.md": {
    "groups": [
        {"title": "Local Democracy", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/local-democracy"},
        {"title": "European Charter of Local Self-Government", "publisher": "Council of Europe", "url": "https://www.coe.int/en/web/congress/european-charter-of-local-self-government"},
        {"title": "Fiscal Federalism 2022", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/fiscal-federalism-2022_201c75b6-en.html"},
        {"title": "Intergovernmental fiscal transfers and fiscal equalisation in a time of consolidation", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/intergovernmental-fiscal-transfers-and-fiscal-equalisation-in-a-time-of-consolidation_4853a4d0-en.html"},
        {"title": "Governing the City", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/governing-the-city_9789264226500-en.html"},
        {"title": "Municipal Finances: A Handbook for Local Governments", "publisher": "World Bank", "url": "https://documents.worldbank.org/en/publication/documents-reports/documentdetail/403951468180872451/municipal-finances-a-handbook-for-local-governments"},
        {"title": "Federal Systems, Intergovernmental Relations and Federated Regions", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/federal-systems-intergovernmental-relations-and-federated-regions"},
        {"title": "United Nations Charter (full text)", "publisher": "United Nations", "url": "https://www.un.org/en/about-us/un-charter/full-text"},
        {"title": "UN General Assembly - Fifth Committee / Article 17", "publisher": "United Nations", "url": "https://www.un.org/en/ga/fifth/art17.shtml"},
        {"title": "How we are funded", "publisher": "United Nations Peacekeeping", "url": "https://peacekeeping.un.org/en/how-we-are-funded"}
    ]
}
,

"archive/830-decision-rule-defaults-for-ideal-governments-of-each-scope-local-majorities-municipal-ordinary-rules-federal-double-keys-and-no-fake-global-unanimity.md": {
    "groups": [
        {"title": "Local Democracy", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/local-democracy"},
        {"title": "Opposition and Legislative Minorities: Constitutional Roles, Rights and Recognition", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/opposition-and-legislative-minorities-constitutional-roles-rights-recognition"},
        {"title": "Bicameralism", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/bicameralism"},
        {"title": "Constitutional Amendment Procedures", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/constitutional-amendment-procedures"},
        {"title": "Governing the City", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/governing-the-city_9789264226500-en.html"},
        {"title": "Regional Governance in OECD Countries", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/regional-governance-in-oecd-countries_4d7c6483-en.html"},
        {"title": "Recommendation CM/Rec(2022)2 on democratic accountability of elected representatives and elected bodies at local and regional level", "publisher": "Council of Europe", "url": "https://rm.coe.int/0900001680a57739"},
        {"title": "Chapter IV: The General Assembly (Articles 9-22)", "publisher": "United Nations", "url": "https://www.un.org/en/about-us/un-charter/chapter-4"},
        {"title": "How Decisions are Made at the UN", "publisher": "United Nations", "url": "https://www.un.org/en/model-united-nations/how-decisions-are-made-un"},
        {"title": "Rules of Procedure", "publisher": "United Nations", "url": "https://www.un.org/en/model-united-nations/rules-procedure-0"}
    ]
}
,

"archive/829-selection-defaults-for-ideal-governments-of-each-scope-open-local-voice-proportional-councils-metro-wide-elections-federal-shared-rule-and-delegated-global-seats.md": {
    "groups": [
        {"title": "Local Democracy", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/local-democracy"},
        {"title": "Democracy at the Local Level", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/democracy-local-level"},
        {"title": "Electoral System Design: The International IDEA Handbook", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/electoral-system-design-international-idea-handbook"},
        {"title": "Electoral system design in the context of constitution-building", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/electoral-system-design-context-constitution-building"},
        {"title": "Electoral Systems", "publisher": "ACE Electoral Knowledge Network", "url": "https://aceproject.org/ace-en/topics/es/onePage"},
        {"title": "Practical Advice for Electoral System Designers", "publisher": "ACE Electoral Knowledge Network", "url": "https://aceproject.org/main/english/es/es70.htm"},
        {"title": "Governing the City", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/governing-the-city_9789264226500-en.html"},
        {"title": "The OECD Metropolitan Governance Survey", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/the-oecd-metropolitan-governance-survey_5jz43zldh08p-en.html"},
        {"title": "Bicameralism", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/bicameralism"},
        {"title": "Second Chambers in Federal Systems", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/second-chambers-federal-systems"},
        {"title": "Government Formation and Removal Mechanisms", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/government-formation-and-removal-mechanisms"},
        {"title": "United Nations Charter (full text)", "publisher": "United Nations", "url": "https://www.un.org/en/about-us/un-charter/full-text"}
    ]
}
,

"archive/828-mandate-exit-defaults-for-ideal-governments-of-each-scope-local-recall-municipal-dismissal-confidence-loss-bounded-dissolution-and-treaty-lapse.md": {
    "groups": [
        {"title": "Local Democracy", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/local-democracy"},
        {"title": "Direct Democracy", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/direct-democracy"},
        {"title": "Report on the Recall of Mayors and Local Elected Representatives", "publisher": "Venice Commission / Council of Europe", "url": "https://www.venice.coe.int/webforms/documents/default.aspx?pdffile=CDL-AD%282019%29011rev-e"},
        {"title": "European Charter of Local Self-Government", "publisher": "Council of Europe", "url": "https://www.coe.int/en/web/congress/european-charter-of-local-self-government"},
        {"title": "Government Formation and Removal Mechanisms", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/government-formation-and-removal-mechanisms"},
        {"title": "Dissolution of Parliament", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/dissolution-parliament"},
        {"title": "Code of Good Practice in Electoral Matters", "publisher": "Venice Commission / Council of Europe", "url": "https://www.venice.coe.int/files/Code%20de%20conduite_GBR%202025_WEB_A5.pdf"},
        {"title": "Governing the City", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/governing-the-city_9789264226500-en.html"},
        {"title": "United Nations Charter (full text)", "publisher": "United Nations", "url": "https://www.un.org/en/about-us/un-charter/full-text"},
        {"title": "Security Council Reporting and mandate cycles", "publisher": "United Nations", "url": "https://main.un.org/securitycouncil/sites/default/files/reporting_and_mandate_cycles.pdf"}
    ]
}
,

"archive/827-mandate-duration-defaults-for-ideal-governments-of-each-scope-short-local-rotation-municipal-and-metro-stability-national-renewal-windows-and-treaty-review-clocks.md": {
    "groups": [
        {"title": "Local Democracy", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/local-democracy"},
        {"title": "Report on the Recall of Mayors and Local Elected Representatives", "publisher": "Venice Commission / Council of Europe", "url": "https://www.venice.coe.int/webforms/documents/default.aspx?pdffile=CDL-AD%282019%29011rev-e"},
        {"title": "Government Formation and Removal Mechanisms", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/government-formation-and-removal-mechanisms"},
        {"title": "Dissolution of Parliament", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/dissolution-parliament"},
        {"title": "Code of Good Practice in Electoral Matters", "publisher": "Venice Commission / Council of Europe", "url": "https://www.venice.coe.int/files/Code%20de%20conduite_GBR%202025_WEB_A5.pdf"},
        {"title": "Report on Term Limits Part II", "publisher": "Venice Commission / Council of Europe", "url": "https://www.venice.coe.int/webforms/documents/default.aspx?pdffile=CDL-AD%282019%29007-e"},
        {"title": "Governing the City", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/governing-the-city_9789264226500-en.html"},
        {"title": "Universal Periodic Review", "publisher": "United Nations Sustainable Development Group", "url": "https://unsdg.un.org/2030-agenda/strengthening-international-human-rights/universal-periodic-review"},
        {"title": "A/79/336", "publisher": "United Nations General Assembly", "url": "https://docs.un.org/en/A/79/336"}
    ]
}
,


"archive/826-mandate-source-defaults-for-ideal-governments-of-each-scope-assembly-voice-council-confidence-metro-public-mandates-regional-investiture-national-confidence-and-treaty-delegation.md": {
    "groups": [
        {"title": "Local Democracy", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/local-democracy"},
        {"title": "European Charter of Local Self-Government", "publisher": "Council of Europe", "url": "https://www.coe.int/en/web/congress/european-charter-of-local-self-government"},
        {"title": "Governing the City", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/governing-the-city_9789264226500-en.html"},
        {"title": "International Practices of Metropolitan Governance", "publisher": "World Bank", "url": "https://documents.worldbank.org/en/publication/documents-reports/documentdetail/278861591018281649"},
        {"title": "Regional democracy - Council of Europe Reference Framework", "publisher": "Council of Europe", "url": "https://edoc.coe.int/en/local-democracy/7645-regional-democracy-council-of-europe-reference-framework.html"},
        {"title": "Government Formation and Removal Mechanisms", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/government-formation-and-removal-mechanisms"},
        {"title": "Federalism", "publisher": "International IDEA", "url": "https://www.idea.int/sites/default/files/publications/federalism-primer.pdf"},
        {"title": "United Nations Charter (full text)", "publisher": "United Nations", "url": "https://www.un.org/en/about-us/un-charter/full-text"}
    ]
}
,


"archive/825-regime-form-defaults-for-ideal-governments-of-each-scope-steward-assemblies-municipal-administration-metropolitan-mandates-regional-parliamentarism-national-confidence-and-global-narrow-waists.md": {
    "groups": [
        {"title": "Local Democracy", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/local-democracy"},
        {"title": "Governing the City", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/governing-the-city_9789264226500-en.html"},
        {"title": "International Practices of Metropolitan Governance", "publisher": "World Bank", "url": "https://documents.worldbank.org/en/publication/documents-reports/documentdetail/278861591018281649"},
        {"title": "Regional Governance in OECD Countries", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/regional-governance-in-oecd-countries_4d7c6483-en.html"},
        {"title": "Government Formation and Removal Mechanisms", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/government-formation-and-removal-mechanisms"},
        {"title": "Bicameralism", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/bicameralism"},
        {"title": "Second Chambers in Federal Systems", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/second-chambers-federal-systems"},
        {"title": "Non-Executive Presidents in Parliamentary Democracies", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/non-executive-presidents-parliamentary-democracies"},
        {"title": "Constitutional Monarchs in Parliamentary Democracies", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/constitutional-monarchs-parliamentary-democracies"},
        {"title": "United Nations Charter (full text)", "publisher": "United Nations", "url": "https://www.un.org/en/about-us/un-charter/full-text"}
    ]
}
,
"archive/824-regulatory-and-enforcement-boundary-chain-templates-for-cross-boundary-scope-forms-signal-routing-joined-up-inspections-bounded-permitting-public-sanctions-and-no-heavy-power-by-shared-badge.md": {
    "groups": [
        {"title": "European Charter of Local Self-Government (ETS No. 122)", "publisher": "Council of Europe", "url": "https://www.coe.int/en/web/conventions/full-list/-/conventions/treaty/122"},
        {"title": "Explanatory Report to the European Charter of Local Self-Government", "publisher": "Council of Europe", "url": "https://rm.coe.int/16800ca437"},
        {"title": "Regulatory Enforcement and Inspections", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/regulatory-enforcement-and-inspections_9789264208117-en.html"},
        {"title": "OECD Regulatory Enforcement and Inspections Toolkit", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/oecd-regulatory-enforcement-and-inspections-toolkit_9789264303959-en.html"},
        {"title": "Best practice principles for licensing and permitting", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/best-practice-principles-for-licensing-and-permitting_5f63586d-en/full-report.html"},
        {"title": "International Practices of Metropolitan Governance", "publisher": "World Bank", "url": "https://documents.worldbank.org/en/publication/documents-reports/documentdetail/278861591018281649"},
        {"title": "Risk-Based Approaches to Business Regulation: A Note for Reformers", "publisher": "World Bank Group", "url": "https://documents.worldbank.org/en/publication/documents-reports/documentdetail/880271603464018549"}
    ]
}
,

"archive/823-contracting-boundary-chain-templates-for-cross-boundary-scope-forms-light-support-buying-principal-owned-commissioning-chartered-concessions-change-control-and-no-heavy-power-by-contract-escape-hatch.md": {
    "groups": [
        {"title": "Recommendation of the Council on Public Procurement", "publisher": "OECD Legal Instruments", "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0411"},
        {"title": "Implementing the OECD Recommendation on Public Procurement in OECD and Partner Countries: 2020-2024 Report", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/implementing-the-oecd-recommendation-on-public-procurement-in-oecd-and-partner-countries_02a46a58-en.html"},
        {"title": "Enabling Inter-Municipal Shared Service Provision in Lithuania", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/enabling-inter-municipal-shared-service-provision-in-lithuania_f8ad6859-en.html"},
        {"title": "Directive 2014/24/EU on public procurement", "publisher": "EUR-Lex / European Union", "url": "https://eur-lex.europa.eu/eli/dir/2014/24/oj/eng"},
        {"title": "Directive 2014/23/EU on the award of concession contracts", "publisher": "EUR-Lex / European Union", "url": "https://eur-lex.europa.eu/eli/dir/2014/23/oj/eng"},
        {"title": "Managing PPP Contracts", "publisher": "World Bank / PPP Resource Center", "url": "https://ppp.worldbank.org/print/pdf/node/5541"},
        {"title": "A Framework for Disclosure in Public-Private Partnership Projects", "publisher": "World Bank", "url": "https://documents.worldbank.org/en/publication/documents-reports/documentdetail/744411637834708119/a-framework-for-disclosure-in-public-private-partnership-projects"}
    ]
}
,

"archive/822-asset-and-liability-chain-templates-for-cross-boundary-scope-forms-member-owned-infrastructure-ring-fenced-balance-sheets-handback-maps-contingent-obligations-and-no-heavy-power-by-orphaned-balance-sheet.md": {
    "groups": [
        {"title": "Recommendation 132 (2003) on municipal property in the light of the principles of the European Charter of Local Self-Government", "publisher": "Council of Europe / Congress of Local and Regional Authorities", "url": "https://rm.coe.int/recommendation-132-of-the-congress-of-local-and-regional-authorities-o/1680719b85"},
        {"title": "Regulation (EC) No 1082/2006 on a European grouping of territorial cooperation (EGTC) — consolidated text", "publisher": "EUR-Lex / European Union", "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02006R1082-20140622"},
        {"title": "Recommendation of the Council on the Governance of Infrastructure", "publisher": "OECD Legal Instruments", "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0460"},
        {"title": "Management of asset performance throughout the life cycle", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/government-at-a-glance-2025_0efd0bcd-en/full-report/management-of-asset-performance-throughout-the-life-cycle_77aa88af.html"},
        {"title": "Enabling Inter-Municipal Shared Service Provision in Lithuania", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/enabling-inter-municipal-shared-service-provision-in-lithuania_f8ad6859-en.html"},
        {"title": "Municipal Finances: A Handbook for Local Governments", "publisher": "World Bank", "url": "https://documents.worldbank.org/en/publication/documents-reports/documentdetail/403951468180872451"}
    ]
}
,

"archive/821-dispute-resolution-chain-templates-for-cross-boundary-scope-forms-negotiation-ladders-mediation-expert-determination-jurisdiction-maps-continuity-orders-and-no-heavy-power-by-hostage-dispute.md": {
    "groups": [
        {"title": "European Charter of Local Self-Government (ETS No. 122)", "publisher": "Council of Europe", "url": "https://www.coe.int/en/web/conventions/full-list/-/conventions/treaty/122"},
        {"title": "Regulation (EC) No 1082/2006 on a European grouping of territorial cooperation (EGTC) — consolidated text", "publisher": "EUR-Lex / European Union", "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02006R1082-20140622"},
        {"title": "Governing together", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/governing-together_ff7c8ac4-en.html"},
        {"title": "Enabling Inter-Municipal Shared Service Provision in Lithuania", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/enabling-inter-municipal-shared-service-provision-in-lithuania_f8ad6859-en.html"},
        {"title": "Inter-municipal co-operation in the Western Balkans", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/inter-municipal-co-operation-in-the-western-balkans_67efc50a-en.html"},
        {"title": "Toolkit for Access to Justice and People-Centred Justice Systems", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/toolkit-for-access-to-justice-and-people-centred-justice-systems_aecf7f78-en.html"}
    ]
}
,

"archive/820-decision-rule-chain-templates-for-cross-boundary-scope-forms-ordinary-majorities-qualified-majorities-unanimity-reserves-deadlock-breakers-and-no-heavy-power-by-procedural-veto.md": {
    "groups": [
        {"title": "Regulation (EC) No 1082/2006 on a European grouping of territorial cooperation (EGTC) — consolidated text", "publisher": "EUR-Lex / European Union", "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02006R1082-20140622"},
        {"title": "International Practices of Metropolitan Governance", "publisher": "World Bank", "url": "https://documents.worldbank.org/en/publication/documents-reports/documentdetail/278861591018281649"},
        {"title": "Inter-municipal co-operation in the Western Balkans", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/inter-municipal-co-operation-in-the-western-balkans_67efc50a-en.html"},
        {"title": "Enabling Inter-Municipal Shared Service Provision in Lithuania", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/enabling-inter-municipal-shared-service-provision-in-lithuania_f8ad6859-en.html"},
        {"title": "Recommendation CM/Rec(2022)2 on democratic accountability of elected representatives and elected bodies at local and regional level", "publisher": "Council of Europe", "url": "https://search.coe.int/cm?i=0900001680a57739"}
    ]
}
,

"archive/819-boundary-and-membership-chain-templates-for-cross-boundary-scope-forms-accession-gates-territory-rules-amendment-thickness-exit-protocols-dissolution-paths-and-no-map-by-one-way-ratchet.md": {
    "groups": [
        {"title": "European Charter of Local Self-Government (ETS No. 122)", "publisher": "Council of Europe", "url": "https://www.coe.int/en/web/conventions/full-list/-/conventions/treaty/122"},
        {"title": "Explanatory Report to the European Charter of Local Self-Government", "publisher": "Council of Europe", "url": "https://rm.coe.int/16800ca437"},
        {"title": "Regulation (EC) No 1082/2006 on a European grouping of territorial cooperation (EGTC) — consolidated text", "publisher": "EUR-Lex / European Union", "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02006R1082-20140622"},
        {"title": "The EU-OECD Definition of a Functional Urban Area", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/the-eu-oecd-definition-of-a-functional-urban-area_d58cb34d-en.html"},
        {"title": "Governing the City", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/governing-the-city_9789264226500-en.html"},
        {"title": "International Practices of Metropolitan Governance", "publisher": "World Bank", "url": "https://documents.worldbank.org/en/publication/documents-reports/documentdetail/278861591018281649"}
    ]
}
,

"archive/818-information-chain-templates-for-cross-boundary-scope-forms-shared-facts-observatories-record-homes-official-statistics-links-publication-calendars-and-no-heavy-power-by-private-dashboard.md": {
    "groups": [
        {"title": "Fundamental Principles of Official Statistics", "publisher": "United Nations Statistics Division", "url": "https://unstats.un.org/unsd/dnss/gp/fundprinciples.aspx"},
        {"title": "OECD Local Data Portal", "publisher": "OECD", "url": "https://localdataportal.oecd.org/about.html"},
        {"title": "Methodology and sources", "publisher": "OECD Local Data Portal", "url": "https://localdataportal.oecd.org/methodology.html"},
        {"title": "A Guide to Setting up an Urban Observatory", "publisher": "UN-Habitat", "url": "https://unhabitat.org/a-guide-to-setting-up-an-urban-observatory"},
        {"title": "Urban Observatories - Urban Indicators Database", "publisher": "UN-Habitat", "url": "https://data.unhabitat.org/pages/urban-observatories"},
        {"title": "The Government Analytics Handbook", "publisher": "World Bank", "url": "https://www.worldbank.org/en/publication/government-analytics"},
        {"title": "European Charter of Local Self-Government (ETS No. 122)", "publisher": "Council of Europe", "url": "https://www.coe.int/en/web/conventions/full-list/-/conventions/treaty/122"}
    ]
}
,


"archive/817-participation-chain-templates-for-cross-boundary-scope-forms-open-dockets-hearings-user-councils-deliberative-mini-publics-response-ledgers-and-no-heavy-power-by-consultation-theater.md": {
    "groups": [
        {"title": "Additional Protocol to the European Charter of Local Self-Government on the right to participate in the affairs of a local authority (CETS No. 207)", "publisher": "Council of Europe", "url": "https://www.coe.int/en/web/conventions/full-list/-/conventions/treaty/207"},
        {"title": "Recommendation CM/Rec(2018)4 on the participation of citizens in local public life", "publisher": "Council of Europe", "url": "https://www.coe.int/en/web/youth/-/recommendation-on-the-participation-of-citizens-in-local-public-life"},
        {"title": "Recommendation of the Council on Open Government", "publisher": "OECD Legal Instruments", "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0438"},
        {"title": "OECD Guidelines for Citizen Participation Processes", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/oecd-guidelines-for-citizen-participation-processes_f765caf6-en.html"},
        {"title": "Open government and citizen participation", "publisher": "OECD", "url": "https://www.oecd.org/en/topics/open-government-and-citizen-participation.html"},
        {"title": "Recommendation CM/Rec(2023)6 on deliberative democracy", "publisher": "Council of Europe", "url": "https://search.coe.int/cm?i=0900001680ac627a"}
    ]
}
,

"archive/816-oversight-chain-templates-for-cross-boundary-scope-forms-member-scrutiny-external-audit-ombuds-routes-judicial-review-and-no-heavy-power-by-self-marking.md": {
    "groups": [
        {"title": "European Charter of Local Self-Government (ETS No. 122)", "publisher": "Council of Europe", "url": "https://www.coe.int/en/web/conventions/full-list/-/conventions/treaty/122"},
        {"title": "Recommendation CM/Rec(2019)3 on supervision of local authorities’ activities", "publisher": "Council of Europe", "url": "https://rm.coe.int/090000168093d066"},
        {"title": "Recommendation CM/Rec(2022)2 on democratic accountability of elected representatives and elected bodies at local and regional level", "publisher": "Council of Europe", "url": "https://rm.coe.int/0900001680a57739"},
        {"title": "Principles on the Protection and Promotion of the Ombudsman Institution (The Venice Principles)", "publisher": "Venice Commission / Council of Europe", "url": "https://www.venice.coe.int/webforms/documents/?pdf=CDL-AD%282019%29005-e"},
        {"title": "INTOSAI-P 1 – The Lima Declaration", "publisher": "INTOSAI", "url": "https://www.intosai.org/fileadmin/downloads/documents/open_access/INT_P_1_u_P_10/INTOSAI_P_1_en_2019.pdf"},
        {"title": "ISSAI 100 – Fundamental Principles of Public-Sector Auditing", "publisher": "INTOSAI", "url": "https://www.intosai.org/fileadmin/downloads/documents/open_access/ISSAI_100_to_400/issai_100/ISSAI_100_EN.pdf"},
        {"title": "Recommendation of the Council on Open Government", "publisher": "OECD Legal Instruments", "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0438"},
        {"title": "The OECD Metropolitan Governance Survey", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/the-oecd-metropolitan-governance-survey_5jz43zldh08p-en.html"}
    ]
}
,

"archive/815-administrative-chain-templates-for-cross-boundary-scope-forms-host-secretariats-principal-owned-backbones-chartered-operators-records-homes-and-no-heavy-power-by-borrowed-bureaucracy.md": {
    "groups": [
        {"title": "European Charter of Local Self-Government (ETS No. 122)", "publisher": "Council of Europe", "url": "https://www.coe.int/en/web/conventions/full-list/-/conventions/treaty/122"},
        {"title": "Enabling Inter-Municipal Shared Service Provision in Lithuania", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/enabling-inter-municipal-shared-service-provision-in-lithuania_f8ad6859-en.html"},
        {"title": "The OECD Metropolitan Governance Survey", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/the-oecd-metropolitan-governance-survey_5jz43zldh08p-en.html"},
        {"title": "Governing the City", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/governing-the-city_9789264226500-en.html"},
        {"title": "International Practices of Metropolitan Governance", "publisher": "World Bank", "url": "https://documents.worldbank.org/en/publication/documents-reports/documentdetail/278861591018281649"}
    ]
}
,

"archive/814-fiscal-chain-templates-for-cross-boundary-scope-forms-dues-and-service-payments-assigned-revenues-equalization-keys-capital-lanes-and-no-heavy-power-by-shadow-treasury.md": {
    "groups": [
        {"title": "European Charter of Local Self-Government (ETS No. 122)", "publisher": "Council of Europe", "url": "https://www.coe.int/en/web/conventions/full-list/-/conventions/treaty/122"},
        {"title": "Recommendation of the Council on Effective Public Investment Across Levels of Government", "publisher": "OECD Legal Instruments", "url": "https://legalinstruments.oecd.org/public/doc/302/a9a0bd09-2e76-4e68-9f15-84729cdbe829.htm"},
        {"title": "Enabling Inter-Municipal Shared Service Provision in Lithuania", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/enabling-inter-municipal-shared-service-provision-in-lithuania_f8ad6859-en.html"},
        {"title": "OECD Fiscal Decentralisation Database", "publisher": "OECD", "url": "https://www.oecd.org/en/data/datasets/oecd-fiscal-decentralisation-database.html"},
        {"title": "Going Granular with Regional and Municipal Fiscal Data", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/going-granular-with-regional-and-municipal-fiscal-data_8a17c019-en.html"},
        {"title": "International Practices of Metropolitan Governance", "publisher": "World Bank", "url": "https://documents.worldbank.org/en/publication/documents-reports/documentdetail/278861591018281649"},
        {"title": "Municipal Finances: A Handbook for Local Governments", "publisher": "World Bank", "url": "https://openknowledge.worldbank.org/entities/publication/baee6e22-9826-59ea-b070-e3d6ad5a5599"}
    ]
}
,
"archive/813-legitimacy-chain-templates-for-cross-boundary-scope-forms-delegated-councils-principal-owned-backbones-double-key-authorities-directly-elected-tiers-and-no-heavy-power-by-convenience-composition.md": {
    "groups": [
        {"title": "European Charter of Local Self-Government (ETS No. 122)", "publisher": "Council of Europe", "url": "https://www.coe.int/en/web/conventions/full-list/-/conventions/treaty/122"},
        {"title": "Regions and Cities - Where Policies and People Meet: Policy Briefs", "publisher": "OECD", "url": "https://www.oecd.org/content/dam/oecd/en/networks/high-level-meetings-of-the-rdpc/regions-and-cities-where-policies-and-people-meet-policy-briefs.pdf/_jcr_content/renditions/original./regions-and-cities-where-policies-and-people-meet-policy-briefs.pdf"},
        {"title": "Enabling Inter-Municipal Shared Service Provision in Lithuania", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/enabling-inter-municipal-shared-service-provision-in-lithuania_f8ad6859-en.html"},
        {"title": "Regional Governance in OECD Countries", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/regional-governance-in-oecd-countries_4d7c6483-en.html"},
        {"title": "Governing the City", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/governing-the-city_9789264226500-en.html"}
    ]
}
,

"archive/812-institutional-form-choice-ladders-for-ideal-governments-of-each-scope-thin-connectors-shared-service-backbones-bounded-authorities-general-purpose-tiers-and-no-new-tier-by-spillover-alone.md": {
    "groups": [
        {"title": "European Charter of Local Self-Government (ETS No. 122)", "publisher": "Council of Europe", "url": "https://www.coe.int/en/web/conventions/full-list/-/conventions/treaty/122"},
        {"title": "Recommendation of the Council on Effective Public Investment Across Levels of Government", "publisher": "OECD Legal Instruments", "url": "https://legalinstruments.oecd.org/public/doc/302/a9a0bd09-2e76-4e68-9f15-84729cdbe829.htm"},
        {"title": "Enabling Inter-Municipal Shared Service Provision in Lithuania", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/enabling-inter-municipal-shared-service-provision-in-lithuania_f8ad6859-en.html"},
        {"title": "Governing the City", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/governing-the-city_9789264226500-en.html"},
        {"title": "OECD Definition of Cities and Functional Urban Areas", "publisher": "OECD", "url": "https://www.oecd.org/en/data/datasets/oecd-definition-of-cities-and-functional-urban-areas.html"},
        {"title": "International Practices of Metropolitan Governance", "publisher": "World Bank", "url": "https://documents.worldbank.org/en/publication/documents-reports/documentdetail/278861591018281649"}
    ]
}
,

"archive/811-scope-verdict-packets-for-ideal-governments-of-each-scope-settled-holdings-frontier-thresholds-benchmark-findings-repair-routes-public-proof-and-no-applied-judgment-by-scattered-cross-reference.md": {
    "groups": [
        {"title": "Recommendation of the Council on Public Policy Evaluation", "publisher": "OECD Legal Instruments", "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0478"},
        {"title": "Implementation Toolkit for the OECD Recommendation on Public Policy Evaluation", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/implementation-toolkit-for-the-oecd-recommendation-on-public-policy-evaluation_77faa4fe-en.html"},
        {"title": "Development co-operation peer reviews and learning", "publisher": "OECD", "url": "https://www.oecd.org/en/topics/development-co-operation-peer-reviews-and-learning.html"},
        {"title": "Joint External Evaluation (JEE)", "publisher": "World Health Organization", "url": "https://www.who.int/emergencies/operations/international-health-regulations-monitoring-evaluation-framework/joint-external-evaluations"},
        {"title": "Recommendation of the Council on Open Government", "publisher": "OECD Legal Instruments", "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0438"}
    ]
}
,

"archive/810-threshold-dossiers-for-ideal-governments-of-each-scope-metro-triggers-county-pooling-regional-platform-proof-fiscal-floors-legitimacy-thickness-and-no-tier-thickening-by-anecdote.md": {
    "groups": [
        {"title": "OECD Definition of Cities and Functional Urban Areas", "publisher": "OECD", "url": "https://www.oecd.org/en/data/datasets/oecd-definition-of-cities-and-functional-urban-areas.html"},
        {"title": "Effective Public Investment Toolkit", "publisher": "OECD", "url": "https://www.oecd.org/en/about/projects/effective-public-investment-toolkit.html"},
        {"title": "Regional Governance in OECD Countries", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/regional-governance-in-oecd-countries_4d7c6483-en.html"},
        {"title": "OECD Fiscal Decentralisation Database", "publisher": "OECD", "url": "https://www.oecd.org/en/data/datasets/oecd-fiscal-decentralisation-database.html"},
        {"title": "European Charter of Local Self-Government (ETS No. 122)", "publisher": "Council of Europe", "url": "https://www.coe.int/en/web/conventions/full-list/-/conventions/treaty/122"},
        {"title": "International Practices of Metropolitan Governance", "publisher": "World Bank", "url": "https://documents.worldbank.org/en/publication/documents-reports/documentdetail/278861591018281649"}
    ]
}
,

"archive/809-research-frontier-for-ideal-governments-of-each-scope-settled-defaults-live-thresholds-morphology-uncertainty-fiscal-floor-tests-legitimacy-triggers-and-no-false-precision-by-constitutional-confidence-theater.md": {
    "groups": [
        {"title": "Making Decentralisation Work", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/making-decentralisation-work_g2g9faa7-en.html"},
        {"title": "Effective Public Investment Toolkit", "publisher": "OECD", "url": "https://www.oecd.org/en/about/projects/effective-public-investment-toolkit.html"},
        {"title": "European Charter of Local Self-Government (ETS No. 122)", "publisher": "Council of Europe", "url": "https://www.coe.int/en/web/conventions/full-list/-/conventions/treaty/122"},
        {"title": "Unpacking Metropolitan Governance for Sustainable Development", "publisher": "UN-Habitat / GIZ", "url": "https://unhabitat.org/sites/default/files/download-manager-files/Unpacking%20Metropolitan%20Governance.pdf"},
        {"title": "International Practices of Metropolitan Governance", "publisher": "World Bank", "url": "https://documents.worldbank.org/en/publication/documents-reports/documentdetail/278861591018281649"},
        {"title": "Approaches to Metropolitan Area Governance", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/approaches-to-metropolitan-area-governance_5jz5j1q7s128-en.html"}
    ]
}
,

"archive/807-assessment-team-independence-and-conflict-discipline-for-scope-reviews-recusal-rosters-secondment-firebreaks-host-picked-experts-donor-pathways-and-no-constitutional-judgment-by-interested-mission.md": {
    "groups": [
        {"title": "Government Auditing Standards (2024 Revision)", "publisher": "U.S. Government Accountability Office", "url": "https://www.gao.gov/assets/d24106786.pdf"},
        {"title": "Declaration of interests for experts", "publisher": "World Health Organization", "url": "https://www.who.int/about/ethics/declaration-of-interests"},
        {"title": "Guidelines for Managing Conflict of Interest in the Public Service", "publisher": "OECD Legal Instruments", "url": "https://legalinstruments.oecd.org/public/doc/130/130.en.pdf"},
        {"title": "European Code of Conduct for all Persons Involved in Local and Regional Governance", "publisher": "Council of Europe / Congress of Local and Regional Authorities", "url": "https://rm.coe.int/european-code-of-conduct-for-all-persons-involved-in-local-and-regiona/16808d3295"}
    ]
}
,

"archive/808-calibration-packs-moderation-loops-and-precedent-banks-for-scope-assessments-score-anchors-difficult-case-conferences-documented-departures-and-no-benchmark-by-reviewer-mood.md": {
    "groups": [
        {"title": "Government Auditing Standards (2024 Revision)", "publisher": "U.S. Government Accountability Office", "url": "https://www.gao.gov/assets/d24106786.pdf"},
        {"title": "DAC Peer Review Methodology, Updated 2023", "publisher": "OECD", "url": "https://one.oecd.org/document/DCD/DAC%282022%2957/FINAL/en/pdf"},
        {"title": "Handbook for Peer Reviews on Transparency and Exchange of Information on Request", "publisher": "OECD", "url": "https://www.oecd.org/content/dam/oecd/en/networks/global-forum-tax-transparency/handbook-for-peer-reviews-on-transparency-and-exchange-of-information-on-request.pdf"},
        {"title": "Methodology for Round 2 peer reviews and non-member reviews", "publisher": "OECD", "url": "https://www.oecd.org/tax/transparency/documents/methodology-eoir-peer-reviews-november-2021.pdf"},
        {"title": "Joint External Evaluation (JEE)", "publisher": "World Health Organization", "url": "https://www.who.int/emergencies/operations/international-health-regulations-monitoring-evaluation-framework/joint-external-evaluations"},
        {"title": "Interim manual for the performance evaluation of regulatory systems", "publisher": "World Health Organization", "url": "https://cdn.who.int/media/docs/default-source/medicines/regulatory-systems/manual-combined-rev1.pdf?download=true&sfvrsn=27547ada_8"}
    ]
}
,

"archive/806-evidence-registers-and-provenance-chains-for-scope-assessments-exhibit-ids-source-typing-redaction-ledgers-finding-links-and-no-verdict-by-orphaned-exhibit.md": {
    "groups": [
        {"title": "Yellow Book: Government Auditing Standards", "publisher": "U.S. Government Accountability Office", "url": "https://www.gao.gov/yellowbook"},
        {"title": "Assessing Data Reliability", "publisher": "U.S. Government Accountability Office", "url": "https://www.gao.gov/products/gao-20-283g"},
        {"title": "Country Implementation Guide Voluntary Joint External Evaluation (JEE)", "publisher": "World Health Organization", "url": "https://extranet.who.int/sph/sites/default/files/document-library/document/WHO-WHE-CPI-2017.62-eng.pdf"},
        {"title": "DAC Peer Review Methodology, Updated 2023", "publisher": "OECD", "url": "https://one.oecd.org/document/DCD/DAC%282022%2957/FINAL/en/pdf"},
        {"title": "Recommendation of the Council on Open Government", "publisher": "OECD Legal Instruments", "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0438"}
    ]
}
,

"archive/805-sampling-frames-and-case-selection-discipline-for-scope-assessments-risk-bands-ordinary-and-failed-routes-negative-cases-and-no-benchmark-by-showcase-tour.md": {
    "groups": [
        {"title": "Service Availability and Readiness Assessment (SARA)", "publisher": "World Health Organization", "url": "https://www.who.int/data/data-collection-tools/service-availability-and-readiness-assessment-%28sara%29"},
        {"title": "Quantitative Service Delivery Surveys (QSDS) study description", "publisher": "World Bank Microdata Library", "url": "https://microdata.worldbank.org/index.php/catalog/854/study-description"},
        {"title": "Public Expenditure Tracking Survey (PETS) study description", "publisher": "World Bank Microdata Library", "url": "https://microdata.worldbank.org/index.php/catalog/875"},
        {"title": "Assessing Data Reliability (Supersedes GAO-09-680G)", "publisher": "U.S. Government Accountability Office", "url": "https://www.gao.gov/products/gao-20-283g"},
        {"title": "Center for Audit Excellence — Using Sampling in Performance Audits", "publisher": "U.S. Government Accountability Office", "url": "https://www.gao.gov/about/what-gao-does/audit-role/cae"},
        {"title": "DAC Peer Review Methodology, Updated 2023", "publisher": "OECD", "url": "https://one.oecd.org/document/DCD/DAC%282022%2957/FINAL/en/pdf"}
    ]
}
,

"archive/804-tracer-routes-and-lived-path-verification-for-scope-governance-user-journeys-fund-flows-case-walks-handoff-tests-and-no-constitution-by-org-chart.md": {
    "groups": [
        {"title": "Service Availability and Readiness Assessment (SARA)", "publisher": "World Health Organization", "url": "https://www.who.int/data/data-collection-tools/service-availability-and-readiness-assessment-%28sara%29"},
        {"title": "Service Delivery Facility Surveys / PETS and QSDS overview", "publisher": "World Bank Microdata Library", "url": "https://microdata.worldbank.org/index.php/catalog/pets/about"},
        {"title": "Together for Better Public Services: Partnering with Citizens and Civil Society", "publisher": "OECD", "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2011/08/together-for-better-public-services-partnering-with-citizens-and-civil-society_g1g1472d/9789264118843-en.pdf"},
        {"title": "Implementation toolkit on legislative actions for consumer protection enforcement co-operation", "publisher": "OECD", "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2021/06/implementation-toolkit-on-legislative-actions-for-consumer-protection-enforcement-co-operation_1e0ccb4b/eddcdc57-en.pdf"}
    ]
}
,

"archive/803-close-out-verification-and-reopen-rules-for-scope-governance-repair-ledgers-mid-term-checks-field-revisit-residual-risk-and-no-closure-by-self-certification.md": {
    "groups": [
        {"title": "DAC Peer Review Methodology, Updated 2023", "publisher": "OECD", "url": "https://one.oecd.org/document/DCD/DAC%282022%2957/FINAL/en/pdf"},
        {"title": "Implementation Toolkit for the OECD Recommendation on Public Policy Evaluation", "publisher": "OECD", "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2025/02/implementation-toolkit-for-the-oecd-recommendation-on-public-policy-evaluation_f24516be/77faa4fe-en.pdf"},
        {"title": "Postmonitoring of the Charter and postelectoral dialogue", "publisher": "Council of Europe / Congress of Local and Regional Authorities", "url": "https://www.coe.int/en/web/congress/postmonitoring-and-postelectoral-dialogue"},
        {"title": "Monitoring of the European Charter of Local Self-Government", "publisher": "Council of Europe / Congress of Local and Regional Authorities", "url": "https://www.coe.int/en/web/congress/monitoring-of-the-european-charter-of-local-self-government"},
        {"title": "After action review", "publisher": "World Health Organization", "url": "https://www.who.int/emergencies/operations/emergency-response-reviews/after-action-review"},
        {"title": "National Action Plan for Health Security", "publisher": "World Health Organization", "url": "https://www.who.int/emergencies/operations/international-health-regulations-monitoring-evaluation-framework/national-action-plan-for-health-security"},
        {"title": "IHR Monitoring and Evaluation Framework", "publisher": "World Health Organization", "url": "https://extranet.who.int/sph/ihr-monitoring-evaluation"},
        {"title": "Documenting Progress following the Joint External Evaluation (JEE) and Implementation of the National Action Plan for Health Security (NAPHS) in the Republic of Sierra Leone", "publisher": "World Health Organization", "url": "https://extranet.who.int/sph/documenting-progress-following-joint-external-evaluation-jee-and-implementation-national-action"},
        {"title": "Disaster Resilience Scorecard for Cities", "publisher": "UNDRR / MCR2030", "url": "https://mcr2030.undrr.org/disaster-resilience-scorecard-cities"},
        {"title": "Resilience Roadmap Stage B", "publisher": "UNDRR / MCR2030", "url": "https://mcr2030.undrr.org/resilience-roadmap/stage-b"}
    ]
}
,




"archive/802-management-responses-and-corrective-action-ledgers-for-scope-governance-finding-by-finding-owners-dependencies-budget-closure-proof-and-no-verdict-without-a-repair-docket.md": {
    "groups": [
        {"title": "Monitoring of the European Charter of Local Self-Government", "publisher": "Council of Europe / Congress of Local and Regional Authorities", "url": "https://www.coe.int/en/web/congress/monitoring-of-the-european-charter-of-local-self-government"},
        {"title": "Postmonitoring of the Charter and postelectoral dialogue", "publisher": "Council of Europe / Congress of Local and Regional Authorities", "url": "https://www.coe.int/en/web/congress/postmonitoring-and-postelectoral-dialogue"},
        {"title": "Joint External Evaluations", "publisher": "World Health Organization", "url": "https://www.who.int/emergencies/operations/international-health-regulations-monitoring-evaluation-framework/joint-external-evaluations"},
        {"title": "National Action Planning for Health Security", "publisher": "World Health Organization", "url": "https://www.who.int/emergencies/operations/international-health-regulations-monitoring-evaluation-framework/national-action-plan-for-health-security"},
        {"title": "National Action Plan for Health Security (NAPHS) tool", "publisher": "World Health Organization Regional Office for Europe", "url": "https://www.who.int/europe/tools-and-toolkits/naphs-tool"},
        {"title": "Improving Governance with Policy Evaluation", "publisher": "OECD", "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2020/06/improving-governance-with-policy-evaluation_040f9225/89b1577d-en.pdf"},
        {"title": "Public policy evaluation", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/government-at-a-glance-2025_0efd0bcd-en/full-report/public-policy-evaluation_e59d50bb.html"},
        {"title": "Recommendation of the Council on Public Policy Evaluation", "publisher": "OECD Legal Instruments", "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0478"},
        {"title": "The Disaster Resilience Scorecard for Cities – Action Guide. Chapter 2: How to create a prioritized action plan and prepare projects", "publisher": "UNDRR / MCR2030", "url": "https://mcr2030.undrr.org/publications/scorecard-actionguide-ch2"}
    ]
}
,

"archive/801-finding-registers-for-scope-assessments-lane-specific-scores-confidence-classes-severity-clocks-contradiction-residue-and-no-constitutional-verdict-by-blended-number.md": {
    "groups": [
        {"title": "Applying Evaluation Criteria Thoughtfully", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/applying-evaluation-criteria-thoughtfully_543e84ed-en.html"},
        {"title": "Recommendation of the Council on Public Policy Evaluation", "publisher": "OECD Legal Instruments", "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0478"},
        {"title": "Joint External Evaluation (JEE)", "publisher": "World Health Organization", "url": "https://www.who.int/emergencies/operations/international-health-regulations-monitoring-evaluation-framework/joint-external-evaluations"},
        {"title": "Joint external evaluation of International Health Regulations (2005) core capacities of Samoa: mission report", "publisher": "World Health Organization", "url": "https://extranet.who.int/sph/sites/default/files/2025-02/JEE%20Report%20Samoa%202023.pdf"},
        {"title": "Disaster Resilience Scorecard for Cities", "publisher": "UNDRR / MCR2030", "url": "https://mcr2030.undrr.org/disaster-resilience-scorecard-cities"},
        {"title": "Monitoring of the European Charter of Local Self-Government", "publisher": "Council of Europe / Congress of Local and Regional Authorities", "url": "https://www.coe.int/en/web/congress/monitoring-of-the-european-charter-of-local-self-government"}
    ]
}
,


"archive/800-assessment-missions-for-ideal-governments-by-scope-self-assessment-desk-review-site-visits-public-hearings-evidence-rooms-management-response-and-no-benchmark-by-questionnaire-alone.md": {
    "groups": [
        {"title": "Monitoring of the European Charter of Local Self-Government", "publisher": "Council of Europe / Congress of Local and Regional Authorities", "url": "https://www.coe.int/en/web/congress/monitoring-of-the-european-charter-of-local-self-government"},
        {"title": "Joint External Evaluations", "publisher": "World Health Organization", "url": "https://www.who.int/emergencies/operations/international-health-regulations-monitoring-evaluation-framework/joint-external-evaluations"},
        {"title": "International Health Regulations (IHR): Joint External Evaluation (JEE): Country Implementation Guide", "publisher": "World Health Organization", "url": "https://extranet.who.int/sph/sites/default/files/document-library/document/WHO-WHE-CPI-2017.62-eng.pdf"},
        {"title": "Disaster Resilience Scorecard for Cities", "publisher": "UNDRR / MCR2030", "url": "https://mcr2030.undrr.org/disaster-resilience-scorecard-cities"},
        {"title": "OECD Public Governance Reviews", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/oecd-public-governance-reviews_22190414.html"},
        {"title": "DAC Peer Review Methodology, Updated 2023", "publisher": "OECD", "url": "https://one.oecd.org/document/DCD/DAC%282022%2957/FINAL/en/pdf"},
        {"title": "Public policy evaluation", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/government-at-a-glance-2025_0efd0bcd-en/full-report/public-policy-evaluation_e59d50bb.html"},
        {"title": "Implementation Toolkit for the OECD Recommendation on Public Policy Evaluation", "publisher": "OECD", "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2025/02/implementation-toolkit-for-the-oecd-recommendation-on-public-policy-evaluation_f24516be/77faa4fe-en.pdf"}
    ]
}
,
"archive/799-sunset-renewal-graduation-and-burial-rules-for-temporary-scope-arrangements-bridges-pilots-derogations-special-measures-and-no-shadow-constitution-by-serial-extension.md": {
    "groups": [
        {"title": "The Updated Rule of Law Checklist", "publisher": "Venice Commission", "url": "https://www.venice.coe.int/webforms/documents/default.aspx?pdffile=CDL-AD%282025%29002-e"},
        {"title": "European Charter of Local Self-Government", "publisher": "Council of Europe", "url": "https://rm.coe.int/european-charter-of-local-self-government-eng/1680a87cc3"},
        {"title": "Recommendation CM/Rec(2019)3 of the Committee of Ministers to member States on supervision of local authorities’ activities", "publisher": "Council of Europe", "url": "https://rm.coe.int/090000168093d066"},
        {"title": "OECD Regulatory Policy Outlook 2021", "publisher": "OECD", "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2021/10/oecd-regulatory-policy-outlook-2021_c5274577/38b0fdb1-en.pdf"},
        {"title": "Better Regulation Guidelines", "publisher": "European Commission", "url": "https://commission.europa.eu/document/download/a83f6d6c-aff1-4d84-8c29-61722b7c969e_en?filename=better-regulation-guidelines.pdf"},
        {"title": "Regulatory experimentation: Moving Ahead on the Agile Regulatory Governance Agenda", "publisher": "OECD", "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2024/04/regulatory-experimentation_fc84553c/f193910c-en.pdf"}
    ]
}
,

"archive/798-reference-classes-and-comparator-cohorts-for-ideal-governments-by-scope-morphology-matched-peers-functional-territories-capacity-bands-and-no-benchmark-by-postcard.md": {
    "groups": [
        {"title": "OECD Definition of Cities and Functional Urban Areas", "publisher": "OECD", "url": "https://www.oecd.org/en/data/datasets/oecd-definition-of-cities-and-functional-urban-areas.html"},
        {"title": "OECD Geographical Definitions", "publisher": "OECD", "url": "https://www.oecd.org/en/data/datasets/oecd-geographical-definitions.html"},
        {"title": "OECD Regions and Cities at a Glance 2024", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/oecd-regions-and-cities-at-a-glance-2024_f42db3bf-en.html"},
        {"title": "Methodology - Degree of urbanisation", "publisher": "Eurostat", "url": "https://ec.europa.eu/eurostat/web/degree-of-urbanisation/methodology"},
        {"title": "Applying the Degree of Urbanisation — A methodological manual to define cities, towns and rural areas", "publisher": "UN-Habitat", "url": "https://unhabitat.org/applying-the-degree-of-urbanisation-a-methodological-manual-to-define-cities-towns-and-rural-areas"},
        {"title": "Subnational finance and investment", "publisher": "OECD", "url": "https://www.oecd.org/en/topics/subnational-finance-and-investment.html"},
        {"title": "2022 Synthesis Report World Observatory on Subnational Government Finance and Investment", "publisher": "OECD / UCLG", "url": "https://www.oecd.org/en/publications/2022-synthesis-report-world-observatory-on-subnational-government-finance-and-investment_b80a8cdb-en.html"}
    ]
}
,

"archive/794-sequenced-upgrade-paths-for-ideal-governments-of-each-scope-first-honest-steps-bridge-arrangements-cutover-gates-and-no-full-stack-redesign-by-manifesto.md": {
    "groups": [
        {"title": "Making Decentralisation Work", "publisher": "OECD", "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2019/03/making-decentralisation-work_g1g9faa7/g2g9faa7-en.pdf"},
        {"title": "Multi-level Governance Reforms: Overview of OECD Country Experiences", "publisher": "OECD", "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2017/05/multi-level-governance-reforms_g1g77b03/9789264272866-en.pdf"},
        {"title": "Recommendation of the Council on Effective Public Investment Across Levels of Government", "publisher": "OECD Legal Instruments", "url": "https://legalinstruments.oecd.org/Public/Info.aspx?infoRef=C%282014%2932&lang=en"},
        {"title": "Effective Public Investment Toolkit", "publisher": "OECD", "url": "https://www.oecd.org/en/about/projects/effective-public-investment-toolkit.html"},
        {"title": "A contemporary commentary by the Congress on the Explanatory Report to the European Charter of Local Self-Government", "publisher": "Council of Europe", "url": "https://rm.coe.int/09000016809ed6de"},
        {"title": "Opinion on the local self-government part of the draft Roadmap on Good Democratic Governance in Ukraine", "publisher": "Council of Europe", "url": "https://rm.coe.int/coe-opinion-ceggpad-2023-4-reform-roadmap-eng-fin-/48802a90e1"},
        {"title": "An Introduction to Decentralization, Multi-Level Governance, and Intergovernmental Relations: A Toolkit for Intergovernmental Architecture Analysis", "publisher": "World Bank", "url": "https://documents1.worldbank.org/curated/en/921721625759457018/pdf/An-Introduction-to-Decentralization-Multi-Level-Governance-and-Intergovernmental-Relations-A-Toolkit-for-Intergovernmental-Architecture-Analysis.pdf"}
    ]
}
,

"archive/793-maintenance-calendars-for-ideal-governments-of-each-scope-benchmark-refresh-stress-drill-cadence-trigger-overrides-public-registries-and-no-constitutional-care-by-sporadic-panic.md": {
    "groups": [
        {"title": "A contemporary commentary by the Congress on the Explanatory Report to the European Charter of Local Self-Government", "publisher": "Council of Europe", "url": "https://rm.coe.int/09000016809ed6de"},
        {"title": "Recurring issues based on assessments resulting from Congress monitoring and election observation missions (reference period 2021-2024)", "publisher": "Council of Europe", "url": "https://rm.coe.int/recurring-issues-based-on-assessments-resulting-from-congress-monitori/1680b1ccaf"},
        {"title": "Recommendation of the Council on Public Policy Evaluation", "publisher": "OECD Legal Instruments", "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0478"},
        {"title": "Effective Public Investment Toolkit", "publisher": "OECD", "url": "https://www.oecd.org/en/about/projects/effective-public-investment-toolkit.html"},
        {"title": "IHR Monitoring and Evaluation Framework", "publisher": "World Health Organization", "url": "https://extranet.who.int/sph/ihr-monitoring-evaluation"},
        {"title": "Disaster Resilience Scorecard for Cities", "publisher": "UNDRR / MCR2030", "url": "https://mcr2030.undrr.org/disaster-resilience-scorecard-cities"},
        {"title": "The Disaster Resilience Scorecard for Cities – Action Guide. Chapter 1: Overview of the survey results", "publisher": "UNDRR", "url": "https://www.undrr.org/publication/scorecard-actionguide-ch1"}
    ]
}
,

"archive/792-stress-test-and-drill-cards-for-ideal-governments-of-each-scope-essential-service-continuity-command-legibility-fiscal-buffers-rights-discipline-rescoping-signals-and-no-paper-constitution-by-calm-weather.md": {
    "groups": [
        {"title": "European Charter of Local Self-Government", "publisher": "Council of Europe", "url": "https://rm.coe.int/european-charter-of-local-self-government-eng/1680a87cc3"},
        {"title": "Recommendation of the Council on the Governance of Critical Risks", "publisher": "OECD Legal Instruments", "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0405"},
        {"title": "Recommendation of the Council on Effective Public Investment Across Levels of Government", "publisher": "OECD Legal Instruments", "url": "https://legalinstruments.oecd.org/Public/Info.aspx?infoRef=C%282014%2932&lang=en"},
        {"title": "Improving subnational governments' resilience in the wake of the COVID-19 pandemic", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/improving-subnational-governments-resilience-in-the-wake-of-the-covid-19-pandemic_6b1304c8-en.html"},
        {"title": "Sendai Framework for Disaster Risk Reduction 2015-2030", "publisher": "UNDRR", "url": "https://www.undrr.org/publication/sendai-framework-disaster-risk-reduction-2015-2030"},
        {"title": "International Health Regulations", "publisher": "World Health Organization", "url": "https://www.who.int/health-topics/international-health-regulations"},
        {"title": "Toolkit for local implementation of the IHR", "publisher": "WHO EMRO", "url": "https://www.emro.who.int/international-health-regulations/ihr-news/toolkit-for-local-implementation-of-the-ihr.html"}
    ]
}
,

"archive/791-benchmark-cards-for-ideal-governments-of-each-scope-vocation-fit-kit-floors-fiscal-congruence-review-lanes-tripwires-and-no-admiration-without-scoring.md": {
    "groups": [
        {"title": "European Charter of Local Self-Government", "publisher": "Council of Europe", "url": "https://www.coe.int/en/web/impact-convention-human-rights/european-charter-of-local-self-government"},
        {"title": "OECD Principles on Urban Policy", "publisher": "OECD", "url": "https://www.oecd.org/en/about/programmes/oecd-programme-on-national-urban-policy/oecd-principles-on-urban-policy.html"},
        {"title": "Recommendation of the Council on Effective Public Investment Across Levels of Government", "publisher": "OECD Legal Instruments", "url": "https://legalinstruments.oecd.org/Public/Info.aspx?infoRef=C%282014%2932&lang=en"},
        {"title": "Recommendation of the Council on Regional Development Policy", "publisher": "OECD", "url": "https://www.oecd.org/en/about/projects/implementing-the-oecd-recommendation-on-regional-development-policy-toolkit.html"},
        {"title": "United Nations Charter", "publisher": "United Nations", "url": "https://www.un.org/en/about-us/un-charter"},
        {"title": "International Health Regulations", "publisher": "World Health Organization", "url": "https://www.who.int/health-topics/international-health-regulations"}
    ]
}
,


"archive/797-contestability-ladders-for-scope-governance-benchmark-objections-trigger-appeals-intervention-review-handback-denials-and-no-constitutional-maintenance-by-self-marking.md": {
    "groups": [
        {"title": "European Charter of Local Self-Government", "publisher": "Council of Europe", "url": "https://rm.coe.int/european-charter-of-local-self-government-eng/1680a87cc3"},
        {"title": "Explanatory Report to the European Charter of Local Self-Government", "publisher": "Council of Europe", "url": "https://rm.coe.int/16800ca437"},
        {"title": "A contemporary commentary by the Congress on the Explanatory Report to the European Charter of Local Self-Government", "publisher": "Council of Europe", "url": "https://rm.coe.int/09000016809ed6de"},
        {"title": "The Updated Rule of Law Checklist", "publisher": "Venice Commission", "url": "https://www.venice.coe.int/webforms/documents/default.aspx?pdffile=CDL-AD%282025%29002-e"},
        {"title": "Recommendation of the Council on Open Government", "publisher": "OECD Legal Instruments", "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0438"}
    ]
}
,

"archive/796-intervention-ladders-for-failing-governments-of-each-scope-support-first-proportional-supervision-special-measures-handback-clocks-and-no-permanent-emergency-custody.md": {
    "groups": [
        {"title": "European Charter of Local Self-Government", "publisher": "Council of Europe", "url": "https://rm.coe.int/european-charter-for-local-self-government-english-version-pdf-a6-59-p/16807198a3"},
        {"title": "Explanatory Report to the European Charter of Local Self-Government", "publisher": "Council of Europe", "url": "https://rm.coe.int/16800ca437"},
        {"title": "Supervision and auditing of local authorities' action", "publisher": "Council of Europe", "url": "https://rm.coe.int/1680748104"},
        {"title": "Assigning responsibilities across levels of government", "publisher": "OECD", "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2018/09/assigning-responsibilities-across-levels-of-government_d3650b01/f0944eae-en.pdf"},
        {"title": "Making Decentralisation Work", "publisher": "OECD", "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2019/03/making-decentralisation-work_g1g9faa7/g2g9faa7-en.pdf"},
        {"title": "An Introduction to Decentralization, Multi-Level Governance, and Intergovernmental Relations: A Toolkit for Intergovernmental Architecture Analysis", "publisher": "World Bank", "url": "https://documents1.worldbank.org/curated/en/921721625759457018/pdf/An-Introduction-to-Decentralization-Multi-Level-Governance-and-Intergovernmental-Relations-A-Toolkit-for-Intergovernmental-Architecture-Analysis.pdf"}
    ]
}
,

"archive/795-public-proof-packs-for-ideal-governments-of-each-scope-benchmark-publication-stress-summaries-maintenance-ledgers-transition-boards-and-no-constitutional-claim-without-outward-evidence.md": {
    "groups": [
        {"title": "Recommendation of the Council on Open Government", "publisher": "OECD Legal Instruments", "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0438"},
        {"title": "Transparency of public information", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/government-at-a-glance-2025_0efd0bcd-en/full-report/transparency-of-public-information_60a963c4.html"},
        {"title": "Access to official documents", "publisher": "Council of Europe", "url": "https://www.coe.int/en/web/human-rights-intergovernmental-cooperation/-/access-to-official-documents"},
        {"title": "International Health Regulations Monitoring and Evaluation Framework", "publisher": "World Health Organization", "url": "https://www.who.int/emergencies/operations/international-health-regulations-monitoring-evaluation-framework"},
        {"title": "Disaster Resilience Scorecard for Cities", "publisher": "UNDRR / MCR2030", "url": "https://mcr2030.undrr.org/disaster-resilience-scorecard-cities"}
    ]
}
,



"archive/789-impartial-decision-maker-separation-of-functions-and-ex-parte-contact-necessity-tests-for-ideal-governments-recusal-staff-firebreaks-record-discipline-and-no-adjudication-by-backstage-influence.md": {
    "groups": [
        {"title": "The administration and you — a handbook", "publisher": "Council of Europe", "url": "https://rm.coe.int/eng-handbook-on-administration/1680a03ee2"},
        {"title": "The Principles of Public Administration", "publisher": "OECD / SIGMA", "url": "https://www.sigmaweb.org/content/dam/sigma/en/publications/reports/2023/11/the-principles-of-public-administration_5e68f805/7f5ec453-en.pdf"},
        {"title": "Administrative Procedure Act", "publisher": "United States Department of Justice", "url": "https://www.justice.gov/sites/default/files/jmd/legacy/2014/05/01/act-pl79-404.pdf"},
        {"title": "Statement of Principles for Administrative Adjudication", "publisher": "ACUS", "url": "https://www.acus.gov/sites/default/files/documents/SOP-Administrative-Adjudication-2026.02.05.pdf"},
        {"title": "Best Practices for Adjudication Not Involving an Evidentiary Hearing", "publisher": "ACUS", "url": "https://www.acus.gov/document/best-practices-adjudication-not-involving-evidentiary-hearing"},
        {"title": "Federal Administrative Adjudication Outside the Administrative Procedure Act", "publisher": "ACUS", "url": "https://www.acus.gov/sites/default/files/documents/Federal%20Administrative%20Adj%20Outside%20the%20APA%20-%20Final.pdf"}
    ]
}
,

"archive/788-representation-counsel-nonlawyer-assistance-and-support-person-necessity-tests-for-ideal-governments-choice-capacity-qualification-confidentiality-and-no-rights-by-solo-navigation.md": {
    "groups": [
        {"title": "The administration and you — a handbook", "publisher": "Council of Europe", "url": "https://rm.coe.int/eng-handbook-on-administration/1680a03ee2"},
        {"title": "Guidelines on the efficiency and the effectiveness of legal aid schemes in the areas of civil and administrative law", "publisher": "Council of Europe", "url": "https://search.coe.int/cm?i=0900001680a39918"},
        {"title": "A regulation for an open, efficient and independent European Union administration", "publisher": "European Parliament", "url": "https://www.europarl.europa.eu/cmsdata/95453/regulation.PDF"},
        {"title": "Administrative Procedure Act", "publisher": "United States Department of Justice", "url": "https://www.justice.gov/sites/default/files/jmd/legacy/2014/05/01/act-pl79-404.pdf"},
        {"title": "Nonlawyer Assistance and Representation in Agency Adjudications", "publisher": "ACUS", "url": "https://www.acus.gov/projects/nonlawyer-assistance-and-representation-agency-adjudications"}
    ]
}
,

"archive/787-language-interpretation-plain-language-and-accessible-format-necessity-tests-for-ideal-governments-comprehension-duty-translation-thresholds-and-no-rights-by-unreadable-procedure.md": {
    "groups": [
        {"title": "The administration and you — a handbook", "publisher": "Council of Europe", "url": "https://rm.coe.int/eng-handbook-on-administration/1680a03ee2"},
        {"title": "Recommendation CM/Rec(2007)7 on good administration", "publisher": "Council of Europe", "url": "https://rm.coe.int/cmrec-2007-7-of-the-cm-to-ms-on-good-administration/16809f007c"},
        {"title": "Toolkit for Access to Justice and People-Centred Justice Systems", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/toolkit-for-access-to-justice-and-people-centred-justice-systems_aecf7f78-en.html"},
        {"title": "Government at a Glance 2025", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/government-at-a-glance-2025_0efd0bcd-en.html"},
        {"title": "Convention on the Rights of Persons with Disabilities", "publisher": "OHCHR", "url": "https://www.ohchr.org/en/instruments-mechanisms/instruments/convention-rights-persons-disabilities"},
        {"title": "The Single Digital Gateway in the Western Balkans", "publisher": "OECD / SIGMA", "url": "https://www.oecd.org/en/publications/the-single-digital-gateway-in-the-western-balkans_3cbd03cd-en.html"}
    ]
}
,

"archive/786-right-to-be-heard-and-oral-hearing-necessity-tests-for-ideal-governments-notice-of-adverse-case-paper-default-credibility-triggers-remote-option-and-no-decision-by-unanswered-file.md": {
    "groups": [
        {"title": "Recommendation CM/Rec(2007)7 on good administration", "publisher": "Council of Europe", "url": "https://rm.coe.int/cmrec-2007-7-of-the-cm-to-ms-on-good-administration/16809f007c"},
        {"title": "The administration and you — a handbook", "publisher": "Council of Europe", "url": "https://rm.coe.int/eng-handbook-on-administration/1680a03ee2"},
        {"title": "Checklist for a General Law on Administrative Procedures", "publisher": "OECD / SIGMA", "url": "https://www.sigmaweb.org/content/dam/sigma/en/documents/2005/Checklist-for-a-General-Law-on-Administrative-Procedures.pdf"},
        {"title": "Implementation of laws on general administrative procedure in the Western Balkans", "publisher": "OECD / SIGMA", "url": "https://one.oecd.org/document/GOV/SIGMA(2021)2/en/pdf"},
        {"title": "The Principles of Public Administration", "publisher": "OECD / SIGMA", "url": "https://www.sigmaweb.org/content/dam/sigma/en/publications/reports/2023/11/the-principles-of-public-administration_5e68f805/7f5ec453-en.pdf"},
        {"title": "Guide for Remote Hearings", "publisher": "Council of Europe / CEPEJ", "url": "https://rm.coe.int/cepej-2025-3-en-guide-for-remote-hearings-2763-8911-6430-1/1680b6bb7b"}
    ]
}
,

"archive/785-administrative-fact-finding-evidentiary-burden-and-duty-to-assist-necessity-tests-for-ideal-governments-ex-officio-records-proof-alternatives-and-no-rights-by-impossible-evidence.md": {
    "groups": [
        {"title": "The administration and you — a handbook", "publisher": "Council of Europe", "url": "https://rm.coe.int/eng-handbook-on-administration/1680a03ee2"},
        {"title": "Recommendation CM/Rec(2007)7 on good administration", "publisher": "Council of Europe", "url": "https://rm.coe.int/cmrec-2007-7-of-the-cm-to-ms-on-good-administration/16809f007c"},
        {"title": "Checklist for a General Law on Administrative Procedures", "publisher": "OECD / SIGMA", "url": "https://www.sigmaweb.org/content/dam/sigma/en/documents/2005/Checklist-for-a-General-Law-on-Administrative-Procedures.pdf"},
        {"title": "Procedural Fairness: Issues in Civil and Administrative Enforcement Proceedings", "publisher": "OECD", "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2011/10/procedural-fairness-issues-in-civil-and-administrative-enforcement-proceedings_e727ebdc/78c4eb25-en.pdf"},
        {"title": "Toolkit for Access to Justice and People-Centred Justice Systems", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/toolkit-for-access-to-justice-and-people-centred-justice-systems_aecf7f78-en.html"},
        {"title": "ReNEUAL Model Rules on EU Administrative Procedure", "publisher": "ReNEUAL", "url": "https://www.reneual.eu/images/Home/ReNEUAL--Model-Rules-update-2015_rules-only-2017.PDF"}
    ]
}
,

"archive/784-administrative-consistency-equal-treatment-and-reasoned-departure-necessity-tests-for-ideal-governments-like-cases-alike-public-memory-and-no-random-walk-administration.md": {
    "groups": [
        {"title": "Recommendation CM/Rec(2007)7 on good administration", "publisher": "Council of Europe", "url": "https://rm.coe.int/cmrec-2007-7-of-the-cm-to-ms-on-good-administration/16809f007c"},
        {"title": "The administration and you — a handbook", "publisher": "Council of Europe", "url": "https://rm.coe.int/eng-handbook-on-administration/1680a03ee2"},
        {"title": "The European Code of Good Administrative Behaviour", "publisher": "European Ombudsman", "url": "https://www.ombudsman.europa.eu/en/document/en/3510"},
        {"title": "OECD Regulatory Enforcement and Inspections Toolkit", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/oecd-regulatory-enforcement-and-inspections-toolkit_9789264303959-en.html"},
        {"title": "The Principles of Public Administration", "publisher": "OECD / SIGMA", "url": "https://www.sigmaweb.org/publications/principles-public-administration.htm"},
        {"title": "ReNEUAL Model Rules on EU Administrative Procedure", "publisher": "ReNEUAL", "url": "https://www.reneual.eu/images/Home/ReNEUAL--Model-Rules-update-2015_rules-only-2017.PDF"}
    ]
}
,

"archive/783-legitimate-expectations-reliance-and-fair-frustration-necessity-tests-for-ideal-governments-clear-assurances-transition-relief-proportionate-reversal-and-no-bait-and-switch-state.md": {
    "groups": [
        {"title": "The administration and you — a handbook", "publisher": "Council of Europe", "url": "https://rm.coe.int/eng-handbook-on-administration/1680a03ee2"},
        {"title": "ReNEUAL Model Rules on EU Administrative Procedure", "publisher": "ReNEUAL", "url": "https://www.reneual.eu/images/Home/ReNEUAL--Model-Rules-update-2015_rules-only-2017.PDF"},
        {"title": "Recommendation CM/Rec(2007)7 on good administration", "publisher": "Council of Europe", "url": "https://rm.coe.int/cmrec-2007-7-of-the-cm-to-ms-on-good-administration/16809f007c"},
        {"title": "The Principles of Public Administration", "publisher": "OECD / SIGMA", "url": "https://www.sigmaweb.org/content/dam/sigma/en/publications/reports/2023/11/the-principles-of-public-administration_5e68f805/7f5ec453-en.pdf"},
        {"title": "OECD Regulatory Policy Outlook 2025", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/oecd-regulatory-policy-outlook-2025_56b60e39-en.html"}
    ]
}
,

"archive/782-administrative-guidance-circulars-and-soft-law-necessity-tests-for-ideal-governments-publicity-legal-status-clarity-consultable-updates-and-no-hidden-law-by-guidance.md": {
    "groups": [
        {"title": "OECD Regulatory Enforcement and Inspections Toolkit", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/oecd-regulatory-enforcement-and-inspections-toolkit_9789264303959-en.html"},
        {"title": "Best practice principles for licensing and permitting", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/best-practice-principles-for-licensing-and-permitting_5f63586d-en/full-report.html"},
        {"title": "OECD Regulatory Policy Outlook 2025", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/oecd-regulatory-policy-outlook-2025_56b60e39-en.html"},
        {"title": "Recommendation CM/Rec(2007)7 on good administration", "publisher": "Council of Europe", "url": "https://rm.coe.int/cmrec-2007-7-of-the-cm-to-ms-on-good-administration/16809f007c"},
        {"title": "The administration and you — a handbook", "publisher": "Council of Europe", "url": "https://rm.coe.int/eng-handbook-on-administration/1680a03ee2"}
    ]
}
,

"archive/781-administrative-self-correction-reopening-withdrawal-and-revocation-necessity-tests-for-ideal-governments-clerical-fix-benefit-reliance-unlawful-act-recall-reasons-and-no-stability-by-known-error.md": {
    "groups": [
        {"title": "The administration and you — a handbook", "publisher": "Council of Europe", "url": "https://rm.coe.int/eng-handbook-on-administration/1680a03ee2"},
        {"title": "Recommendation CM/Rec(2007)7 on good administration", "publisher": "Council of Europe", "url": "https://rm.coe.int/cmrec-2007-7-of-the-cm-to-ms-on-good-administration/16809f007c"},
        {"title": "ReNEUAL Model Rules on EU Administrative Procedure", "publisher": "ReNEUAL", "url": "https://www.reneual.eu/images/Home/ReNEUAL-Model_Rules-Compilation_BooksI_VI_2014-09-03.pdf"},
        {"title": "The Pan-European General Principles on Non-Judicial Administrative Appeals", "publisher": "ReNEUAL", "url": "https://www.reneual.eu/projects-and-publications/reneual-2-0?catid=2&id=36&view=article"},
        {"title": "Guide to Good Administrative Procedures for Egypt", "publisher": "SIGMA", "url": "https://www.sigmaweb.org/content/dam/sigma/en/documents/2018/Guide-I_Good-Administration-Procedures-for-Egypt_EN.pdf"}
    ]
}
,

"archive/780-administrative-silence-and-tacit-decisions-necessity-tests-for-ideal-governments-clear-defaults-escalation-non-silence-for-high-risk-acts-and-no-government-by-non-reply.md": {
    "groups": [
        {"title": "Recommendation CM/Rec(2007)7 on good administration", "publisher": "Council of Europe", "url": "https://rm.coe.int/cmrec-2007-7-of-the-cm-to-ms-on-good-administration/16809f007c"},
        {"title": "The administration and you — a handbook", "publisher": "Council of Europe", "url": "https://rm.coe.int/eng-handbook-on-administration/1680a03ee2"},
        {"title": "Toolkit for Access to Justice and People-Centred Justice Systems", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/toolkit-for-access-to-justice-and-people-centred-justice-systems_aecf7f78-en.html"},
        {"title": "The Single Digital Gateway in the Western Balkans", "publisher": "OECD / SIGMA", "url": "https://www.oecd.org/en/publications/the-single-digital-gateway-in-the-western-balkans_3cbd03cd-en.html"},
        {"title": "Business Licensing Reforms in Romania", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/business-licensing-reforms-in-romania_be4f13bb-en.html"}
    ]
}
,

"archive/779-interim-relief-and-urgent-public-law-protection-necessity-tests-for-ideal-governments-stays-preservation-orders-irreparable-harm-clocks-and-no-rights-by-fait-accompli.md": {
    "groups": [
        {"title": "Recommendation CM/Rec(2007)7 on good administration", "publisher": "Council of Europe", "url": "https://rm.coe.int/cmrec-2007-7-of-the-cm-to-ms-on-good-administration/16809f007c"},
        {"title": "The administration and you — a handbook", "publisher": "Council of Europe", "url": "https://rm.coe.int/eng-handbook-on-administration/1680a03ee2"},
        {"title": "Guide to good practice in respect of domestic remedies", "publisher": "ECHR / Council of Europe", "url": "https://www.echr.coe.int/documents/d/echr/pub_coe_domestics_remedies_eng"},
        {"title": "Interim measures", "publisher": "ECHR", "url": "https://www.echr.coe.int/documents/d/echr/fs_interim_measures_eng"},
        {"title": "Toolkit for Access to Justice and People-Centred Justice Systems", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/toolkit-for-access-to-justice-and-people-centred-justice-systems_aecf7f78-en.html"}
    ]
}
,

"archive/778-administrative-justice-timeliness-and-delay-remedies-necessity-tests-for-ideal-governments-priority-lanes-case-management-clock-publication-and-no-rights-by-queue-decay.md": {
    "groups": [
        {"title": "Toolkit for Access to Justice and People-Centred Justice Systems", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/toolkit-for-access-to-justice-and-people-centred-justice-systems_aecf7f78-en.html"},
        {"title": "Making Justice Systems More Effective and People Centred", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/making-justice-systems-more-effective-and-people-centred_e02fd90b-en.html"},
        {"title": "SATURN Guidelines for Judicial Time Management (4th revision)", "publisher": "CEPEJ / Council of Europe", "url": "https://rm.coe.int/cepej-2021-13-en-revised-saturn-guidelines-4th-revision/1680a4cf81"},
        {"title": "Time Management Checklist", "publisher": "CEPEJ / Council of Europe", "url": "https://rm.coe.int/cepej-2023-5-time-management-checklist-en/1680abaafa"},
        {"title": "Implementing the SATURN Time Management Tools in Courts", "publisher": "CEPEJ / Council of Europe", "url": "https://rm.coe.int/european-commission-for-the-efficiency-of-justice-cepej-guide-to-imple/16807476ab"},
        {"title": "The right to trial within reasonable time", "publisher": "Council of Europe", "url": "https://rm.coe.int/the-right-to-trial-within-reasonable-time-eng/16808e712c"}
    ]
}
,


"archive/777-execution-of-administrative-and-judicial-decisions-against-public-authorities-necessity-tests-for-ideal-governments-compliance-clocks-budget-home-escalation-and-no-judgment-by-non-execution.md": {
    "groups": [
        {"title": "Toolkit for Access to Justice and People-Centred Justice Systems", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/toolkit-for-access-to-justice-and-people-centred-justice-systems_aecf7f78-en.html"},
        {"title": "Recommendation Rec(2003)16 on the execution of administrative and judicial decisions in the field of administrative law", "publisher": "Council of Europe", "url": "https://search.coe.int/cm?i=09000016805df14f"},
        {"title": "Guidelines for a better implementation of the existing Council of Europe’s recommendation on enforcement", "publisher": "CEPEJ / Council of Europe", "url": "https://rm.coe.int/16807473cd"},
        {"title": "Good practice guide on enforcement of judicial decisions", "publisher": "CEPEJ / Council of Europe", "url": "https://rm.coe.int/european-commission-for-the-efficiency-of-justice-cepej-good-practice-/16807477bf"},
        {"title": "Guide on Article 46 of the Convention – Binding force and execution of judgments", "publisher": "ECHR Knowledge Sharing", "url": "https://ks.echr.coe.int/documents/d/echr-ks/guide_art_46_eng"}
    ]
}
,

"archive/776-court-fees-fee-waivers-cost-protection-and-public-interest-costs-necessity-tests-for-ideal-governments-affordability-merits-screening-security-for-costs-discipline-and-no-rights-by-priced-out-review.md": {
    "groups": [
        {"title": "Toolkit for Access to Justice and People-Centred Justice Systems", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/toolkit-for-access-to-justice-and-people-centred-justice-systems_aecf7f78-en.html"},
        {"title": "Guidelines on the efficiency and the effectiveness of legal aid schemes in the areas of civil and administrative law", "publisher": "Council of Europe / CDCJ", "url": "https://www.coe.int/en/web/cdcj/activities/free-legal-aid/-/asset_publisher/rKYnef9L78a2/content/legal-aid-in-civil-and-administrative-law-new-guidelines"},
        {"title": "Checklist for promoting access to justice", "publisher": "CEPEJ / Council of Europe", "url": "https://rm.coe.int/cepej-2025-16-access-to-justice-checklist-en-pour-publication/488029d233"},
        {"title": "Recommendation No. R (93) 1 on effective access to the law and to justice for the very poor", "publisher": "Council of Europe", "url": "https://search.coe.int/cm?i=09000016804df0ee"},
        {"title": "Access to Justice", "publisher": "UNECE / Aarhus Convention", "url": "https://unece.org/environment-policy/public-participation/access-to-justice"}
    ]
}
,

"archive/775-administrative-compensation-and-public-liability-necessity-tests-for-ideal-governments-claims-boards-prompt-payment-fault-vs-strict-zones-and-no-quash-only-rights.md": {
    "groups": [
        {"title": "Recommendation CM/Rec(2007)7 on good administration", "publisher": "Council of Europe", "url": "https://rm.coe.int/cmrec-2007-7-of-the-cm-to-ms-on-good-administration/16809f007c"},
        {"title": "Recommendation Rec(2003)16 on the execution of administrative and judicial decisions in the field of administrative law", "publisher": "Council of Europe", "url": "https://search.coe.int/cm/Pages/result_details.aspx?ObjectID=09000016805df14f"},
        {"title": "Recommendation No. R (84) 15 relating to public liability", "publisher": "Council of Europe", "url": "https://rm.coe.int/16804e3398"},
        {"title": "The administration and you — a handbook", "publisher": "Council of Europe", "url": "https://rm.coe.int/eng-handbook-on-administration/1680a03ee2"},
        {"title": "Recommendation of the Council on Access to Justice and People-Centred Justice Systems", "publisher": "OECD", "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0498"},
        {"title": "Recommendation of the Council on Human-Centred Public Administrative Services", "publisher": "OECD", "url": "https://legalinstruments.oecd.org/api/print?ids=729&lang=en"}
    ]
}
,

"archive/774-representative-actions-public-interest-standing-and-collective-redress-necessity-tests-for-ideal-governments-qualified-entities-funding-transparency-settlement-review-and-no-systemic-illegality-by-claimant-atomization.md": {
    "groups": [
        {"title": "Recommendation of the Council on Access to Justice and People-Centred Justice Systems", "publisher": "OECD", "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0498"},
        {"title": "Toolkit for Access to Justice and People-Centred Justice Systems", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/toolkit-for-access-to-justice-and-people-centred-justice-systems_aecf7f78-en.html"},
        {"title": "Consumer protection – Representative actions", "publisher": "EUR-Lex / European Union", "url": "https://eur-lex.europa.eu/EN/legal-content/summary/consumer-protection-representative-actions.html"},
        {"title": "Access to Justice", "publisher": "UNECE / Aarhus Convention", "url": "https://unece.org/environment-policy/public-participation/access-to-justice"},
        {"title": "Recommendation CM/Rec(2007)14 on the legal status of non-governmental organisations in Europe", "publisher": "Council of Europe", "url": "https://search.coe.int/cm?i=09000016805d534d"},
        {"title": "Recommendation CM/Rec(2024)2 on countering the use of strategic lawsuits against public participation (SLAPPs)", "publisher": "Council of Europe", "url": "https://rm.coe.int/0900001680af2805"}
    ]
}
,

"archive/773-administrative-appeal-and-tribunal-necessity-tests-for-ideal-governments-reasons-file-access-internal-review-suspensive-relief-merits-vs-legality-review-and-no-rights-by-one-shot-decision.md": {
    "groups": [
        {"title": "Recommendation CM/Rec(2007)7 on good administration", "publisher": "Council of Europe", "url": "https://rm.coe.int/cmrec-2007-7-of-the-cm-to-ms-on-good-administration/16809f007c"},
        {"title": "Guide to Good Administrative Practices for Public Authorities", "publisher": "Council of Europe", "url": "https://rm.coe.int/guide-good-administrative-practices-web/1680abd88b"},
        {"title": "Recommendation of the Council on Access to Justice and People-Centred Justice Systems", "publisher": "OECD", "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0491"},
        {"title": "Toolkit for Access to Justice and People-Centred Justice Systems", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/toolkit-for-access-to-justice-and-people-centred-justice-systems_aecf7f78-en.html"},
        {"title": "Making Justice Systems More Effective and People Centred", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/making-justice-systems-more-effective-and-people-centred_e02fd90b-en/full-report/administrative-justice-as-the-interface-between-people-and-institutions_88464c56.html"},
        {"title": "Implementation of laws on general administrative procedure in the Western Balkans", "publisher": "OECD / SIGMA", "url": "https://one.oecd.org/document/GOV/SIGMA(2021)2/en/pdf"}
    ]
}
,

"archive/772-ombuds-and-maladministration-redress-necessity-tests-for-ideal-governments-independent-complaint-entry-own-motion-investigation-recommendation-powers-systemic-reporting-and-no-rights-by-complaint-maze.md": {
    "groups": [
        {"title": "Principles on the Protection and Promotion of the Ombudsman Institution (the Venice Principles)", "publisher": "Venice Commission / Council of Europe", "url": "https://www.venice.coe.int/webforms/documents/default.aspx?lang=EN&pdf=CDL-AD(2019)005-e"},
        {"title": "The Role of Ombudsman Institutions in Open Government", "publisher": "OECD", "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2018/12/the-role-of-ombudsman-institutions-in-open-government_d2bf09ed/7353965f-en.pdf"},
        {"title": "Making Justice Systems More Effective and People Centred", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/making-justice-systems-more-effective-and-people-centred_e02fd90b-en/full-report/administrative-justice-as-the-interface-between-people-and-institutions_88464c56.html"},
        {"title": "Guide to Good Administrative Practices for Public Authorities", "publisher": "Council of Europe", "url": "https://rm.coe.int/guide-good-administrative-practices-web/1680abd88b"},
        {"title": "Ombudsman institutions in Europe – the need for a set of common standards", "publisher": "Parliamentary Assembly of the Council of Europe", "url": "https://assembly.coe.int/nw/xml/XRef/Xref-XML2HTML-EN.asp?fileid=28161"}
    ]
}
,

"archive/771-public-policy-evaluation-and-management-response-necessity-tests-for-ideal-governments-workplans-independence-publication-response-ledgers-reopen-triggers-and-no-learning-by-unanswered-recommendation.md": {
    "groups": [
        {"title": "Recommendation of the Council on Public Policy Evaluation", "publisher": "OECD", "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0478"},
        {"title": "Implementation Toolkit for the OECD Recommendation on Public Policy Evaluation", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/implementation-toolkit-for-the-oecd-recommendation-on-public-policy-evaluation_77faa4fe-en.html"},
        {"title": "Public policy evaluation: Government at a Glance 2025", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/government-at-a-glance-2025_0efd0bcd-en/full-report/public-policy-evaluation_e59d50bb.html"},
        {"title": "UNDP Evaluation Policy, 2025–2030", "publisher": "UNDP", "url": "https://www.undp.org/publications/undp-evaluation-policy-2025-2030"},
        {"title": "A World Bank Group Management Report on Implementation of IEG Recommendations (Management Action Record 2024) and IEG Validation", "publisher": "World Bank Group / IEG", "url": "https://documents1.worldbank.org/curated/en/099103124182541982/pdf/BOSIB-78edb945-c550-409b-ac47-0c1106fba191.pdf"},
        {"title": "Toolkit for the preparation, implementation, monitoring, reporting and evaluation of public administration reform and sector strategies", "publisher": "OECD / SIGMA", "url": "https://www.sigmaweb.org/publications/toolkit-for-the-preparation-implementation-monitoring-reporting-and-evaluation-of-public-administration-reform-and-sector-strategies.htm"}
    ]
}
,

"archive/770-internal-audit-inspection-and-inspector-general-necessity-tests-for-ideal-governments-risk-based-plans-direct-reporting-hotlines-case-routing-quality-review-and-no-self-inspection-by-line-command.md": {
    "groups": [
        {"title": "The Principles of Public Administration", "publisher": "OECD / SIGMA", "url": "https://www.sigmaweb.org/publications/principles-public-administration.htm"},
        {"title": "Internal control and audit in the public sector", "publisher": "OECD", "url": "https://www.oecd.org/en/topics/internal-control-and-audit-in-the-public-sector.html"},
        {"title": "Enhancing co-operation between internal and external auditors", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/enhancing-co-operation-between-internal-and-external-auditors_0d4976ed-en.html"},
        {"title": "Quality Standards for Inspection and Evaluation", "publisher": "CIGIE / IGnet", "url": "https://www.ignet.gov/sites/default/files/files/QualityStandardsforInspectionandEvaluation-2020.pdf"},
        {"title": "Frequently Asked Questions", "publisher": "CIGIE / IGnet", "url": "https://www.ignet.gov/content/frequently-asked-questions"},
        {"title": "Inspector General Act of 1978", "publisher": "United States Code", "url": "https://uscode.house.gov/view.xhtml?edition=prelim&path=%2Fprelim%40title5%2Fpart1%2Fchapter4"}
    ]
}
,

"archive/769-supreme-audit-and-public-accounts-follow-up-necessity-tests-for-ideal-governments-independence-open-reports-opposition-chaired-hearings-implementation-ledgers-and-no-accountability-by-unread-audit.md": {
    "groups": [
        {"title": "INTOSAI-P 1 – Declaration of Lima", "publisher": "INTOSAI", "url": "https://www.intosai.org/fileadmin/downloads/documents/open_access/INT_P_1_u_P_10/INTOSAI_P_1_en_2019.pdf"},
        {"title": "INTOSAI-P 10 – Mexico Declaration on SAI Independence", "publisher": "INTOSAI", "url": "https://www.intosai.org/fileadmin/downloads/documents/open_access/INT_P_1_u_P_10/INTOSAI_P_10_en_2019.pdf"},
        {"title": "INTOSAI-P 20 – Principles of Transparency and Accountability", "publisher": "INTOSAI", "url": "https://www.intosai.org/fileadmin/downloads/documents/open_access/INT_P_11_to_P_99/INTOSAI_P_20/INTOSAI_P_20_en_2019.pdf"},
        {"title": "Developing Effective Working Relationships Between Supreme Audit Institutions and Parliaments", "publisher": "OECD / SIGMA", "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2017/06/developing-effective-working-relationships-between-supreme-audit-institutions-and-parliaments_010545a8/d56ab899-en.pdf"},
        {"title": "Increasing the impact of supreme audit institutions through engagement with external stakeholders", "publisher": "OECD / SIGMA", "url": "https://one.oecd.org/document/GOV/SIGMA%282024%292/en/pdf"},
        {"title": "Effective budget oversight", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/quality-budget-institutions_8e811202-en/full-report/effective-budget-oversight_4d58ff32.html"}
    ]
}
,

"archive/768-whistleblower-protection-and-reporting-person-necessity-tests-for-ideal-governments-safe-channels-confidentiality-triage-anti-retaliation-remedy-and-no-integrity-by-punishing-disclosure.md": {
    "groups": [
        {"title": "OECD Public Integrity Handbook", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/oecd-public-integrity-handbook_ac8ed8e8-en.html"},
        {"title": "Committing to Effective Whistleblower Protection", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/committing-to-effective-whistleblower-protection_9789264252639-en.html"},
        {"title": "Directive (EU) 2019/1937 on the protection of persons who report breaches of Union law", "publisher": "European Union", "url": "https://eur-lex.europa.eu/eli/dir/2019/1937/oj/eng"},
        {"title": "Protection for whistleblowers", "publisher": "European Commission", "url": "https://commission.europa.eu/topics/human-rights/your-fundamental-rights-eu/protection-whistleblowers_en"},
        {"title": "Thematic Areas in Anti-Corruption: Whistle-blower protection", "publisher": "UNODC", "url": "https://www.unodc.org/corruption/en/learn/thematic-areas/whistle-blower-protection.html"},
        {"title": "Protecting Whistle-blowers: Practical Toolkit for Developing Whistle-blower Protection Frameworks", "publisher": "UNODC", "url": "https://track.unodc.org/track/uploads/res/track/resourcehub/2025/protecting_whistle-blowers_practical_toolkit_for_developing_whistle-blower_protection_frameworks_html/UNODC_2025_Protecting_Whistle-blowers_Toolkit.pdf"}
    ]
}
,

"archive/767-conflict-of-interest-and-asset-and-interest-disclosure-necessity-tests-for-ideal-governments-risk-tiering-recusal-divestment-verification-publication-and-no-office-with-a-private-shadow-ledger.md": {
    "groups": [
        {"title": "Conflict of interest", "publisher": "OECD", "url": "https://www.oecd.org/en/topics/conflict-of-interest.html"},
        {"title": "OECD Guidelines for Managing Conflict of Interest in the Public Service", "publisher": "OECD", "url": "https://legalinstruments.oecd.org/public/doc/130/130.en.pdf"},
        {"title": "Asset and Interest Disclosure: A Technical Guide", "publisher": "World Bank / StAR", "url": "https://openknowledge.worldbank.org/entities/publication/558c551a-0f3e-4366-87fb-f8eb5e42d5a3"},
        {"title": "Asset and Interest Disclosure", "publisher": "Open Government Partnership", "url": "https://www.opengovpartnership.org/open-gov-guide/anti-corruption-asset-and-interest-disclosure/"},
        {"title": "Stricter regulation needed to prevent corruption in top executive functions of central governments, says GRECO", "publisher": "Council of Europe / GRECO", "url": "https://www.coe.int/en/web/portal/-/stricter-regulation-needed-to-prevent-corruption-in-top-executive-functions-of-central-governments-says-greco"}
    ]
}
,

"archive/766-lobbying-transparency-and-revolving-door-necessity-tests-for-ideal-governments-registers-meeting-logs-gift-rules-cooling-off-advice-lanes-and-no-policy-by-invisible-influence.md": {
    "groups": [
        {"title": "Recommendation on Transparency and Integrity in Lobbying", "publisher": "OECD", "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0379"},
        {"title": "Lobbying in the 21st Century", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/lobbying-in-the-21st-century_c6d8eff8-en.html"},
        {"title": "Strengthening the Framework on Pre- and Post-Public Employment in Romania", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/strengthening-the-framework-on-pre-and-post-public-employment-in-romania_24381cc1-en.html"},
        {"title": "Conflict of interest", "publisher": "OECD", "url": "https://www.oecd.org/en/topics/conflict-of-interest.html"},
        {"title": "Stricter regulation needed to prevent corruption in top executive functions of central governments, says GRECO", "publisher": "Council of Europe / GRECO", "url": "https://www.coe.int/en/web/portal/-/stricter-regulation-needed-to-prevent-corruption-in-top-executive-functions-of-central-governments-says-greco"}
    ]
}
,

"archive/765-access-to-information-and-information-commissioner-necessity-tests-for-ideal-governments-requester-neutrality-narrow-exceptions-publication-schemes-appeal-powers-delay-discipline-and-no-right-to-know-without-an-enforcer.md": {
    "groups": [
        {"title": "Tromsø Convention / Convention on Access to Official Documents", "publisher": "Council of Europe", "url": "https://www.coe.int/en/web/access-to-official-documents"},
        {"title": "Institutions Guaranteeing Access to Information", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/institutions-guaranteeing-access-to-information_e6d58b52-en.html"},
        {"title": "Recommendation of the Council on Open Government", "publisher": "OECD", "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0438"},
        {"title": "Oversight institutions", "publisher": "UNESCO", "url": "https://www.unesco.org/en/right-access-information/oversight-bodies"},
        {"title": "2021 Report on Public Access to Information", "publisher": "UNESCO", "url": "https://www.unesco.org/reports/access-to-information/2021/en/executive-summary"}
    ]
}
,

"archive/764-political-finance-necessity-tests-for-ideal-governments-small-donor-pluralism-real-time-disclosure-spending-ceilings-audit-trails-digital-ad-archives-and-no-office-by-money-primary.md": {
    "groups": [
        {"title": "Funding of Political Parties and Election Campaigns: A Handbook on Political Finance", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/funding-political-parties-and-election-campaigns-handbook-political-finance"},
        {"title": "Political Finance Regulations around the World", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/political-finance-regulations-around-world-overview-international-idea"},
        {"title": "Political Finance in the Digital Age: Towards Evidence-Based Reforms", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/political-finance-digital-age-towards-evidence-based-reforms"},
        {"title": "Financing Democracy", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/financing-democracy_9789264249455-en.html"},
        {"title": "Guidelines on Political Party Regulation (Second Edition)", "publisher": "OSCE/ODIHR and Venice Commission", "url": "https://www.venice.coe.int/webforms/documents/default.aspx?pdffile=CDL-AD%282020%29032-e"}
    ]
}
,

"archive/763-caretaker-government-and-pre-election-restraint-necessity-tests-for-ideal-governments-routine-administration-incoming-government-consultation-major-appointments-freeze-emergency-carve-outs-and-no-mandate-stretch-between-verdict-and-handover.md": {
    "groups": [
        {"title": "Caretaker convention", "publisher": "New Zealand Cabinet Office", "url": "https://www.dpmc.govt.nz/our-business-units/cabinet-office/supporting-work-cabinet/cabinet-manual/6-elections-transitions-and-government-formation/caretaker-convention"},
        {"title": "Government Decision Making during the Period of Caretaker Government", "publisher": "New Zealand Cabinet Office", "url": "https://www.dpmc.govt.nz/publications/co-23-10-government-decision-making-during-period-caretaker-government"},
        {"title": "Election guidance for civil servants", "publisher": "GOV.UK / Cabinet Office", "url": "https://www.gov.uk/government/publications/election-guidance-for-civil-servants"},
        {"title": "Joint Guidelines for Preventing and Responding to the Misuse of Administrative Resources during Electoral Processes", "publisher": "OSCE/ODIHR and Venice Commission", "url": "https://www.osce.org/sites/default/files/f/documents/8/a/227506.pdf"}
    ]
}
,

"archive/762-official-opposition-and-legislative-minority-necessity-tests-for-ideal-governments-recognition-scrutiny-rights-agenda-oxygen-committee-chairs-evidence-capacity-and-no-government-by-majority-blackout.md": {
    "groups": [
        {"title": "Opposition and Legislative Minorities: Constitutional Roles, Rights and Recognition", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/opposition-and-legislative-minorities"},
        {"title": "The Role of the Legislative Opposition in Emergencies", "publisher": "International IDEA", "url": "https://www.idea.int/sites/default/files/publications/role-of-the-legislative-opposition-in-emergencies.pdf"},
        {"title": "Effective budget oversight", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/quality-budget-institutions_8e811202-en/full-report/effective-budget-oversight_4d58ff32.html"},
        {"title": "Joint Guidelines for Preventing and Responding to the Misuse of Administrative Resources during Electoral Processes", "publisher": "OSCE/ODIHR and Venice Commission", "url": "https://www.osce.org/sites/default/files/f/documents/8/a/227506.pdf"}
    ]
}
,


"archive/761-vacancy-and-acting-office-necessity-tests-for-ideal-governments-succession-order-time-limits-limited-powers-public-reporting-and-no-government-by-permanent-interim.md": {
    "groups": [
        {"title": "Public Administration in the Western Balkans 2024", "publisher": "OECD / SIGMA", "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2025/03/public-administration-in-the-western-balkans-2024_07555c85/1ec4c18f-en.pdf"},
        {"title": "Public Employment and Management 2021", "publisher": "OECD", "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2021/12/public-employment-and-management-2021_6a1fc237/938f0d65-en.pdf"},
        {"title": "Government Formation and Removal Mechanisms", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/government-formation-and-removal-mechanisms"},
        {"title": "Opinion on the Proposed Amendments to the Constitution of Finland", "publisher": "Venice Commission / Council of Europe", "url": "https://www.venice.coe.int/webforms/documents/default.aspx?pdffile=CDL-AD%282026%29003-e"},
        {"title": "Opinion on Certain Draft Amendments to the Law on the Constitutional Court of Bosnia and Herzegovina", "publisher": "Venice Commission / Council of Europe", "url": "https://www.venice.coe.int/webforms/documents/default.aspx?pdffile=CDL-AD%282024%29002-e"}
    ]
}
,

"archive/760-public-appointments-necessity-tests-for-ideal-governments-merit-vs-political-trust-open-competition-mixed-selection-confirmation-discipline-and-no-office-by-patronage-default.md": {
    "groups": [
        {"title": "Recommendation of the Council on Public Service Leadership and Capability", "publisher": "OECD", "url": "https://legalinstruments.oecd.org/public/doc/641/641.en.pdf"},
        {"title": "Study on the Political Involvement in Senior Staffing and on the Delineation of Responsibilities between Ministers and Senior Civil Servants", "publisher": "OECD / SIGMA", "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2007/07/study-on-the-political-involvement-in-senior-staffing-and-on-the-delineation-of-responsibilities-between-ministers-and-senior-civil-servants_g17a199d/136274825752.pdf"},
        {"title": "Governance Code on Public Appointments", "publisher": "GOV.UK / Commissioner for Public Appointments", "url": "https://www.gov.uk/government/publications/governance-code-for-public-appointments/governance-code-on-public-appointments-html"},
        {"title": "Judicial Appointments", "publisher": "International IDEA", "url": "https://www.idea.int/sites/default/files/publications/judicial-appointments-primer.pdf"},
        {"title": "Independent Regulatory and Oversight (Fourth-Branch) Institutions", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/independent-regulatory-and-oversight-fourth-branch-institutions"}
    ]
}
,


"archive/759-independent-institutions-necessity-tests-for-ideal-governments-referee-functions-bounded-mandates-appointment-discipline-budget-protection-review-lanes-and-no-fourth-branch-sprawl.md": {
    "groups": [
        {"title": "Independent Regulatory and Oversight (Fourth-Branch) Institutions", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/independent-regulatory-and-oversight-fourth-branch-institutions"},
        {"title": "Independent Institutions: Enhancing Democratic Integrity and Accountability through Constitutional Design", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/html/independent-institutions-enhancing-democratic-integrity-and"},
        {"title": "Recommendation of the Council on Regulatory Policy and Governance", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/recommendation-of-the-council-on-regulatory-policy-and-governance_9789264209022-en.html"},
        {"title": "The Governance of Regulators", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/oecd-best-practice-principles-for-regulatory-policy_23116013.html"},
        {"title": "Being an Independent Regulator", "publisher": "OECD", "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2016/07/being-an-independent-regulator_g1g66e65/9789264255401-en.pdf"}
    ]
}
,

"archive/758-delegated-legislation-and-executive-rulemaking-necessity-tests-for-ideal-governments-framework-statutes-purposes-scope-time-limits-scrutiny-publication-and-no-government-by-decree-laundering.md": {
    "groups": [
        {"title": "The Role of Parliament in Delegated Legislation: Principles for Safeguarding Legislative Transparency and Democratic Accountability", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/html/role-parliament-delegated-legislation-principles-safeguarding"},
        {"title": "Recommendation of the Council on Regulatory Policy and Governance", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/recommendation-of-the-council-on-regulatory-policy-and-governance_9789264209022-en.html"},
        {"title": "OECD Best Practice Principles for Regulatory Policy", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/oecd-best-practice-principles-for-regulatory-policy_23116013.html"},
        {"title": "The Updated Rule of Law Checklist", "publisher": "Venice Commission / Council of Europe", "url": "https://www.venice.coe.int/webforms/documents/default.aspx?pdffile=CDL-AD%282025%29002-e"},
        {"title": "Presidential Legislative Powers", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/presidential-legislative-powers"}
    ]
}
,

"archive/757-emergency-powers-necessity-tests-for-ideal-governments-ordinary-law-first-temporal-limits-legislative-renewal-judicial-review-and-no-shadow-constitution-by-crisis.md": {
    "groups": [
        {"title": "Emergency powers - what standards?", "publisher": "Council of Europe / Venice Commission", "url": "https://www.coe.int/en/web/human-rights-rule-of-law/venice-commission-covid19"},
        {"title": "Compilation of Venice Commission opinions, reports and studies on emergency situations", "publisher": "Venice Commission / Council of Europe", "url": "https://rm.coe.int/venice-commission-compilation-on-states-of-emergency-eng/16809e85b9"},
        {"title": "The Updated Rule of Law Checklist", "publisher": "Venice Commission / Council of Europe", "url": "https://www.venice.coe.int/webforms/documents/default.aspx?pdffile=CDL-AD%282025%29002-e"},
        {"title": "Emergency law responses to the Covid-19 pandemic", "publisher": "International IDEA", "url": "https://www.idea.int/gsod-2021/sites/default/files/2021-11/emergency-law-responses-covid19-pandemic-gsod2021.pdf"}
    ]
}
,

"archive/756-constitutional-review-necessity-tests-for-ideal-governments-integrated-apex-vs-specialized-court-ordinary-court-referral-abstract-review-remedial-bounds-and-no-guardian-without-docket-discipline.md": {
    "groups": [
        {"title": "The Fundamentals of Constitutional Courts", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/fundamentals-constitutional-courts"},
        {"title": "Judicial Appointments", "publisher": "International IDEA", "url": "https://www.idea.int/sites/default/files/publications/judicial-appointments-primer.pdf"},
        {"title": "Judicial Tenure, Removal, Immunity and Accountability", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/judicial-tenure-removal-immunity-and-accountability"},
        {"title": "Compilation of Venice Commission opinions, reports and studies on constitutional justice", "publisher": "Venice Commission / Council of Europe", "url": "https://www.venice.coe.int/webforms/documents/default.aspx?pdffile=CDL-PI%282022%29050-e"},
        {"title": "The Updated Rule of Law Checklist", "publisher": "Venice Commission / Council of Europe", "url": "https://www.venice.coe.int/webforms/documents/default.aspx?pdffile=CDL-AD%282025%29002-e"}
    ]
}
,

"archive/755-constitutional-referendum-necessity-tests-for-ideal-governments-amendment-classes-double-majorities-question-clarity-balanced-information-and-no-plebiscitary-shortcuts.md": {
    "groups": [
        {"title": "Direct Democracy", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/direct-democracy"},
        {"title": "Constitutional Amendment Procedures", "publisher": "International IDEA", "url": "https://www.idea.int/sites/default/files/publications/constitutional-amendment-procedures-primer.pdf"},
        {"title": "Revised Code of Good Practice on Referendums", "publisher": "Venice Commission / Council of Europe", "url": "https://www.venice.coe.int/webforms/documents/default.aspx?pdffile=CDL-AD%282022%29015-e"},
        {"title": "Report on Constitutional Amendment", "publisher": "Venice Commission / Council of Europe", "url": "https://www.venice.coe.int/webforms/documents/default.aspx?pdffile=CDL-AD%282010%29001-e"}
    ]
}
,

"archive/754-head-of-state-necessity-tests-for-ideal-governments-no-separate-crown-below-national-scale-ceremonial-arbiters-collective-headship-reserve-powers-on-rails-and-no-duplicate-democratic-apex.md": {
    "groups": [
        {"title": "Non-Executive Presidents in Parliamentary Democracies", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/non-executive-presidents-parliamentary-democracies"},
        {"title": "Constitutional Monarchs in Parliamentary Democracies", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/constitutional-monarchs-parliamentary-democracies"},
        {"title": "Electing Presidents in Presidential and Semi-Presidential Democracies", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/electing-presidents-presidential-and-semi-presidential-democracies"},
        {"title": "Government Formation and Removal Mechanisms", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/government-formation-and-removal-mechanisms"},
        {"title": "The Federal Council", "publisher": "Swiss Confederation / Presence Switzerland", "url": "https://www.aboutswitzerland.eda.admin.ch/en/the-federal-council"},
        {"title": "Federal Council", "publisher": "Swiss Confederation", "url": "https://www.admin.ch/gov/en/start/federal-council.html"}
    ]
}
,

"archive/753-upper-chamber-necessity-tests-for-ideal-governments-territorial-shared-rule-bounded-veto-domains-asymmetric-bargains-suspensive-delay-and-no-duplicate-bicameralism.md": {
    "groups": [
        {"title": "Bicameralism", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/bicameralism"},
        {"title": "Report on Bicameralism", "publisher": "Venice Commission / Council of Europe", "url": "https://www.venice.coe.int/webforms/documents/?pdf=CDL-AD(2024)007-e"},
        {"title": "Regional Governance in OECD Countries", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/regional-governance-in-oecd-countries_4d7c6483-en.html"},
        {"title": "European Charter of Local Self-Government", "publisher": "Council of Europe", "url": "https://www.coe.int/en/web/impact-convention-human-rights/european-charter-of-local-self-government"}
    ]
}
,

"archive/752-government-formation-and-removal-by-scope-micro-local-recall-municipal-manager-confidence-metro-investiture-parliamentary-default-constructive-no-confidence-fixed-terms-and-no-dual-democratic-command.md": {
    "groups": [
        {"title": "Government Formation and Removal Mechanisms", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/government-formation-and-removal-mechanisms"},
        {"title": "Electing Presidents in Presidential and Semi-Presidential Democracies", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/electing-presidents-presidential-and-semi-presidential-democracies"},
        {"title": "Presidential Legislative Powers", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/presidential-legislative-powers"},
        {"title": "Non-Executive Presidents in Parliamentary Democracies", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/non-executive-presidents-parliamentary-democracies"},
        {"title": "The OECD Metropolitan Governance Survey", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/the-oecd-metropolitan-governance-survey_5jz43zldh08p-en.html"},
        {"title": "Council-Manager Form of Government Resources", "publisher": "ICMA", "url": "https://icma.org/page/council-manager-form-government-resources"},
        {"title": "Cities 101 — Forms of Local Government", "publisher": "National League of Cities", "url": "https://www.nlc.org/resource/cities-101-forms-of-local-government/"},
        {"title": "European Charter of Local Self-Government", "publisher": "Council of Europe", "url": "https://www.coe.int/en/web/impact-convention-human-rights/european-charter-of-local-self-government"}
    ]
}
,
"archive/751-regional-tier-necessity-tests-territorial-platforms-shared-rule-asymmetry-collapse-and-no-map-inheritance-as-constitution.md": {
    "groups": [
        {"title": "Assigning responsibilities across levels of government", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html"},
        {"title": "Regional Governance in OECD Countries", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/regional-governance-in-oecd-countries_4d7c6483-en.html"},
        {"title": "The OECD Metropolitan Governance Survey", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/the-oecd-metropolitan-governance-survey_5jz43zldh08p-en.html"},
        {"title": "OECD Principles on Urban Policy", "publisher": "OECD", "url": "https://www.oecd.org/en/about/programmes/oecd-programme-on-national-urban-policy/oecd-principles-on-urban-policy.html"},
        {"title": "European Charter of Local Self-Government", "publisher": "Council of Europe", "url": "https://www.coe.int/en/web/impact-convention-human-rights/european-charter-of-local-self-government"},
        {"title": "Building More Resilient Cross-border Regions", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/building-more-resilient-cross-border-regions_d5fd3e59-en.html"},
        {"title": "Local Democracy", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/local-democracy"},
        {"title": "From Crisis to Resilience: World Bank Support to Small States", "publisher": "World Bank", "url": "https://www.worldbank.org/en/country/smallstates/brief/world-bank-support-to-small-states"}
    ]
}
,

"archive/750-polity-morphology-archetypes-for-ideal-government-stacks-dense-metro-polycentric-federal-sparse-archipelagic-and-cross-border-overlay-with-no-one-world-default.md": {
    "groups": [
        {"title": "Assigning responsibilities across levels of government", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html"},
        {"title": "Regional Governance in OECD Countries", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/regional-governance-in-oecd-countries_4d7c6483-en.html"},
        {"title": "The OECD Metropolitan Governance Survey", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/the-oecd-metropolitan-governance-survey_5jz43zldh08p-en.html"},
        {"title": "OECD Principles on Urban Policy", "publisher": "OECD", "url": "https://www.oecd.org/en/about/programmes/oecd-programme-on-national-urban-policy/oecd-principles-on-urban-policy.html"},
        {"title": "Building More Resilient Cross-border Regions", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/building-more-resilient-cross-border-regions_d5fd3e59-en.html"},
        {"title": "European Charter of Local Self-Government", "publisher": "Council of Europe", "url": "https://www.coe.int/en/web/impact-convention-human-rights/european-charter-of-local-self-government"},
        {"title": "Local Democracy", "publisher": "International IDEA", "url": "https://www.idea.int/publications/catalogue/local-democracy"},
        {"title": "From Crisis to Resilience: World Bank Support to Small States", "publisher": "World Bank", "url": "https://www.worldbank.org/en/country/smallstates/brief/world-bank-support-to-small-states"}
    ]
}
,

"archive/749-ideal-governments-by-scope-micro-local-voice-municipal-competence-county-rural-pooling-metropolitan-systems-regional-platforms-national-solidarity-continental-compacts-and-global-narrow-waists.md": {
    "groups": [
        {"title": "Assigning responsibilities across levels of government", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html"},
        {"title": "European Charter of Local Self-Government", "publisher": "Council of Europe", "url": "https://www.coe.int/en/web/impact-convention-human-rights/european-charter-of-local-self-government"},
        {"title": "International Guidelines on Decentralization and Access to Basic Services for All", "publisher": "UN-Habitat", "url": "https://unhabitat.org/international-guidelines-on-decentralization-and-access-to-basic-services-for-all"},
        {"title": "OECD Principles on Urban Policy", "publisher": "OECD", "url": "https://www.oecd.org/en/about/programmes/oecd-programme-on-national-urban-policy/oecd-principles-on-urban-policy.html"},
        {"title": "The OECD Metropolitan Governance Survey", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/the-oecd-metropolitan-governance-survey_5jz43zldh08p-en.html"},
        {"title": "Intergovernmental fiscal transfers and fiscal equalisation in a time of consolidation", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/intergovernmental-fiscal-transfers-and-fiscal-equalisation-in-a-time-of-consolidation_4853a4d0-en.html"},
        {"title": "UN Charter", "publisher": "United Nations", "url": "https://www.un.org/en/about-us/un-charter"},
        {"title": "International Cooperation and Global Public Goods", "publisher": "World Bank", "url": "https://www.worldbank.org/en/programs/knowledge-for-change/brief/Int-Coop-Global-Goods"}
    ]
}
,

"archive/748-historical-object-boundary-repair-packets-for-retired-government-bodies-scopes-and-shells-split-merge-creator-links-and-no-one-dead-authority-by-cataloguing-accident.md": {
    "groups": [
        {"title": "Assigning responsibilities across levels of government", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html"},
        {"title": "Guidance on Providing Information About Your Records", "publisher": "The National Archives", "url": "https://cdn.nationalarchives.gov.uk/documents/information-management/guidance-on-providing-information-about-your-records.pdf"},
        {"title": "Basic Web Archiving Guidance", "publisher": "The National Archives", "url": "https://cdn.nationalarchives.gov.uk/documents/information-management/web-archiving-guidance.pdf"},
        {"title": "Content design: planning, writing and managing content", "publisher": "UK Government", "url": "https://www.gov.uk/guidance/content-design/gov-uk-content-retention-and-withdrawal-archiving-policy"},
        {"title": "Unpublishing and withdrawing ('archiving')", "publisher": "UK Government", "url": "https://www.gov.uk/guidance/how-to-publish-on-gov-uk/unpublishing-and-archiving"},
        {"title": "NARA 1301, Lifecycle Data Standards and Lifecycle Authority Control", "publisher": "U.S. National Archives and Records Administration", "url": "https://www.archives.gov/files/about/policies/nara1301.docx.pdf%3F_ga%3D2.125791242.1442077890.1699914723-1396814520.1657300307"},
        {"title": "Archival Materials and Related Elements", "publisher": "U.S. National Archives and Records Administration", "url": "https://www.archives.gov/research/catalog/lcdrg/archival-materials"},
        {"title": "National Archives Catalog Search Tips", "publisher": "U.S. National Archives and Records Administration", "url": "https://www.archives.gov/research/catalog/help/search-tips"},
        {"title": "AC 34.2025", "publisher": "U.S. National Archives and Records Administration", "url": "https://www.archives.gov/records-mgmt/memos/ac-34-2025"}
    ]
}
,

"archive/747-register-deconsolidation-and-standalone-restoration-packets-for-absorbed-tombstones-reversible-grouping-object-specific-re-expansion-and-no-permanent-flattening-by-catalog-convenience.md": {
    "groups": [
        {"title": "Assigning responsibilities across levels of government", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html"},
        {"title": "Organising and grouping content on GOV.UK", "publisher": "UK Government", "url": "https://www.gov.uk/guidance/content-design/organising-and-grouping-content-on-gov-uk"},
        {"title": "Content design: planning, writing and managing content", "publisher": "UK Government", "url": "https://www.gov.uk/guidance/content-design/gov-uk-content-retention-and-withdrawal-archiving-policy"},
        {"title": "Unpublishing and withdrawing ('archiving')", "publisher": "UK Government", "url": "https://www.gov.uk/guidance/how-to-publish-on-gov-uk/unpublishing-and-archiving"},
        {"title": "Change slug and redirect a route", "publisher": "GOV.UK Developer Documentation", "url": "https://docs.publishing.service.gov.uk/manual/howto-change-slug-and-create-redirect.html"},
        {"title": "Configure transition mappings for a site", "publisher": "GOV.UK Developer Documentation", "url": "https://docs.publishing.service.gov.uk/manual/configure-transition-mappings.html"},
        {"title": "Transition a site to GOV.UK", "publisher": "GOV.UK Developer Documentation", "url": "https://docs.publishing.service.gov.uk/manual/transition-a-site.html"},
        {"title": "Basic Web Archiving Guidance", "publisher": "The National Archives", "url": "https://cdn.nationalarchives.gov.uk/documents/information-management/web-archiving-guidance.pdf"},
        {"title": "Guide to Federal Records", "publisher": "U.S. National Archives and Records Administration", "url": "https://www.archives.gov/research/guide-fed-records"},
        {"title": "About the Guide to Federal Records", "publisher": "U.S. National Archives and Records Administration", "url": "https://www.archives.gov/research/guide-fed-records/about.html"},
        {"title": "AC 34.2025", "publisher": "U.S. National Archives and Records Administration", "url": "https://www.archives.gov/records-mgmt/memos/ac-34-2025"}
    ]
}
,

"archive/746-historical-register-rehousing-and-cross-catalog-migration-packets-for-absorbed-tombstones-register-home-change-stable-entry-identifiers-alias-continuity-and-no-disappearance-by-replatforming.md": {
    "groups": [
        {"title": "Assigning responsibilities across levels of government", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html"},
        {"title": "Content design: planning, writing and managing content", "publisher": "UK Government", "url": "https://www.gov.uk/guidance/content-design/gov-uk-content-retention-and-withdrawal-archiving-policy"},
        {"title": "Unpublishing and withdrawing ('archiving')", "publisher": "UK Government", "url": "https://www.gov.uk/guidance/how-to-publish-on-gov-uk/unpublishing-and-archiving"},
        {"title": "Change slug and redirect a route", "publisher": "GOV.UK Developer Documentation", "url": "https://docs.publishing.service.gov.uk/manual/howto-change-slug-and-create-redirect.html"},
        {"title": "Transition a site to GOV.UK", "publisher": "GOV.UK Developer Documentation", "url": "https://docs.publishing.service.gov.uk/manual/transition-a-site.html"},
        {"title": "Configure transition mappings for a site", "publisher": "GOV.UK Developer Documentation", "url": "https://docs.publishing.service.gov.uk/manual/configure-transition-mappings.html"},
        {"title": "Basic Web Archiving Guidance", "publisher": "The National Archives", "url": "https://cdn.nationalarchives.gov.uk/documents/information-management/web-archiving-guidance.pdf"},
        {"title": "Using the National Archives Catalog", "publisher": "U.S. National Archives and Records Administration", "url": "https://www.archives.gov/research/catalog/help/using"},
        {"title": "AC 34.2025", "publisher": "U.S. National Archives and Records Administration", "url": "https://www.archives.gov/records-mgmt/memos/ac-34-2025"}
    ]
}
,

"archive/745-tombstone-consolidation-and-register-absorption-packets-for-retired-government-bodies-scopes-and-shells-directory-merge-alias-preservation-correction-chain-retention-and-no-disappearance-by-tidying.md": {
    "groups": [
        {"title": "Assigning responsibilities across levels of government", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html"},
        {"title": "Content design: planning, writing and managing content", "publisher": "UK Government", "url": "https://www.gov.uk/guidance/content-design/gov-uk-content-retention-and-withdrawal-archiving-policy"},
        {"title": "Organising and grouping content on GOV.UK", "publisher": "UK Government", "url": "https://www.gov.uk/guidance/content-design/organising-and-grouping-content-on-gov-uk"},
        {"title": "Unpublishing and withdrawing ('archiving')", "publisher": "UK Government", "url": "https://www.gov.uk/guidance/how-to-publish-on-gov-uk/unpublishing-and-archiving"},
        {"title": "Redirect an HTML attachment's URL in Whitehall", "publisher": "GOV.UK Developer Documentation", "url": "https://docs.publishing.service.gov.uk/manual/howto-redirect-html-attachment-urls-from-whitehall.html"},
        {"title": "Basic Web Archiving Guidance", "publisher": "The National Archives", "url": "https://cdn.nationalarchives.gov.uk/documents/information-management/web-archiving-guidance.pdf"},
        {"title": "About the Guide to Federal Records", "publisher": "U.S. National Archives and Records Administration", "url": "https://www.archives.gov/research/guide-fed-records/about.html"},
        {"title": "Using the National Archives Catalog", "publisher": "U.S. National Archives and Records Administration", "url": "https://www.archives.gov/research/catalog/help/using"},
        {"title": "AC 34.2025", "publisher": "U.S. National Archives and Records Administration", "url": "https://www.archives.gov/records-mgmt/memos/ac-34-2025"}
    ]
}
,

"archive/744-tombstone-stewardship-and-health-check-packets-for-retired-government-bodies-scopes-and-shells-named-maintainer-link-probes-stewardship-transfer-and-no-orphaned-memory-surfaces.md": {
    "groups": [
        {"title": "Assigning responsibilities across levels of government", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html"},
        {"title": "Unpublishing and withdrawing ('archiving')", "publisher": "UK Government", "url": "https://www.gov.uk/guidance/how-to-publish-on-gov-uk/unpublishing-and-archiving"},
        {"title": "Content design: planning, writing and managing content", "publisher": "UK Government", "url": "https://www.gov.uk/guidance/content-design/gov-uk-content-retention-and-withdrawal-archiving-policy"},
        {"title": "Redirect an HTML attachment's URL in Whitehall", "publisher": "UK Government / GOV.UK Developer Documentation", "url": "https://docs.publishing.service.gov.uk/manual/howto-redirect-html-attachment-urls-from-whitehall.html"},
        {"title": "Basic Web Archiving Guidance", "publisher": "The National Archives", "url": "https://cdn.nationalarchives.gov.uk/documents/information-management/web-archiving-guidance.pdf"},
        {"title": "NARA Guidance on Managing Web Records Background", "publisher": "U.S. National Archives and Records Administration", "url": "https://www.archives.gov/records-mgmt/policy/managing-web-records-background.html"},
        {"title": "AC 34.2025", "publisher": "U.S. National Archives and Records Administration", "url": "https://www.archives.gov/records-mgmt/memos/ac-34-2025"}
    ]
}
,

"archive/743-tombstone-challenge-and-correction-packets-for-retired-government-bodies-scopes-and-shells-standing-material-error-evidence-chain-and-no-historical-repair-by-helpdesk-fiat.md": {
    "groups": [
        {"title": "Assigning responsibilities across levels of government", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html"},
        {"title": "What to do with your records if your public body is undergoing a status change", "publisher": "The National Archives", "url": "https://cdn.nationalarchives.gov.uk/documents/information-management/dissolution-of-public-bodies.pdf"},
        {"title": "Basic Web Archiving Guidance", "publisher": "The National Archives", "url": "https://cdn.nationalarchives.gov.uk/documents/information-management/web-archiving-guidance.pdf"},
        {"title": "Unpublishing and withdrawing ('archiving')", "publisher": "UK Government", "url": "https://www.gov.uk/guidance/how-to-publish-on-gov-uk/unpublishing-and-archiving"},
        {"title": "Content design: planning, writing and managing content", "publisher": "UK Government", "url": "https://www.gov.uk/guidance/content-design/gov-uk-content-retention-and-withdrawal-archiving-policy"},
        {"title": "AC 34.2025", "publisher": "U.S. National Archives and Records Administration", "url": "https://www.archives.gov/records-mgmt/memos/ac-34-2025"},
        {"title": "NARA Guidance on Managing Web Records", "publisher": "U.S. National Archives and Records Administration", "url": "https://www.archives.gov/records-mgmt/policy/managing-web-records.html"}
    ]
}
,

"archive/742-tombstone-rerouting-packets-for-retired-government-bodies-scopes-and-shells-successor-drift-lookup-updates-correction-chains-and-no-historical-rewrite-by-fresh-redirect.md": {
    "groups": [
        {"title": "Assigning responsibilities across levels of government", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html"},
        {"title": "What to do with your records if your public body is undergoing a status change", "publisher": "The National Archives", "url": "https://cdn.nationalarchives.gov.uk/documents/information-management/dissolution-of-public-bodies.pdf"},
        {"title": "Basic Web Archiving Guidance", "publisher": "The National Archives", "url": "https://cdn.nationalarchives.gov.uk/documents/information-management/web-archiving-guidance.pdf"},
        {"title": "AC 34.2025", "publisher": "U.S. National Archives and Records Administration", "url": "https://www.archives.gov/records-mgmt/memos/ac-34-2025"},
        {"title": "Web Records", "publisher": "U.S. National Archives and Records Administration", "url": "https://www.archives.gov/records-mgmt/policy/web-records"},
        {"title": "Unpublishing and withdrawing ('archiving')", "publisher": "UK Government", "url": "https://www.gov.uk/guidance/how-to-publish-on-gov-uk/unpublishing-and-archiving"}
    ]
}
,

"archive/741-historical-lookup-and-tombstone-packets-for-retired-government-bodies-scopes-and-shells-successor-crosswalks-archive-homes-one-question-lane-and-no-live-authority-by-memorial-page.md": {
    "groups": [
        {"title": "Assigning responsibilities across levels of government", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html"},
        {"title": "What to do with your records if your public body is undergoing a status change", "publisher": "The National Archives", "url": "https://cdn.nationalarchives.gov.uk/documents/information-management/dissolution-of-public-bodies.pdf"},
        {"title": "Basic Web Archiving Guidance", "publisher": "The National Archives", "url": "https://cdn.nationalarchives.gov.uk/documents/information-management/web-archiving-guidance.pdf"},
        {"title": "redirection technical guidance for government departments", "publisher": "The National Archives", "url": "https://cdn.nationalarchives.gov.uk/documents/information-management/redirection-technical-guidance-for-departments-v4.2-web-version.pdf"},
        {"title": "AC 34.2025", "publisher": "U.S. National Archives and Records Administration", "url": "https://www.archives.gov/records-mgmt/memos/ac-34-2025"},
        {"title": "Web Records", "publisher": "U.S. National Archives and Records Administration", "url": "https://www.archives.gov/records-mgmt/policy/web-records"},
        {"title": "Unpublishing and withdrawing ('archiving')", "publisher": "UK Government", "url": "https://www.gov.uk/guidance/how-to-publish-on-gov-uk/unpublishing-and-archiving"}
    ]
}
,

"archive/740-residual-estate-termination-certificates-for-post-custody-government-closeout-shells-zero-residue-proof-final-routing-and-no-ghost-state-by-never-ending-tail.md": {
    "groups": [
        {"title": "Assigning responsibilities across levels of government", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html"},
        {"title": "Public Bodies: A Guide for Departments - Chapter 10", "publisher": "UK Government / Cabinet Office", "url": "https://assets.publishing.service.gov.uk/media/633443a6e90e0772dde3636a/Public_Bodies_-_a_guide_for_departments_-_chapter_10.pdf"},
        {"title": "Public Bodies Reforms - Checklist for Departments", "publisher": "UK Government / The National Archives", "url": "https://cdn.nationalarchives.gov.uk/documents/guidance-docs/public-bodies-reforms-checklist-for-departments.pdf"},
        {"title": "What to do with your records if your public body is undergoing a status change", "publisher": "The National Archives", "url": "https://cdn.nationalarchives.gov.uk/documents/information-management/dissolution-of-public-bodies.pdf"},
        {"title": "AC 34.2025", "publisher": "U.S. National Archives and Records Administration", "url": "https://www.archives.gov/records-mgmt/memos/ac-34-2025"},
        {"title": "Group accounting manual 2024 to 2025", "publisher": "UK Government / Department of Health and Social Care", "url": "https://assets.publishing.service.gov.uk/media/6854255216eefd7361e989ed/dhsc-group-accounting-manual-2024-to-2025-june-2025.pdf"},
        {"title": "Preparing for PFI contract expiry", "publisher": "UK Government / Infrastructure and Projects Authority", "url": "https://assets.publishing.service.gov.uk/media/621c877de90e0710bdc09a96/IPA_Guidance_-_Preparing_for_PFI_Contract_Expiry.pdf"}
    ]
}
,

"archive/739-residual-estate-packets-for-post-custody-government-closeout-shells-claims-record-access-financial-tail-review-clocks-and-no-ghost-state-by-leftover-residue.md": {
    "groups": [
        {"title": "Assigning responsibilities across levels of government", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html"},
        {"title": "Public Bodies Reforms - Checklist for Departments", "publisher": "UK Government / The National Archives", "url": "https://cdn.nationalarchives.gov.uk/documents/guidance-docs/public-bodies-reforms-checklist-for-departments.pdf"},
        {"title": "Public Bodies: A Guide for Departments - Chapter 10", "publisher": "UK Government / Cabinet Office", "url": "https://assets.publishing.service.gov.uk/media/633443a6e90e0772dde3636a/Public_Bodies_-_a_guide_for_departments_-_chapter_10.pdf"},
        {"title": "Dissolution and Privatisation of Public Bodies", "publisher": "The National Archives", "url": "https://cdn.nationalarchives.gov.uk/documents/dissolution-and-privatisation-guidance-v1.pdf"},
        {"title": "Moving? Consolidating? Reorganizing?", "publisher": "U.S. National Archives and Records Administration", "url": "https://www.archives.gov/records-mgmt/publications/moving-consolidating-reorganizing.html"},
        {"title": "Preparing for PFI contract expiry", "publisher": "UK Government / Infrastructure and Projects Authority", "url": "https://assets.publishing.service.gov.uk/media/621c877de90e0710bdc09a96/IPA_Guidance_-_Preparing_for_PFI_Contract_Expiry.pdf"},
        {"title": "Information Commissioner's Office - Management agreement 2018-2021", "publisher": "UK Government / Department for Culture, Media and Sport", "url": "https://www.gov.uk/government/publications/information-commissioners-office-management-agreement-2018-2021/information-commissioners-office-management-agreement-2018-2021"},
        {"title": "Bulb SAR: post transfer facility", "publisher": "UK Government / HM Treasury", "url": "https://www.gov.uk/government/publications/bulb-special-administration-regime-sar-post-transfer-facility/bulb-sar-post-transfer-facility"}
    ]
}
,

"archive/738-custodian-discharge-packets-for-ideal-government-neutral-custody-final-account-residual-liabilities-record-seal-and-no-shadow-government-by-finished-interim.md": {
    "groups": [
        {"title": "Assigning responsibilities across levels of government", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html"},
        {"title": "The Mid-Tier Contract - Schedule 30 (Exit Management)", "publisher": "UK Government / Cabinet Office", "url": "https://www.gov.uk/government/publications/the-mid-tier-contract-schedule-30-exit-management"},
        {"title": "Chapter 36. Transition into use", "publisher": "UK Government / Infrastructure and Projects Authority", "url": "https://projectdelivery.gov.uk/teal-book/home/part-f-solution-delivery/chapter-36-transition-into-use/"},
        {"title": "Public Bodies Reforms - Checklist for Departments", "publisher": "UK Government / The National Archives", "url": "https://cdn.nationalarchives.gov.uk/documents/guidance-docs/public-bodies-reforms-checklist-for-departments.pdf"},
        {"title": "Dissolution and Privatisation of Public Bodies", "publisher": "The National Archives", "url": "https://cdn.nationalarchives.gov.uk/documents/dissolution-and-privatisation-guidance-v1.pdf"},
        {"title": "Records Management Resources for Agencies Undergoing Reorganizations or Other Major Changes", "publisher": "U.S. National Archives and Records Administration", "url": "https://www.archives.gov/records-mgmt/drawdown"},
        {"title": "Checklist to Support Agencies Undergoing Reorganizations or Other Major Changes", "publisher": "U.S. National Archives and Records Administration", "url": "https://www.archives.gov/files/records-mgmt/memos/draw-down-checklist.pdf"},
        {"title": "Bulb SAR: post transfer facility", "publisher": "UK Government / HM Treasury", "url": "https://www.gov.uk/government/publications/bulb-special-administration-regime-sar-post-transfer-facility/bulb-sar-post-transfer-facility"},
        {"title": "Put your company into administration", "publisher": "UK Government", "url": "https://www.gov.uk/put-your-company-into-administration"}
    ]
}
,

"archive/737-release-packets-for-ideal-government-neutral-custody-full-partial-and-phased-release-receiver-readiness-residual-safeguards-and-no-custody-exit-by-impatience.md": {
    "groups": [
        {"title": "Assigning responsibilities across levels of government", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html"},
        {"title": "Model Services Contract - Guidance for Authorities", "publisher": "UK Government / Cabinet Office", "url": "https://assets.publishing.service.gov.uk/media/68af2474960e2d135b4c8eb2/Buyer_Guidance_-_MSC_v2.2A_2025.pdf"},
        {"title": "The Mid-Tier Contract - Schedule 30 (Exit Management)", "publisher": "UK Government / Cabinet Office", "url": "https://www.gov.uk/government/publications/the-mid-tier-contract-schedule-30-exit-management"},
        {"title": "Public Bodies Reforms - Checklist for Departments", "publisher": "UK Government / The National Archives", "url": "https://cdn.nationalarchives.gov.uk/documents/guidance-docs/public-bodies-reforms-checklist-for-departments.pdf"},
        {"title": "Dissolution and Privatisation of Public Bodies", "publisher": "The National Archives", "url": "https://cdn.nationalarchives.gov.uk/documents/dissolution-and-privatisation-guidance-v1.pdf"},
        {"title": "AC 34.2025", "publisher": "U.S. National Archives and Records Administration", "url": "https://www.archives.gov/records-mgmt/memos/ac-34-2025"},
        {"title": "Moving? Consolidating? Reorganizing?", "publisher": "U.S. National Archives and Records Administration", "url": "https://www.archives.gov/records-mgmt/publications/moving-consolidating-reorganizing.html"},
        {"title": "Rules on ensuring the effective functioning of a financial market infrastructure special administration regime", "publisher": "HM Treasury", "url": "https://www.gov.uk/government/consultations/rules-on-ensuring-the-effective-functioning-of-a-financial-market-infrastructure-special-administration-regime/rules-on-ensuring-the-effective-functioning-of-a-financial-market-infrastructure-special-administration-regime"}
    ]
}
,

"archive/736-temporary-neutral-custody-packets-for-ideal-government-scope-shifts-contested-handoffs-rights-bearing-queues-record-spines-credential-escrow-and-no-settlement-by-possession.md": {
    "groups": [
        {"title": "Assigning responsibilities across levels of government", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html"},
        {"title": "Records collection policy", "publisher": "The National Archives", "url": "https://cdn.nationalarchives.gov.uk/documents/information-management/records-collection-policy.pdf"},
        {"title": "Records Management Resources for Agencies Undergoing Reorganizations or Other Major Changes", "publisher": "U.S. National Archives and Records Administration", "url": "https://www.archives.gov/records-mgmt/drawdown"},
        {"title": "Assessing and monitoring the Economic and Financial Standing of Suppliers guidance note", "publisher": "UK Government", "url": "https://www.gov.uk/government/publications/the-sourcing-and-consultancy-playbooks/assessing-and-monitoring-the-economic-and-financial-standing-of-suppliers-guidance-note-html--2"},
        {"title": "Model Services Contract - Guidance for Authorities", "publisher": "UK Government", "url": "https://assets.publishing.service.gov.uk/media/68af2474960e2d135b4c8eb2/Buyer_Guidance_-_MSC_v2.2A_2025.pdf"},
        {"title": "Special administration regime for payment and settlement systems", "publisher": "HM Treasury", "url": "https://assets.publishing.service.gov.uk/media/5a7a4a0be5274a319e779350/consult_special_administration_regime_for_payment_and_settlement_systems.pdf"}
    ]
}
,

"archive/735-rollback-packets-for-ideal-government-scope-shifts-failed-stabilization-return-authority-pending-matters-record-lineage-and-no-reversal-by-headline-alone.md": {
    "groups": [
        {"title": "Assigning responsibilities across levels of government", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html"},
        {"title": "Machinery of government change: Checklist for the transferring organisation", "publisher": "The National Archives", "url": "https://cdn.nationalarchives.gov.uk/documents/information-management/checklist-for-transferring-organisation.pdf"},
        {"title": "Machinery of government change: Checklist for the receiving organisation", "publisher": "The National Archives", "url": "https://cdn.nationalarchives.gov.uk/documents/information-management/checklist-for-receiving-organisation.pdf"},
        {"title": "Public Bodies Reforms: Checklist for departments", "publisher": "UK Government / The National Archives", "url": "https://cdn.nationalarchives.gov.uk/documents/guidance-docs/public-bodies-reforms-checklist-for-departments.pdf"},
        {"title": "Records Management Resources for Agencies Undergoing Reorganizations or Other Major Changes", "publisher": "U.S. National Archives and Records Administration", "url": "https://www.archives.gov/records-mgmt/drawdown"},
        {"title": "Checklist to Support Agencies Undergoing Reorganizations or Other Major Changes", "publisher": "U.S. National Archives and Records Administration", "url": "https://www.archives.gov/files/records-mgmt/memos/draw-down-checklist.pdf"},
        {"title": "Service management good practice", "publisher": "UK Government", "url": "https://www.gov.uk/government/publications/public-services-network-psn-service-management-good-practice/service-management-good-practice"},
        {"title": "Deploying software regularly", "publisher": "UK Government Service Manual", "url": "https://www.gov.uk/service-manual/technology/deploying-software-regularly"},
        {"title": "Service transition manager", "publisher": "UK Government Digital and Data Profession", "url": "https://ddat-capability-framework.service.gov.uk/role/service-transition-manager"}
    ]
}
,

"archive/734-post-closure-stabilization-packets-for-ideal-government-scope-shifts-independent-live-window-rebound-triggers-review-metrics-and-no-independence-by-one-quiet-week.md": {
    "groups": [
        {"title": "Assigning responsibilities across levels of government", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html"},
        {"title": "How the live phase works", "publisher": "UK Government Service Manual", "url": "https://www.gov.uk/service-manual/agile-delivery/how-the-live-phase-works"},
        {"title": "How to set performance metrics for your service", "publisher": "UK Government Service Manual", "url": "https://www.gov.uk/service-manual/measuring-success/how-to-set-performance-metrics-for-your-service"},
        {"title": "Producing post-implementation reviews: principles of best practice", "publisher": "UK Government", "url": "https://www.gov.uk/government/publications/business-regulation-producing-post-implementation-reviews/producing-post-implementation-reviews-principles-of-best-practice"},
        {"title": "Machinery of government change: Checklist for the receiving organisation", "publisher": "The National Archives", "url": "https://cdn.nationalarchives.gov.uk/documents/information-management/checklist-for-receiving-organisation.pdf"},
        {"title": "Migrating information between records management systems", "publisher": "The National Archives", "url": "https://cdn.nationalarchives.gov.uk/documents/information-management/edrms.pdf"},
        {"title": "Public Bodies Reforms: Checklist for departments", "publisher": "UK Government / The National Archives", "url": "https://cdn.nationalarchives.gov.uk/documents/guidance-docs/public-bodies-reforms-checklist-for-departments.pdf"},
        {"title": "Service transition manager", "publisher": "UK Government Digital and Data Profession", "url": "https://ddat-capability-framework.service.gov.uk/role/service-transition-manager"}
    ]
}
,


"archive/733-bridge-closure-packets-for-ideal-government-scope-shifts-host-release-channel-retirement-records-signoff-and-no-temporary-forever.md": {
    "groups": [
        {"title": "Assigning responsibilities across levels of government", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html"},
        {"title": "The Sourcing Playbook (HTML)", "publisher": "UK Government", "url": "https://www.gov.uk/government/publications/the-sourcing-and-consultancy-playbooks/the-sourcing-playbook-html"},
        {"title": "Closing the contract", "publisher": "UK Government / Procurement Pathway", "url": "https://www.procurementpathway.civilservice.gov.uk/lifecycle/manage/closing-the-contract/"},
        {"title": "Machinery of government change: Checklist for the receiving organisation", "publisher": "The National Archives", "url": "https://cdn.nationalarchives.gov.uk/documents/information-management/checklist-for-receiving-organisation.pdf"},
        {"title": "Machinery of government change: Checklist for the transferring organisation", "publisher": "The National Archives", "url": "https://cdn.nationalarchives.gov.uk/documents/information-management/checklist-for-transferring-organisation.pdf"},
        {"title": "Records Management Resources for Agencies Undergoing Reorganizations or Other Major Changes", "publisher": "U.S. National Archives and Records Administration", "url": "https://www.archives.gov/records-mgmt/drawdown"},
        {"title": "Updating Schedules", "publisher": "U.S. National Archives and Records Administration", "url": "https://www.archives.gov/records-mgmt/scheduling/updates"}
    ]
}
,



"archive/732-transitional-hosting-packets-for-ideal-government-scope-shifts-host-of-record-command-boundaries-forwarding-duties-expiry-clocks-and-no-sovereignty-by-borrowed-runtime.md": {
    "groups": [
        {"title": "Assigning responsibilities across levels of government", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html"},
        {"title": "Machinery of Government Guidance", "publisher": "UK Government", "url": "https://assets.publishing.service.gov.uk/media/5a81a03aed915d74e6233465/2016_07_29_machinery_of_government_guidance.pdf"},
        {"title": "Public Bodies Reforms: Checklist for departments", "publisher": "UK Government / The National Archives", "url": "https://cdn.nationalarchives.gov.uk/documents/guidance-docs/public-bodies-reforms-checklist-for-departments.pdf"},
        {"title": "Machinery of government change: Checklist for the transferring organisation", "publisher": "The National Archives", "url": "https://cdn.nationalarchives.gov.uk/documents/information-management/checklist-for-transferring-organisation.pdf"},
        {"title": "Scheduling Records", "publisher": "U.S. National Archives and Records Administration", "url": "https://www.archives.gov/records-mgmt/scheduling/sch-records"}
    ]
}
,

"archive/731-cutover-witness-packets-for-ideal-government-scope-shifts-effective-state-old-holder-new-holder-exception-ledger-and-no-transfer-by-folklore.md": {
    "groups": [
        {"title": "Assigning responsibilities across levels of government", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html"},
        {"title": "Machinery of Government Guidance", "publisher": "UK Government", "url": "https://assets.publishing.service.gov.uk/media/5a81a03aed915d74e6233465/2016_07_29_machinery_of_government_guidance.pdf"},
        {"title": "Public Bodies Reforms: Checklist for departments", "publisher": "UK Government / The National Archives", "url": "https://cdn.nationalarchives.gov.uk/documents/guidance-docs/public-bodies-reforms-checklist-for-departments.pdf"},
        {"title": "Administrative Arrangements Order - 13 May 2025", "publisher": "Australian Government / Department of the Prime Minister and Cabinet", "url": "https://www.pmc.gov.au/resources/aao-13-may-2025"},
        {"title": "The Transfer of Functions (Secretary of State for Foreign, Commonwealth and Development Affairs) Order 2020", "publisher": "UK Government / legislation.gov.uk", "url": "https://www.legislation.gov.uk/uksi/2020/942/pdfs/uksiem_20200942_en.pdf"},
        {"title": "Machinery of Government and organisational change", "publisher": "The National Archives", "url": "https://www.nationalarchives.gov.uk/information-management/manage-information/planning/machinery-of-government-and-organisational-change/"}
    ]
}
,
"archive/730-continuity-packets-for-ideal-government-scope-shifts-staff-budget-records-cases-contracts-assets-cutover-and-no-ratification-by-theory-alone.md": {
    "groups": [
        {"title": "Assigning responsibilities across levels of government", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html"},
        {"title": "Making Decentralisation Work", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/making-decentralisation-work_g2g9faa7-en.html"},
        {"title": "Effective Public Investment Toolkit", "publisher": "OECD", "url": "https://www.oecd.org/en/about/projects/effective-public-investment-toolkit.html"},
        {"title": "European Charter of Local Self-Government", "publisher": "Council of Europe", "url": "https://edoc.coe.int/en/local-democracy/6856-charte-europenne-de-l-autonomie-locale.html"},
        {"title": "Machinery of Government Guidance", "publisher": "UK Government", "url": "https://assets.publishing.service.gov.uk/media/5a81a03aed915d74e6233465/2016_07_29_machinery_of_government_guidance.pdf"},
        {"title": "Public Bodies Reforms: Checklist for departments", "publisher": "UK Government / The National Archives", "url": "https://cdn.nationalarchives.gov.uk/documents/guidance-docs/public-bodies-reforms-checklist-for-departments.pdf"},
        {"title": "Staff transfers in the public sector", "publisher": "UK Government", "url": "https://assets.publishing.service.gov.uk/media/5a79b86540f0b642860da3ad/staff_transfers_145.pdf"},
        {"title": "Moving? Consolidating? Reorganizing?", "publisher": "U.S. National Archives and Records Administration", "url": "https://www.archives.gov/records-mgmt/publications/moving-consolidating-reorganizing.html"}
    ]
}
,
"archive/728-sideways-authority-packets-for-ideal-governments-bounded-remit-footprint-logic-board-fiscal-lane-review-clocks-and-no-functional-wrapper-without-constitutional-kit.md": {
    "groups": [
        {"title": "Beyond Markets and States: Polycentric Governance of Complex Economic Systems", "publisher": "Nobel Prize Outreach", "url": "https://www.nobelprize.org/prizes/economic-sciences/2009/ostrom/lecture/"},
        {"title": "Assigning responsibilities across levels of government", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html"},
        {"title": "Governing the City", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/governing-the-city_9789264226500-en.html"},
        {"title": "Regional Governance in OECD Countries", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/regional-governance-in-oecd-countries_4d7c6483-en.html"},
        {"title": "Directive 2000/60/EC establishing a framework for Community action in the field of water policy", "publisher": "EUR-Lex / European Union", "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:02000L0060-20141120"},
        {"title": "UHC service planning & models of care", "publisher": "World Health Organization", "url": "https://www.who.int/teams/integrated-health-services/clinical-services-and-systems/service-organizations-and-integration"}
    ]
}
,

"archive/727-routing-override-triad-for-ideal-governments-downward-intimacy-upward-guarantees-sideways-functional-authorities-and-no-scope-choice-by-prestige.md": {
    "groups": [
        {"title": "Beyond Markets and States: Polycentric Governance of Complex Economic Systems", "publisher": "Nobel Prize Outreach", "url": "https://www.nobelprize.org/prizes/economic-sciences/2009/ostrom/lecture/"},
        {"title": "Assigning responsibilities across levels of government", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html"},
        {"title": "Governing the City", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/governing-the-city_9789264226500-en.html"},
        {"title": "Regional Governance in OECD Countries", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/regional-governance-in-oecd-countries_4d7c6483-en.html"},
        {"title": "Effective Public Investment Toolkit", "publisher": "OECD", "url": "https://www.oecd.org/en/about/projects/effective-public-investment-toolkit.html"},
        {"title": "European Charter of Local Self-Government", "publisher": "Council of Europe", "url": "https://www.coe.int/en/web/impact-convention-human-rights/european-charter-of-local-self-government"},
        {"title": "The principle of subsidiarity", "publisher": "EUR-Lex / European Union", "url": "https://eur-lex.europa.eu/EN/legal-content/summary/the-principle-of-subsidiarity.html"},
        {"title": "United Nations Charter (full text)", "publisher": "United Nations", "url": "https://www.un.org/en/about-us/un-charter/full-text"},
        {"title": "International Health Regulations (2005)", "publisher": "World Health Organization", "url": "https://www.who.int/publications/i/item/9789241580496"},
        {"title": "Convention on the International Maritime Organization", "publisher": "International Maritime Organization", "url": "https://www.imo.org/en/About/Conventions/Pages/Convention-on-the-International-Maritime-Organization.aspx"},
        {"title": "Constitution and Convention Collection", "publisher": "International Telecommunication Union", "url": "https://www.itu.int/en/history/pages/constitutionandconvention.aspx"}
    ]
}
,

"archive/726-default-function-routing-table-for-ideal-governments-everyday-place-shared-systems-guarantor-duties-compact-unions-and-treaty-narrow-waists.md": {
    "groups": [
        {"title": "Beyond Markets and States: Polycentric Governance of Complex Economic Systems", "publisher": "Nobel Prize Outreach", "url": "https://www.nobelprize.org/prizes/economic-sciences/2009/ostrom/lecture/"},
        {"title": "Assigning responsibilities across levels of government", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html"},
        {"title": "Governing the City", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/governing-the-city_9789264226500-en.html"},
        {"title": "Regional Governance in OECD Countries", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/regional-governance-in-oecd-countries_4d7c6483-en.html"},
        {"title": "Effective Public Investment Toolkit", "publisher": "OECD", "url": "https://www.oecd.org/en/about/projects/effective-public-investment-toolkit.html"},
        {"title": "European Charter of Local Self-Government", "publisher": "Council of Europe", "url": "https://www.coe.int/en/web/impact-convention-human-rights/european-charter-of-local-self-government"},
        {"title": "The principle of subsidiarity", "publisher": "EUR-Lex / European Union", "url": "https://eur-lex.europa.eu/EN/legal-content/summary/the-principle-of-subsidiarity.html"},
        {"title": "United Nations Charter (full text)", "publisher": "United Nations", "url": "https://www.un.org/en/about-us/un-charter/full-text"},
        {"title": "International Health Regulations (2005)", "publisher": "World Health Organization", "url": "https://www.who.int/publications/i/item/9789241580496"},
        {"title": "Convention on the International Maritime Organization", "publisher": "International Maritime Organization", "url": "https://www.imo.org/en/About/Conventions/Pages/Convention-on-the-International-Maritime-Organization.aspx"},
        {"title": "Constitution and Convention Collection", "publisher": "International Telecommunication Union", "url": "https://www.itu.int/en/history/pages/constitutionandconvention.aspx"}
    ]
}
,

"archive/725-ideal-governance-stack-from-block-to-planet-territorial-tiers-functional-authorities-compact-unions-and-no-empty-tier-fetish.md": {
    "groups": [
        {"title": "Elinor Ostrom – Prize Lecture: Beyond Markets and States: Polycentric Governance of Complex Economic Systems", "publisher": "Nobel Prize Outreach", "url": "https://www.nobelprize.org/prizes/economic-sciences/2009/ostrom/lecture/"},
        {"title": "European Charter of Local Self-Government", "publisher": "Council of Europe", "url": "https://rm.coe.int/european-charter-of-local-self-government-eng/1680a87cc3"},
        {"title": "Additional Protocol on the right to participate in the affairs of a local authority", "publisher": "Council of Europe", "url": "https://www.coe.int/en/web/congress/additional-protocol-to-the-european-charter-of-local-self-government-on-the-right-to-participate-in-the-affairs-of-a-local-authority"},
        {"title": "Assigning responsibilities across levels of government", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html"},
        {"title": "Regional Governance in OECD Countries", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/regional-governance-in-oecd-countries_4d7c6483-en.html"},
        {"title": "Governing the City", "publisher": "OECD", "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2015/02/governing-the-city_g1g4d75d/9789264226500-en.pdf"},
        {"title": "The principle of subsidiarity", "publisher": "EUR-Lex / European Union", "url": "https://eur-lex.europa.eu/EN/legal-content/summary/the-principle-of-subsidiarity.html"},
        {"title": "United Nations Charter", "publisher": "United Nations", "url": "https://www.un.org/en/about-us/un-charter/full-text"},
        {"title": "International Health Regulations (2005)", "publisher": "World Health Organization", "url": "https://www.who.int/publications/i/item/9789241580496"},
        {"title": "International Maritime Organization", "publisher": "International Maritime Organization", "url": "https://www.imo.org/"}
    ]
}
,


"archive/724-guidance-packets-for-lane-typed-government-fields-rule-hierarchy-interpretive-notes-precedent-digests-reliance-boundaries-and-no-binding-law-by-helpdesk.md": {
    "groups": [
        {"title": "OECD Regulatory Policy Outlook 2025", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/oecd-regulatory-policy-outlook-2025_56b60e39-en.html"},
        {"title": "Recommendation of the Council on Regulatory Policy and Governance", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/recommendation-of-the-council-on-regulatory-policy-and-governance_9789264209022-en.html"},
        {"title": "Policy on Regulatory Transparency and Accountability", "publisher": "Government of Canada / Treasury Board of Canada Secretariat", "url": "https://www.canada.ca/en/government/system/laws/developing-improving-federal-regulations/requirements-developing-managing-reviewing-regulations/policy-regulatory-transparency-accountability.html"},
        {"title": "Policy on Providing Guidance on Regulatory Requirements", "publisher": "Innovation, Science and Economic Development Canada", "url": "https://ised-isde.canada.ca/site/acts-regulations/en/policy-providing-guidance-regulatory-requirements"},
        {"title": "Interpretation Policy: Global Affairs Canada", "publisher": "Global Affairs Canada", "url": "https://international.canada.ca/en/global-affairs/corporate/transparency/acts-regulations/interpretation-policy"},
        {"title": "Interpretations, Policies and Guidelines (IPGs)", "publisher": "Employment and Social Development Canada", "url": "https://www.canada.ca/en/employment-social-development/programs/laws-regulations/labour/interpretations-policies.html"},
        {"title": "Find HMRC manuals", "publisher": "HM Revenue & Customs", "url": "https://www.gov.uk/find-hmrc-manuals"},
        {"title": "VAT Tertiary Legislation", "publisher": "HM Revenue & Customs", "url": "https://www.gov.uk/guidance/vat-tertiary-legislation"},
        {"title": "UCC - Guidance documents", "publisher": "European Commission / DG TAXUD", "url": "https://taxation-customs.ec.europa.eu/customs/union-customs-code/ucc-guidance-documents_en"}
    ]
}
,


"archive/723-review-packets-for-lane-typed-government-fields-reconsideration-appeal-remand-interim-relief-finality-and-no-government-by-remedy-maze.md": {
    "groups": [
        {"title": "Making Justice Systems More Effective and People Centred", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/making-justice-systems-more-effective-and-people-centred_e02fd90b-en.html"},
        {"title": "Administrative justice as the interface between people and institutions", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/making-justice-systems-more-effective-and-people-centred_e02fd90b-en/full-report/administrative-justice-as-the-interface-between-people-and-institutions_88464c56.html"},
        {"title": "Toolkit for Access to Justice and People-Centred Justice Systems", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/toolkit-for-access-to-justice-and-people-centred-justice-systems_aecf7f78-en.html"},
        {"title": "Challenge a benefit decision (mandatory reconsideration)", "publisher": "GOV.UK", "url": "https://www.gov.uk/mandatory-reconsideration"},
        {"title": "Appeal a benefit decision", "publisher": "GOV.UK", "url": "https://www.gov.uk/appeal-benefit-decision"},
        {"title": "ARTG1030 - Introduction: reviews of HMRC decisions", "publisher": "UK Government / HM Revenue & Customs", "url": "https://www.gov.uk/hmrc-internal-manuals/appeals-reviews-and-tribunals-guidance/artg1030"},
        {"title": "ARTG2010 - Reviews and appeals overview: Process for direct taxes", "publisher": "UK Government / HM Revenue & Customs", "url": "https://www.gov.uk/hmrc-internal-manuals/appeals-reviews-and-tribunals-guidance/artg2010"},
        {"title": "CPP benefits - Request a reconsideration", "publisher": "Government of Canada", "url": "https://www.canada.ca/en/services/benefits/publicpensions/cpp/request-reconsideration.html"},
        {"title": "EI Reconsideration", "publisher": "Government of Canada", "url": "https://www.canada.ca/en/services/benefits/ei/ei-reconsideration.html"},
        {"title": "Resolving your dispute: Objection rights under the Income Tax Act", "publisher": "Government of Canada / CRA", "url": "https://www.canada.ca/en/revenue-agency/services/forms-publications/publications/p148/p148-resolving-your-dispute-objection-appeal-rights-under-income-tax-act.html"},
        {"title": "Objections, appeals, disputes, and relief measures", "publisher": "Government of Canada / CRA", "url": "https://www.canada.ca/en/revenue-agency/services/about-canada-revenue-agency-cra/complaints-disputes.html"},
        {"title": "Right to good administration", "publisher": "European Commission", "url": "https://commission.europa.eu/topics/human-rights/your-fundamental-rights-eu/know-your-rights/citizens-rights/right-good-administration_en"},
        {"title": "Code of Good Administrative Behaviour and complaints", "publisher": "European Commission", "url": "https://commission.europa.eu/about/service-standards-and-principles/ethics-and-good-administration/good-administration/code-good-administrative-behaviour-and-complaints_en"}
    ]
}
,

"archive/722-effect-packets-for-lane-typed-government-fields-activation-ladders-compliance-clocks-stay-rules-and-no-government-by-effective-date-alone.md": {
    "groups": [
        {"title": "OECD Regulatory Enforcement and Inspections Toolkit", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/oecd-regulatory-enforcement-and-inspections-toolkit_9789264303959-en.html"},
        {"title": "Regulatory Enforcement and Inspections", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/regulatory-enforcement-and-inspections_9789264208117-en.html"},
        {"title": "Compliance and Enforcement Strategy", "publisher": "GOV.UK / Marine Management Organisation", "url": "https://www.gov.uk/government/publications/compliance-and-enforcement-strategy/compliance-and-enforcement-strategy"},
        {"title": "Environmental permit - Guidance on the Appeal procedure", "publisher": "GOV.UK", "url": "https://www.gov.uk/government/publications/environmental-permit-appeal-form/environmental-permit-guidance-on-the-appeal-procedure"},
        {"title": "Labour Program administrative monetary penalties (AMP)", "publisher": "Government of Canada", "url": "https://www.canada.ca/en/employment-social-development/corporate/portfolio/labour/administrative-monetary-penalties.html"},
        {"title": "Administrative monetary penalties", "publisher": "Canadian Food Inspection Agency", "url": "https://inspection.canada.ca/en/inspection-and-enforcement/actions-taken/amps"}
    ]
}
,

"archive/721-notice-packets-for-lane-typed-government-fields-service-rules-proof-models-clock-starts-failed-delivery-and-no-government-by-presumed-receipt.md": {
    "groups": [
        {"title": "Service Section", "publisher": "HCCH", "url": "https://www.hcch.net/en/instruments/conventions/specialised-sections/service"},
        {"title": "Convention of 15 November 1965 on the Service Abroad of Judicial and Extrajudicial Documents in Civil or Commercial Matters", "publisher": "HCCH", "url": "https://www.hcch.net/en/instruments/conventions/full-text/?cid=17"},
        {"title": "PART 6 – SERVICE OF DOCUMENTS", "publisher": "Civil Procedure Rules / UK Ministry of Justice", "url": "https://www.justice.gov.uk/courts/procedure-rules/civil/rules/part06"},
        {"title": "PRACTICE DIRECTION 6A – SERVICE WITHIN THE UNITED KINGDOM", "publisher": "Civil Procedure Rules / UK Ministry of Justice", "url": "https://www.justice.gov.uk/courts/procedure-rules/civil/rules/part06/pd_part06a"},
        {"title": "More secure transactions on the Internet", "publisher": "EUR-Lex", "url": "https://eur-lex.europa.eu/EN/legal-content/summary/more-secure-transactions-on-the-internet.html"},
        {"title": "Consolidated text of Regulation (EU) No 910/2014 (eIDAS)", "publisher": "EUR-Lex", "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:02014R0910-20241018"},
        {"title": "How can I check if my application has been received?", "publisher": "Government of Canada / IRCC", "url": "https://ircc.canada.ca/english/helpcentre/answer.asp?qnum=028&top=4"},
        {"title": "How to check the status of your IRCC application", "publisher": "Government of Canada / IRCC", "url": "https://www.canada.ca/en/immigration-refugees-citizenship/services/application/check-status.html"},
        {"title": "Change your Correspondence preference online", "publisher": "Government of Canada / CRA", "url": "https://www.canada.ca/en/revenue-agency/services/update-information-cra/personal/change-mail-online.html"},
        {"title": "Disruption of Canada Post services", "publisher": "Government of Canada / Service Canada", "url": "https://www.canada.ca/en/employment-social-development/corporate/portfolio/service-canada/postal-disruption.html"}
    ]
}
,
"archive/720-decision-packets-for-lane-typed-government-fields-determination-class-reason-giving-effectivity-appeal-linkage-and-no-government-by-outcome-letter-alone.md": {
    "groups": [
        {"title": "Right to good administration", "publisher": "European Commission", "url": "https://commission.europa.eu/topics/human-rights/your-fundamental-rights-eu/know-your-rights/citizens-rights/right-good-administration_en"},
        {"title": "Code of Good Administrative Behaviour and complaints", "publisher": "European Commission", "url": "https://commission.europa.eu/about/service-standards-and-principles/ethics-and-good-administration/good-administration/code-good-administrative-behaviour-and-complaints_en"},
        {"title": "ARTG3050 - Reviews and appeals for indirect taxes: appealing against a decision or assessment: telling the customer of the decision", "publisher": "UK Government / HM Revenue & Customs", "url": "https://www.gov.uk/hmrc-internal-manuals/appeals-reviews-and-tribunals-guidance/artg3050"},
        {"title": "Procedural Guide: Planning appeals – England", "publisher": "GOV.UK", "url": "https://www.gov.uk/government/publications/planning-appeals-procedural-guide/procedural-guide-planning-appeals-england"},
        {"title": "Challenge a benefit decision (mandatory reconsideration)", "publisher": "GOV.UK", "url": "https://www.gov.uk/mandatory-reconsideration"},
        {"title": "Explaining application refusals: Officer decision notes", "publisher": "Government of Canada", "url": "https://www.canada.ca/en/immigration-refugees-citizenship/corporate/transparency/officer-decision-notes.html"},
        {"title": "CPP benefits - Request a reconsideration", "publisher": "Government of Canada", "url": "https://www.canada.ca/en/services/benefits/publicpensions/cpp/request-reconsideration.html"},
        {"title": "Cancel or waive penalties and interest: After you apply", "publisher": "Government of Canada", "url": "https://www.canada.ca/en/revenue-agency/services/about-canada-revenue-agency-cra/complaints-disputes/cancel-waive-penalties-interest/after-you-apply.html"}
    ]
}
,
"archive/719-case-packets-for-lane-typed-government-fields-intake-triage-state-model-lineage-notice-duty-and-no-government-by-unofficial-casework.md": {

    "groups": [
        {"title": "Seamless and accessible public administrative services", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/2025/06/government-at-a-glance-2025_70e14c6c/full-report/seamless-and-accessible-public-administrative-services_3dae4bc2.html"},
        {"title": "Roles and responsibilities for public administrative services design and delivery", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/2025/06/government-at-a-glance-2025_70e14c6c/full-report/roles-and-responsibilities-for-public-administrative-services-design-and-delivery_e939ff96.html"},
        {"title": "Service Standard", "publisher": "UK Government", "url": "https://www.gov.uk/service-manual/service-standard"},
        {"title": "GOV.UK Notify live assessment report", "publisher": "UK Government", "url": "https://www.gov.uk/service-standard-reports/gov-dot-uk-notify-live-assessment-report"},
        {"title": "Confirmation pages", "publisher": "GOV.UK Design System", "url": "https://design-system.service.gov.uk/patterns/confirmation-pages/"},
        {"title": "Natural Health Products Management of Applications Policy: Application screening and assessment", "publisher": "Government of Canada", "url": "https://www.canada.ca/en/health-canada/services/drugs-health-products/natural-health-products/legislation-guidelines/guidance-documents/management-product-licence-applications-attestations/application-screening-assessment.html"},
        {"title": "Competition Bureau Fees and Service Standards Handbook for Mergers and Merger-Related Matters", "publisher": "Government of Canada", "url": "https://competition-bureau.canada.ca/en/competition-bureau-fees-and-service-standards-handbook-mergers-and-merger-related-matters"},
        {"title": "How to check the status of your IRCC application", "publisher": "Government of Canada", "url": "https://www.canada.ca/en/immigration-refugees-citizenship/services/application/check-status.html"},
        {"title": "When can I check my application status?", "publisher": "Government of Canada", "url": "https://ircc.canada.ca/english/helpcentre/answer.asp?qnum=1494&top=3"},
        {"title": "Right to good administration", "publisher": "European Commission", "url": "https://commission.europa.eu/topics/human-rights/your-fundamental-rights-eu/know-your-rights/citizens-rights/right-good-administration_en"}
    ]
}
,
"archive/718-service-packets-for-lane-typed-government-fields-whole-service-front-doors-route-classes-service-floors-continuity-and-no-government-by-front-door-scatter.md": {
    "groups": [
        {"title": "Recommendation of the Council on Human-Centred Public Administrative Services", "publisher": "OECD Legal Instruments", "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0503"},
        {"title": "Strategies and institutional organisation for public administrative services delivery", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/government-at-a-glance-2025_0efd0bcd-en/full-report/strategies-and-institutional-organisation-for-public-administrative-services-delivery_0db8451f.html"},
        {"title": "Seamless and accessible public administrative services", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/government-at-a-glance-2025_0efd0bcd-en/full-report/seamless-and-accessible-public-administrative-services_3dae4bc2.html"},
        {"title": "Measurement, engagement and improvement of public administrative services", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/government-at-a-glance-2025_0efd0bcd-en/full-report/measurement-engagement-and-improvement-of-public-administrative-services_3b589a5f.html"},
        {"title": "Service Standard", "publisher": "UK Government", "url": "https://www.gov.uk/service-manual/service-standard"},
        {"title": "How government defines a service", "publisher": "UK Government / CDDO", "url": "https://services.blog.gov.uk/2024/09/25/how-government-defines-a-service/"},
        {"title": "Guideline on Service and Digital", "publisher": "Government of Canada", "url": "https://www.canada.ca/en/government/system/digital-government/guideline-service-digital.html"},
        {"title": "Public Service Delivery", "publisher": "World Bank", "url": "https://www.worldbank.org/en/programs/govtech/public-service-delivery"},
        {"title": "Indicators of citizen-centric public service delivery", "publisher": "World Bank", "url": "https://documents.worldbank.org/en/publication/documents-reports/documentdetail/775701527003544796"}
    ]
}
,
"archive/717-asset-packets-for-lane-typed-government-fields-estate-fleet-equipment-condition-discipline-handback-and-no-government-by-orphan-assets.md": {
    "groups": [
        {"title": "Management of assets throughout their life cycle", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/management-of-assets-throughout-their-life-cycle_86ce92d8-en.html"},
        {"title": "Effective Public Investment Toolkit", "publisher": "OECD", "url": "https://www.oecd.org/en/about/projects/effective-public-investment-toolkit.html"},
        {"title": "Government Functional Standard GovS 004: Property", "publisher": "UK Government", "url": "https://www.gov.uk/government/publications/government-standard-for-property-govs-004/government-functional-standard-govs-004-property"},
        {"title": "Facilities Management Standard 001: Management and Services", "publisher": "UK Government", "url": "https://www.gov.uk/government/publications/facilities-management-standards-for-govs-004-property/facilities-management-standard-001-management-and-services"},
        {"title": "PI-12. Public asset management", "publisher": "PEFA", "url": "https://www.pefa.org/node/4797"},
        {"title": "Bringing Public Assets Out of the Shadows: Optimizing Infrastructure Services, Unlocking Revenues", "publisher": "World Bank", "url": "https://documents.worldbank.org/en/publication/documents-reports/documentdetail/099070623155016874"},
        {"title": "Property, Plant, and Equipment", "publisher": "IFAC / IPSASB", "url": "https://www.ifac.org/consultations-projects/property-plant-and-equipment"}
    ]
}
,

"archive/716-information-packets-for-lane-typed-government-fields-canonical-case-home-access-model-sharing-boundaries-retention-clocks-and-no-government-by-portal-shell.md": {
    "groups": [
        {"title": "Digital government", "publisher": "OECD", "url": "https://www.oecd.org/en/topics/digital-government.html"},
        {"title": "Data governance", "publisher": "OECD", "url": "https://www.oecd.org/en/topics/data-governance.html"},
        {"title": "Federal Records Management", "publisher": "U.S. National Archives and Records Administration", "url": "https://www.archives.gov/records-mgmt"},
        {"title": "Records Management Regulations and Guidance", "publisher": "U.S. National Archives and Records Administration", "url": "https://www.archives.gov/records-mgmt/policy"},
        {"title": "Records management code", "publisher": "The National Archives (UK)", "url": "https://www.nationalarchives.gov.uk/information-management/manage-information/planning/records-management-code/"},
        {"title": "Digital Identity Guidelines (SP 800-63-4)", "publisher": "NIST", "url": "https://csrc.nist.gov/pubs/sp/800/63/4/final"},
        {"title": "Data sharing: a code of practice", "publisher": "Information Commissioner’s Office", "url": "https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-sharing/data-sharing-a-code-of-practice/"},
        {"title": "Cybersecurity Performance Goals (CPGs)", "publisher": "CISA", "url": "https://www.cisa.gov/cybersecurity-performance-goals-cpgs"},
        {"title": "GovTech Maturity Index (GTMI)", "publisher": "World Bank", "url": "https://www.worldbank.org/en/programs/govtech/gtmi"}
    ]
}
,



"archive/715-capability-packets-for-lane-typed-government-fields-employer-lane-merit-floor-training-ladders-surge-rosters-and-no-government-by-borrowed-payroll.md": {
    "groups": [
        {"title": "Public employment and management", "publisher": "OECD", "url": "https://www.oecd.org/en/topics/public-employment-and-management.html"},
        {"title": "Public service and human resource management", "publisher": "SIGMA / OECD", "url": "https://www.sigmaweb.org/en/thematic-areas/Public-service-and-human-resource-management.html"},
        {"title": "Public Workforce Performance and Prosperity", "publisher": "World Bank", "url": "https://www.worldbank.org/en/publication/public-workforce-performance-and-prosperity"},
        {"title": "Recruitment Principles", "publisher": "Civil Service Commission", "url": "https://civilservicecommission.independent.gov.uk/recruitment/recruitment-principles"},
        {"title": "Exceptions", "publisher": "Civil Service Commission", "url": "https://civilservicecommission.independent.gov.uk/recruitment/exceptions"},
        {"title": "Civil Service People Plan 2024-2027", "publisher": "UK Government People Group", "url": "https://www.gov.uk/government/publications/civil-service-people-plan-2024-2027"},
        {"title": "Public service", "publisher": "International Labour Organization", "url": "https://www.ilo.org/topics-and-sectors/industries-and-sectors/public-service"}
    ]
}
,
"archive/714-fiscal-packets-for-lane-typed-government-fields-operating-base-equalization-spine-reserves-capital-lanes-and-no-government-by-grant-fog.md": {
    "groups": [
        {"title": "Public finance and budgets", "publisher": "OECD", "url": "https://www.oecd.org/en/topics/public-finance-and-budgets.html"},
        {"title": "Fiscal federalism network", "publisher": "OECD", "url": "https://www.oecd.org/en/topics/fiscal-federalism-network.html"},
        {"title": "Intergovernmental fiscal transfers and fiscal equalisation in a time of consolidation", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/intergovernmental-fiscal-transfers-and-fiscal-equalisation-in-a-time-of-consolidation_4853a4d0-en.html"},
        {"title": "How Does the IMF Encourage Greater Fiscal Transparency?", "publisher": "International Monetary Fund", "url": "https://www.imf.org/en/about/factsheets/sheets/2023/how-does-the-imf-encourage-greater-fiscal-transparency"},
        {"title": "Public Expenditure and Financial Accountability (PEFA)", "publisher": "PEFA", "url": "https://www.pefa.org/"},
        {"title": "A Practitioner's Guide to Intergovernmental Fiscal Transfers", "publisher": "World Bank", "url": "https://openknowledge.worldbank.org/entities/publication/a6fcf378-81ae-5fdb-82b5-52e7ea504dd0"}
    ]
}
,
"archive/713-delegation-packets-for-lane-typed-government-fields-principal-lane-reserved-powers-operator-chains-step-in-rights-and-no-public-duty-by-outsourced-wrapper.md": {
    "groups": [
        {"title": "The Sourcing Playbook", "publisher": "UK Cabinet Office / Government Commercial Function", "url": "https://www.gov.uk/government/publications/the-sourcing-and-consultancy-playbooks"},
        {"title": "Assessing and monitoring the Economic and Financial Standing of Suppliers guidance note (HTML)", "publisher": "UK Government", "url": "https://www.gov.uk/government/publications/the-sourcing-and-consultancy-playbooks/assessing-and-monitoring-the-economic-and-financial-standing-of-suppliers-guidance-note-html--2"},
        {"title": "Risk Allocation and Pricing Approaches guidance note (HTML)", "publisher": "UK Government", "url": "https://www.gov.uk/government/publications/the-sourcing-and-consultancy-playbooks/risk-allocation-and-pricing-approaches-guidance-note-html"},
        {"title": "Public procurement", "publisher": "OECD", "url": "https://www.oecd.org/en/topics/public-procurement.html"},
        {"title": "Contracting Out Government Services", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/contracting-out-government-services_9789264162174-en.html"},
        {"title": "PPP Resource Center", "publisher": "World Bank", "url": "https://ppp.worldbank.org/"},
        {"title": "Establishing Contract Management Structures", "publisher": "World Bank", "url": "https://ppp.worldbank.org/establishing-contract-management-structures"},
        {"title": "Procurement Framework", "publisher": "World Bank Group", "url": "https://www.worldbank.org/ext/en/what-we-do/project-procurement/framework"},
        {"title": "Contract Management Capability Programme (HTML)", "publisher": "UK Government", "url": "https://www.gov.uk/government/publications/civil-service-helping-you-with-managing-suppliers-and-contracts/contract-management-capability-programme-html"}
    ]
}
,
"archive/712-amendment-packets-for-lane-typed-government-fields-change-classes-ratification-ladders-version-ledgers-drift-logs-and-no-field-redesign-by-memo.md": {
    "groups": [
        {"title": "OECD Regulatory Policy Outlook 2025", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/oecd-regulatory-policy-outlook-2025_56b60e39-en.html"},
        {"title": "OECD Best Practice Principles for Regulatory Policy", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/oecd-best-practice-principles-for-regulatory-policy_23116013.html"},
        {"title": "Policy development and co-ordination", "publisher": "SIGMA / OECD", "url": "https://www.sigmaweb.org/en/thematic-areas/Policy-development-and-co-ordination.html"},
        {"title": "Guide to making legislation", "publisher": "UK Cabinet Office", "url": "https://www.gov.uk/government/publications/guide-to-making-legislation"},
        {"title": "Consultation principles", "publisher": "UK Government", "url": "https://www.gov.uk/government/publications/consultation-principles-guidance/consultation-principles-2018"},
        {"title": "Have your say", "publisher": "European Commission", "url": "https://ec.europa.eu/info/law/better-regulation/"},
        {"title": "WHO Governance / Basic documents", "publisher": "World Health Organization", "url": "https://apps.who.int/gb/gov/"}
    ]
}
,
"archive/711-oversight-packets-for-lane-typed-government-fields-audit-inspection-ombuds-parliamentary-scrutiny-follow-up-ledgers-and-no-self-certification-by-the-same-office.md": {
    "groups": [
        {"title": "Documents", "publisher": "INTOSAI", "url": "https://www.intosai.org/documents.html"},
        {"title": "Self-assessment tools", "publisher": "Inter-Parliamentary Union", "url": "https://www.ipu.org/impact/democracy-and-strong-parliaments/ipu-standards/self-assessment-tools"},
        {"title": "Organisation, accountability and oversight", "publisher": "SIGMA / OECD", "url": "https://www.sigmaweb.org/en/thematic-areas/Organisation%2C-accountability-and-oversight.html"},
        {"title": "Organisation of public administration: Agency governance, autonomy and accountability", "publisher": "SIGMA / OECD", "url": "https://www.sigmaweb.org/en/publications/organisation-of-public-administration_07316cc3-en.html"},
        {"title": "Complaint Standards", "publisher": "Parliamentary and Health Service Ombudsman", "url": "https://www.ombudsman.org.uk/organisations-we-investigate/complaint-standards"},
        {"title": "Our Main Functions", "publisher": "World Bank Accountability Mechanism", "url": "https://accountability.worldbank.org/en/main-functions"},
        {"title": "25 Venice Principles - Democratic ABCs for ombudsman institutions", "publisher": "Council of Europe", "url": "https://www.coe.int/en/web/portal/-/25-venice-principles-democratic-abcs-for-ombudsman-institutions"}
    ]
}
,
"archive/710-participation-packets-for-lane-typed-government-fields-agenda-windows-method-fit-inclusion-duties-response-ledgers-and-no-public-input-by-one-off-hearing.md": {
    "groups": [
        {"title": "Open government and citizen participation", "publisher": "OECD", "url": "https://www.oecd.org/en/topics/open-government-and-citizen-participation.html"},
        {"title": "OECD Guidelines for Citizen Participation Processes", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/oecd-guidelines-for-citizen-participation-processes_f765caf6-en.html"},
        {"title": "Citizen participation and deliberation: Government at a Glance 2025", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/government-at-a-glance-2025_0efd0bcd-en/full-report/citizen-participation-and-deliberation_52b90285.html"},
        {"title": "Taking Action to Achieve Meaningful Citizen Participation", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/exploring-new-frontiers-in-citizen-participation-in-the-policy-cycle_77f5098c-en/full-report/taking-action-to-achieve-meaningful-citizen-participation_e0665ac3.html"},
        {"title": "Guidelines for civil participation in political decision making", "publisher": "Council of Europe", "url": "https://www.coe.int/en/web/participatory-democracy/guidelines"},
        {"title": "Consultation principles: guidance", "publisher": "UK Government", "url": "https://www.gov.uk/government/publications/consultation-principles-guidance"},
        {"title": "Citizen Engagement", "publisher": "World Bank", "url": "https://www.worldbank.org/en/programs/govtech/citizen-engagement"}
    ]
}
,
"archive/709-challenge-packets-for-lane-typed-government-fields-entry-routes-complaints-petitions-second-look-lanes-feedback-duties-and-no-public-voice-by-consultation-theater.md": {
    "groups": [
        {"title": "Open government and citizen participation", "publisher": "OECD", "url": "https://www.oecd.org/en/topics/open-government-and-citizen-participation.html"},
        {"title": "OECD Guidelines for Citizen Participation Processes", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/oecd-guidelines-for-citizen-participation-processes_f765caf6-en.html"},
        {"title": "OECD Recommendation of the Council on Open Government", "publisher": "OECD", "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0438"},
        {"title": "Complaint Standards", "publisher": "Parliamentary and Health Service Ombudsman", "url": "https://www.ombudsman.org.uk/organisations-we-investigate/complaint-standards"},
        {"title": "Grievance Redress Service", "publisher": "World Bank", "url": "https://www.worldbank.org/en/projects-operations/products-and-services/grievance-redress-service"},
        {"title": "Code of Good Administrative Behaviour and complaints", "publisher": "European Commission", "url": "https://commission.europa.eu/about/service-standards-and-principles/ethics-and-good-administration/good-administration/code-good-administrative-behaviour-and-complaints_en"}
    ]
}
,

"archive/708-evidence-packets-for-lane-typed-government-fields-shared-indicators-trigger-maps-blind-spot-registers-assurance-rhythm-and-no-government-by-dashboard-vibes.md": {
    "groups": [
        {"title": "Public policy monitoring and evaluation", "publisher": "OECD", "url": "https://www.oecd.org/en/topics/public-policy-monitoring-and-evaluation.html"},
        {"title": "Multi-level governance", "publisher": "OECD", "url": "https://www.oecd.org/en/topics/multi-level-governance.html"},
        {"title": "Effective Public Investment Toolkit", "publisher": "OECD", "url": "https://www.oecd.org/en/about/projects/effective-public-investment-toolkit.html"},
        {"title": "Magenta Book: Central Government guidance on evaluation (HTML)", "publisher": "UK HM Treasury / GOV.UK", "url": "https://www.gov.uk/government/publications/the-magenta-book/magenta-book-central-government-guidance-on-evaluation-html"},
        {"title": "International Health Regulations Monitoring and Evaluation Framework", "publisher": "World Health Organization", "url": "https://www.who.int/emergencies/operations/international-health-regulations-monitoring-evaluation-framework"},
        {"title": "The Theory of Change Process – Guidance for Outcome Based Evaluation", "publisher": "UK Government Analysis Function", "url": "https://analysisfunction.civilservice.gov.uk/policy-store/the-analysis-function-theory-of-change-toolkit/"}
    ]
}
,
"archive/707-sunset-packets-for-obsolete-government-lanes-bodies-and-temporary-machinery-review-triggers-successor-homes-residue-registers-closure-proof-and-no-immortal-institutions-by-inherited-backlog.md": {
    "groups": [
        {"title": "Public bodies", "publisher": "UK Cabinet Office", "url": "https://www.gov.uk/guidance/public-bodies-reform"},
        {"title": "Requirements for Reviews of Public Bodies", "publisher": "UK Cabinet Office", "url": "https://www.gov.uk/government/publications/public-bodies-review-programme/requirements-for-reviews-of-public-bodies"},
        {"title": "Guidance on the undertaking of Reviews of Public Bodies", "publisher": "UK Cabinet Office", "url": "https://www.gov.uk/government/publications/public-bodies-review-programme/guidance-on-the-undertaking-of-reviews-of-public-bodies"},
        {"title": "What to do with your records if your public body is undergoing a status change", "publisher": "The National Archives", "url": "https://cdn.nationalarchives.gov.uk/documents/information-management/dissolution-of-public-bodies.pdf"},
        {"title": "Public Bodies Act 2011 - Explanatory Notes", "publisher": "UK legislation.gov.uk", "url": "https://www.legislation.gov.uk/ukpga/2011/24/notes/contents"},
        {"title": "Organisation of public administration: Agency governance, autonomy and accountability", "publisher": "SIGMA / OECD", "url": "https://www.sigmaweb.org/en/publications/organisation-of-public-administration_07316cc3-en.html"}
    ]
}
,
"archive/706-repair-packets-for-recurrently-failing-government-fields-after-action-conversion-root-cause-ownership-funding-lanes-closure-proof-and-no-government-by-permanent-recovery-mode.md": {
    "groups": [
        {"title": "Homeland Security Exercise Evaluation Program", "publisher": "FEMA", "url": "https://preptoolkit.fema.gov/web/hseep-resources"},
        {"title": "Improvement Planning Templates", "publisher": "FEMA", "url": "https://preptoolkit.fema.gov/web/hseep-resources/improvement-planning"},
        {"title": "Emergency response reviews", "publisher": "World Health Organization", "url": "https://www.who.int/emergencies/operations/emergency-response-reviews"},
        {"title": "Intra-action review", "publisher": "World Health Organization", "url": "https://www.who.int/emergencies/operations/emergency-response-reviews/intra-action-review"},
        {"title": "Multi-level governance", "publisher": "OECD", "url": "https://www.oecd.org/en/topics/multi-level-governance.html"},
        {"title": "Managing Emerging Critical Risks", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/managing-emerging-critical-risks_1f9858ea-en.html"}
    ]
}
,

"archive/705-mode-packets-for-lane-typed-government-fields-normal-degraded-emergency-recovery-handback-clocks-and-no-permanent-government-by-exception.md": {
    "groups": [
        {"title": "National Incident Management System (NIMS)", "publisher": "FEMA", "url": "https://www.fema.gov/emergency-managers/nims"},
        {"title": "NIMS Components — Guidance and Tools", "publisher": "FEMA", "url": "https://www.fema.gov/emergency-managers/nims/components"},
        {"title": "UK Government Resilience Action Plan", "publisher": "UK Cabinet Office", "url": "https://www.gov.uk/government/publications/uk-government-resilience-action-plan/uk-government-resilience-action-plan-html"},
        {"title": "Sendai Framework for Disaster Risk Reduction 2015-2030", "publisher": "UNDRR", "url": "https://www.undrr.org/publication/sendai-framework-disaster-risk-reduction-2015-2030"},
        {"title": "National health emergency alert and response framework", "publisher": "World Health Organization", "url": "https://www.who.int/publications/i/item/9789240113893"},
        {"title": "Building resilience through disaster risk management in intermediary cities", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/building-resilience-through-disaster-risk-management-in-intermediary-cities_b2f1efb1-en.html"}
    ]
}
,
"archive/704-control-plane-packets-for-lane-typed-government-fields-priorities-common-ledger-exception-queues-and-no-hidden-center-by-coordination.md": {
    "groups": [
        {"title": "Multi-level governance", "publisher": "OECD", "url": "https://www.oecd.org/en/topics/multi-level-governance.html"},
        {"title": "Effective Public Investment Toolkit", "publisher": "OECD", "url": "https://www.oecd.org/en/about/projects/effective-public-investment-toolkit.html"},
        {"title": "OECD Recommendation on Regional Development Policy", "publisher": "OECD", "url": "https://www.oecd.org/en/about/projects/implementing-the-oecd-recommendation-on-regional-development-policy-toolkit.html"},
        {"title": "National Urban Policy", "publisher": "UN-Habitat", "url": "https://unhabitat.org/programme/national-urban-policy"},
        {"title": "Strengthening Institutions for Urban and Metropolitan Management and Service Delivery", "publisher": "World Bank", "url": "https://openknowledge.worldbank.org/entities/publication/30e29830-a739-52c7-8cb2-ea7baf8535e0"}
    ]
}
,
"archive/703-interface-packets-for-lane-typed-government-stacks-lead-lanes-handoffs-shared-facts-escalation-clocks-and-no-governance-by-glue-folklore.md": {
    "groups": [
        {"title": "Assigning responsibilities across levels of government", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html"},
        {"title": "Effective Public Investment Toolkit", "publisher": "OECD", "url": "https://www.oecd.org/en/about/projects/effective-public-investment-toolkit.html"},
        {"title": "European Charter of Local Self-Government (ETS No. 122)", "publisher": "Council of Europe", "url": "https://www.coe.int/en/web/conventions/full-list/-/conventions/treaty/122"},
        {"title": "Strengthening Institutions for Urban and Metropolitan Management and Service Delivery", "publisher": "World Bank", "url": "https://openknowledge.worldbank.org/entities/publication/30e29830-a739-52c7-8cb2-ea7baf8535e0"},
        {"title": "National Urban Policy", "publisher": "UN-Habitat", "url": "https://unhabitat.org/programme/national-urban-policy"}
    ]
}
,
"archive/702-unbundling-mixed-function-claims-before-scope-choice-lane-split-first-packet-second-rivalry-third-and-no-one-tier-answer-to-a-composite-field.md": {
    "groups": [
        {"title": "Assigning responsibilities across levels of government", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html"},
        {"title": "European Charter of Local Self-Government (ETS No. 122)", "publisher": "Council of Europe", "url": "https://www.coe.int/en/web/conventions/full-list/-/conventions/treaty/122"},
        {"title": "Strengthening Institutions for Urban and Metropolitan Management and Service Delivery", "publisher": "World Bank", "url": "https://openknowledge.worldbank.org/entities/publication/30e29830-a739-52c7-8cb2-ea7baf8535e0"},
        {"title": "Regional Governance in OECD Countries", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/regional-governance-in-oecd-countries_4d7c6483-en.html"},
        {"title": "National Urban Policy", "publisher": "UN-Habitat", "url": "https://unhabitat.org/programme/national-urban-policy"}
    ]
}
,
"archive/701-adjudication-matrix-for-competing-ideal-governments-of-the-same-function-packet-comparison-dominance-tests-reversible-tie-breaks-and-no-scope-choice-by-ideology-alone.md": {
    "groups": [
        {"title": "Assigning responsibilities across levels of government", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html"},
        {"title": "Recommendation of the Council on Regulatory Policy and Governance", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/recommendation-of-the-council-on-regulatory-policy-and-governance_9789264209022-en.html"},
        {"title": "Effective Public Investment Toolkit", "publisher": "OECD", "url": "https://www.oecd.org/en/about/projects/effective-public-investment-toolkit.html"},
        {"title": "European Charter of Local Self-Government (ETS No. 122)", "publisher": "Council of Europe", "url": "https://www.coe.int/en/web/conventions/full-list/-/conventions/treaty/122"},
        {"title": "Regional Governance in OECD Countries", "publisher": "OECD", "url": "https://www.oecd.org/en/publications/regional-governance-in-oecd-countries_4d7c6483-en.html"},
        {"title": "National Urban Policy", "publisher": "UN-Habitat", "url": "https://unhabitat.org/programme/national-urban-policy"}
    ]
}
,
"archive/700-minimum-design-packet-for-ideal-governments-of-each-scope-archetype-vocation-boundary-kit-fiscal-proof-exception-ladder-upgrade-triggers-and-no-essay-length-restatement.md": {
    "groups": [
        {"title": "Assigning responsibilities across levels of government", "publisher": "OECD", "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2018/09/assigning-responsibilities-across-levels-of-government_d3650b01/f0944eae-en.pdf"},
        {"title": "European Charter of Local Self-Government (ETS No. 122)", "publisher": "Council of Europe", "url": "https://www.coe.int/en/web/conventions/full-list/-/conventions/treaty/122"},
        {"title": "Regional Governance in OECD Countries", "publisher": "OECD", "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2022/12/regional-governance-in-oecd-countries_a9c03edb/4d7c6483-en.pdf"},
        {"title": "Strengthening Institutions for Urban and Metropolitan Management and Service Delivery", "publisher": "World Bank", "url": "https://openknowledge.worldbank.org/entities/publication/30e29830-a739-52c7-8cb2-ea7baf8535e0"},
        {"title": "World Public Sector Report 2023", "publisher": "United Nations DESA", "url": "https://desapublications.un.org/sites/default/files/publications/2023-10/World%20Public%20Sector%20Report%202023.pdf"}
    ]
}
,
"archive/699-scope-spine-for-ideal-governments-seven-default-tiers-label-to-vocation-crosswalks-two-exception-ladders-and-no-new-tier-theory-every-time.md": {
    "groups": [
        {"title": "Assigning responsibilities across levels of government", "publisher": "OECD", "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2018/09/assigning-responsibilities-across-levels-of-government_d3650b01/f0944eae-en.pdf"},
        {"title": "European Charter of Local Self-Government (ETS No. 122)", "publisher": "Council of Europe", "url": "https://www.coe.int/en/web/conventions/full-list/-/conventions/treaty/122"},
        {"title": "Strengthening Institutions for Urban and Metropolitan Management and Service Delivery", "publisher": "World Bank", "url": "https://openknowledge.worldbank.org/entities/publication/30e29830-a739-52c7-8cb2-ea7baf8535e0"},
        {"title": "Regional Governance in OECD Countries", "publisher": "OECD", "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2022/12/regional-governance-in-oecd-countries_a9c03edb/4d7c6483-en.pdf"},
        {"title": "Fiscal challenges in small states", "publisher": "World Bank", "url": "https://thedocs.worldbank.org/en/doc/f43fb9163f5e4704740c30b614a9ad59-0050012024/related/GEP-June-2024-Topical-Issue-2.pdf"},
        {"title": "World Public Sector Report 2023", "publisher": "United Nations DESA", "url": "https://desapublications.un.org/sites/default/files/publications/2023-10/World%20Public%20Sector%20Report%202023.pdf"},
        {"title": "Our Common Agenda — Section 4", "publisher": "United Nations", "url": "https://www.un.org/en/content/common-agenda-report/assets/pdf/Our_Common_Agenda_English_Section_4.pdf"}
    ]
}
,
"archive/698-shared-regime-implementing-partner-and-pass-through-constitutions-due-diligence-workplans-cash-transfer-assurance-suspension-closeout-and-no-mission-by-subaward-fog.md": {
    "groups": [
        {"title": "Framework of Engagement with Non-State Actors (FENSA)", "publisher": "World Health Organization", "url": "https://apps.who.int/gb/bd/PDF/Framework_Engagement_non-State_Actors.pdf"},
        {"title": "Guide for staff on engagement with non-State actors", "publisher": "World Health Organization", "url": "https://iris.who.int/bitstream/handle/10665/366748/WHO-CRE-DAN-2023.2-eng.pdf"},
        {"title": "Non-State actors in official relations with WHO (EB156/39)", "publisher": "World Health Organization", "url": "https://apps.who.int/gb/ebwha/pdf_files/EB156/B156_39-en.pdf"},
        {"title": "Non-State actors in official relations with WHO (EB154/37)", "publisher": "World Health Organization", "url": "https://apps.who.int/gb/ebwha/pdf_files/EB154/B154_37-en.pdf"},
        {"title": "UNICEF HACT Policy", "publisher": "UNICEF", "url": "https://open.unicef.org/sites/transparency/files/documents/UNICEF_HACT_Policy.pdf"},
        {"title": "UNICEF HACT Procedure", "publisher": "UNICEF", "url": "https://open.unicef.org/sites/transparency/files/documents/UNICEF_HACT_Procedure.pdf"},
        {"title": "Harmonized Approach to Cash Transfers (HACT) Framework", "publisher": "United Nations Sustainable Development Group", "url": "https://unsdg.un.org/sites/default/files/HACT-2014-UNDG-Framework-EN.pdf"},
        {"title": "Summary of Harmonized approach to cash transfers (HACT)", "publisher": "UNICEF Agora", "url": "https://agora.unicef.org/course/view.php?id=1312"}
    ]
}
,
"archive/697-shared-regime-strategic-planning-and-results-constitutions-general-programmes-programme-budgets-theories-of-change-baselines-targets-reviews-and-no-mission-by-project-pile.md": {
    "groups": [
        {"title": "Programme Budget Digital Platform 2024-2025", "publisher": "World Health Organization", "url": "https://www.who.int/about/accountability/budget/programme-budget-digital-platform-2024-2025"},
        {"title": "WHO Results Report 2024-2025", "publisher": "World Health Organization", "url": "https://www.who.int/about/accountability/results/who-results-report-2024-2025"},
        {"title": "Results report 2024 (Programme budget 2024–2025: performance assessment)", "publisher": "World Health Organization", "url": "https://apps.who.int/gb/ebwha/pdf_files/WHA78/A78_17-en.pdf"},
        {"title": "WHO Fourteenth General Programme of Work, 2025-2028", "publisher": "World Health Organization", "url": "https://www.who.int/about/general-programme-of-work/fourteenth"},
        {"title": "A Global Health Strategy for 2025–2028", "publisher": "World Health Organization", "url": "https://www.who.int/publications/i/item/9789240101012"},
        {"title": "Setting technical priorities at country level", "publisher": "World Health Organization", "url": "https://www.who.int/about/accountability/budget/programme-budget-digital-platform-2024-2025/setting-technical-priorities-at-country-level"}
    ]
}
,

"archive/696-shared-regime-evaluation-and-learning-constitutions-workplans-independence-management-response-recommendation-tracking-after-action-review-and-no-regime-by-report-shelf.md": {
    "groups": [
        {"title": "WHO Evaluation Office", "publisher": "World Health Organization", "url": "https://www.who.int/about/evaluation"},
        {"title": "WHO Evaluation Office — Policy and governance", "publisher": "World Health Organization", "url": "https://www.who.int/about/evaluation/policy-and-governance"},
        {"title": "Evaluation Policy (2025)", "publisher": "World Health Organization", "url": "https://www.who.int/publications/b/81396"},
        {"title": "Evaluation workplan 2024–2025", "publisher": "World Health Organization", "url": "https://www.who.int/publications/m/item/evaluation-workplan-2024---2025"},
        {"title": "2024 Evaluation Annual Report (EB155/4)", "publisher": "World Health Organization", "url": "https://www.who.int/publications/m/item/2024-evaluation-annual-report-%28en155-4%29"},
        {"title": "UNEG Norms and Standards for Evaluation in the UN System", "publisher": "United Nations Evaluation Group", "url": "https://www.unevaluation.org/uneg_publications/uneg-norms-and-standards-evaluation-un-system"},
        {"title": "Administrative Instruction on Evaluation", "publisher": "United Nations Policy Portal", "url": "https://policy.un.org/sites/default/files/files/documents/2022/Jan/evaluation_administrative_instruction_-_guidelines.pdf"},
        {"title": "Guidance for after action review (AAR)", "publisher": "World Health Organization", "url": "https://www.who.int/publications/i/item/WHO-WHE-CPI-2019.4"}
    ]
}
,
"archive/695-shared-regime-enterprise-risk-and-internal-control-constitutions-risk-appetite-owners-registers-control-testing-exceptions-assurance-maps-and-no-governance-by-unknown-exposure.md": {
    "groups": [
        {"title": "WHO Risk Management Strategy", "publisher": "World Health Organization", "url": "https://www.who.int/publications/m/item/risk-management-strategy"},
        {"title": "Principal Risks", "publisher": "World Health Organization", "url": "https://www.who.int/publications/m/item/principal-risks"},
        {"title": "WHO Risk Appetite Statement (May 2025)", "publisher": "World Health Organization", "url": "https://www.who.int/about/governance/member-states-portal"},
        {"title": "Compliance, risk management and ethics: annual report", "publisher": "World Health Organization", "url": "https://apps.who.int/gb/pbac/pdf_files/PBAC42/PBAC42_4-en.pdf"},
        {"title": "Enterprise Risk Management and Internal Control Policy", "publisher": "United Nations Policy Portal", "url": "https://policy.un.org/sites/default/files/files/documents/2022/May/enterprise_risk_management_and_internal_control.pdf"},
        {"title": "Statement on Internal Control", "publisher": "United Nations Policy Portal", "url": "https://policy.un.org/en/accountability/internal-controls/statement-internal-control"},
        {"title": "Internal control and audit", "publisher": "OECD", "url": "https://www.oecd.org/en/topics/internal-control-and-audit-in-the-public-sector.html"}
    ]
}
,

"archive/694-shared-regime-statistics-and-indicator-constitutions-designation-methodology-metadata-revisions-quality-assurance-release-calendars-and-no-governance-by-number-theater.md": {
    "groups": [
        {"title": "Fundamental Principles of Official Statistics", "publisher": "United Nations Statistics Division", "url": "https://unstats.un.org/fpos/"},
        {"title": "UN Fundamental Principles of Official Statistics handbook section", "publisher": "United Nations Statistics Division", "url": "https://unstats.un.org/capacity-development/handbook/html/Handbook/C3/UN_Fundamental_Principles_of_Official_Statistics.htm"},
        {"title": "Maturity Model on Quality Culture in Official Statistics", "publisher": "United Nations Statistics Division", "url": "https://unstats.un.org/unsd/methodology/dataquality/qc/"},
        {"title": "WHO data principles", "publisher": "World Health Organization", "url": "https://www.who.int/data/principles"},
        {"title": "Indicator Metadata Registry List", "publisher": "World Health Organization", "url": "https://www.who.int/data/gho/indicator-metadata-registry"},
        {"title": "Data quality assurance (DQA)", "publisher": "World Health Organization", "url": "https://www.who.int/data/data-collection-tools/health-service-data/data-quality-assurance-dqa"}
    ]
}
,
"archive/693-shared-regime-personal-data-and-privacy-constitutions-legal-basis-purpose-limits-minimization-subject-rights-transfers-breach-response-and-no-mission-by-data-drift.md": {
    "groups": [
        {"title": "WHO Personal Data Protection Policy", "publisher": "World Health Organization", "url": "https://www.who.int/publications/m/item/who-personal-data-protection-policy"},
        {"title": "WHO data policy", "publisher": "World Health Organization", "url": "https://data.who.int/about/data/data-policy"},
        {"title": "WHO data principles", "publisher": "World Health Organization", "url": "https://www.who.int/data/principles"},
        {"title": "Data Protection", "publisher": "United Nations Policy Portal", "url": "https://policy.un.org/en/information-and-technology/data-protection"},
        {"title": "Data protection and privacy policy for the Secretariat of the United Nations (ST/SGB/2024/3)", "publisher": "United Nations", "url": "https://docs.un.org/en/st/SGB/2024/3"},
        {"title": "UN Guide on Privacy-Enhancing Technologies for Official Statistics", "publisher": "United Nations Statistics Division", "url": "https://unstats.un.org/bigdata/task-teams/privacy/guide/"}
    ]
}
,
"archive/692-shared-regime-digital-and-cyber-operating-constitutions-system-owners-identity-and-access-admin-tiers-change-windows-incident-response-vulnerability-disclosure-backups-recovery-vendor-lanes-and-no-secretariat-by-shared-password.md": {
    "groups": [
        {"title": "WHO Data Policy", "publisher": "World Health Organization", "url": "https://www.who.int/about/policies/publishing/data-policy"},
        {"title": "Vulnerability Hall of Fame", "publisher": "World Health Organization", "url": "https://www.who.int/about/cybersecurity/vulnerability-hall-of-fame"},
        {"title": "Effective, innovative and secure digital platforms and services aligned with the needs of users, corporate functions, technical programmes and health emergencies operations", "publisher": "World Health Organization", "url": "https://www.who.int/about/accountability/results/who-results-report-2022-mtr/output/2022/effective--innovative-and-secure-digital-platforms-and-services-aligned-with-the-needs-of-users--corporate-functions--technical-programmes-and-health-emergencies-operations"},
        {"title": "Report of the Internal Auditor", "publisher": "World Health Organization", "url": "https://apps.who.int/gb/ebwha/pdf_files/WHA78/A78_26-en.pdf"},
        {"title": "Use of information and communication technology resources and data", "publisher": "United Nations Secretariat", "url": "https://docs.un.org/en/st/sgb/2004/15"},
        {"title": "United Nations Responsible Disclosure & Reporter Acknowledgment Policy", "publisher": "United Nations Office of Information and Communications Technology", "url": "https://unite.un.org/en/united-nations-responsible-disclosure-reporter-acknowledgment-policy"},
        {"title": "Managing Risk", "publisher": "United Nations Archives and Records Management Section", "url": "https://archives.un.org/en/content/managing-risk"},
        {"title": "How do I protect records from loss or damage?", "publisher": "United Nations Archives and Records Management Section", "url": "https://archives.un.org/sites/default/files/RM-Guidelines/guidance_protecting_records_from_loss.pdf"},
        {"title": "How do I know which records are vital?", "publisher": "United Nations Archives and Records Management Section", "url": "https://archives.un.org/sites/default/files/RM-Guidelines/guidance_vital_records.pdf"}
    ]
}
,
"archive/691-shared-regime-information-classification-and-disclosure-constitutions-public-on-request-internal-confidential-strict-harm-tests-downgrading-external-sharing-and-no-secrecy-by-folder-folklore.md": {
    "groups": [
        {"title": "Information Disclosure Policy", "publisher": "World Health Organization", "url": "https://cdn.who.int/media/docs/default-source/documents/about-us/infodisclosurepolicy.pdf?sfvrsn=c1520275_11"},
        {"title": "WHO Data Policy", "publisher": "World Health Organization", "url": "https://www.who.int/about/policies/publishing/data-policy"},
        {"title": "Data and Information", "publisher": "United Nations Policy Portal", "url": "https://policy.un.org/en/information-and-technology/data-and-information"},
        {"title": "Managing Risk", "publisher": "United Nations Archives and Records Management Section", "url": "https://archives.un.org/en/content/managing-risk"},
        {"title": "Guidelines for Sharing United Nations Official Information with External Parties", "publisher": "United Nations Archives and Records Management Section", "url": "https://archives.un.org/sites/default/files/guideline_-_sharing_united_nations_official_information_with_external_parties.pdf"}
    ]
}
,

"archive/690-shared-regime-field-security-and-continuity-constitutions-designated-officials-risk-tiers-clearance-crisis-cells-stockpiles-evacuation-and-no-presence-by-hope.md": {
    "groups": [
        {"title": "United Nations Security Management System", "publisher": "United Nations Policy Portal", "url": "https://policy.un.org/en/security/about-legal-and-policy-framework/united-nations-security-management-system"},
        {"title": "Security of UN Premises", "publisher": "United Nations Policy Portal", "url": "https://policy.un.org/en/security/specific-security-considerations/security-un-premises"},
        {"title": "Security Clearance", "publisher": "United Nations Policy Portal", "url": "https://policy.un.org/en/security/operational-guidance/security-clearance"},
        {"title": "United Nations crisis management support and duty station teams", "publisher": "United Nations General Assembly", "url": "https://docs.un.org/en/A/79/692"},
        {"title": "Safety and security in the organizations of the United Nations system", "publisher": "United Nations Joint Inspection Unit", "url": "https://docs.un.org/en/JIU/REP/2016/9"},
        {"title": "Operations", "publisher": "World Health Organization", "url": "https://www.who.int/emergencies/operations"},
        {"title": "Operations Support and Logistics (OSL)", "publisher": "World Health Organization South-East Asia", "url": "https://www.who.int/southeastasia/outbreaks-and-emergencies/Response-coordination/osl"}
    ]
}
,
"archive/689-shared-regime-territorial-presence-constitutions-headquarters-regional-offices-country-offices-liaison-posts-service-hubs-host-instruments-review-clocks-and-no-regime-by-landlord-permission.md": {
    "groups": [
        {"title": "WHO Organizational structure", "publisher": "World Health Organization", "url": "https://www.who.int/about/structure"},
        {"title": "WHO country offices", "publisher": "World Health Organization", "url": "https://www.who.int/countries/country-presence/reports/2025/country-offices"},
        {"title": "Core capacities of WHO country and regional offices strengthened to drive measurable impact at country level", "publisher": "World Health Organization", "url": "https://www.who.int/about/accountability/results/who-results-report-2020-mtr/output/pb-2026-2027/8.1.2-core-capacities-of-who-country-and-regional-offices-strengthened-to-drive-measurable-impact-at-country-level"},
        {"title": "Report of the Chair of the UNSDG on development coordination office activities", "publisher": "United Nations Economic and Social Council", "url": "https://docs.un.org/en/E/2025/61?direct=true"},
        {"title": "Convention on the Privileges and Immunities of the United Nations", "publisher": "United Nations", "url": "https://legal.un.org/avl/ha/cpiun-cpisa/cpiun-cpisa.html"},
        {"title": "Where can I find information about the UN-US Headquarters Agreement?", "publisher": "Ask DAG! / United Nations", "url": "https://ask.un.org/faq/268923"}
    ]
}
,
"archive/688-shared-regime-private-law-claims-constitutions-contracts-torts-procurement-disputes-standing-claims-bodies-arbitration-insurance-and-no-immunity-without-remedy.md": {
    "groups": [
        {"title": "Convention on the Privileges and Immunities of the United Nations", "publisher": "United Nations", "url": "https://legal.un.org/avl/ha/cpiun-cpisa/cpiun-cpisa.html"},
        {"title": "Privileges and immunities of the United Nations", "publisher": "United Nations General Assembly", "url": "https://docs.un.org/en/A/RES/22%28I%29"},
        {"title": "Procedures in place for implementation of article VIII, section 29, of the Convention on the Privileges and Immunities of the United Nations", "publisher": "United Nations", "url": "https://docs.un.org/en/A/C.5/49/65"},
        {"title": "General Conditions of Contract for Goods and Services", "publisher": "United Nations", "url": "https://www.un.org/procurement/sites/default/files/2025/August%202025/general-conditions-contracts-goods-and-services-accessible-english.pdf"},
        {"title": "UNCITRAL Arbitration Rules", "publisher": "UNCITRAL", "url": "https://uncitral.un.org/en/texts/arbitration/contractualtexts/arbitration"},
        {"title": "PCA Arbitration Rules", "publisher": "Permanent Court of Arbitration", "url": "https://pca-cpa.org/en/services/arbitration-services/pca-arbitration-rules/"},
        {"title": "Settlement of disputes to which international organizations are parties", "publisher": "United Nations International Law Commission", "url": "https://legal.un.org/ilc/reports/2024/english/chp4.pdf"}
    ]
}
,
"archive/687-shared-regime-privileges-and-immunities-constitutions-functional-independence-jurisdiction-tax-customs-inviolability-waiver-and-no-sovereignty-cosplay.md": {
    "groups": [
        {"title": "Convention on the Privileges and Immunities of the United Nations", "publisher": "United Nations", "url": "https://legal.un.org/avl/ha/cpiun-cpisa/cpiun-cpisa.html"},
        {"title": "Chapter III: Privileges and Immunities, Diplomatic and Consular Relations, etc.", "publisher": "United Nations Treaty Collection", "url": "https://treaties.un.org/pages/CTCTreaties.aspx?clang=_en&id=3&subid=A"},
        {"title": "Basic Documents", "publisher": "World Health Organization", "url": "https://apps.who.int/gb/bd/pdf_files/Bd_49th-en.pdf"},
        {"title": "Where can I find information about the UN-US Headquarters Agreement?", "publisher": "Ask DAG! / United Nations", "url": "https://ask.un.org/faq/268923"},
        {"title": "Canadian Visa and Entry Information", "publisher": "International Civil Aviation Organization", "url": "https://www.icao.int/canadian-visa-and-entry-information"},
        {"title": "Vienna Convention on the Representation of States in their Relations with International Organizations of a Universal Character", "publisher": "United Nations", "url": "https://legal.un.org/ilc/texts/instruments/english/conventions/5_1_1975.pdf"}
    ]
}
,

"archive/686-shared-regime-administrative-justice-constitutions-ethics-ombuds-investigations-management-evaluation-tribunals-and-no-secretariat-by-untestable-discipline.md": {
    "groups": [
        {"title": "United Nations Internal Justice System", "publisher": "United Nations", "url": "https://www.un.org/en/internaljustice/"},
        {"title": "Management Evaluation", "publisher": "United Nations", "url": "https://www.un.org/en/internaljustice/undt/the-management-evaluation.shtml"},
        {"title": "UN Dispute Tribunal Time Limits", "publisher": "United Nations", "url": "https://www.un.org/en/internaljustice/undt/time-limits.shtml"},
        {"title": "Statute of the United Nations Appeals Tribunal", "publisher": "United Nations", "url": "https://www.un.org/en/internaljustice/unat/unat-statute.shtml"},
        {"title": "Protection against retaliation", "publisher": "United Nations Ethics Office", "url": "https://www.un.org/en/ethics/protection-against-retaliation/index.shtml"},
        {"title": "How we investigate", "publisher": "Office of Internal Oversight Services", "url": "https://oios.un.org/how-we-investigate"},
        {"title": "Statute of the Administrative Tribunal of the International Labour Organization", "publisher": "International Labour Organization", "url": "https://www.ilo.org/resource/statute-administrative-tribunal-international-labour-organization"}
    ]
}
,
"archive/685-shared-regime-procurement-constitutions-competition-thresholds-exceptions-award-records-protest-debarment-and-no-regime-by-sole-source-habit.md": {
    "groups": [
        {"title": "United Nations Procurement Manual", "publisher": "United Nations", "url": "https://www.un.org/procurement/sites/default/files/2025/June%202025/procurement-manual-english.pdf"},
        {"title": "Policies and Regulations", "publisher": "UN Procurement", "url": "https://www.un.org/procurement/about-us/policies-and-regulations"},
        {"title": "UN Supplier Code of Conduct", "publisher": "United Nations", "url": "https://www.un.org/procurement/sites/default/files/2025/June%202025/code-conduct-english.pdf"},
        {"title": "WHO Procurement: become a supplier", "publisher": "World Health Organization", "url": "https://www.who.int/about/accountability/procurement/become-a-supplier"},
        {"title": "WHO solicitation material showing debriefing and procurement complaint mechanism", "publisher": "World Health Organization", "url": "https://cdn.who.int/media/docs/default-source/wpro---documents/countries/china/joint-research-and-dah-capacity-development-in-lmics.pdf"}
    ]
}
,

"archive/684-shared-regime-secretariat-workforce-constitutions-appointments-merit-geographic-balance-secondments-conduct-separation-and-no-regime-by-patronage.md": {
    "groups": [
        {"title": "Chapter XV: The Secretariat (Articles 97-101)", "publisher": "United Nations", "url": "https://www.un.org/en/about-us/un-charter/chapter-15"},
        {"title": "Article 101 — Charter of the United Nations — Repertory", "publisher": "United Nations Codification Division", "url": "https://legal.un.org/repertory/art101.shtml"},
        {"title": "WHO Staff Regulations and Staff Rules", "publisher": "World Health Organization", "url": "https://cdn.who.int/media/docs/default-source/human-resources/staff-regulations-and-staff-rules.pdf?download=true&sfvrsn=358ad6b1_22"},
        {"title": "Standards of Conduct for the International Civil Service", "publisher": "International Civil Service Commission", "url": "https://icsc.un.org/Resources/General/Publications/standardse.pdf"},
        {"title": "The election of WHO Director-General", "publisher": "World Health Organization", "url": "https://www.who.int/about/governance/election"},
        {"title": "WTO | Director-General: Selection Process", "publisher": "World Trade Organization", "url": "https://www.wto.org/english/thewto_e/dg_e/dg_selection_process_e.htm"}
    ]
}
,
"archive/683-shared-regime-budget-constitutions-assessed-and-voluntary-funds-appropriations-working-capital-arrears-audit-and-no-governance-by-donor-patchwork.md": {
    "groups": [
        {"title": "United Nations Financial Regulations and Rules of the United Nations", "publisher": "United Nations", "url": "https://docs.un.org/en/st/sgb/2003/7"},
        {"title": "Amendments to the Financial Regulations and Financial Rules", "publisher": "World Health Organization", "url": "https://apps.who.int/gb/ebwha/pdf_files/EB152/B152_30-en.pdf"},
        {"title": "Agreement Establishing the WTO", "publisher": "World Trade Organization", "url": "https://www.wto.org/english/res_e/booksp_e/agrmntseries1_wto_e.pdf"},
        {"title": "Office of Internal Oversight Services", "publisher": "United Nations", "url": "https://oios.un.org/"},
        {"title": "United Nations Board of Auditors", "publisher": "United Nations", "url": "https://www.un.org/en/auditors/board/"}
    ]
}
,

"archive/682-shared-regime-language-and-text-discipline-official-working-languages-translation-interpretation-authentic-texts-terminology-control-and-no-law-by-convenience-copy.md": {
    "groups": [
        {"title": "Official Languages", "publisher": "United Nations", "url": "https://www.un.org/en/our-work/official-languages"},
        {"title": "Multilingualism | Secretary-General", "publisher": "United Nations", "url": "https://www.un.org/sg/en/multilingualism/index.shtml"},
        {"title": "Rules of Procedure of the World Health Assembly", "publisher": "World Health Organization", "url": "https://apps.who.int/gb/edg/pdf_files/Ref-docs/rules-of-procedure-en.pdf"},
        {"title": "WHO Basic Documents", "publisher": "World Health Organization", "url": "https://apps.who.int/gb/bd/pdf_files/Bd_49th-en.pdf"},
        {"title": "WTO | Who we are", "publisher": "World Trade Organization", "url": "https://www.wto.org/english/thewto_e/whatis_e/who_we_are_e.htm"},
        {"title": "WTO public corpus", "publisher": "World Trade Organization", "url": "https://www.wto.org/english/res_e/corpus_e/corpus_e.htm"}
    ]
}
,
"archive/681-shared-regime-session-constitutions-regular-special-emergency-extraordinary-virtual-hybrid-adjournment-recess-and-no-government-by-permanent-session.md": {
    "groups": [
        {"title": "Chapter IV: The General Assembly (Articles 9-22)", "publisher": "United Nations", "url": "https://www.un.org/en/about-us/un-charter/chapter-4"},
        {"title": "UN General Assembly — Rules of Procedure — Sessions", "publisher": "United Nations General Assembly", "url": "https://www.un.org/en/ga/about/ropga/ropga_sessions.shtml"},
        {"title": "Emergency Special Sessions", "publisher": "United Nations General Assembly", "url": "https://www.un.org/en/ga/sessions/emergency.shtml"},
        {"title": "WTO | legal texts — Marrakesh Agreement", "publisher": "World Trade Organization", "url": "https://www.wto.org/english/docs_e/legal_e/04-wto_e.htm"},
        {"title": "WTO Ministerial Conference background", "publisher": "World Trade Organization", "url": "https://www.wto.org/english/thewto_e/minist_e/min99_e/english/about_e/03bgd_e.htm"},
        {"title": "Special procedures to regulate the conduct of hybrid meetings of the Second special session of the World Health Assembly", "publisher": "World Health Organization", "url": "https://apps.who.int/gb/ebwha/pdf_files/WHASSA2/SSA2_2-en.pdf"},
        {"title": "Special procedures", "publisher": "World Health Organization", "url": "https://apps.who.int/gb/ebwha/pdf_files/WHA74/A74%285%29-en.pdf"}
    ]
}
,
"archive/680-shared-regime-jurisprudence-memory-and-consistency-holdings-digests-departure-reasons-advisory-opinions-and-no-random-walk-governance.md": {
    "groups": [
        {"title": "Statute of the International Court of Justice", "publisher": "International Court of Justice", "url": "https://www.icj-cij.org/statute"},
        {"title": "Summary of the Advisory Opinion of 19 July 2024", "publisher": "International Court of Justice", "url": "https://www.icj-cij.org/node/204176"},
        {"title": "ECHR Knowledge Sharing Platform (ECHR-KS)", "publisher": "European Court of Human Rights", "url": "https://ks.echr.coe.int/web/echr-ks"},
        {"title": "All Case-Law Guides", "publisher": "European Court of Human Rights", "url": "https://ks.echr.coe.int/web/echr-ks/all-case-law-guides"},
        {"title": "Dispute settlement gateway", "publisher": "World Trade Organization", "url": "https://www.wto.org/english/tratop_e/dispu_e/dispu_e.htm"},
        {"title": "Appellate Body Repertory of Reports and Awards 1995-2013", "publisher": "World Trade Organization", "url": "https://www.wto.org/english/tratop_e/dispu_e/repertory_e/repertory_e.htm"}
    ]
}
,
"archive/679-shared-regime-interpretation-constitutions-authentic-texts-ordinary-meaning-context-object-purpose-authoritative-interpretations-guidance-and-no-binding-law-by-helpdesk.md": {
    "groups": [
        {"title": "Vienna Convention on the Law of Treaties (1969)", "publisher": "United Nations", "url": "https://legal.un.org/ilc/texts/instruments/english/conventions/1_1_1969.pdf"},
        {"title": "The United Nations Treaty Handbook", "publisher": "United Nations Treaty Collection", "url": "https://treaties.un.org/pages/Resource.aspx?path=Publication%2FTH%2FPage1_en.xml"},
        {"title": "Agreement Establishing the WTO", "publisher": "World Trade Organization", "url": "https://www.wto.org/english/docs_e/legal_e/04-wto_e.htm"},
        {"title": "WTO Analytical Index — WTO Agreement Article IX", "publisher": "World Trade Organization", "url": "https://www.wto.org/english/res_e/publications_e/ai17_e/wto_agree_art9_jur.pdf"},
        {"title": "Dispute Settlement Understanding", "publisher": "World Trade Organization", "url": "https://www.wto.org/english/tratop_e/dispu_e/dsu_e.htm"},
        {"title": "Appellate Body Repertory — WTO Agreement Article IX", "publisher": "World Trade Organization", "url": "https://www.wto.org/english/tratop_e/dispu_e/repertory_e/w4_e.htm"}
    ]
}
,
"archive/678-shared-regime-independence-and-conflict-discipline-declarations-recusal-confidentiality-secondments-donor-firebreaks-and-no-expertise-by-capture.md": {
    "groups": [
        {
            "title": "Declaration of interests",
            "publisher": "World Health Organization",
            "url": "https://www.who.int/about/ethics/declaration-of-interests",
        },
        {
            "title": "Regulations for Expert Advisory Panels and Committees",
            "publisher": "World Health Organization",
            "url": "https://apps.who.int/gb/bd/pdf/bd47/en/regu-for-expert-en.pdf",
        },
        {
            "title": "Framework of Engagement with Non-State Actors (FENSA)",
            "publisher": "World Health Organization",
            "url": "https://apps.who.int/gb/bd/PDF/Framework_Engagement_non-State_Actors.pdf",
        },
        {
            "title": "WHO’s engagement with non-State actors",
            "publisher": "World Health Organization",
            "url": "https://www.who.int/about/collaboration/non-state-actors",
        },
        {
            "title": "IPCC Conflict of Interest Policy",
            "publisher": "Intergovernmental Panel on Climate Change",
            "url": "https://www.ipcc.ch/site/assets/uploads/2018/09/ipcc-conflict-of-interest-2016.pdf",
        },
        {
            "title": "Code of Practice and Procedures for handling of conflicts of interest in BTR reviews",
            "publisher": "United Nations Framework Convention on Climate Change",
            "url": "https://unfccc.int/sites/default/files/resource/Code%20of%20Practice%20and%20Procedures%20for%20handling%20of%20conf%20info%20in%20BTR%20reviews_v1.1.pdf",
        }
    ]
}
,
"archive/677-shared-regime-external-participation-constitutions-accreditation-observer-categories-submissions-hearings-transparency-registers-and-no-public-power-by-lanyard.md": {
    "groups": [
        {
            "title": "Non-State actors in official relations with WHO",
            "publisher": "World Health Organization",
            "url": "https://www.who.int/about/collaboration/non-state-actors/non-state-actors-in-official-relations-with-who",
        },
        {
            "title": "WHO Register of non-State actors",
            "publisher": "World Health Organization",
            "url": "https://www.who.int/about/collaboration/non-state-actors/who-register-of-non-state-actors",
        },
        {
            "title": "How to obtain observer status",
            "publisher": "United Nations Framework Convention on Climate Change",
            "url": "https://unfccc.int/process-and-meetings/parties-non-party-stakeholders/non-party-stakeholders/overview/how-to-obtain-observer-status",
        },
        {
            "title": "Statistics on participation and in-session engagement",
            "publisher": "United Nations Framework Convention on Climate Change",
            "url": "https://unfccc.int/process-and-meetings/parties-non-party-stakeholders/non-party-stakeholders/statistics-on-non-party-stakeholders/statistics-on-participation-and-in-session-engagement",
        },
        {
            "title": "Observers",
            "publisher": "WHO Framework Convention on Tobacco Control",
            "url": "https://fctc.who.int/convention/conference-of-the-parties/observers",
        },
        {
            "title": "Guidelines for arrangements on relations with non-governmental organizations",
            "publisher": "World Trade Organization",
            "url": "https://www.wto.org/english/forums_e/ngo_e/guide_e.htm",
        }
    ]
}
,
"archive/676-shared-regime-subsidiary-body-constitutions-committees-working-groups-expert-panels-terms-of-reference-report-back-sunset-and-no-shadow-regime-by-working-party.md": {
    "groups": [
        {
            "title": "Chapter IV: The General Assembly (Articles 9-22)",
            "publisher": "United Nations",
            "url": "https://www.un.org/en/about-us/un-charter/chapter-4",
        },
        {
            "title": "Subsidiary organs of the General Assembly",
            "publisher": "United Nations General Assembly",
            "url": "https://www.un.org/en/ga/about/subsidiary/index.shtml",
        },
        {
            "title": "Rules of Procedure of the Executive Board",
            "publisher": "World Health Organization",
            "url": "https://apps.who.int/gb/edg/pdf_files/Ref-docs/new-rules-of-procedure-of-the-eb-en.pdf",
        },
        {
            "title": "Regulations for Expert Advisory Panels and Committees",
            "publisher": "World Health Organization",
            "url": "https://apps.who.int/gb/bd/pdf/bd47/en/regu-for-expert-en.pdf",
        },
        {
            "title": "Agreement Establishing the WTO",
            "publisher": "World Trade Organization",
            "url": "https://www.wto.org/english/res_e/booksp_e/agrmntseries1_wto_e.pdf",
        },
        {
            "title": "Agreement on Technical Barriers to Trade",
            "publisher": "World Trade Organization",
            "url": "https://www.wto.org/english/docs_e/legal_e/17-tbt_e.htm",
        }
    ]
}
,
"archive/675-shared-regime-initiative-and-text-sponsorship-ladders-agenda-items-proposals-amendments-cosponsorship-withdrawal-financial-screening-and-no-law-by-ghost-draft.md": {
    "groups": [
        {
            "title": "Rules of Procedure of the General Assembly",
            "publisher": "United Nations General Assembly",
            "url": "https://docs.un.org/en/A/520/rev.19",
        },
        {
            "title": "Guidelines for the preparation, co-sponsorship and timely submission of proposals",
            "publisher": "United Nations General Assembly",
            "url": "https://www.un.org/en/ga/pdf/guidelines_preparation_co-sponsorship_proposals_submission_GA78.pdf",
        },
        {
            "title": "Rules of Procedure of the Executive Board",
            "publisher": "World Health Organization",
            "url": "https://apps.who.int/gb/edg/pdf_files/Ref-docs/new-rules-of-procedure-of-the-eb-en.pdf",
        },
        {
            "title": "EB152 documentation portal",
            "publisher": "World Health Organization",
            "url": "https://apps.who.int/gb/e/e_eb152.html",
        },
        {
            "title": "Agreement Establishing the WTO",
            "publisher": "World Trade Organization",
            "url": "https://www.wto.org/english/res_e/booksp_e/agrmntseries1_wto_e.pdf",
        }
    ]
}
,


"archive/674-shared-regime-records-and-publicity-public-private-sessions-document-registers-meeting-records-vote-records-authentic-texts-corrections-and-no-governance-by-missing-papertrail.md": {
    "groups": [
        {
            "title": "UN General Assembly - Rules of Procedure - Meetings",
            "publisher": "United Nations General Assembly",
            "url": "https://www.un.org/en/ga/about/ropga/meetings.shtml",
        },
        {
            "title": "Rules of Procedure of the World Health Assembly",
            "publisher": "World Health Organization",
            "url": "https://apps.who.int/gb/edg/pdf_files/Ref-docs/rules-of-procedure-en.pdf",
        },
        {
            "title": "Modalities and methods of work of the Executive Board and the Health Assembly",
            "publisher": "World Health Organization",
            "url": "https://apps.who.int/gb/gr/pdf_files/consultation-doc-on-rules-of-procedure.pdf",
        },
        {
            "title": "Official documents and legal texts",
            "publisher": "World Trade Organization",
            "url": "https://www.wto.org/english/docs_e/docs_e.htm",
        },
        {
            "title": "UN Glossary of terms relating to Treaty actions",
            "publisher": "United Nations Treaty Collection",
            "url": "https://treaties.un.org/pages/overview.aspx?path=overview%2Fglossary%2Fpage1_en.xml",
        },
        {
            "title": "Secretariat - Official Document System",
            "publisher": "United Nations",
            "url": "https://documents.un.org/doc/undoc/gen/n24/279/64/pdf/n2427964.pdf",
        }
    ]
}
,
"archive/673-shared-regime-officer-and-secretariat-powers-chairs-bureaus-procedural-control-neutral-support-legal-advice-and-no-government-by-convening-clique.md": {
    "groups": [
        {
            "title": "UN General Assembly - Rules of Procedure - President",
            "publisher": "United Nations General Assembly",
            "url": "https://www.un.org/en/ga/about/ropga/prez.shtml",
        },
        {
            "title": "UN General Assembly - Rules of Procedure - Secretariat",
            "publisher": "United Nations General Assembly",
            "url": "https://www.un.org/en/ga/about/ropga/secretariat.shtml",
        },
        {
            "title": "Rules of Procedure of the World Health Assembly",
            "publisher": "World Health Organization",
            "url": "https://apps.who.int/gb/edg/pdf_files/Ref-docs/rules-of-procedure-en.pdf",
        },
        {
            "title": "Overview of Governing Bodies The roles of the Officers",
            "publisher": "World Health Organization",
            "url": "https://apps.who.int/gb/gov/assets/overview-of-governing-bodies.pdf",
        },
        {
            "title": "Draft terms of reference to strengthen the effectiveness of the Officers of the Executive Board",
            "publisher": "World Health Organization",
            "url": "https://apps.who.int/gb/ebwha/pdf_files/EB156/B156_%283%29-en.pdf",
        }
    ]
}
,
"archive/672-shared-regime-decision-rules-agenda-gates-quorum-consensus-simple-majority-qualified-majority-double-majority-veto-limits-and-no-governance-by-fake-unanimity.md": {
    "groups": [
        {
            "title": "Chapter IV: The General Assembly (Articles 9-22)",
            "publisher": "United Nations",
            "url": "https://www.un.org/en/about-us/un-charter/chapter-4",
        },
        {
            "title": "Credentials, Rules of Procedure | UN General Assembly",
            "publisher": "United Nations General Assembly",
            "url": "https://www.un.org/en/ga/about/ropga/credentials.shtml",
        },
        {
            "title": "Rules of Procedure of the World Health Assembly",
            "publisher": "World Health Organization",
            "url": "https://apps.who.int/gb/edg/pdf_files/Ref-docs/rules-of-procedure-en.pdf",
        },
        {
            "title": "Agreement Establishing the WTO",
            "publisher": "World Trade Organization",
            "url": "https://www.wto.org/english/res_e/booksp_e/agrmntseries1_wto_e.pdf",
        },
        {
            "title": "Rules of Procedure of the Conference of the Parties to the WHO Framework Convention on Tobacco Control",
            "publisher": "WHO FCTC",
            "url": "https://fctc.who.int/docs/librariesprovider12/default-document-library/rules-of-procedure-cop.pdf?download=true&sfvrsn=8fe42de6_7",
        },
        {
            "title": "Qualified majority",
            "publisher": "Council of the European Union",
            "url": "https://www.consilium.europa.eu/en/council-eu/how-does-the-council-vote/qualified-majority/",
        }
    ]
}
,
"archive/671-shared-regime-representation-ladders-credentials-chief-delegates-alternates-observers-speaking-rights-committee-access-and-no-state-voice-by-self-appointment.md": {
    "groups": [
        {
            "title": "Credentials Committee",
            "publisher": "United Nations General Assembly",
            "url": "https://www.un.org/en/ga/credentials/credentials.shtml",
        },
        {
            "title": "Rules of Procedure of the World Health Assembly",
            "publisher": "World Health Organization",
            "url": "https://apps.who.int/gb/edg/pdf_files/Ref-docs/rules-of-procedure-en.pdf",
        },
        {
            "title": "Rules of Procedure of the Conference of the Parties to the WHO Framework Convention on Tobacco Control",
            "publisher": "WHO FCTC",
            "url": "https://fctc.who.int/docs/librariesprovider12/default-document-library/rules-of-procedure-cop.pdf?download=true&sfvrsn=8fe42de6_7",
        },
        {
            "title": "Convention on the Privileges and Immunities of the United Nations",
            "publisher": "United Nations",
            "url": "https://treaties.un.org/doc/treaties/1946/12/19461214%2010-17%20pm/ch_iii_1p.pdf",
        },
        {
            "title": "Agreement Establishing the WTO",
            "publisher": "World Trade Organization",
            "url": "https://www.wto.org/english/res_e/booksp_e/agrmntseries1_wto_e.pdf",
        }
    ]
}
,

"archive/670-shared-regime-exit-ladders-denunciation-withdrawal-suspension-expulsion-savings-clauses-wind-down-duties-and-no-perpetual-membership-fiction.md": {
    "groups": [
        {
            "title": "UN Glossary of terms relating to Treaty actions",
            "publisher": "United Nations Treaty Collection",
            "url": "https://treaties.un.org/pages/overview.aspx?path=overview%2Fglossary%2Fpage1_en.xml",
        },
        {
            "title": "Treaty Handbook",
            "publisher": "United Nations Treaty Collection",
            "url": "https://treaties.un.org/doc/source/publications/thb/english.pdf",
        },
        {
            "title": "Chapter II: Membership (Articles 3-6)",
            "publisher": "United Nations",
            "url": "https://www.un.org/en/about-us/un-charter/chapter-2",
        },
        {
            "title": "WTO | legal texts - Marrakesh Agreement",
            "publisher": "World Trade Organization",
            "url": "https://www.wto.org/english/docs_e/legal_e/04-wto_e.htm",
        },
        {
            "title": "European Convention on Human Rights",
            "publisher": "European Court of Human Rights",
            "url": "https://www.echr.coe.int/documents/d/echr/convention_ENG",
        }
    ]
}
,
"archive/669-shared-regime-entry-ladders-observers-signatories-provisional-application-accession-admission-thresholds-depositaries-entry-into-force-and-no-membership-by-affiliation-claim.md": {
    "groups": [
        {
            "title": "UN Glossary of terms relating to Treaty actions",
            "publisher": "United Nations Treaty Collection",
            "url": "https://treaties.un.org/pages/overview.aspx?path=overview%2Fglossary%2Fpage1_en.xml",
        },
        {
            "title": "Frequently Asked Questions",
            "publisher": "United Nations Treaty Collection",
            "url": "https://treaties.un.org/Pages/Overview.aspx?path=overview%2Ffaq%2Fpage1_en.xml",
        },
        {
            "title": "Non-Member Observer State Resources",
            "publisher": "United Nations Library",
            "url": "https://research.un.org/en/unmembers/observers",
        },
        {
            "title": "How to become a member of the WTO",
            "publisher": "World Trade Organization",
            "url": "https://www.wto.org/english/thewto_e/acc_e/acces_e.htm",
        },
        {
            "title": "The accession process - the procedures and how they are established",
            "publisher": "World Trade Organization",
            "url": "https://www.wto.org/english/thewto_e/acc_e/cbt_course_e/c4s2p1_e.htm",
        }
    ]
}
,
"archive/666-compliance-ladders-for-shared-regimes-reporting-peer-review-inspection-dispute-settlement-remediation-suspension-and-no-treaty-by-voluntary-vibes.md": {
    "groups": [
        {
            "title": "International health regulations",
            "publisher": "World Health Organization",
            "url": "https://www.who.int/health-topics/international-health-regulations",
        },
        {
            "title": "Preparing for the Enhanced Transparency Framework",
            "publisher": "UN Climate Change",
            "url": "https://unfccc.int/process-and-meetings/transparency-and-reporting/preparing-for-the-ETF",
        },
        {
            "title": "FAQ - Implementing the Enhanced Transparency Framework",
            "publisher": "UN Climate Change",
            "url": "https://unfccc.int/FAQ-moving-towards-the-ETF",
        },
        {
            "title": "Safeguards and verification",
            "publisher": "International Atomic Energy Agency",
            "url": "https://www.iaea.org/topics/safeguards-and-verification",
        },
        {
            "title": "Dispute settlement gateway",
            "publisher": "World Trade Organization",
            "url": "https://www.wto.org/english/tratop_e/dispu_e/dispu_e.htm",
        },
        {
            "title": "Exchange of information on request: A robust and transparent review process",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/networks/global-forum-tax-transparency/resources/exchange-of-information-on-request-peer-review-process.html",
        },
        {
            "title": "Ratings on exchange of information on request",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/networks/global-forum-tax-transparency/resources/exchange-of-information-on-request-ratings.html",
        },
        {
            "title": "Universal Safety Oversight Audit Programme (USOAP)",
            "publisher": "International Civil Aviation Organization",
            "url": "https://www.icao.int/usoapcma",
        }
    ]
}
,
"archive/668-shared-regime-change-ladders-review-conferences-amendments-protocols-annex-updates-tacit-acceptance-version-registers-and-no-regime-rewrite-by-secretariat-faq.md": {
    "groups": [
        {
            "title": "Treaty Handbook",
            "publisher": "United Nations Treaty Collection",
            "url": "https://treaties.un.org/doc/source/publications/thb/english.pdf",
        },
        {
            "title": "The Montreal Protocol on Substances that Deplete the Ozone Layer",
            "publisher": "Ozone Secretariat / UNEP",
            "url": "https://ozone.unep.org/treaties/montreal-protocol",
        },
        {
            "title": "Decision III/1: Adjustments and amendment",
            "publisher": "Ozone Secretariat / UNEP",
            "url": "https://ozone.unep.org/treaties/montreal-protocol/meetings/third-meeting-parties/decisions/decision-iii1-adjustments-and-amendment",
        },
        {
            "title": "International Convention on Standards of Training, Certification and Watchkeeping for Seafarers (STCW)",
            "publisher": "International Maritime Organization",
            "url": "https://www.imo.org/en/About/Conventions/Pages/International-Convention-on-Standards-of-Training%2C-Certification-and-Watchkeeping-for-Seafarers-%28STCW%29.aspx",
        },
        {
            "title": "Standards and Recommended Practices (SARPs)",
            "publisher": "International Civil Aviation Organization",
            "url": "https://www.icao.int/safety-management/standards-and-recommended-practices-sarps",
        },
        {
            "title": "Q&A: International Health Regulations: amendments",
            "publisher": "World Health Organization",
            "url": "https://www.who.int/news-room/questions-and-answers/item/international-health-regulations-amendments",
        },
        {
            "title": "AGREEMENT ESTABLISHING THE WTO",
            "publisher": "World Trade Organization",
            "url": "https://www.wto.org/english/res_e/booksp_e/agrmntseries1_wto_e.pdf",
        }
    ]
}
,
"archive/667-differentiated-commitments-in-shared-regimes-reservations-opt-outs-derogations-transition-periods-territorial-application-review-clocks-and-no-uniformity-by-false-claim.md": {
    "groups": [
        {
            "title": "UN Glossary of terms relating to Treaty actions",
            "publisher": "United Nations Treaty Collection",
            "url": "https://treaties.un.org/pages/overview.aspx?path=overview%2Fglossary%2Fpage1_en.xml",
        },
        {
            "title": "Vienna Convention on the Law of Treaties (1969)",
            "publisher": "United Nations",
            "url": "https://legal.un.org/ilc/texts/instruments/english/conventions/1_1_1969.pdf",
        },
        {
            "title": "Depositary Notifications (CNs) by the Secretary-General",
            "publisher": "United Nations Treaty Collection",
            "url": "https://treaties.un.org/Pages/Content.aspx?path=DB%2FCNs%2FpageIntro_en.xml",
        },
        {
            "title": "International Health Regulations (2005)",
            "publisher": "World Health Organization",
            "url": "https://apps.who.int/gb/bd/pdf_files/IHR_2014-2022-2024-en.pdf",
        },
        {
            "title": "Enhanced cooperation",
            "publisher": "EUR-Lex",
            "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=legissum%3Axy0015",
        }
    ]
}
,
"archive/665-external-commitment-landing-paths-signature-ratification-transposition-direct-effect-operational-owners-and-no-treaty-by-press-release.md": {
    "groups": [
        {
            "title": "UN Glossary of terms relating to Treaty actions",
            "publisher": "United Nations Treaty Collection",
            "url": "https://treaties.un.org/pages/overview.aspx?path=overview%2Fglossary%2Fpage1_en.xml",
        },
        {
            "title": "Transposition",
            "publisher": "EUR-Lex",
            "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=legissum%3Atransposition",
        },
        {
            "title": "The direct effect of European Union law",
            "publisher": "EUR-Lex",
            "url": "https://eur-lex.europa.eu/EN/legal-content/summary/the-direct-effect-of-european-union-law.html",
        },
        {
            "title": "International health regulations",
            "publisher": "World Health Organization",
            "url": "https://www.who.int/health-topics/international-health-regulations",
        },
        {
            "title": "National focal points",
            "publisher": "World Health Organization",
            "url": "https://www.who.int/teams/ihr/national-focal-points",
        },
        {
            "title": "Standards and Recommended Practices (SARPs)",
            "publisher": "International Civil Aviation Organization",
            "url": "https://www.icao.int/safety-management/standards-and-recommended-practices-sarps",
        }
    ]
}
,
"archive/664-obligation-and-funding-formulas-by-problem-class-capacity-to-pay-equalization-polluter-pays-beneficiary-pays-risk-solidarity-and-no-one-formula-federalism.md": {
    "groups": [
        {
            "title": "Assessed Contributions",
            "publisher": "United Nations",
            "url": "https://policy.un.org/en/finance-and-budget/contributions-and-other-income/assessed-contributions",
        },
        {
            "title": "Fiscal Equalisation in OECD Countries",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/fiscal-equalisation-in-oecd-countries_5k97b11n2gxx-en.html",
        },
        {
            "title": "Water",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/topics/water.html",
        },
        {
            "title": "Guiding Principles concerning International Economic Aspects of Environmental Policies",
            "publisher": "OECD Legal Instruments",
            "url": "https://legalinstruments.oecd.org/en/instruments/oecd-legal-0102",
        },
        {
            "title": "United Nations Framework Convention on Climate Change",
            "publisher": "UN Climate Change",
            "url": "https://unfccc.int/resource/ccsites/zimbab/conven/text/art03.htm",
        },
        {
            "title": "The Explainer: The Paris Agreement",
            "publisher": "UN Climate Change",
            "url": "https://unfccc.int/news/the-explainer-the-paris-agreement",
        }
    ]
}
,
"archive/663-cross-border-integration-ladders-information-sharing-minimum-standards-mutual-recognition-common-enforcement-budget-tools-and-no-union-by-slogan.md": {
    "groups": [
        {
            "title": "The principle of subsidiarity",
            "publisher": "EUR-Lex",
            "url": "https://eur-lex.europa.eu/EN/legal-content/summary/the-principle-of-subsidiarity.html",
        },
        {
            "title": "Principle of conferral",
            "publisher": "EUR-Lex",
            "url": "https://eur-lex.europa.eu/EN/legal-content/glossary/principle-of-conferral.html",
        },
        {
            "title": "International health regulations",
            "publisher": "World Health Organization",
            "url": "https://www.who.int/health-topics/international-health-regulations",
        },
        {
            "title": "Standards and Recommended Practices (SARPs)",
            "publisher": "International Civil Aviation Organization",
            "url": "https://www.icao.int/safety-management/standards-and-recommended-practices-sarps",
        },
        {
            "title": "Conventions",
            "publisher": "International Maritime Organization",
            "url": "https://www.imo.org/en/about/conventions/pages/default.aspx",
        },
        {
            "title": "Enhanced cooperation",
            "publisher": "EUR-Lex",
            "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=legissum%3Axy0015",
        }
    ]
}
,
"archive/662-global-institution-toolkit-by-problem-class-assemblies-secretariats-scientific-panels-registries-inspection-compliance-funds-and-no-world-state-monoculture.md": {
    "groups": [
        {
            "title": "United Nations Charter (full text)",
            "publisher": "United Nations",
            "url": "https://www.un.org/en/about-us/un-charter/full-text",
        },
        {
            "title": "International health regulations",
            "publisher": "World Health Organization",
            "url": "https://www.who.int/health-topics/international-health-regulations",
        },
        {
            "title": "The History of ICAO and the Chicago Convention",
            "publisher": "International Civil Aviation Organization",
            "url": "https://www.icao.int/history-icao-and-chicago-convention",
        },
        {
            "title": "Conventions",
            "publisher": "International Maritime Organization",
            "url": "https://www.imo.org/en/about/conventions/pages/default.aspx",
        },
        {
            "title": "Paris Agreement",
            "publisher": "UN Climate Change",
            "url": "https://unfccc.int/process-and-meetings/the-paris-agreement",
        },
        {
            "title": "Structure",
            "publisher": "Intergovernmental Panel on Climate Change",
            "url": "https://www.ipcc.ch/about/structure/",
        }
    ]
}
,
"archive/661-collapsed-stack-rules-for-microstates-city-states-fused-tiers-shared-capacity-and-no-full-ladder-cosplay.md": {
    "groups": [
        {
            "title": "Local Democracy",
            "publisher": "International IDEA",
            "url": "https://www.idea.int/publications/catalogue/local-democracy",
        },
        {
            "title": "Federalism",
            "publisher": "International IDEA",
            "url": "https://www.idea.int/sites/default/files/publications/federalism-primer.pdf",
        },
        {
            "title": "Improving public sector capacity-strengthening support for small island developing states",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/improving-public-sector-capacity-strengthening-support-for-small-island-developing-states_aec0effa-en.html",
        },
        {
            "title": "Small States, Smart Solutions : Improving Connectivity and Increasing the Effectiveness of Public Services",
            "publisher": "World Bank",
            "url": "https://openknowledge.worldbank.org/entities/publication/d686137c-a7ab-599e-80a8-3f8501286f91",
        },
        {
            "title": "Fiscal Challenges in Small States",
            "publisher": "World Bank",
            "url": "https://documents1.worldbank.org/curated/en/099434409172423992/pdf/IDU-b75b641e-7953-41a9-98c3-f2c39b25d6f3.pdf",
        }
    ]
}
,
"archive/660-canonical-government-matrix-by-scope-legislature-executive-civil-service-fiscal-base-review-participation-and-no-full-stack-rewrite-for-every-tier.md": {
    "groups": [
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-of-local-self-government-eng/1680a87cc3",
        },
        {
            "title": "Additional Protocol to the European Charter of Local Self-Government on the right to participate in the affairs of a local authority",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/168008482a",
        },
        {
            "title": "Recommendation CM/Rec(2023)5 on the principles of good democratic governance",
            "publisher": "Council of Europe",
            "url": "https://search.coe.int/cm/Pages/result_details.aspx?ObjectId=0900001680ac77e4",
        },
        {
            "title": "Assigning responsibilities across levels of government",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html",
        },
        {
            "title": "Approaches to Metropolitan Area Governance",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/approaches-to-metropolitan-area-governance_5jz5j1q7s128-en.html",
        },
        {
            "title": "OECD Principles on Urban Policy",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/about/programmes/oecd-programme-on-national-urban-policy/oecd-principles-on-urban-policy.html",
        },
        {
            "title": "Navigating conflict and fostering co-operation in fiscal federalism",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/navigating-conflict-and-fostering-co-operation-in-fiscal-federalism_3d5c8c20-en.html",
        },
        {
            "title": "Federalism",
            "publisher": "International IDEA",
            "url": "https://www.idea.int/sites/default/files/publications/federalism-primer.pdf",
        },
        {
            "title": "Second Chambers in Federal Systems",
            "publisher": "International IDEA",
            "url": "https://www.idea.int/publications/catalogue/second-chambers-federal-systems",
        },
        {
            "title": "UN Charter",
            "publisher": "United Nations",
            "url": "https://www.un.org/en/about-us/un-charter",
        },
        {
            "title": "International health regulations",
            "publisher": "World Health Organization",
            "url": "https://www.who.int/health-topics/international-health-regulations",
        }
    ]
}
,
"archive/659-scope-evidentiary-break-presumptions-burden-allocation-and-no-stack-change-by-missing-file.md": {
    "groups": [
        {
            "title": "The functioning of administrative judiciaries in the Western Balkans",
            "publisher": "OECD / SIGMA",
            "url": "https://one.oecd.org/document/GOV/SIGMA%282024%296/en/pdf",
        },
        {
            "title": "The Right to Open Public Administrations in Europe",
            "publisher": "OECD / SIGMA",
            "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2010/01/the-right-to-open-public-administrations-in-europe_g17a1f12/5km4g0zfqt27-en.pdf",
        },
        {
            "title": "Guidelines on electronic evidence in civil and administrative proceedings",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/guidelines-on-electronic-evidence-and-explanatory-memorandum/1680968ab5",
        },
        {
            "title": "Recommendation CM/Rec(2007)7 on good administration",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/cmrec-2007-7-of-the-cm-to-ms-on-good-administration/16809f007c",
        },
        {
            "title": "The administration and you – A handbook",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/eng-handbook-on-administration/1680a03ee2",
        }
    ]
}
,
"archive/658-scope-evidentiary-continuity-record-provenance-and-no-proof-laundering-by-migration.md": {
    "groups": [
        {
            "title": "Digital government",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/topics/digital-government.html",
        },
        {
            "title": "Data governance",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/topics/data-governance.html",
        },
        {
            "title": "The Path to Becoming a Data-Driven Public Sector",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/the-path-to-becoming-a-data-driven-public-sector_059814a7-en.html",
        },
        {
            "title": "Council of Europe Convention on Access to Official Documents (CETS No. 205)",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/168069660a",
        },
        {
            "title": "Guidelines on electronic evidence in civil and administrative proceedings",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/guidelines-on-electronic-evidence-and-explanatory-memorandum/1680968ab5",
        },
        {
            "title": "Recommendation CM/Rec(2007)7 on good administration",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/cmrec-2007-7-of-the-cm-to-ms-on-good-administration/16809f007c",
        }
    ]
}
,
"archive/657-scope-successor-accountability-legacy-acts-liabilities-records-and-no-blame-laundering-by-rescoping.md": {
    "groups": [
        {
            "title": "Assigning responsibilities across levels of government",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html",
        },
        {
            "title": "Recommendation of the Council on Regulatory Policy and Governance",
            "publisher": "OECD",
            "url": "https://legalinstruments.oecd.org/public/doc/273/273.en.pdf",
        },
        {
            "title": "Implementation of laws on general administrative procedure in the Western Balkans",
            "publisher": "OECD / SIGMA",
            "url": "https://one.oecd.org/document/GOV/SIGMA%282021%292/en/pdf",
        },
        {
            "title": "Recommendation CM/Rec(2007)7 on good administration",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/cmrec-2007-7-of-the-cm-to-ms-on-good-administration/16809f007c",
        },
        {
            "title": "The administration and you – A handbook",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/eng-handbook-on-administration/1680a03ee2",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-of-local-self-government-eng/1680a87cc3",
        }
    ]
}
,
"archive/656-scope-transition-rules-for-pending-matters-cutover-queues-file-transfer-and-no-stack-change-by-midstream-grab.md": {
    "groups": [
        {
            "title": "Recommendation of the Council on Regulatory Policy and Governance",
            "publisher": "OECD",
            "url": "https://legalinstruments.oecd.org/public/doc/273/273.en.pdf",
        },
        {
            "title": "Assigning responsibilities across levels of government",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html",
        },
        {
            "title": "Implementation of laws on general administrative procedure in the Western Balkans",
            "publisher": "OECD / SIGMA",
            "url": "https://one.oecd.org/document/GOV/SIGMA%282021%292/en/pdf",
        },
        {
            "title": "Recommendation CM/Rec(2007)7 on good administration",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/cmrec-2007-7-of-the-cm-to-ms-on-good-administration/16809f007c",
        },
        {
            "title": "The administration and you – A handbook",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/eng-handbook-on-administration/1680a03ee2",
        },
        {
            "title": "Lithuania — Opinion on draft and adopted amendments to the Law on the Lithuanian National Radio and Television",
            "publisher": "Venice Commission of the Council of Europe",
            "url": "https://www.venice.coe.int/webforms/documents/default.aspx?pdffile=CDL-AD%282026%29001-e",
        },
        {
            "title": "Poland — Joint Opinion on European standards regulating the status of judges",
            "publisher": "Venice Commission / DGI of the Council of Europe",
            "url": "https://www.venice.coe.int/webforms/documents/default.aspx?pdffile=CDL-AD%282024%29029-e",
        },
        {
            "title": "Montenegro — Urgent follow-up opinion to the opinions on the Law on the Special State Prosecutor's Office",
            "publisher": "Venice Commission of the Council of Europe",
            "url": "https://www.venice.coe.int/webforms/documents/default.aspx?pdffile=CDL-AD%282024%29014-e",
        }
    ]
}
,
"archive/655-scope-retroactivity-limits-future-only-defaults-curative-acts-and-no-stack-change-by-backdating.md": {
    "groups": [
        {
            "title": "Recommendation of the Council on Regulatory Policy and Governance",
            "publisher": "OECD",
            "url": "https://legalinstruments.oecd.org/public/doc/273/273.en.pdf",
        },
        {
            "title": "Assigning responsibilities across levels of government",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html",
        },
        {
            "title": "Rule of Law Checklist",
            "publisher": "Venice Commission of the Council of Europe",
            "url": "https://www.venice.coe.int/images/SITE%20IMAGES/Publications/Rule_of_Law_Check_List.pdf",
        },
        {
            "title": "Recommendation CM/Rec(2007)7 on good administration",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/cmrec-2007-7-of-the-cm-to-ms-on-good-administration/16809f007c",
        },
        {
            "title": "The administration and you – A handbook",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/eng-handbook-on-administration/1680a03ee2",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-of-local-self-government-eng/1680a87cc3",
        }
    ]
}
,
"archive/654-scope-promulgation-authentic-heads-effective-dates-and-no-stack-change-by-unpublished-object.md": {
    "groups": [
        {
            "title": "Recommendation of the Council on Regulatory Policy and Governance",
            "publisher": "OECD",
            "url": "https://legalinstruments.oecd.org/public/doc/273/273.en.pdf",
        },
        {
            "title": "OECD Regulatory Policy Outlook 2025",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/oecd-regulatory-policy-outlook-2025_56b60e39-en.html",
        },
        {
            "title": "Assigning responsibilities across levels of government",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html",
        },
        {
            "title": "Recommendation CM/Rec(2007)7 on good administration",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/cmrec-2007-7-of-the-cm-to-ms-on-good-administration/16809f007c",
        },
        {
            "title": "The administration and you – A handbook",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/eng-handbook-on-administration/1680a03ee2",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-of-local-self-government-eng/1680a87cc3",
        }
    ]
}
,
"archive/653-scope-source-hierarchies-authority-ladders-and-no-stack-change-by-the-loudest-surface.md": {
    "groups": [
        {
            "title": "Assigning responsibilities across levels of government",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html",
        },
        {
            "title": "Recommendation of the Council on Regulatory Policy and Governance",
            "publisher": "OECD",
            "url": "https://legalinstruments.oecd.org/public/doc/273/273.en.pdf",
        },
        {
            "title": "Rule of Law Checklist",
            "publisher": "Venice Commission of the Council of Europe",
            "url": "https://www.venice.coe.int/images/SITE%20IMAGES/Publications/Rule_of_Law_Check_List.pdf",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-of-local-self-government-eng/1680a87cc3",
        },
        {
            "title": "Publication of Judicial Decisions",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/publication-of-judicial-decisions-the-council-of-europe-s-points-for-c/1680aeb36d",
        },
        {
            "title": "Issues affecting the consistency of judicial decisions and best practices",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/issues-affecting-the-consistency-of-judicial-decisions-and-best-practi/1680afd8a5",
        }
    ]
}
,
"archive/652-scope-desuetude-limits-abandonment-fictions-and-no-stack-change-by-atrophy.md": {
    "groups": [
        {
            "title": "Assigning responsibilities across levels of government",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html",
        },
        {
            "title": "Making Decentralisation Work",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/making-decentralisation-work_g2g9faa7-en.html",
        },
        {
            "title": "Recommendation of the Council on Regulatory Policy and Governance",
            "publisher": "OECD",
            "url": "https://legalinstruments.oecd.org/public/doc/273/273.en.pdf",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-of-local-self-government-eng/1680a87cc3",
        },
        {
            "title": "Explanatory report to the European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/16800ca437",
        },
        {
            "title": "Recommendation CM/Rec(2019)3 on supervision of local authorities’ activities",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/090000168093d066",
        }
    ]
}
,
"archive/651-scope-prescription-limits-delay-bars-adverse-possession-and-no-stack-change-by-time-alone.md": {
    "groups": [
        {
            "title": "Assigning responsibilities across levels of government",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html",
        },
        {
            "title": "Recommendation of the Council on Regulatory Policy and Governance",
            "publisher": "OECD",
            "url": "https://legalinstruments.oecd.org/public/doc/273/273.en.pdf",
        },
        {
            "title": "OECD Regulatory Policy Outlook 2025",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/oecd-regulatory-policy-outlook-2025_56b60e39-en.html",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-of-local-self-government-eng/1680a87cc3",
        },
        {
            "title": "Explanatory report to the European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/16800ca437",
        },
        {
            "title": "Recommendation CM/Rec(2019)3 on supervision of local authorities’ activities",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/090000168093d066",
        }
    ]
}
,
"archive/650-scope-estoppel-limits-reliance-sunk-cost-benefit-retention-and-no-stack-change-by-dependence.md": {
    "groups": [
        {
            "title": "Assigning responsibilities across levels of government",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html",
        },
        {
            "title": "Recommendation of the Council on Regulatory Policy and Governance",
            "publisher": "OECD",
            "url": "https://legalinstruments.oecd.org/public/doc/273/273.en.pdf",
        },
        {
            "title": "OECD Regulatory Policy Outlook 2025",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/oecd-regulatory-policy-outlook-2025_56b60e39-en.html",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-of-local-self-government-eng/1680a87cc3",
        },
        {
            "title": "Explanatory report to the European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/16800ca437",
        },
        {
            "title": "Recommendation CM/Rec(2019)3 on supervision of local authorities’ activities",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/090000168093d066",
        }
    ]
}
,
"archive/649-scope-waiver-discipline-authorized-consent-and-no-stack-change-by-silence-side-letter-or-wrong-organ.md": {
    "groups": [
        {
            "title": "Assigning responsibilities across levels of government",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html",
        },
        {
            "title": "Recommendation of the Council on Regulatory Policy and Governance",
            "publisher": "OECD",
            "url": "https://legalinstruments.oecd.org/public/doc/273/273.en.pdf",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-of-local-self-government-eng/1680a87cc3",
        },
        {
            "title": "The right of local authorities to be consulted by other levels of government",
            "publisher": "Council of Europe Congress of Local and Regional Authorities",
            "url": "https://rm.coe.int/the-right-of-local-authorities-to-be-consulted-by-other-levels-of-gove/168071962f",
        },
        {
            "title": "Recommendation CM/Rec(2019)3 on supervision of local authorities’ activities",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/090000168093d066",
        }
    ]
}
,

"archive/648-scope-functional-equivalence-rules-anti-circumvention-tests-and-no-stack-change-by-relabeling.md": {
    "groups": [
        {
            "title": "Assigning responsibilities across levels of government",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html",
        },
        {
            "title": "Recommendation of the Council on Regulatory Policy and Governance",
            "publisher": "OECD",
            "url": "https://legalinstruments.oecd.org/public/doc/273/273.en.pdf",
        },
        {
            "title": "OECD Regulatory Policy Outlook 2025",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/oecd-regulatory-policy-outlook-2025_56b60e39-en.html",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-of-local-self-government-eng/1680a87cc3",
        },
        {
            "title": "Recommendation CM/Rec(2019)3 on supervision of local authorities’ activities",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/090000168093d066",
        },
        {
            "title": "The consultation of local authorities by higher levels of government",
            "publisher": "Council of Europe Congress of Local and Regional Authorities",
            "url": "https://rm.coe.int/the-consultation-of-local-authorities-by-higher-levels-of-government-g/16808ecb38",
        }
    ]
}
,
"archive/647-scope-remand-discipline-cure-instructions-bounded-reopening-and-no-stack-redesign-by-reconsideration.md": {
    "groups": [
        {
            "title": "Assigning responsibilities across levels of government",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html",
        },
        {
            "title": "Recommendation of the Council on Regulatory Policy and Governance",
            "publisher": "OECD",
            "url": "https://legalinstruments.oecd.org/public/doc/273/273.en.pdf",
        },
        {
            "title": "OECD Regulatory Policy Outlook 2025",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/oecd-regulatory-policy-outlook-2025_56b60e39-en.html",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-of-local-self-government-eng/1680a87cc3",
        },
        {
            "title": "Contemporary commentary by the Congress on the explanatory report to the European Charter of Local Self-Government",
            "publisher": "Council of Europe Congress of Local and Regional Authorities",
            "url": "https://rm.coe.int/09000016809ed6de",
        },
        {
            "title": "Recurring issues based on assessments resulting from Congress monitoring and election observation missions",
            "publisher": "Council of Europe Congress of Local and Regional Authorities",
            "url": "https://rm.coe.int/recurring-issues-based-on-assessments-resulting-from-congress-monitori/1680b1ccaf",
        }
    ]
}
,
"archive/646-scope-severability-fallback-baselines-partial-invalidity-and-no-whole-stack-collapse-by-contamination.md": {
    "groups": [
        {
            "title": "Assigning responsibilities across levels of government",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html",
        },
        {
            "title": "Recommendation of the Council on Regulatory Policy and Governance",
            "publisher": "OECD",
            "url": "https://legalinstruments.oecd.org/public/doc/273/273.en.pdf",
        },
        {
            "title": "OECD Regulatory Policy Outlook 2025",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/oecd-regulatory-policy-outlook-2025_56b60e39-en.html",
        },
        {
            "title": "OECD Economic Outlook, Volume 2025 Issue 2 — Time for a regulatory reset",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/oecd-economic-outlook-volume-2025-issue-2_9f653ca1-en/full-report/time-for-a-regulatory-reset_90ca6147.html",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-of-local-self-government-eng/1680a87cc3",
        },
        {
            "title": "Explanatory report to the European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/16800ca437",
        },
        {
            "title": "Recommendation CM/Rec(2019)3 on supervision of local authorities’ activities",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/090000168093d066",
        }
    ]
}
,
"archive/645-scope-standstill-defaults-suspensory-effect-interim-relief-and-no-stack-change-by-racing-the-clock.md": {
    "groups": [
        {
            "title": "Assigning responsibilities across levels of government",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html",
        },
        {
            "title": "Recommendation of the Council on Regulatory Policy and Governance",
            "publisher": "OECD",
            "url": "https://legalinstruments.oecd.org/public/doc/273/273.en.pdf",
        },
        {
            "title": "Regulatory Policy and Governance",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/regulatory-policy-and-governance_9789264116573-en.html",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-of-local-self-government-eng/1680a87cc3",
        },
        {
            "title": "Explanatory report to the European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/16800ca437",
        },
        {
            "title": "Recommendation CM/Rec(2019)3 on supervision of local authorities’ activities",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/090000168093d066",
        },
        {
            "title": "Contemporary commentary by the Congress on the explanatory report to the European Charter of Local Self-Government",
            "publisher": "Council of Europe Congress of Local and Regional Authorities",
            "url": "https://rm.coe.int/contemporary-commentary-by-the-congress-on-the-explanatory-report-to-t/1680a06149",
        }
    ]
}
,
"archive/644-scope-nullity-rules-void-voidable-cure-freeze-lanes-and-no-constitutional-laundering-by-fait-accompli.md": {
    "groups": [
        {
            "title": "Assigning responsibilities across levels of government",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html",
        },
        {
            "title": "Recommendation of the Council on Regulatory Policy and Governance",
            "publisher": "OECD",
            "url": "https://legalinstruments.oecd.org/public/doc/273/273.en.pdf",
        },
        {
            "title": "OECD Regulatory Policy Outlook 2025",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/oecd-regulatory-policy-outlook-2025_56b60e39-en.html",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-of-local-self-government-eng/1680a87cc3",
        },
        {
            "title": "Explanatory report to the European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/16800ca437",
        },
        {
            "title": "Recommendation CM/Rec(2019)3 on supervision of local authorities’ activities",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/090000168093d066",
        },
        {
            "title": "The consultation of local authorities by higher levels of government",
            "publisher": "Council of Europe Congress of Local and Regional Authorities",
            "url": "https://rm.coe.int/the-consultation-of-local-authorities-by-higher-levels-of-government-g/16808d3c72",
        }
    ]
}
,
"archive/643-scope-reactivation-certificates-dormancy-fresh-clearance-and-no-constitutional-necromancy.md": {
    "groups": [
        {
            "title": "Assigning responsibilities across levels of government",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html",
        },
        {
            "title": "Recommendation of the Council on Regulatory Policy and Governance",
            "publisher": "OECD",
            "url": "https://legalinstruments.oecd.org/public/doc/273/273.en.pdf",
        },
        {
            "title": "Reviewing the Stock of Regulation",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/reviewing-the-stock-of-regulation_1a8f33bc-en.html",
        },
        {
            "title": "OECD Regulatory Policy Outlook 2025",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/oecd-regulatory-policy-outlook-2025_56b60e39-en.html",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-of-local-self-government-eng/1680a87cc3",
        },
        {
            "title": "Explanatory report to the European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/16800ca437",
        },
        {
            "title": "Recommendation CM/Rec(2019)3 on supervision of local authorities’ activities",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/090000168093d066",
        },
        {
            "title": "The consultation of local authorities by higher levels of government",
            "publisher": "Council of Europe Congress of Local and Regional Authorities",
            "url": "https://rm.coe.int/the-consultation-of-local-authorities-by-higher-levels-of-government-g/16808d3c72",
        }
    ]
}
,
"archive/642-scope-retirement-certificates-repeal-cleanup-successor-crosswalks-and-no-constitutional-ghosting.md": {
    "groups": [
        {
            "title": "Assigning responsibilities across levels of government",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html",
        },
        {
            "title": "Reviewing the Stock of Regulation",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/reviewing-the-stock-of-regulation_1a8f33bc-en.html",
        },
        {
            "title": "OECD Regulatory Policy Outlook 2025",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/oecd-regulatory-policy-outlook-2025_56b60e39-en.html",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-of-local-self-government-eng/1680a87cc3",
        },
        {
            "title": "Explanatory report to the European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/16800ca437",
        },
        {
            "title": "The consultation of local authorities by higher levels of government",
            "publisher": "Council of Europe Congress of Local and Regional Authorities",
            "url": "https://rm.coe.int/the-consultation-of-local-authorities-by-higher-levels-of-government-g/16808d3c72",
        }
    ]
}
,
"archive/641-scope-settlement-certificates-provisional-to-settled-promotion-and-no-constitutional-permanence-by-elapsed-time.md": {
    "groups": [
        {
            "title": "Assigning responsibilities across levels of government",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html",
        },
        {
            "title": "OECD Regulatory Policy Outlook 2025",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/oecd-regulatory-policy-outlook-2025_56b60e39-en.html",
        },
        {
            "title": "Reviewing the Stock of Regulation",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/reviewing-the-stock-of-regulation_1a8f33bc-en.html",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-for-local-self-government-english-version-pdf-a6-59-p/16807198a3",
        },
        {
            "title": "Explanatory Report to the European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/16800ca437",
        },
        {
            "title": "Recommendation CM/Rec(2019)3 on supervision of local authorities’ activities",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/090000168093d066",
        }
    ]
}
,
"archive/640-post-launch-scope-observability-variance-ledgers-rollback-lanes-and-no-stack-change-by-runtime-custom.md": {
    "groups": [
        {
            "title": "Assigning responsibilities across levels of government",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html",
        },
        {
            "title": "OECD Regulatory Policy Outlook 2025",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/oecd-regulatory-policy-outlook-2025_56b60e39-en.html",
        },
        {
            "title": "Recommendation of the Council on Public Policy Evaluation",
            "publisher": "OECD",
            "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0478",
        },
        {
            "title": "Implementation Toolkit for the OECD Recommendation on Public Policy Evaluation",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/implementation-toolkit-for-the-oecd-recommendation-on-public-policy-evaluation_77faa4fe-en.html",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-of-local-self-government-eng/1680a87cc3",
        },
        {
            "title": "Explanatory report to the European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/16800ca437",
        },
        {
            "title": "Recommendation CM/Rec(2019)3 of the Committee of Ministers to member States on supervision of local authorities’ activities",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/090000168093d066",
        },
        {
            "title": "Regional democracy — Council of Europe Reference Framework",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/regional-democracy-reference-framework/168072febd",
        }
    ]
},

"archive/639-scope-conformance-before-go-live-implementation-attestations-readiness-gates-and-no-stack-change-by-deployment-drift.md": {
    "groups": [
        {
            "title": "Assigning responsibilities across levels of government",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html",
        },
        {
            "title": "Recommendation of the Council on Regulatory Policy and Governance",
            "publisher": "OECD",
            "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0390",
        },
        {
            "title": "Recommendation on Digital Government Strategies",
            "publisher": "OECD",
            "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0406/",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-of-local-self-government-eng/1680a87cc3",
        },
        {
            "title": "Explanatory report to the European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/16800ca437",
        },
        {
            "title": "Adequate financial resources for local authorities",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/1680718ef4",
        },
        {
            "title": "Regional democracy — Council of Europe Reference Framework",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/regional-democracy-reference-framework/168072febd",
        }
    ]
},

"archive/638-clear-statement-rules-for-scope-change-interpretive-backstops-and-no-rescoping-by-ambiguity.md": {
    "groups": [
        {
            "title": "Assigning responsibilities across levels of government",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html",
        },
        {
            "title": "Recommendation of the Council on Regulatory Policy and Governance",
            "publisher": "OECD",
            "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0390",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://www.coe.int/en/web/impact-convention-human-rights/european-charter-of-local-self-government",
        },
        {
            "title": "Explanatory report to the European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/16800ca437",
        },
        {
            "title": "Regional democracy — Council of Europe Reference Framework",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/regional-democracy-reference-framework/168072febd",
        }
    ]
},

"archive/637-scope-overrides-explicit-departure-statements-review-clocks-and-no-constitutional-clearance-by-quiet-disregard.md": {
    "groups": [
        {
            "title": "Assigning responsibilities across levels of government",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html",
        },
        {
            "title": "Recommendation of the Council on Regulatory Policy and Governance",
            "publisher": "OECD",
            "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0390",
        },
        {
            "title": "OECD Regulatory Policy Outlook 2025",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/oecd-regulatory-policy-outlook-2025_56b60e39-en.html",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://www.coe.int/en/web/impact-convention-human-rights/european-charter-of-local-self-government",
        },
        {
            "title": "The right of local authorities to be consulted by other levels of government",
            "publisher": "Council of Europe Congress of Local and Regional Authorities",
            "url": "https://rm.coe.int/the-right-of-local-authorities-to-be-consulted-by-other-levels-of-gove/168071962f",
        },
        {
            "title": "Regional democracy — Council of Europe Reference Framework",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/regional-democracy-reference-framework/168072febd",
        }
    ]
},

"archive/636-scope-opinions-clearance-lanes-signed-reasons-and-no-stack-change-by-self-certification.md": {
    "groups": [
        {
            "title": "Assigning responsibilities across levels of government",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html",
        },
        {
            "title": "Recommendation of the Council on Regulatory Policy and Governance",
            "publisher": "OECD",
            "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0390",
        },
        {
            "title": "Regulatory oversight",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/oecd-regulatory-policy-outlook-2021_38b0fdb1-en/full-report/regulatory-oversight_99cdcbab.html",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://www.coe.int/en/web/impact-convention-human-rights/european-charter-of-local-self-government",
        },
        {
            "title": "The right of local authorities to be consulted by other levels of government",
            "publisher": "Council of Europe Congress of Local and Regional Authorities",
            "url": "https://rm.coe.int/the-right-of-local-authorities-to-be-consulted-by-other-levels-of-gove/168071962f",
        },
        {
            "title": "Regional democracy — Council of Europe Reference Framework",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/regional-democracy-reference-framework/168072febd",
        }
    ]
},


"archive/635-scope-diff-packets-before-after-register-amendments-and-no-constitutional-change-by-side-effect.md": {
    "groups": [
        {
            "title": "Assigning responsibilities across levels of government",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html",
        },
        {
            "title": "Making Decentralisation Work",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/making-decentralisation-work_g2g9faa7-en.html",
        },
        {
            "title": "Multi-level Governance Reforms",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/multi-level-governance-reforms_9789264272866-en.html",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://www.coe.int/en/web/impact-convention-human-rights/european-charter-of-local-self-government",
        },
        {
            "title": "The right of local authorities to be consulted by other levels of government",
            "publisher": "Council of Europe Congress of Local and Regional Authorities",
            "url": "https://rm.coe.int/the-right-of-local-authorities-to-be-consulted-by-other-levels-of-gove/168071962f",
        },
        {
            "title": "Regional democracy — Council of Europe Reference Framework",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/regional-democracy-reference-framework/168072febd",
        }
    ]
},

"archive/634-scope-jurisprudence-digests-precedent-registers-and-no-multilevel-government-by-constitutional-amnesia.md": {
    "groups": [
        {
            "title": "Assigning responsibilities across levels of government",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html",
        },
        {
            "title": "Navigating conflict and fostering co-operation in fiscal federalism",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/navigating-conflict-and-fostering-co-operation-in-fiscal-federalism_3d5c8c20-en.html",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://www.coe.int/en/web/impact-convention-human-rights/european-charter-of-local-self-government",
        },
        {
            "title": "Explanatory report to the European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/16800ca437",
        },
        {
            "title": "Regional democracy — Council of Europe Reference Framework",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/regional-democracy-reference-framework/168072febd",
        },
        {
            "title": "Publication of judicial decisions — The Council of Europe’s points for consideration",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/publication-of-judicial-decisions-the-council-of-europe-s-points-for-c/1680aeb36d",
        }
    ]
},

"archive/633-canonical-scope-registers-responsibility-matrices-exception-ledgers-and-no-government-by-jurisdiction-folklore.md": {
    "groups": [
        {
            "title": "Assigning responsibilities across levels of government",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html",
        },
        {
            "title": "Making Decentralisation Work",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/making-decentralisation-work_g2g9faa7-en.html",
        },
        {
            "title": "OECD Recommendation on Regional Development Policy",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/about/projects/implementing-the-oecd-recommendation-on-regional-development-policy-toolkit.html",
        },
        {
            "title": "Multi-level Governance Reforms",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/multi-level-governance-reforms_9789264272866-en.html",
        },
        {
            "title": "Regional Governance in OECD Countries",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/regional-governance-in-oecd-countries_4d7c6483-en.html",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://www.coe.int/en/web/impact-convention-human-rights/european-charter-of-local-self-government",
        },
        {
            "title": "Explanatory report to the European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/16800ca437",
        },
        {
            "title": "Regional democracy — Council of Europe Reference Framework",
            "publisher": "Council of Europe",
            "url": "https://edoc.coe.int/en/local-democracy/7645-regional-democracy-council-of-europe-reference-framework.html",
        }
    ]
},


"archive/632-scope-audit-triggers-review-packets-evaluation-lanes-and-no-constitutional-sleepwalk.md": {
    "groups": [
        {
            "title": "Assigning responsibilities across levels of government",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html",
        },
        {
            "title": "Making Decentralisation Work",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/making-decentralisation-work_g2g9faa7-en.html",
        },
        {
            "title": "Multi-level Governance Reforms",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/multi-level-governance-reforms_9789264272866-en.html",
        },
        {
            "title": "Effective Public Investment Toolkit",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/about/projects/effective-public-investment-toolkit.html",
        },
        {
            "title": "Regional Governance in OECD Countries",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/regional-governance-in-oecd-countries_4d7c6483-en.html",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://www.coe.int/en/web/impact-convention-human-rights/european-charter-of-local-self-government",
        },
        {
            "title": "The right of local authorities to be consulted by other levels of government",
            "publisher": "Council of Europe Congress of Local and Regional Authorities",
            "url": "https://rm.coe.int/the-right-of-local-authorities-to-be-consulted-by-other-levels-of-gove/168071962f",
        },
        {
            "title": "Regional democracy — Council of Europe Reference Framework",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/regional-democracy-reference-framework/168072febd",
        }
    ]
},

"archive/631-reversibility-for-ideal-governments-of-each-scope-handback-clocks-fresh-proof-return-lanes-and-no-one-way-recentralization-ratchet.md": {
    "groups": [
        {
            "title": "Assigning responsibilities across levels of government",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html",
        },
        {
            "title": "Making Decentralisation Work",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/making-decentralisation-work_g2g9faa7-en.html",
        },
        {
            "title": "Multi-level Governance Reforms",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/multi-level-governance-reforms_9789264272866-en.html",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://www.coe.int/en/web/impact-convention-human-rights/european-charter-of-local-self-government",
        },
        {
            "title": "The right of local authorities to be consulted by other levels of government",
            "publisher": "Council of Europe Congress of Local and Regional Authorities",
            "url": "https://rm.coe.int/the-right-of-local-authorities-to-be-consulted-by-other-levels-of-gove/168071962f",
        },
        {
            "title": "Regional democracy — Council of Europe Reference Framework",
            "publisher": "Council of Europe",
            "url": "https://edoc.coe.int/en/local-democracy/7645-regional-democracy-council-of-europe-reference-framework.html",
        }
    ]
},

"archive/630-rescoping-authority-for-ideal-governments-of-each-scope-administration-by-law-constitutional-bargains-by-consent-and-no-jurisdictional-rewire-by-executive-deal.md": {
    "groups": [
        {
            "title": "Assigning responsibilities across levels of government",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html",
        },
        {
            "title": "Making Decentralisation Work",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/making-decentralisation-work_g2g9faa7-en.html",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://www.coe.int/en/web/impact-convention-human-rights/european-charter-of-local-self-government",
        },
        {
            "title": "Explanatory report to the European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/16800ca437",
        },
        {
            "title": "The right of local authorities to be consulted by other levels of government",
            "publisher": "Council of Europe Congress of Local and Regional Authorities",
            "url": "https://rm.coe.int/the-right-of-local-authorities-to-be-consulted-by-other-levels-of-gove/168071962f",
        },
        {
            "title": "Regional democracy — Council of Europe Reference Framework",
            "publisher": "Council of Europe",
            "url": "https://edoc.coe.int/en/local-democracy/7645-regional-democracy-council-of-europe-reference-framework.html",
        }
    ]
},


"archive/629-default-presumptions-for-ideal-governments-of-each-scope-local-first-for-ordinary-place-system-tiers-by-proof-guarantor-layers-by-duty-and-no-scope-without-burden-of-proof.md": {
    "groups": [
        {
            "title": "Assigning responsibilities across levels of government",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html",
        },
        {
            "title": "Making Decentralisation Work",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/making-decentralisation-work_g2g9faa7-en.html",
        },
        {
            "title": "Multi-level Governance Reforms",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/multi-level-governance-reforms_9789264272866-en.html",
        },
        {
            "title": "Approaches to Metropolitan Area Governance",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/approaches-to-metropolitan-area-governance_5jz5j1q7s128-en.html",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://www.coe.int/en/web/impact-convention-human-rights/european-charter-of-local-self-government",
        },
        {
            "title": "Regional democracy — Council of Europe Reference Framework",
            "publisher": "Council of Europe",
            "url": "https://edoc.coe.int/en/local-democracy/7645-regional-democracy-council-of-europe-reference-framework.html",
        },
        {
            "title": "UN Charter",
            "publisher": "United Nations",
            "url": "https://www.un.org/en/about-us/un-charter",
        },
        {
            "title": "International Health Regulations",
            "publisher": "World Health Organization",
            "url": "https://www.who.int/health-topics/international-health-regulations",
        }
    ]
},


"archive/628-honesty-tests-for-ideal-governments-of-each-scope-vocation-complete-kits-constitutional-upgrade-and-no-jurisdictional-cosplay.md": {
    "groups": [
        {
            "title": "Assigning responsibilities across levels of government",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html",
        },
        {
            "title": "Making Decentralisation Work",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/making-decentralisation-work_g2g9faa7-en.html",
        },
        {
            "title": "Multi-level Governance Reforms",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/multi-level-governance-reforms_9789264272866-en.html",
        },
        {
            "title": "Approaches to Metropolitan Area Governance",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/approaches-to-metropolitan-area-governance_5jz5j1q7s128-en.html",
        },
        {
            "title": "Governing the City",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/governing-the-city_9789264226500-en.html",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://www.coe.int/en/web/impact-convention-human-rights/european-charter-of-local-self-government",
        },
        {
            "title": "Regional democracy — Council of Europe Reference Framework",
            "publisher": "Council of Europe",
            "url": "https://edoc.coe.int/en/local-democracy/7645-regional-democracy-council-of-europe-reference-framework.html",
        },
        {
            "title": "UN Charter",
            "publisher": "United Nations",
            "url": "https://www.un.org/en/about-us/un-charter",
        },
        {
            "title": "International Health Regulations",
            "publisher": "World Health Organization",
            "url": "https://www.who.int/health-topics/international-health-regulations",
        }
    ]
},


"archive/627-constitutionalization-bundles-for-shared-territorial-power-core-upgrades-supporting-upgrades-and-no-government-by-single-home-fetish.md": {
    "groups": [
        {
            "title": "Decentralisation",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/topics/sub-issues/decentralisation.html",
        },
        {
            "title": "Making Decentralisation Work",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/2019/03/making-decentralisation-work_g1g9faa7.html",
        },
        {
            "title": "Multi-level Governance Reforms",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/multi-level-governance-reforms_9789264272866-en.html",
        },
        {
            "title": "Assigning responsibilities across levels of government",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html",
        },
        {
            "title": "Approaches to Metropolitan Area Governance",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/approaches-to-metropolitan-area-governance_5jz5j1q7s128-en.html",
        },
        {
            "title": "Governing the City",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/governing-the-city_9789264226500-en.html",
        },
        {
            "title": "Metropolitan Governance Models",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/coe-overview-of-metropolitan-governance-celgrlex-201711/1680aef607",
        },
        {
            "title": "Regional democracy — Council of Europe Reference Framework",
            "publisher": "Council of Europe",
            "url": "https://edoc.coe.int/en/local-democracy/7645-regional-democracy-council-of-europe-reference-framework.html",
        }
    ]
},


"archive/626-public-communication-homes-for-shared-territorial-power-canonical-channels-corrections-inclusive-reach-and-no-government-by-press-release-federation.md": {
    "groups": [
        {
            "title": "OECD Report on Public Communication",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/oecd-report-on-public-communication_22f8031c-en.html",
        },
        {
            "title": "Recommendation of the Council on Open Government",
            "publisher": "OECD",
            "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0438",
        },
        {
            "title": "Open Government for Stronger Democracies",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/open-government-for-stronger-democracies_5478db5b-en.html",
        },
        {
            "title": "Trust and information integrity",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/oecd-survey-on-drivers-of-trust-in-public-institutions-2024-results_9a20554b-en/full-report/trust-and-information-integrity_49ce5100.html",
        },
        {
            "title": "Access to official documents — Guide",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/access-to-official-documents-guide/168069660c",
        },
        {
            "title": "12 Principles of Good Democratic Governance",
            "publisher": "Council of Europe",
            "url": "https://www.coe.int/en/web/centre-of-expertise-for-multilevel-governance/12-principles",
        },
        {
            "title": "E-Democracy",
            "publisher": "Council of Europe Congress of Local and Regional Authorities",
            "url": "https://www.coe.int/en/web/congress/e-democracy",
        }
    ]
},


"archive/625-temporal-homes-for-shared-territorial-power-pilot-clocks-review-amendment-succession-and-no-government-by-immortal-pilot.md": {
    "groups": [
        {
            "title": "Multi-level Governance Reforms",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/multi-level-governance-reforms_9789264272866-en.html",
        },
        {
            "title": "Government at a Glance 2025 — Ex post evaluation",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/government-at-a-glance-2025_0efd0bcd-en/full-report/ex-post-evaluation_5fd27bda.html",
        },
        {
            "title": "Public policy monitoring and evaluation",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/topics/public-policy-monitoring-and-evaluation.html",
        },
        {
            "title": "Government at a Glance 2025 — Public policy evaluation",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/government-at-a-glance-2025_0efd0bcd-en/full-report/public-policy-evaluation_e59d50bb.html",
        },
        {
            "title": "Regulatory experimentation: Moving ahead on the agile regulatory governance agenda",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/regulatory-experimentation_f193910c-en.html",
        },
        {
            "title": "Territorial reforms in Europe: Does size matter?",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/territorial-reforms-in-europe-does-size-matter-territorial-amalgamatio/168076cf16",
        },
        {
            "title": "Regional democracy — Council of Europe Reference Framework",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/regional-democracy-reference-framework/168072febd",
        }
    ]
},


"archive/624-territorial-homes-for-shared-territorial-power-boundaries-membership-accession-exit-review-and-no-government-by-opt-in-map.md": {
    "groups": [
        {
            "title": "The EU-OECD definition of a functional urban area",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/the-eu-oecd-definition-of-a-functional-urban-area_d58cb34d-en.html",
        },
        {
            "title": "Approaches to Metropolitan Area Governance",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/approaches-to-metropolitan-area-governance_5jz5j1q7s128-en.html",
        },
        {
            "title": "Five years of the OECD Principles on Urban Policy",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/five-years-of-the-oecd-principles-on-urban-policy_e1104359-en.html",
        },
        {
            "title": "A contemporary commentary by the Congress on the Explanatory Report to the European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/09000016809ed6de",
        },
        {
            "title": "Territorial reforms in Europe: Does size matter?",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/territorial-reforms-in-europe-does-size-matter-territorial-amalgamatio/168076cf16",
        },
        {
            "title": "Regional democracy — Council of Europe Reference Framework",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/regional-democracy-reference-framework/168072febd",
        }
    ]
},


"archive/623-redress-homes-for-shared-territorial-power-complaints-hearings-appeals-ombuds-and-no-government-by-jurisdiction-hunt.md": {
    "groups": [
        {
            "title": "Recommendation of the Council on Access to Justice and People-Centred Justice Systems",
            "publisher": "OECD Legal Instruments",
            "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0498",
        },
        {
            "title": "Making Justice Systems More Effective and People Centred",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/making-justice-systems-more-effective-and-people-centred_e02fd90b-en.html",
        },
        {
            "title": "The role of Ombudsman Institutions in Open Government",
            "publisher": "OECD",
            "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2018/12/the-role-of-ombudsman-institutions-in-open-government_d2bf09ed/7353965f-en.pdf",
        },
        {
            "title": "The Governance of Regulators",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/the-governance-of-regulators_9789264209015-en.html",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-for-local-self-government-english-version-pdf-a6-59-p/16807198a3",
        },
        {
            "title": "Recommendation CM/Rec(2019)6 of the Committee of Ministers to member States on the development of the Ombudsman institution",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/090000168098392f",
        },
        {
            "title": "The office of Ombudsman and local and regional authorities",
            "publisher": "Council of Europe Congress",
            "url": "https://rm.coe.int/the-office-of-ombudsman-and-local-and-regional-authorities-draft-resol/1680719865",
        },
        {
            "title": "Principles on the Protection and Promotion of the Ombudsman Institution (the Venice Principles)",
            "publisher": "Venice Commission / Council of Europe",
            "url": "https://www.venice.coe.int/webforms/documents/default.aspx?pdffile=CDL-AD%282019%29005-e",
        }
    ]
},


"archive/622-emergency-homes-for-shared-territorial-power-emergency-operations-continuity-mutual-aid-recovery-and-no-government-by-crisis-summit.md": {
    "groups": [
        {
            "title": "Building resilience through disaster risk management in intermediary cities",
            "publisher": "OECD / UN-Habitat",
            "url": "https://www.oecd.org/en/publications/building-resilience-through-disaster-risk-management-in-intermediary-cities_b2f1efb1-en.html",
        },
        {
            "title": "Towards an All-Hazards Approach to Emergency Preparedness and Response",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/towards-an-all-hazards-approach-to-emergency-preparedness-and-response_9789264289031-en.html",
        },
        {
            "title": "Good Governance for Critical Infrastructure Resilience",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/good-governance-for-critical-infrastructure-resilience_02f0e5a0-en.html",
        },
        {
            "title": "Ensuring the resilience of critical infrastructure: Government at a Glance 2025",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/government-at-a-glance-2025_0efd0bcd-en/full-report/ensuring-the-resilience-of-critical-infrastructure_896f59cf.html",
        },
        {
            "title": "Sendai Framework for Disaster Risk Reduction 2015-2030",
            "publisher": "UNDRR",
            "url": "https://www.undrr.org/publication/sendai-framework-disaster-risk-reduction-2015-2030",
        },
        {
            "title": "Words into Action guidelines: Implementation guide for local disaster risk reduction and resilience strategies",
            "publisher": "UNDRR",
            "url": "https://www.undrr.org/publication/words-action-guidelines-implementation-guide-local-disaster-risk-reduction-and",
        },
        {
            "title": "Local authorities confronting natural disasters and emergencies",
            "publisher": "Council of Europe Congress",
            "url": "https://rm.coe.int/local-authorities-confronting-natural-disasters-and-emergencies-04-03-/16807192cb",
        },
        {
            "title": "Resolution 500 (2024) — Local and regional responses to natural disasters and climate hazards: from risk preparedness to resilience",
            "publisher": "Council of Europe Congress",
            "url": "https://rm.coe.int/res-500-2024-en-local-and-regional-responses-to-natural-disasters-jean/1680af1c08%20%2B",
        }
    ]
},

"archive/621-digital-operating-homes-for-shared-territorial-power-case-systems-identity-access-release-discipline-and-no-government-by-portal-shell.md": {
    "groups": [
        {
            "title": "Recommendation of the Council on Digital Government Strategies",
            "publisher": "OECD Legal Instruments",
            "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0406",
        },
        {
            "title": "The E-Leaders Handbook on the Governance of Digital Government",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/the-e-leaders-handbook-on-the-governance-of-digital-government_ac7f2531-en.html",
        },
        {
            "title": "The OECD Digital Government Policy Framework",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/the-oecd-digital-government-policy-framework_f64fed2a-en.html",
        },
        {
            "title": "Digital public infrastructure: Government at a Glance 2025",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/government-at-a-glance-2025_0efd0bcd-en/full-report/digital-public-infrastructure_1cee4220.html",
        },
        {
            "title": "Recommendation on Digital Security Risk Management",
            "publisher": "OECD Legal Instruments",
            "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0479",
        },
        {
            "title": "Convention 108 and Protocols",
            "publisher": "Council of Europe",
            "url": "https://www.coe.int/en/web/data-protection/convention108-and-protocol",
        },
        {
            "title": "Tromsø Convention — access to official documents",
            "publisher": "Council of Europe",
            "url": "https://www.coe.int/en/web/access-to-official-documents",
        }
    ]
},

"archive/620-workforce-homes-for-shared-territorial-power-employer-status-recruitment-training-labor-relations-and-no-government-by-borrowed-payroll.md": {
    "groups": [
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-for-local-self-government-english-version-pdf-a6-59-p/16807198a3",
        },
        {
            "title": "Regional democracy — Council of Europe Reference Framework",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/regional-democracy-reference-framework/168072febd",
        },
        {
            "title": "Recommendation of the Council on Public Service Leadership and Capability",
            "publisher": "OECD Legal Instruments",
            "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0445",
        },
        {
            "title": "Workforce Insights from Central Governments",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/workforce-insights-from-central-governments_2f9080b1-en.html",
        },
        {
            "title": "An international framework for human resource management indicators in public administration",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/an-international-framework-for-human-resource-management-indicators-in-public-administration_03763bab-en.html",
        },
        {
            "title": "Public employment and management",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/topics/public-employment-and-management.html",
        }
    ]
},

"archive/619-contract-homes-for-shared-territorial-power-procurement-franchising-change-control-exit-capacity-and-no-government-by-concession-patchwork.md": {
    "groups": [
        {
            "title": "Recommendation of the Council on Public Procurement",
            "publisher": "OECD Legal Instruments",
            "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0411",
        },
        {
            "title": "Implementing the OECD Recommendation on Public Procurement in OECD and Partner Countries",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/implementing-the-oecd-recommendation-on-public-procurement-in-oecd-and-partner-countries_02a46a58-en.html",
        },
        {
            "title": "Recommendation of the Council on Principles for Public Governance of Public-Private Partnerships",
            "publisher": "OECD Legal Instruments",
            "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0392",
        },
        {
            "title": "Infrastructure governance",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/topics/infrastructure-governance.html",
        },
        {
            "title": "Making public procurement transparent at local and regional levels",
            "publisher": "Council of Europe Congress",
            "url": "https://rm.coe.int/making-public-procurement-transparent-at-local-and-regional-levels/1680932035",
        }
    ]
},


"archive/618-regulatory-homes-for-shared-territorial-power-licensing-permits-standards-inspection-enforcement-and-no-government-by-operator-rulebook.md": {
    "groups": [
        {
            "title": "The Governance of Regulators",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/the-governance-of-regulators_9789264209015-en.html",
        },
        {
            "title": "Governance of Regulators' Practices",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/governance-of-regulators-practices_9789264255401-en.html",
        },
        {
            "title": "Governing the City",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/governing-the-city_9789264226500-en.html",
        },
        {
            "title": "Licensing and Permitting",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/licensing-and-permitting_68fc3301-en.html",
        },
        {
            "title": "Shaping the Relationship Between Public Transport and Innovative Mobility",
            "publisher": "OECD / ITF",
            "url": "https://www.oecd.org/en/publications/shaping-the-relationship-between-public-transport-and-innovative-mobility_7a1f7b89-en.html",
        },
        {
            "title": "Competition and Regulation in the Provision of Local Transportation Services",
            "publisher": "OECD / ITF",
            "url": "https://www.oecd.org/en/publications/competition-and-regulation-in-the-provision-of-local-transportation-services_2f2378f9-en.html",
        },
        {
            "title": "Explanatory report to the European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/09000016800ca431",
        },
        {
            "title": "Updated Rule of Law Checklist",
            "publisher": "Venice Commission / Council of Europe",
            "url": "https://www.venice.coe.int/webforms/documents/default.aspx?pdffile=CDL-AD%282025%29002-e",
        }
    ]
},


"archive/617-capital-homes-for-shared-territorial-power-multi-year-pipelines-asset-stewardship-lifecycle-discipline-and-no-government-by-project-list.md": {
    "groups": [
        {
            "title": "Effective Public Investment Toolkit",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/about/projects/effective-public-investment-toolkit.html",
        },
        {
            "title": "Recommendation on Governance of Infrastructure",
            "publisher": "OECD Legal Instruments",
            "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0460",
        },
        {
            "title": "Financing Cities of Tomorrow",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/financing-cities-of-tomorrow_51bd124a-en.html",
        },
        {
            "title": "Management of assets throughout their life cycle",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/management-of-assets-throughout-their-life-cycle_86ce92d8-en.html",
        },
        {
            "title": "Management of asset performance throughout the life cycle",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/government-at-a-glance-2025_0efd0bcd-en/full-report/management-of-asset-performance-throughout-the-life-cycle_77aa88af.html",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-for-local-self-government-english-version-pdf-a6-59-p/16807198a3",
        }
    ]
},

"archive/616-planning-homes-for-shared-territorial-power-territorial-plans-plan-hierarchies-conformity-and-no-government-by-vision-deck.md": {
    "groups": [
        {
            "title": "Governing the City",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/governing-the-city_9789264226500-en.html",
        },
        {
            "title": "The OECD Metropolitan Governance Survey",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/the-oecd-metropolitan-governance-survey_5jz43zldh08p-en.html",
        },
        {
            "title": "Land-use Planning Systems in the OECD",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/land-use-planning-systems-in-the-oecd_9789264268579-en.html",
        },
        {
            "title": "The theory and practice of spatial planning and development",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/redefining-spatial-planning-and-development-in-israel_89036c98-en/full-report/the-theory-and-practice-of-spatial-planning-and-development_5fe45aef.html",
        },
        {
            "title": "Governance of Land Use",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/about/projects/governance-of-land-use.html",
        },
        {
            "title": "European Regional/Spatial Planning Charter (Torremolinos Charter)",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/6th-european-conference-of-ministers-responsible-for-regional-planning/168076dd93",
        },
        {
            "title": "12th European Conference of Ministers responsible for Regional Planning (Hanover, 2000)",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/09000016804edc27",
        }
    ]
},

"archive/615-service-homes-for-shared-territorial-power-service-authorities-operator-chains-commissioning-continuity-and-no-government-by-memorandum-network.md": {
    "groups": [
        {
            "title": "The governance of public service delivery across territories",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/delivering-quality-education-and-health-care-to-all_83025c02-en/full-report/the-governance-of-public-service-delivery-across-territories_1241e96e.html",
        },
        {
            "title": "Improving the quality of the services to citizens through inter-municipal co-operation (IMC)",
            "publisher": "Council of Europe",
            "url": "https://www.coe.int/en/web/centre-of-expertise-for-multilevel-governance/imc",
        },
        {
            "title": "Governing the City",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/governing-the-city_9789264226500-en.html",
        },
        {
            "title": "Reforming Public Transport Planning and Delivery",
            "publisher": "ITF/OECD",
            "url": "https://www.oecd.org/en/publications/reforming-public-transport-planning-and-delivery_6c2f1869-en.html",
        },
        {
            "title": "Implementation Toolkit: OECD Recommendation on Regional Development Policy",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/about/projects/implementing-the-oecd-recommendation-on-regional-development-policy-toolkit.html",
        }
    ]
},



"archive/614-knowledge-homes-for-shared-territorial-power-observatories-territorial-indicators-basemaps-scenario-capacity-and-no-government-by-fragmented-spreadsheets.md": {
    "groups": [
        {
            "title": "Implementation Toolkit: OECD Recommendation on Regional Development Policy",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/about/projects/implementing-the-oecd-recommendation-on-regional-development-policy-toolkit.html",
        },
        {
            "title": "OECD Definition of Cities and Functional Urban Areas",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/data/datasets/oecd-definition-of-cities-and-functional-urban-areas.html",
        },
        {
            "title": "OECD Local Data Portal",
            "publisher": "OECD",
            "url": "https://localdataportal.oecd.org/methodology.html",
        },
        {
            "title": "Governing the City",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/governing-the-city_9789264226500-en.html",
        },
        {
            "title": "Regional Governance in OECD Countries",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/regional-governance-in-oecd-countries_4d7c6483-en.html",
        },
        {
            "title": "A Guide to Setting up an Urban Observatory",
            "publisher": "UN-Habitat",
            "url": "https://unhabitat.org/a-guide-to-setting-up-an-urban-observatory",
        }
    ]
},

"archive/613-participatory-homes-for-shared-territorial-power-petitions-hearings-mini-publics-territorial-notice-and-no-metropolitan-participation-by-postcode.md": {
    "groups": [
        {
            "title": "Additional Protocol on the right to participate in the affairs of a local authority",
            "publisher": "Council of Europe Congress",
            "url": "https://www.coe.int/en/web/congress/additional-protocol-to-the-european-charter-of-local-self-government-on-the-right-to-participate-in-the-affairs-of-a-local-authority",
        },
        {
            "title": "Deliberative democracy",
            "publisher": "Council of Europe Congress",
            "url": "https://www.coe.int/en/web/congress/deliberative-democracy",
        },
        {
            "title": "Citizen participation at local and regional level in Europe",
            "publisher": "Council of Europe Congress",
            "url": "https://rm.coe.int/168071a7c6",
        },
        {
            "title": "OECD Guidelines for Citizen Participation Processes",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/oecd-guidelines-for-citizen-participation-processes_f765caf6-en.html",
        },
        {
            "title": "Open government and citizen participation",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/topics/open-government-and-citizen-participation.html",
        },
        {
            "title": "Citizen participation and deliberation: Government at a Glance 2025",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/government-at-a-glance-2025_0efd0bcd-en/full-report/citizen-participation-and-deliberation_52b90285.html",
        },
        {
            "title": "Innovative public participation",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/topics/sub-issues/open-government-and-citizen-participation/innovative-public-participation.html",
        }
    ]
},

"archive/612-intergovernmental-homes-for-shared-territorial-power-standing-consultation-compacts-dispute-lanes-and-no-government-by-ad-hoc-summit.md": {
    "groups": [
        {
            "title": "A contemporary commentary by the Congress on the Explanatory Report to the European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/09000016809ed6de",
        },
        {
            "title": "Regional democracy — Council of Europe Reference Framework",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/regional-democracy-reference-framework/168072febd",
        },
        {
            "title": "Regional Governance in OECD Countries",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/regional-governance-in-oecd-countries_4d7c6483-en.html",
        },
        {
            "title": "Implementation Toolkit: OECD Recommendation on Regional Development Policy",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/about/projects/implementing-the-oecd-recommendation-on-regional-development-policy-toolkit.html",
        }
    ]
},

"archive/611-public-law-homes-for-shared-territorial-power-legal-personality-named-competences-rulemaking-and-no-government-by-interlocal-contract.md": {
    "groups": [
        {
            "title": "The European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://www.coe.int/en/web/congress/the-charter-how-it-works",
        },
        {
            "title": "Regional democracy — Council of Europe Reference Framework",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/168074721b",
        },
        {
            "title": "Approaches to Metropolitan Area Governance",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/approaches-to-metropolitan-area-governance_5jz5j1q7s128-en.html",
        },
        {
            "title": "The OECD Metropolitan Governance Survey",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/the-oecd-metropolitan-governance-survey_5jz43zldh08p-en.html",
        },
        {
            "title": "Regional Governance in OECD Countries",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/regional-governance-in-oecd-countries_4d7c6483-en.html",
        }
    ]
},

"archive/607-democratic-homes-for-shared-territorial-power-indirect-councils-double-legitimacy-direct-election-and-no-metropolitan-rule-by-proxy.md": {
    "groups": [
        {
            "title": "The OECD Metropolitan Governance Survey",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/the-oecd-metropolitan-governance-survey_5jz43zldh08p-en.html",
        },
        {
            "title": "Governing the City",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/governing-the-city_9789264226500-en.html",
        },
        {
            "title": "Regional Governance in OECD Countries",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/regional-governance-in-oecd-countries_4d7c6483-en.html",
        },
        {
            "title": "Good governance of large metropolises",
            "publisher": "Council of Europe Congress",
            "url": "https://rm.coe.int/doc/09000016807199cb",
        },
        {
            "title": "Regional democracy — Council of Europe Reference Framework",
            "publisher": "Council of Europe",
            "url": "https://edoc.coe.int/en/local-democracy/7645-regional-democracy-council-of-europe-reference-framework.html",
        }
    ]
},

"archive/606-when-co-operation-becomes-government-thresholds-for-constitutionalizing-shared-territorial-power-and-no-metropolitan-rule-by-consortium.md": {
    "groups": [
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://www.coe.int/en/web/congress/the-charter-how-it-works",
        },
        {
            "title": "Improving the quality of the services to citizens through inter-municipal co-operation (IMC)",
            "publisher": "Council of Europe",
            "url": "https://www.coe.int/en/web/centre-of-expertise-for-multilevel-governance/imc",
        },
        {
            "title": "Decentralisation",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/topics/decentralisation.html",
        },
        {
            "title": "Making Decentralisation Work",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/making-decentralisation-work_g2g9faa7-en.html",
        },
        {
            "title": "OECD Definition of Cities and Functional Urban Areas",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/data/datasets/oecd-definition-of-cities-and-functional-urban-areas.html",
        },
        {
            "title": "Approaches to Metropolitan Area Governance",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/approaches-to-metropolitan-area-governance_5jz5j1q7s128-en.html",
        },
        {
            "title": "The OECD Metropolitan Governance Survey",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/the-oecd-metropolitan-governance-survey_5jz43zldh08p-en.html",
        },
        {
            "title": "Regional democracy — Council of Europe Reference Framework",
            "publisher": "Council of Europe",
            "url": "https://edoc.coe.int/en/local-democracy/7645-regional-democracy-council-of-europe-reference-framework.html",
        }
    ]
},


"archive/610-accountability-homes-for-shared-territorial-power-scrutiny-audit-disclosure-complaints-review-and-no-government-by-jurisdictional-gap.md": {
    "groups": [
        {
            "title": "Recommendation CM/Rec(2022)2 on democratic accountability of elected representatives and elected bodies at local and regional level",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/0900001680a57739",
        },
        {
            "title": "Access to official documents – Guide",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/access-to-official-documents-guide/168069660c",
        },
        {
            "title": "Transparency and open government",
            "publisher": "Council of Europe Congress",
            "url": "https://rm.coe.int/transparency-and-open-government/1680932036",
        },
        {
            "title": "Internal control and audit",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/topics/internal-control-and-audit-in-the-public-sector.html",
        },
        {
            "title": "Public integrity",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/topics/public-integrity.html",
        },
        {
            "title": "The OECD Metropolitan Governance Survey",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/the-oecd-metropolitan-governance-survey_5jz43zldh08p-en.html",
        },
        {
            "title": "Regional Governance in OECD Countries",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/regional-governance-in-oecd-countries_4d7c6483-en.html",
        }
    ]
},


"archive/609-administrative-homes-for-shared-territorial-power-own-executive-own-staff-records-treasury-planning-core-and-no-government-by-secondment-maze.md": {
    "groups": [
        {
            "title": "Regional democracy — Council of Europe Reference Framework",
            "publisher": "Council of Europe",
            "url": "https://edoc.coe.int/en/local-democracy/7645-regional-democracy-council-of-europe-reference-framework.html",
        },
        {
            "title": "Making Decentralisation Work",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/making-decentralisation-work_g2g9faa7-en.html",
        },
        {
            "title": "Governing the City",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/governing-the-city_9789264226500-en.html",
        },
        {
            "title": "Regional Governance in OECD Countries",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/regional-governance-in-oecd-countries_4d7c6483-en.html",
        },
        {
            "title": "Effective Public Investment Toolkit",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/about/projects/effective-public-investment-toolkit.html",
        }
    ]
},

"archive/608-fiscal-homes-for-shared-territorial-power-own-source-revenue-predictable-equalization-capital-discipline-and-no-metropolitan-government-by-begging-bowl.md": {
    "groups": [
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://www.coe.int/en/web/impact-convention-human-rights/european-charter-of-local-self-government",
        },
        {
            "title": "Subnational finance and investment",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/topics/subnational-finance-and-investment.html",
        },
        {
            "title": "OECD Fiscal Decentralisation Database",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/data/datasets/oecd-fiscal-decentralisation-database.html",
        },
        {
            "title": "OECD Definition of Cities and Functional Urban Areas",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/data/datasets/oecd-definition-of-cities-and-functional-urban-areas.html",
        },
        {
            "title": "Approaches to Metropolitan Area Governance",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/approaches-to-metropolitan-area-governance_5jz5j1q7s128-en.html",
        },
        {
            "title": "Regional Governance in OECD Countries",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/regional-governance-in-oecd-countries_4d7c6483-en.html",
        }
    ]
},

"archive/605-repair-ladders-for-multilevel-government-lane-fixes-connectors-kit-completion-cooperation-territorial-upgrades-map-surgery-and-no-reform-by-single-instrument.md": {
    "groups": [
        {
            "title": "Multi-level Governance Reforms",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/multi-level-governance-reforms_9789264272866-en.html",
        },
        {
            "title": "Effective Public Investment Toolkit",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/about/projects/effective-public-investment-toolkit.html",
        },
        {
            "title": "Inter-municipal co-operation in the Western Balkans",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/inter-municipal-co-operation-in-the-western-balkans_a78a01e6-en.html",
        },
        {
            "title": "Tools on Good Democratic Governance",
            "publisher": "Council of Europe Congress",
            "url": "https://www.coe.int/en/web/congress/tools-on-good-governance",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://www.coe.int/en/web/impact-convention-human-rights/european-charter-of-local-self-government",
        },
        {
            "title": "Territorial reforms in Europe: Does size matter?",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/territorial-reforms-in-europe-does-size-matter-territorial-amalgamatio/168076cf16",
        },
        {
            "title": "Governing the City",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/governing-the-city_9789264226500-en.html",
        },
        {
            "title": "International Practices of Metropolitan Governance",
            "publisher": "World Bank",
            "url": "https://documents.worldbank.org/en/publication/documents-reports/documentdetail/278861591018281649",
        }
    ]
},

"archive/604-diagnosing-scope-misfit-overbuild-underbuild-duplicate-chains-orphan-functions-and-no-government-by-institutional-furniture.md": {
    "groups": [
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://www.coe.int/en/web/impact-convention-human-rights/european-charter-of-local-self-government",
        },
        {
            "title": "Regional democracy — Council of Europe Reference Framework",
            "publisher": "Council of Europe",
            "url": "https://edoc.coe.int/en/local-democracy/7645-regional-democracy-council-of-europe-reference-framework.html",
        },
        {
            "title": "Assigning responsibilities across levels of government",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html",
        },
        {
            "title": "Making Decentralisation Work",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/making-decentralisation-work_g2g9faa7-en.html",
        },
        {
            "title": "Effective Public Investment Toolkit",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/about/projects/effective-public-investment-toolkit.html",
        },
        {
            "title": "The governance of public service delivery across territories",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/delivering-quality-education-and-health-care-to-all_83025c02-en/full-report/the-governance-of-public-service-delivery-across-territories_1241e96e.html",
        },
        {
            "title": "The OECD Metropolitan Governance Survey",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/the-oecd-metropolitan-governance-survey_5jz43zldh08p-en.html",
        },
        {
            "title": "Elinor Ostrom – Prize Lecture",
            "publisher": "Nobel Prize Outreach",
            "url": "https://www.nobelprize.org/prizes/economic-sciences/2009/ostrom/lecture/",
        }
    ]
},

"archive/603-order-of-operations-for-ideal-multilevel-government-vocation-assignment-kits-connectors-asymmetry-and-no-reform-by-layer-shopping.md": {
    "groups": [
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://www.coe.int/en/web/impact-convention-human-rights/european-charter-of-local-self-government",
        },
        {
            "title": "Assigning responsibilities across levels of government",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/assigning-responsibilities-across-levels-of-government_f0944eae-en.html",
        },
        {
            "title": "Decentralisation",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/topics/decentralisation.html",
        },
        {
            "title": "Effective Public Investment Toolkit",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/about/projects/effective-public-investment-toolkit.html",
        },
        {
            "title": "Elinor Ostrom – Prize Lecture",
            "publisher": "Nobel Prize Outreach",
            "url": "https://www.nobelprize.org/prizes/economic-sciences/2009/ostrom/lecture/",
        }
    ]
},

"archive/602-ideal-governments-of-each-scope-steward-cells-municipal-general-government-metropolitan-systems-democracy-regional-territorial-platforms-national-guarantor-states-continental-compacts-and-global-treaty-narrow-waists.md": {
    "groups": [
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://www.coe.int/en/web/impact-convention-human-rights/european-charter-of-local-self-government",
        },
        {
            "title": "Regional democracy — Council of Europe Reference Framework",
            "publisher": "Council of Europe",
            "url": "https://edoc.coe.int/en/local-democracy/7645-regional-democracy-council-of-europe-reference-framework.html",
        },
        {
            "title": "The OECD Metropolitan Governance Survey",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/the-oecd-metropolitan-governance-survey_5jz43zldh08p-en.html",
        },
        {
            "title": "Regional Governance in OECD Countries",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/regional-governance-in-oecd-countries_4d7c6483-en.html",
        },
        {
            "title": "Elinor Ostrom – Prize Lecture",
            "publisher": "Nobel Prize Outreach",
            "url": "https://www.nobelprize.org/prizes/economic-sciences/2009/ostrom/lecture/",
        },
        {
            "title": "UN Charter",
            "publisher": "United Nations",
            "url": "https://www.un.org/en/about-us/un-charter",
        },
        {
            "title": "International Health Regulations",
            "publisher": "World Health Organization",
            "url": "https://www.who.int/health-topics/international-health-regulations",
        }
    ]
},


"archive/601-publicity-of-local-deliberation-open-meetings-agenda-notice-closed-session-limits-and-no-government-by-chamber-obscurity.md": {
    "groups": [
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-for-local-self-government-english-version-pdf-a6-59-p/16807198a3",
        },
        {
            "title": "Relations between the public, the local assembly and the executive in local democracy",
            "publisher": "Council of Europe Congress",
            "url": "https://rm.coe.int/relations-between-the-public-the-local-assembly-and-the-executive-in-l/16807191c1",
        },
        {
            "title": "Draft explanatory report to the Additional Protocol to the European Charter of Local Self-Government on the right to participate in the affairs of a local authority",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/168074807d",
        },
        {
            "title": "The Council of Europe Convention on Access to Official Documents (Tromsø Convention)",
            "publisher": "Council of Europe",
            "url": "https://www.coe.int/en/web/access-to-official-documents",
        },
        {
            "title": "OECD Guidelines for Citizen Participation Processes",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/oecd-guidelines-for-citizen-participation-processes_f765caf6-en.html",
        },
        {
            "title": "Open government and citizen participation",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/topics/open-government-and-citizen-participation.html",
        }
    ]
},

"archive/600-organizational-autonomy-internal-administrative-structures-standing-orders-and-no-self-government-by-template-lock.md": {
    "groups": [
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-for-local-self-government-english-version-pdf-a6-59-p/16807198a3",
        },
        {
            "title": "Contemporary commentary of the Congress on the Explanatory Report of the European Charter of Local Self-Government",
            "publisher": "Council of Europe Congress",
            "url": "https://rm.coe.int/09000016809ed6de",
        },
        {
            "title": "Monitoring of the application of the European Charter of Local Self-Government in Slovenia",
            "publisher": "Council of Europe Congress",
            "url": "https://rm.coe.int/cpl-2025-49-02-en-monitoring-of-the-application-of-the-european-charte/488028ca87",
        },
        {
            "title": "Monitoring of the application of the European Charter of Local Self-Government in Poland",
            "publisher": "Council of Europe Congress",
            "url": "https://rm.coe.int/cg-2025-49-10prov-en-monitoring-of-the-application-of-european-charter/488028cb6c",
        },
        {
            "title": "Regional Governance in OECD Countries",
            "publisher": "OECD",
            "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2022/12/regional-governance-in-oecd-countries_a9c03edb/4d7c6483-en.pdf",
        },
        {
            "title": "Regional Democracy Reference Framework",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/regional-democracy-reference-framework/168072febd",
        }
    ]
},


"archive/599-local-and-regional-assembly-scrutiny-rights-agenda-power-questions-committee-capacity-and-no-majoritarian-blackout.md": {
    "groups": [
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-for-local-self-government-english-version-pdf-a6-59-p/16807198a3",
        },
        {
            "title": "Relations between the public, the local assembly and the executive in local democracy",
            "publisher": "Council of Europe Congress",
            "url": "https://rm.coe.int/relations-between-the-public-the-local-assembly-and-the-executive-in-l/16807191c1",
        },
        {
            "title": "Recommendation CM/Rec(2022)2 on democratic accountability of elected representatives and elected bodies at local and regional level",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/0900001680a57739",
        },
        {
            "title": "Monitoring of the application of the European Charter of Local Self-Government in Iceland",
            "publisher": "Council of Europe Congress",
            "url": "https://rm.coe.int/monitoring-of-the-application-of-the-european-charter-of-local-self-go/1680b1bd8b",
        }
    ]
},


"archive/598-conditions-of-office-for-local-elected-representatives-free-mandate-fair-compensation-lawful-removal-and-no-self-government-by-attrition.md": {
    "groups": [
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-for-local-self-government-english-version-pdf-a6-59-p/16807198a3",
        },
        {
            "title": "Contemporary commentary of the Congress on the Explanatory Report of the European Charter of Local Self-Government",
            "publisher": "Council of Europe Congress",
            "url": "https://rm.coe.int/09000016809ed6de",
        },
        {
            "title": "The Congress calls for proper compensation for local and regional elected representatives",
            "publisher": "Council of Europe Congress",
            "url": "https://www.coe.int/en/web/congress/-/le-congres-plaide-pour-une-indemnisation-adequate-des-elus-locaux-et-regionaux",
        },
        {
            "title": "Dismissal of Mayor of Van: Statement by Congress co-Rapporteurs on local democracy in Türkiye",
            "publisher": "Council of Europe Congress",
            "url": "https://www.coe.int/en/web/congress/-/dismissal-of-mayor-of-van-statement-by-congress-co-rapporteurs-on-local-democracy-in-t%C3%BCrkiye",
        },
        {
            "title": "Council of Europe Congress completes second fact-finding visit to Türkiye",
            "publisher": "Council of Europe Congress",
            "url": "https://www.coe.int/en/web/congress/-/council-of-europe-congress-completes-second-fact-finding-visit-to-t%C3%BCrkiye",
        },
        {
            "title": "Adopted Texts",
            "publisher": "Council of Europe Congress",
            "url": "https://www.coe.int/en/web/congress/adopted-texts",
        }
    ]
},


"archive/597-local-participation-rights-petitions-initiatives-referendums-deliberative-mini-publics-and-no-direct-democracy-by-ambush.md": {
    "groups": [
        {
            "title": "Additional Protocol to the European Charter of Local Self-Government on the right to participate in the affairs of a local authority",
            "publisher": "Council of Europe Congress",
            "url": "https://www.coe.int/en/web/congress/additional-protocol-to-the-european-charter-of-local-self-government-on-the-right-to-participate-in-the-affairs-of-a-local-authority",
        },
        {
            "title": "OECD Guidelines for Citizen Participation Processes",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/oecd-guidelines-for-citizen-participation-processes_f765caf6-en.html",
        },
        {
            "title": "Citizen participation and deliberation: Government at a Glance 2025",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/government-at-a-glance-2025_0efd0bcd-en/full-report/citizen-participation-and-deliberation_52b90285.html",
        },
        {
            "title": "Open government and citizen participation",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/topics/open-government-and-citizen-participation.html",
        },
        {
            "title": "New Charter on youth participation in cities and regions: Council of Europe Congress calls for supportive environments for young people",
            "publisher": "Council of Europe Congress",
            "url": "https://www.coe.int/en/web/congress/-/new-charter-on-youth-participation-in-cities-and-regions-council-of-europe-congress-calls-for-supportive-environments-for-young-people",
        },
        {
            "title": "Youth democratic participation – especially at local level – essential in times of stability and crisis alike",
            "publisher": "Council of Europe Congress",
            "url": "https://www.coe.int/en/web/congress/-/youth-democratic-participation-especially-at-local-level-essential-in-times-of-stability-and-crisis-alike",
        }
    ]
},



"archive/596-special-purpose-authorities-utility-districts-metro-agencies-and-no-government-by-quango-sprawl.md": {
    "groups": [
        {
            "title": "The OECD Metropolitan Governance Survey",
            "publisher": "OECD",
            "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2014/05/the-oecd-metropolitan-governance-survey_g17a2494/5jz43zldh08p-en.pdf",
        },
        {
            "title": "Regional Governance in OECD Countries",
            "publisher": "OECD",
            "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2022/12/regional-governance-in-oecd-countries_a9c03edb/4d7c6483-en.pdf",
        },
        {
            "title": "Good governance of large metropolises",
            "publisher": "Council of Europe Congress",
            "url": "https://rm.coe.int/doc/09000016807199cb",
        },
        {
            "title": "International Practices of Metropolitan Governance: A Compendium of Collaborative Arrangements in Metropolitan Areas",
            "publisher": "World Bank",
            "url": "https://documents1.worldbank.org/curated/en/278861591018281649/pdf/International-Practices-of-Metropolitan-Governance-A-Compendium-of-Collaborative-Arrangements-in-Metropolitan-Areas.pdf",
        },
        {
            "title": "Strengthening Institutions for Urban and Metropolitan Governance",
            "publisher": "World Bank",
            "url": "https://documents1.worldbank.org/curated/en/931371495809283076/pdf/115312-PN-P156898-PUBLIC-Policy-Notes-Urban-Institutions-FINAL2.pdf",
        }
    ]
},


"archive/595-territorial-reorganization-incorporation-mergers-splits-status-change-and-no-map-surgery-by-managerial-fiat.md": {
    "groups": [
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-for-local-self-government-english-version-pdf-a6-59-p/16807198a3",
        },
        {
            "title": "Contemporary commentary of the Congress on the Explanatory Report of the European Charter of Local Self-Government",
            "publisher": "Council of Europe Congress",
            "url": "https://rm.coe.int/09000016809ed6de",
        },
        {
            "title": "The right of local authorities to be consulted by other levels of government",
            "publisher": "Council of Europe Congress",
            "url": "https://rm.coe.int/the-right-of-local-authorities-to-be-consulted-by-other-levels-of-gove/168071962f",
        },
        {
            "title": "Monitoring of the application of the European Charter of Local Self-Government in Finland",
            "publisher": "Council of Europe Congress",
            "url": "https://rm.coe.int/recommendation-516-2024-monitoring-of-the-application-of-the-european-/1680b205ac",
        },
        {
            "title": "Multi-level Governance Reforms",
            "publisher": "OECD",
            "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2017/05/multi-level-governance-reforms_g1g77b03/9789264272866-en.pdf",
        },
        {
            "title": "Making multi-level governance work for Slovenia’s regions",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/building-more-competitive-regions-in-slovenia_7dd44220-en/full-report/making-multi-level-governance-work-for-slovenia-s-regions_f2c32b83.html",
        }
    ]
},


"archive/594-local-authority-associations-consortia-transfrontier-co-operation-and-no-self-government-in-isolation.md": {
    "groups": [
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-for-local-self-government-english-version-pdf-a6-59-p/16807198a3",
        },
        {
            "title": "Contemporary commentary of the Congress on the Explanatory Report of the European Charter of Local Self-Government",
            "publisher": "Council of Europe Congress",
            "url": "https://rm.coe.int/09000016809ed6de",
        },
        {
            "title": "Regional Governance in OECD Countries",
            "publisher": "OECD",
            "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2022/12/regional-governance-in-oecd-countries_a9c03edb/4d7c6483-en.pdf",
        }
    ]
},

"archive/593-local-self-government-judicial-remedy-constitutional-standing-interim-relief-and-no-autonomy-without-recourse.md": {
    "groups": [
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-for-local-self-government-english-version-pdf-a6-59-p/16807198a3",
        },
        {
            "title": "Contemporary commentary of the Congress on the Explanatory Report of the European Charter of Local Self-Government",
            "publisher": "Council of Europe Congress",
            "url": "https://rm.coe.int/09000016809ed6de",
        },
        {
            "title": "Monitoring of the application of the European Charter of Local Self-Government in the Republic of Moldova",
            "publisher": "Council of Europe Congress",
            "url": "https://rm.coe.int/cg-2025-49-16prov-en-monitoring-of-the-application-of-the-european-cha/488028d4b8",
        },
        {
            "title": "Monitoring of the application of the European Charter of Local Self-Government in Poland",
            "publisher": "Council of Europe Congress",
            "url": "https://rm.coe.int/cg-2025-49-10prov-en-monitoring-of-the-application-of-european-charter/488028cb6c",
        },
        {
            "title": "Compliance of Norwegian legislation with Article 11 of the European Charter of Local Self-Government",
            "publisher": "Council of Europe Congress",
            "url": "https://rm.coe.int/compliance-of-norwegian-legislation-with-article-11-of-the-european-ch/1680718ab2",
        },
        {
            "title": "Local autonomy, government quality and fragmentation",
            "publisher": "OECD",
            "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2021/01/a-comprehensive-approach-to-understanding-urban-productivity-effects-of-local-governments_fe88e6b5/5ebd25d3-en.pdf",
        }
    ]
},

"archive/592-local-ordinance-power-bylaws-framework-laws-review-lanes-and-no-self-government-by-administration-only.md": {
    "groups": [
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-for-local-self-government-english-version-pdf-a6-59-p/16807198a3",
        },
        {
            "title": "Contemporary commentary of the Congress on the Explanatory Report of the European Charter of Local Self-Government",
            "publisher": "Council of Europe Congress",
            "url": "https://rm.coe.int/09000016809ed6de",
        },
        {
            "title": "Monitoring of the application of the European Charter of Local Self-Government in Greece",
            "publisher": "Council of Europe Congress",
            "url": "https://rm.coe.int/cg-2025-49-17prov-en-monitoring-of-the-application-of-the-european-cha/488028d2bf",
        },
        {
            "title": "Monitoring of the application of the European Charter of Local Self-Government in Poland",
            "publisher": "Council of Europe Congress",
            "url": "https://rm.coe.int/cg-2025-49-10prov-en-monitoring-of-the-application-of-european-charter/488028cb6c",
        },
        {
            "title": "Multi-Level Regulatory Governance",
            "publisher": "OECD",
            "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2009/06/multi-level-regulatory-governance_g17a1cdc/224074617147.pdf",
        },
        {
            "title": "Local autonomy, government quality and fragmentation",
            "publisher": "OECD",
            "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2021/01/a-comprehensive-approach-to-understanding-urban-productivity-effects-of-local-governments_fe88e6b5/5ebd25d3-en.pdf",
        }
    ]
},

"archive/591-concurrent-competences-lead-lane-typing-paramountcy-defaults-and-no-government-by-overlap-fog.md": {
    "groups": [
        {
            "title": "Explanatory Report to the European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/16800ca437",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-for-local-self-government-english-version-pdf-a6-59-p/16807198a3",
        },
        {
            "title": "Implementing regional development strategies: A practitioner’s guide",
            "publisher": "OECD",
            "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2025/06/implementing-regional-development-strategies_850177cf/ae8b0b0e-en.pdf",
        },
        {
            "title": "Recommendations on Enhancing the Skills Governance System in Sweden",
            "publisher": "OECD",
            "url": "https://www.oecd.org/content/dam/oecd/en/about/programmes/dg-reform/sweden/Recommendations-on-Enhancing-the-Skills-Governance-System-in-Sweden.pdf",
        }
    ]
},

"archive/590-multilevel-impact-packets-subsidiarity-territorial-effects-rural-proofing-and-no-lawmaking-by-placeless-abstraction.md": {
    "groups": [
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-for-local-self-government-english-version-pdf-a6-59-p/16807198a3",
        },
        {
            "title": "The right of local authorities to be consulted by other levels of government",
            "publisher": "Council of Europe Congress",
            "url": "https://rm.coe.int/the-right-of-local-authorities-to-be-consulted-by-other-levels-of-gove/168071962f",
        },
        {
            "title": "Better regulation",
            "publisher": "European Commission",
            "url": "https://commission.europa.eu/law/law-making-process/better-regulation_en",
        },
        {
            "title": "Annual Report 2024 on the application of the principles of subsidiarity and proportionality and on relations with national Parliaments",
            "publisher": "European Commission",
            "url": "https://commission.europa.eu/publications/annual-report-2024-application-principles-subsidiarity-and-proportionality-and-relations-national_en",
        },
        {
            "title": "Implementation Toolkit: OECD Recommendation on Regional Development Policy",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/about/projects/implementing-the-oecd-recommendation-on-regional-development-policy-toolkit.html",
        },
        {
            "title": "Rural proofing: Lessons from OECD countries and potential application to health",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/rural-proofing_bf4fa3b5-en.html",
        },
        {
            "title": "Reinforcing Rural Resilience",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/reinforcing-rural-resilience_7cd485e3-en.html",
        }
    ]
},

"archive/589-general-competence-home-rule-local-charters-municipal-initiative-and-no-government-by-ultra-vires-fragment.md": {
    "groups": [
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-for-local-self-government-english-version-pdf-a6-59-p/16807198a3",
        },
        {
            "title": "Contemporary commentary of the Congress on the Explanatory Report of the European Charter of Local Self-Government",
            "publisher": "Council of Europe Congress",
            "url": "https://rm.coe.int/09000016809ed6de",
        },
        {
            "title": "Monitoring of the application of the European Charter of Local Self-Government in Poland",
            "publisher": "Council of Europe Congress",
            "url": "https://rm.coe.int/cg-2025-49-10prov-en-monitoring-of-the-application-of-european-charter/488028cb6c",
        },
        {
            "title": "France Introduction",
            "publisher": "European Committee of the Regions",
            "url": "https://portal.cor.europa.eu/divisionpowers/Pages/France-Introduction.aspx",
        },
        {
            "title": "Germany Introduction",
            "publisher": "European Committee of the Regions",
            "url": "https://portal.cor.europa.eu/divisionpowers/Pages/Germany-Introduction.aspx",
        },
        {
            "title": "Making Decentralisation Work",
            "publisher": "OECD",
            "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2019/03/making-decentralisation-work_g1g9faa7/g2g9faa7-en.pdf",
        }
    ]
},


"archive/588-delegated-state-tasks-local-discretion-agent-status-funding-and-no-mixed-accountability-blur.md": {
    "groups": [
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-for-local-self-government-english-version-pdf-a6-59-p/16807198a3",
        },
        {
            "title": "Contemporary commentary of the Congress on the Explanatory Report of the European Charter of Local Self-Government",
            "publisher": "Council of Europe Congress",
            "url": "https://rm.coe.int/09000016809ed6de",
        },
        {
            "title": "Recommendation CM/Rec(2019)3 of the Committee of Ministers to member States on supervision of local authorities’ activities",
            "publisher": "Council of Europe Committee of Ministers",
            "url": "https://rm.coe.int/090000168093d066",
        },
        {
            "title": "The governance of public service delivery across territories",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/delivering-quality-education-and-health-care-to-all_83025c02-en/full-report/the-governance-of-public-service-delivery-across-territories_1241e96e.html",
        }
    ]
},

"archive/587-deconcentrated-state-administration-prefects-field-offices-and-no-shadow-local-government.md": {
    "groups": [
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-for-local-self-government-english-version-pdf-a6-59-p/16807198a3",
        },
        {
            "title": "Contemporary commentary of the Congress on the Explanatory Report of the European Charter of Local Self-Government",
            "publisher": "Council of Europe Congress",
            "url": "https://rm.coe.int/168071a859",
        },
        {
            "title": "Regional Governance in OECD Countries: Trends, Typology and Tools",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/regional-governance-in-oecd-countries_4d7c6483-en.html",
        },
        {
            "title": "Decentralisation and Regionalisation in Portugal",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/decentralisation-and-regionalisation-in-portugal_fea62108-en.html",
        },
        {
            "title": "Multi-Level Governance in Crisis-Affected Settings",
            "publisher": "UNDP",
            "url": "https://www.undp.org/sites/g/files/zskgke326/files/2025-09/undp-multi-level_governance-in-crisis-affected_settings.pdf",
        }
    ]
},

"archive/586-function-transfer-packs-staff-assets-records-contracts-liabilities-and-no-reassignment-by-legal-text-alone.md": {
    "groups": [
        {
            "title": "Decentralisation",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/topics/decentralisation.html",
        },
        {
            "title": "Making Decentralisation Work",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/making-decentralisation-work_g2g9faa7-en.html",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-for-local-self-government-english-version-pdf-a6-59-p/16807198a3",
        },
        {
            "title": "Multi-Level Governance in Crisis-Affected Settings",
            "publisher": "UNDP",
            "url": "https://www.undp.org/sites/g/files/zskgke326/files/2025-09/undp-multi-level_governance-in-crisis-affected_settings.pdf",
        }
    ]
},

"archive/585-conditional-grants-matching-funds-competitive-programs-and-no-government-by-grant-maze.md": {
    "groups": [
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-for-local-self-government-english-version-pdf-a6-59-p/16807198a3",
        },
        {
            "title": "Monitoring of the application of the European Charter of Local Self-Government in Slovenia",
            "publisher": "Council of Europe Congress",
            "url": "https://rm.coe.int/cpl-2025-49-02-en-monitoring-of-the-application-of-the-european-charte/488028ca87",
        },
        {
            "title": "Effective Public Investment Across Levels of Government",
            "publisher": "OECD Legal Instruments",
            "url": "https://legalinstruments.oecd.org/public/doc/302/302.en.pdf",
        },
        {
            "title": "Effective Public Investment Toolkit",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/about/projects/effective-public-investment-toolkit.html",
        },
        {
            "title": "Place-Based Policies for the Future",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/place-based-policies-for-the-future_e5ff6716-en.html",
        },
        {
            "title": "Conditional Grants in Principle, in Practice and in Operations: A Primer",
            "publisher": "World Bank",
            "url": "https://documents.worldbank.org/en/publication/documents-reports/documentdetail/099225502022337463",
        }
    ]
},
"archive/584-common-floors-local-headroom-explicit-preemption-rules-and-no-silent-override-by-upper-tier-convenience.md": {
    "groups": [
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-for-local-self-government-english-version-pdf-a6-59-p/16807198a3",
        },
        {
            "title": "Recommendation CM/Rec(2019)3 on supervision of local authorities’ activities",
            "publisher": "Council of Europe Committee of Ministers",
            "url": "https://rm.coe.int/090000168093d066",
        },
        {
            "title": "Implementation Toolkit: OECD Recommendation on Regional Development Policy",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/about/projects/implementing-the-oecd-recommendation-on-regional-development-policy-toolkit.html",
        },
        {
            "title": "Place-Based Policies for the Future",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/place-based-policies-for-the-future_e5ff6716-en.html",
        },
        {
            "title": "When should place-based policies be used and at what scale?",
            "publisher": "OECD",
            "url": "https://www.oecd.org/content/dam/oecd/en/about/projects/cfe/place-based-policies-for-the-future/when-should-place-based-policies-be-used-and-at-what-scale.pdf",
        }
    ]
},
"archive/583-subnational-distress-administrative-supervision-special-measures-handback-clocks-and-no-silent-recentralization.md": {
    "groups": [
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-for-local-self-government-english-version-pdf-a6-59-p/16807198a3",
        },
        {
            "title": "Contemporary commentary of the Congress on the Explanatory Report of the European Charter of Local Self-Government",
            "publisher": "Council of Europe Congress",
            "url": "https://rm.coe.int/09000016809ed6de",
        },
        {
            "title": "Recommendation CM/Rec(2019)3 on supervision of local authorities’ activities",
            "publisher": "Council of Europe Committee of Ministers",
            "url": "https://rm.coe.int/090000168093d066",
        },
        {
            "title": "Managing rising subnational fiscal risks",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/managing-rising-subnational-fiscal-risks_58437ac8-en.html",
        },
        {
            "title": "Insolvency Frameworks for Sub-national Governments",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/insolvency-frameworks-for-sub-national-governments_f9874122-en.html",
        },
        {
            "title": "Fiscal Federalism 2022",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/fiscal-federalism-2022_201c75b6-en.html",
        },
        {
            "title": "How to Manage Fiscal Risks from Subnational Governments",
            "publisher": "IMF",
            "url": "https://www.imf.org/-/media/files/publications/howtonotes/2022/english/htnea2022003.pdf",
        }
    ]
},
"archive/582-capability-congruence-minimum-viable-jurisdiction-intermunicipal-backstops-and-no-subsidiarity-by-fiction.md": {
    "groups": [
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-for-local-self-government-english-version-pdf-a6-59-p/16807198a3",
        },
        {
            "title": "Enabling Inter-Municipal Shared Service Provision in Lithuania",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/enabling-inter-municipal-shared-service-provision-in-lithuania_f8ad6859-en.html",
        },
        {
            "title": "Inter-municipal co-operation in the Western Balkans",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/inter-municipal-co-operation-in-the-western-balkans_a78a01e6-en.html",
        },
        {
            "title": "Building More Competitive Regions in Slovenia",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/building-more-competitive-regions-in-slovenia_7dd44220-en.html",
        },
        {
            "title": "Strengthening multi-level governance for island development",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/policy-pathways-beyond-the-shoreline_1aedeacb-en/full-report/strengthening-multi-level-governance-for-island-development_586bd0e2.html",
        }
    ]
},
"archive/581-mandate-finance-congruence-unfunded-mandates-vertical-fiscal-imbalance-and-no-decentralization-by-fiscal-theater.md": {
    "groups": [
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-for-local-self-government-english-version-pdf-a6-59-p/16807198a3",
        },
        {
            "title": "Place-Based Policies for the Future",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/place-based-policies-for-the-future_e5ff6716-en.html",
        },
        {
            "title": "Subnational finance and investment",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/topics/subnational-finance-and-investment.html",
        },
        {
            "title": "Fiscal federalism network",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/topics/fiscal-federalism-network.html",
        },
        {
            "title": "OECD Fiscal Decentralisation Database",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/data/datasets/oecd-fiscal-decentralisation-database.html",
        },
        {
            "title": "Intergovernmental fiscal transfers and fiscal equalisation in a time of consolidation",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/intergovernmental-fiscal-transfers-and-fiscal-equalisation-in-a-time-of-consolidation_4853a4d0-en.html",
        }
    ]
},
"archive/580-asymmetric-decentralization-special-status-territories-and-no-one-size-fits-all-stack.md": {
    "groups": [
        {
            "title": "Asymmetric decentralisation: Trends, challenges and policy implications",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/asymmetric-decentralisation_0898887a-en.html",
        },
        {
            "title": "Decentralisation",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/topics/decentralisation.html",
        },
        {
            "title": "Regional Governance in OECD Countries: Trends, Typology and Tools",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/regional-governance-in-oecd-countries_4d7c6483-en.html",
        },
        {
            "title": "OECD Regional Outlook 2019",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/oecd-regional-outlook-2019_9789264312838-en.html",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-for-local-self-government-english-version-pdf-a6-59-p/16807198a3",
        }
    ]
},
"archive/579-scope-allocation-by-level-intimacy-spillovers-coercion-solidarity-infrastructure-commons-and-no-government-by-level-confusion.md": {
    "groups": [
        {
            "title": "The principle of subsidiarity",
            "publisher": "EUR-Lex / European Union",
            "url": "https://eur-lex.europa.eu/EN/legal-content/summary/the-principle-of-subsidiarity.html",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-for-local-self-government-english-version-pdf-a6-59-p/16807198a3",
        },
        {
            "title": "The OECD Metropolitan Governance Survey",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/the-oecd-metropolitan-governance-survey_5jz43zldh08p-en.html",
        },
        {
            "title": "Five years of the OECD Principles on Urban Policy",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/five-years-of-the-oecd-principles-on-urban-policy_e1104359-en.html",
        },
        {
            "title": "Global State of National Urban Policy 2024",
            "publisher": "OECD / UN-Habitat",
            "url": "https://www.oecd.org/en/publications/global-state-of-national-urban-policy-2024_4db6994c-en.html",
        },
        {
            "title": "Toolkit to Strengthen Multi-Level Governance in Crisis-Affected Settings",
            "publisher": "UNDP",
            "url": "https://www.undp.org/sites/g/files/zskgke326/files/2025-09/undp-toolkit-to-strengthen-multi-level_governance-in-crisis-affected_settings.pdf",
        }
    ]
},
"archive/578-open-data-and-public-information-reuse-by-scope-community-scrutiny-municipal-publishing-regional-aggregation-national-standards-and-no-government-by-pdf-fog.md": {
    "groups": [
        {
            "title": "Government at a Glance 2025 — Transparency of public information",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/government-at-a-glance-2025_0efd0bcd-en/full-report/transparency-of-public-information_60a963c4.html",
        },
        {
            "title": "Recommendation of the Council on Open Government",
            "publisher": "OECD Legal Instruments",
            "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0438",
        },
        {
            "title": "Recommendation of the Council on Enhancing Access to and Sharing of Data",
            "publisher": "OECD Legal Instruments",
            "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0463",
        },
        {
            "title": "Directive (EU) 2019/1024 on open data and the re-use of public sector information",
            "publisher": "EUR-Lex / European Union",
            "url": "https://eur-lex.europa.eu/eli/dir/2019/1024/oj/eng",
        },
        {
            "title": "Commission Implementing Regulation (EU) 2023/138",
            "publisher": "EUR-Lex / European Union",
            "url": "https://eur-lex.europa.eu/eli/reg_impl/2023/138/oj/eng",
        },
        {
            "title": "Open Government",
            "publisher": "Data.gov",
            "url": "https://data.gov/open-gov/",
        },
        {
            "title": "Introducing DCAT-AP for high-value datasets: Enhancing data accessibility across Europe",
            "publisher": "data.europa.eu",
            "url": "https://data.europa.eu/en/news-events/news/introducing-dcat-ap-high-value-datasets-enhancing-data-accessibility-across-europe",
        }
    ]
},
"archive/577-public-service-delivery-one-stop-shops-and-assisted-digital-access-by-scope-community-navigation-municipal-front-counters-regional-shared-service-centers-national-service-standards-and-no-government-by-channel-maze.md": {
    "groups": [
        {
            "title": "Recommendation of the Council on Human-Centred Public Administrative Services",
            "publisher": "OECD Legal Instruments",
            "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0503",
        },
        {
            "title": "Government at a Glance 2025 — Seamless and accessible public administrative services",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/government-at-a-glance-2025_0efd0bcd-en/full-report/seamless-and-accessible-public-administrative-services_3dae4bc2.html",
        },
        {
            "title": "One-Stop Shops for Citizens and Business",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/one-stop-shops-for-citizens-and-business_b0b0924e-en.html",
        },
        {
            "title": "Achieving Integrated Government-to-Business Service Delivery: A Planning Guide for Reformers",
            "publisher": "World Bank Group",
            "url": "https://documents1.worldbank.org/curated/en/229401604053492832/pdf/Achieving-Integrated-Government-to-Business-Service-Delivery-A-Planning-Guide-for-Reformers.pdf",
        },
        {
            "title": "Regulation (EU) 2018/1724 establishing a single digital gateway",
            "publisher": "EUR-Lex / European Union",
            "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX%3A02018R1724-20250119",
        }
    ]
},
"archive/576-base-registries-identifiers-reference-data-and-interoperability-by-scope-community-error-surfacing-municipal-data-stewardship-regional-brokers-national-authoritative-sources-and-no-government-by-contradictory-copies.md": {
    "groups": [
        {
            "title": "European Interoperability Framework – Implementation Strategy",
            "publisher": "EUR-Lex / European Commission",
            "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX%3A52017DC0134",
        },
        {
            "title": "Good Practices on Building Successful Interconnections of Base Registries",
            "publisher": "European Commission",
            "url": "https://ec.europa.eu/isa2/sites/isa/files/publications/access-to-base-registries-good-practices-on-building-successful-interconnections-of-base-registries.pdf",
        },
        {
            "title": "Europe's Single Digital Gateway / Once-Only Technical System",
            "publisher": "European Commission",
            "url": "https://ec.europa.eu/digital-building-blocks/sites/pages/viewpage.action?pageId=712508269",
        },
        {
            "title": "The OECD Digital Government Policy Framework",
            "publisher": "OECD",
            "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2020/10/the-oecd-digital-government-policy-framework_11dd6aa8/f64fed2a-en.pdf",
        },
        {
            "title": "Guidelines on the Use of Registers and Administrative Data for Population and Housing Censuses",
            "publisher": "UNECE",
            "url": "https://unece.org/guidelines-use-registers-and-administrative-data-population-and-housing-censuses-0",
        },
        {
            "title": "Future Company Registers",
            "publisher": "World Bank",
            "url": "https://documents1.worldbank.org/curated/en/099435008302231899/pdf/P17553401702c10490be6e02112bae75050.pdf",
        },
    ]
},
"archive/575-official-notice-service-and-proof-of-delivery-by-scope-community-contact-municipal-address-for-service-regional-coordination-national-effect-rules-and-no-government-by-presumed-receipt.md": {
    "groups": [
        {
            "title": "Recommendation CM/Rec(2007)7 on good administration",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/cmrec-2007-7-of-the-cm-to-ms-on-good-administration/16809f007c",
        },
        {
            "title": "Code of Good Administrative Behaviour for Staff of the European Commission in their relations with the public",
            "publisher": "EUR-Lex / European Union",
            "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=OJ:L_202403083",
        },
        {
            "title": "Universal Postal Convention",
            "publisher": "Universal Postal Union",
            "url": "https://www.upu.int/UPU/media/upu/files/aboutUpu/acts/03-actsConventionAndFinalProtocol/conventionAndFinalProtocolAdoptedAtAbidjanEn.pdf",
        },
        {
            "title": "Regulation (EU) No 910/2014 on electronic identification and trust services",
            "publisher": "EUR-Lex / European Union",
            "url": "https://eur-lex.europa.eu/eli/reg/2014/910/oj/eng",
        },
        {
            "title": "Good Practice Principles for Public Service Design and Delivery in the Digital Age",
            "publisher": "OECD",
            "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2022/11/oecd-good-practice-principles-for-public-service-design-and-delivery-in-the-digital-age_f3845ec3/2ade500b-en.pdf",
        },
        {
            "title": "Convention of 15 November 1965 on the Service Abroad of Judicial and Extrajudicial Documents in Civil or Commercial Matters",
            "publisher": "HCCH",
            "url": "https://www.hcch.net/en/instruments/conventions/full-text/?cid=17",
        },
    ]
},
"archive/574-electronic-identification-signatures-seals-and-document-authentication-by-scope-community-attestation-municipal-enrollment-regional-federation-national-trust-frameworks-and-no-government-by-unverifiable-file.md": {
    "groups": [
        {
            "title": "Recommendation of the Council on the Governance of Digital Identity",
            "publisher": "OECD Legal Instruments",
            "url": "https://legalinstruments.oecd.org/en/instruments/%E2%80%8COECD-LEGAL-0491",
        },
        {
            "title": "Regulation (EU) No 910/2014 on electronic identification and trust services",
            "publisher": "EUR-Lex / European Union",
            "url": "https://eur-lex.europa.eu/eli/reg/2014/910/2024-10-18/eng",
        },
        {
            "title": "SP 800-63-4 Digital Identity Guidelines",
            "publisher": "NIST",
            "url": "https://csrc.nist.gov/pubs/sp/800/63/4/final",
        },
        {
            "title": "FIPS 201-3 Personal Identity Verification (PIV) of Federal Employees and Contractors",
            "publisher": "NIST",
            "url": "https://pages.nist.gov/FIPS201/FIPS201.html",
        },
        {
            "title": "Apostille Section",
            "publisher": "HCCH",
            "url": "https://www.hcch.net/en/instruments/conventions/specialised-sections/apostille",
        },
        {
            "title": "Model Law on the Use and Cross-border Recognition of Identity Management and Trust Services (2022)",
            "publisher": "UNCITRAL",
            "url": "https://uncitral.un.org/en/mlit",
        },
    ]
},
"archive/573-administrative-procedure-permits-and-licenses-by-scope-community-witnessing-municipal-front-doors-regional-technical-review-national-procedure-codes-and-no-government-by-permit-maze.md": {
    "groups": [
        {
            "title": "Licensing and Permitting",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/licensing-and-permitting_68fc3301-en.html",
        },
        {
            "title": "Recommendation of the Council on Regulatory Policy and Governance",
            "publisher": "OECD Legal Instruments",
            "url": "https://legalinstruments.oecd.org/public/doc/273/273.en.pdf",
        },
        {
            "title": "Recommendation CM/Rec(2007)7 on good administration",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/cmrec-2007-7-of-the-cm-to-ms-on-good-administration/16809f007c",
        },
        {
            "title": "Charter of Fundamental Rights of the European Union — Article 41 Right to good administration",
            "publisher": "EUR-Lex / European Union",
            "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX%3A12012P%2FTXT",
        },
        {
            "title": "Regulation (EU) 2018/1724 establishing a single digital gateway",
            "publisher": "EUR-Lex / European Union",
            "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX%3A02018R1724-20250119",
        },
        {
            "title": "Business Ready 2026 Methodology Handbook",
            "publisher": "World Bank",
            "url": "https://thedocs.worldbank.org/en/doc/6364c306d685203c859c60a075df5c3a-0540012026/original/B-READY-MH-2026.pdf",
        },
    ]
},
"archive/572-standards-metrology-testing-accreditation-and-conformity-assessment-by-scope-community-witnessing-municipal-inspection-regional-labs-national-quality-infrastructure-and-no-government-by-unverified-measurement.md": {
    "groups": [
        {
            "title": "Quality Infrastructure",
            "publisher": "World Bank",
            "url": "https://www.worldbank.org/en/topic/competitiveness/brief/qi",
        },
        {
            "title": "Reinforcing Regulatory Frameworks through Standards, Measurements and Assurance",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/reinforcing-regulatory-frameworks-through-standards-measurements-and-assurance_f398be90-en.html",
        },
        {
            "title": "The SI",
            "publisher": "BIPM",
            "url": "https://www.bipm.org/en/measurement-units",
        },
        {
            "title": "CIPM MRA",
            "publisher": "BIPM",
            "url": "https://www.bipm.org/en/cipm-mra",
        },
        {
            "title": "What is legal metrology?",
            "publisher": "OIML",
            "url": "https://www.oiml.org/en/about/legal-metrology",
        },
        {
            "title": "Technical Barriers to Trade",
            "publisher": "WTO",
            "url": "https://wto.org/tbt",
        },
        {
            "title": "ILAC MRA and Signatories",
            "publisher": "ILAC",
            "url": "https://ilac.org/ilac-mra-and-signatories/",
        },
        {
            "title": "MLA Purpose",
            "publisher": "IAF",
            "url": "https://iaf.nu/en/mla-purpose/",
        },
    ]
},
"archive/571-public-records-archives-and-official-publications-by-scope-community-memory-municipal-record-discipline-regional-repositories-national-gazettes-and-no-government-by-disappearing-state.md": {
    "groups": [
        {
            "title": "Universal Declaration on Archives",
            "publisher": "International Council on Archives",
            "url": "https://www.ica.org/resource/universal-declaration-on-archives-uda/",
        },
        {
            "title": "Federal Records Management and the Public",
            "publisher": "U.S. National Archives and Records Administration",
            "url": "https://www.archives.gov/records-mgmt/public",
        },
        {
            "title": "Tromsø Convention",
            "publisher": "Council of Europe",
            "url": "https://www.coe.int/en/web/access-to-official-documents",
        },
        {
            "title": "About the Official Journal",
            "publisher": "Publications Office of the European Union / EUR-Lex",
            "url": "https://eur-lex.europa.eu/content/help/oj/about-oj.html",
        },
        {
            "title": "About the National Archives of the United States",
            "publisher": "U.S. National Archives and Records Administration",
            "url": "https://www.archives.gov/publications/general-info-leaflets/1-about-archives.html",
        },
        {
            "title": "Memory of the World",
            "publisher": "UNESCO",
            "url": "https://www.unesco.org/en/memory-world",
        },
    ]
},
"archive/570-legal-entity-business-and-beneficial-ownership-registries-by-scope-community-witnessing-municipal-entry-desks-regional-coordination-national-public-truth-and-no-government-by-paper-shell.md": {
    "groups": [
        {
            "title": "Business registration pillars",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/business-regulation-pillars_971154c7-en.html",
        },
        {
            "title": "Business Ready 2025",
            "publisher": "World Bank",
            "url": "https://www.worldbank.org/en/businessready",
        },
        {
            "title": "Business Entry",
            "publisher": "World Bank Business Ready",
            "url": "https://www.worldbank.org/en/businessready/topic/business-entry",
        },
        {
            "title": "Topic | Business Location",
            "publisher": "World Bank Business Ready",
            "url": "https://www.worldbank.org/en/businessready/topic/business-location",
        },
        {
            "title": "Guidelines on Statistical Business Registers",
            "publisher": "UNECE",
            "url": "https://unece.org/statistics/publications/guidelines-statistical-business-registers",
        },
        {
            "title": "Guidance on Beneficial Ownership of Legal Persons",
            "publisher": "FATF",
            "url": "https://www.fatf-gafi.org/en/publications/Fatfrecommendations/Guidance-Beneficial-Ownership-Legal-Persons.html",
        },
        {
            "title": "The Legal Entity Identifier (LEI)",
            "publisher": "GLEIF",
            "url": "https://www.gleif.org/en/organizational-identity/lei-vlei/the-legal-entity-identifier-lei",
        },
        {
            "title": "The Global LEI Index",
            "publisher": "GLEIF",
            "url": "https://www.gleif.org/en/organizational-identity/lei-index",
        },
        {
            "title": "Business Registers Interconnection System dashboard",
            "publisher": "European Commission",
            "url": "https://ec.europa.eu/digital-building-blocks/sites/spaces/DIGITAL/pages/210798097/Business%2BRegisters%2BInterconnection%2BSystem%2Bdashboard",
        },
    ]
},
"archive/567-public-borrowing-and-debt-by-scope-no-neighborhood-debt-municipal-capital-discipline-metro-infrastructure-national-stabilization-and-no-government-by-hidden-guarantees.md": {
    "groups": [
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-of-local-self-government-english-version-pdf-a6-59-p/16807198a3",
        },
        {
            "title": "Subnational finance and investment",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/topics/subnational-finance-and-investment.html",
        },
        {
            "title": "Insolvency Frameworks for Sub-national Governments",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/insolvency-frameworks-for-sub-national-governments_f9874122-en.html",
        },
        {
            "title": "Decentralizing Borrowing Powers",
            "publisher": "World Bank",
            "url": "https://openknowledge.worldbank.org/entities/publication/b67cd005-84c5-5649-8358-c734a6ae0572",
        },
        {
            "title": "Subnational Debt, Insolvency, and Market Development",
            "publisher": "World Bank",
            "url": "https://openknowledge.worldbank.org/entities/publication/accabe4a-a265-5852-8998-3069d4d89646",
        },
        {
            "title": "The Fiscal Transparency Code 2019",
            "publisher": "IMF",
            "url": "https://www.imf.org/external/np/fad/trans/Code2019.pdf",
        },
        {
            "title": "The Legal Foundations of Public Debt Transparency: Aligning the Law with Good Practices",
            "publisher": "IMF",
            "url": "https://www.imf.org/-/media/files/publications/wp/2024/english/wpiea2024029-print-pdf.pdf",
        },
        {
            "title": "Sovereign borrowing outlook: Global Debt Report 2026",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/global-debt-report-2026_e9d80efd-en/full-report/sovereign-borrowing-outlook_4470147b.html",
        },
    ]
},
"archive/566-electoral-systems-by-scope-direct-local-voice-municipal-proportionality-metropolitan-legitimacy-regional-balancing-national-pr-and-federal-shared-rule.md": {
    "groups": [
        {
            "title": "Electoral System Design: The New International IDEA Handbook",
            "publisher": "International IDEA",
            "url": "https://www.idea.int/publications/catalogue/electoral-system-design-new-international-idea-handbook",
        },
        {
            "title": "Electoral System Design Database",
            "publisher": "International IDEA",
            "url": "https://www.idea.int/data-tools/data/electoral-system-design-database",
        },
        {
            "title": "Code of Good Practice in Electoral Matters",
            "publisher": "Venice Commission / Council of Europe",
            "url": "https://www.venice.coe.int/webforms/documents/?pdf=CDL-AD(2002)023rev2-cor-e",
        },
        {
            "title": "Local Democracy",
            "publisher": "International IDEA",
            "url": "https://www.idea.int/publications/catalogue/local-democracy",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://edoc.coe.int/en/local-democracy/6856-charte-europenne-de-l-autonomie-locale.html",
        },
        {
            "title": "Direct Democracy: The International IDEA Handbook",
            "publisher": "International IDEA",
            "url": "https://www.idea.int/publications/catalogue/direct-democracy-international-idea-handbook",
        },
        {
            "title": "Innovative public participation",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/topics/sub-issues/open-government-and-citizen-participation/innovative-public-participation.html",
        },
        {
            "title": "Innovative Citizen Participation and New Democratic Institutions",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/innovative-citizen-participation-and-new-democratic-institutions_339306da-en.html",
        },
        {
            "title": "Citizen participation and deliberation: Government at a Glance 2025",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/government-at-a-glance-2025_0efd0bcd-en/full-report/citizen-participation-and-deliberation_52b90285.html",
        },
        {
            "title": "Bicameralism",
            "publisher": "International IDEA",
            "url": "https://www.idea.int/publications/catalogue/bicameralism",
        },
        {
            "title": "Second Chambers in Federal Systems",
            "publisher": "International IDEA",
            "url": "https://www.idea.int/publications/catalogue/second-chambers-federal-systems",
        },
        {
            "title": "Government Formation and Removal Mechanisms",
            "publisher": "International IDEA",
            "url": "https://www.idea.int/publications/catalogue/government-formation-and-removal-mechanisms",
        },
        {
            "title": "OECD Principles on Urban Policy",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/about/programmes/oecd-programme-on-national-urban-policy/oecd-principles-on-urban-policy.html",
        },
    ]
},
"archive/565-ideal-constitutional-kits-by-scope-neighborhood-voice-municipal-councils-metropolitan-democracy-regional-federal-capacity-national-solidarity-continental-compacts-and-global-narrow-waists.md": {
    "groups": [
        {
            "title": "The principle of subsidiarity",
            "publisher": "EUR-Lex / European Union",
            "url": "https://eur-lex.europa.eu/EN/legal-content/glossary/principle-of-subsidiarity.html",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://www.coe.int/en/web/impact-convention-human-rights/european-charter-of-local-self-government",
        },
        {
            "title": "International Guidelines on Decentralization and Access to Basic Services for All",
            "publisher": "UN-Habitat",
            "url": "https://unhabitat.org/international-guidelines-on-decentralization-and-access-to-basic-services-for-all",
        },
        {
            "title": "OECD Principles on Urban Policy",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/about/programmes/oecd-programme-on-national-urban-policy/oecd-principles-on-urban-policy.html",
        },
        {
            "title": "What Makes Cities More Productive? Evidence on the Role of Urban Governance from Five OECD Countries",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/what-makes-cities-more-productive-evidence-on-the-role-of-urban-governance-from-five-oecd-countries_5jz432cf2d8p-en.html",
        },
        {
            "title": "OECD Guidelines for Citizen Participation Processes",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/oecd-guidelines-for-citizen-participation-processes_f765caf6-en.html",
        },
        {
            "title": "Innovative Citizen Participation and New Democratic Institutions",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/innovative-citizen-participation-and-new-democratic-institutions_339306da-en.html",
        },
        {
            "title": "The Paris Agreement",
            "publisher": "UNFCCC",
            "url": "https://unfccc.int/process-and-meetings/the-paris-agreement",
        },
        {
            "title": "International health regulations",
            "publisher": "WHO",
            "url": "https://www.who.int/health-topics/international-health-regulations",
        },
        {
            "title": "BBNJ Agreement status",
            "publisher": "United Nations Treaty Collection",
            "url": "https://treaties.un.org/Pages/ViewDetails.aspx?chapter=21&clang=_en&mtdsg_no=XXI-10&src=TREATY",
        },
    ]
},
"archive/564-anti-corruption-bodies-and-integrity-commissions-by-scope-local-routing-regional-case-development-national-specialization-and-no-government-by-heroic-commission.md": {
    "groups": [
        {
            "title": "Anti-corruption agencies and commissions",
            "publisher": "UNODC",
            "url": "https://www.unodc.org/corruption/en/learn/thematic-areas/anti-corruption-agencies-and-commissions.html",
        },
        {
            "title": "United Nations Convention against Corruption",
            "publisher": "UNODC",
            "url": "https://www.unodc.org/pdf/corruption/publications_unodc_convention-e.pdf",
        },
        {
            "title": "Jakarta Statement on Principles for Anti-Corruption Agencies",
            "publisher": "UNODC / UNDP / anti-corruption practitioners",
            "url": "https://www.unodc.org/documents/corruption/WG-Prevention/Art_6_Preventive_anti-corruption_bodies/JAKARTA_STATEMENT_en.pdf",
        },
        {
            "title": "Colombo Commentary on the Jakarta Statement on Principles for Anti-Corruption Agencies",
            "publisher": "UNODC",
            "url": "https://www.unodc.org/documents/corruption/Publications/2020/20-00107_Colombo_Commentary_Ebook.pdf",
        },
        {
            "title": "Recommendation of the Council on Public Integrity",
            "publisher": "OECD Legal Instruments",
            "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0435",
        },
        {
            "title": "Integrity and anti-corruption strategies",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/government-at-a-glance-2025_0efd0bcd-en/full-report/integrity-and-anti-corruption-strategies_9ecb07c9.html",
        },
        {
            "title": "About GRECO mutual evaluations",
            "publisher": "Council of Europe / GRECO",
            "url": "https://www.coe.int/en/web/greco/evaluations/about",
        },
        {
            "title": "About the GlobE Network",
            "publisher": "UNODC GlobE Network",
            "url": "https://globenetwork.unodc.org/globenetwork/en/about.html",
        },
    ]
},
"archive/563-public-procurement-institutions-and-review-by-scope-local-needs-regional-shared-buying-national-rules-independent-challenges-and-no-government-by-emergency-sole-source-fog.md": {
    "groups": [
        {
            "title": "Recommendation of the Council on Public Procurement",
            "publisher": "OECD Legal Instruments",
            "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0411",
        },
        {
            "title": "Implementing the OECD Recommendation on Public Procurement in OECD and Partner Countries: 2020-2024 Report",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/implementing-the-oecd-recommendation-on-public-procurement-in-oecd-and-partner-countries_02a46a58-en/full-report/implementation-of-the-oecd-recommendation-in-member-and-partner-countries_2305bb1b.html",
        },
        {
            "title": "Efficient public procurement",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/government-at-a-glance-2025_0efd0bcd-en/full-report/efficient-public-procurement_9420d708.html",
        },
        {
            "title": "Professionalisation of public procurement",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/government-at-a-glance-2025_0efd0bcd-en/full-report/professionalisation-of-public-procurement_ec3e5fa8.html",
        },
        {
            "title": "Guide to Enactment of the UNCITRAL Model Law on Public Procurement",
            "publisher": "UNCITRAL",
            "url": "https://uncitral.un.org/sites/uncitral.un.org/files/media-documents/uncitral/en/guide-enactment-model-law-public-procurement-e.pdf",
        },
        {
            "title": "Agreement on Government Procurement as Amended",
            "publisher": "WTO",
            "url": "https://www.wto.org/english/docs_e/legal_e/rev-gpr-94_01_e.htm",
        },
        {
            "title": "Project Procurement Framework",
            "publisher": "World Bank Group",
            "url": "https://www.worldbank.org/ext/en/what-we-do/project-procurement/framework",
        },
        {
            "title": "Procurement Regulations for IPF Borrowers (7th edition, September 2025)",
            "publisher": "World Bank Group",
            "url": "https://thedocs.worldbank.org/en/doc/c84273d1b230aeb2b0b8134de5dc8cd7-0290012025/original/Procurement-Regulations-7th-Edition-Sep-2025.pdf",
        },
        {
            "title": "Open Contracting Global Principles",
            "publisher": "Open Contracting Partnership",
            "url": "https://www.open-contracting.org/what-is-open-contracting/global-principles/",
        },
        {
            "title": "Open Contracting Data Standard",
            "publisher": "Open Contracting Partnership",
            "url": "https://www.open-contracting.org/data-standard/",
        },
    ]
},
"archive/562-civil-registration-vital-statistics-and-legal-identity-institutions-by-scope-local-event-capture-municipal-service-access-regional-backstops-national-trust-frameworks-and-no-government-by-documentary-erasure.md": {
    "groups": [
        {
            "title": "UN Legal Identity Agenda",
            "publisher": "UN Statistics Division",
            "url": "https://unstats.un.org/legal-identity-agenda/",
        },
        {
            "title": "Handbook on Civil Registration and Vital Statistics Systems: Management, Operation and Maintenance, Revision 1",
            "publisher": "UN Statistics Division",
            "url": "https://unstats.un.org/unsd/demographic-social/Standards-and-Methods/files/Handbooks/crvs/crvs-mgt-E.pdf",
        },
        {
            "title": "The role of unique identifiers in civil registration & vital statistics and national identification systems",
            "publisher": "UN Legal Identity Agenda",
            "url": "https://unstats.un.org/legal-identity-agenda/documents/Reports/Unique_Identifiers_in_Civil_Registration.pdf",
        },
        {
            "title": "Principles on Identification for Sustainable Development",
            "publisher": "World Bank ID4D",
            "url": "https://id4d.worldbank.org/guide/1-principles",
        },
        {
            "title": "Interoperability",
            "publisher": "World Bank ID4D",
            "url": "https://id4d.worldbank.org/guide/interoperability",
        },
        {
            "title": "Birth registration",
            "publisher": "UNICEF Data",
            "url": "https://data.unicef.org/topic/child-protection/birth-registration/",
        },
        {
            "title": "The Right Start in Life: 2024 update",
            "publisher": "UNICEF Data",
            "url": "https://data.unicef.org/resources/the-right-start-in-life-2024-update/",
        },
    ]
},
"archive/561-districting-and-boundary-commissions-by-scope-local-polling-areas-municipal-wards-regional-mapmaking-national-equal-suffrage-rules-and-no-government-by-incumbent-cartography.md": {
    "groups": [
        {
            "title": "Report on Constituency Delineation and Seat Allocation",
            "publisher": "Venice Commission",
            "url": "https://www.venice.coe.int/webforms/documents/default.aspx?pdffile=CDL-AD%282017%29034-e",
        },
        {
            "title": "Code of Good Practice in Electoral Matters",
            "publisher": "Venice Commission / Council of Europe",
            "url": "https://www.venice.coe.int/images/SITE%20IMAGES/Publications/Code_conduite_PREMS%20026115%20GBR.pdf",
        },
        {
            "title": "Electoral Boundary Delimitation",
            "publisher": "International IDEA",
            "url": "https://www.idea.int/news-media/multimedia-reports/electoral-boundary-delimitation",
        },
        {
            "title": "Designation of a Boundary Authority",
            "publisher": "ACE Electoral Knowledge Network",
            "url": "https://aceproject.org/ace-en/topics/bd/bdb/bdb01/",
        },
        {
            "title": "Human Rights and Elections",
            "publisher": "OHCHR",
            "url": "https://www.ohchr.org/sites/default/files/2022-02/Human-Rights-and-Elections.pdf",
        },
    ]
},
"archive/560-official-statistics-and-census-institutions-by-scope-local-administrative-data-discipline-regional-capacity-national-independence-and-no-government-by-partisan-numbers.md": {
    "groups": [
        {
            "title": "Fundamental Principles of Official Statistics",
            "publisher": "UN Statistics Division",
            "url": "https://unstats.un.org/fpos/",
        },
        {
            "title": "Handbook on Management and Organization of National Statistical Systems",
            "publisher": "UN Statistics Division",
            "url": "https://unstats.un.org/capacity-development/handbook/Handbook_All_2025A_202505.pdf",
        },
        {
            "title": "UN NQAF — Methodology",
            "publisher": "UN Statistics Division",
            "url": "https://unstats.un.org/unsd/methodology/dataquality/",
        },
        {
            "title": "Generic Law on Official Statistics",
            "publisher": "UNECE",
            "url": "https://unece.org/statistics/publications/generic-law-official-statistics",
        },
        {
            "title": "European Statistics Code of Practice",
            "publisher": "Eurostat",
            "url": "https://ec.europa.eu/eurostat/web/quality/european-quality-standards/european-statistics-code-of-practice",
        },
        {
            "title": "Population and housing censuses",
            "publisher": "UN Statistics Division",
            "url": "https://unstats.un.org/unsd/demographic-social/census/",
        },
        {
            "title": "Standards for Data Dissemination",
            "publisher": "IMF",
            "url": "https://www.imf.org/en/about/factsheets/sheets/2023/standards-for-data-dissemination",
        },
        {
            "title": "The Special Data Dissemination Standard: Guide for Subscribers and Users",
            "publisher": "IMF",
            "url": "https://www.imf.org/en/publications/manuals-guides/issues/2016/12/31/the-special-data-dissemination-standard-guide-for-subscribers-and-users-40363",
        },
    ]
},
"archive/559-access-to-information-and-data-protection-institutions-by-scope-local-records-help-municipal-disclosure-discipline-regional-casework-national-independence-and-no-government-by-secrecy-or-panopticon.md": {
    "groups": [
        {
            "title": "Tromsø Convention",
            "publisher": "Council of Europe",
            "url": "https://www.coe.int/en/web/access-to-official-documents",
        },
        {
            "title": "Right to Information",
            "publisher": "UNESCO",
            "url": "https://www.unesco.org/en/right-information",
        },
        {
            "title": "Oversight institutions",
            "publisher": "UNESCO",
            "url": "https://www.unesco.org/en/right-access-information/oversight-bodies",
        },
        {
            "title": "Convention 108 and Protocols",
            "publisher": "Council of Europe",
            "url": "https://www.coe.int/en/web/data-protection/convention108-and-protocol",
        },
        {
            "title": "Regulation (EU) 2016/679 — Chapter VI Independent supervisory authorities",
            "publisher": "EUR-Lex / European Union",
            "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX%3A32016R0679",
        },
        {
            "title": "Data Protection Authority & you",
            "publisher": "European Data Protection Board",
            "url": "https://www.edpb.europa.eu/sme-data-protection-guide/data-protection-authority-and-you_en",
        },
    ]
},
"archive/558-public-defense-and-legal-aid-by-scope-local-entry-municipal-navigation-regional-provider-capacity-national-independence-and-no-justice-by-unaffordable-counsel.md": {
    "groups": [
        {
            "title": "Basic Principles on the Role of Lawyers",
            "publisher": "OHCHR / UN Congress on the Prevention of Crime and the Treatment of Offenders",
            "url": "https://www.ohchr.org/en/instruments-mechanisms/instruments/basic-principles-role-lawyers",
        },
        {
            "title": "United Nations Principles and Guidelines on Access to Legal Aid in Criminal Justice Systems",
            "publisher": "UN General Assembly / UNODC",
            "url": "https://www.unodc.org/documents/justice-and-prison-reform/UN_principles_and_guidlines_on_access_to_legal_aid.pdf",
        },
        {
            "title": "Access to Legal Aid",
            "publisher": "UNODC",
            "url": "https://www.unodc.org/unodc/en/justice-and-prison-reform/legal-aid.html",
        },
        {
            "title": "Models for Governing, Administering and Funding Legal Aid",
            "publisher": "UNODC Education for Justice",
            "url": "https://www.unodc.org/e4j/en/crime-prevention-criminal-justice/module-3/key-issues/5--models-for-governing--administering-and-funding-legal-aid.html",
        },
        {
            "title": "Access to legal aid for those with specific needs",
            "publisher": "UNODC Education for Justice",
            "url": "https://www.unodc.org/e4j/en/crime-prevention-criminal-justice/module-3/key-issues/4--access-to-legal-aid-for-those-with-specific-needs.html",
        },
        {
            "title": "Legal aid",
            "publisher": "Council of Europe",
            "url": "https://www.coe.int/en/web/cdcj/activities/free-legal-aid",
        },
        {
            "title": "Legal aid in civil and administrative law: new guidelines",
            "publisher": "Council of Europe",
            "url": "https://www.coe.int/en/web/portal/-/legal-aid-in-civil-and-administrative-law-new-guidelines",
        },
        {
            "title": "Early Access to Legal Aid in Criminal Justice Processes Handbook",
            "publisher": "UNDP / UNODC / Open Society Foundations",
            "url": "https://www.undp.org/publications/early-access-legal-aid-criminal-justice-processes-handbook",
        },
        {
            "title": "Legal Aid Service Provision: A Guide to Programming in Africa",
            "publisher": "UNDP",
            "url": "https://www.undp.org/publications/legal-aid-service-provision-guide-programming-africa",
        },
    ]
},
"archive/557-detention-corrections-and-reentry-by-scope-local-contact-and-release-links-regional-custody-probation-national-rights-floors-and-no-government-by-warehousing.md": {
    "groups": [
        {
            "title": "United Nations Standard Minimum Rules for the Treatment of Prisoners (the Nelson Mandela Rules)",
            "publisher": "OHCHR / UN General Assembly",
            "url": "https://www.ohchr.org/sites/default/files/Documents/ProfessionalInterest/NelsonMandelaRules.pdf",
        },
        {
            "title": "Optional Protocol to the Convention against Torture and other Cruel, Inhuman or Degrading Treatment or Punishment",
            "publisher": "OHCHR / UN General Assembly",
            "url": "https://www.ohchr.org/en/instruments-mechanisms/instruments/optional-protocol-convention-against-torture-and-other-cruel",
        },
        {
            "title": "National Preventive Mechanisms",
            "publisher": "OHCHR",
            "url": "https://www.ohchr.org/en/treaty-bodies/spt/national-preventive-mechanisms",
        },
        {
            "title": "United Nations Standard Minimum Rules for Non-custodial Measures (The Tokyo Rules)",
            "publisher": "OHCHR / UN General Assembly",
            "url": "https://www.ohchr.org/en/instruments-mechanisms/instruments/united-nations-standard-minimum-rules-non-custodial-measures",
        },
        {
            "title": "United Nations Rules for the Treatment of Women Prisoners and Non-custodial Measures for Women Offenders",
            "publisher": "OHCHR / UN General Assembly",
            "url": "https://www.ohchr.org/en/instruments-mechanisms/instruments/united-nations-rules-treatment-women-prisoners-and-non-custodial",
        },
        {
            "title": "European Prison Rules",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/09000016809ee581",
        },
        {
            "title": "The European Probation Rules",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/16806f54e6",
        },
        {
            "title": "Organizational models of prison health: considerations for better governance",
            "publisher": "WHO Europe",
            "url": "https://www.who.int/europe/publications/i/item/WHO-EURO-2020-1268-41018-55685",
        },
        {
            "title": "The Prevention of Recidivism and the Social Reintegration of Offenders",
            "publisher": "UNODC",
            "url": "https://www.unodc.org/documents/justice-and-prison-reform/18-02303_ebook.pdf",
        },
    ]
},
"archive/556-police-services-by-scope-neighborhood-legibility-municipal-or-county-operations-metropolitan-serious-crime-bureaus-national-standards-and-no-police-self-investigation.md": {
    "groups": [
        {
            "title": "Code of Conduct for Law Enforcement Officials",
            "publisher": "OHCHR / UN General Assembly",
            "url": "https://www.ohchr.org/en/instruments-mechanisms/instruments/code-conduct-law-enforcement-officials",
        },
        {
            "title": "Basic Principles on the Use of Force and Firearms by Law Enforcement Officials",
            "publisher": "OHCHR",
            "url": "https://www.ohchr.org/en/instruments-mechanisms/instruments/basic-principles-use-force-and-firearms-law-enforcement",
        },
        {
            "title": "Police oversight mechanisms in the Council of Europe member states",
            "publisher": "Council of Europe",
            "url": "https://edoc.coe.int/en/international-law/7414-police-oversight-mechanisms-in-the-council-of-europe-member-states.html",
        },
        {
            "title": "Crime Prevention & Criminal Justice Module 5 Key Issues: Key mechanisms and actors in police accountability and oversight",
            "publisher": "UNODC",
            "url": "https://www.unodc.org/e4j/en/crime-prevention-criminal-justice/module-5/key-issues/2--key-mechanisms-and-actors-in-police-accountability-and-oversight.html",
        },
        {
            "title": "Community-oriented policing",
            "publisher": "United Nations Police",
            "url": "https://police.un.org/en/community-oriented-policing",
        },
        {
            "title": "Chapter 4: Law Enforcement and Democratic Policing",
            "publisher": "OHCHR",
            "url": "https://www.ohchr.org/sites/default/files/documents/publications/professional-training/manual-hr-for-law-enforcement-officials-ch4.pdf",
        },
        {
            "title": "Guidebook on Democratic Policing",
            "publisher": "OSCE",
            "url": "https://www.osce.org/spmu/23804",
        },
    ]
},
"archive/555-independent-human-rights-and-equality-institutions-by-scope-local-access-regional-reach-national-paris-principles-cores-and-no-government-by-self-certified-rights-compliance.md": {
    "groups": [
        {
            "title": "Principles relating to the Status of National Institutions (The Paris Principles)",
            "publisher": "OHCHR / UN General Assembly",
            "url": "https://www.ohchr.org/en/instruments-mechanisms/instruments/principles-relating-status-national-institutions-paris",
        },
        {
            "title": "Indicator 16.a.1 metadata: Existence of independent National Human Rights Institutions in compliance with the Paris Principles",
            "publisher": "OHCHR",
            "url": "https://www.ohchr.org/sites/default/files/Documents/Issues/HRIndicators/MetadataNHRIAccreditation.pdf",
        },
        {
            "title": "Recommendation CM/Rec(2021)1 on the development and strengthening of effective, pluralist and independent national human rights institutions",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/0900001680a1f4da",
        },
        {
            "title": "National institutions for the promotion and protection of human rights",
            "publisher": "Council of Europe Commissioner for Human Rights",
            "url": "https://rm.coe.int/168066d07a",
        },
        {
            "title": "ECRI General Policy Recommendation No. 2 on Equality Bodies to combat racism and intolerance at national level",
            "publisher": "ECRI / Council of Europe",
            "url": "https://hudoc.ecri.coe.int/eng?i=REC-02rev-2018-006-ENG",
        },
    ]
},
    "archive/554-ombuds-institutions-by-scope-frontline-complaint-entry-municipal-redress-regional-coordination-national-independence-and-no-government-by-unanswered-grievance.md": {
        "groups": [
            {
                "title": "Principles on the Protection and Promotion of the Ombudsman Institution (The Venice Principles)",
                "publisher": "Venice Commission / Council of Europe",
                "url": "https://www.venice.coe.int/webforms/documents/?pdf=CDL-AD%282019%29005-e",
            },
            {
                "title": "Recommendation CM/Rec(2019)6 on the development of the Ombudsman institution",
                "publisher": "Council of Europe",
                "url": "https://rm.coe.int/090000168098392f",
            },
            {
                "title": "Appendix I to Recommendation on the development of the Ombudsman institution",
                "publisher": "Council of Europe",
                "url": "https://rm.coe.int/appendix-i-to-recommendation-including-illustrative-examples-establish/168094fcc2",
            },
            {
                "title": "The role of Ombudsman Institutions in Open Government",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/publications/the-role-of-ombudsman-institutions-in-open-government_7353965f-en.html",
            },
            {
                "title": "Administrative justice as the interface between people and institutions",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/publications/making-justice-systems-more-effective-and-people-centred_e02fd90b-en/full-report/administrative-justice-as-the-interface-between-people-and-institutions_88464c56.html",
            },
        ]
    },
    "archive/553-supreme-audit-institutions-and-external-public-audit-by-scope-local-books-regional-state-audit-national-independence-and-no-government-by-self-audit.md": {
        "groups": [
            {
                "title": "Independence of Supreme Audit Institutions",
                "publisher": "INTOSAI",
                "url": "https://www.intosai.org/focus-areas/independence.html",
            },
            {
                "title": "Declaration of Lima",
                "publisher": "INTOSAI",
                "url": "https://www.intosai.org/fileadmin/downloads/documents/open_access/INT_P_1_u_P_10/INTOSAI_P_1_en_2019.pdf",
            },
            {
                "title": "PEFA's Seven Pillars",
                "publisher": "PEFA",
                "url": "https://www.pefa.org/resources",
            },
            {
                "title": "PI-30. External audit",
                "publisher": "PEFA",
                "url": "https://www.pefa.org/node/4930",
            },
            {
                "title": "PI-31. Legislative scrutiny of audit reports",
                "publisher": "PEFA",
                "url": "https://www.pefa.org/node/4915",
            },
            {
                "title": "Increasing the impact of supreme audit institutions through external engagement",
                "publisher": "SIGMA / OECD",
                "url": "https://www.oecd.org/gov/increasing-the-impact-of-supreme-audit-institutions-through-external-engagement-5d25341e-en.htm",
            },
            {
                "title": "Fundamental Principles of Public-Sector Auditing (ISSAI 100)",
                "publisher": "INTOSAI / ISSAI",
                "url": "https://www.issai.org/pronouncements/issai-100-fundamental-principles-of-public-sector-auditing/",
            },
        ]
    },
    "archive/552-electoral-administration-by-scope-local-voter-service-municipal-operations-regional-tabulation-national-standards-and-no-government-by-partisan-referee.md": {
        "groups": [
            {
                "title": "Electoral Processes",
                "publisher": "International IDEA",
                "url": "https://www.idea.int/theme/electoral-processes",
            },
            {
                "title": "Independence in Electoral Management",
                "publisher": "International IDEA",
                "url": "https://www.idea.int/sites/default/files/publications/independence-in-electoral-management.pdf",
            },
            {
                "title": "Code of Good Practice in Electoral Matters",
                "publisher": "Venice Commission / Council of Europe",
                "url": "https://www.venice.coe.int/files/Code%20de%20conduite_GBR%202025_WEB_A5.pdf",
            },
            {
                "title": "Report on Constituency Delineation and Seat Allocation",
                "publisher": "Venice Commission / Council of Europe",
                "url": "https://www.venice.coe.int/webforms/documents/default.aspx?pdffile=CDL-AD%282017%29034-e",
            },
            {
                "title": "Human Rights and Elections",
                "publisher": "OHCHR",
                "url": "https://www.ohchr.org/Documents/Publications/Human-Rights-and-Elections.pdf",
            },
            {
                "title": "Handbook for the Observation of Election Dispute Resolution",
                "publisher": "OSCE/ODIHR",
                "url": "https://odihr.osce.org/sites/default/files/f/documents/9/7/429566_0.pdf",
            },
        ]
    },
    "archive/551-public-prosecution-by-scope-local-diversion-regional-ordinary-charging-national-integrity-cases-and-no-government-by-prosecutor.md": {
        "groups": [
            {
                "title": "Guidelines on the Role of Prosecutors",
                "publisher": "OHCHR",
                "url": "https://www.ohchr.org/en/instruments-mechanisms/instruments/guidelines-role-prosecutors",
            },
            {
                "title": "Recommendation Rec(2000)19 on the role of public prosecution in the criminal justice system",
                "publisher": "Council of Europe",
                "url": "https://search.coe.int/cm?i=09000016804be55a",
            },
            {
                "title": "Recommendation CM/Rec(2012)11 on the role of public prosecutors outside the criminal justice system",
                "publisher": "Council of Europe",
                "url": "https://rm.coe.int/16807096c5",
            },
            {
                "title": "Independence, accountability and ethics of prosecutors",
                "publisher": "Consultative Council of European Prosecutors / Council of Europe",
                "url": "https://rm.coe.int/opinion-13-ccpe-2018-2e-independence-accountability-and-ethics-of-pros/1680907e9d",
            },
            {
                "title": "Report on European Standards as regards the Independence of the Judicial System: Part II - the Prosecution Service",
                "publisher": "Venice Commission / Council of Europe",
                "url": "https://www.venice.coe.int/webforms/documents/CDL-AD%282010%29040.aspx",
            },
            {
                "title": "The Status and Role of Prosecutors: A United Nations Office on Drugs and Crime and International Association of Prosecutors Guide",
                "publisher": "UNODC",
                "url": "https://www.unodc.org/documents/justice-and-prison-reform/HB_role_and_status_prosecutors_14-05222_Ebook.pdf",
            },
        ]
    },
    "archive/550-judiciaries-by-scope-neighborhood-entry-regional-trial-courts-national-apex-review-and-global-rights-backstops.md": {
        "groups": [
            {
                "title": "Basic Principles on the Independence of the Judiciary",
                "publisher": "OHCHR",
                "url": "https://www.ohchr.org/en/instruments-mechanisms/instruments/basic-principles-independence-judiciary",
            },
            {
                "title": "Judicial independence and impartiality",
                "publisher": "Council of Europe",
                "url": "https://www.coe.int/en/web/cdcj/judicial-independence-and-impartiality",
            },
            {
                "title": "Quality of justice",
                "publisher": "CEPEJ / Council of Europe",
                "url": "https://www.coe.int/en/web/cepej/cepej-work/quality-of-justice",
            },
            {
                "title": "Judicial Appointments",
                "publisher": "International IDEA",
                "url": "https://www.idea.int/publications/catalogue/judicial-appointments",
            },
            {
                "title": "Judicial Tenure, Removal, Immunity and Accountability",
                "publisher": "International IDEA",
                "url": "https://www.idea.int/publications/catalogue/judicial-tenure-removal-immunity-and-accountability",
            },
            {
                "title": "Courts in Federal Countries",
                "publisher": "International IDEA",
                "url": "https://www.idea.int/sites/default/files/publications/courts-in-federal-countries.pdf",
            },
            {
                "title": "The Fundamentals of Constitutional Courts",
                "publisher": "International IDEA",
                "url": "https://www.idea.int/publications/catalogue/fundamentals-constitutional-courts",
            },
            {
                "title": "Data and Analytics (JUPITER)",
                "publisher": "World Bank",
                "url": "https://www.worldbank.org/en/programs/global-program-on-justice-and-rule-of-law/data-and-analytics",
            },
        ]
    },
    "archive/549-civil-service-and-public-workforce-merit-neutrality-capability-fair-pay-and-no-government-by-patronage.md": {
        "groups": [
            {
                "title": "Recommendation of the Council on Public Service Leadership and Capability",
                "publisher": "OECD",
                "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0445",
            },
            {
                "title": "The Principles of Public Administration (2023 edition)",
                "publisher": "SIGMA / OECD / European Union",
                "url": "https://www.sigmaweb.org/publications/the-principles-of-public-administration-2023.htm",
            },
            {
                "title": "Public Workforce Performance and Prosperity",
                "publisher": "World Bank",
                "url": "https://www.worldbank.org/en/publication/public-workforce-performance-and-prosperity",
            },
            {
                "title": "Pay, working conditions and remote working arrangements: Workforce Insights from Central Governments",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/publications/workforce-insights-from-central-governments_2f9080b1-en/full-report/pay-working-conditions-and-remote-working-arrangements_1b18ae6b.html",
            },
            {
                "title": "Collective bargaining and labour relations",
                "publisher": "International Labour Organization",
                "url": "https://www.ilo.org/topics-and-sectors/collective-bargaining-and-labour-relations",
            },
        ]
    },
    "archive/548-legislatures-by-scope-neighborhood-assemblies-municipal-councils-metro-chambers-federal-shared-rule-and-no-government-by-decree.md": {
        "groups": [
            {
                "title": "European Charter of Local Self-Government",
                "publisher": "Council of Europe",
                "url": "https://rm.coe.int/european-charter-for-local-self-government-english-version-pdf-a6-59-p/16807198a3",
            },
            {
                "title": "Quality Budget Institutions — Effective budget oversight",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/publications/quality-budget-institutions_8e811202-en/full-report/effective-budget-oversight_4d58ff32.html",
            },
            {
                "title": "The Role of Parliament in Delegated Legislation: Principles for Safeguarding Legislative Transparency and Democratic Accountability",
                "publisher": "International IDEA",
                "url": "https://www.idea.int/sites/default/files/2026-02/role-of-parliament-in-delegated-legislation.pdf",
            },
            {
                "title": "Bicameralism",
                "publisher": "International IDEA",
                "url": "https://www.idea.int/sites/default/files/publications/bicameralism-primer.pdf",
            },
            {
                "title": "Guidelines on Democratic Lawmaking for Better Laws",
                "publisher": "OSCE/ODIHR",
                "url": "https://cdn.osce.org/sites/default/files/f/documents/a/3/558321_3.pdf",
            },
            {
                "title": "CPA Benchmarks for Democratic Legislatures (overview)",
                "publisher": "Commonwealth Parliamentary Association",
                "url": "https://www.cpahq.org/what-we-do/benchmarking/what-are-the-benchmarks/",
            },
        ]
    },
    "archive/547-budgeting-treasury-and-public-accounts-credible-ceilings-legislative-authority-one-treasury-and-no-government-by-fund-fog.md": {
        "groups": [
            {
                "title": "Recommendation of the Council on Budgetary Governance",
                "publisher": "OECD",
                "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0410/",
            },
            {
                "title": "Quality Budget Institutions",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/publications/quality-budget-institutions_8e811202-en/full-report.html",
            },
            {
                "title": "Best Practices for Parliaments in Budgeting",
                "publisher": "OECD",
                "url": "https://one.oecd.org/document/GOV/SBO%282022%293/en/pdf",
            },
            {
                "title": "Fiscal Transparency Evaluation",
                "publisher": "IMF",
                "url": "https://www.imf.org/en/topics/fiscal-policies/fiscal-transparency",
            },
            {
                "title": "Treasury Single Account: Concept, Design and Implementation Issues",
                "publisher": "IMF",
                "url": "https://www.imf.org/en/publications/wp/issues/2016/12/31/treasury-single-account-concept-design-and-implementation-issues-23927",
            },
            {
                "title": "PEFA resources and seven pillars",
                "publisher": "PEFA",
                "url": "https://www.pefa.org/resources",
            },
        ]
    },
    "archive/546-public-enterprises-and-state-owned-enterprises-explicit-rationales-separated-roles-hard-budget-constraints-and-open-books.md": {
        "groups": [
            {
                "title": "Corporate governance of state-owned enterprises",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/topics/corporate-governance-of-state-owned-enterprises.html",
            },
            {
                "title": "Ownership and Governance of State-Owned Enterprises 2024",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/publications/ownership-and-governance-of-state-owned-enterprises-2024_395c9956-en.html",
            },
            {
                "title": "Competitive Neutrality Toolkit",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/publications/competitive-neutrality-toolkit_3247ba44-en.html",
            },
            {
                "title": "Managing Fiscal Risks from State-Owned Enterprises",
                "publisher": "IMF",
                "url": "https://www.imf.org/en/publications/wp/issues/2020/09/25/managing-fiscal-risks-from-state-owned-enterprises-49773",
            },
            {
                "title": "The Fiscal Transparency Code 2019",
                "publisher": "IMF",
                "url": "https://www.imf.org/external/np/fad/trans/Code2019.pdf",
            },
            {
                "title": "Public Reporting on State-Owned Enterprises",
                "publisher": "World Bank",
                "url": "https://documents.worldbank.org/en/publication/documents-reports/documentdetail/099618010192225944",
            },
        ]
    },
    "archive/545-regulators-inspections-and-enforcement-role-clarity-risk-based-proportionality-due-process-and-no-government-by-shakedown.md": {
        "groups": [
            {
                "title": "The Governance of Regulators",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/publications/the-governance-of-regulators_24151440.html",
            },
            {
                "title": "OECD Regulatory Enforcement and Inspections Toolkit",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/publications/oecd-regulatory-enforcement-and-inspections-toolkit_9789264303959-en.html",
            },
            {
                "title": "Regulatory delivery",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/topics/regulatory-delivery.html",
            },
            {
                "title": "The administration and you – A handbook",
                "publisher": "Council of Europe",
                "url": "https://www.coe.int/en/web/cdcj/-/the-administration-and-you-a-handbook",
            },
            {
                "title": "The administration and you – A handbook (3rd edition)",
                "publisher": "Council of Europe Publishing",
                "url": "https://book.coe.int/en/international-law/11916-the-administration-and-you-a-handbook-3rd-edition.html",
            },
        ]
    },
    "archive/544-delegated-public-functions-contractors-concessions-nonprofits-and-platforms-cannot-be-constitutional-escape-hatches.md": {
        "groups": [
            {
                "title": "Recommendation of the Council on Principles for Public Governance of Public-Private Partnerships",
                "publisher": "OECD",
                "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0349",
            },
            {
                "title": "PPP Online Reference Guide",
                "publisher": "World Bank",
                "url": "https://ppp.worldbank.org/PPP_Online_Reference_Guide",
            },
            {
                "title": "Public Financial Management Frameworks for PPPs",
                "publisher": "World Bank",
                "url": "https://ppp.worldbank.org/public-financial-management-frameworks-ppps",
            },
            {
                "title": "Key Characteristics of the State Duty to Protect",
                "publisher": "OHCHR",
                "url": "https://www.ohchr.org/Documents/Issues/Business/B-Tech/b-tech-foundational-paper-state-duty-to-protect.pdf",
            },
            {
                "title": "Making public procurement transparent at local and regional levels",
                "publisher": "Council of Europe",
                "url": "https://rm.coe.int/making-public-procurement-transparent-at-local-and-regional-levels/1680932035",
            },
            {
                "title": "Frequently asked questions on a human rights-based approach to development cooperation",
                "publisher": "OHCHR",
                "url": "https://www.ohchr.org/sites/default/files/Documents/Publications/FAQen.pdf",
            },
        ]
    },
    "archive/543-special-purpose-authorities-and-arms-length-bodies-narrow-remits-hard-charters-open-books-and-sunset-review.md": {
        "groups": [
            {
                "title": "Organisation of public administration: agency governance, autonomy and accountability",
                "publisher": "OECD",
                "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2021/10/organisation-of-public-administration-agency-governance-autonomy-and-accountability_054558d8/07316cc3-en.pdf",
            },
            {
                "title": "OECD Guidelines on Corporate Governance of State-Owned Enterprises 2024",
                "publisher": "OECD",
                "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2024/06/oecd-guidelines-on-corporate-governance-of-state-owned-enterprises-2024_68fa05cd/18a24f43-en.pdf",
            },
            {
                "title": "Targeting an effective scale of policy action in all cities",
                "publisher": "OECD",
                "url": "https://www.oecd.org/content/dam/oecd/en/about/programmes/cfe/oecd-principles-on-urban-policy/OECD-Principles-on-Urban-Policy.pdf/_jcr_content/renditions/original./OECD-Principles-on-Urban-Policy.pdf",
            },
            {
                "title": "Five years of the OECD Principles on Urban Policy",
                "publisher": "OECD",
                "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2025/12/five-years-of-the-oecd-principles-on-urban-policy_049bafa2/e1104359-en.pdf",
            },
            {
                "title": "Approaches to Metropolitan Area Governance",
                "publisher": "OECD",
                "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2014/04/approaches-to-metropolitan-area-governance_g17a248c/5jz5j1q7s128-en.pdf",
            },
        ]
    },
    "archive/542-intergovernmental-machinery-lawful-councils-compacts-formula-finance-and-no-government-by-summit.md": {
        "groups": [
            {
                "title": "Making Decentralisation Work",
                "publisher": "OECD",
                "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2019/03/making-decentralisation-work_g1g9faa7/g2g9faa7-en.pdf",
            },
            {
                "title": "Navigating conflict and fostering co-operation in fiscal federalism",
                "publisher": "OECD",
                "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2024/07/navigating-conflict-and-fostering-co-operation-in-fiscal-federalism_98bc9f50/3d5c8c20-en.pdf",
            },
            {
                "title": "The consultation of local authorities by higher levels of government",
                "publisher": "Council of Europe",
                "url": "https://rm.coe.int/the-consultation-of-local-authorities-by-higher-levels-of-government-g/16808d3c72",
            },
            {
                "title": "Federalism",
                "publisher": "International IDEA",
                "url": "https://www.idea.int/sites/default/files/publications/federalism-primer.pdf",
            },
            {
                "title": "Federal Systems, Intergovernmental Relations and Federated Regions",
                "publisher": "International IDEA",
                "url": "https://www.idea.int/sites/default/files/publications/federal-systems-intergovernmental-relations-and-federated-regions.pdf",
            },
        ]
    },
    "archive/490-representation-by-scope-neighborhood-voice-metro-election-federal-shared-rule-and-deliberative-complement.md": {
        "groups": [
            {
                "title": "European Charter of Local Self-Government",
                "publisher": "Council of Europe",
                "url": "https://rm.coe.int/european-charter-for-local-self-government-english-version-pdf-a6-59-p/16807198a3",
            },
            {
                "title": "Innovative Citizen Participation and New Democratic Institutions",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/publications/innovative-citizen-participation-and-new-democratic-institutions_339306da-en/full-report.html",
            },
            {
                "title": "Second Chambers in Federal Systems",
                "publisher": "International IDEA",
                "url": "https://www.idea.int/publications/catalogue/second-chambers-federal-systems",
            },
            {
                "title": "Electoral System Design: The New International IDEA Handbook",
                "publisher": "International IDEA",
                "url": "https://www.idea.int/publications/catalogue/electoral-system-design-new-international-idea-handbook",
            },
            {
                "title": "Report on Bicameralism",
                "publisher": "Venice Commission",
                "url": "https://www.venice.coe.int/webforms/documents/default.aspx?pdffile=CDL-AD%282024%29007-e",
            },
        ]
    },
    "archive/491-adaptive-boundaries-functional-geographies-prior-consultation-and-no-frozen-maps.md": {
        "groups": [
            {
                "title": "European Charter of Local Self-Government",
                "publisher": "Council of Europe",
                "url": "https://rm.coe.int/european-charter-for-local-self-government-english-version-pdf-a6-59-p/16807198a3",
            },
            {
                "title": "The consultation of local authorities by higher levels of government",
                "publisher": "Council of Europe",
                "url": "https://rm.coe.int/the-consultation-of-local-authorities-by-higher-levels-of-government-g/16808d3c72",
            },
            {
                "title": "OECD Principles on Urban Policy",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/about/programmes/oecd-programme-on-national-urban-policy/oecd-principles-on-urban-policy.html",
            },
            {
                "title": "What Makes Cities More Productive? Evidence on the Role of Urban Governance from Five OECD Countries",
                "publisher": "OECD",
                "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2014/05/what-makes-cities-more-productive-evidence-on-the-role-of-urban-governance-from-five-oecd-countries_g17a2497/5jz432cf2d8p-en.pdf",
            },
        ]
    },
    "archive/492-competence-conflict-routing-intergovernmental-arbitration-and-no-settlement-by-fiscal-blackmail.md": {
        "groups": [
            {
                "title": "Navigating conflict and fostering co-operation in fiscal federalism",
                "publisher": "OECD",
                "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2024/07/navigating-conflict-and-fostering-co-operation-in-fiscal-federalism_98bc9f50/3d5c8c20-en.pdf",
            },
            {
                "title": "The consultation of local authorities by higher levels of government",
                "publisher": "Council of Europe",
                "url": "https://rm.coe.int/the-consultation-of-local-authorities-by-higher-levels-of-government-g/16808d3c72",
            },
            {
                "title": "Bulletin Special Issue: Relations with other State Powers",
                "publisher": "Venice Commission",
                "url": "https://www.venice.coe.int/files/bulletin/specbull-relations-with-other-state-powers-e.pdf",
            },
            {
                "title": "Report on the status of the European Charter of Local Self-Government in the constitutional and legal systems of states parties",
                "publisher": "Venice Commission",
                "url": "https://www.venice.coe.int/webforms/documents/default.aspx?pdffile=CDL-AD%282025%29049-e",
            },
        ]
    },
    "archive/493-executive-by-scope-neighborhood-stewards-city-administration-metro-legitimacy-federal-cabinets-and-narrow-waist-secretariats.md": {
        "groups": [
            {
                "title": "A Practical Guide to Constitution Building: The Design of the Executive Branch",
                "publisher": "International IDEA",
                "url": "https://www.idea.int/sites/default/files/publications/chapters/practical-guide-to-constitution-building/a-practical-guide-to-constitution-building-chapter-4.pdf",
            },
            {
                "title": "Recommendation CM/Rec(2023)5 of the Committee of Ministers to member States on the principles of good democratic governance",
                "publisher": "Council of Europe",
                "url": "https://rm.coe.int/0900001680abeb87",
            },
            {
                "title": "Approaches to Metropolitan Area Governance",
                "publisher": "OECD",
                "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2014/04/approaches-to-metropolitan-area-governance_g17a248c/5jz5j1q7s128-en.pdf",
            },
            {
                "title": "European Charter of Local Self-Government",
                "publisher": "Council of Europe",
                "url": "https://rm.coe.int/european-charter-for-local-self-government-english-version-pdf-a6-59-p/16807198a3",
            },
        ]
    },
    "archive/494-remedy-stack-by-scope-local-ombuds-administrative-justice-constitutional-review-and-subsidiarity-safe-access.md": {
        "groups": [
            {
                "title": "Courts in Federal Countries",
                "publisher": "International IDEA",
                "url": "https://www.idea.int/sites/default/files/publications/courts-in-federal-countries.pdf",
            },
            {
                "title": "Study on Individual Access to Constitutional Justice",
                "publisher": "Venice Commission",
                "url": "https://www.venice.coe.int/webforms/documents/default.aspx?pdffile=cdl-ad%282010%29039rev-e",
            },
            {
                "title": "Protection, promotion and development of the Ombudsman institution",
                "publisher": "Council of Europe",
                "url": "https://rm.coe.int/protection-promotion-and-development-of-the-ombudsman-institution/1680a13325",
            },
        ]
    },
    "archive/495-crisis-federalism-threshold-escalation-rule-of-law-temporariness-and-handback-clocks.md": {
        "groups": [
            {
                "title": "Respect for Democracy, Human Rights and the Rule of Law during States of Emergency",
                "publisher": "Venice Commission",
                "url": "https://www.venice.coe.int/webforms/documents/default.aspx?pdffile=CDL-AD%282020%29014-e",
            },
            {
                "title": "International health regulations",
                "publisher": "World Health Organization",
                "url": "https://www.who.int/health-topics/international-health-regulations",
            },
            {
                "title": "Risk governance",
                "publisher": "UNDRR",
                "url": "https://www.undrr.org/implementing-sendai-framework/risk-governance",
            },
        ]
    },
    "archive/487-subsidiarity-by-default-burden-of-proof-for-upward-scope-and-recallable-delegation.md": {
        "groups": [
            {
                "title": "The principle of subsidiarity",
                "publisher": "EUR-Lex - European Union",
                "url": "https://eur-lex.europa.eu/EN/legal-content/summary/the-principle-of-subsidiarity.html",
            },
            {
                "title": "Multi-level governance",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/topics/multi-level-governance.html",
            },
            {
                "title": "The Prize in Economic Sciences 2009 - Popular information",
                "publisher": "Nobel Prize Outreach",
                "url": "https://www.nobelprize.org/prizes/economic-sciences/2009/popular-information/",
            },
        ]
    },
    "archive/488-scope-typed-governance-stack-block-municipality-metro-region-nation-and-planet.md": {
        "groups": [
            {
                "title": "OECD Principles on Urban Policy",
                "publisher": "OECD",
                "url": "https://www.oecd.org/content/dam/oecd/en/about/programmes/cfe/oecd-principles-on-urban-policy/OECD-Principles-on-Urban-Policy.pdf/_jcr_content/renditions/original./OECD-Principles-on-Urban-Policy.pdf",
            },
            {
                "title": "What Makes Cities More Productive? Evidence on the Role of Urban Governance from Five OECD Countries",
                "publisher": "OECD",
                "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2014/05/what-makes-cities-more-productive-evidence-on-the-role-of-urban-governance-from-five-oecd-countries_g17a2497/5jz432cf2d8p-en.pdf",
            },
            {
                "title": "International health regulations",
                "publisher": "World Health Organization",
                "url": "https://www.who.int/health-topics/international-health-regulations",
            },
            {
                "title": "The Paris Agreement",
                "publisher": "UN Climate Change",
                "url": "https://unfccc.int/process-and-meetings/the-paris-agreement",
            },
            {
                "title": "UN Charter | United Nations",
                "publisher": "United Nations",
                "url": "https://www.un.org/en/about-us/un-charter",
            },
            {
                "title": "About the ICANN Community",
                "publisher": "ICANN",
                "url": "https://www.icann.org/en/community",
            },
        ]
    },
    "archive/489-fiscal-equalization-universal-floors-and-no-postcode-lottery.md": {
        "groups": [
            {
                "title": "Making Decentralisation Work",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/publications/making-decentralisation-work_g2g9faa7-en.html",
            },
            {
                "title": "Fiscal Federalism 2022",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/publications/fiscal-federalism-2022_201c75b6-en.html",
            },
            {
                "title": "Fiscal Equalisation in OECD Countries",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/publications/fiscal-equalisation-in-oecd-countries_5k97b11n2gxx-en.html",
            },
            {
                "title": "Fiscal equalisation and regional development policies",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/publications/fiscal-equalisation-and-regional-development-policies_0d28a879-en.html",
            },
        ]
    },
    "archive/496-civil-service-by-scope-stewardship-without-patronage-municipal-professionalism-metro-capacity-and-constitutional-merit-cores.md": {
        "groups": [
            {
                "title": "The Principles of Public Administration",
                "publisher": "SIGMA / OECD",
                "url": "https://www.sigmaweb.org/content/dam/sigma/en/publications/reports/2023/11/the-principles-of-public-administration_5e68f805/7f5ec453-en.pdf",
            },
            {
                "title": "European Charter of Local Self-Government",
                "publisher": "Council of Europe",
                "url": "https://rm.coe.int/european-charter-for-local-self-government-english-version-pdf-a6-59-p/16807198a3",
            },
            {
                "title": "Recommendation CM/Rec(2023)5 of the Committee of Ministers to member States on the principles of good democratic governance",
                "publisher": "Council of Europe",
                "url": "https://search.coe.int/cm?i=0900001680abeb87",
            },
        ]
    },
    "archive/497-public-knowledge-by-scope-local-records-metro-observatories-independent-statistics-audit-and-open-science.md": {
        "groups": [
            {
                "title": "Fundamental Principles of Official Statistics",
                "publisher": "United Nations Statistics Division",
                "url": "https://unstats.un.org/unsd/dnss/gp/fundprinciples.aspx",
            },
            {
                "title": "Recommendation of the Council on Good Statistical Practice",
                "publisher": "OECD",
                "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0417",
            },
            {
                "title": "INTOSAI-P 1 - Declaration of Lima",
                "publisher": "INTOSAI",
                "url": "https://www.intosai.org/fileadmin/downloads/documents/open_access/INT_P_1_u_P_10/INTOSAI_P_1_en_2019.pdf",
            },
            {
                "title": "INTOSAI-P 10 - Mexico Declaration on SAI Independence",
                "publisher": "INTOSAI",
                "url": "https://www.intosai.org/fileadmin/downloads/documents/open_access/INT_P_1_u_P_10/INTOSAI_P_10_en_2019.pdf",
            },
            {
                "title": "UNESCO Recommendation on Open Science",
                "publisher": "UNESCO",
                "url": "https://www.unesco.org/en/open-science/about",
            },
        ]
    },
    "archive/498-constitutional-change-by-scope-local-charters-double-majorities-constituent-consent-and-no-silent-recentralization.md": {
        "groups": [
            {
                "title": "Report on Constitutional Amendment",
                "publisher": "Venice Commission",
                "url": "https://www.venice.coe.int/webforms/documents/?pdf=cdl-ad%282010%29001-e",
            },
            {
                "title": "Constitutional Amendment Procedures",
                "publisher": "International IDEA",
                "url": "https://www.idea.int/sites/default/files/publications/constitutional-amendment-procedures-primer.pdf",
            },
            {
                "title": "Federalism",
                "publisher": "International IDEA",
                "url": "https://www.idea.int/sites/default/files/publications/federalism-primer.pdf",
            },
            {
                "title": "European Charter of Local Self-Government",
                "publisher": "Council of Europe",
                "url": "https://rm.coe.int/european-charter-for-local-self-government-english-version-pdf-a6-59-p/16807198a3",
            },
            {
                "title": "Revised Code of Good Practice on Referendums",
                "publisher": "Venice Commission",
                "url": "https://www.venice.coe.int/webforms/documents/default.aspx?pdffile=CDL-AD%282022%29015-e",
            },
        ]
    },
    "archive/499-public-integrity-by-scope-local-disclosure-conflict-checks-lobbying-transparency-asset-declarations-and-anti-capture-routing.md": {
        "groups": [
            {
                "title": "Recommendation of the Council on Public Integrity",
                "publisher": "OECD",
                "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0435",
            },
            {
                "title": "Recommendation on Transparency and Integrity in Lobbying and Influence",
                "publisher": "OECD",
                "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0379",
            },
            {
                "title": "UNCAC Chapter II: Prevention",
                "publisher": "UNODC",
                "url": "https://www.unodc.org/corruption/en/learn/what-is-uncac/prevention.html",
            },
            {
                "title": "Asset Declarations for Public Officials",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/publications/asset-declarations-for-public-officials_9789264095281-en.html",
            },
        ]
    },
    "archive/500-political-competition-by-scope-civic-lists-durable-parties-public-finance-spending-discipline-and-no-incumbency-self-dealing.md": {
        "groups": [
            {
                "title": "Guidelines on Political Party Regulation",
                "publisher": "OSCE/ODIHR and Venice Commission",
                "url": "https://odihr.osce.org/sites/default/files/f/documents/8/1/538473.pdf",
            },
            {
                "title": "Recommendation Rec(2003)4 on common rules against corruption in the funding of political parties and electoral campaigns",
                "publisher": "Council of Europe",
                "url": "https://rm.coe.int/16806cc1f1",
            },
            {
                "title": "Preventing and responding to the misuse of administrative resources during electoral processes",
                "publisher": "Venice Commission and OSCE/ODIHR",
                "url": "https://www.venice.coe.int/images/GBR_2016_Guidelines_resources_elections.pdf",
            },
            {
                "title": "Code of Good Practice in Electoral Matters",
                "publisher": "Venice Commission",
                "url": "https://search.coe.int/cm/Pages/result_details.aspx?ObjectID=090000168092af01",
            },
        ]
    },
    "archive/501-public-sphere-by-scope-community-media-public-service-independence-ownership-transparency-and-civic-information-commons.md": {
        "groups": [
            {
                "title": "Recommendation CM/Rec(2018)1 on media pluralism and transparency of media ownership",
                "publisher": "Council of Europe",
                "url": "https://www.coe.int/en/web/freedom-expression/committee-of-ministers-adopted-texts/-/asset_publisher/aDXmrol0vvsU/content/recommendation-cm-rec-2018-1-1-of-the-committee-of-ministers-to-member-states-on-media-pluralism-and-transparency-of-media-ownership",
            },
            {
                "title": "Recommendation CM/Rec(2012)1 on public service media governance",
                "publisher": "Council of Europe",
                "url": "https://search.coe.int/cm/Pages/result_details.aspx?ObjectID=09000016805cb4b4",
            },
            {
                "title": "Recommendation CM/Rec(2022)4 on promoting a favourable environment for quality journalism in the digital age",
                "publisher": "Council of Europe",
                "url": "https://www.coe.int/en/web/freedom-expression/committee-of-ministers-adopted-texts/-/asset_publisher/aDXmrol0vvsU/content/recommendation-cm-rec-2022-4-of-the-committee-of-ministers-to-member-states-on-promoting-a-favourable-environment-for-quality-journalism-in-the-digita",
            },
            {
                "title": "European Media Freedom Act",
                "publisher": "European Union",
                "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=OJ%3AL_202401083",
            },
            {
                "title": "Community Media",
                "publisher": "UNESCO",
                "url": "https://www.unesco.org/en/media-pluralism-diversity/community-media",
            },
        ]
    },
    "archive/502-public-safety-by-scope-prevention-first-local-legitimacy-metro-serious-crime-coordination-and-rights-locked-cooperation.md": {
        "groups": [
            {
                "title": "Code of Conduct for Law Enforcement Officials",
                "publisher": "OHCHR",
                "url": "https://www.ohchr.org/en/instruments-mechanisms/instruments/code-conduct-law-enforcement-officials",
            },
            {
                "title": "Basic Principles on the Use of Force and Firearms by Law Enforcement Officials",
                "publisher": "OHCHR",
                "url": "https://www.ohchr.org/en/instruments-mechanisms/instruments/basic-principles-use-force-and-firearms-law-enforcement",
            },
            {
                "title": "Police oversight mechanisms in the Council of Europe member states",
                "publisher": "Council of Europe",
                "url": "https://edoc.coe.int/en/international-law/7414-police-oversight-mechanisms-in-the-council-of-europe-member-states.html",
            },
            {
                "title": "Crime Prevention",
                "publisher": "UNODC",
                "url": "https://www.unodc.org/unodc/justice-and-prison-reform/cpcj-crimeprevention-home.html",
            },
            {
                "title": "Handbook on the Crime Prevention Guidelines",
                "publisher": "UNODC",
                "url": "https://www.unodc.org/e4j/en/data/_university_uni_/2247_handbook_on_the_crime_prevention_guidelines.html",
            },
            {
                "title": "Legal documents",
                "publisher": "INTERPOL",
                "url": "https://www.interpol.int/Who-we-are/Legal-framework/Legal-documents",
            },
            {
                "title": "Data protection",
                "publisher": "INTERPOL",
                "url": "https://www.interpol.int/Who-we-are/Legal-framework/Data-protection",
            },
            {
                "title": "Compliance and review",
                "publisher": "INTERPOL",
                "url": "https://www.interpol.int/How-we-work/Notices/Compliance-and-review",
            },
        ]
    },
    "archive/503-intelligence-by-scope-no-local-secret-police-judicial-authorization-minimization-and-multi-key-oversight.md": {
        "groups": [
            {
                "title": "Report on the Democratic oversight of the Security Services",
                "publisher": "Venice Commission",
                "url": "https://www.coe.int/en/web/venice-commission/-/opinion-388",
            },
            {
                "title": "Update of the 2007 Report on the Democratic Oversight of the Security Services and Report on Democratic Oversight of Signals Intelligence Agencies",
                "publisher": "Venice Commission",
                "url": "https://www.venice.coe.int/webforms/documents/?pdf=CDL-AD%282015%29006-e",
            },
            {
                "title": "Control of internal security services in council of Europe member states",
                "publisher": "Parliamentary Assembly of the Council of Europe",
                "url": "https://assembly.coe.int/nw/xml/XRef/Xref-XML2HTML-en.asp?fileid=16689&lang=en",
            },
            {
                "title": "Special Rapporteur on the right to privacy",
                "publisher": "OHCHR",
                "url": "https://www.ohchr.org/en/special-procedures/sr-privacy",
            },
            {
                "title": "Digital space and human rights",
                "publisher": "OHCHR",
                "url": "https://www.ohchr.org/en/topic/digital-space-and-human-rights",
            },
        ]
    },
    "archive/504-defense-by-scope-civilian-control-civil-defense-no-subnational-war-machines-and-narrow-waist-collective-security.md": {
        "groups": [
            {
                "title": "Code of Conduct on Politico-Military Aspects of Security",
                "publisher": "OSCE",
                "url": "https://www.osce.org/node/660127",
            },
            {
                "title": "UN Charter | United Nations",
                "publisher": "United Nations",
                "url": "https://www.un.org/en/about-us/un-charter",
            },
            {
                "title": "Maintain International Peace and Security",
                "publisher": "United Nations",
                "url": "https://www.un.org/en/our-work/maintain-international-peace-and-security",
            },
            {
                "title": "Reform and co-operation in the security sector",
                "publisher": "OSCE",
                "url": "https://www.osce.org/node/660109",
            },
        ]
    },
    "archive/505-land-and-housing-by-scope-secure-tenure-municipal-place-making-metro-housing-markets-regional-landscapes-and-national-fairness.md": {
        "groups": [
            {
                "title": "Urban housing",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/topics/urban-housing.html",
            },
            {
                "title": "Steering the Metropolis: Metropolitan Governance for Sustainable Urban Development",
                "publisher": "UN-Habitat",
                "url": "https://unhabitat.org/steering-the-metropolis-metropolitan-governance-for-sustainable-urban-development",
            },
            {
                "title": "OHCHR and the right to adequate housing",
                "publisher": "OHCHR",
                "url": "https://www.ohchr.org/en/housing",
            },
            {
                "title": "A/HRC/49/48: Spatial segregation and the right to adequate housing",
                "publisher": "OHCHR",
                "url": "https://www.ohchr.org/en/documents/thematic-reports/ahrc4948-spatial-segregation-and-right-adequate-housing-report-special",
            },
            {
                "title": "Secure Land Rights for All",
                "publisher": "UN-Habitat",
                "url": "https://unhabitat.org/secure-land-rights-for-all",
            },
        ]
    },
    "archive/506-health-by-scope-primary-care-regional-capacity-national-risk-pools-and-global-alerts.md": {
        "groups": [
            {
                "title": "Primary health care",
                "publisher": "World Health Organization",
                "url": "https://www.who.int/news-room/fact-sheets/detail/primary-health-care",
            },
            {
                "title": "Health Systems Governance",
                "publisher": "World Health Organization",
                "url": "https://www.who.int/health-topics/health-systems-governance",
            },
            {
                "title": "Universal health coverage (UHC)",
                "publisher": "World Health Organization",
                "url": "https://www.who.int/news-room/fact-sheets/detail/universal-health-coverage-%28uhc%29",
            },
            {
                "title": "International Health Regulations",
                "publisher": "World Health Organization",
                "url": "https://www.who.int/health-topics/international-health-regulations",
            },
        ]
    },
    "archive/507-membership-and-movement-by-scope-local-inclusion-national-citizenship-regional-mobility-and-global-protection.md": {
        "groups": [
            {
                "title": "International standards governing migration policy",
                "publisher": "OHCHR",
                "url": "https://www.ohchr.org/en/migration/international-standards-governing-migration-policy",
            },
            {
                "title": "Migration Governance Indicators",
                "publisher": "IOM",
                "url": "https://www.iom.int/migration-governance-indicators",
            },
            {
                "title": "Global compact for migration",
                "publisher": "United Nations",
                "url": "https://refugeesmigrants.un.org/migration-compact",
            },
            {
                "title": "Ending statelessness",
                "publisher": "UNHCR",
                "url": "https://www.unhcr.org/what-we-do/protect-human-rights/ending-statelessness",
            },
            {
                "title": "About statelessness",
                "publisher": "UNHCR",
                "url": "https://www.unhcr.org/what-we-do/protect-human-rights/ending-statelessness/about-statelessness",
            },
        ]
    },
    "archive/508-education-and-learning-by-scope-local-belonging-metropolitan-desegregation-regional-systems-national-rights-and-global-knowledge.md": {
        "groups": [
            {
                "title": "Right to education",
                "publisher": "UNESCO",
                "url": "https://www.unesco.org/en/right-education",
            },
            {
                "title": "Education Governance in Action",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/publications/education-governance-in-action_9789264262829-en.html",
            },
            {
                "title": "Cities and Education 2030: Local challenges, global imperatives",
                "publisher": "UNESCO-IIEP",
                "url": "https://www.iiep.unesco.org/en/projects/cities-and-education-2030",
            },
            {
                "title": "Inclusion in education",
                "publisher": "UNESCO",
                "url": "https://www.unesco.org/en/inclusion-education",
            },
        ]
    },
    "archive/509-work-and-income-security-by-scope-local-access-regional-labour-markets-national-social-insurance-and-transnational-portability.md": {
        "groups": [
            {
                "title": "Labour administration",
                "publisher": "ILO",
                "url": "https://www.ilo.org/topics-and-sectors/labour-administration",
            },
            {
                "title": "Public employment services and active labour market policies for transitions",
                "publisher": "ILO",
                "url": "https://www.ilo.org/publications/public-employment-services-and-active-labour-market-policies-transitions",
            },
            {
                "title": "Social Protection Floors Recommendation, 2012 (No. 202)",
                "publisher": "ILO",
                "url": "https://www.ilo.org/publications/social-protection-floors-recommendation-2012-no-202",
            },
            {
                "title": "Social dialogue and tripartism",
                "publisher": "ILO",
                "url": "https://www.ilo.org/topics-and-sectors/social-dialogue-and-tripartism",
            },
        ]
    },
    "archive/510-networked-utilities-by-scope-local-access-metropolitan-mobility-basin-and-grid-coordination-national-universal-service-and-cross-border-interoperability.md": {
        "groups": [
            {
                "title": "The OECD Principles on Water Governance and implementation strategy",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/topics/sub-issues/water-governance/the-oecd-principles-on-water-governance-and-implementation-strategy.html",
            },
            {
                "title": "Electricity Grids and Secure Energy Transitions",
                "publisher": "IEA",
                "url": "https://www.iea.org/reports/electricity-grids-and-secure-energy-transitions",
            },
            {
                "title": "Policy Directions for Establishing a Metropolitan Transport Authority for Korea's Capital Region",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/publications/policy-directions-for-establishing-a-metropolitan-transport-authority-for-korea-s-capital-region_8b87cefc-en.html",
            },
            {
                "title": "Global Connectivity Report 2025",
                "publisher": "ITU",
                "url": "https://www.itu.int/itu-d/reports/statistics/global-connectivity-report-2025/",
            },
        ]
    },
    "archive/511-climate-by-scope-local-adaptation-metropolitan-form-regional-resilience-national-transition-and-global-carbon-limits.md": {
        "groups": [
            {
                "title": "The Paris Agreement",
                "publisher": "UN Climate Change",
                "url": "https://unfccc.int/process-and-meetings/the-paris-agreement",
            },
            {
                "title": "National Adaptation Plans",
                "publisher": "UN Climate Change",
                "url": "https://unfccc.int/national-adaptation-plans",
            },
            {
                "title": "Climate adaptation: Why local governments cannot do it alone",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/publications/climate-adaptation-why-local-governments-cannot-do-it-alone_be90ac30-en.html",
            },
            {
                "title": "A Territorial Approach to Climate Action and Resilience",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/publications/a-territorial-approach-to-climate-action-and-resilience_1ec42b0a-en.html",
            },
            {
                "title": "Guiding Principles for City Climate Action Planning",
                "publisher": "UN-Habitat",
                "url": "https://unhabitat.org/guiding-principles-for-city-climate-action-planning",
            },
        ]
    },
    "archive/512-biodiversity-by-scope-local-stewardship-municipal-ecology-regional-landscapes-national-law-and-global-commons.md": {
        "groups": [
            {
                "title": "Kunming-Montreal Global Biodiversity Framework",
                "publisher": "Convention on Biological Diversity",
                "url": "https://www.cbd.int/gbf",
            },
            {
                "title": "Target 1",
                "publisher": "Convention on Biological Diversity",
                "url": "https://www.cbd.int/gbf/targets/1",
            },
            {
                "title": "Target 3",
                "publisher": "Convention on Biological Diversity",
                "url": "https://www.cbd.int/gbf/targets/3",
            },
            {
                "title": "National Biodiversity Strategies and Action Plans (NBSAPs)",
                "publisher": "Convention on Biological Diversity",
                "url": "https://www.cbd.int/nbsap",
            },
            {
                "title": "National Biodiversity Strategies and Action Plans",
                "publisher": "UNEP",
                "url": "https://www.unep.org/topics/nature-action/global-biodiversity-framework/national-biodiversity-strategies-and-action",
            },
            {
                "title": "Traditional Knowledge, Innovations and Practices",
                "publisher": "Convention on Biological Diversity",
                "url": "https://www.cbd.int/traditional/intro.shtml",
            },
        ]
    },
    "archive/513-food-systems-by-scope-local-access-regional-foodsheds-national-guarantees-and-fair-global-rules.md": {
        "groups": [
            {
                "title": "Governance for agrifood systems transformation",
                "publisher": "FAO",
                "url": "https://www.fao.org/policy-support/governance/en",
            },
            {
                "title": "Sustainable food and agriculture",
                "publisher": "FAO",
                "url": "https://www.fao.org/policy-support/governance/Sustainable-food-and-agriculture/en",
            },
            {
                "title": "Right to food",
                "publisher": "FAO",
                "url": "https://www.fao.org/right-to-food/en",
            },
            {
                "title": "Committee on World Food Security (CFS)",
                "publisher": "FAO",
                "url": "https://www.fao.org/cfs/en/",
            },
            {
                "title": "About Codex Alimentarius",
                "publisher": "FAO/WHO",
                "url": "https://www.fao.org/fao-who-codexalimentarius/about-codex/en/",
            },
            {
                "title": "Voluntary Guidelines for Securing Sustainable Small-Scale Fisheries",
                "publisher": "FAO",
                "url": "https://www.fao.org/voluntary-guidelines-small-scale-fisheries/en",
            },
        ]
    },
    "archive/514-justice-by-scope-local-resolution-city-legal-aid-regional-courts-national-codes-and-global-rights.md": {
        "groups": [
            {
                "title": "Toolkit for Access to Justice and People-Centred Justice Systems",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/publications/toolkit-for-access-to-justice-and-people-centred-justice-systems_aecf7f78-en.html",
            },
            {
                "title": "Making Justice Systems More Effective and People Centred",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/publications/making-justice-systems-more-effective-and-people-centred_e02fd90b-en.html",
            },
            {
                "title": "Basic Principles on the Independence of the Judiciary",
                "publisher": "OHCHR",
                "url": "https://www.ohchr.org/en/instruments-mechanisms/instruments/basic-principles-independence-judiciary",
            },
            {
                "title": "Checklist for promoting access to justice",
                "publisher": "Council of Europe CEPEJ",
                "url": "https://rm.coe.int/cepej-2025-16-access-to-justice-checklist-en-pour-publication/488029d233",
            },
        ]
    },
    "archive/515-digital-public-infrastructure-by-scope-local-access-city-service-design-national-rails-and-global-open-standards.md": {
        "groups": [
            {
                "title": "Digital public infrastructure for digital governments",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/publications/digital-public-infrastructure-for-digital-governments_ff525dc8-en.html",
            },
            {
                "title": "Digital public infrastructure: Government at a Glance 2025",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/publications/government-at-a-glance-2025_0efd0bcd-en/full-report/digital-public-infrastructure_1cee4220.html",
            },
            {
                "title": "Global Connectivity Report 2025",
                "publisher": "ITU",
                "url": "https://www.itu.int/itu-d/reports/statistics/global-connectivity-report-2025/",
            },
            {
                "title": "Digital Public Infrastructure",
                "publisher": "UNDP",
                "url": "https://www.undp.org/digital/digital-public-infrastructure",
            },
            {
                "title": "How the DPG Standard and the Universal DPI Safeguards Framework are charting a safe and inclusive digital future",
                "publisher": "UNDP",
                "url": "https://www.undp.org/digital/blog/how-dpg-standard-and-universal-dpi-safeguards-framework-are-charting-safe-and-inclusive-digital-future",
            },
            {
                "title": "Introduction to the IETF",
                "publisher": "IETF",
                "url": "https://www.ietf.org/about/introduction/",
            },
            {
                "title": "What Does ICANN Do?",
                "publisher": "ICANN",
                "url": "https://www.icann.org/resources/pages/what-2012-02-25-en",
            },
        ]
    },
    "archive/516-markets-and-company-power-by-scope-local-entry-metro-space-national-antitrust-and-fair-global-rules.md": {
        "groups": [
            {
                "title": "Competition and market dynamism",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/topics/competition-and-market-dynamism.html",
            },
            {
                "title": "OECD Competition Trends 2025",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/publications/oecd-competition-trends-2025_8c4bd00b-en.html",
            },
            {
                "title": "G20/OECD Principles of Corporate Governance 2023",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/publications/g20-oecd-principles-of-corporate-governance-2023_ed750b30-en.html",
            },
            {
                "title": "OECD Corporate Governance Factbook 2025",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/publications/oecd-corporate-governance-factbook-2025_f4f43735-en.html",
            },
            {
                "title": "The United Nations set of principles on competition",
                "publisher": "UNCTAD",
                "url": "https://unctad.org/topic/competition-and-consumer-protection/the-united-nations-set-of-principles-on-competition",
            },
            {
                "title": "Understanding the WTO - principles of the trading system",
                "publisher": "WTO",
                "url": "https://www.wto.org/english/thewto_e/whatis_e/tif_e/fact2_e.htm",
            },
            {
                "title": "Global Minimum Tax",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/topics/global-minimum-tax.html",
            },
        ]
    },
    "archive/517-public-revenue-and-taxation-by-scope-local-own-source-taxes-metropolitan-base-sharing-national-progressivity-and-global-anti-evasion-floors.md": {
        "groups": [
            {
                "title": "Fiscal Federalism 2022",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/publications/fiscal-federalism-2022_201c75b6-en.html",
            },
            {
                "title": "Synthesising good practices in fiscal federalism",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/publications/synthesising-good-practices-in-fiscal-federalism_89cd0319-en.html",
            },
            {
                "title": "Global Minimum Tax",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/topics/global-minimum-tax.html",
            },
            {
                "title": "Global Anti-Base Erosion Model Rules (Pillar Two)",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/topics/sub-issues/global-minimum-tax/global-anti-base-erosion-model-rules-pillar-two.html",
            },
        ]
    },
    "archive/518-public-investment-and-procurement-by-scope-local-maintenance-metro-systems-national-capital-discipline-and-narrow-global-standards.md": {
        "groups": [
            {
                "title": "Recommendation of the Council on Effective Public Investment Across Levels of Government",
                "publisher": "OECD",
                "url": "https://legalinstruments.oecd.org/public/doc/302/302.en.pdf",
            },
            {
                "title": "Effective Public Investment Toolkit",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/about/projects/effective-public-investment-toolkit.html",
            },
            {
                "title": "Recommendation of the Council on Public Procurement",
                "publisher": "OECD",
                "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0411",
            },
            {
                "title": "Implementing the OECD Recommendation on Public Procurement in OECD and partner countries",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/publications/implementing-the-oecd-recommendation-on-public-procurement-in-oecd-and-partner-countries_02a46a58-en/full-report/overview_fab2711c.html",
            },
            {
                "title": "Strategic public procurement",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/topics/strategic-public-procurement.html",
            },
            {
                "title": "Recommendation on Governance of Infrastructure",
                "publisher": "OECD",
                "url": "https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0460",
            },
        ]
    },
    "archive/519-innovation-and-industrial-policy-by-scope-local-entrepreneurship-regional-clusters-national-missions-and-open-global-coordination.md": {
        "groups": [
            {
                "title": "Broad-based Innovation Policy for All Regions and Cities",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/publications/broad-based-innovation-policy-for-all-regions-and-cities_299731d2-en.html",
            },
            {
                "title": "Place-based industrial policy",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/publications/place-based-industrial-policy_43edc0df-en.html",
            },
            {
                "title": "Implementation Toolkit: OECD Recommendation on Regional Development Policy",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/about/projects/implementing-the-oecd-recommendation-on-regional-development-policy-toolkit.html",
            },
            {
                "title": "Industrial Policy Advice and Capacity Development - Our policy tools",
                "publisher": "UNIDO",
                "url": "https://www.unido.org/industrial-policy-advice-and-capacity-development/our-policy-tools",
            },
            {
                "title": "Subsidies and Countervailing Measures overview",
                "publisher": "WTO",
                "url": "https://www.wto.org/english/tratop_e/scm_e/subs_e.htm",
            },
            {
                "title": "Agreement on Subsidies and Countervailing Measures",
                "publisher": "WTO",
                "url": "https://www.wto.org/english/docs_e/legal_e/scm_e.htm",
            },
        ]
    },
    "archive/520-care-and-support-by-scope-household-reciprocity-municipal-services-regional-care-systems-national-social-insurance-and-global-worker-protection.md": {
        "groups": [
            {
                "title": "Advancing decent work and the care economy: An essential component of social development",
                "publisher": "International Labour Organization",
                "url": "https://www.ilo.org/publications/advancing-decent-work-and-care-economy-essential-component-social",
            },
            {
                "title": "Care economy",
                "publisher": "International Labour Organization",
                "url": "https://www.ilo.org/topics-and-sectors/care-economy",
            },
            {
                "title": "Ageing and long-term care",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/topics/ageing-and-long-term-care.html",
            },
            {
                "title": "Long-term care workers",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/publications/health-at-a-glance-2025_8f9e3f98-en/full-report/long-term-care-workers_9c3bdbaf.html",
            },
            {
                "title": "Long-term care settings",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/publications/health-at-a-glance-2025_8f9e3f98-en/full-report/long-term-care-settings_9f4aa221.html",
            },
        ]
    },
    "archive/521-disability-and-accessibility-by-scope-local-barrier-removal-municipal-universal-design-regional-supports-national-rights-and-global-standards.md": {
        "groups": [
            {
                "title": "Convention on the Rights of Persons with Disabilities",
                "publisher": "OHCHR",
                "url": "https://www.ohchr.org/en/instruments-mechanisms/instruments/convention-rights-persons-disabilities",
            },
            {
                "title": "WHO Disability Health Equity Initiative",
                "publisher": "World Health Organization",
                "url": "https://www.who.int/initiatives/disability-health-equity-initiative",
            },
            {
                "title": "Strengthening disability inclusion through collaboration",
                "publisher": "World Health Organization",
                "url": "https://www.who.int/health-topics/environmental-health/strengthening-disability-inclusion-through-collaboration",
            },
            {
                "title": "How to support local authorities to implement human rights",
                "publisher": "UNESCO",
                "url": "https://www.unesco.org/en/articles/how-support-local-authorities-implement-human-rights",
            },
        ]
    },
    "archive/522-culture-and-heritage-by-scope-local-belonging-municipal-institutions-regional-ecologies-national-pluralism-and-global-commons.md": {
        "groups": [
            {
                "title": "Cultural rights",
                "publisher": "UNESCO",
                "url": "https://www.unesco.org/en/mondiacult/cultural-rights",
            },
            {
                "title": "UNESCO Global Report on Cultural Policies",
                "publisher": "UNESCO",
                "url": "https://www.unesco.org/en/culture/global-report",
            },
            {
                "title": "Convention on the Protection and Promotion of the Diversity of Cultural Expressions",
                "publisher": "UNESCO",
                "url": "https://www.unesco.org/en/legal-affairs/convention-protection-and-promotion-diversity-cultural-expressions",
            },
            {
                "title": "The 2005 Convention on the Protection and Promotion of the Diversity of Cultural Expressions",
                "publisher": "UNESCO",
                "url": "https://www.unesco.org/en/node/560",
            },
            {
                "title": "World Heritage",
                "publisher": "UNESCO",
                "url": "https://www.unesco.org/en/world-heritage",
            },
        ]
    },
    "archive/523-gender-equality-and-bodily-autonomy-by-scope-local-safety-municipal-access-regional-referral-national-equality-and-global-rights.md": {
        "groups": [
            {
                "title": "Convention on the Elimination of All Forms of Discrimination against Women",
                "publisher": "OHCHR",
                "url": "https://www.ohchr.org/en/instruments-mechanisms/instruments/convention-elimination-all-forms-discrimination-against-women",
            },
            {
                "title": "Sexual and reproductive health and rights",
                "publisher": "World Health Organization",
                "url": "https://www.who.int/health-topics/sexual-and-reproductive-health-and-rights",
            },
            {
                "title": "Adolescent sexual and reproductive health and rights",
                "publisher": "World Health Organization",
                "url": "https://www.who.int/teams/sexual-and-reproductive-health-and-research-%28srh%29/areas-of-work/adolescent-and-sexual-and-reproductive-health-and-rights",
            },
            {
                "title": "Istanbul Convention Action against violence against women and domestic violence",
                "publisher": "Council of Europe",
                "url": "https://www.coe.int/en/web/istanbul-convention/about-the-convention",
            },
            {
                "title": "Gender-based violence against women and girls",
                "publisher": "OHCHR",
                "url": "https://www.ohchr.org/en/women/gender-based-violence-against-women-and-girls",
            },
        ]
    },
    "archive/524-children-and-youth-by-scope-local-belonging-municipal-voice-regional-opportunity-national-guarantees-and-global-rights.md": {
        "groups": [
            {
                "title": "Convention on the Rights of the Child",
                "publisher": "OHCHR",
                "url": "https://www.ohchr.org/en/instruments-mechanisms/instruments/convention-rights-child",
            },
            {
                "title": "Building a Child Friendly City",
                "publisher": "UNICEF",
                "url": "https://www.unicef.org/childfriendlycities/building-child-friendly-city",
            },
            {
                "title": "Adolescent development and participation",
                "publisher": "UNICEF",
                "url": "https://www.unicef.org/adolescence",
            },
            {
                "title": "Adolescent participation and civic engagement",
                "publisher": "UNICEF",
                "url": "https://www.unicef.org/adolescence/participation",
            },
            {
                "title": "Guide: Adolescents and participation",
                "publisher": "UNICEF",
                "url": "https://www.unicef.org/adolescentkit/reports/guide-adolescents-and-participation",
            },
        ]
    },
    "archive/525-civil-society-and-association-by-scope-local-mutual-aid-municipal-civic-space-regional-networks-national-freedom-and-global-solidarity.md": {
        "groups": [
            {
                "title": "Freedom of assembly and of association",
                "publisher": "OHCHR",
                "url": "https://www.ohchr.org/en/topic/freedom-assembly-and-association",
            },
            {
                "title": "OHCHR and protecting and expanding civic space",
                "publisher": "OHCHR",
                "url": "https://www.ohchr.org/en/civic-space",
            },
            {
                "title": "United Nations Guidance Note on Protection and Promotion of Civic Space",
                "publisher": "OHCHR",
                "url": "https://www.ohchr.org/en/civic-space/role-united-nations-protecting-and-promoting-civic-space",
            },
            {
                "title": "Protection and promotion of civic space",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/publications/government-at-a-glance-2025_0efd0bcd-en/full-report/protection-and-promotion-of-civic-space_61c25f94.html",
            },
            {
                "title": "Open government and citizen participation",
                "publisher": "OECD",
                "url": "https://www.oecd.org/en/topics/open-government-and-citizen-participation.html",
            },
        ]
    },
"archive/526-older-persons-and-ageing-by-scope-local-belonging-municipal-age-friendly-design-regional-supports-national-income-security-and-global-rights.md": {
    "groups": [
        {
            "title": "Older persons",
            "publisher": "OHCHR",
            "url": "https://www.ohchr.org/en/topic/older-persons",
        },
        {
            "title": "OHCHR and older persons",
            "publisher": "OHCHR",
            "url": "https://www.ohchr.org/en/older-persons",
        },
        {
            "title": "United Nations Principles for Older Persons",
            "publisher": "OHCHR",
            "url": "https://www.ohchr.org/en/instruments-mechanisms/instruments/united-nations-principles-older-persons",
        },
        {
            "title": "Ageing and health",
            "publisher": "World Health Organization",
            "url": "https://www.who.int/news-room/fact-sheets/detail/ageing-and-health",
        },
        {
            "title": "WHO's work on the UN Decade of Healthy Ageing (2021-2030)",
            "publisher": "World Health Organization",
            "url": "https://www.who.int/initiatives/decade-of-healthy-ageing",
        },
        {
            "title": "Integrated care for older people approach (ICOPE)",
            "publisher": "World Health Organization",
            "url": "https://www.who.int/teams/maternal-newborn-child-adolescent-health-and-ageing/ageing-and-health/integrated-care-for-older-people-icope",
        },
        {
            "title": "Creating age-friendly cities and communities",
            "publisher": "World Health Organization",
            "url": "https://www.who.int/activities/creating-age-friendly-cities-and-communities",
        },
        {
            "title": "Ageing and long-term care",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/topics/ageing-and-long-term-care.html",
        },
    ]
},
"archive/527-end-of-life-and-death-care-by-scope-local-accompaniment-municipal-death-administration-regional-palliative-capacity-national-rights-and-global-pain-relief.md": {
    "groups": [
        {
            "title": "Palliative care",
            "publisher": "World Health Organization",
            "url": "https://www.who.int/health-topics/palliative-care",
        },
        {
            "title": "Palliative care",
            "publisher": "World Health Organization",
            "url": "https://www.who.int/teams/integrated-health-services/clinical-services-and-systems/palliative-care",
        },
        {
            "title": "Guide on the decision-making process regarding medical treatment in end-of-life situations",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/CoERMPublicCommonSearchServices/DisplayDCTMContent?documentId=090000168039e8e2",
        },
        {
            "title": "About the right to health and human rights",
            "publisher": "OHCHR",
            "url": "https://www.ohchr.org/en/special-procedures/sr-health/about-right-health-and-human-rights",
        },
        {
            "title": "Right to pain relief: 5.5 billion people have no access to treatment, warn UN experts",
            "publisher": "OHCHR",
            "url": "https://www.ohchr.org/en/press-releases/2015/10/right-pain-relief-55-billion-people-have-no-access-treatment-warn-un-experts",
        },
    ]
},
"archive/528-freedom-of-conscience-and-religion-by-scope-local-coexistence-municipal-neutrality-regional-fairness-national-rights-and-global-protection.md": {
    "groups": [
        {
            "title": "Freedom of religion",
            "publisher": "OHCHR",
            "url": "https://www.ohchr.org/en/topic/freedom-religion",
        },
        {
            "title": "Special Rapporteur on freedom of religion or belief",
            "publisher": "OHCHR",
            "url": "https://www.ohchr.org/en/special-procedures/sr-religion-or-belief",
        },
        {
            "title": "International standards",
            "publisher": "OHCHR",
            "url": "https://www.ohchr.org/en/special-procedures/sr-religion-or-belief/international-standards",
        },
        {
            "title": "Guidelines for Review of Legislation Pertaining to Religion or Belief",
            "publisher": "OSCE/ODIHR",
            "url": "https://odihr.osce.org/odihr/13993",
        },
        {
            "title": "The Rabat Plan of Action",
            "publisher": "OHCHR",
            "url": "https://www.ohchr.org/en/documents/outcome-documents/rabat-plan-action",
        },
        {
            "title": "Strasbourg Principles for inter-religious dialogue within the Council of Europe",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/strasbourg-principles/1680a65e46",
        },
    ]
},
"archive/529-indigenous-peoples-and-self-government-by-scope-community-authority-municipal-consent-regional-co-governance-national-plurinational-constitutionalism-and-global-rights.md": {
    "groups": [
        {
            "title": "United Nations Declaration on the Rights of Indigenous Peoples",
            "publisher": "United Nations",
            "url": "https://www.un.org/development/desa/indigenouspeoples/wp-content/uploads/sites/19/2018/11/UNDRIP_E_web.pdf",
        },
        {
            "title": "About Indigenous Peoples and human rights",
            "publisher": "OHCHR",
            "url": "https://www.ohchr.org/en/indigenous-peoples/about-indigenous-peoples-and-human-rights",
        },
        {
            "title": "Consultation and free, prior and informed consent (FPIC)",
            "publisher": "OHCHR",
            "url": "https://www.ohchr.org/en/indigenous-peoples/consultation-and-free-prior-and-informed-consent-fpic",
        },
        {
            "title": "Report on Self-Determination under the UN Declaration on the Rights of Indigenous Peoples",
            "publisher": "OHCHR / Expert Mechanism on the Rights of Indigenous Peoples",
            "url": "https://www.ohchr.org/en/calls-for-input/report-self-determination-under-un-declaration-rights-indigenous-peoples",
        },
        {
            "title": "Indigenous and Tribal Peoples Convention, 1989 (No. 169)",
            "publisher": "ILO",
            "url": "https://www.ilo.org/media/324306/download",
        },
    ]
},
"archive/530-language-and-linguistic-pluralism-by-scope-local-use-municipal-service-access-regional-language-ecologies-national-rights-and-global-support.md": {
    "groups": [
        {
            "title": "Multilingualism and Linguistic diversity",
            "publisher": "UNESCO",
            "url": "https://www.unesco.org/en/multilingualism-linguistic-diversity",
        },
        {
            "title": "What you need to know about multilingual education",
            "publisher": "UNESCO",
            "url": "https://www.unesco.org/en/languages-education/need-know",
        },
        {
            "title": "European Charter for Regional or Minority Languages",
            "publisher": "Council of Europe",
            "url": "https://www.coe.int/en/web/european-charter-regional-or-minority-languages",
        },
        {
            "title": "About the European Charter for Regional or Minority Languages",
            "publisher": "Council of Europe",
            "url": "https://www.coe.int/en/web/european-charter-regional-or-minority-languages/about-the-charter",
        },
        {
            "title": "Language Rights of Linguistic Minorities: A Practical Guide for Implementation",
            "publisher": "OHCHR",
            "url": "https://www.ohchr.org/en/documents/tools-and-resources/language-rights-linguistic-minorities-practical-guide-implementation",
        },
        {
            "title": "Declaration on the Rights of Persons Belonging to National or Ethnic, Religious and Linguistic Minorities",
            "publisher": "OHCHR",
            "url": "https://www.ohchr.org/en/instruments-mechanisms/instruments/declaration-rights-persons-belonging-national-or-ethnic",
        },
        {
            "title": "Indigenous Languages Decade (2022-2032)",
            "publisher": "UNESCO",
            "url": "https://www.unesco.org/en/decades/indigenous-languages",
        },
    ]
},
"archive/531-rural-remote-and-peripheral-places-by-scope-local-agency-intermunicipal-service-backbones-regional-catchments-national-territorial-solidarity-and-global-learning.md": {
    "groups": [
        {
            "title": "Implementation Toolkit: OECD Recommendation on Regional Development Policy",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/about/projects/implementing-the-oecd-recommendation-on-regional-development-policy-toolkit.html",
        },
        {
            "title": "Rural Well-being: Geography of Opportunities",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/rural-well-being_d25cef80-en.html",
        },
        {
            "title": "Rural development",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/topics/rural-development.html",
        },
        {
            "title": "Territorial cohesion",
            "publisher": "European Commission",
            "url": "https://ec.europa.eu/regional_policy/policy/what/territorial-cohesion_en",
        },
        {
            "title": "Urban-rural linkages",
            "publisher": "European Commission",
            "url": "https://ec.europa.eu/regional_policy/policy/what/territorial-cohesion/urban-rural-linkages_en",
        },
    ]
},
"archive/532-water-and-sanitation-by-scope-local-access-municipal-stormwater-basin-governance-national-rights-and-transboundary-cooperation.md": {
    "groups": [
        {
            "title": "The OECD Principles on Water Governance and implementation strategy",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/topics/sub-issues/water-governance/the-oecd-principles-on-water-governance-and-implementation-strategy.html",
        },
        {
            "title": "The Water Convention and the Protocol on Water and Health",
            "publisher": "UNECE",
            "url": "https://unece.org/environment-policy/water",
        },
        {
            "title": "OHCHR and the rights to water and sanitation",
            "publisher": "OHCHR",
            "url": "https://www.ohchr.org/en/water-and-sanitation",
        },
        {
            "title": "Water, sanitation and hygiene (WASH)",
            "publisher": "World Health Organization",
            "url": "https://www.who.int/health-topics/water-sanitation-and-hygiene-wash",
        },
        {
            "title": "Water risks and resilience",
            "publisher": "UNDRR",
            "url": "https://www.undrr.org/implementing-sendai-framework/sendai-framework-action/water-risks-and-resilience",
        },
    ]
},
"archive/533-waste-and-materials-by-scope-local-collection-regional-recovery-national-producer-responsibility-and-global-hazard-controls.md": {
    "groups": [
        {
            "title": "Circular economy in cities and regions",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/topics/circular-economy-in-cities-and-regions.html",
        },
        {
            "title": "Extended producer responsibility and economic instruments",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/topics/extended-producer-responsibility-and-economic-instruments.html",
        },
        {
            "title": "Global Waste Management Outlook 2024",
            "publisher": "UNEP",
            "url": "https://www.unep.org/resources/global-waste-management-outlook-2024",
        },
        {
            "title": "Basel Convention Overview",
            "publisher": "Basel Convention Secretariat",
            "url": "https://www.basel.int/theconvention/overview/tabid/1271/default.aspx",
        },
        {
            "title": "E-waste Overview",
            "publisher": "Basel Convention Secretariat",
            "url": "https://www.basel.int/implementation/ewaste/overview/tabid/4063/default.aspx",
        },
    ]
},
"archive/534-extractive-resources-by-scope-local-consent-regional-cumulative-impacts-national-public-rents-and-global-just-transition-guardrails.md": {
    "groups": [
        {
            "title": "The UN Secretary-General's Initiative on Critical Energy Transition Minerals",
            "publisher": "United Nations",
            "url": "https://www.un.org/en/climatechange/critical-minerals",
        },
        {
            "title": "Strengthening laws and governance",
            "publisher": "UNEP",
            "url": "https://www.unep.org/topics/extractives/strengthening-laws-and-governance",
        },
        {
            "title": "EITI Standard 2023",
            "publisher": "Extractive Industries Transparency Initiative",
            "url": "https://eiti.org/eiti-standard",
        },
        {
            "title": "Critical minerals",
            "publisher": "UN Trade and Development (UNCTAD)",
            "url": "https://unctad.org/topic/commodities/critical-minerals",
        },
        {
            "title": "Metals and Minerals",
            "publisher": "World Bank Group",
            "url": "https://www.worldbank.org/ext/en/topic/metals-and-minerals",
        },
    ]
},

"archive/535-transport-and-logistics-by-scope-local-streets-metro-transit-regional-corridors-national-networks-and-global-interoperability.md": {
    "groups": [
        {
            "title": "ITF Transport Outlook 2023",
            "publisher": "OECD / International Transport Forum",
            "url": "https://www.oecd.org/en/publications/itf-transport-outlook-2023_b6cc9ad5-en.html",
        },
        {
            "title": "Urban Logistics Hubs",
            "publisher": "OECD / International Transport Forum",
            "url": "https://www.oecd.org/en/publications/urban-logistics-hubs_da4dee9f-en.html",
        },
        {
            "title": "The Future of Public Transport Funding",
            "publisher": "OECD / International Transport Forum",
            "url": "https://www.oecd.org/en/publications/the-future-of-public-transport-funding_82a4ba65-en.html",
        },
        {
            "title": "Air Transport Policy and Regulation",
            "publisher": "International Civil Aviation Organization",
            "url": "https://www.icao.int/air-transport-policy-and-regulation",
        },
        {
            "title": "List of IMO Conventions",
            "publisher": "International Maritime Organization",
            "url": "https://www.imo.org/en/about/conventions/pages/listofconventions.aspx",
        },
    ]
},
"archive/536-oceans-coasts-and-fisheries-by-scope-local-stewardship-regional-seascapes-national-jurisdiction-and-global-high-seas-guardrails.md": {
    "groups": [
        {
            "title": "Oceans and the Law of the Sea",
            "publisher": "United Nations",
            "url": "https://www.un.org/en/global-issues/oceans-and-the-law-of-the-sea",
        },
        {
            "title": "BBNJ Agreement",
            "publisher": "United Nations",
            "url": "https://www.un.org/bbnjagreement/en",
        },
        {
            "title": "Small-scale fisheries governance",
            "publisher": "Food and Agriculture Organization of the United Nations",
            "url": "https://www.fao.org/voluntary-guidelines-small-scale-fisheries/key-thematic-areas/sustainable-resource-management/small-scale-fisheries-governance/en",
        },
        {
            "title": "Pollution Prevention",
            "publisher": "International Maritime Organization",
            "url": "https://www.imo.org/en/ourwork/environment/pages/pollution-prevention.aspx",
        },
        {
            "title": "Target 3: Conserve 30% of Land, Waters and Seas",
            "publisher": "Convention on Biological Diversity",
            "url": "https://www.cbd.int/gbf/targets/3",
        },
    ]
},
"archive/537-outer-space-and-orbital-commons-by-scope-local-hosting-regional-spaceports-national-authorization-and-global-sustainability-guardrails.md": {
    "groups": [
        {
            "title": "The Outer Space Treaty",
            "publisher": "United Nations Office for Outer Space Affairs",
            "url": "https://www.unoosa.org/oosa/en/ourwork/spacelaw/treaties/outerspacetreaty.html",
        },
        {
            "title": "Long-term Sustainability of Outer Space Activities Information Repository",
            "publisher": "United Nations Office for Outer Space Affairs",
            "url": "https://lts.unoosa.org/",
        },
        {
            "title": "The Space2030 Agenda: Space as a Driver of Sustainable Development",
            "publisher": "United Nations Office for Outer Space Affairs",
            "url": "https://www.unoosa.org/oosa/en/ourwork/space4sdgs/space2030agenda.html",
        },
        {
            "title": "Working Group on the \"Space2030\" Agenda",
            "publisher": "United Nations Office for Outer Space Affairs",
            "url": "https://www.unoosa.org/oosa/en/ourwork/copuos/working-group-on-the-space2030-agenda.html",
        },
        {
            "title": "Space Law Treaties and Principles",
            "publisher": "United Nations Office for Outer Space Affairs",
            "url": "https://www.unoosa.org/oosa/en/ourwork/spacelaw/treaties.html",
        },
    ]
},
"archive/538-money-and-payments-by-scope-local-cash-access-municipal-acceptance-national-public-money-and-global-interoperability.md": {
    "groups": [
        {
            "title": "Financial Infrastructure",
            "publisher": "World Bank Group",
            "url": "https://www.worldbank.org/ext/en/topic/financial-sector/financial-infrastructure",
        },
        {
            "title": "Government-to-person (G2Px)",
            "publisher": "World Bank Group",
            "url": "https://www.worldbank.org/en/programs/g2px",
        },
        {
            "title": "CPMI Cross-border payments programme",
            "publisher": "Bank for International Settlements",
            "url": "https://www.bis.org/cpmi/cross_border.htm",
        },
        {
            "title": "Access to and acceptance of cash",
            "publisher": "European Central Bank",
            "url": "https://www.ecb.europa.eu/euro/cash_strategy/acceptance-cash/html/index.en.html",
        },
        {
            "title": "The Global Findex Database 2025",
            "publisher": "World Bank Group",
            "url": "https://www.worldbank.org/en/publication/globalfindex",
        },
    ]
},
"archive/539-banking-credit-and-financial-stability-by-scope-local-relationship-lending-regional-development-finance-national-prudential-oversight-and-global-backstops.md": {
    "groups": [
        {
            "title": "Core Principles for effective banking supervision",
            "publisher": "Bank for International Settlements / Basel Committee on Banking Supervision",
            "url": "https://www.bis.org/bcbs/publ/d573.htm",
        },
        {
            "title": "Key Attributes of Effective Resolution Regimes for Financial Institutions (revised version 2024)",
            "publisher": "Financial Stability Board",
            "url": "https://www.fsb.org/2024/04/key-attributes-of-effective-resolution-regimes-for-financial-institutions-revised-version-2024/",
        },
        {
            "title": "Financial Infrastructure",
            "publisher": "World Bank Group",
            "url": "https://www.worldbank.org/ext/en/topic/financial-sector/financial-infrastructure",
        },
        {
            "title": "The Global Findex Database 2025",
            "publisher": "World Bank Group",
            "url": "https://www.worldbank.org/en/publication/globalfindex",
        },
        {
            "title": "Financial Access Survey (FAS) 2025 Annual Report",
            "publisher": "International Monetary Fund",
            "url": "https://data.imf.org/en/datasets/IMF.STA%3AFAS",
        },
    ]
},
"archive/540-trade-customs-and-border-procedures-by-scope-local-port-interfaces-regional-gateways-national-trade-policy-and-global-rules.md": {
    "groups": [
        {
            "title": "Agreement on Trade Facilitation",
            "publisher": "World Trade Organization",
            "url": "https://www.wto.org/english/docs_e/legal_e/tfa_e.htm",
        },
        {
            "title": "WCO Data Model",
            "publisher": "World Customs Organization",
            "url": "https://www.wcoomd.org/DataModel",
        },
        {
            "title": "Trade facilitation",
            "publisher": "UN Trade and Development (UNCTAD)",
            "url": "https://unctad.org/topic/transport-and-trade-logistics/trade-facilitation",
        },
        {
            "title": "SAFE Framework of Standards 2025",
            "publisher": "World Customs Organization",
            "url": "https://www.wcoomd.org/en/media/newsroom/2025/september/responding-to-emerging-challenges-and-paving-the-way-for-a-secure.aspx",
        },
        {
            "title": "International LPI",
            "publisher": "World Bank Group",
            "url": "https://lpi.worldbank.org/international",
        },
    ]
}
,
"archive/569-addresses-place-names-and-administrative-geography-by-scope-community-legibility-municipal-address-authority-regional-coherence-national-reference-frames-and-no-government-by-phantom-location.md": {
    "groups": [
        {
            "title": "Addressing Solutions",
            "publisher": "Universal Postal Union",
            "url": "https://www.upu.int/en/postal-solutions/programmes-services/addressing-solutions",
        },
        {
            "title": "United Nations Integrated Geospatial Information Framework: Overarching Strategy",
            "publisher": "United Nations Committee of Experts on Global Geospatial Information Management",
            "url": "https://ggim.un.org/UN-IGIF/documents/Part_1_UN-IGIF_Overarching_Strategy_Second_Edition_27Feb2023.pdf",
        },
        {
            "title": "The Global Statistical Geospatial Framework – 2nd Edition 2025",
            "publisher": "United Nations Expert Group on the Integration of Statistical and Geospatial Information",
            "url": "https://ggim.un.org/meetings/GGIM-committee/15th-Session/documents/GSGF_v2_GGIM.pdf",
        },
        {
            "title": "CES 2030 Census Recommendations — Chapter 8 Geospatial information and small area statistics for censuses",
            "publisher": "United Nations Economic Commission for Europe",
            "url": "https://w3.unece.org/recs2030census/webpage11.html",
        },
        {
            "title": "INSPIRE Data Specification on Addresses – Technical Guidelines",
            "publisher": "European Commission / INSPIRE Maintenance and Implementation Group",
            "url": "https://knowledge-base.inspire.ec.europa.eu/publications/inspire-data-specification-addresses-technical-guidelines_en",
        },
        {
            "title": "Authoritative Data in an Evolving Geospatial Landscape: An Exploration of Policy and Legal Challenges",
            "publisher": "United Nations Committee of Experts on Global Geospatial Information Management",
            "url": "https://ggim.un.org/meetings/GGIM-committee/13th-Session/documents/E_C20_2023_16_Add%202-Authoritative_Data_in_an_Evolving_Geospatial_Landscape_20Jul2023.pdf",
        }
    ]
}

,
"archive/568-land-administration-and-cadastre-by-scope-community-witnessing-municipal-parcel-service-regional-coordination-national-tenure-rules-and-no-government-by-documentary-dispossession.md": {
    "groups": [
        {
            "title": "Voluntary Guidelines on Responsible Governance of Tenure of Land, Fisheries and Forests in the Context of National Food Security (VGGT)",
            "publisher": "Food and Agriculture Organization of the United Nations",
            "url": "https://www.fao.org/land-water/land/land-governance/land-resources-planning-toolbox/category/details/en/c/1043060/",
        },
        {
            "title": "United Nations Expert Group on Land Administration and Management",
            "publisher": "United Nations Committee of Experts on Global Geospatial Information Management",
            "url": "https://ggim.un.org/Expert-Group-LAM.cshtml",
        },
        {
            "title": "Enhancing Public Sector Performance: Malaysia’s Experience with Transforming Land Administration",
            "publisher": "World Bank Group",
            "url": "https://documents.worldbank.org/curated/en/928151510547698367/pdf/121243-REVISED-World-Bank-Report-06-Land-Administration-FA-FULL-Web-V2.pdf",
        },
        {
            "title": "ECE Guidelines on Real Property Units and Identifiers",
            "publisher": "United Nations Economic Commission for Europe",
            "url": "https://unece.org/housing-and-land-management/publications/ece-guidelines-real-property-units-and-identifiers",
        },
        {
            "title": "Social Tenure Domain Model",
            "publisher": "Global Land Tool Network",
            "url": "https://stdm.gltn.net/",
        }
    ]
}
,
"archive/541-government-by-scope-micro-local-stewardship-municipal-professionalism-metropolitan-democracy-regional-capacity-national-guarantees-and-global-narrow-waists.md": {
    "groups": [
        {
            "title": "Recommendation CM/Rec(2023)5 of the Committee of Ministers to member States on the principles of good democratic governance",
            "publisher": "Council of Europe",
            "url": "https://search.coe.int/cm/Pages/result_details.aspx?ObjectId=0900001680ac77e4",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-for-local-self-government-english-version-pdf-a6-59-p/16807198a3",
        },
        {
            "title": "OECD Principles on Urban Policy",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/about/programmes/oecd-programme-on-national-urban-policy/oecd-principles-on-urban-policy.html",
        },
        {
            "title": "Navigating conflict and fostering co-operation in fiscal federalism",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/publications/navigating-conflict-and-fostering-co-operation-in-fiscal-federalism_3d5c8c20-en.html",
        },
        {
            "title": "Federalism",
            "publisher": "International IDEA",
            "url": "https://www.idea.int/sites/default/files/publications/federalism-primer.pdf",
        },
        {
            "title": "UN Charter",
            "publisher": "United Nations",
            "url": "https://www.un.org/en/about-us/un-charter",
        },
        {
            "title": "International health regulations",
            "publisher": "World Health Organization",
            "url": "https://www.who.int/health-topics/international-health-regulations",
        }
    ]
}
,
"archive/729-ratification-packets-for-ideal-government-scope-shifts-proof-weights-consent-ladders-double-legitimacy-and-no-function-move-by-wrong-organ.md": {
    "groups": [
        {
            "title": "Assigning responsibilities across levels of government",
            "publisher": "OECD",
            "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2018/09/assigning-responsibilities-across-levels-of-government_d3650b01/f0944eae-en.pdf",
        },
        {
            "title": "Effective Public Investment Toolkit",
            "publisher": "OECD",
            "url": "https://www.oecd.org/en/about/projects/effective-public-investment-toolkit.html",
        },
        {
            "title": "Effective Public Investment Across Levels of Government",
            "publisher": "OECD",
            "url": "https://legalinstruments.oecd.org/public/doc/302/302.en.pdf",
        },
        {
            "title": "European Charter of Local Self-Government",
            "publisher": "Council of Europe",
            "url": "https://rm.coe.int/european-charter-of-local-self-government-eng/1680a87cc3",
        },
        {
            "title": "Protocol (No 2) on the application of the principles of subsidiarity and proportionality",
            "publisher": "EUR-Lex / European Union",
            "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX%3A12008E%2FPRO%2F02",
        },
        {
            "title": "The principle of subsidiarity",
            "publisher": "EUR-Lex / European Union",
            "url": "https://eur-lex.europa.eu/EN/legal-content/summary/the-principle-of-subsidiarity.html",
        },
        {
            "title": "Multi-Level Governance Reforms",
            "publisher": "OECD",
            "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2017/05/multi-level-governance-reforms_g1g77b03/9789264272866-en.pdf",
        }
    ]
}


}


def normalize_group(group: dict) -> dict:
    title = " ".join(str(group.get("title", "")).split())
    publisher = " ".join(str(group.get("publisher", "")).split())
    url = str(group.get("url", "")).strip()
    if url:
        parts = urlsplit(url)
        filtered_query = []
        for key, value in parse_qsl(parts.query, keep_blank_values=True):
            low = key.lower()
            if low.startswith("utm_") or low in {"fbclid", "gclid", "mc_cid", "mc_eid", "ref", "ref_src"}:
                continue
            filtered_query.append((key, value))
        query = urlencode(filtered_query, doseq=True)
        url = urlunsplit((parts.scheme, parts.netloc, parts.path, query, ""))
        if url.endswith("/"):
            url = url.rstrip("/")
    return {"title": title, "publisher": publisher, "url": url}


def dedupe_groups(notes: dict[str, dict]) -> dict[str, dict]:
    cleaned = {}
    for note, payload in notes.items():
        seen = set()
        groups = []
        for raw_group in payload.get("groups", []):
            group = normalize_group(raw_group)
            key = (group.get("title"), group.get("publisher"), group.get("url"))
            if key in seen:
                continue
            seen.add(key)
            groups.append(group)
        cleaned[note] = {"groups": groups}
    return cleaned


def main() -> None:
    seed = json.loads((ROOT / "SOURCES.json").read_text(encoding="utf-8"))
    notes = dict(seed.get("notes", {}))
    notes.update(NEW_NOTE_SOURCES)
    notes = dedupe_groups(notes)
    data = {
        "revision": CURRENT_REV,
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "notes": notes,
    }
    (ROOT / "SOURCES.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print("OK: wrote SOURCES.json")


if __name__ == "__main__":
    main()
