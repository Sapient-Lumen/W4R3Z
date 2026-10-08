# 467 — Native evidence lanes, normalized packets, and no semantic re-ownership

## One-line thesis

Consequential public-AI archives should keep native logs, vendor exports, raw witnesses, replay references, normalized packets, and downstream summaries in distinct evidence lanes so portability does not silently rewrite source semantics, missingness, or authority.

## Why this matters

Governance evidence rarely arrives in one clean format. It may begin as a vendor export, a platform-native audit trail, a system-produced JSON log, a screenshot, a raw witness packet, or a replay-only reference into a live environment. Later, someone turns that source-native material into a portable bundle, a human-readable case packet, a summary for oversight, or a merged dossier for appeal.

That translation work is necessary. Raw artifacts are often too brittle, too large, too privileged, or too specialized to travel on their own. But translation also creates a subtle governance failure: the normalized or downstream artifact starts to look cleaner, more durable, and more legible than the native basis, so it quietly inherits semantic authority it has not earned. Missing fields become “not present.” Replay-only references start to read like copied evidence. A dashboard export with unstable schema gets retold as a fully stable institutional record. A downstream diagnostic summary quietly re-owns the meanings that belonged to the originating system.

The archive already covers authenticity pins, source-backed summaries, authorship classes, and contemporaneous witnesses. What it still lacked was one note explicitly governing the **lane boundary** between source-native evidence and the portable or interpreted artifacts that follow it.

## Pattern pack

### 1. Preserve native-lane identity before summarizing it

A consequential evidence object should retain enough native identity to answer:

- what system produced it,
- what format or schema family it belongs to,
- whether it is stable, unstable, or provisional,
- when it was captured,
- what environment or version produced it,
- and whether the archive holds bytes, a replay path, or only a reference.

Normalization should not erase source posture.

### 2. Distinguish copied artifacts from replay-only references

The archive should keep at least these states separate:

- copied native artifact preserved in the packet,
- transformed or normalized derivative preserved in the packet,
- replay-only reference that requires later retrieval,
- and summary-only mention with no portable native basis attached.

A reviewer should not have to guess which kind of access they really have.

### 3. Normalize missingness and drift honestly

When a portable packet is built from native evidence, it should visibly preserve:

- omitted attachments,
- missing native fields,
- schema drift,
- unavailable replay context,
- access-restricted segments,
- and transformations applied during packing.

Absence should not become “no issue found” merely because the portable packet is tidier.

### 4. Keep downstream conclusions in a separate lane

A normalized packet may support later conclusions: incident diagnosis, compliance review, appeal analysis, newsroom summary, or executive briefing. Those downstream products should remain clearly separate from the imported native evidence and from the normalized packet itself. The archive should preserve:

- what came from the native source,
- what came from the normalization step,
- and what came from later interpretation or judgment.

That separation helps later reviewers disagree with the diagnosis without having to dispute the capture history.

### 5. Let multiple consumers cite one pack without re-owning its semantics

Where practical, different consumers should be able to cite the same imported pack for their own purposes instead of each building a private adapter that silently rewrites meanings. A build review, appeal packet, oversight memo, or incident note may all consume one portable bundle, but they should not each pretend to define the native semantics anew.

### 6. Preserve stability posture and transformation history

If a source lane is unstable, schema-shifting, or known to change across versions, the packet should say so explicitly. If the archive transformed the artifact to make it portable, it should preserve:

- the transformation performed,
- the reason for it,
- the limits of the transformed version,
- and any important properties the transformation may not reproduce perfectly.

Portability is valuable, but it is still a transformation.

### 7. Fail closed when the portable layer would overclaim the native basis

If the native artifact cannot be authenticated, replayed, fully captured, or interpreted without unresolved drift, the portable layer should narrow its claims. It may still say:

- a packet exists,
- some facts were imported,
- some fields are unavailable,
- and stronger conclusions remain blocked.

It should not quietly speak with the confidence of a complete native record.

## Guardrails

- Do not let normalized convenience erase native provenance, stability posture, or missing fields.
- Do not call a replay path a copied artifact.
- Do not let downstream diagnosis inherit the authority of source-native evidence by layout or rhetoric alone.
- Do not silently compress transformation history out of the portable packet.
- Do not build many consumer-specific adapters that each redefine the same source semantics differently.

## Failure modes

- **portable-pack laundering**: a convenient normalized packet is mistaken for the entire native truth.
- **replay-as-capture confusion**: a retrievable path is mistaken for bytes already preserved.
- **missingness flattening**: unstable or absent fields become fake certainty in downstream summaries.
- **semantic re-ownership**: each downstream consumer quietly rewrites what the native evidence meant.
- **transformation amnesia**: a converted artifact loses the record of how and why it was changed.

## Practical tests

A lane-honest evidence regime passes when it can answer yes to all of the following:

1. Can every consequential evidence packet distinguish native artifacts, normalized derivatives, replay-only references, and summaries?
2. Does the packet preserve source posture, including stability or drift where relevant?
3. Are omitted fields, missing attachments, and access restrictions visible rather than flattened away?
4. Are downstream conclusions kept in a separate interpretive lane from the native evidence they cite?
5. Can multiple consumers reuse one pack without each silently redefining its underlying semantics?

## Compression rule for the archive

If a portable packet can say **here is the evidence** but cannot also say **what was native, what was transformed, what is only replayable, and what later readers merely concluded**, then it is still letting **portability impersonate provenance**.
