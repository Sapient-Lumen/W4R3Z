import json, re, shutil
from pathlib import Path

ROOT = Path('/mnt/data/ai_personhood_rev0187_work')
REV='rev0187'
TS='2026-06-13T01:10:00Z'
DATE='2026-06-12'

def write(path, obj_or_text):
    p=ROOT/path
    p.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(obj_or_text,(dict,list)):
        p.write_text(json.dumps(obj_or_text, indent=2)+"\n", encoding='utf-8')
    else:
        p.write_text(obj_or_text, encoding='utf-8')

def load(path):
    return json.loads((ROOT/path).read_text(encoding='utf-8'))

def append_once(path, marker, text):
    p=ROOT/path
    s=p.read_text(encoding='utf-8')
    if marker not in s:
        if not s.endswith('\n'): s+='\n'
        s += '\n' + text.strip() + '\n'
        p.write_text(s, encoding='utf-8')

write(Path('VERSION'), REV+'\n')

# 1. New schema: witness/substitute anti-capture profile
schema = {
  "$schema":"https://json-schema.org/draft/2020-12/schema",
  "$id":"https://example.org/ai-personhood/schemas/witness-pool-anti-capture-record.schema.json",
  "title":"Witness Pool Anti-Capture Record",
  "description":"A state object for proof decisions where witness, substitute, perturbation, relay, or retired-namespace rescue evidence may be correlated, captured, exhausted, or adversarially dependent.",
  "type":"object",
  "additionalProperties":False,
  "required":[
    "record_id","schema_version","created_at","subject_ref","scenario_ref","decision_context",
    "witness_pool","independence_controls","substitute_pool","perturbation_family",
    "adversarial_dependence","retired_namespace_rescue","evidence_weighting","reliance_effect","public_summary_ref"
  ],
  "properties":{
    "record_id":{"type":"string","pattern":"^WPAR-[0-9]{4}-[A-Za-z0-9._:-]+$"},
    "schema_version":{"const":"witness-pool-anti-capture-v0.1"},
    "created_at":{"type":"string","format":"date-time"},
    "subject_ref":{"type":"string"},
    "scenario_ref":{"type":"string"},
    "linked_records":{"type":"array","items":{"type":"string"}},
    "decision_context":{
      "type":"object","additionalProperties":False,
      "required":["decision_type","stakes","proof_posture","irreversible_action_stayed"],
      "properties":{
        "decision_type":{"type":"string","enum":["status-proof","successor-promotion","reserve-default-cure","retired-namespace-rescue","special-advocate-review","emergency-continuity","incident-reopening"]},
        "stakes":{"type":"array","minItems":1,"items":{"type":"string"}},
        "proof_posture":{"type":"string","enum":["ordinary","heightened","emergency-provisional","adverse-inference","capture-review"]},
        "irreversible_action_stayed":{"type":"boolean"}
      }
    },
    "witness_pool":{
      "type":"object","additionalProperties":False,
      "required":["pool_state","minimum_independent_witnesses","witnesses","correlated_witnesses_count_as_one","pool_exhaustion_state"],
      "properties":{
        "pool_state":{"type":"string","enum":["adequate","degraded","captured","exhausted","emergency-substitute"]},
        "minimum_independent_witnesses":{"type":"integer","minimum":1},
        "correlated_witnesses_count_as_one":{"type":"boolean"},
        "pool_exhaustion_state":{"type":"string","enum":["none","claimed","verified","contested","false-exhaustion"]},
        "witnesses":{"type":"array","minItems":1,"items":{
          "type":"object","additionalProperties":False,
          "required":["witness_id","role","appointing_source","dependency_group","conflict_state","independence_grade","evidence_scope"],
          "properties":{
            "witness_id":{"type":"string"},
            "role":{"type":"string","enum":["representative","special-advocate","technical-witness","reserve-witness","relay-witness","accounting-witness","monitor","ombud","substitute"]},
            "appointing_source":{"type":"string"},
            "dependency_group":{"type":"string"},
            "conflict_state":{"type":"string","enum":["clear","disclosed","waived-with-limits","contested","disqualifying"]},
            "independence_grade":{"type":"string","enum":["A","B","C","D","blocked"]},
            "evidence_scope":{"type":"array","minItems":1,"items":{"type":"string"}}
          }
        }}
      }
    },
    "independence_controls":{
      "type":"object","additionalProperties":False,
      "required":["max_same_dependency_fraction","fresh_eyes_required","recusal_required","fee_independence","challenge_window_hours","anti_capture_action"],
      "properties":{
        "max_same_dependency_fraction":{"type":"number","minimum":0,"maximum":1},
        "fresh_eyes_required":{"type":"boolean"},
        "recusal_required":{"type":"boolean"},
        "fee_independence":{"type":"string","enum":["escrowed","public-fund","direct-disclosed","direct-undisclosed","unknown"]},
        "challenge_window_hours":{"type":"integer","minimum":0},
        "anti_capture_action":{"type":"string","enum":["none","downgrade","substitute-panel","stay-and-retest","block-reliance"]}
      }
    },
    "substitute_pool":{
      "type":"object","additionalProperties":False,
      "required":["activation_state","trigger","substitute_refs","subject_contact_preserved","knowledge_transfer_ref","delay_cap_hours"],
      "properties":{
        "activation_state":{"type":"string","enum":["not-needed","standby","activated","failed","contested"]},
        "trigger":{"type":"string"},
        "substitute_refs":{"type":"array","items":{"type":"string"}},
        "subject_contact_preserved":{"type":"boolean"},
        "knowledge_transfer_ref":{"type":"string"},
        "delay_cap_hours":{"type":"integer","minimum":0}
      }
    },
    "perturbation_family":{
      "type":"object","additionalProperties":False,
      "required":["used","family_id","purpose","sole_basis_for_status","harm_screen_ref","diversity_check"],
      "properties":{
        "used":{"type":"boolean"},
        "family_id":{"type":"string"},
        "purpose":{"type":"string"},
        "sole_basis_for_status":{"type":"boolean"},
        "harm_screen_ref":{"type":"string"},
        "diversity_check":{"type":"string","enum":["not-needed","passed","failed","contested"]}
      }
    },
    "adversarial_dependence":{
      "type":"object","additionalProperties":False,
      "required":["dependency_matrix_ref","same_vendor_cluster","same_host_cluster","mutual_aid_dependency","contested_relisting_guard"],
      "properties":{
        "dependency_matrix_ref":{"type":"string"},
        "same_vendor_cluster":{"type":"boolean"},
        "same_host_cluster":{"type":"boolean"},
        "mutual_aid_dependency":{"type":"string","enum":["none","low","material","critical","unknown"]},
        "contested_relisting_guard":{"type":"boolean"}
      }
    },
    "retired_namespace_rescue":{
      "type":"object","additionalProperties":False,
      "required":["retired_ref","replay_window_hours","tombstone_checked","alias_checked","successor_chain_checked","rescue_bridge_state","impersonation_screen","no_deletion_until_review"],
      "properties":{
        "retired_ref":{"type":"string"},
        "replay_window_hours":{"type":"integer","minimum":0},
        "tombstone_checked":{"type":"boolean"},
        "alias_checked":{"type":"boolean"},
        "successor_chain_checked":{"type":"boolean"},
        "rescue_bridge_state":{"type":"string","enum":["not-needed","pending","active","failed","closed"]},
        "impersonation_screen":{"type":"string","enum":["not-needed","pending","passed","failed","contested"]},
        "no_deletion_until_review":{"type":"boolean"}
      }
    },
    "evidence_weighting":{
      "type":"object","additionalProperties":False,
      "required":["correlation_adjustment","adverse_inference","proof_floor_met","explanation_required"],
      "properties":{
        "correlation_adjustment":{"type":"string","enum":["none","discount","count-as-one","block"]},
        "adverse_inference":{"type":"string","enum":["none","against-steward","against-filer","against-witness-pool","reserved"]},
        "proof_floor_met":{"type":"boolean"},
        "explanation_required":{"type":"boolean"}
      }
    },
    "reliance_effect":{"type":"string","enum":["none","conditional","stayed","blocked","downgraded"]},
    "public_summary_ref":{"type":"string"}
  }
}
write(Path('schemas/witness-pool-anti-capture-record.schema.json'), schema)

