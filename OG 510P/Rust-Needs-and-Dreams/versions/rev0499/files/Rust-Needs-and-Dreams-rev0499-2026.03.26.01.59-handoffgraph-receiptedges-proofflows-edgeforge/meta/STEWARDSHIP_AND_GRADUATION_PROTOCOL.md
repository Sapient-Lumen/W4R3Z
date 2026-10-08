# Stewardship and graduation protocol

## Purpose
Use this protocol when the repo is not merely asking **what is worthy**, **what should be built first**, **what vehicle should it start in**, or **what operator grammar it should expose**, but also:
- where the contribution should actually live as it matures;
- what should remain companion-first;
- what belongs as raw fact in Cargo/rustc/docs.rs/crates.io or other first-party/service surfaces;
- what might deserve optional toolchain distribution;
- and what only becomes credible through project- or consortium-grade stewardship.

Read with:
- `design/epic-contribution-stewardship-and-graduation-map-2026Q1.md`
- `design/epic-contribution-operating-surface-2026Q1.md`
- `design/epic-contribution-worthy-repo-buildout-2026Q1.md`
- `design/epic-contribution-incubation-map-2026Q1.md`
- `design/epic-contribution-boundary-map-2026Q1.md`
- `design/epic-contribution-decision-rights-map-2026Q1.md`
- `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`
- `meta/AMNESIA_RESISTORS.md`

## Required moves
1. Re-open the nearest canon before inventing a new maturity story.
   - read the current broad ranking, buildout order, incubation map, boundary map, decision-rights map, and operating-surface note.
   - do not answer a graduation question from one fresh source or one local instinct.

2. Separate five different homes explicitly.
   For each serious seam, distinguish:
   - product home now;
   - raw-fact or authority home;
   - plausible future graduation home;
   - long-run stewardship home;
   - refused graduation move.

3. Prefer primary sources that reveal residency or maintenance posture.
   Prioritize sources that show:
   - upstream compatibility boundaries;
   - custom subcommand or extension posture;
   - optional toolchain component examples;
   - service-owned truth surfaces;
   - specification/reference stewardship;
   - consortium/foundation or institutional ownership.

4. Default to split-home designs before monolith fantasies.
   - raw facts may belong upstream while review/doctor/waive/diff logic stays companion-first;
   - service truth may remain service-side while operator review stays local;
   - consortium-maintained corpora may sit above companion exporters and upstream hooks.

5. Use optional toolchain distribution sparingly.
   Treat the Clippy-like shape as real but rare.
   Only recommend it when broad reach matters more than rapid independent cadence and when the proof burden is already unusually high.

6. Promote only the compatibility-bearing substrate.
   If a contribution earned upstream asks, ask for:
   - fact surfaces;
   - stable IDs;
   - structured machine outputs;
   - bounded contracts.
   Do **not** ask to upstream the whole product unless the authority itself must live there.

7. Keep service truth distinct from review truth.
   A registry or docs host can expose authoritative service facts without becoming the whole product or policy answer.

8. Move renewal-heavy commons into durable stewardship on purpose.
   If a seam depends on cross-organization maintenance, qualification posture, or long-horizon acceptance corpora, say so explicitly and route it toward project/foundation/consortium ownership rather than endless companion drift.

9. Update continuity rails in the same revision.
   At minimum refresh:
   - `AGENTS.md`
   - `INDEX.md`
   - `PRIORITIES.md`
   - `RESEARCH_LOG.md`
   - `STRATEGIC_FRONTIER.md`
   - `meta/ACTIVE_FRONTIER.md`
   - `meta/CANONICAL_WORKING_SET.md`
   - `meta/LATEST_REVISION_FILESET.md`
   - `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`
   - `meta/REVISION_OPERATING_PROTOCOL.md`
   - `meta/AMNESIA_RESISTORS.md`
   - `atlases/portfolio-source-atlas-v0/sources.json`

## Default interpretation rules
- do not confuse incubation vehicle with end-state stewardship;
- do not treat optional toolchain distribution as equivalent to Cargo core;
- do not treat service truth as complete ecosystem judgment;
- do not keep canonical-substrate work forever in an external repo once authority is the real missing piece;
- do not centralize review or policy logic merely because raw facts became available upstream;
- and do not route a consortium-shaped commons into one vendor or one assistant-maintained archive view.

## Failure modes
### Failure mode 1: everything graduates into Cargo
This usually means the archive noticed importance but forgot compatibility burden and split-home design.

### Failure mode 2: service truth impersonates product truth
A registry security tab or docs host JSON surface is not the same thing as a review boundary or compatibility program.

### Failure mode 3: companion drift without stewardship
Some work should remain companion-first; some should not remain forever-prototype once authority or coalition maintenance becomes the bottleneck.

### Failure mode 4: toolchain distribution as prestige theater
Optional distribution should solve reach and compatibility needs, not serve as a status upgrade.

### Failure mode 5: consortium work flattened into a crate
If the real challenge is shared renewal, qualification posture, or tuple acceptance, one binary will not solve it.

## Preferred output shape for future revisions
When adding a stewardship/graduation refinement, prefer sections in this order:
1. what changed in the external signal;
2. what homes are available now;
3. what split-home design is recommended;
4. what can plausibly graduate later;
5. what must stay service-side or canonical;
6. what needs durable stewardship;
7. what tempting graduation move should be refused.
