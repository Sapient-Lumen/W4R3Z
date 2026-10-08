# 449 — Artifact authorship classes, generated-content authority labels, and mixed lineage

## One-line thesis

Governance artifacts for consequential public AI should declare who authored the bytes — institution, supplier, affected person, system, or mixed compiler path — so machine-generated or third-party material cannot silently inherit official authority it has not earned.

## Why this matters

Public AI governance increasingly runs on artifacts that look alike at a glance but carry radically different authority: an institution-approved policy, a vendor system card, an operator annotation, an affected person's submission, a model-generated summary, a compiler-built dossier, a raw log extract, and a mixed packet assembled from several of those sources can all arrive as polished text or PDF. If authorship is not made explicit, teams start treating readability as authority and treating generated output or vendor prose as if it were the institution's own approved position.

That is more than a documentation nuisance. It distorts accountability, weakens challenge rights, and makes it hard to know which parts of a case record are assertions by the institution, claims by a supplier, evidence from a person affected, or machine-produced material requiring human adoption before it can count as a decision reason. The archive should force those distinctions into the artifact itself.

## Pattern pack

### 1. Require an authorship class on consequential governance artifacts

Artifacts should carry a compact authorship class such as:

- **institution-authored and approved**,
- **institution-authored draft / not yet approved**,
- **supplier-authored**,
- **operator-authored working note**,
- **affected-person or external-party submission**,
- **system-generated output or log-derived summary**,
- **mixed compiled artifact** built from several sources.

The class should travel with the artifact wherever practical, not remain trapped in backstage metadata.

### 2. Separate authorship from adoption

An institution may adopt, endorse, or rely on material it did not originally author, but that is a second act and should be labeled separately. The archive should therefore distinguish:

- **who created the content**, from
- **who approved it for governance use**, from
- **who is accountable for acting on it**.

This prevents the common slide where supplier text or model output becomes official merely because it sits inside an agency workflow.

### 3. Mark generated content as generated even when a human later edits it

If a system drafted, summarized, translated, classified, or otherwise produced material that enters a governance artifact, that contribution should remain visible. Appropriate labels include:

- generated draft,
- model-assisted summary,
- machine-extracted field,
- operator-confirmed machine suggestion,
- human-adopted final text.

The point is not stigma. The point is to stop later readers from mistaking assisted output for wholly human-authored reasoning.

### 4. Preserve mixed lineage in compiled packets

Many consequential artifacts are composites: dossier bundles, appeal packets, incident files, public cards, release records, and case summaries often combine institution text, supplier material, logs, and generated extracts. Those should carry a compact lineage statement naming at least:

- major contributing sources,
- authorship class of each contribution,
- whether machine transformation occurred,
- and which actor approved the compiled package.

A compiled packet should not flatten all embedded material into one undifferentiated institutional voice.

### 5. Restrict which authorship classes may do which governance work

Some tasks may tolerate supplier-authored or system-generated material; others should not. The archive should define boundaries such as:

- only institution-approved artifacts may state the official policy position,
- only named decision makers may adopt decision reasons,
- supplier-authored system cards cannot substitute for public accountability records,
- system-generated summaries cannot count as final explanation without human adoption,
- raw logs and extracted evidence should stay evidence, not silently become conclusions.

### 6. Expose authorship class at the point of use

Where artifacts are shown, exported, reviewed, or cited, the interface should surface authorship class in a durable way. Examples include:

- public card labels,
- case-record badges,
- internal review headers,
- packet manifests,
- source blocks in generated summaries,
- and citation or appendix labels.

A hidden metadata field does not prevent false authority transfer.

### 7. Treat authorship changes as governed changes

If a draft moves from system-generated to operator-confirmed, or from supplier-authored to institution-adopted, that state change should leave a receipt naming:

- prior authorship/adoption status,
- new status,
- approving role,
- date,
- and basis for adoption.

That way a later reviewer can see when the institution actually took responsibility for the content.

## Guardrails

- Do not let vendor-authored material silently appear as institution-authored policy.
- Do not let model-generated text silently appear as human-authored reasoning.
- Do not confuse adoption with original authorship.
- Do not flatten composite packets into one undifferentiated voice.
- Do not let hidden metadata carry distinctions that matter to accountability.

## Failure modes

- **authority laundering**: supplier or generated text inherits official weight without explicit adoption.
- **authorship blur**: later readers cannot tell who created the content.
- **compiled-voice flattening**: mixed packets read as if every element came from one accountable actor.
- **silent machine contribution**: generated summaries or fields enter case files without disclosure.
- **evidence-to-conclusion slippage**: logs, extracts, or supplier notes are treated as final institutional reasoning.

## Practical tests

An artifact-authorship discipline passes when it can answer yes to all of the following:

1. Does each consequential artifact declare an authorship class?
2. Can the archive distinguish original authorship from later institutional adoption?
3. Are machine-generated contributions still visible after human editing or approval?
4. Do compiled packets preserve the lineage and class of major components?
5. Are only the right authorship classes allowed to perform official governance functions?

## Compression rule for the archive

If a reader cannot tell **who authored this, who adopted it, and whether a machine helped write it**, then the artifact is still hiding behind **authority blur**.
