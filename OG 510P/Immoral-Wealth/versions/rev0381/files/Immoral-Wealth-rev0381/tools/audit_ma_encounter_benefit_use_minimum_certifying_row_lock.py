#!/usr/bin/env python3
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]
REV='rev0380'
CID='social-security-medicare-claim-security-rev0318'
bridge=json.loads((ROOT/'cases/social-security-medicare-claim-security-rev0318-ma-encounter-benefit-use-minimum-certifying-row-lock-rev0380.json').read_text(encoding='utf-8'))
required=['benefit_offered_flag','service_request_id','organization_determination_outcome','encounter_join_key','encounter_no_payment_variables_flag','payment_source_id','supplemental_benefit_denied_not_in_utilization_flag','rebate_actual_use_evidence','beneficiary_service_restoration_date']
blob=json.dumps(bridge, sort_keys=True)
missing=[x for x in required if x not in blob]
blocks=bridge.get('false_pass_blocks') or []
needed_blocks=['No encounter-data pass','No PBP/offered-benefit pass','No zero-utilization pass','No rebate-allocation pass','No supplemental-benefit-reporting pass']
missing_blocks=[x for x in needed_blocks if x not in blob]
if bridge.get('certification_status_after_rev0380')!='not_certified_current':
    print('ERROR: bridge must remain not certified current')
    sys.exit(1)
if missing or missing_blocks or len(blocks)<10:
    print('ERROR: weak row lock', missing, missing_blocks, len(blocks))
    sys.exit(1)
print('PASSED: MA encounter/benefit-use minimum certifying row lock audit')