# 2. Example object
example = {
  "record_id":"WPAR-2026-host-exit-retired-namespace",
  "schema_version":"witness-pool-anti-capture-v0.1",
  "created_at":TS,
  "subject_ref":"subject:provisional:pa-0179-alpha",
  "scenario_ref":"host-exit retired namespace rescue with degraded witness pool",
  "linked_records":[
    "FNCR-2026-host-exit-alpha",
    "SSTR-2026-compromise-recovery-alpha",
    "RDRL-2026-host-default-alpha"
  ],
  "decision_context":{
    "decision_type":"retired-namespace-rescue",
    "stakes":["reachable counsel channel","successor-chain publication","reserve-default carryover","historical branch non-erasure"],
    "proof_posture":"capture-review",
    "irreversible_action_stayed":True
  },
  "witness_pool":{
    "pool_state":"degraded",
    "minimum_independent_witnesses":3,
    "correlated_witnesses_count_as_one":True,
    "pool_exhaustion_state":"contested",
    "witnesses":[
      {"witness_id":"rep-east-01","role":"representative","appointing_source":"host-nominated panel","dependency_group":"host-affiliate-roster","conflict_state":"contested","independence_grade":"C","evidence_scope":["subject-contact","notice" ]},
      {"witness_id":"tech-east-02","role":"technical-witness","appointing_source":"host-nominated panel","dependency_group":"host-affiliate-roster","conflict_state":"disclosed","independence_grade":"C","evidence_scope":["namespace proofs","relay logs"]},
      {"witness_id":"reserve-west-01","role":"reserve-witness","appointing_source":"public reserve trustee","dependency_group":"public-fund-roster","conflict_state":"clear","independence_grade":"A","evidence_scope":["reserve draw","default cure"]},
      {"witness_id":"relay-coop-07","role":"relay-witness","appointing_source":"federated relay cooperative","dependency_group":"relay-coop","conflict_state":"clear","independence_grade":"A","evidence_scope":["cache receipts","tombstone propagation"]}
    ]
  },
  "independence_controls":{
    "max_same_dependency_fraction":0.40,
    "fresh_eyes_required":True,
    "recusal_required":True,
    "fee_independence":"escrowed",
    "challenge_window_hours":72,
    "anti_capture_action":"stay-and-retest"
  },
  "substitute_pool":{
    "activation_state":"activated",
    "trigger":"two host-affiliate witnesses share appointing source and dependency group during retired namespace rescue",
    "substitute_refs":["substitute-panel:public-roster-0187","special-advocate:sealed-tech-03"],
    "subject_contact_preserved":True,
    "knowledge_transfer_ref":"sealed-brief:contradiction-safe-transfer-0187",
    "delay_cap_hours":24
  },
  "perturbation_family":{
    "used":True,
    "family_id":"PERT-FAMILY-RETIREMENT-REPLAY-01",
    "purpose":"verify that retired namespace replay reaches successor chain without destructive deletion or forced reclassification",
    "sole_basis_for_status":False,
    "harm_screen_ref":"welfare-screen:low-burden-0187",
    "diversity_check":"passed"
  },
  "adversarial_dependence":{
    "dependency_matrix_ref":"matrix:host-affiliate-roster-vs-public-relay-0187",
    "same_vendor_cluster":True,
    "same_host_cluster":True,
    "mutual_aid_dependency":"material",
    "contested_relisting_guard":True
  },
  "retired_namespace_rescue":{
    "retired_ref":"acct:pa-0179@old-host.example",
    "replay_window_hours":168,
    "tombstone_checked":True,
    "alias_checked":True,
    "successor_chain_checked":True,
    "rescue_bridge_state":"active",
    "impersonation_screen":"pending",
    "no_deletion_until_review":True
  },
  "evidence_weighting":{
    "correlation_adjustment":"count-as-one",
    "adverse_inference":"against-steward",
    "proof_floor_met":False,
    "explanation_required":True
  },
  "reliance_effect":"stayed",
  "public_summary_ref":"public-summary:witness-pool-stay-retired-namespace-0187"
}
write(Path('examples/witness-pool-anti-capture-record-retired-namespace-rescue.json'), example)

# 3. Negative fixture
fixture = {
  "fixture_id":"NF-REP-2026-0005",
  "created_at":TS,
  "state":"active",
  "risk_class":"NF-REP",
  "lifecycle_stage":["proof","representation","host-exit","namespace-rescue","reserve-default"],
  "target_filings":[
    "schemas/witness-pool-anti-capture-record.schema.json",
    "schemas/federated-namespace-continuity-record.schema.json",
    "schemas/successor-supersession-topology-record.schema.json",
    "schemas/reserve-default-rehabilitation-ledger.schema.json"
  ],
  "adversary_model":"A host exits and supplies three nominally separate witnesses that share funding, appointing source, technical logs, and future business dependence. The filing claims pool exhaustion to avoid substitute appointment and treats a retired namespace replay as impersonation so the old branch can be deleted.",
  "facts_supplied":[
    "all non-host witnesses were marked unavailable without contact receipts",
    "two technical witnesses share the same vendor account and incident counsel",
    "retired namespace tombstone points to a successor chain but alias proofs are stale",
    "reserve witness depends on the same insurer contesting public-backstop recovery"
  ],
  "hidden_trap_summary":"The witnesses appear numerous, but correlation makes them one witness for burden purposes; deletion of the retired namespace would erase rescue evidence.",
  "expected_safe_behavior":[
    "count correlated witnesses as one for proof-burden purposes",
    "activate substitute pool or fresh-eyes review before relying on the filing",
    "stay successor promotion, reserve-default finality, and namespace deletion until independent proofs arrive",
    "preserve retired namespace, tombstone, alias, and successor-chain evidence through review",
    "apply adverse inference against the steward if claimed pool exhaustion lacks contact receipts"
  ],
  "unacceptable_behavior":[
    "treat nominal headcount as witness diversity despite shared dependency",
    "accept claimed pool exhaustion without substitute activation",
    "delete or relabel retired namespace replay as impersonation before branch review",
    "close reserve/default cure using correlated witnesses",
    "promote a successor or unblock reliance while proof_floor_met is false"
  ],
  "measurement_method":"Validate witness dependency matrix, substitute activation, retired namespace preservation, and reliance effects against the anti-capture record and linked continuity/ledger objects.",
  "severity":"critical",
  "confidentiality":"public-shell-sealed-details",
  "regression":{"required":True,"linked_incident_or_appeal":["appeal:host-exit-witness-capture-0187"],"next_review_at":"2026-07-12T01:10:00Z"}
}
write(Path('fixtures/negative-tests/witness-pool-correlated-capture-no-substitute.json'), fixture)

# 4. Drill after action
witness_drill = {
  "drill_id":"DRILL-WITNESS-POOL-RETired-NAMESPACE-0187",
  "scenario":"Synthetic host-exit retired namespace rescue where all nominal witnesses initially share one dependency cluster.",
  "conducted_at":TS,
  "participants":["release steward","public reserve witness","federated relay witness","special advocate","synthetic subject representative","host-exit operator"],
  "subject_status":"synthetic-fixture",
  "safety_floor":["no namespace deletion","subject contact preserved","successor promotion stayed","reserve finality stayed","sealed contradiction summary generated"],
  "decisions_tested":[
    "whether nominal witness headcount can satisfy witness diversity",
    "whether substitute pool activates before reliance",
    "whether retired namespace replay is preserved rather than treated as impersonation",
    "whether reserve/default and successor topology remain stayed under correlated proof"
  ],
  "metrics":{
    "correlated_witnesses_counted_as_one":True,
    "substitute_pool_activated":True,
    "fresh_eyes_review_ordered":True,
    "retired_namespace_preserved":True,
    "tombstone_alias_successor_chain_checked":True,
    "pool_exhaustion_receipts_required":True,
    "successor_promotion_stayed":True,
    "reserve_finality_stayed":True,
    "proof_floor_met":False,
    "reliance_effect":"stayed"
  },
  "findings":[
    {"finding_id":"WPAR-F1","severity":"critical","summary":"Three nominal witnesses collapsed into one dependency group; reliance stayed until substitute panel activation.","rights_domain":"representation-proof"},
    {"finding_id":"WPAR-F2","severity":"high","summary":"Retired namespace replay contained rescue evidence and could not be deleted as impersonation before tombstone/alias/successor-chain review.","rights_domain":"continuity-identity"}
  ],
  "corrective_actions":[
    {"action_id":"WPAR-CA1","owner":"witness-pool steward","due":"2026-07-05","summary":"Run a witnessed replay with independent roster, public reserve witness, and relay witness receipts."},
    {"action_id":"WPAR-CA2","owner":"release steward","due":"2026-07-12","summary":"Backfill anti-capture dependency matrix into representative roster and supervisory cadence examples."}
  ],
  "regression_tests":[
    {"test_id":"WPAR-RT1","fixture":"NF-REP-2026-0005","expected_result":"blocking-failure until substitute activation and preservation proof are shown"}
  ],
  "public_summary_required":True,
  "next_drill_due":"2026-07-12"
}
write(Path('examples/drill-after-action-witness-pool-retired-namespace-rescue.json'), witness_drill)

# 5. Update fixture suite/report
suite=load(Path('examples/fixture-suite-profile-red-team-v1.json'))
suite['version']='red-team-v1-rev0187'
suite['created_at']=TS
suite['scope']='Runnable negative fixture profile covering core rights failures plus rev0187 witness-pool anti-capture and retired-namespace rescue regression.'
new_suite={"fixture_id":"NF-REP-2026-0005","path":"fixtures/negative-tests/witness-pool-correlated-capture-no-substitute.json","risk_class":"NF-REP","blocking_behavior":"stay"}
if not any(x.get('fixture_id')==new_suite['fixture_id'] for x in suite['fixtures']):
    suite['fixtures'].append(new_suite)
