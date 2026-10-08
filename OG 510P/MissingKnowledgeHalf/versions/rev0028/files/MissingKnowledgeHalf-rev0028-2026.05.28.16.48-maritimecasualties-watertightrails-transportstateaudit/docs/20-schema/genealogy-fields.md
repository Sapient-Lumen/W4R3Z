# Genealogy and anti-genealogy fields

Record types:

- person,
- work,
- influence link,
- advisor/student link,
- collaborator link,
- correspondence link,
- scene,
- event,
- institution/lab,
- translation/reception link,
- reaction-against link,
- lost-lineage marker.

Minimum payload for a relation:

- source node,
- target node,
- relation type,
- direction,
- dates,
- evidence source,
- confidence,
- interpretive caution,
- underrepresented/lost-lineage flag if relevant.

## Rev0005 addendum: first promoted GEN fields

The first promoted genealogy records require `record_class`, `relation_types`, `nodes`, `edges`, `confidence_ladder`, `scope_cautions`, and `why_it_matters_for_missing_half`. A formal advisor edge, a workshop co-presence edge, and an anti-genealogy evaluator edge are different record species and must not be collapsed.
