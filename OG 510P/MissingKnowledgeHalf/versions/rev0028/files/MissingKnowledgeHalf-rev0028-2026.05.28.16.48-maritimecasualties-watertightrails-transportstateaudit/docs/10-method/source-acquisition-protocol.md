# Source acquisition protocol

## Source classes

1. **Primary official** — registry, regulator, accident report, court record, original publication, official technical report, archived dataset, preregistration.
2. **Primary participant** — memoir, interview, oral history, correspondence, lab notebook, participant statement.
3. **Secondary synthesis** — meta-analysis, review article, historian’s account, encyclopedia-like synthesis.
4. **Journalistic** — reporting that can identify leads and timelines but usually needs corroboration for promotion.
5. **Informal** — blog posts, forums, social media, GitHub issues, slide decks, conference notes.
6. **Seed only** — archive seed material; never sufficient for factual promotion.

## Acquisition fields

Every future source record should include:

- source ID,
- title,
- author or issuing body,
- date,
- URL/DOI/registry/case number,
- retrieval date,
- evidence class,
- permanence token,
- archive/capture status,
- local hash if content is stored,
- copyability/legal note,
- sensitivity note,
- record IDs supported,
- exact claim(s) supported or qualified.

## Searched-source memory

A source pass must leave memory of rejected and searched sources, not only used sources. This protects against repeated work and selection bias.

## Promotion gate

No record can be promoted above `seed_mention` unless a source row exists or the revision receipt declares a justified exception.
