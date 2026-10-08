# 846 — Retirement and merge docket for Radical Governance: canon waists, active notes, supersession labels, source hygiene, and no archive by immortal note

## One-line thesis

The archive should now maintain an explicit retirement and merge docket: keep the canon waists active, mark adjacent restatements as superseded or merge candidates when they stop being first citation points, repair source hygiene by class rather than by panic, and refuse the fiction that every numbered note remains equally current forever.

## Why this matters

The archive has become valuable enough to need maintenance law. Without a retirement docket, every note remains notionally alive, every compression layer competes with every other layer, and readers must guess which formulation is first-line.

This note does not delete the archive’s history. It creates a public record of how to slim without vandalizing the research trail. The goal is not minimalism for its own sake. The goal is lower future reading cost, clearer authority, and fewer duplicative surfaces.


## Rev0713 applied docket pointer

The first applied use of this retirement logic is `847`, which consolidates the broad scope-answer cluster without deleting older notes. Use that pass as the model for future status labels: first map citation order, then mark supersession, then defer hard machine-readable status until case use proves the labels.

## Pattern pack

### 1. Use four retirement labels

| Label | Meaning | Reader instruction |
| --- | --- | --- |
| **active** | current first-line or still directly useful | cite normally |
| **superseded** | preserved for history but no longer first citation point | cite only for lineage or a detail not carried forward |
| **merge candidate** | should be folded into a canon waist, source index, or nearby note | do not create adjacent notes until merge is considered |
| **burial candidate** | obsolete, misleading, or duplicative enough that preservation imposes net cost | preserve only if a historical reason remains |

Labels should be reversible. A note can return to active status if a case shows it carries a still-needed lens.

### 2. Current canon-waist status

| Note or range | Proposed status | Reason |
| --- | --- | --- |
| `841` | active canon waist | pocket answer for ideal governments by scope |
| `790` | active long canon waist | longer dispatch and answer-key table |
| `842`–`843` | active operating canon | audit and growth discipline |
| `844` | active opposition waist | required adversarial layer for strong defaults |
| `845` | active case-packet docket | applied-test queue for doctrine |
| `846` | active maintenance docket | retirement and merge discipline |
| `825`–`840` | active lens run | regime form through preemption defaults; cite only the live lens |
| `848` | active cross-boundary dispatcher | first stop before using the `812`–`824` chain |
| `812`–`824` | active cross-boundary chain run, dispatcher-installed | form-choice machinery for compact, connector, and shared-system bodies; cite only live chain fields through `848` |
| `791`–`811` | active benchmark and assessment run, but consolidation candidate after use | valuable, but should be merged into a slimmer assessment manual once case packets reveal which parts are actually used |
| `403`–`438` | active source-repaired digital/public-AI domain run | now has source-waist coverage; should not be expanded unless a live case needs the module |

This is a docket, not a final deletion order.

### 3. Immediate merge candidates

| Cluster | Candidate action | Why |
| --- | --- | --- |
| repeated scope-answer formulations around `541`, `565`, `579`, `628`–`631`, `660`, `790`, `841` | mark older broad-scope statements as superseded-first-citation by `841` and `790` | preserve discovery path but stop readers from treating every compression as equal |
| benchmark, drill, maintenance, proof, intervention, contestability, comparator, mission, finding, response, close-out, tracer, sampling, evidence, independence, calibration notes `791`–`808` | later fold into one assessment manual or machine-readable checklist | the sequence is useful but too many adjacent process notes can become operational fog |
| form-choice and chain templates `812`–`824` plus dispatcher `848` | keep active for now; test `848` through applied packets before considering a single cross-boundary-form manual | the chain structure is powerful, but likely over-granular without a first stop |
| default run `825`–`840` | keep active; add a one-page dispatcher rather than more adjacent defaults | each lens is distinct, but the run should not keep growing by analogy |
| source-waist repair materials | keep in `SOURCES` and source JSON, not in numbered notes unless judgment changes | source repair should not become doctrine bloat |

The archive should prefer labeled consolidation over deletion until case use shows what is truly redundant.

### 4. Source-hygiene classes

Source maintenance should use classes rather than a single panic button.

| Class | Trigger | Action |
| --- | --- | --- |
| **current anchor** | official or high-quality source still current and useful | keep |
| **stale but harmless** | older source still historically useful | keep, but avoid making it first anchor |
| **stale and misleading** | law, policy, or institutional page has changed | replace or add warning in source entry |
| **PDF-only anchor** | source is a PDF but no durable HTML alternative exists | keep cited link; do not download or store the PDF |
| **secondary explainer** | useful background but not authority | keep only if primary source is also present |
| **dead or moved** | link fails or redirects to generic page | replace, use archive only if absolutely necessary, and mark the replacement date |
| **over-padded** | many sources repeat the same proof | reduce to the most probative sources |

