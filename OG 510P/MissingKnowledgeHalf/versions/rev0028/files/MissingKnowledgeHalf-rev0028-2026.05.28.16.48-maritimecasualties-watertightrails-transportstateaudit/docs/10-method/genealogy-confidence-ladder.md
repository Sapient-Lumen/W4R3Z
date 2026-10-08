# Genealogy confidence ladder

Rev0005 opens the genealogy lane. The most important rule is that **a relation is not a vibe**. Every edge needs a relation type, source type, confidence, and scope caution.

## Relation classes

- **Formal lineage:** doctoral advisor, postdoc mentor, institutional appointment, committee member. These are relatively easy to source but are not the same as influence.
- **Scene co-presence:** conference, workshop, lab, seminar, summer school, correspondence network, oral-history scene. These prove opportunity for contact, not influence by themselves.
- **Cited influence:** explicit citation, preface, acknowledgement, dedication, interview, memoir, or historian-supported influence claim.
- **Reaction / anti-genealogy:** a person, school, report, or movement defines itself against another claim, method, school, or promise.
- **Transmission infrastructure:** database, archive, syllabus, translation chain, festschrift, obituary, oral-history collection.

## Confidence levels

- **High:** primary institutional or archival source directly supports the relation.
- **Medium:** official/institutional secondary source supports the relation but primary edge source has not been extracted.
- **Low:** secondary synthesis or community database suggests the relation; useful for queueing, not for final claims.
- **Not evidence of absence:** absence from a genealogy database is not proof that a relation or influence did not exist.

## Edge payload minimum

Each edge should carry: `from`, `to`, `edge_type`, `source_id`, `locator`, `confidence`, `not_equivalent_to`, and `what_would_change_status`.

Rev0005 uses this ladder to promote `MKH-GEN-0001`, `MKH-GEN-0004`, and `MKH-GEN-0005` without importing any unsourced person-edge graph.