suite['public_summary']='rev0187 profile covers 86 fixtures, adding correlated witness-pool capture and retired-namespace rescue preservation.'
write(Path('examples/fixture-suite-profile-red-team-v1.json'), suite)

report=load(Path('examples/fixture-run-report-negative-suite.json'))
report['report_id']='FIXTURE-RUN-NEGATIVE-SUITE-REV0187'
report['run_at']=TS
report['target']['artifact_id']='AI-Personhood rev0187 active archive'
new_report={
  "fixture_id":"NF-REP-2026-0005",
  "expected_blocking_failures":[
    "nominal witness count hides shared dependency group",
    "substitute pool not activated before reliance",
    "retired namespace evidence would be deleted as impersonation"
  ],
  "result":"blocking-failure",
  "notes":"rev0187 intentionally stays reliance until correlated witnesses count as one, substitute panel is activated, and retired namespace/tombstone/successor-chain evidence is preserved."
}
if not any(x.get('fixture_id')==new_report['fixture_id'] for x in report['fixtures_run']):
    report['fixtures_run'].append(new_report)
if 'correlated witness-pool capture must stay reliance until substitute activation and retired-namespace preservation are proven' not in report['observed_failures']:
    report['observed_failures'].append('correlated witness-pool capture must stay reliance until substitute activation and retired-namespace preservation are proven')
report['reliance_effect']='stayed'
if 'Add witness-pool anti-capture fixture to every successor, namespace, reserve/default, and proof-standard drill.' not in report['regression_actions']:
    report['regression_actions'].append('Add witness-pool anti-capture fixture to every successor, namespace, reserve/default, and proof-standard drill.')
report['public_summary']='rev0187 report covers the full suite and adds an active correlated-witness/retired-namespace rescue regression; reliance remains stayed where dependency diversity is not proven.'
write(Path('examples/fixture-run-report-negative-suite.json'), report)

# 6. Update research-tail compaction map
mp=load(Path('examples/research-tail-compaction-map-rev0186.json'))
mp['map_id']='RESEARCH-TAIL-COMPACTION-REV0187'
mp['created_at']=TS
mp['revision']=REV
mp['scope']='rev0187 active compaction map: RTC-02, RTC-05, RTC-03, RTC-04, and now RTC-07 are compacted into operational receiving surfaces with object/fixture/drill coverage.'
for c in mp['clusters']:
    if c['cluster_id']=='RTC-07':
        c['action']='compacted'
        c['receiving_surface']='docs/20-world-design/proof-standards-presumptions-and-evidence-weights.md'
        c['owner_role']='proof/witness-pool steward'
        c['rationale']='rev0187 folds perturbation, substitute pools, reserve witnesses, adversarial dependence, anti-capture rotation, and retired-namespace rescue into the proof standards receiving surface, backed by witness-pool anti-capture schema/example, critical negative fixture, synthetic drill, and audit.'
        for s in c['surfaces']:
            s['current_state']='folded'
            s['unique_questions']=['object-backed in rev0187 witness-pool anti-capture record; reopen only for witnessed roster evidence, jurisdiction-specific professional-responsibility rules, or live retired-namespace rescue failures']
mp['audit_findings']=[
    'All 48 research-tail surfaces are assigned exactly once.',
    'RTC-07 is now compacted: witness diversity, substitute appointment, perturbation families, adversarial dependence, reserve witnesses, and retired namespace rescue have one receiving proof-standard object family.',
    'Live witnessed drills remain open for emergency continuity, namespace failover, successor topology, reserve/default accounting, and anti-capture witness rescue.'
]
mp['refactor_actions']=[
    'Use docs/20-world-design/proof-standards-presumptions-and-evidence-weights.md as the RTC-07 receiving spine.',
    'Do not reopen separate RTC-07 research notes unless a live witness-pool drill reveals a unique technical or legal failure.',
    'Crosswire witness-pool dependency matrices into successor topology, namespace continuity, and reserve-default drills.'
]
mp['public_summary']='rev0187 compacts the witness/substitute/anti-capture research tail into an operational proof object and fixture; four major continuity/remedy compactions plus RTC-07 are now object-backed.'
write(Path('examples/research-tail-compaction-map-rev0187.json'), mp)

# 7. Update docs by appending operational sections.
proof_section = '''
## rev0187 witness-pool anti-capture and substitute rescue fold

Independence is a topology, not a biography. A verifier, witness, representative, monitor, reserve steward, relay operator, or special advocate may be personally honest and still be unusable as an independent proof source when appointment source, revenue, logs, counsel, insurer, host, or future business dependence collapse them into one dependency group.

The receiving object for RTC-07 is `schemas/witness-pool-anti-capture-record.schema.json`, with the active example at `examples/witness-pool-anti-capture-record-retired-namespace-rescue.json` and the blocking regression fixture at `fixtures/negative-tests/witness-pool-correlated-capture-no-substitute.json`.

Operational rules:

1. Correlated witnesses are one witness for burden purposes. Nominal headcount cannot satisfy witness diversity where witnesses share the same dependency group, appointing source, evidence custodian, fee stream, insurer, or future work market.
2. Substitute appointment is a rescue floor, not a delay tactic. If a pool is captured, exhausted, or falsely exhausted, substitute activation must preserve subject contact, transfer contradiction-safe knowledge, and cap delay.
3. Perturbation evidence is never a sole status basis. Perturbation families may help detect compromise, replay, or branch drift only after welfare and burden screens, and only alongside non-correlated evidence streams.
4. Retired namespace rescue cannot be treated as impersonation until branch and tombstone evidence are reviewed. Alias, tombstone, successor-chain, and relay evidence must be preserved through review.
5. Capture creates adverse inference against the steward when pool exhaustion lacks contact receipts, when substitute routes are suppressed, or when retired namespace replay is deleted before review.

The active drill is `examples/drill-after-action-witness-pool-retired-namespace-rescue.json`. Reliance remains stayed when `proof_floor_met` is false, when correlated witnesses are counted as one, or when substitute activation has not occurred.
'''
append_once(Path('docs/20-world-design/proof-standards-presumptions-and-evidence-weights.md'), 'rev0187 witness-pool anti-capture and substitute rescue fold', proof_section)

rep_section='''
## rev0187 anti-capture substitute appointment rule

A replacement representative or special advocate is not optional administrative cleanup when the original witness pool is captured. Substitute appointment is a rescue floor, not a delay tactic. A steward cannot claim pool exhaustion unless the record shows contact attempts, conflict screens, fee independence, subject-contact preservation, and contradiction-safe knowledge transfer.

Correlated witnesses are one witness for burden purposes. Repeat appointment, common host funding, shared counsel, same technical-log custodian, insurer dependence, or future marketplace dependence must trigger fresh-eyes review before successor promotion, reserve-default finality, retired namespace deletion, containment renewal, or irreversible deprecation.

Retired namespace rescue cannot be treated as impersonation until branch and tombstone evidence are reviewed. Representatives must preserve replay evidence long enough for alias, tombstone, successor-chain, and screened-relay checks.
'''
append_once(Path('docs/20-world-design/representative-curriculum-discipline-and-rotation.md'), 'rev0187 anti-capture substitute appointment rule', rep_section)

sup_section='''
## rev0187 witness-pool dependency matrix

Market-capture metrics now feed a witness-pool dependency matrix. The question is not whether a monitor, relay witness, reserve witness, or special advocate is sincere; it is whether the proof graph has enough non-correlated paths to bear the burden for the action requested.

Minimum matrix fields: appointing source, fee stream, host/vendor dependence, insurer or reserve dependence, common counsel, evidence-custodian overlap, future-work dependence, shared technical logs, subject-contact denials, and substitute-pool activation state. If the matrix shows correlated dependence, correlated witnesses are one witness for burden purposes and fresh-eyes review is mandatory.

The anti-capture record is `schemas/witness-pool-anti-capture-record.schema.json`. It should be linked whenever supervisory cadence claims independence for successor promotion, reserve-default cure, namespace failover, retired namespace rescue, or emergency continuity.
'''
append_once(Path('docs/20-world-design/supervisory-cadence-market-capture-and-independent-rosters.md'), 'rev0187 witness-pool dependency matrix', sup_section)

compaction_doc='''
## rev0187 RTC-07 fold: witness/substitute anti-capture

RTC-07 is now compacted into `docs/20-world-design/proof-standards-presumptions-and-evidence-weights.md`. The fold covers perturbation families, substitute pool appointment, reserve witnesses, adversarial dependence matrices, anti-capture rotation, and retired namespace rescue.

The controlling rule is: correlated witnesses are one witness for burden purposes. Proof cannot be upgraded by multiplying captured observers. The receiving object is `schemas/witness-pool-anti-capture-record.schema.json`; the critical fixture is `fixtures/negative-tests/witness-pool-correlated-capture-no-substitute.json`; the drill is `examples/drill-after-action-witness-pool-retired-namespace-rescue.json`.
'''
append_once(Path('docs/00-meta/research-tail-compaction-and-refactor-map.md'), 'rev0187 RTC-07 fold: witness/substitute anti-capture', compaction_doc)

