# rev0871 quarantined-source public-surface firewall and state/local example boundaries

**Track:** Shared / source-use safety / voter-facing public surfaces / release-gate drift control  
Status: synthetic release-gate audit; not current voter instruction, not legal advice, not source-byte cache completeness, not public-guidance authorization, and not live-pilot evidence.

## Why this was the riskiest next cut

Rev0868 quarantined 70 mutable state/local source rows. Rev0869 turned those rows into an adopter authority-capture no-go queue. Rev0870 added a capture-record validator. That still left one fail-open path: a maintainer could edit a voter-facing evidence-surface document and put quarantined state/local rows under a heading such as “current official sources” or “authoritative public examples,” making an example route look like current voter instruction.

Rev0871 closes that wording path with a concrete scan instead of another registry. The affected documents may still use state/local routes as examples, but the examples must be framed as official route examples only and must carry a local non-instruction boundary. The promotion path remains adopter-specific capture evidence plus validator pass.

## Files changed

Added:

- `scripts/check_quarantined_source_public_surface_firewall.py`
- `artifacts/reports/quarantined-source-public-surface-firewall-report.json`
- `docs/909-quarantined-source-public-surface-firewall-and-state-local-example-boundaries.md`

Updated:

- 21 voter-facing evidence-surface docs in the `docs/317` through `docs/343` range that cite quarantined state/local example routes.
- `scripts/release_gate_steps.py`
- `docs/162-release-and-ci-evidence-pipeline.md`
- current release reports and pre-pilot ledgers for `v871`.

## What the new gate enforces

The gate scans `docs/`, `artifacts/checklists/`, and `artifacts/templates/` for `xref:` citations to lockfile rows tagged both `jurisdiction_quarantine` and `not_current_voter_instruction`.

For each affected public-surface document, the gate requires:

1. a `STATE_LOCAL_QUARANTINE_BOUNDARY:` marker;
2. a source-section heading that says `Sources (official route examples; not current voter instruction)` rather than authoritative/current-source language;
3. no risky active-claim paragraph around quarantined xrefs unless the paragraph itself carries the non-instruction boundary, except compact source-list bullets covered by the marked source section; and
4. a generated report matching the current working tree.

The generated report currently records 21 affected public-surface docs and 139 quarantined-source references. It is a wording and drift firewall, not source freshness or source-byte verification.

## Source-use boundary

The online public-authority context continues to support this conservative framing. EAC’s state-registration/voting page says states and territories administer elections differently and routes readers to state and local election-office information. EAC’s “who is in charge” explainer says election administration varies by state and often by county, city, or township. The EAC/CISA public-communications guide is explicitly for state, local, tribal, and territorial election officials as primary official-information sources. Inside this cube, those facts support routing and adopter capture; they do not support copying mutable state/local pages into public answers without local capture, scope, conflict review, and human approval. (xref: `eac_register_and_vote_in_your_state_page`; xref: `eac_who_is_in_charge_of_elections_in_my_state_page`; xref: `eac_enhancing_election_security_public_comms_2024_pdf`)

## Why this is substance, not bureaucracy

The change removes a concrete misuse path from the docs themselves. A later maintainer cannot accidentally move quarantined state/local examples back into public-answer prose as if they were current instructions without breaking the release gate. A reviewer also no longer has to read every long voter-surface document to see whether the state/local quarantine survived the edit; the report lists exactly where the references remain.

## Remaining work

The remaining hard work is still adopter-specific:

- choose a real adopter jurisdiction;
- capture the exact official page or official channel for that jurisdiction and election/effective-date scope;
- store byte/text hash evidence;
- resolve conflicts across state, county, local, form, FAQ, and help-channel surfaces;
- record responsible office and public help route;
- obtain human approval; and
- validate the capture record before promotion.

Until then, the 70 quarantined rows remain example official routes only. They are not current voter instruction, legal authority, current-law advice, source-byte cache completeness, publication authorization, certification, independent validation, or live-pilot readiness.
