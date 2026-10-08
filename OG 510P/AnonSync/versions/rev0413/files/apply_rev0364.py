from pathlib import Path
root = Path('/mnt/data/workrev0364')

readme_add = '''## Revision addendum — transfer-cost truth, resend geometry, and splittability ceiling after rev0363

This revision continues directly from `rev0363` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **piecewise delta transfer, whole-file resend after piece shift, archive-assisted rename reuse, splittable-vs-nonsplittable priority behavior, and queue preemption under download priority**.
2. Tightens the non-clone line again: borrow Resilio's candor that `changed data only`, `whole file again`, `renamed without retransmit`, and `downloaded first` are different truths; refuse any contract where the operator still has to reconstruct `how many bytes will actually move here, why did this file resend in full, and did priority change order or network cost?` from several articles.
3. Adds one new **Resilio evaluation** document focused on why present-day transfer-cost truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for transfer-cost contract sheet, resend-geometry review, byte-cost proof, transfer-shape timeline, and transfer-cost lineage receipt.
5. Makes one hard product decision explicit: **transfer cost is a first-class contract object rather than an optimistic side effect of `syncs only changed data` marketing language.**
6. Makes another hard product decision explicit: **piecewise delta, whole-file resend, archive-hit rename reuse, queue priority, and splittability ceiling are separate truths.**
7. Makes a third hard product decision explicit: **`higher priority` is weaker than `lower byte cost`, and `same bytes under a new pathname` is weaker than `rename reuse is actually proven on this cohort`.**
8. Packages the result as another continuation archive whose new tranche makes the `transfer-cost-contract / resend-geometry-review / byte-cost-proof / transfer-shape-timeline / transfer-cost-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1324-resilio-transfer-cost-resend-geometry-and-splittability-ceiling-fragmentation-evaluation.md`
- `1325-transfer-cost-contract-sheet-page-splittability-reuse-basis-and-order-vs-byte-cost-interface-spec.md`
- `1326-resend-geometry-review-page-piece-shift-rename-reuse-and-archive-gate-interface-spec.md`
- `1327-byte-cost-proof-page-piecewise-delta-full-resend-and-priority-evidence-interface-spec.md`
- `1328-transfer-shape-timeline-page-queue-preemption-archive-hit-and-whole-file-fallback-events-interface-spec.md`
- `1329-transfer-cost-lineage-receipt-page-byte-cost-basis-reuse-path-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's transfer-cost contract**

This time the reason is especially clear around **piecewise delta transfer, full resend after piece-shift edits, archive-assisted rename reuse, and splittable-only priority guarantees**.
Current official materials simultaneously show that:

- current `When a file changes, does Resilio Sync transfer the entire file again, or just the part that's changed?` docs still say Sync splits files into pieces from 32KB up to 2MB, usually sends only changed pieces, but will re-sync the whole file if the edit shifts all pieces
- those same current docs still say the stronger `avoid whole-file resend even after shift` sentence belongs to the separate Sync Business diff-delta lane rather than the ordinary baseline
- current `What happens when file is renamed` docs still say rename reuse depends on the remote peer finding the same hash in Archive and that without Archive enabled the file will be re-synced again
- current `File download priority` docs still say priority can reorder the active queue by mtime or size, can suspend lower-priority downloads immediately, but strictly follows the prioritization rules only for files that are split in pieces during transfer
- those same current priority docs still say queue rebuilds and the 50k active-file ceiling can change performance independently of the actual byte cost of any one file

That candor is useful.
The transfer-cost contract is the problem.
AnonSync should not clone a world where the operator still has to translate `sync only changed data`, `rename`, `priority`, `suspended`, `large file`, and `archive` into one stable answer about byte-cost class, reuse basis, splittability class, queue order, and blocked stronger sentence by stitching together several KB articles.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because transfer cost is a real contract with separate truths for byte-cost class, rename-reuse basis, splittability ceiling, and queue order, but the present contract still scatters the answer to `how many bytes will actually move, why did this resend in full, and did priority change only order or also cost?` across several KB articles instead of owning it as one stable page family.**
'''

