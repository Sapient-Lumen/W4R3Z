#!/usr/bin/env python3
import collections, json, pathlib, sys
root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
errors=[]
version=(root/'VERSION').read_text(encoding='utf-8').strip()
cube=json.loads((root/'cube-index.json').read_text(encoding='utf-8'))
blocked=[
    ('review_trigger','new_calibration_file'),
    ('anti_pattern','unclassified_anti_pattern'),
    ('remedy_type','not_remedy_specific'),
    ('floor_risk','no_specific_floor_risk'),
    ('market_structure','not_market_specific'),
    ('delivery_channel','not_channel_specific'),
    ('burden_mechanic','not_incidence_specific'),
    ('rights_affected','not_rights_specific'),
]
for rec in cube.get('route_records',[]):
    rid=rec.get('id')
    axes=rec.get('axes',{})
    for axis,value in blocked:
        if value in axes.get(axis,[]):
            errors.append(f'{rid} retains blocked live-axis sentinel {axis}={value}')
summary=cube.get('audit_summary',{})
if summary.get('axis_hygiene_required') is not True:
    errors.append('cube audit_summary must mark axis_hygiene_required=True')
metrics=summary.get('axis_hygiene_metrics',{})
required_zero=[
    'blocked_review_trigger_new_calibration_file',
    'blocked_anti_pattern_unclassified_anti_pattern',
    'blocked_remedy_type_not_remedy_specific',
    'blocked_floor_risk_no_specific_floor_risk',
    'blocked_market_not_market_specific',
    'blocked_channel_not_channel_specific',
    'blocked_burden_not_incidence_specific',
    'blocked_rights_not_rights_specific',
]
for key in required_zero:
    if metrics.get(key) != 0:
        errors.append(f'axis hygiene metric {key} must be 0, got {metrics.get(key)!r}')

# Rev0309 tax-administration anti-pattern gate: do not collapse access/fallback/contest failures back into generic rent_extraction.
tax_admin_rent=[rec.get('id') for rec in cube.get('route_records',[]) if rec.get('family')=='tax_administration_access' and 'rent_extraction' in rec.get('axes',{}).get('anti_pattern',[])]
axis_hygiene_metrics=summary.get('axis_hygiene_metrics',{})
if axis_hygiene_metrics.get('tax_admin_rent_extraction_antipattern_remaining') != len(tax_admin_rent):
    errors.append(f'axis hygiene metric tax_admin_rent_extraction_antipattern_remaining is stale: expected {len(tax_admin_rent)}, got {axis_hygiene_metrics.get("tax_admin_rent_extraction_antipattern_remaining")!r}')
if tax_admin_rent:
    errors.append('tax-administration route anti_pattern axes must be specific, not rent_extraction: '+', '.join(tax_admin_rent[:10]))

# Rev0310 legal-enforcement coercive-axis gate: do not hide seizure/privilege/willfulness/bounty/probation duties behind generic route labels.
legal_recs=[rec for rec in cube.get('route_records',[]) if rec.get('family')=='legal_enforcement_penalty']
legal_rent=[rec.get('id') for rec in legal_recs if 'rent_extraction' in rec.get('axes',{}).get('anti_pattern',[])]
legal_public_only=[rec.get('id') for rec in legal_recs if rec.get('axes',{}).get('delivery_channel') == ['public_channel']]
legal_legal_risk=[rec.get('id') for rec in legal_recs if 'legal_risk_transfer' in rec.get('axes',{}).get('burden_mechanic',[])]
legal_waiver=[rec.get('id') for rec in legal_recs if 'waiver' in rec.get('axes',{}).get('remedy_type',[])]
for metric_name, ids in {
    'legal_enforcement_rent_extraction_antipattern_remaining': legal_rent,
    'legal_enforcement_public_channel_only_remaining': legal_public_only,
    'legal_enforcement_legal_risk_transfer_burden_remaining': legal_legal_risk,
    'legal_enforcement_waiver_remedy_remaining': legal_waiver,
}.items():
    if axis_hygiene_metrics.get(metric_name) != len(ids):
        errors.append(f'axis hygiene metric {metric_name} is stale: expected {len(ids)}, got {axis_hygiene_metrics.get(metric_name)!r}')
if legal_rent:
    errors.append('legal-enforcement route anti_pattern axes must be coercion-specific, not rent_extraction: '+', '.join(legal_rent[:10]))
if legal_public_only:
    errors.append('legal-enforcement route delivery_channel axes must name the coercive channel, not only public_channel: '+', '.join(legal_public_only[:10]))