This keeps the archive from confusing source quantity with source quality.

### 5. Do not let generated surfaces become authority

`ARCHIVE_INDEX.json`, `THREADS.md`, `THREAD_SUMMARY.json`, `CONTROL_SURFACES.json`, `ASSURANCE_ARTIFACTS.json`, `LIFECYCLE_GATES.json`, `RELEASES.json`, and `MANIFEST.json` are routing and integrity surfaces. They should help readers find notes, see tags, and verify package state. They should not decide doctrine.

If a generated tag says a note is about a topic, that means the string matcher found enough evidence to route attention. It does not mean the archive has made a doctrinal judgment under that tag.

### 6. Install the no-immortal-note rule

Every numbered note should be eligible for one of three future actions:

1. stay active because it is used;
2. become superseded because a better waist exists;
3. become a merge or burial candidate because it increases reading cost more than decision value.

A note that is never allowed to change status is not an archive note. It is a relic.

### 7. Merge before adding adjacent doctrine

Before adding a new note in any dense cluster, future work should ask:

- Can this be a paragraph inside `841`, `790`, `843`, `844`, `845`, or `846`?
- Can it be a source entry rather than a note?
- Can it be a case-packet field rather than a universal doctrine?
- Can it be a checklist item in an existing assessment run?
- Does it demote, retire, or clarify an older note?

Only if the answer is no should a new numbered note exist.

### 8. Use retirement as an audit event

A retirement label should include:

| Field | Content |
| --- | --- |
| note or cluster | file number, range, or theme |
| proposed label | active, superseded, merge candidate, burial candidate |
| replacement first stop | where readers should go first |
| preservation reason | why the old note remains useful, if it does |
| risk of retirement | what knowledge might be lost |
| review clock | when or after which case packets to revisit |

Retirement is a public-record event, not a silent housekeeping change.

### 9. Machine-readable status after applied contrast

The docket originally warned against premature `NOTE_STATUS.json`. That warning has now been satisfied by applied use: `849` tested the strong bounded-authority case, `850` tested the thinner shared-service-backbone case, `851` tested the middle basin / flood-risk-platform case, `852` tested the asset-heavy utility case, and `853` tested the contract-heavy P3 / crossing case. A machine-readable status layer is therefore justified, but only as a reversible routing surface.

`NOTE_STATUS.json` should name first-citation points, active-via-dispatcher chains, superseded-first-citation notes, and consolidation candidates. It must not become deletion authority. A note can return to active status if an applied packet proves that it still carries a live lens.

### 10. Immediate operating rule

Use this order:

1. answer broad scope questions from `841` and `790`;
2. test defaults through `844` before strengthening them;
3. choose real cases from `845` before adding more universal doctrine;
4. use `848` before entering the `812`–`824` cross-boundary chain;
5. read `849` through `855` as contrast packets before thickening, thinning, platforming, asset-ring-fencing, contract-hardening, enforcing, or treaty-waisting a cross-boundary form;
6. use this note and `NOTE_STATUS.json` before creating adjacent notes in dense clusters;
7. repair sources in `sources/source_catalog.json` and source keys in `sources/source_keys.json` rather than widening note text;
8. let generated indexes route attention but not settle authority.

## Failure modes

- **retirement theater**: labels are created but no reader behavior changes.
- **deletion vandalism**: useful historical path is removed before a replacement is stable.
- **metadata freeze**: machine labels make a temporary judgment look permanent.
- **source hoarding**: source indexes grow because nobody wants to decide which anchors matter.
- **manual sprawl**: consolidation turns many short notes into one unreadable mega-document.
- **tag overread**: generated tags are treated as doctrinal classifications.

## Anti-theater tests

1. Can a reader tell the first citation point for the broad scope answer?
2. Can a reader tell which dense clusters are candidates for consolidation?
3. Does a proposed retirement label include a replacement first stop?
4. Does source repair change grounding without importing bulky artifacts?
5. Does the archive preserve enough lineage to explain why it changed?
6. Does the docket reduce future note creation?

## Reconstruction instruction

The next reconstruction pass should test `854` and `855` now satisfy pure regulatory / enforcement power and treaty / global narrow-waist governance. The next pass should audit consolidation of the `812`–`824` chain rather than expanding it. Statuses should stay visible, reversible, and subordinate to the case matrix.
