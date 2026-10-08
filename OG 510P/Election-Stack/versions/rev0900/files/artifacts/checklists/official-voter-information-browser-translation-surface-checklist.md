# Official voter-information browser-translation surface checklist

Use this checklist when an election office needs the **current answer/help lane to remain reconstructible even if a browser translates the already-open official page, translates selected text, or keeps translation active across later pages in the same language/tab context**.

## Scope and boundary review

- [ ] Record which public routes were reviewed for browser-integrated translation behavior.
- [ ] Distinguish this surface from language selectors / locale fallback, alternate-language discovery, reader mode, and browser-integrated page-summary / page-context AI behavior.
- [ ] Keep “browser convenience translation of the original page” separate from “reviewed official translated page the office actually stands behind.”

## Authority and equivalence review

- [ ] Check whether the page still exposes source-language office identity, jurisdiction scope, and current-state cues clearly enough after likely browser translation.
- [ ] Review whether the official translated/help lane stays visible enough that browser translation remains subordinate rather than quietly looking like the canonical multilingual publication.
- [ ] Avoid designs where the translated convenience rendering appears more authoritative than the reviewed official translation or help lane.

## Selected-text and partial-translation review

- [ ] Review likely phrases or excerpts a voter could translate out of context.
- [ ] Check whether important exceptions, routing notes, or deadline qualifiers live close enough to the operative sentence to survive excerpt translation.
- [ ] If the answer is not safely portable through isolated translation, make the page say so plainly and route the voter to the current translated/help lane.

## Persistence and recovery review

- [ ] Review whether browser translation may continue automatically across the same language, site, or tab context.
- [ ] Keep original-language recovery and official translated/help routing legible even if the browser stays in translated mode.
- [ ] Do not assume translation behavior is universal across browsers, settings, language pairs, regions, platforms, or enterprise policies.

## Privacy and evidence review

- [ ] Preserve a small public digest of reviewed routes, translation contexts, recovery/help anchors, and last review time.
- [ ] Do not preserve translated transcripts, copied browser prompts, or individualized language histories merely to prove the posture was reviewed.
- [ ] Keep any future idea of browser-native translation provenance or perfect diff auditing in quarantine until trustworthy standardized hooks actually exist.