if legal_legal_risk:
    errors.append('legal-enforcement route burden_mechanic axes must name the concrete coercive burden, not legal_risk_transfer: '+', '.join(legal_legal_risk[:10]))
if legal_waiver:
    errors.append('legal-enforcement route remedy_type axes must name the concrete coercive remedy, not waiver: '+', '.join(legal_waiver[:10]))

# Rev0311 labor/care status-and-benefit axis gate: do not hide care-load, credential, pension, platform, or benefit duties behind generic route labels.
labor_recs=[rec for rec in cube.get('route_records',[]) if rec.get('family')=='labor_care_benefits']
labor_rent=[rec.get('id') for rec in labor_recs if 'rent_extraction' in rec.get('axes',{}).get('anti_pattern',[])]
labor_legal_risk=[rec.get('id') for rec in labor_recs if 'legal_risk_transfer' in rec.get('axes',{}).get('burden_mechanic',[])]
labor_public_only=[rec.get('id') for rec in labor_recs if rec.get('axes',{}).get('delivery_channel') == ['public_channel']]
for metric_name, ids in {
    'labor_care_rent_extraction_antipattern_remaining': labor_rent,
    'labor_care_legal_risk_transfer_burden_remaining': labor_legal_risk,
    'labor_care_public_channel_only_remaining': labor_public_only,
}.items():
    if axis_hygiene_metrics.get(metric_name) != len(ids):
        errors.append(f'axis hygiene metric {metric_name} is stale: expected {len(ids)}, got {axis_hygiene_metrics.get(metric_name)!r}')
if labor_rent:
    errors.append('labor/care route anti_pattern axes must name the status, care, credential, pension, childcare, or worker-benefit failure, not rent_extraction: '+', '.join(labor_rent[:10]))
if labor_legal_risk:
    errors.append('labor/care route burden_mechanic axes must name the concrete status/benefit burden, not legal_risk_transfer: '+', '.join(labor_legal_risk[:10]))
if labor_public_only:
    errors.append('labor/care route delivery_channel axes must name the care, benefit, credential, pension, platform, or dependency channel, not only public_channel: '+', '.join(labor_public_only[:10]))

# Rev0312 environment/climate non-compensable-harm axis gate: do not hide environmental harm behind generic rent, compliance, pass-through, legal-risk, public-channel, or community-benefit labels.
env_recs=[rec for rec in cube.get('route_records',[]) if rec.get('family')=='environment_climate_commons']
env_rent=[rec.get('id') for rec in env_recs if 'rent_extraction' in rec.get('axes',{}).get('anti_pattern',[])]
env_compliance=[rec.get('id') for rec in env_recs if 'compliance_theater' in rec.get('axes',{}).get('anti_pattern',[])]
env_public=[rec.get('id') for rec in env_recs if 'public_channel' in rec.get('axes',{}).get('delivery_channel',[])]
env_price_pass=[rec.get('id') for rec in env_recs if 'price_pass_through' in rec.get('axes',{}).get('burden_mechanic',[])]
env_legal_risk=[rec.get('id') for rec in env_recs if 'legal_risk_transfer' in rec.get('axes',{}).get('burden_mechanic',[])]
env_community=[rec.get('id') for rec in env_recs if 'community_benefit' in rec.get('axes',{}).get('remedy_type',[])]
for metric_name, ids in {
    'environment_rent_extraction_antipattern_remaining': env_rent,
    'environment_compliance_theater_antipattern_remaining': env_compliance,
    'environment_public_channel_delivery_remaining': env_public,
    'environment_price_pass_through_burden_remaining': env_price_pass,
    'environment_legal_risk_transfer_burden_remaining': env_legal_risk,
    'environment_community_benefit_remedy_remaining': env_community,
}.items():
    if axis_hygiene_metrics.get(metric_name) != len(ids):
        errors.append(f'axis hygiene metric {metric_name} is stale: expected {len(ids)}, got {axis_hygiene_metrics.get(metric_name)!r}')
if env_rent:
    errors.append('environment/climate route anti_pattern axes must name environmental mechanics, not rent_extraction: '+', '.join(env_rent[:10]))
if env_compliance:
    errors.append('environment/climate route anti_pattern axes must name environmental mechanics, not compliance_theater: '+', '.join(env_compliance[:10]))