eval_add = '''## Revision addendum — transfer-cost truth, resend geometry, and splittability ceiling after rev0363

This revision continues directly from `rev0363` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **piecewise delta transfer, whole-file resend after piece shift, archive-assisted rename reuse, splittable-vs-nonsplittable priority behavior, and queue preemption under download priority**.
2. Tightens the non-clone line again: borrow Resilio's candor that `changed data only`, `whole file again`, `renamed without retransmit`, and `downloaded first` are different truths; refuse any contract where the operator still has to reconstruct `how many bytes will actually move here, why did this file resend in full, and did priority change order or network cost?` from several articles.
3. Adds one new **Resilio evaluation** document focused on why present-day transfer-cost truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for transfer-cost contract sheet, resend-geometry review, byte-cost proof, transfer-shape timeline, and transfer-cost lineage receipt.
5. Makes one hard product decision explicit: **transfer cost is a first-class contract object rather than an optimistic side effect of `syncs only changed data`.**
6. Makes another hard product decision explicit: **piecewise delta, whole-file resend, archive-hit rename reuse, queue priority, and splittability ceiling are separate truths.**
7. Makes a third hard product decision explicit: **`higher priority` is weaker than `lower byte cost`, and `same bytes under a new pathname` is weaker than `rename reuse is actually proven on this cohort`.**
8. Packages the result as another continuation archive whose new tranche makes the `transfer-cost-contract / resend-geometry-review / byte-cost-proof / transfer-shape-timeline / transfer-cost-receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's transfer-cost contract**

This time the reason is especially clear around **piecewise delta transfer, full resend after piece-shift edits, archive-assisted rename reuse, and splittable-only priority guarantees**.
Current official materials simultaneously show that:

- current `When a file changes, does Resilio Sync transfer the entire file again, or just the part that's changed?` docs still say Sync splits files into pieces from 32KB up to 2MB, usually sends only changed pieces, but will re-sync the whole file if the edit shifts all pieces
- those same current docs still say the stronger `avoid whole-file resend even after shift` sentence belongs to the separate Sync Business diff-delta lane rather than the ordinary baseline
- current `What happens when file is renamed` docs still say rename reuse depends on the remote peer finding the same hash in Archive and that without Archive enabled the file will be re-synced again
- current `File download priority` docs still say priority can reorder the active queue by mtime or size, can suspend lower-priority downloads immediately, but strictly follows the prioritization rules only for files that are split in pieces during transfer
- those same current priority docs still say queue rebuilds and the 50k active-file ceiling can change performance independently of the actual byte cost of any one file

That candor is useful.
The transfer-cost contract is the problem.
AnonSync should not clone a world where the operator still has to translate `sync only changed data`, `rename`, `priority`, `suspended`, `large file`, and `archive` into one stable answer about byte-cost class, reuse basis, splittability class, queue order, and blocked stronger sentence by stitching together several KB articles.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because transfer cost is a real contract with separate truths for byte-cost class, rename-reuse basis, splittability ceiling, and queue order, but the present contract still scatters the answer to `how many bytes will actually move, why did this resend in full, and did priority change only order or also cost?` across several KB articles instead of owning it as one stable page family.**
'''

score_add = '''## Revision addendum — transfer-cost scorecard after rev0363

The new evaluated seam is **transfer cost / resend geometry / splittability ceiling**.

| Seam | Current Resilio posture | Borrow / clone / reject | Why | Required AnonSync pages |
| --- | --- | --- | --- | --- |
| Piecewise delta transfer, whole-file resend on piece shift, archive-assisted rename reuse, queue priority, and splittable-only priority guarantees | Useful but too article-shaped | **Adapt** | Current docs are admirably candid that `changed data only`, `whole file again`, `rename without retransmit`, and `download first` are not the same thing — but the operator still has to reconstruct `how many bytes will actually move here, why did this resend in full, and did priority change order or byte cost?` from separate FAQ, security, and tips articles | **Transfer-cost contract sheet**, **Resend-geometry review**, **Byte-cost proof**, **Transfer-shape timeline**, and **Transfer-cost lineage receipt** |

> borrow Resilio's candor that piecewise delta, whole-file resend, archive-hit rename reuse, and splittability-gated priority are materially different truths  
> reject any contract where one `syncs only changed data` sentence hides byte-cost class, queue-only priority, or the Archive gate behind rename reuse
'''

