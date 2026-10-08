# Meta: Live Ecosystem Refresh Protocol (rev0489)

## Purpose
Use this protocol when the archive needs to answer a question like:
- what is ideal Rust still missing **right now**;
- what does the **latest archive + latest official ecosystem signals** imply together;
- what current worthy contribution should be built, deepened, held, folded, or refused;
- or what meta-hygiene should govern archive answers that rely on fresh public Rust material.

This protocol is **not** the broad ladder.
It is **not** a live packet.
It is **not** a substitute for reading the current dossiers and packets.
It exists to stop future revisions from doing one of two bad things:
- pretending the archive can answer “latest” from memory; or
- pretending one fresh blog post, survey summary, or current controversy settles the whole strategy map.

Read with:
- `design/epic-contribution-live-ecosystem-refresh-2026Q1.md`
- `design/epic-contribution-live-decision-packets-2026Q1.md`
- `design/epic-contribution-candidate-dossiers-2026Q1.md`
- `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`
- `meta/REVISION_OPERATING_PROTOCOL.md`
- `meta/AMNESIA_RESISTORS.md`
- `RESEARCH_LOG.md`
- `atlases/portfolio-source-atlas-v0/sources.json`

## Default rule
A healthy live-refresh answer must keep five truths visibly separate:
1. **unchanged canon** — what the archive still believes;
2. **fresh external signal** — what official or primary sources say now;
3. **changed interpretation** — what moved because of those signals;
4. **current packet posture** — what is `advance`, `deepen`, `hold`, `fold`, or `kill` now;
5. **meta-hygiene** — how the assistant should avoid flattening the above into one smooth story.

If those truths blur together, the refresh is lossy even if the prose sounds confident.

## Required moves for a live-refresh revision

### 1) Re-open the current archive before browsing outward
Minimum read set:
- `AGENTS.md`
- `INDEX.md`
- `PRIORITIES.md`
- `RESEARCH_LOG.md`
- `STRATEGIC_FRONTIER.md`
- `meta/ACTIVE_FRONTIER.md`
- `meta/CANONICAL_WORKING_SET.md`
- current dossier / packet files if the answer touches present-tense posture.

### 2) Use fresh, primary, and date-explicit sources
For live Rust ecosystem refreshes, prefer:
- official Rust blog posts;
- Inside Rust posts;
- Rust Project Goals pages;
- Cargo/Rust docs;
- Rust Foundation or other primary stewardship sources when the claim is about funding, stewardship, or institutional support.

Record exact source dates in the research log or the source atlas.
Never leave “the latest survey”, “the current challenges writeup”, or “the new Cargo work” uncited or undated.

### 3) Keep source-candor explicit
A live-refresh source may be:
- strong for pain categories but weak for exact technical requirements;
- strong for roadmap direction but weak for present availability;
- or current but itself part of the story because of controversy, retraction, or unusual scope.

Say so.
Do not let currentness impersonate scope fitness.

### 4) Keep strategy separate from present-tense action
A worthy contribution can be strategically important and still currently deserve `hold`.
A current `advance` can be narrower than the larger dream it points toward.
A live-refresh revision must say which question it is answering:
- broad strategic importance;
- current delivery priority;
- or archive-operating / meta-hygiene.

### 5) Treat surveys/interviews as pain maps, not final kernel specs
Survey and interview material is excellent for:
- identifying recurring pain categories;
- validating that a problem is broad rather than idiosyncratic;
- identifying domains that need deeper work.

It is weaker for:
- deciding exact command/file/schema/kernel surfaces by itself;
- proving that one implementation shape has already won;
- or justifying hosted platform sprawl.

### 6) Refresh the files that preserve continuity
A non-trivial live-refresh revision should usually update:
- `RESEARCH_LOG.md`
- `meta/LATEST_REVISION_FILESET.md`
- `atlases/portfolio-source-atlas-v0/sources.json`
- the nearest broad design note or latest-refresh note
- and the relevant routing files.

## Failure modes to refuse
- one survey summary becoming the whole ranking rewrite;
- one roadmap/goal page becoming proof that a contribution is already solved;
- one controversial or retracted post becoming general atmosphere rather than scoped evidence;
- one assistant summary becoming a proxy for source-candor;
- current packet posture being silently overwritten by broad strategic enthusiasm;
- recommendation systems being widened without renewed freshness and editorial-capacity accounting.

## Minimum non-claims
A live ecosystem refresh must **not** claim that it:
- replaced the broad ladder unless it explicitly did so;
- superseded the current live packets unless those packets were actually refreshed;
- proved a kernel surface from broad interviews/surveys alone;
- or solved recommendation/renewal burden just by being current.

## Suggested output grammar
A strong live-refresh answer often has this shape:
1. what is unchanged;
2. what current official sources add;
3. what that changes in ranking or delivery posture;
4. what tempting broader move is still refused;
5. what files now govern future answers.

## Why this file exists
The archive already had continuity rails and source-atlas discipline.
What it still lacked was one explicit rule for the particularly failure-prone question:

> “read the latest archive, browse the latest Rust signals, and tell me what ideal Rust still needs.”

That question is too important to answer from memory and too easy to overfit to one current post.