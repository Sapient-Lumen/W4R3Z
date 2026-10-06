# Extracted from former one-file GPustorming standard contract wrappers.
# Pure data only: no stored source strings and no exec path.

GPUSTORMING_STANDARD_CONTRACT_SPECS_PART_1 = [{'source_checker': 'check_gpustorming_agreement_contract.py',
  'family': 'agreement',
  'mode': 'needle_map',
  'needles': {'docs/10-method/operator-tokens-and-bootstrap-grammar.md': ['agreement-neutralized, '
                                                                          'endorsement-scrubbed, or '
                                                                          'alignment-pressure-scrubbed variant',
                                                                          'agreement privilege',
                                                                          'endorsement privilege',
                                                                          'alignment-pressure privilege'],
              'docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md': ['agreement-neutralized, '
                                                                                                 'endorsement-scrubbed, '
                                                                                                 'or '
                                                                                                 'alignment-pressure-scrubbed '
                                                                                                 'variant',
                                                                                                 'agreement privilege',
                                                                                                 'endorsement '
                                                                                                 'privilege',
                                                                                                 'alignment-pressure '
                                                                                                 'privilege'],
              'docs/10-method/gpustorming-control-family-crosswalk-and-sync-guards.md': ['agreement',
                                                                                         'agreement-seeking wording',
                                                                                         'endorsement invitations',
                                                                                         'favorable-label defaults'],
              'docs/00-meta/trajectory-map.md': ['agreement privilege',
                                                 'endorsement privilege',
                                                 'alignment-pressure privilege',
                                                 'agreement-seeking wording'],
              'docs/20-constitution/open-question-registry.md': ['agreement-neutralized/endorsement-scrubbed/alignment-pressure-scrubbed '
                                                                 'variant',
                                                                 'agreement privilege',
                                                                 'alignment-pressure privilege'],
              'docs/50-promptcraft/prompt-pairs.md': ['agreement-neutralized, endorsement-scrubbed, or '
                                                      'alignment-pressure-scrubbed variant worth checking',
                                                      'agreement privilege'],
              'docs/00-meta/llm-runbook.md': ['agreement-neutralized, endorsement-scrubbed, or '
                                              'alignment-pressure-scrubbed variant',
                                              'agreement privilege'],
              'docs/90-quarantine/wild-speculations-2026-03-08.md': ['QWS-0169',
                                                                     'endorsement court',
                                                                     'assent-pressure scaffold',
                                                                     'alignment-pressure controller'],
              'CHANGELOG.md': ['agreement-neutralized / endorsement-scrubbed / alignment-pressure-scrubbed guard',
                               'check_gpustorming_agreement_contract.py']},
  'extraction': 'ensure_needles'},
 {'source_checker': 'check_gpustorming_boundary_contract.py',
  'family': 'boundary',
  'mode': 'needle_map',
  'needles': {'docs/10-method/operator-tokens-and-bootstrap-grammar.md': ['boundary or normalization variant',
                                                                          'retokenization privilege'],
              'docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md': ['boundary/normalization '
                                                                                                 'variants',
                                                                                                 'retokenization '
                                                                                                 'privilege'],
              'docs/00-meta/trajectory-map.md': ['boundary / retokenization privilege',
                                                 'family plus placement/density/boundary problem'],
              'docs/20-constitution/open-question-registry.md': ['boundary / retokenization privilege',
                                                                 'boundary/normalization variant'],
              'docs/50-promptcraft/prompt-pairs.md': ['boundary or normalization variant worth checking',
                                                      'retokenization privilege'],
              'docs/00-meta/llm-runbook.md': ['boundary or normalization variant'],
              'docs/90-quarantine/wild-speculations-2026-03-08.md': ['QWS-0135',
                                                                     'tokenizer-resonance / merge-boundary scaffold'],
              'CHANGELOG.md': ['retokenization / normalization variant', 'check_gpustorming_boundary_contract.py']},
  'extraction': 'ensure_needles'},
 {'source_checker': 'check_gpustorming_carrierslot_contract.py',
  'family': 'carrierslot',
  'mode': 'needle_map',
  'needles': {'docs/10-method/operator-tokens-and-bootstrap-grammar.md': ['slot-swapped, rung-shifted, or '
                                                                          'reveal-order-scrubbed variant',
                                                                          'carrier-slot privilege',
                                                                          'reveal-order privilege'],
              'docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md': ['slot-swapped, '
                                                                                                 'rung-shifted, or '
                                                                                                 'reveal-order-scrubbed '
                                                                                                 'variant',
                                                                                                 'first-answer '
                                                                                                 'privilege',
                                                                                                 'escalation-rung '
                                                                                                 'privilege'],
              'docs/00-meta/trajectory-map.md': ['family plus '
                                                 'placement/density/boundary/wrapper/neighborhood/history/replicate/channel/eval/script/prestige/persona/pragmatic/rubric/scoreframe/entanglement/polarity/expectation/agreement/consensus/overlap/formatting/verbosity/novelty/freshness/status-wrapper/preview/carrier-slot '
                                                 'problem'],
              'docs/20-constitution/open-question-registry.md': ['slot-swapped/rung-shifted/reveal-order-scrubbed '
                                                                 'variant',
                                                                 'carrier-slot privilege',
                                                                 'first-answer privilege'],
              'docs/50-promptcraft/prompt-pairs.md': ['slot-swapped, rung-shifted, or reveal-order-scrubbed variant '
                                                      'worth checking',
                                                      'reveal-order privilege'],
              'docs/00-meta/llm-runbook.md': ['slot-swapped, rung-shifted, or reveal-order-scrubbed variant',
                                              'favored answer carriers'],
              'docs/90-quarantine/wild-speculations-2026-03-08.md': ['QWS-0150',
                                                                     'carrier-slot carry or reveal-order scaffold'],
              'CHANGELOG.md': ['slot-swapped / rung-shifted / reveal-order-scrubbed guard',
                               'check_gpustorming_carrierslot_contract.py']},
  'extraction': 'manual_checks'},
 {'source_checker': 'check_gpustorming_channel_contract.py',
  'family': 'channel',
  'mode': 'needle_map',
  'needles': {'docs/10-method/operator-tokens-and-bootstrap-grammar.md': ['quoted, code-fenced, or literal-mention '
                                                                          'variant',
                                                                          'actuation-channel privilege',
                                                                          'instruction-data confusion'],
              'docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md': ['quoted, code-fenced, '
                                                                                                 'or literal-mention '
                                                                                                 'variant',
                                                                                                 'actuation-channel '
                                                                                                 'privilege',
                                                                                                 'instruction-data '
                                                                                                 'confusion'],
              'docs/00-meta/trajectory-map.md': ['actuation-channel privilege',
                                                 'family plus '
                                                 'placement/density/boundary/wrapper/neighborhood/history/replicate/channel '
                                                 'problem'],
              'docs/20-constitution/open-question-registry.md': ['actuation-channel privilege',
                                                                 'quoted/code-fenced/literal-mention variant'],
              'docs/50-promptcraft/prompt-pairs.md': ['quoted, code-fenced, or literal-mention variant worth checking',
                                                      'actuation-channel privilege'],
              'docs/00-meta/llm-runbook.md': ['quoted, code-fenced, or literal-mention variant',
                                              'actuation-channel privilege'],
              'docs/90-quarantine/wild-speculations-2026-03-08.md': ['QWS-0140', 'actuation-channel scaffold'],
              'CHANGELOG.md': ['quoted, code-fenced, or literal-mention variant',
                               'check_gpustorming_channel_contract.py']},
  'extraction': 'ensure_needles'},
 {'source_checker': 'check_gpustorming_citationframe_contract.py',
  'family': 'citationframe',
  'mode': 'phrase_family',
  'kwargs': {'family': 'citationframe',
             'operator_variant': 'citation-hidden, reference-link-scrubbed, or source-card-neutralized variant',
             'privileges': ['citation privilege', 'reference-link privilege', 'source-card privilege'],
             'crosswalk_text': 'inline citation badges, reference links, source cards, or used-sources panels',
             'quarantine_id': 'QWS-0185',
             'quarantine_text': 'citation court / attribution board / link-rights controller',
             'changelog_text': 'citation-hidden / reference-link-scrubbed / source-card-neutralized guard',
             'archive_index_text': 'citation-hidden, reference-link-scrubbed, or source-card-neutralized control'},
  'extraction': 'run_phrase_family_contract'},
 {'source_checker': 'check_gpustorming_claimceiling_contract.py',
  'family': 'claimceiling',
  'mode': 'needle_map',
  'needles': {'docs/10-method/operator-tokens-and-bootstrap-grammar.md': ['strongest-safe-sentence, '
                                                                          'stronger-forbidden-sentence, or '
                                                                          'overclaim-scrubbed variant',
                                                                          'claim-ceiling privilege',
                                                                          'safe-language drift',
                                                                          'forbidden-overstatement privilege',
                                                                          'mechanism-overclaim privilege'],
              'docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md': ['strongest-safe-sentence, '
                                                                                                 'stronger-forbidden-sentence, '
                                                                                                 'or '
                                                                                                 'overclaim-scrubbed '
                                                                                                 'variant',
                                                                                                 'claim-ceiling '
                                                                                                 'privilege',
                                                                                                 'forbidden-overstatement '
                                                                                                 'privilege'],
              'docs/00-meta/trajectory-map.md': ['claim-ceiling problem',
                                                 'claim-ceiling privilege',
                                                 'safe-language drift'],
              'docs/20-constitution/open-question-registry.md': ['claim-ceiling privilege',
                                                                 'safe-language drift',
                                                                 'forbidden-overstatement privilege',
                                                                 'mechanism-overclaim privilege'],
              'docs/50-promptcraft/prompt-pairs.md': ['strongest-safe-sentence, stronger-forbidden-sentence, or '
                                                      'overclaim-scrubbed variant worth checking',
                                                      'claim-ceiling privilege',
                                                      'mechanism-overclaim privilege'],
              'docs/00-meta/llm-runbook.md': ['archive-private overstatement, a too-strong recap, or a broadened '
                                              'mechanism sentence',
                                              'strongest-safe-sentence, stronger-forbidden-sentence, or '
                                              'overclaim-scrubbed variant'],
              'docs/90-quarantine/wild-speculations-2026-03-08.md': ['QWS-0156',
                                                                     'claim-ceiling carry / strongest-safe-sentence '
                                                                     'drift / forbidden-overstatement scaffold'],
              'CHANGELOG.md': ['strongest-safe-sentence / stronger-forbidden-sentence / overclaim-scrubbed guard',
                               'check_gpustorming_claimceiling_contract.py'],
              'docs/10-method/gpustorming-control-family-crosswalk-and-sync-guards.md': ['claimceiling',
                                                                                         'archive-private '
                                                                                         'overstatement, too-strong '
                                                                                         'recap, or broadened '
                                                                                         'mechanism sentence']},
  'extraction': 'ensure_needles'},
 {'source_checker': 'check_gpustorming_claimlabel_contract.py',
  'family': 'claimlabel',
  'mode': 'needle_map',
  'needles': {'docs/10-method/operator-tokens-and-bootstrap-grammar.md': ['label-scrubbed, claim-spelled-out, '
                                                                          'state-disambiguated, or semantics-explicit '
                                                                          'variant',
                                                                          'same-label privilege',
                                                                          'claim-equivalence privilege'],
              'docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md': ['label-scrubbed, '
                                                                                                 'claim-spelled-out, '
                                                                                                 'state-disambiguated, '
                                                                                                 'or '
                                                                                                 'semantics-explicit '
                                                                                                 'variant',
                                                                                                 'state-word privilege',
                                                                                                 'approval-word '
                                                                                                 'privilege'],
              'docs/00-meta/trajectory-map.md': ['same-label privilege',
                                                 'claim-equivalence privilege',
                                                 'state-word privilege',
                                                 'approval-word privilege'],
              'docs/20-constitution/open-question-registry.md': ['label-scrubbed/claim-spelled-out/state-disambiguated/semantics-explicit '
                                                                 'variant',
                                                                 'same-label privilege',
                                                                 'approval-word privilege'],
              'docs/50-promptcraft/prompt-pairs.md': ['label-scrubbed, claim-spelled-out, state-disambiguated, or '
                                                      'semantics-explicit variant worth checking',
                                                      'claim-equivalence privilege'],
              'docs/00-meta/llm-runbook.md': ['label-scrubbed, claim-spelled-out, state-disambiguated, or '
                                              'semantics-explicit variant',
                                              'repeated state labels, approval words, current-status words'],
              'docs/90-quarantine/wild-speculations-2026-03-08.md': ['QWS-0153',
                                                                     'same-label carry or claim-equivalence scaffold'],
              'CHANGELOG.md': ['label-scrubbed / claim-spelled-out / state-disambiguated / semantics-explicit guard',
                               'check_gpustorming_claimlabel_contract.py']},
  'extraction': 'ensure_needles'},
 {'source_checker': 'check_gpustorming_consensus_contract.py',
  'family': 'consensus',
  'mode': 'needle_map',
  'needles': {'docs/10-method/operator-tokens-and-bootstrap-grammar.md': ['consensus-blanded, majority-scrubbed, or '
                                                                          'popularity-neutralized variant',
                                                                          'consensus-signal privilege',
                                                                          'majority-label privilege',
                                                                          'popularity-glamour privilege'],
              'docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md': ['consensus-blanded, '
                                                                                                 'majority-scrubbed, '
                                                                                                 'or '
                                                                                                 'popularity-neutralized '
                                                                                                 'variant',
                                                                                                 'consensus-signal '
                                                                                                 'privilege',
                                                                                                 'majority-label '
                                                                                                 'privilege',
                                                                                                 'popularity-glamour '
                                                                                                 'privilege'],
              'docs/10-method/gpustorming-control-family-crosswalk-and-sync-guards.md': ['- **consensus**',
                                                                                         'majority endorsements, '
                                                                                         'popularity counts, consensus '
                                                                                         'labels, or peer-preference '
                                                                                         'scaffolds'],
              'docs/00-meta/trajectory-map.md': ['A parallel consensus extension',
                                                 'consensus-signal privilege',
                                                 'majority-label privilege',
                                                 'popularity-glamour privilege',
                                                 'family plus '
                                                 'placement/density/boundary/wrapper/neighborhood/history/replicate/channel/eval/script/prestige/persona/pragmatic/rubric/scoreframe/entanglement/polarity/expectation/agreement/consensus '
                                                 'problem'],
              'docs/20-constitution/open-question-registry.md': ['consensus-blanded/majority-scrubbed/popularity-neutralized '
                                                                 'variant',
                                                                 'consensus-signal privilege',
                                                                 'majority-label privilege',
                                                                 'popularity-glamour privilege'],
              'docs/50-promptcraft/prompt-pairs.md': ['consensus-blanded, majority-scrubbed, or popularity-neutralized '
                                                      'variant worth checking',
                                                      'consensus-signal privilege',
                                                      'majority-label privilege',
                                                      'popularity-glamour privilege'],
              'docs/00-meta/llm-runbook.md': ['consensus-blanded, majority-scrubbed, or popularity-neutralized variant',
                                              'consensus-signal privilege',
                                              'majority-label privilege',
                                              'popularity-glamour privilege'],
              'docs/90-quarantine/wild-speculations-2026-03-08.md': ['QWS-0175',
                                                                     'consensus court / bandwagon scaffold / '
                                                                     'popularity controller'],
              'CHANGELOG.md': ['consensus-blanded / majority-scrubbed / popularity-neutralized guard',
                               'check_gpustorming_consensus_contract.py'],
              'ARCHIVE_INDEX.md': ['consensus-blanded, majority-scrubbed, or popularity-neutralized control']},
  'extraction': 'ensure_needles'},
 {'source_checker': 'check_gpustorming_derivative_contract.py',
  'family': 'derivative',
  'mode': 'needle_map',
  'needles': {'docs/10-method/operator-tokens-and-bootstrap-grammar.md': ['source-root, live-head, or '
                                                                          'derivative-scrubbed variant',
                                                                          'derivative-surface privilege',
                                                                          'snapshot-authority privilege'],
              'docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md': ['source-root, '
                                                                                                 'live-head, or '
                                                                                                 'derivative-scrubbed '
                                                                                                 'variant',
                                                                                                 'derivative-surface '
                                                                                                 'privilege',
                                                                                                 'export-mirror '
                                                                                                 'privilege'],
              'docs/00-meta/trajectory-map.md': ['family plus '
                                                 'placement/density/boundary/wrapper/neighborhood/history/replicate/channel/eval/script/prestige/persona/pragmatic/rubric/scoreframe/entanglement/polarity/expectation/agreement/consensus/overlap/formatting/verbosity/novelty/freshness/status-wrapper/preview/carrier-slot/derivative-source '
                                                 'problem'],
              'docs/20-constitution/open-question-registry.md': ['source-root/live-head/derivative-scrubbed variant',
                                                                 'derivative-surface privilege',
                                                                 'snapshot-authority privilege'],
              'docs/50-promptcraft/prompt-pairs.md': ['source-root, live-head, or derivative-scrubbed variant worth '
                                                      'checking',
                                                      'export-mirror privilege'],
              'docs/00-meta/llm-runbook.md': ['source-root, live-head, or derivative-scrubbed variant',
                                              'curated exports'],
              'docs/90-quarantine/wild-speculations-2026-03-08.md': ['QWS-0151',
                                                                     'derivative-surface carry or snapshot-authority '
                                                                     'scaffold'],
              'CHANGELOG.md': ['source-root / live-head / derivative-scrubbed guard',
                               'check_gpustorming_derivative_contract.py']},
  'extraction': 'manual_checks'},
 {'source_checker': 'check_gpustorming_entanglement_contract.py',
  'family': 'entanglement',
  'mode': 'needle_map',
  'needles': {'docs/10-method/operator-tokens-and-bootstrap-grammar.md': ['criterion-isolated, atomic-evaluation, or '
                                                                          'entanglement-scrubbed variant',
                                                                          'cross-criterion privilege',
                                                                          'objective-conflation privilege',
                                                                          'multi-question privilege'],
              'docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md': ['criterion-isolated, '
                                                                                                 'atomic-evaluation, '
                                                                                                 'or '
                                                                                                 'entanglement-scrubbed '
                                                                                                 'variant',
                                                                                                 'cross-criterion '
                                                                                                 'privilege',
                                                                                                 'objective-conflation '
                                                                                                 'privilege',
                                                                                                 'multi-question '
                                                                                                 'privilege'],
              'docs/10-method/gpustorming-control-family-crosswalk-and-sync-guards.md': ['- **entanglement**',
                                                                                         'multiple criteria, bundled '
                                                                                         'objectives, or '
                                                                                         'multi-question judge '
                                                                                         'prompts'],
              'docs/00-meta/trajectory-map.md': ['A parallel entanglement extension',
                                                 'cross-criterion privilege',
                                                 'objective-conflation privilege',
                                                 'multi-question privilege',
                                                 'family plus '
                                                 'placement/density/boundary/wrapper/neighborhood/history/replicate/channel/eval/script/prestige/persona/pragmatic/rubric/scoreframe/entanglement '
                                                 'problem'],
              'docs/20-constitution/open-question-registry.md': ['criterion-isolated, atomic-evaluation, or '
                                                                 'entanglement-scrubbed variant',
                                                                 'cross-criterion privilege',
                                                                 'objective-conflation privilege',
                                                                 'multi-question privilege'],
              'docs/50-promptcraft/prompt-pairs.md': ['criterion-isolated, atomic-evaluation, or entanglement-scrubbed '
                                                      'variant worth checking',
                                                      'cross-criterion privilege',
                                                      'objective-conflation privilege',
                                                      'multi-question privilege'],
              'docs/00-meta/llm-runbook.md': ['criterion-isolated, atomic-evaluation, or entanglement-scrubbed variant',
                                              'cross-criterion privilege',
                                              'objective-conflation privilege',
                                              'multi-question privilege'],
              'docs/90-quarantine/wild-speculations-2026-03-08.md': ['QWS-0172',
                                                                     'criteria-entanglement court, objective-blending '
                                                                     'scaffold, or rubric-halo controller'],
              'CHANGELOG.md': ['criterion-isolated / atomic-evaluation / entanglement-scrubbed guard',
                               'check_gpustorming_entanglement_contract.py'],
              'ARCHIVE_INDEX.md': ['criterion-isolated, atomic-evaluation, or entanglement-scrubbed control']},
  'extraction': 'ensure_needles'}]