if env_public:
    errors.append('environment/climate route delivery_channel axes must name the permit, registry, utility, insurance, mobility, fishery, minerals, port, monitoring, security, or insolvency channel, not public_channel: '+', '.join(env_public[:10]))
if env_price_pass:
    errors.append('environment/climate route burden_mechanic axes must name concrete environmental burden, not price_pass_through: '+', '.join(env_price_pass[:10]))
if env_legal_risk:
    errors.append('environment/climate route burden_mechanic axes must name concrete prefunding/insolvency burden, not legal_risk_transfer: '+', '.join(env_legal_risk[:10]))
if env_community:
    errors.append('environment/climate route remedy_type axes must name concrete environmental repair or no-go move, not community_benefit: '+', '.join(env_community[:10]))

# Rev0313 financial-system guarantee/reserve/custody axis gate: do not hide backstops, de-risking, stablecoin reserves, event contracts, priority, or policyholder surplus behind generic route labels.
fin_recs=[rec for rec in cube.get('route_records',[]) if rec.get('family')=='financial_system_risk']
fin_rent=[rec.get('id') for rec in fin_recs if 'rent_extraction' in rec.get('axes',{}).get('anti_pattern',[])]
fin_public_loss=[rec.get('id') for rec in fin_recs if 'public_loss_private_upside' in rec.get('axes',{}).get('anti_pattern',[])]
fin_compliance=[rec.get('id') for rec in fin_recs if 'compliance_theater' in rec.get('axes',{}).get('anti_pattern',[])]
fin_platform=[rec.get('id') for rec in fin_recs if 'platform_account' in rec.get('axes',{}).get('delivery_channel',[])]
fin_legal_risk=[rec.get('id') for rec in fin_recs if 'legal_risk_transfer' in rec.get('axes',{}).get('burden_mechanic',[])]
fin_fee=[rec.get('id') for rec in fin_recs if 'fee_surcharge' in rec.get('axes',{}).get('burden_mechanic',[])]
fin_clawback=[rec.get('id') for rec in fin_recs if 'clawback' in rec.get('axes',{}).get('remedy_type',[])]
fin_disclosure=[rec.get('id') for rec in fin_recs if 'disclosure' in rec.get('axes',{}).get('remedy_type',[])]
for metric_name, ids in {
    'financial_rent_extraction_antipattern_remaining': fin_rent,
    'financial_public_loss_private_upside_antipattern_remaining': fin_public_loss,
    'financial_compliance_theater_antipattern_remaining': fin_compliance,
    'financial_platform_account_delivery_remaining': fin_platform,
    'financial_legal_risk_transfer_burden_remaining': fin_legal_risk,
    'financial_fee_surcharge_burden_remaining': fin_fee,
    'financial_clawback_remedy_remaining': fin_clawback,
    'financial_disclosure_remedy_remaining': fin_disclosure,
}.items():
    if axis_hygiene_metrics.get(metric_name) != len(ids):
        errors.append(f'axis hygiene metric {metric_name} is stale: expected {len(ids)}, got {axis_hygiene_metrics.get(metric_name)!r}')
if fin_rent:
    errors.append('financial-system route anti_pattern axes must name guarantee, reserve, de-risking, event-contract, priority, or surplus mechanics, not rent_extraction: '+', '.join(fin_rent[:10]))
if fin_public_loss:
    errors.append('financial-system route anti_pattern axes must name the concrete guarantee/reserve/priority failure, not public_loss_private_upside: '+', '.join(fin_public_loss[:10]))
if fin_compliance:
    errors.append('financial-system route anti_pattern axes must name fiscal-risk or reporting mechanics, not compliance_theater: '+', '.join(fin_compliance[:10]))
if fin_platform:
    errors.append('financial-system route delivery_channel axes must name the exchange, account, self-exclusion, custody, reserve, backstop, priority, or policyholder channel, not platform_account: '+', '.join(fin_platform[:10]))
if fin_legal_risk:
    errors.append('financial-system route burden_mechanic axes must name the concrete market-access, preemption, reserve, or priority burden, not legal_risk_transfer: '+', '.join(fin_legal_risk[:10]))
if fin_fee:
    errors.append('financial-system route burden_mechanic axes must name the concrete charge/loss mechanics, not fee_surcharge: '+', '.join(fin_fee[:10]))
if fin_clawback:
    errors.append('financial-system route remedy_type axes must name the concrete recovery, reserve, priority, or repair move, not clawback: '+', '.join(fin_clawback[:10]))
