#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
required=[
 'FIELDWORK-CHARTER.json','CONTRIBUTOR-CONSENT-STATE-MACHINE.json','TESTIMONY-INTAKE-SCHEMA.json','INTERVIEW-PROTOCOL-ATLAS.json',
 'QUOTE-AND-PARAPHRASE-GATE.json','DEIDENTIFICATION-AND-RECONTEXTUALIZATION-STANDARD.json','PARTICIPANT-DISTRESS-AND-STOP-PROTOCOL.json',
 'CONTRIBUTOR-COMPENSATION-AND-CREDIT-LEDGER.json','DATA-CUSTODY-AND-ACCESS-CONTROL-LEDGER.json','FIELDWORK-REVIEW-BOARD-CHARTER.json',
 'FIELDWORK-SAMPLE-QUEUE.json','PILOT-INTERVIEW-DRYRUN-PACKET.json','SOURCE-ACQUISITION-TRIAGE-MATRIX.json'
]
missing=[p for p in required if not (ROOT/p).exists()]
if missing: raise SystemExit('FIELDWORK CHECK FAIL missing '+repr(missing))
charter=json.loads((ROOT/'FIELDWORK-CHARTER.json').read_text())
if charter.get('current_state',{}).get('testimony_collection_allowed') is not False:
    raise SystemExit('FIELDWORK CHECK FAIL testimony collection appears enabled')
if charter.get('current_state',{}).get('private_contributor_record_count') != 0:
    raise SystemExit('FIELDWORK CHECK FAIL private contributor count nonzero')
consent=json.loads((ROOT/'CONTRIBUTOR-CONSENT-STATE-MACHINE.json').read_text())
state_names={s['name'] for s in consent['states']}
needed={'no_contact_no_material','approved_for_internal_archive_only','approved_for_public_paraphrase_no_quote','approved_for_exact_quote_anonymous','withdrawn_closed'}
if not needed.issubset(state_names):
    raise SystemExit('FIELDWORK CHECK FAIL missing consent states '+repr(sorted(needed-state_names)))
quote=json.loads((ROOT/'QUOTE-AND-PARAPHRASE-GATE.json').read_text())
if 'suicide means or method detail' not in quote.get('quote_blockers',[]):
    raise SystemExit('FIELDWORK CHECK FAIL suicide method quote blocker missing')
custody=json.loads((ROOT/'DATA-CUSTODY-AND-ACCESS-CONTROL-LEDGER.json').read_text())
if 'do not contain raw private audio' not in custody.get('hard_rule',''):
    raise SystemExit('FIELDWORK CHECK FAIL custody hard rule too weak')
print('FIELDWORK CHECK OK: protocols present; testimony collection remains disabled; dry run only')