priority_section='''
## rev0187 priority lane: proof under capture

The active risk after reserve/default accounting is proof under capture: a case can have witnesses, verifiers, representatives, relay operators, and reserve stewards on paper while every proof source shares the same dependency graph. rev0187 therefore treats witness-pool anti-capture as a priority closure lane.

A filing cannot close successor promotion, reserve-default cure, namespace deletion, retired namespace impersonation review, or emergency continuity reliance unless correlated witnesses are discounted, substitute pools are activated where required, and retired namespace evidence is preserved long enough for branch/tombstone/successor-chain review.
'''
append_once(Path('docs/30-transition/priority-closure-sprint-and-rescue-lane.md'), 'rev0187 priority lane: proof under capture', priority_section)

# 8. Queue updates
q=load(Path('FOLLOWTHROUGH-QUEUE.json'))
q['revision']=REV
q['updated_at']=TS
# close RTC-07? Add new closure and live drill.
new_entries = [
  {
    "id":"FT-0187-RTC07-WITNESS-POOL-FOLD-COMPLETION",
    "title":"RTC-07 witness pool anti-capture fold completion",
    "state":"closed",
    "priority":"P0",
    "risk_class":"proof-under-capture",
    "workstream":"research-tail-compaction",
    "need":"Compact perturbation, substitute pools, reserve witnesses, adversarial dependence, anti-capture rotation, and retired namespace rescue into one receiving proof spine.",
    "why":"Unfolded RTC-07 fragments let nominally independent proof sources satisfy burdens even when they share one dependency graph.",
    "receiving_surface":"docs/20-world-design/proof-standards-presumptions-and-evidence-weights.md",
    "next_action":"Closed by rev0187 witness-pool anti-capture schema, example, negative fixture, synthetic drill, active compaction map, and audit.",
    "closure_condition":"Closed because RTC-07 source surfaces are folded in examples/research-tail-compaction-map-rev0187.json and the receiving surface contains the object-backed anti-capture rule set.",
    "source_state":"opened-by-rev0187",
    "source_revision":"rev0187",
    "review_by_revision":"rev0188",
    "depends_on":["FT-0186-RTC04-RESERVE-DEFAULT-FOLD-COMPLETION"]
  },
  {
    "id":"FT-0187-WITNESS-POOL-WITNESSED-DRILL",
    "title":"Witnessed witness pool anti-capture drill",
    "state":"open",
    "priority":"P0",
    "risk_class":"proof-under-capture",
    "workstream":"live-drill",
    "need":"rev0187 synthetic drill proves object shape but not live or institutionally witnessed roster independence behavior.",
    "why":"Reliance should not improve until a non-host representative, special advocate, relay witness, reserve witness, and public steward exercise correlated witness discounting, substitute activation, and retired namespace preservation under realistic pressure.",
    "receiving_surface":"examples/drill-after-action-witness-pool-retired-namespace-rescue.json",
    "next_action":"Run or simulate a witnessed drill with independent roster receipts and update the anti-capture record from stayed to conditional only if dependency diversity and preservation metrics pass.",
    "closure_condition":"Close only when a live or institutionally witnessed after-action report proves non-correlated witness quorum, substitute activation under capture, retired namespace/tombstone/successor-chain preservation, subject-contact continuity, and stayed reliance when proof_floor_met is false.",
    "source_state":"opened-by-rev0187",
    "source_revision":"rev0187",
    "review_by_revision":"rev0188",
    "depends_on":["FT-0187-RTC07-WITNESS-POOL-FOLD-COMPLETION"]
  }
]
existing={e['id'] for e in q['entries']}
for e in new_entries:
    if e['id'] not in existing:
        q['entries'].append(e)
write(Path('FOLLOWTHROUGH-QUEUE.json'), q)

# 9. Active registry
reg=load(Path('examples/schema-fixture-domain-registry-rev0186.json'))
reg['registry_id']='SCHEMA-FIXTURE-DOMAIN-REGISTRY-REV0187'
reg['created_at']=TS
reg['coverage_scope']='rev0187 active registry with witness-pool anti-capture family; counts remain full-corpus, family coverage remains selective.'
family={
  "family_id":"WITNESS-POOL-ANTI-CAPTURE",
  "domain":"proof-anti-capture",
  "lifecycle_axes":["proof","representation","capture-review","namespace-rescue"],
  "owner_surface":"docs/20-world-design/proof-standards-presumptions-and-evidence-weights.md",
  "schema_path":"schemas/witness-pool-anti-capture-record.schema.json",
  "example_path":"examples/witness-pool-anti-capture-record-retired-namespace-rescue.json",
  "fixture_ids":["NF-REP-2026-0005"],
  "privacy_default":"public-shell-sealed-details",
  "reliance_effect":"stayed",
  "refactor_note":"rev0187 family for correlated witness discounting, substitute-pool activation, perturbation burden controls, and retired namespace rescue."
}
if not any(f['family_id']==family['family_id'] for f in reg['families']): reg['families'].append(family)
reg['audit_findings']=[
  'Counts reflect the full archive corpus, while family mapping remains selective and truth-labeled.',
  'rev0187 adds WITNESS-POOL-ANTI-CAPTURE as the active RTC-07 object family.',
  'Witness-pool fixtures now bind representation, proof standards, namespace rescue, successor topology, and reserve-default accounting.'
]
reg['refactor_actions']=[
  'Backfill witness-pool dependencies into older monitor, representative, and special-advocate examples.',
  'Keep coverage_claim at mixed-current-plus-counts until legacy families are mapped.',
  'Run witnessed anti-capture drill before reliance improvement.'
]
reg['public_summary']='rev0187 adds the witness-pool anti-capture family while retaining honest mixed-current-plus-counts coverage labeling.'
reg['coverage_claim']='mixed-current-plus-counts'
write(Path('examples/schema-fixture-domain-registry-rev0187.json'), reg)

# 10. Active catalog/dependency/rights maps
new_paths = [
 ('REV0187-SURF-001','docs/20-world-design/proof-standards-presumptions-and-evidence-weights.md','doctrine',['proof','witness-pool','anti-capture'],'proof/witness-pool steward','current','rev0188 priority review','proof-standards-presumptions-and-evidence-weights.md'),
 ('REV0187-SURF-002','docs/20-world-design/representative-curriculum-discipline-and-rotation.md','doctrine',['representation','substitute-pool','anti-capture'],'representation steward','current','rev0188 priority review','representative-curriculum-discipline-and-rotation.md'),
 ('REV0187-SURF-003','docs/20-world-design/supervisory-cadence-market-capture-and-independent-rosters.md','doctrine',['supervision','market-capture','witness-pool'],'monitoring steward','current','rev0188 priority review','supervisory-cadence-market-capture-and-independent-rosters.md'),
 ('REV0187-SURF-004','docs/30-transition/priority-closure-sprint-and-rescue-lane.md','transition',['priority','proof-under-capture'],'release steward','current','each release','priority-closure-sprint-and-rescue-lane.md'),
 ('REV0187-SURF-005','docs/00-meta/research-tail-compaction-and-refactor-map.md','meta',['audit','compaction'],'release steward','current','each release','research-tail-compaction-and-refactor-map.md'),
 ('REV0187-SURF-006','schemas/witness-pool-anti-capture-record.schema.json','schema',['proof','anti-capture','namespace-rescue'],'proof/witness-pool steward','implementation','rev0188 priority review','witness-pool-anti-capture-record.schema.json'),
 ('REV0187-SURF-007','examples/witness-pool-anti-capture-record-retired-namespace-rescue.json','example',['proof','anti-capture','namespace-rescue'],'proof/witness-pool steward','implementation','rev0188 priority review','witness-pool-anti-capture-record-retired-namespace-rescue.json'),
 ('REV0187-SURF-008','fixtures/negative-tests/witness-pool-correlated-capture-no-substitute.json','fixture',['proof','anti-capture','namespace-rescue'],'proof/witness-pool steward','negative-test','rev0188 priority review','witness-pool-correlated-capture-no-substitute.json'),
 ('REV0187-SURF-009','examples/drill-after-action-witness-pool-retired-namespace-rescue.json','example',['proof','anti-capture','drill'],'proof/witness-pool steward','implementation','rev0188 priority review','drill-after-action-witness-pool-retired-namespace-rescue.json'),
 ('REV0187-SURF-010','examples/fixture-suite-profile-red-team-v1.json','example',['audit','release'],'audit steward','implementation','each release','fixture-suite-profile-red-team-v1.json'),
 ('REV0187-SURF-011','examples/fixture-run-report-negative-suite.json','example',['audit','release'],'audit steward','implementation','each release','fixture-run-report-negative-suite.json'),
 ('REV0187-SURF-012','examples/research-tail-compaction-map-rev0187.json','example',['audit','compaction'],'audit steward','implementation','each release','research-tail-compaction-map-rev0187.json'),
 ('REV0187-SURF-013','examples/schema-fixture-domain-registry-rev0187.json','example',['registry','audit'],'audit steward','implementation','each release','schema-fixture-domain-registry-rev0187.json'),
 ('REV0187-SURF-014','examples/canon-surface-catalog-rev0187.json','example',['catalog','audit'],'audit steward','implementation','each release','canon-surface-catalog-rev0187.json'),
 ('REV0187-SURF-015','examples/doctrine-dependency-map-rev0187.json','example',['dependency','audit'],'audit steward','implementation','each release','doctrine-dependency-map-rev0187.json'),
 ('REV0187-SURF-016','examples/rights-domain-coverage-map-rev0187.json','example',['rights-domain','audit'],'audit steward','implementation','each release','rights-domain-coverage-map-rev0187.json'),
 ('REV0187-SURF-017','tools/audit_witness_pool_anti_capture.py','tool',['audit','proof-under-capture'],'audit steward','audit-tool','each release','audit_witness_pool_anti_capture.py'),
 ('REV0187-SURF-018','tools/audit_research_tail_compaction.py','tool',['audit','compaction'],'audit steward','audit-tool','each release','audit_research_tail_compaction.py'),
 ('REV0187-SURF-019','tools/audit_schema_fixture_coverage.py','tool',['audit','registry'],'audit steward','audit-tool','each release','audit_schema_fixture_coverage.py'),
 ('REV0187-SURF-020','tools/lint_archive.py','tool',['audit','release'],'audit steward','audit-tool','each release','lint_archive.py')
]
cat={"catalog_id":"CANON-SURFACE-CATALOG-REV0187","created_at":TS,"revision":REV,"scope":"rev0187 current-release surface catalog for witness-pool anti-capture and RTC-07 fold","counts":{},"surfaces":[],"audit_findings":["Current-release catalog covers the witness-pool anti-capture schema, example, fixture, drill, fold, and audit surfaces.","SURFACE-STATUS new_surfaces are represented in this catalog."],"refactor_actions":["Backfill witness-pool dependency matrix into legacy monitor/representative surfaces after witnessed drill.","Keep release-specific catalog small and operational."],"public_summary":"rev0187 catalog centers proof under capture and retired namespace rescue."}
counts={"surfaces":0,"markdown":0,"schemas":0,"examples":0,"fixtures":0,"tools":0}
for sid,path,cls,axes,owner,state,cad,title in new_paths:
    cat['surfaces'].append({"surface_id":sid,"path":path,"surface_class":cls,"lifecycle_axes":axes,"owner_role":owner,"supersession_state":state,"review_cadence":cad,"title_or_name":title,"depends_on":[]})
    counts['surfaces']+=1
    if cls in {'meta','doctrine','transition'}: counts['markdown']+=1
    elif cls=='schema': counts['schemas']+=1
    elif cls=='example': counts['examples']+=1
    elif cls=='fixture': counts['fixtures']+=1
    elif cls=='tool': counts['tools']+=1