if fin_disclosure:
    errors.append('financial-system route remedy_type axes must name the concrete fiscal/market remedy, not disclosure: '+', '.join(fin_disclosure[:10]))


# Rev0314 wealth/property and procurement axis gates: do not hide valuation, liquidity, registry, subsidy-condition, stockpile, patent-access, or classified-procurement mechanics behind generic labels.
wealth_recs=[rec for rec in cube.get('route_records',[]) if rec.get('family')=='wealth_property_rent']
wealth_rent=[rec.get('id') for rec in wealth_recs if 'rent_extraction' in rec.get('axes',{}).get('anti_pattern',[])]
wealth_compliance=[rec.get('id') for rec in wealth_recs if 'compliance_theater' in rec.get('axes',{}).get('anti_pattern',[])]
wealth_public_loss=[rec.get('id') for rec in wealth_recs if 'public_loss_private_upside' in rec.get('axes',{}).get('anti_pattern',[])]
wealth_price_pass=[rec.get('id') for rec in wealth_recs if 'price_pass_through' in rec.get('axes',{}).get('burden_mechanic',[])]
wealth_deferral=[rec.get('id') for rec in wealth_recs if 'deferral' in rec.get('axes',{}).get('remedy_type',[])]
for metric_name, ids in {
    'wealth_property_rent_extraction_antipattern_remaining': wealth_rent,
    'wealth_property_compliance_theater_antipattern_remaining': wealth_compliance,
    'wealth_property_public_loss_private_upside_antipattern_remaining': wealth_public_loss,
    'wealth_property_price_pass_through_burden_remaining': wealth_price_pass,
    'wealth_property_deferral_remedy_remaining': wealth_deferral,
}.items():
    if axis_hygiene_metrics.get(metric_name) != len(ids):
        errors.append(f'axis hygiene metric {metric_name} is stale: expected {len(ids)}, got {axis_hygiene_metrics.get(metric_name)!r}')
if wealth_rent:
    errors.append('wealth/property route anti_pattern axes must name site-rent, registry, valuation, public-asset, or transfer mechanics, not rent_extraction: '+', '.join(wealth_rent[:10]))
if wealth_compliance:
    errors.append('wealth/property route anti_pattern axes must name wealth-register or public-asset mechanics, not compliance_theater: '+', '.join(wealth_compliance[:10]))
if wealth_public_loss:
    errors.append('wealth/property route anti_pattern axes must name public-asset or social-dividend mechanics, not public_loss_private_upside: '+', '.join(wealth_public_loss[:10]))
if wealth_price_pass:
    errors.append('wealth/property route burden_mechanic axes must name the concrete valuation, tenant, transfer, or public-asset burden, not price_pass_through: '+', '.join(wealth_price_pass[:10]))
if wealth_deferral:
    errors.append('wealth/property route remedy_type axes must name the concrete liquidity, hardship, site-rent, or reset remedy, not deferral: '+', '.join(wealth_deferral[:10]))

proc_recs=[rec for rec in cube.get('route_records',[]) if rec.get('family')=='public_procurement_industrial_policy']
proc_rent=[rec.get('id') for rec in proc_recs if 'rent_extraction' in rec.get('axes',{}).get('anti_pattern',[])]
proc_access=[rec.get('id') for rec in proc_recs if 'access_exclusion' in rec.get('axes',{}).get('anti_pattern',[])]
proc_compliance=[rec.get('id') for rec in proc_recs if 'compliance_theater' in rec.get('axes',{}).get('anti_pattern',[])]
proc_price_pass=[rec.get('id') for rec in proc_recs if 'price_pass_through' in rec.get('axes',{}).get('burden_mechanic',[])]
proc_clawback=[rec.get('id') for rec in proc_recs if 'clawback' in rec.get('axes',{}).get('remedy_type',[])]
for metric_name, ids in {
    'procurement_rent_extraction_antipattern_remaining': proc_rent,
    'procurement_access_exclusion_antipattern_remaining': proc_access,
    'procurement_compliance_theater_antipattern_remaining': proc_compliance,
    'procurement_price_pass_through_burden_remaining': proc_price_pass,
    'procurement_clawback_remedy_remaining': proc_clawback,
}.items():
    if axis_hygiene_metrics.get(metric_name) != len(ids):
        errors.append(f'axis hygiene metric {metric_name} is stale: expected {len(ids)}, got {axis_hygiene_metrics.get(metric_name)!r}')
if proc_rent:
    errors.append('procurement route anti_pattern axes must name subsidy, stockpile, patent, emergency, or classified-contract mechanics, not rent_extraction: '+', '.join(proc_rent[:10]))
