# PILOT-001 decision — DOJ SLS law-enforcement source inventory

Rev0003 selects the first active pilot: the DOJ Civil Rights Division Special Litigation Section law-enforcement source inventory.

The decision is not that DOJ records are complete, neutral, or sufficient. The decision is that they are a strong first **source-graph** substrate: official, public, document-linked, department-level, and full of status/version edge cases that the cube must learn to handle before it ever becomes an officer lookup tool.

## Why this is the first pilot

The seed asks for a national, normalized, longitudinal corpus spanning misconduct, lawsuits, settlements, discipline, decertification, officer mobility, FOIA, news, and civil-society datasets. That end-state is too dangerous to approach by scraping names first. A safer first build is a source graph that can say what public record carriers exist and what they can support.

The DOJ SLS pilot gives the cube:

- findings reports;
- complaints;
- consent decrees;
- settlement agreements;
- technical-assistance letters;
- closing letters;
- court orders;
- monitor/compliance materials;
- enforcement / closed / investigation / statement-of-interest status labels;
- multi-agency and subunit cases;
- political/status drift.

Those are exactly the materials that train the archive to distinguish allegation, finding, remedy, order, settlement, compliance, closure, and current status.

## What is admitted

Rev0003 admits 27 source-carrier rows in `data/source_graph/doj_sls_law_enforcement_agencies.seed.json`.

Each row says, in effect:

> DOJ lists this agency/matter row with these document-class labels and this source-page status label, accessed at this time.

That is all.

## What is not admitted

No row says that misconduct occurred. No row names an officer. No row summarizes a civilian harm. No row creates a lawsuit record. No row creates a settlement record. No row creates a department score.

## Why status drift is central

The pilot immediately reveals a core problem: public accountability sources change over time. A matter may be listed as enforcement, later partially terminated, later closed, while local monitor pages or court dockets preserve a different or more granular status. The cube must preserve historical records and current status separately.

The rule for this pilot is:

- `source_page_status` is what a source page says at access time.
- `status_signal` is a press release, motion, monitor notice, local update, or other cue.
- `court_order_status` is a status grounded in a court order.
- `current_status_candidate` is a display candidate only after recheck.

Public display may not collapse these.

## Success condition

The pilot succeeds if a future revision can generate a public department source inventory page that is useful without being accusatory, stale, or person-extractive.