direction_add = '''## Revision addendum — product direction after rev0363: transfer cost must compile into one reviewed movement contract

Another current Resilio pass sharpens one more direction-level decision:

- **transfer cost is first-class product state**
- **byte-cost class, reuse basis, queue order, and splittability ceiling are separate public truths**
- **`higher priority` must never overclaim `less data will move`**
- **`same content under a new name` must never overclaim `rename reuse is actually proven`**
- **durable receipts, not KB archaeology, preserve why bytes moved the way they did and what stronger efficiency sentence remained blocked**

From that, five product-direction rules follow:

1. A sync product may not let one `only changed data` sentence stand in for piecewise delta, whole-file resend after shift, archive-assisted rename reuse, or edition-gated diff-delta behavior.
2. Any priority control must publish whether it changes order only, byte cost only, both, or merely the active queue competition.
3. Any rename or move claim must keep its reuse basis visible instead of implying that same-hash arrivals automatically avoid retransmission everywhere.
4. Any queue suspension must remain visibly weaker than transfer cancellation and weaker than reduced network cost.
5. Durable receipts, not performance folklore, must preserve byte-cost class, reuse basis, splittability class, queue order, and the blocked stronger sentence.
'''

sources_add = '''## Revision addendum — official sources emphasized in rev0364

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about changed-piece transfer, whole-file resend after piece-shift edits, Archive-gated rename reuse, and the difference between queue priority and byte cost.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `changed data only`, `whole file again`, `rename without retransmit`, and `downloaded first` are different truths?

> where do those same current docs still show that the ordinary operator answer about `how many bytes will actually move, why did this resend in full, and did priority change order or byte cost?` depends on several articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `When a file changes, does Resilio Sync transfer the entire file again, or just the part that's changed?` article, which still says Sync splits files into pieces from 32KB up to 2MB, normally transfers only changed pieces, but re-syncs the whole file if the edit shifts all pieces, with a stronger diff-delta answer reserved to Sync Business.
- Resilio's current `What happens when file is renamed` article, which still says rename reuse depends on finding the same hash in Archive and that without Archive enabled the bytes will be re-synced again.
- Resilio's current `File download priority` article, which still says priority reorders active downloads by file modification time or size, can suspend lower-priority transfers immediately, but strictly follows prioritization rules only for files split in pieces during transfer.
- That same current priority article, which still says queue rebuilds, the 50k active-file ceiling, and UI ordering mismatches can alter perceived behavior without changing the underlying byte-cost class.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that network movement shape is not one thing
- but current Resilio still answers `how many bytes will move here, why did this resend in full, and what exactly did priority change?` too diffusely
- AnonSync should therefore prefer explicit transfer-cost sheets, resend-geometry reviews, byte-cost proof pages, transfer-shape timelines, and durable lineage receipts over overloaded performance folklore

Primary sources:

- When a file changes, does Resilio Sync transfer the entire file again, or just the part that's changed?  
  https://help.resilio.com/hc/en-us/articles/206217095-When-a-file-changes-does-Resilio-Sync-transfer-the-entire-file-again-or-just-the-part-that-s-changed

- What happens when file is renamed  
  https://help.resilio.com/hc/en-us/articles/209606526-What-happens-when-file-is-renamed

- File download priority  
  https://help.resilio.com/hc/en-us/articles/42328167759251-File-download-priority
'''

status_add = '''## Revision addendum — transfer-cost truth, resend geometry, and splittability ceiling after rev0363

This tranche locks the next seam around **transfer-cost truth**.
The key decisions now made explicit in the archive are:

- **transfer cost is a first-class contract object rather than a side effect of `sync only changed data` language**
- **piecewise delta, whole-file resend, archive-hit rename reuse, queue priority, and splittability ceiling are different truths**
- **`higher priority` is weaker than `lower byte cost`, and `suspended` is weaker than `cancelled`**
- **`same bytes under a new pathname` is weaker than `rename reuse is actually proven on this cohort`**
- **every serious movement claim now needs one receipt that preserves byte-cost basis, reuse path, splittability class, queue order, and the blocked stronger sentence**

New docs added in this tranche:

- `1324-resilio-transfer-cost-resend-geometry-and-splittability-ceiling-fragmentation-evaluation.md`
- `1325-transfer-cost-contract-sheet-page-splittability-reuse-basis-and-order-vs-byte-cost-interface-spec.md`
- `1326-resend-geometry-review-page-piece-shift-rename-reuse-and-archive-gate-interface-spec.md`
- `1327-byte-cost-proof-page-piecewise-delta-full-resend-and-priority-evidence-interface-spec.md`
- `1328-transfer-shape-timeline-page-queue-preemption-archive-hit-and-whole-file-fallback-events-interface-spec.md`
- `1329-transfer-cost-lineage-receipt-page-byte-cost-basis-reuse-path-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `syncs only changed data` can no longer hide whether the current case is piecewise delta, a whole-file resend after geometry shift, or a rename that only avoids retransmission because Archive supplied the bytes locally
- queue controls now stay visibly separate from byte-cost claims instead of letting `higher priority` impersonate `less network movement`
- splittability is now first-class, so strict priority guarantees cannot silently overextend onto nonsplittable transfer lanes
- rename review now publishes the Archive gate instead of implying that same-content arrivals always avoid retransmission
- later operators can open one receipt and see why bytes moved the way they did here, what was merely reordered, what actually avoided retransmit, and which stronger efficiency sentence the product still refused to make
'''

