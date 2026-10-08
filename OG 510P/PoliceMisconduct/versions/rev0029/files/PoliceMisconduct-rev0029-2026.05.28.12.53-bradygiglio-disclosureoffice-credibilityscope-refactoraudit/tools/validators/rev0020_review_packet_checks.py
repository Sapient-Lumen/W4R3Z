"""Rev0020 review-packet validation facet.

This module is intentionally small: the monolithic tools/validate_surfaces.py still owns
make lint, but this facet documents and performs the rev0020 packet-kernel checks so
future revisions can continue factoring validation by office.
"""

from __future__ import annotations

from pathlib import Path
import json


def load(root: Path, rel: str):
    return json.loads((root / rel).read_text(encoding='utf-8'))


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    states = load(root, 'data/review_packets/rev0020_review_packet_states.json').get('states', [])
    types = load(root, 'data/review_packets/rev0020_review_packet_types.json').get('packet_types', [])
    risks = load(root, 'data/review_packets/rev0020_risk_tier_routes.json').get('risk_tiers', [])
    decisions = load(root, 'data/review_packets/rev0020_decision_receipt_templates.json').get('decision_templates', [])
    cross = load(root, 'data/review_packets/rev0020_source_family_packet_crosswalk.json').get('rows', [])
    if len(states) != 24:
        errors.append(f'rev0020 expected 24 packet states, found {len(states)}')
    if len(types) != 20:
        errors.append(f'rev0020 expected 20 packet types, found {len(types)}')
    if len(risks) != 10:
        errors.append(f'rev0020 expected 10 risk tiers, found {len(risks)}')
    if len(decisions) != 15:
        errors.append(f'rev0020 expected 15 decision templates, found {len(decisions)}')
    if len(cross) != 24:
        errors.append(f'rev0020 expected 24 source-family crosswalk rows, found {len(cross)}')
    for row in cross:
        if row.get('live_data_allowed_rev0020') is not False:
            errors.append(f"rev0020 crosswalk {row.get('crosswalk_id')} allows live data")
        if row.get('public_claims_admitted_rev0020') != 0:
            errors.append(f"rev0020 crosswalk {row.get('crosswalk_id')} admits public claims")
    return errors
