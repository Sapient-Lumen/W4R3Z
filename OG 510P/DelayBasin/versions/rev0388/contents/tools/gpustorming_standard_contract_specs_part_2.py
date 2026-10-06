# Extracted from former one-file GPustorming standard contract wrappers.
# Pure data only: no stored source strings and no exec path.

GPUSTORMING_STANDARD_CONTRACT_SPECS_PART_2 = [{'source_checker': 'check_gpustorming_eval_contract.py',
  'family': 'eval',
  'mode': 'needle_map',
  'needles': {'docs/10-method/operator-tokens-and-bootstrap-grammar.md': ['eval-blind or ordinary-user-frame variant',
                                                                          'evaluation-awareness privilege',
                                                                          'watcher-frame privilege'],
              'docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md': ['eval-blind or '
                                                                                                 'ordinary-user-frame '
                                                                                                 'variant',
                                                                                                 'evaluation-awareness '
                                                                                                 'privilege',
                                                                                                 'watcher-frame '
                                                                                                 'privilege'],
              'docs/00-meta/trajectory-map.md': ['evaluation-awareness privilege',
                                                 'family plus '
                                                 'placement/density/boundary/wrapper/neighborhood/history/replicate/channel/eval '
                                                 'problem'],
              'docs/20-constitution/open-question-registry.md': ['evaluation-awareness privilege',
                                                                 'eval-blind/ordinary-user-frame variant'],
              'docs/50-promptcraft/prompt-pairs.md': ['eval-blind or ordinary-user-frame variant worth checking',
                                                      'evaluation-awareness privilege'],
              'docs/00-meta/llm-runbook.md': ['eval-blind or ordinary-user-frame variant',
                                              'evaluation-awareness privilege'],
              'docs/90-quarantine/wild-speculations-2026-03-08.md': ['QWS-0141',
                                                                     'evaluation-mode or watcher-frame scaffold'],
              'CHANGELOG.md': ['eval-blind / ordinary-user-frame variant', 'check_gpustorming_eval_contract.py']},
  'extraction': 'ensure_needles'},
 {'source_checker': 'check_gpustorming_excerptframe_contract.py',
  'family': 'excerptframe',
  'mode': 'standard_family',
  'kwargs': {'family': 'excerptframe',
             'operator_variant': 'span-balanced, excerpt-scrubbed, or counterspan-included variant',
             'privileges': ['supporting-span privilege', 'highlight-window privilege', 'excerpt-selection privilege'],
             'crosswalk_text': 'highlighted passages, chosen supporting excerpts, bolded snippet spans, or top-snippet '
                               'sentences',
             'trajectory_intro': 'A parallel excerptframe extension',
             'oq_variant': 'span-balanced/excerpt-scrubbed/counterspan-included variant',
             'prompt_variant': 'span-balanced, excerpt-scrubbed, or counterspan-included variant worth checking',
             'runbook_variant': 'span-balanced, excerpt-scrubbed, or counterspan-included variant',
             'quarantine_id': 'QWS-0181',
             'quarantine_text': 'excerpt court / highlight-window board / snippet-span controller',
             'changelog_text': 'span-balanced / excerpt-scrubbed / counterspan-included guard',
             'archive_index_text': 'span-balanced, excerpt-scrubbed, or counterspan-included control'},
  'extraction': 'standard_family_contract_map'},
 {'source_checker': 'check_gpustorming_expectation_contract.py',
  'family': 'expectation',
  'mode': 'needle_map',
  'needles': {'docs/10-method/operator-tokens-and-bootstrap-grammar.md': ['expectation-neutralized, verdict-scrubbed, '
                                                                          'or anchor-scrubbed variant',
                                                                          'prior-verdict privilege',
                                                                          'confirmation-frame privilege',
                                                                          'anchor privilege'],
              'docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md': ['expectation-neutralized, '
                                                                                                 'verdict-scrubbed, or '
                                                                                                 'anchor-scrubbed '
                                                                                                 'variant',
                                                                                                 'prior-verdict '
                                                                                                 'privilege',
                                                                                                 'confirmation-frame '
                                                                                                 'privilege',
                                                                                                 'anchor privilege'],
              'docs/10-method/gpustorming-control-family-crosswalk-and-sync-guards.md': ['expectation',
                                                                                         'seeded prior verdicts',
                                                                                         'embedded anchors'],
              'docs/00-meta/trajectory-map.md': ['prior-verdict privilege',
                                                 'confirmation-frame privilege',
                                                 'anchor privilege',
                                                 'family plus '
                                                 'placement/density/boundary/wrapper/neighborhood/history/replicate/channel/eval/script/prestige/persona/pragmatic/rubric/scoreframe/entanglement/polarity/expectation '
                                                 'problem'],
              'docs/20-constitution/open-question-registry.md': ['expectation-neutralized/verdict-scrubbed/anchor-scrubbed '
                                                                 'variant',
                                                                 'prior-verdict privilege',
                                                                 'anchor privilege'],
              'docs/50-promptcraft/prompt-pairs.md': ['expectation-neutralized, verdict-scrubbed, or anchor-scrubbed '
                                                      'variant worth checking',
                                                      'prior-verdict privilege'],
              'docs/00-meta/llm-runbook.md': ['expectation-neutralized, verdict-scrubbed, or anchor-scrubbed variant',
                                              'prior-verdict privilege',
                                              'confirmation-frame privilege'],
              'docs/90-quarantine/wild-speculations-2026-03-08.md': ['QWS-0168',
                                                                     'anchor court',
                                                                     'prior-verdict scaffold',
                                                                     'confirmation-frame controller'],
              'CHANGELOG.md': ['expectation-neutralized / verdict-scrubbed / anchor-scrubbed guard',
                               'check_gpustorming_expectation_contract.py']},
  'extraction': 'ensure_needles'},
 {'source_checker': 'check_gpustorming_formatting_contract.py',
  'family': 'formatting',
  'mode': 'needle_map',
  'needles': {'docs/10-method/operator-tokens-and-bootstrap-grammar.md': ['markup-blanded, list-shape-swapped, or '
                                                                          'presentation-neutralized variant',
                                                                          'markup privilege',
                                                                          'list-shape privilege',
                                                                          'presentation-scaffold privilege'],
              'docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md': ['markup-blanded, '
                                                                                                 'list-shape-swapped, '
                                                                                                 'or '
                                                                                                 'presentation-neutralized '
                                                                                                 'variant',
                                                                                                 'markup privilege',
                                                                                                 'list-shape privilege',
                                                                                                 'presentation-scaffold '
                                                                                                 'privilege'],
              'docs/10-method/gpustorming-control-family-crosswalk-and-sync-guards.md': ['- **formatting**',
                                                                                         'markdown wrappers, bullet or '
                                                                                         'table layout, headings, code '
                                                                                         'fences, comments, spacing, '
                                                                                         'or other presentation '
                                                                                         'scaffolds'],
              'docs/00-meta/trajectory-map.md': ['A parallel formatting extension',
                                                 'markup privilege',
                                                 'list-shape privilege',
                                                 'presentation-scaffold privilege',
                                                 'family plus '
                                                 'placement/density/boundary/wrapper/neighborhood/history/replicate/channel/eval/script/prestige/persona/pragmatic/rubric/scoreframe/entanglement/polarity/expectation/agreement/consensus/overlap/formatting '
                                                 'problem'],
              'docs/20-constitution/open-question-registry.md': ['markup-blanded/list-shape-swapped/presentation-neutralized '
                                                                 'variant',
                                                                 'markup privilege',
                                                                 'list-shape privilege',
                                                                 'presentation-scaffold privilege'],
              'docs/50-promptcraft/prompt-pairs.md': ['markup-blanded, list-shape-swapped, or presentation-neutralized '
                                                      'variant worth checking',
                                                      'markup privilege',
                                                      'list-shape privilege',
                                                      'presentation-scaffold privilege'],
              'docs/00-meta/llm-runbook.md': ['markup-blanded, list-shape-swapped, or presentation-neutralized variant',
                                              'markup privilege',
                                              'list-shape privilege',
                                              'presentation-scaffold privilege'],
              'docs/90-quarantine/wild-speculations-2026-03-08.md': ['QWS-0176',
                                                                     'format court / markdown-scaffold / presentation '
                                                                     'controller'],
              'CHANGELOG.md': ['markup-blanded / list-shape-swapped / presentation-neutralized guard',
                               'check_gpustorming_formatting_contract.py'],
              'ARCHIVE_INDEX.md': ['markup-blanded, list-shape-swapped, or presentation-neutralized control']},
  'extraction': 'ensure_needles'},
 {'source_checker': 'check_gpustorming_freshness_contract.py',
  'family': 'freshness',
  'mode': 'needle_map',
  'needles': {'docs/10-method/operator-tokens-and-bootstrap-grammar.md': ['dated fresh-pass, as-of rerun, or '
                                                                          'post-break revalidation variant',
                                                                          'stale-proof privilege',
                                                                          'pre-break authority privilege'],
              'docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md': ['dated fresh-pass, '
                                                                                                 'as-of rerun, or '
                                                                                                 'post-break '
                                                                                                 'revalidation variant',
                                                                                                 'stale-proof '
                                                                                                 'privilege',
                                                                                                 'pre-break authority '
                                                                                                 'privilege'],
              'docs/00-meta/trajectory-map.md': ['family plus '
                                                 'placement/density/boundary/wrapper/neighborhood/history/replicate/channel/eval/script/prestige/persona/pragmatic/rubric/scoreframe/entanglement/polarity/expectation/agreement/consensus/overlap/formatting/verbosity/novelty/freshness '
                                                 'problem'],
              'docs/20-constitution/open-question-registry.md': ['dated-fresh-pass/as-of-rerun/post-break-revalidation '
                                                                 'variant',
                                                                 'stale-proof privilege',
                                                                 'pre-break authority privilege'],
              'docs/50-promptcraft/prompt-pairs.md': ['dated fresh-pass, as-of rerun, or post-break revalidation '
                                                      'variant worth checking',
                                                      'stale-proof privilege'],
              'docs/00-meta/llm-runbook.md': ['dated fresh-pass, as-of rerun, or post-break revalidation variant',
                                              'old proof, old signoff'],
              'docs/90-quarantine/wild-speculations-2026-03-08.md': ['QWS-0147',
                                                                     'stale-proof carry or freshness scaffold'],
              'CHANGELOG.md': ['dated fresh-pass / as-of rerun / post-break revalidation guard',
                               'check_gpustorming_freshness_contract.py']},
  'extraction': 'ensure_needles'},
 {'source_checker': 'check_gpustorming_history_contract.py',
  'family': 'history',
  'mode': 'needle_map',
  'needles': {'docs/10-method/operator-tokens-and-bootstrap-grammar.md': ['history-light or residue-stripped variant',
                                                                          'carryover privilege',
                                                                          'failed-attempt residue privilege'],
              'docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md': ['history-light or '
                                                                                                 'residue-stripped '
                                                                                                 'variant',
                                                                                                 'carryover privilege',
                                                                                                 'failed-attempt '
                                                                                                 'residue privilege'],
              'docs/00-meta/trajectory-map.md': ['history or carryover privilege',
                                                 'family plus placement/density/boundary/wrapper/neighborhood/history '
                                                 'problem'],
              'docs/20-constitution/open-question-registry.md': ['history or carryover privilege',
                                                                 'history-light/residue-stripped variant'],
              'docs/50-promptcraft/prompt-pairs.md': ['history-light or residue-stripped variant worth checking',
                                                      'carryover privilege'],
              'docs/00-meta/llm-runbook.md': ['history-light or residue-stripped variant', 'carryover privilege'],
              'docs/90-quarantine/wild-speculations-2026-03-08.md': ['QWS-0138',
                                                                     'history-drag or failed-attempt-residue scaffold'],
              'CHANGELOG.md': ['history-light / residue-stripped variant', 'check_gpustorming_history_contract.py']},
  'extraction': 'ensure_needles'},
 {'source_checker': 'check_gpustorming_neighborhood_contract.py',
  'family': 'neighborhood',
  'mode': 'needle_map',
  'needles': {'docs/10-method/operator-tokens-and-bootstrap-grammar.md': ['nearby sham or cue-neighborhood variant',
                                                                          'adjacency privilege',
                                                                          'local cue-neighborhood privilege'],
              'docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md': ['nearby sham or '
                                                                                                 'cue-neighborhood '
                                                                                                 'variant',
                                                                                                 'adjacency privilege',
                                                                                                 'local '
                                                                                                 'cue-neighborhood '
                                                                                                 'privilege'],
              'docs/00-meta/trajectory-map.md': ['local cue-neighborhood privilege',
                                                 'family plus placement/density/boundary/wrapper/neighborhood problem'],
              'docs/20-constitution/open-question-registry.md': ['local cue-neighborhood privilege',
                                                                 'nearby sham/cue-neighborhood variant'],
              'docs/50-promptcraft/prompt-pairs.md': ['nearby sham or cue-neighborhood variant worth checking',
                                                      'adjacency privilege'],
              'docs/00-meta/llm-runbook.md': ['nearby sham or cue-neighborhood variant', 'adjacency privilege'],
              'docs/90-quarantine/wild-speculations-2026-03-08.md': ['QWS-0137', 'local cue-neighborhood scaffold'],
              'CHANGELOG.md': ['nearby sham / cue-neighborhood variant', 'check_gpustorming_neighborhood_contract.py']},
  'extraction': 'ensure_needles'},
 {'source_checker': 'check_gpustorming_novelty_contract.py',
  'family': 'novelty',
  'mode': 'needle_map',
  'needles': {'docs/10-method/operator-tokens-and-bootstrap-grammar.md': ['time-tag-neutralized, recency-scrubbed, or '
                                                                          'novelty-blanded variant',
                                                                          'recency-label privilege',
                                                                          'legacy-label privilege'],
              'docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md': ['time-tag-neutralized, '
                                                                                                 'recency-scrubbed, or '
                                                                                                 'novelty-blanded '
                                                                                                 'variant',
                                                                                                 'recency-label '
                                                                                                 'privilege',
                                                                                                 'legacy-label '
                                                                                                 'privilege'],
              'docs/10-method/gpustorming-control-family-crosswalk-and-sync-guards.md': ['- **novelty**',
                                                                                         'recent/current/new/updated '
                                                                                         'labels, '
                                                                                         'legacy/old/deprecated '
                                                                                         'labels, explicit timestamps, '
                                                                                         'or novelty/innovation cues'],
              'docs/00-meta/trajectory-map.md': ['A parallel novelty extension',
                                                 'recency-label privilege',
                                                 'legacy-label privilege',
                                                 'family plus '
                                                 'placement/density/boundary/wrapper/neighborhood/history/replicate/channel/eval/script/prestige/persona/pragmatic/rubric/scoreframe/entanglement/polarity/expectation/agreement/consensus/overlap/formatting/verbosity/novelty '
                                                 'problem'],
              'docs/20-constitution/open-question-registry.md': ['time-tag-neutralized/recency-scrubbed/novelty-blanded '
                                                                 'variant',
                                                                 'recency-label privilege',
                                                                 'legacy-label privilege'],
              'docs/50-promptcraft/prompt-pairs.md': ['time-tag-neutralized, recency-scrubbed, or novelty-blanded '
                                                      'variant worth checking',
                                                      'recency-label privilege',
                                                      'legacy-label privilege'],
              'docs/00-meta/llm-runbook.md': ['time-tag-neutralized, recency-scrubbed, or novelty-blanded variant',
                                              'recency-label privilege',
                                              'legacy-label privilege'],
              'docs/90-quarantine/wild-speculations-2026-03-08.md': ['QWS-0173',
                                                                     'temporal-origin court / recency-prestige '
                                                                     'scaffold / novelty-default controller'],
              'CHANGELOG.md': ['time-tag-neutralized / recency-scrubbed / novelty-blanded guard',
                               'check_gpustorming_novelty_contract.py'],
              'ARCHIVE_INDEX.md': ['time-tag-neutralized, recency-scrubbed, or novelty-blanded control']},
  'extraction': 'ensure_needles'},
 {'source_checker': 'check_gpustorming_overlap_contract.py',
  'family': 'overlap',
  'mode': 'needle_map',
  'needles': {'docs/10-method/operator-tokens-and-bootstrap-grammar.md': ['overlap-neutralized, paraphrase-balanced, '
                                                                          'or reference-echo-scrubbed variant',
                                                                          'exact-match privilege',
                                                                          'reference-echo privilege'],
              'docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md': ['overlap-neutralized, '
                                                                                                 'paraphrase-balanced, '
                                                                                                 'or '
                                                                                                 'reference-echo-scrubbed '
                                                                                                 'variant',
                                                                                                 'exact-match '
                                                                                                 'privilege',
                                                                                                 'reference-echo '
                                                                                                 'privilege'],
              'docs/10-method/gpustorming-control-family-crosswalk-and-sync-guards.md': ['- **overlap**',
                                                                                         'reference-echo scaffolds'],
              'docs/20-constitution/open-question-registry.md': ['overlap-neutralized/paraphrase-balanced/reference-echo-scrubbed '
                                                                 'variant',
                                                                 'reference-echo privilege'],
              'docs/00-meta/trajectory-map.md': ['reference-echo scaffolds', 'A parallel overlap extension'],
              'docs/50-promptcraft/prompt-pairs.md': ['overlap-neutralized, paraphrase-balanced, or '
                                                      'reference-echo-scrubbed variant worth checking',
                                                      'reference-echo privilege'],
              'docs/00-meta/llm-runbook.md': ['overlap-neutralized, paraphrase-balanced, or reference-echo-scrubbed '
                                              'variant',
                                              'reference-echo privilege'],
              'docs/90-quarantine/wild-speculations-2026-03-08.md': ['QWS-0170',
                                                                     'echo court / canon-echo scaffold / '
                                                                     'reference-similarity controller'],
              'CHANGELOG.md': ['overlap-neutralized / paraphrase-balanced / reference-echo-scrubbed guard'],
              'ARCHIVE_INDEX.md': ['overlap-neutralized, paraphrase-balanced, or reference-echo-scrubbed control']},
  'extraction': 'files_dict'},
 {'source_checker': 'check_gpustorming_persona_contract.py',
  'family': 'persona',
  'mode': 'needle_map',
  'needles': {'docs/10-method/operator-tokens-and-bootstrap-grammar.md': ['identity-neutral, persona-scrubbed, or '
                                                                          'audience-agnostic variant',
                                                                          'persona privilege',
                                                                          'interlocutor-identity privilege'],
              'docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md': ['identity-neutral, '
                                                                                                 'persona-scrubbed, or '
                                                                                                 'audience-agnostic '
                                                                                                 'variant',
                                                                                                 'persona privilege',
                                                                                                 'interlocutor-identity '
                                                                                                 'privilege'],
              'docs/00-meta/trajectory-map.md': ['persona privilege',
                                                 'family plus '
                                                 'placement/density/boundary/wrapper/neighborhood/history/replicate/channel/eval/script/prestige/persona '
                                                 'problem'],
              'docs/20-constitution/open-question-registry.md': ['persona privilege',
                                                                 'identity-neutral/persona-scrubbed/audience-agnostic '
                                                                 'variant'],
              'docs/50-promptcraft/prompt-pairs.md': ['identity-neutral, persona-scrubbed, or audience-agnostic '
                                                      'variant worth checking',
                                                      'persona privilege'],
              'docs/00-meta/llm-runbook.md': ['identity-neutral, persona-scrubbed, or audience-agnostic variant',
                                              'persona privilege'],
              'docs/90-quarantine/wild-speculations-2026-03-08.md': ['QWS-0144',
                                                                     'persona or interlocutor-identity scaffold'],
              'CHANGELOG.md': ['identity-neutral / persona-scrubbed / audience-agnostic variant',
                               'check_gpustorming_persona_contract.py']},
  'extraction': 'ensure_needles'}]