docs = {
'docs/1324-resilio-transfer-cost-resend-geometry-and-splittability-ceiling-fragmentation-evaluation.md': '''## Resilio seam evaluation — transfer cost, resend geometry, and splittability ceiling

Current official Resilio Sync docs still expose another strong non-clone seam around **transfer-cost truth**.
The important current facts are not subtle:

- `When a file changes, does Resilio Sync transfer the entire file again, or just the part that's changed?` still says Sync splits files into pieces from 32KB up to 2MB and normally transfers only changed pieces.
- That same current article still says if an edit shifts all pieces, the whole file will be re-synced.
- That same current article still says the stronger `avoid whole-file resend even in shift cases` answer belongs to the separate Sync Business diff-delta lane rather than the ordinary baseline.
- `What happens when file is renamed` still says rename reuse depends on finding the same hash in Archive and that without Archive enabled the file will be re-synced again.
- `File download priority` still says priority can reorder active downloads by modification time or file size, can suspend lower-priority transfers immediately, but strictly follows prioritization rules only for files split in pieces during transfer.
- That same priority article still says queue rebuilds and the 50k active-file ceiling can change performance independently of the actual byte-cost class of any one file.

This is strong operational candor.
It is also exactly why AnonSync should not clone the present page contract.
One ordinary answer to `how many bytes will actually move here, why did this resend in full, and did priority change order or network cost?` still depends on combining a FAQ article, a rename/Archive article, and a newer priority article.

So this tranche freezes a stronger replacement line: **byte-cost class, rename-reuse basis, queue order, and splittability ceiling become separate modeled truths.**

That is why this revision adds five more first-class pages: **Transfer-cost contract sheet**, **Resend-geometry review**, **Byte-cost proof**, **Transfer-shape timeline**, and **Transfer-cost lineage receipt**.
''',
'docs/1325-transfer-cost-contract-sheet-page-splittability-reuse-basis-and-order-vs-byte-cost-interface-spec.md': '''## Transfer-cost contract sheet

### Purpose
Make the product say **how bytes will really move and why** before it says `syncs only changed data`, `high priority`, `rename without re-download`, `fast`, or `efficient`.

### The contract object
Each serious movement sentence renders these fields together:

- **Byte-cost class**: metadata-only, piecewise delta, archive-assisted local reuse, whole-file resend, mixed, or unknown.
- **Reuse basis**: remote delta proof, local Archive hash hit, no reuse basis, feature-gated diff-delta lane, or unknown.
- **Splittability class**: splittable, nonsplittable, mixed queue, or unknown.
- **Queue order class**: default order, mtime-priority, size-priority, manually elevated elsewhere, suspended by higher priority, or unknown.
- **Cost witness**: current send/receive evidence, rule-only expectation, post-hoc byte counters, or unknown.
- **Fallback trigger**: piece shift, Archive absent, queue saturation, active-file cap, feature lane missing, or unknown.
- **Efficiency floor**: no honest byte-saving claim, some bytes avoided, full local rename reuse plausible, or unknown.
- **Blocked stronger sentence**: the next stronger efficiency claim the product refuses to make.

### Default language rules
- `higher priority` is intentionally weaker than `less data will move`.
- `same content under a new name` is intentionally weaker than `rename reuse is proven`.
- `delta sync` is intentionally weaker than `piecewise delta on this case`.
- `suspended` is intentionally weaker than `cancelled`.
- `fast` is intentionally weaker than `low byte cost`.

### Required persistent receipts
Any serious movement, performance, or prioritization sentence stores one durable receipt preserving byte-cost class, reuse basis, splittability class, queue order class, fallback trigger, and the blocked stronger sentence.
''',
'docs/1326-resend-geometry-review-page-piece-shift-rename-reuse-and-archive-gate-interface-spec.md': '''## Resend-geometry review page

### Question
Why did this file move the way it did?

### Mandatory review branches
1. **Piecewise delta branch**  
   Use when the current evidence says only changed pieces are moving.

2. **Whole-file resend branch**  
   Use when edit geometry shifted all pieces or the product lacks stronger diff-delta proof.

3. **Archive-assisted rename branch**  
   Use when the destination can satisfy a rename/move by finding the same hash in Archive instead of re-downloading the bytes.

4. **Archive-missing rename branch**  
   Use when the operator expects rename reuse but Archive is absent or unusable, so the bytes will be re-synced again.

5. **Priority-only branch**  
   Use when the only current claim is queue order, not byte-cost reduction.

6. **Splittability ceiling branch**  
   Use when strict priority behavior cannot be promised because the file or lane is not proven splittable.

### Required review outputs
- byte-cost class
- reuse basis
- splittability class
- queue order class
- active fallback trigger
- blocked stronger sentence

### Review language guardrails
Never let:
- `renamed` imply `no retransmission`
- `prioritized` imply `cheaper`
- `suspended` imply `aborted`
- `changed` imply `piecewise delta`
''',
'docs/1327-byte-cost-proof-page-piecewise-delta-full-resend-and-priority-evidence-interface-spec.md': '''## Byte-cost proof page

A strong movement claim must publish the strongest honest proof it has.

### Proof ladder
- **P0 — no byte-cost proof**  
  Only a general feature description exists.

- **P1 — rule-derived expectation**  
  The current lane is known to prefer changed-piece transfer or Archive rename reuse, but no case-specific witness is shown.

- **P2 — case-shaped witness**  
  The current case has a known trigger like piece shift, Archive hash hit, or queue preemption.

- **P3 — observed movement proof**  
  Runtime evidence shows delta movement, full resend, or priority-only suspension in this concrete transfer.

### Stronger-sentence barriers
Do not say:
- `only changed data moved` without at least P2
- `rename avoided retransmission` without Archive-hit basis
- `priority reduced transfer cost` unless byte-cost evidence exists independently of order evidence
- `strict priority applied` when the lane is not proven splittable
''',
'docs/1328-transfer-shape-timeline-page-queue-preemption-archive-hit-and-whole-file-fallback-events-interface-spec.md': '''## Transfer-shape timeline page

Render the operator-visible history as movement-shape events, not just generic progress.

### Event classes
- file entered queue
- queue priority changed
- lower-priority transfer suspended
- piecewise delta lane selected
- whole-file fallback triggered
- Archive hash hit found
- rename reuse completed
- queue rebuilt
- active-file ceiling blocked entry
- stronger efficiency claim revoked

### Timeline rules
- queue events and byte-cost events must remain separate
- Archive-hit events stay visibly separate from remote delta events
- splittability ceiling stays visible whenever strict priority cannot be promised
- the first event that forced whole-file fallback must remain easy to read later
''',
'docs/1329-transfer-cost-lineage-receipt-page-byte-cost-basis-reuse-path-and-blocked-stronger-sentences-interface-spec.md': '''## Transfer-cost lineage receipt page

Each serious movement claim stores one durable receipt with these fields:

- requested sentence
- byte-cost class
- reuse basis
- splittability class
- queue order class
- strongest proof level
- active fallback trigger
- blocked stronger sentence

### Example blocked stronger sentences
- `this was higher priority` did **not** prove `this moved fewer bytes`
- `this was renamed` did **not** prove `this avoided retransmission`
- `this normally sends only changed pieces` did **not** prove `this specific edit avoided a whole-file resend`
'''
}

def prepend(path_str, text):
    p = root / path_str
    old = p.read_text()
    p.write_text(text.rstrip() + '\n\n' + old)

prepend('README.md', readme_add)
prepend('docs/10-resilio-sync-evaluation.md', eval_add)
prepend('docs/11-resilio-borrow-line-and-non-clone-scorecard.md', score_add)
prepend('docs/20-product-direction.md', direction_add)
prepend('docs/sources.md', sources_add)
prepend('docs/00-status.md', status_add)

for name, content in docs.items():
    (root / name).write_text(content.strip() + '\n')

(root / 'update_rev0364.py').write_text('''from pathlib import Path\n\nroot = Path(__file__).resolve().parent\nprint("rev0364 content is already materialized in this archive; no further patching required")\nprint("new docs: 1324-1329")\n''')
print('applied rev0364')
