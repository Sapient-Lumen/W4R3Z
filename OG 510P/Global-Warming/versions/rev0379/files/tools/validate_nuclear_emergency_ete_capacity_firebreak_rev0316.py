#!/usr/bin/env python3
"""Validate rev0316 BVPS ETE/capacity/public-context firebreak tables."""
import csv, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
CUBE = ROOT / 'cube'

def read(name):
    with open(CUBE/name, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

expected = {
('traditional_vehicle_demand_residential_population','winter_day','fair_weather'):(164514,65222,195,316),
('traditional_vehicle_demand_residential_population','winter_day','adverse_weather'):(164514,65222,280,442),
('traditional_vehicle_demand_residential_population','winter_night','fair_weather'):(130634,55178,175,261),
('traditional_vehicle_demand_residential_population','winter_night','adverse_weather'):(130634,55178,220,365),
('traditional_vehicle_demand_residential_population','summer_weekend','fair_weather'):(135351,56567,170,258),
('traditional_vehicle_demand_residential_population','summer_weekend','adverse_weather'):(135351,56567,200,317),
('high_vehicle_demand_residential_population','winter_day','fair_weather'):(164514,89066,255,417),
('high_vehicle_demand_residential_population','winter_day','adverse_weather'):(164514,89066,360,585),
('high_vehicle_demand_residential_population','winter_night','fair_weather'):(130634,79022,220,364),
('high_vehicle_demand_residential_population','winter_night','adverse_weather'):(130634,79022,315,498),
('high_vehicle_demand_residential_population','summer_weekend','fair_weather'):(135351,80411,225,361),
('high_vehicle_demand_residential_population','summer_weekend','adverse_weather'):(135351,80411,275,444),
}
rows = read('nuclear-emergency-beavervalley-ete-loadcase-rev0316.csv')
if len(rows) != 12:
    raise SystemExit(f'expected 12 ETE rows, got {len(rows)}')
for r in rows:
    key=(r['scenario_family'],r['season_time'],r['weather'])
    vals=(int(r['population']),int(r['vehicles']),int(r['evacuation_90_percent_minutes']),int(r['evacuation_100_percent_minutes']))
    if expected.get(key) != vals:
        raise SystemExit(f'ETE mismatch {key}: {vals} expected {expected.get(key)}')
cap = read('nuclear-emergency-beavervalley-pa-reception-mass-care-capacity-rev0316.csv')
total = [r for r in cap if r['support_county']=='TOTAL'][0]
if (int(total['mass_care_requirement']), int(total['listed_capacity']), int(total['listed_margin'])) != (8507,25914,17407):
    raise SystemExit('mass-care total mismatch')
assign = read('nuclear-emergency-beavervalley-pa-reception-assignment-rev0316.csv')
if len(assign) != 27 or sum(int(r['risk_population_2020']) for r in assign) != 85081:
    raise SystemExit('reception assignment count/population mismatch')
leaks = read('nuclear-emergency-public-context-to-local-closure-leak-test-rev0316.csv')
if any(r['public_closure_leak'] != 'no' or r['status'] != 'pass' for r in leaks):
    raise SystemExit('public closure leak test failed')
print('rev0316 validation helper passed')
