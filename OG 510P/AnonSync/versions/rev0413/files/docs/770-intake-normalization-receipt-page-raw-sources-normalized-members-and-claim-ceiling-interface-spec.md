# Intake normalization receipt page — raw sources, normalized members, and claim ceiling interface spec

## Purpose

Leave a durable receipt proving what raw evidence was harvested, how it was normalized, and what provenance ceiling still applies before or after packet assembly.

## Inputs

- raw evidence intake object
- artifact normalization review
- packet assembly review
- actual normalized members retained
- excluded / discarded / split-out source list

## Primary questions this page must answer

1. What raw sources existed at intake time?
2. What transformations turned them into normalized members?
3. What raw sources were excluded, discarded, or split out, and why?
4. What strongest lineage/provenance sentence is justified now?
5. When should the operator reopen intake rather than trust this receipt as settled?

## Sections

### 1. Raw intake summary

Show:

- intake batch id
- raw-source count
- witness/platform coverage
- original path classes represented
- provenance posture

### 2. Normalized outputs

Show:

- normalized-member count
- raw-to-normalized lineage summary
- members preserved as originals
- members created by extraction / pruning / recompression / rename

### 3. Exclusions and splits

Show:

- discarded raw sources
- split-out members and target packet if any
- duplicate handling summary
- stronger forbidden sentence about completeness

### 4. Claim ceiling

Show:

- strongest honest provenance sentence
- residual uncertainty (`origin weakened`, `witness missing`, `folder overscope unresolved`, `cleanup may have removed context`, `none-significant`)
- what later manifest/export review may still claim

### 5. Reopen boundary

Show triggers such as:

- a required raw source was never typed or bound to a witness
- normalization discarded a member later found to matter
- packet split changed the audience or ask scope
- later manifest review finds lineage too weak
- recipient asks for the original raw member rather than the normalized derivative

## Guardrails

- Never let this receipt read like export proof; it only proves intake and normalization state.
- Never omit discarded or split-out raw sources.
- Never treat a cleaned packet as equivalent to original raw custody unless that is actually true.
- Never let normalization success hide provenance weakness.

## Output

A durable intake-normalization receipt preserving raw-source inventory, normalized outputs, exclusions, lineage confidence, and reopen boundary.