if proc_access:
    errors.append('procurement route anti_pattern axes must name the concrete allocation or paywall failure, not access_exclusion: '+', '.join(proc_access[:10]))
if proc_compliance:
    errors.append('procurement route anti_pattern axes must name the concrete inventory, testing, or capacity failure, not compliance_theater: '+', '.join(proc_compliance[:10]))
if proc_price_pass:
    errors.append('procurement route burden_mechanic axes must name the concrete subsidy, recovery, stockpile, paywall, or cost-overrun burden, not price_pass_through: '+', '.join(proc_price_pass[:10]))
if proc_clawback:
    errors.append('procurement route remedy_type axes must name the concrete recapture, recovery, allocation, march-in, audit, or recompetition move, not clawback: '+', '.join(proc_clawback[:10]))

# Rev0305 compression gate: stop live-route controlled vocabulary from regrowing route-local singleton sprawl.
if summary.get('axis_vocabulary_compression_required') is not True:
    errors.append('cube audit_summary must mark axis_vocabulary_compression_required=True')
compressed_axes=['anti_pattern','review_trigger','base','instrument','proof_posture']
route_counts={}
for axis in compressed_axes:
    c=collections.Counter()
    for rec in cube.get('route_records',[]):
        c.update(rec.get('axes',{}).get(axis,[]))
    route_counts[axis]={'unique':len(c),'singletons':sum(1 for n in c.values() if n==1),'uses':sum(c.values())}
axis_declared={a.get('id'):len(a.get('values',[])) for a in cube.get('axes',[])}
compression=summary.get('axis_vocabulary_compression_metrics',{})
expected={}
for axis in compressed_axes:
    expected[f'route_{axis}_unique_after']=route_counts[axis]['unique']
    expected[f'route_{axis}_singletons_after']=route_counts[axis]['singletons']
    expected[f'route_{axis}_uses_after']=route_counts[axis]['uses']
    expected[f'declared_{axis}_values_after']=axis_declared.get(axis)
for key,val in expected.items():
    if compression.get(key) != val:
        errors.append(f'axis vocabulary compression metric {key} is stale: expected {val}, got {compression.get(key)!r}')
ceilings={
    'route_anti_pattern_unique_after':170,
    'route_anti_pattern_singletons_after':140,
    'route_review_trigger_unique_after':130,
    'route_review_trigger_singletons_after':105,
    'route_base_unique_after':45,
    'route_base_singletons_after':20,
    'route_instrument_unique_after':40,
    'route_instrument_singletons_after':12,
    'route_proof_posture_unique_after':35,
    'route_proof_posture_singletons_after':5,
    'declared_anti_pattern_values_after':215,
    'declared_review_trigger_values_after':165,
    'declared_base_values_after':120,
    'declared_instrument_values_after':55,
    'declared_proof_posture_values_after':90,
}
for key,limit in ceilings.items():
    val=compression.get(key)
    if not isinstance(val,int) or val > limit:
        errors.append(f'axis vocabulary compression ceiling exceeded: {key}={val!r} > {limit}')
report_rel=cube.get('axis_hygiene_audit_report_path')
if not report_rel or not (root/report_rel).exists():
    errors.append('cube-index.json axis_hygiene_audit_report_path must point to an existing report')
elif version not in (root/report_rel).read_text(encoding='utf-8')[:200]:
    errors.append('axis hygiene audit report opening must name the active revision')
# Ensure declared axis values match route usage plus declarative case-contract
# requirements; otherwise the cube silently keeps dead vocabulary or drops case vocabulary.
case_contracts=json.loads((root/'docs/00-meta/case-contracts.json').read_text(encoding='utf-8'))
case_axis_values={}
for contract in case_contracts.get('contracts',[]):
    for ax, vals in contract.get('required_axes',{}).items():
        case_axis_values.setdefault(ax,set()).update(vals)
for axis in cube.get('axes',[]):
    aid=axis.get('id')
    declared=set(axis.get('values',[]))
    used={v for rec in cube.get('route_records',[]) for v in rec.get('axes',{}).get(aid,[])} | case_axis_values.get(aid,set())
    if declared != used:
        errors.append(f'axis {aid} declared values do not match route plus case-contract usage: extra={sorted(declared-used)[:10]} missing={sorted(used-declared)[:10]}')
if errors:
    raise SystemExit('\n'.join(errors))
print('axis hygiene audit ok')
