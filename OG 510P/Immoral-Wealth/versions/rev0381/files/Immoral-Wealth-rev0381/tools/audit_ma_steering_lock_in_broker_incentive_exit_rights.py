#!/usr/bin/env python3
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]
REV='rev0381'
bridge=json.loads((ROOT/'cases/social-security-medicare-claim-security-rev0318-ma-steering-lock-in-broker-incentive-exit-rights-bridge-rev0381.json').read_text(encoding='utf-8'))
required=['enrollment_event_id','broker_or_agent_npn','tpmo_or_lead_generator_id','compensation_amount_initial','renewal_compensation_amount','plan_universe_presented','plans_not_presented_or_blocked','financial_incentive_or_bonus_marker','marketing_or_hcp_referral_payment_marker','written_consent_to_share_lead_data','beneficiary_disability_status','dual_lis_or_complex_care_marker','misleading_marketing_complaint_id','cms_complaint_tracking_module_or_ctm_id','special_enrollment_period_or_correction_right','medigap_guaranteed_issue_status','medigap_underwriting_barrier','exit_to_traditional_medicare_feasibility','post_enrollment_denial_or_access_problem','claim_security_row_join_key']
blob=json.dumps(bridge, sort_keys=True)
missing=[x for x in required if x not in blob]
blocks=bridge.get('false_pass_blocks') or []
needed=['No enrollment-neutral pass','No broker-disclosure pass','No compensation-cap pass','No complaint-only pass','No Medigap-exit pass','No DOJ-allegation pass','No OIG-work-plan pass']
missing_blocks=[x for x in needed if x not in blob]
if bridge.get('certification_status_after_rev0381')!='not_certified_current' or bridge.get('certified_current_case_count_after')!=0:
    print('ERROR: rev0381 bridge must remain not certified current')
    sys.exit(1)
if missing or missing_blocks or len(blocks)<10:
    print('ERROR: weak steering/lock-in bridge', missing, missing_blocks, len(blocks))
    sys.exit(1)
print('PASSED: MA steering/lock-in broker incentive and exit-rights bridge audit')