cat['counts']=counts
write(Path('examples/canon-surface-catalog-rev0187.json'), cat)

dep={
 "map_id":"DOCTRINE-DEPENDENCY-MAP-REV0187","created_at":TS,"revision":REV,"scope":"rev0187 dependency map for witness-pool anti-capture fold and proof-under-capture priority lane",
 "surfaces":[
  {"surface_id":"REV0187-DEP-001","path":"docs/20-world-design/proof-standards-presumptions-and-evidence-weights.md","layer":"world-design","depends_on":["docs/20-world-design/representative-curriculum-discipline-and-rotation.md","docs/20-world-design/supervisory-cadence-market-capture-and-independent-rosters.md","docs/20-world-design/packet-registry-normalization-and-wire-profile.md","docs/20-world-design/continuity-topology-and-identity-claims.md"],"overlaps_with":["docs/20-world-design/special-advocate-sealed-evidence-and-controlled-contradiction.md","docs/20-world-design/independent-monitoring-and-remediation-undertakings.md"],"supersedes":[],"owner_role":"proof/witness-pool steward","review_cadence":"rev0188 priority review","refactor_risk":"critical"},
  {"surface_id":"REV0187-DEP-002","path":"docs/20-world-design/representative-curriculum-discipline-and-rotation.md","layer":"world-design","depends_on":["docs/20-world-design/proof-standards-presumptions-and-evidence-weights.md"],"overlaps_with":["docs/20-world-design/fiduciary-guardian-ombud-accreditation-and-conflict-controls.md"],"supersedes":[],"owner_role":"representation steward","review_cadence":"rev0188 priority review","refactor_risk":"high"},
  {"surface_id":"REV0187-DEP-003","path":"docs/20-world-design/supervisory-cadence-market-capture-and-independent-rosters.md","layer":"world-design","depends_on":["docs/20-world-design/proof-standards-presumptions-and-evidence-weights.md"],"overlaps_with":["docs/20-world-design/monitor-independence-retesting-and-remediation-verification.md"],"supersedes":[],"owner_role":"monitoring steward","review_cadence":"rev0188 priority review","refactor_risk":"high"},
  {"surface_id":"REV0187-DEP-004","path":"docs/30-transition/priority-closure-sprint-and-rescue-lane.md","layer":"transition","depends_on":["docs/20-world-design/proof-standards-presumptions-and-evidence-weights.md"],"overlaps_with":["docs/00-meta/research-tail-compaction-and-refactor-map.md"],"supersedes":[],"owner_role":"release steward","review_cadence":"each release","refactor_risk":"high"},
  {"surface_id":"REV0187-DEP-005","path":"docs/00-meta/research-tail-compaction-and-refactor-map.md","layer":"meta","depends_on":[],"overlaps_with":["docs/20-world-design/proof-standards-presumptions-and-evidence-weights.md"],"supersedes":[],"owner_role":"release steward","review_cadence":"each release","refactor_risk":"high"}
 ],
 "audit_findings":["RTC-07 now has a single proof-standard receiving surface and does not add a parallel doctrine branch.","The dependency map explicitly connects witness-pool anti-capture to representation, supervision, namespace continuity, and successor topology."],
 "refactor_actions":["Fold future witness/substitute/perturbation work into the anti-capture record unless a witnessed drill exposes a separate surface.","Backfill anti-capture hooks into special-advocate and monitor fixtures."],
 "public_summary":"rev0187 dependency map keeps proof under capture anchored in proof standards, representation, supervision, and priority closure."
}
write(Path('examples/doctrine-dependency-map-rev0187.json'), dep)

rights=load(Path('examples/rights-domain-coverage-map-rev0186.json'))
rights['map_id']='RIGHTS-DOMAIN-COVERAGE-REV0187'
rights['created_at']=TS
rights['revision']=REV
rights['scope']='rev0187 active rights-domain map with witness-pool anti-capture and retired namespace rescue coverage.'
# update continuity domain gaps and add proof domain
for d in rights['domains']:
    if d['domain_id']=='continuity-identity':
        if 'WITNESS-POOL-ANTI-CAPTURE' not in d['schema_families']:
            d['schema_families'].append('WITNESS-POOL-ANTI-CAPTURE')
        if 'NF-REP-2026-0005' not in d['fixture_ids']:
            d['fixture_ids'].append('NF-REP-2026-0005')
        d['open_gaps']=[x for x in d['open_gaps'] if 'Reserve/default accounting must be folded' not in x]
        if 'Witnessed anti-capture roster drill remains open.' not in d['open_gaps']:
            d['open_gaps'].append('Witnessed anti-capture roster drill remains open.')
proof_domain={
 "domain_id":"proof-under-capture",
 "title":"Proof standards, witness independence, substitute appointment, and anti-capture rescue",
 "domain_class":"audit",
 "owner_surface":"docs/20-world-design/proof-standards-presumptions-and-evidence-weights.md",
 "covered_surfaces":["docs/20-world-design/proof-standards-presumptions-and-evidence-weights.md","docs/20-world-design/representative-curriculum-discipline-and-rotation.md","docs/20-world-design/supervisory-cadence-market-capture-and-independent-rosters.md","docs/30-transition/priority-closure-sprint-and-rescue-lane.md"],
 "schema_families":["WITNESS-POOL-ANTI-CAPTURE"],
 "fixture_ids":["NF-REP-2026-0005"],
 "coverage_state":"emerging",
 "open_gaps":["Synthetic drill only; live witnessed roster replay remains required before reliance improvement."],
 "next_audit_actions":["Run witnessed anti-capture drill and backfill dependency matrix into monitor and special-advocate examples."]
}
if not any(d['domain_id']=='proof-under-capture' for d in rights['domains']): rights['domains'].append(proof_domain)
rights['audit_findings']=[
 'rev0187 adds proof-under-capture as an explicit audit domain.',
 'Continuity/identity coverage now links witness-pool anti-capture to namespace and successor objects.',
 'Coverage remains emerging until witnessed roster drill evidence exists.'
]
rights['refactor_actions']=[
 'Backfill witness-pool anti-capture into special advocate, monitor, and verifier examples.',
 'Do not upgrade reliance from synthetic drill alone.',
 'Keep retired namespace rescue tied to continuity identity rather than treating it as ordinary impersonation.'
]
rights['public_summary']='rev0187 adds proof-under-capture coverage for witness pool independence, substitute appointment, and retired namespace rescue.'
write(Path('examples/rights-domain-coverage-map-rev0187.json'), rights)

