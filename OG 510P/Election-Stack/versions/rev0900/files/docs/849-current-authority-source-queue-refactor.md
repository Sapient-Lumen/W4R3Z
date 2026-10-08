# 849 — Current-authority source queue refactor

**Track:** Shared / Source freshness / Refactor  
**Status:** v844 audit/refactor helper  
**Scope:** `scripts/report_current_authority_source_queue.py`, `artifacts/reports/current-authority-source-queue-rev0844.json`, `artifacts/reports/source-review-pressure-rev0844.json`, `artifacts/reports/platform-source-tail-rev0844.json`

## Why this exists

v842 and v843 showed that the 30-day source-review pressure is not one queue. Most of the near-term rows are platform/UI/vendor pages. Those should be consolidated, sampled, or demoted before maintainers burn hours reviewing mutable help pages one by one.

The smaller but riskier set is the current-authority queue: election authority, cyber authority, accessibility/right-to-vote authority, official public communications, and state/local authority references. These rows are more likely to affect what an adopter thinks is current, official, or voter-relevant.

## v844 generated queue

Run:

```bash
python3 scripts/report_current_authority_source_queue.py
```

Current v844 output:

- `current_authority_due_count`: 147
- `federal_election_authority`: 58
- `state_or_local_authority`: 29
- `federal_cyber_authority`: 26
- `official_public_comms_authority`: 15
- `accessibility_or_rights_authority`: 9
- `federal_standards_or_ai_authority`: 9
- `other_current_authority`: 1

Companion pressure reports remain:

- expired source-review windows: 0
- due within 30 days: 893
- platform/UI/vendor due within 30 days: 720
- source-pressure current-authority lane: 142

The 147/142 difference is intentional: this report includes a few state/local and host-based authority rows that the broader pressure-lane classifier separates or classifies differently.

## Maintainer action order

1. Review or pin federal election-authority rows first when they support standards, certification, VVSG, EAC, or election-administration claims.
2. Review CISA/election-security and NIST/AI/cyber rows next when they support verifier, AI, or cyber-control claims.
3. Review state/local authority rows before any local adoption or voter-facing use.
4. Treat platform/UI/vendor rows as a consolidation/sampling lane, not as a 720-click release blocker.
5. Do not extend `review_by` mechanically. Each extension needs one of: pinned bytes, currentness note, demotion from current authority to background context, or replacement with a more durable source.

## Boundary

This report does not refresh sources, prove current voter instructions, prove current law, or authorize live-pilot/legal reliance. It is a maintainer attention map so the next source pass starts with the references most likely to hurt trust if stale.
