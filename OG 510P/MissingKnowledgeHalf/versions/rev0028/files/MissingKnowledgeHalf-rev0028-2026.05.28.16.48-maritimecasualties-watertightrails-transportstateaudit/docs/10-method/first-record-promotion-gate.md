# First record promotion gate

Revision: `rev0003`

Rev0003 tests the minimum gate for moving from `seed_mention` to a promoted record.

## Minimum gate used here

A record may become `promoted_record_primary_source_backed_one_pass_reviewed` when it has:

1. at least one primary or official source;
2. a separate source record with evidence class, URL/identifier, retrieval date, permanence token, and copyability note;
3. at least one bounded claim with explicit source support;
4. an evidence profile that names limitations;
5. an ethics block;
6. unknowns and next actions;
7. a revision receipt admitting the promotion.

This gate is intentionally lower than final synthesis. It allows the archive to begin while preserving correction paths.

## What source-backed does not mean

It does not mean:

- all sources have been exhausted;
- official reports are infallible;
- the causal story is complete;
- later corrections cannot change the record;
- a pattern is mature merely because several famous cases rhyme.

## Why official engineering reports are the first lane

Engineering investigations often expose sequence, proximate cause, contributing factors, recommendations, and post-incident controls. They are therefore the cleanest way to test the denominator graph before moving to harder domains such as unpublished null results or contested replication history.


## Rev0004 extension: non-engineering gate

Rev0004 extends the first-record gate to replication and medical negative-result records. A non-engineering record may be admitted after one pass when it has:

1. at least one peer-reviewed, official, or professional/archive source;
2. separated claims with exact source locators;
3. a `type_payload` that preserves the prior evidentiary route and the endpoint/status-changing evidence;
4. explicit scope cautions that prevent sloganization;
5. unknowns and next actions that name missing primary sources, practice-lag work, or child-record splits.

This is still not final synthesis. It is controlled admission into the denominator graph.