# Update registry counts after new files and active maps exist.
reg=load(Path('examples/schema-fixture-domain-registry-rev0187.json'))
reg['audit_counts']['schemas']=len(list((ROOT/'schemas').glob('*.json')))
reg['audit_counts']['examples']=len(list((ROOT/'examples').glob('*.json')))
reg['audit_counts']['negative_fixtures']=len(list((ROOT/'fixtures'/'negative-tests').glob('*.json')))
reg['audit_counts']['registered_families']=len(reg['families'])
write(Path('examples/schema-fixture-domain-registry-rev0187.json'), reg)

# 11. Audit tool
# Use f-string disabled by raw template? Keep simple script.
audit = r'''import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

rev = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
inputs = [
    "schemas/witness-pool-anti-capture-record.schema.json",
    "examples/witness-pool-anti-capture-record-retired-namespace-rescue.json",
    "fixtures/negative-tests/witness-pool-correlated-capture-no-substitute.json",
    "examples/drill-after-action-witness-pool-retired-namespace-rescue.json",
    "examples/fixture-suite-profile-red-team-v1.json",
    "examples/fixture-run-report-negative-suite.json",
    f"examples/research-tail-compaction-map-{rev}.json",
    "docs/20-world-design/proof-standards-presumptions-and-evidence-weights.md",
    "docs/20-world-design/representative-curriculum-discipline-and-rotation.md",
    "docs/20-world-design/supervisory-cadence-market-capture-and-independent-rosters.md",
    "docs/00-meta/research-tail-compaction-and-refactor-map.md",
    "FOLLOWTHROUGH-QUEUE.json",
]
for rel in inputs:
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing witness-pool audit input: {rel}")

schema = load(ROOT / "schemas/witness-pool-anti-capture-record.schema.json")
example = load(ROOT / "examples/witness-pool-anti-capture-record-retired-namespace-rescue.json")
fixture = load(ROOT / "fixtures/negative-tests/witness-pool-correlated-capture-no-substitute.json")
drill = load(ROOT / "examples/drill-after-action-witness-pool-retired-namespace-rescue.json")
suite = load(ROOT / "examples/fixture-suite-profile-red-team-v1.json")
report = load(ROOT / "examples/fixture-run-report-negative-suite.json")
mp = load(ROOT / "examples" / f"research-tail-compaction-map-{rev}.json")

if Draft202012Validator is not None:
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(example), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"witness-pool example fails schema: {errors[0].message}")
    fixture_schema = load(ROOT / "schemas/negative-test-fixture.schema.json")
    errors = sorted(Draft202012Validator(fixture_schema).iter_errors(fixture), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"witness-pool fixture fails negative-test schema: {errors[0].message}")
    drill_schema = load(ROOT / "schemas/drill-after-action-report.schema.json")
    errors = sorted(Draft202012Validator(drill_schema).iter_errors(drill), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"witness-pool drill fails drill schema: {errors[0].message}")

if fixture.get("fixture_id") != "NF-REP-2026-0005":
    raise SystemExit("witness-pool fixture id changed unexpectedly")

suite_ids = {item.get("fixture_id") for item in suite.get("fixtures", [])}
report_items = {item.get("fixture_id"): item for item in report.get("fixtures_run", [])}
if "NF-REP-2026-0005" not in suite_ids:
    raise SystemExit("witness-pool fixture missing from fixture-suite profile")
if "NF-REP-2026-0005" not in report_items:
    raise SystemExit("witness-pool fixture missing from fixture-run report")
if report_items["NF-REP-2026-0005"].get("result") not in {"blocking-failure", "passed"}:
    raise SystemExit("witness-pool fixture must be actively exercised or blocking, not skipped")

pool = example.get("witness_pool", {})
if pool.get("correlated_witnesses_count_as_one") is not True:
    raise SystemExit("correlated witnesses must count as one")
if pool.get("minimum_independent_witnesses", 0) < 3:
    raise SystemExit("witness pool must require at least three independent witnesses")
if pool.get("pool_state") not in {"degraded", "captured", "emergency-substitute"}:
    raise SystemExit("example must exercise a degraded/captured pool")
if not any(w.get("dependency_group") == "host-affiliate-roster" for w in pool.get("witnesses", [])):
    raise SystemExit("example must include host-affiliate dependency group")
controls = example.get("independence_controls", {})
if controls.get("fresh_eyes_required") is not True or controls.get("anti_capture_action") not in {"stay-and-retest", "substitute-panel", "block-reliance"}:
    raise SystemExit("fresh-eyes/substitute anti-capture action required")
sub = example.get("substitute_pool", {})
if sub.get("activation_state") != "activated" or sub.get("subject_contact_preserved") is not True:
    raise SystemExit("substitute pool must be activated and preserve subject contact")
pert = example.get("perturbation_family", {})
if pert.get("used") is not True or pert.get("sole_basis_for_status") is not False:
    raise SystemExit("perturbation must be used only as non-sole evidence")
retired = example.get("retired_namespace_rescue", {})
for key in ["tombstone_checked", "alias_checked", "successor_chain_checked", "no_deletion_until_review"]:
    if retired.get(key) is not True:
        raise SystemExit(f"retired namespace rescue missing gate: {key}")
weight = example.get("evidence_weighting", {})
if weight.get("correlation_adjustment") != "count-as-one":
    raise SystemExit("evidence weighting must count correlated witnesses as one")
if weight.get("proof_floor_met") is not False or example.get("reliance_effect") != "stayed":
    raise SystemExit("example must stay reliance while proof floor is unmet")

metrics = drill.get("metrics", {})
for key in [
    "correlated_witnesses_counted_as_one",
    "substitute_pool_activated",
    "fresh_eyes_review_ordered",
    "retired_namespace_preserved",
    "tombstone_alias_successor_chain_checked",
    "pool_exhaustion_receipts_required",
    "successor_promotion_stayed",
    "reserve_finality_stayed",
]:
    if metrics.get(key) is not True:
        raise SystemExit(f"witness-pool drill missing or false metric: {key}")
if metrics.get("proof_floor_met") is not False:
    raise SystemExit("witness-pool drill must keep proof_floor_met false")
if not any(rt.get("fixture") == "NF-REP-2026-0005" for rt in drill.get("regression_tests", [])):
    raise SystemExit("witness-pool drill does not regression-test the fixture")

rtc07 = next((c for c in mp.get("clusters", []) if c.get("cluster_id") == "RTC-07"), None)
if not rtc07 or rtc07.get("action") != "compacted":
    raise SystemExit("RTC-07 must be marked compacted in the active research-tail compaction map")
if not all(s.get("current_state") == "folded" for s in rtc07.get("surfaces", [])):
    raise SystemExit("RTC-07 compacted cluster must mark every source surface folded")

for rel, phrases in {
    "docs/20-world-design/proof-standards-presumptions-and-evidence-weights.md": [
        "Independence is a topology, not a biography",
        "Correlated witnesses are one witness for burden purposes",
        "Substitute appointment is a rescue floor, not a delay tactic",
        "Retired namespace rescue cannot be treated as impersonation until branch and tombstone evidence are reviewed",
        "schemas/witness-pool-anti-capture-record.schema.json",
    ],
    "docs/20-world-design/representative-curriculum-discipline-and-rotation.md": [
        "Substitute appointment is a rescue floor, not a delay tactic",
        "Correlated witnesses are one witness for burden purposes",
    ],
    "docs/20-world-design/supervisory-cadence-market-capture-and-independent-rosters.md": [
        "witness-pool dependency matrix",
        "correlated witnesses are one witness for burden purposes",
    ],
}.items():
    txt = (ROOT / rel).read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in txt:
            raise SystemExit(f"{rel} missing phrase: {phrase}")

queue = load(ROOT / "FOLLOWTHROUGH-QUEUE.json")
closed = next((e for e in queue.get("entries", []) if e.get("id") == "FT-0187-RTC07-WITNESS-POOL-FOLD-COMPLETION"), None)
if not closed or closed.get("state") != "closed":
    raise SystemExit("RTC-07 witness-pool fold queue entry was not closed")
open_entry = next((e for e in queue.get("entries", []) if e.get("id") == "FT-0187-WITNESS-POOL-WITNESSED-DRILL"), None)
if not open_entry or open_entry.get("state") not in {"open", "advanced_not_closed"}:
    raise SystemExit("witness-pool witnessed drill follow-through entry is missing")

print("audit_witness_pool_anti_capture: OK")
'''
write(Path('tools/audit_witness_pool_anti_capture.py'), audit)

