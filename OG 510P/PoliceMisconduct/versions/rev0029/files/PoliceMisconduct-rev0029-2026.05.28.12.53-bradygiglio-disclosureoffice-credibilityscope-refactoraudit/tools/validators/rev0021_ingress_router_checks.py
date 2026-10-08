"""Rev0021 ingress-router validation facet.

This facet checks the new ingress router and schema-audit surfaces. It is also mirrored
inside tools/validate_surfaces.py so `make lint` remains the stable entrypoint.
"""
from __future__ import annotations
from pathlib import Path
import json


def load(root: Path, rel: str):
    return json.loads((root / rel).read_text(encoding='utf-8'))


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    routes = load(root, 'data/ingress/rev0021_record_kind_ingress_routes.json').get('routes', [])
    artifacts = load(root, 'data/ingress/rev0021_artifact_type_registry.json').get('artifact_types', [])
    cross = load(root, 'data/ingress/rev0021_source_family_ingress_crosswalk.json').get('rows', [])
    gates = load(root, 'data/ingress/rev0021_ingress_gate_matrix.json').get('gates', [])
    fixtures = load(root, 'data/ingress/rev0021_synthetic_first_fixture_queue.json').get('fixtures', [])
    tripwires = load(root, 'data/ingress/rev0021_live_data_tripwires.json').get('tripwires', [])
    if len(artifacts) != 40: errors.append(f'rev0021 expected 40 artifact types, found {len(artifacts)}')
    if len(routes) != 44: errors.append(f'rev0021 expected 44 ingress routes, found {len(routes)}')
    if len(cross) != 24: errors.append(f'rev0021 expected 24 source-family crosswalk rows, found {len(cross)}')
    if len(gates) != 24: errors.append(f'rev0021 expected 24 ingress gates, found {len(gates)}')
    if len(fixtures) != 18: errors.append(f'rev0021 expected 18 synthetic fixtures, found {len(fixtures)}')
    if len(tripwires) != 25: errors.append(f'rev0021 expected 25 tripwires, found {len(tripwires)}')
    for r in routes:
        if r.get('live_records_created_rev0021') != 0 or r.get('public_claims_admitted_rev0021') != 0:
            errors.append(f"rev0021 route {r.get('ingress_route_id')} admits live records or public claims")
    for fx in fixtures:
        if fx.get('uses_live_people_or_real_incidents') is not False or fx.get('uses_live_source_payload') is not False:
            errors.append(f"rev0021 fixture {fx.get('fixture_id')} uses live data")
    return errors