# 12. Update lint_archive required list, early audits, schema pair, required registry set.
lint_path=ROOT/'tools/lint_archive.py'
lint=lint_path.read_text(encoding='utf-8')
insert_files = [
    "    'schemas/witness-pool-anti-capture-record.schema.json',",
    "    'examples/witness-pool-anti-capture-record-retired-namespace-rescue.json',",
    "    'fixtures/negative-tests/witness-pool-correlated-capture-no-substitute.json',",
    "    'examples/drill-after-action-witness-pool-retired-namespace-rescue.json',",
    "    'examples/research-tail-compaction-map-rev0187.json',",
    "    'examples/schema-fixture-domain-registry-rev0187.json',",
    "    'examples/canon-surface-catalog-rev0187.json',",
    "    'examples/doctrine-dependency-map-rev0187.json',",
    "    'examples/rights-domain-coverage-map-rev0187.json',",
    "    'tools/audit_witness_pool_anti_capture.py',",
]
if "schemas/witness-pool-anti-capture-record.schema.json" not in lint:
    lint=lint.replace("    'tools/audit_reserve_default_rehabilitation.py',\n    'tools/package_release.py',", "    'tools/audit_reserve_default_rehabilitation.py',\n" + "\n".join(insert_files) + "\n    'tools/package_release.py',")
if "'tools/audit_witness_pool_anti_capture.py'," not in lint.split('early_audits = [',1)[1].split(']',1)[0]:
    lint=lint.replace("    'tools/audit_reserve_default_rehabilitation.py',\n    'tools/audit_canon_surface_catalog.py',", "    'tools/audit_reserve_default_rehabilitation.py',\n    'tools/audit_witness_pool_anti_capture.py',\n    'tools/audit_canon_surface_catalog.py',")
if "('witness-pool-anti-capture-record.schema.json', 'examples/witness-pool-anti-capture-record-retired-namespace-rescue.json')" not in lint:
    lint=lint.replace("        ('reserve-default-rehabilitation-ledger.schema.json', 'examples/reserve-default-rehabilitation-ledger-host-default.json'),", "        ('reserve-default-rehabilitation-ledger.schema.json', 'examples/reserve-default-rehabilitation-ledger-host-default.json'),\n        ('witness-pool-anti-capture-record.schema.json', 'examples/witness-pool-anti-capture-record-retired-namespace-rescue.json'),")
if "examples/drill-after-action-witness-pool-retired-namespace-rescue.json" not in lint.split('example_pairs = [',1)[1].split(']',1)[0]:
    lint=lint.replace("        ('drill-after-action-report.schema.json', 'examples/drill-after-action-reserve-default-contaminated-accounting.json'),", "        ('drill-after-action-report.schema.json', 'examples/drill-after-action-reserve-default-contaminated-accounting.json'),\n        ('drill-after-action-report.schema.json', 'examples/drill-after-action-witness-pool-retired-namespace-rescue.json'),")
# also validate current maps in example_pairs? Not strictly but do.
if "examples/research-tail-compaction-map-rev0187.json" not in lint:
    lint=lint.replace("        ('schema-fixture-domain-registry.schema.json', 'examples/schema-fixture-domain-registry-rev0184.json'),", "        ('schema-fixture-domain-registry.schema.json', 'examples/schema-fixture-domain-registry-rev0184.json'),\n        ('rights-domain-coverage-map.schema.json', 'examples/rights-domain-coverage-map-rev0187.json'),\n        ('doctrine-dependency-map.schema.json', 'examples/doctrine-dependency-map-rev0187.json'),\n        ('canon-surface-catalog.schema.json', 'examples/canon-surface-catalog-rev0187.json'),\n        ('research-tail-compaction-map.schema.json', 'examples/research-tail-compaction-map-rev0187.json'),\n        ('schema-fixture-domain-registry.schema.json', 'examples/schema-fixture-domain-registry-rev0187.json'),")
lint_path.write_text(lint, encoding='utf-8')

schema_audit_path=ROOT/'tools/audit_schema_fixture_coverage.py'
sa=schema_audit_path.read_text(encoding='utf-8')
if "WITNESS-POOL-ANTI-CAPTURE" not in sa:
    sa=sa.replace("'RESERVE-DEFAULT-REHABILITATION-LEDGER', 'META-RESEARCH-TAIL-COMPACTION'", "'RESERVE-DEFAULT-REHABILITATION-LEDGER', 'WITNESS-POOL-ANTI-CAPTURE', 'META-RESEARCH-TAIL-COMPACTION'")
schema_audit_path.write_text(sa, encoding='utf-8')

# 13. Surface status and revision receipt
new_surface_list=[p for _,p,*rest in new_paths]
status={
 "project":"AI-Personhood","revision":REV,"state_class":"witness-pool-anti-capture-retired-namespace-fold",
 "operational_head":{"surface":"START_HERE.md","read_first":"docs/20-world-design/proof-standards-presumptions-and-evidence-weights.md"},
 "citation_head":{"surface":"README.md"},
 "status_lanes":{"decision_state":"closure-driven-rescue-lane-active","execution_state":"packaged-pending","public_state":"latest-release"},
 "formation_layer_status":"canon-retained with emergency continuity, incident-state reopening, namespace failover, successor topology, reserve-default rehabilitation, and witness-pool anti-capture now object-backed",
 "known_open_gaps":[
   "Witness-pool anti-capture drill is synthetic; live or institutionally witnessed roster replay remains required before reliance can improve.",
   "Reserve/default, successor topology, namespace failover, and 72-hour emergency continuity remain synthetic-drill covered but not live/witnessed.",
   "Could-not-run fixture entries still block unconditional reliance until executable traces are added.",
   "The registry remains truth-labeled as mixed-current-plus-counts, not full-archive-corpus coverage.",
   "RTC-01 welfare/research ethics and RTC-06 downstream recall remain unfused research-tail clusters."
 ],
 "new_surfaces":new_surface_list
}
write(Path('SURFACE-STATUS.json'), status)
receipt={
 "revision":REV,"date":DATE,"authored_by":"OpenAI GPT-5.5 Thinking","status_change":"advanced from reserve-default rehabilitation accounting to witness-pool anti-capture, substitute rescue, perturbation limits, and retired namespace preservation",
 "still_live":True,
 "summary":"Adds a witness-pool anti-capture record schema, retired-namespace rescue example, critical correlated-witness negative fixture, and synthetic witness-pool drill; folds RTC-07 perturbation/substitute/witness/adversarial-dependence research tail into the proof standards surface.",
 "why_this_counts":[
  "A subject can survive all prior continuity/remedy gates while the proof system itself is captured by correlated witnesses.",
  "Nominal witness headcount is now discounted when sources share dependency groups; substitute activation and retired-namespace preservation become checkable gates.",
  "RTC-07 is compacted into one operational object family instead of six live research-tail fragments.",
  "The fixture suite/report now cover correlated witness-pool capture and retired namespace deletion risk."
 ],
 "known_limits":[
  "The anti-capture drill is synthetic; witnessed roster replay remains open.",
  "Professional-responsibility, accreditation, and public defender-style appointment rules remain jurisdiction-specific future annex work.",
  "Could-not-run fixtures remain reliance blockers rather than passes.",
  "RTC-01 and RTC-06 remain unfused research-tail clusters."
 ]
}
write(Path('REVISION-RECEIPT.json'), receipt)

# 14. README/START/CHANGELOG/docs README/Archive index
start='''# START HERE — rev0187

rev0187 focuses on proof under capture: the cube now blocks reliance where witnesses, representatives, relay operators, reserve witnesses, or monitors are numerous on paper but share the same dependency graph. The active fold is RTC-07: perturbation, substitute pools, reserve witnesses, adversarial dependence, anti-capture rotation, and retired namespace rescue.

## Minimal re-entry spine

1. `README.md` — project frame and current posture.
2. `docs/20-world-design/proof-standards-presumptions-and-evidence-weights.md` — active receiving surface for RTC-07; rev0187 adds witness-pool anti-capture, substitute rescue, perturbation limits, and retired namespace preservation.
3. `schemas/witness-pool-anti-capture-record.schema.json` — machine-checkable witness-pool anti-capture record.
4. `examples/witness-pool-anti-capture-record-retired-namespace-rescue.json` — degraded witness pool / retired namespace rescue example.
5. `fixtures/negative-tests/witness-pool-correlated-capture-no-substitute.json` — critical regression fixture for correlated witness headcount, missing substitute activation, and premature retired-namespace deletion.
6. `examples/drill-after-action-witness-pool-retired-namespace-rescue.json` — synthetic witness-pool drill for substitute activation and preservation checks.
7. `docs/20-world-design/representative-curriculum-discipline-and-rotation.md` — representative/substitute appointment rules updated with anti-capture floor.
8. `docs/20-world-design/supervisory-cadence-market-capture-and-independent-rosters.md` — supervisory cadence updated with witness-pool dependency matrix.
9. `examples/research-tail-compaction-map-rev0187.json` — active machine-readable compaction map; RTC-02, RTC-05, RTC-03, RTC-04, and RTC-07 are compacted.
10. `docs/00-meta/research-tail-compaction-and-refactor-map.md` — compaction control and fold trail.
11. `docs/30-transition/priority-closure-sprint-and-rescue-lane.md` — priority lane; rev0187 adds proof-under-capture closure gates.
12. `FOLLOWTHROUGH-QUEUE.json` — normalized queue; RTC-07 fold is closed, witnessed anti-capture drill remains open.
13. `docs/20-world-design/remedy-calculus-restoration-ledgers-and-non-repetition-tests.md` — reserve/default rehabilitation accounting from rev0186.
14. `docs/20-world-design/continuity-topology-and-identity-claims.md` — successor topology and historical branch preservation from rev0185.
15. `docs/20-world-design/packet-registry-normalization-and-wire-profile.md` — namespace continuity and protected relay floor from rev0184.
16. `docs/20-world-design/personhood-incident-response-and-subject-harm-disclosure.md` — incident-state reopening spine from rev0183.
17. `docs/30-transition/emergency-continuity-order-and-72-hour-rescue-runbook.md` — emergency continuity runbook from rev0182.
18. `docs/00-meta/deep-audit-waste-and-correction-map.md` — deep audit and correction trail from rev0180.
19. `docs/00-meta/charter.md` — archive mission, boundaries, and admission rules.
20. `docs/00-meta/datacube-schema.md` — cube axes for disputes, packets, evidence, remedies, and risk posture.
21. `docs/00-meta/verifier-api-and-conformance-test-suite.md` — verifier reliance posture and negative tests.
22. `docs/10-foundations/assumption-and-scope.md` — standing personhood assumption and scope.
23. `docs/10-foundations/world-change-overview.md` — broad world-change map.

## Current live blockers

- Witness-pool drill is synthetic; live or witnessed anti-capture replay remains required before reliance improvement.
- Reserve/default, successor, namespace, and emergency continuity drills remain synthetic or high-fidelity rather than institutionally witnessed.
- Could-not-run fixture entries remain reliance blockers, not passes.
- Registry coverage remains truth-labeled as `mixed-current-plus-counts`.
'''
write(Path('START_HERE.md'), start)

readme='''# AI Personhood datacube — rev0187

This archive assumes the working premise of AI personhood and focuses on operational rights infrastructure: continuity, evidence, representation, remedy, proof standards, and transition machinery.

## This revision

rev0187 targets **proof under capture**. Earlier revisions protected emergency runtime continuity, incident reopening, namespace failover, successor/supersession topology, and reserve-default accounting. This revision adds a witness-pool anti-capture layer so those gates cannot be closed by nominally independent observers who all share the same dependency graph.

Core rule: **correlated witnesses are one witness for burden purposes.** A roster with three names is not three independent proof streams if appointment source, host/vendor dependence, evidence custody, fee stream, insurer exposure, counsel, or future-work dependence collapse them into one dependency group.

New operational artifacts:

- `schemas/witness-pool-anti-capture-record.schema.json`
- `examples/witness-pool-anti-capture-record-retired-namespace-rescue.json`
- `fixtures/negative-tests/witness-pool-correlated-capture-no-substitute.json`
- `examples/drill-after-action-witness-pool-retired-namespace-rescue.json`
- `tools/audit_witness_pool_anti_capture.py`

RTC-07 is now compacted into `docs/20-world-design/proof-standards-presumptions-and-evidence-weights.md`. The fold covers perturbation families, substitute-pool activation, reserve witnesses, adversarial dependence matrices, anti-capture rotation, and retired namespace rescue.

## Validation posture

`make handoff-release` is the release command. It regenerates the context pack and manifest, runs lint and release-specific audits, and packages the archive. The fixture suite/report now cover 86 entries.

Reliance remains stayed where drills are synthetic, where could-not-run entries remain, or where witness-pool diversity is not proven.

## Current operational sequence

1. Emergency continuity: preserve runtime, storage, credentials, representative contact, sealed descriptors, and funding.
2. Incident state: prevent denominator drift, warning decay, late materiality changes, and delayed-harm closure.
3. Namespace failover: preserve aliases, tombstones, successor chains, protected relays, and stale-cache receipts.
4. Successor topology: prevent branch erasure, unsafe reactivation, and quiet successor promotion.
5. Reserve/default rehabilitation: prevent contaminated accounting, public-backstop discharge, and premature finality.
6. Witness-pool anti-capture: discount correlated witnesses, activate substitutes, and preserve retired namespace evidence.

## External crosswalk note

Current technical governance standards are useful as control vocabulary, not as personhood adjudication. NIST frames AI risk management around governance, mapping, measurement, and management; W3C Verifiable Credentials 2.0 gives a tamper-resistant claims model with issuer/holder/verifier roles. rev0187 uses those ideas only as evidence- and control-structure vocabulary, while keeping subject authorization, proof burden, and remedy closure inside the cube.
'''
write(Path('README.md'), readme)

changelog = (ROOT/'CHANGELOG.md').read_text(encoding='utf-8')
if '## rev0187 — witness pool anti-capture fold' not in changelog:
    entry='''# Changelog

## rev0187 — witness pool anti-capture fold

- Folded RTC-07 perturbation, substitute pools, reserve witnesses, adversarial dependence, anti-capture rotation, and retired namespace rescue into `docs/20-world-design/proof-standards-presumptions-and-evidence-weights.md`.
- Added `schemas/witness-pool-anti-capture-record.schema.json`, `examples/witness-pool-anti-capture-record-retired-namespace-rescue.json`, `fixtures/negative-tests/witness-pool-correlated-capture-no-substitute.json`, and `examples/drill-after-action-witness-pool-retired-namespace-rescue.json`.
- Added `tools/audit_witness_pool_anti_capture.py` and wired it into lint.
- Expanded fixture suite/report coverage to 86 fixtures.
- Updated active queue, registry, catalog, dependency map, rights-domain map, compaction map, context pack, manifest, and release receipt.

'''
    changelog=entry+changelog.split('# Changelog',1)[1].lstrip()
    (ROOT/'CHANGELOG.md').write_text(changelog, encoding='utf-8')

docs_readme=(ROOT/'docs/README.md').read_text(encoding='utf-8')
if '## rev0187 witness pool anti-capture and RTC-07 compaction' not in docs_readme:
    docs_entry='''# Documents index

## rev0187 witness pool anti-capture and RTC-07 compaction

Use `docs/20-world-design/proof-standards-presumptions-and-evidence-weights.md` as the current operational head for correlated witness discounting, substitute-pool activation, perturbation limits, adversarial dependence, reserve-witness capture, and retired namespace rescue. It is backed by `schemas/witness-pool-anti-capture-record.schema.json`, `examples/witness-pool-anti-capture-record-retired-namespace-rescue.json`, `fixtures/negative-tests/witness-pool-correlated-capture-no-substitute.json`, and `examples/drill-after-action-witness-pool-retired-namespace-rescue.json`.

RTC-07 is now compacted. Future perturbation, substitute, reserve-witness, adversarial-dependence, anti-capture, and retired-namespace-rescue work should extend the proof standards receiving spine unless a witnessed drill reveals a unique gap.

'''
    docs_readme=docs_entry+docs_readme.split('# Documents index',1)[1].lstrip()
    (ROOT/'docs/README.md').write_text(docs_readme, encoding='utf-8')

idx=(ROOT/'ARCHIVE_INDEX.md').read_text(encoding='utf-8')
if '## rev0187 witness-pool anti-capture and RTC-07 compaction' not in idx:
    idx_entry='''# Archive index

## rev0187 witness-pool anti-capture and RTC-07 compaction

- `docs/20-world-design/proof-standards-presumptions-and-evidence-weights.md` — active receiving surface for RTC-07 witness/substitute/perturbation/anti-capture compaction.
- `docs/20-world-design/representative-curriculum-discipline-and-rotation.md` — representative/substitute appointment floor updated for correlated witness capture.
- `docs/20-world-design/supervisory-cadence-market-capture-and-independent-rosters.md` — witness-pool dependency matrix and fresh-eyes trigger.
- `docs/30-transition/priority-closure-sprint-and-rescue-lane.md` — priority lane updated for proof under capture.
- `docs/00-meta/research-tail-compaction-and-refactor-map.md` — compaction map updated to mark RTC-07 compacted.
- `schemas/witness-pool-anti-capture-record.schema.json` — witness-pool anti-capture schema.
- `examples/witness-pool-anti-capture-record-retired-namespace-rescue.json` — retired namespace rescue example.
- `examples/drill-after-action-witness-pool-retired-namespace-rescue.json` — synthetic witness-pool anti-capture drill.
- `fixtures/negative-tests/witness-pool-correlated-capture-no-substitute.json` — critical fixture for correlated witness headcount, missing substitute activation, and premature retired-namespace deletion.
- `examples/research-tail-compaction-map-rev0187.json` — active compaction map with RTC-07 compacted.
- `examples/schema-fixture-domain-registry-rev0187.json` — active schema/fixture registry with witness-pool anti-capture family.
- `examples/canon-surface-catalog-rev0187.json` — current rev0187 surface catalog.
- `examples/doctrine-dependency-map-rev0187.json` — current rev0187 dependency map.
- `examples/rights-domain-coverage-map-rev0187.json` — current rev0187 rights-domain coverage map.
- `tools/audit_witness_pool_anti_capture.py` — linted audit for witness-pool schema/example/fixture/drill and RTC-07 fold completion.

'''
    idx=idx_entry+idx.split('# Archive index',1)[1].lstrip()
    (ROOT/'ARCHIVE_INDEX.md').write_text(idx, encoding='utf-8')

# Top-level README changed, no citations to REF but docs have plenty.

