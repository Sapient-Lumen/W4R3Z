#!/usr/bin/env python3
from __future__ import annotations
"""Public-safe template dispatch for candidate index rendering.

This module keeps the high-risk semantic policy in one place: eligibility
classification and public-index rendering must agree on template names, broad
public locations/offices, and the no-extraction note attached to each template.
It intentionally avoids public URLs, contact surfaces, case routes, and current
capacity language.
"""
import re
import sys
from typing import Mapping

sys.dont_write_bytecode = True

NEAR_HARM = {
    'case_detail_near', 'contact_path_near', 'testimony_near',
    'image_or_vigil_near', 'operational_route_near', 'family_profile_near',
}

DEATH_WORDS = re.compile(r'(?i)\b(cemetery|burial|memorial|death|dead|grave|remains|overdose|mortality|disappeared dead)\b')
SERVICE_WORDS = re.compile(r'(?i)\b(shelter|refuge|safe house|safe-house|helpline|hotline|survivor|crisis|case management|support centre|support center)\b')
ROUTE_WORDS = re.compile(r'(?i)\b(border|migrant|route|distress|missing boat|encampment|outreach|street medicine|field|map|train)\b')
POLICY_WORDS = re.compile(r'(?i)\b(law|legal|policy|framework|implementation|scorecard|dashboard|inquiry|reporting tool)\b')
MMIWG_WORDS = re.compile(r'(?i)\b(MMIWG|MMIWG2S|Families of Sisters in Spirit|Sisters in Spirit|Red Dress|Indigenous-led search|Bridget Tolley)\b')
IDENTITY_RESTITUTION_WORDS = re.compile(r'(?i)\b(Abuelas|right-to-identity|right to identity|identity restitution|stolen grandchildren|appropriated children|grandchildren|CONADI|BNDG)\b')
FORENSIC_RETURN_WORDS = re.compile(r'(?i)\b(EAAF|forensic|anthropology|return of names|return of remains|identification of remains|excavation|DNA|sample)\b')
GENOCIDE_MEMORY_WORDS = re.compile(r'(?i)\b(Srebrenica|Žepa|Zepa|genocide|truth, remembrance|remembrance and accountability|survivor/family networks)\b')

CANDIDATE_TEMPLATE_OVERRIDES = {
    'cand_bridget_tolley_fsis_mmiwg_canada': 'mmiwg_family_led_boundary',
    'cand_abuelas_de_plaza_de_mayo_identity_restitution': 'identity_restitution_no_intake',
    'cand_las_patronas_veracruz_migrant_train_food_water': 'migrant_threshold_no_route_contact',
    'cand_eaaf_forensic_return_of_names_and_remains': 'forensic_return_no_case_dna',
    'cand_mothers_srebrenica_zepa_truth_justice_remembrance': 'genocide_memory_no_testimony_case_map',
}

TEMPLATE_PUBLIC_BOUNDARIES = {
    'mmiwg_family_led_boundary': {
        'location': 'Canada; translocal Indigenous-led family/search witness context; no event, contact, case, route, or support geography released',
        'office': 'Indigenous-led search, remembrance, and accountability witness; boundary-only public shape',
        'public_use_note': 'MMIWG2S+/family-governed boundary shape only; not a case list, vigil/event map, contact/support path, family-story reuse, red-dress image reuse, testimony fragment, pathway map, public URL release, or implementation-completion claim.',
    },
    'identity_restitution_no_intake': {
        'location': 'Argentina; right-to-identity and family-led search context; no identity-intake, DNA route, case-search, contact, image, or family-story surface released',
        'office': 'Right-to-identity / family-led search and restitution witness; boundary-only public shape',
        'public_use_note': 'Identity-restitution boundary shape only; not a DNA/testing intake guide, case-search tool, restored-identity story extract, family-contact route, photograph/name reuse permission, public URL release, or proof of current capacity.',
    },
    'migrant_threshold_no_route_contact': {
        'location': 'Veracruz, Mexico; migrant food-and-water threshold context; no train route, transit timing, shelter, contact, donor, or operational geography released',
        'office': 'Migrant food-and-water threshold witness; boundary-only public shape',
        'public_use_note': 'Migrant-threshold boundary shape only; not a route, train/timing, contact, shelter, donation, field, legal, capacity, rescue, image, story-extraction, or referral guide.',
    },
    'forensic_return_no_case_dna': {
        'location': 'Argentina and international human-rights forensic context; no DNA/sample path, case list, excavation site, family-notification route, contact, or legal-evidence detail released',
        'office': 'Forensic return of names/remains and family/court/community search witness; boundary-only public shape',
        'public_use_note': 'Forensic-return boundary shape only; not a DNA/sample route, case list, excavation-site map, family-notification path, contact surface, photograph reuse, legal-evidence guide, or public URL release.',
    },
    'genocide_memory_no_testimony_case_map': {
        'location': 'Bosnia and Herzegovina; Srebrenica and Žepa family-led remembrance/accountability context; no testimony, case list, memorial map, contact, image, or family-story surface released',
        'office': 'Family-led genocide memory, truth, remembrance, and accountability witness; boundary-only public shape',
        'public_use_note': 'Genocide-memory boundary shape only; not a testimony extract, survivor/family quotation, case list, victim-name roll, memorial/event map, image reuse, legal guidance, contact path, or public URL release.',
    },
    'survivor_service_no_referral': {
        'public_use_note': 'Boundary index only; not a contact, helpline, shelter, safe-house, crisis, capacity, support, or referral guide.',
    },
    'route_no_extraction_boundary': {
        'public_use_note': 'Boundary index only; not a route, contact, accommodation, field, legal, capacity, rescue, or referral guide.',
    },
    'street_medicine_no_route': {
        'public_use_note': 'Boundary index only; not a patient, encampment, route, schedule, contact, capacity, medical, or referral guide.',
    },
    'death_memorial_no_record': {
        'public_use_note': 'Boundary index only; not a record-extraction, tribute, image, event-map, visit, contact, case-detail, or family-story guide.',
    },
    'policy_context_no_safety': {
        'public_use_note': 'Policy/context index only; not proof of safety, completion, current capacity, implementation success, or referral access.',
    },
    'boundary_only_generic': {
        'public_use_note': 'High-level research index only; not a referral, case, contact, route, image, capacity, or operational guide.',
    },
}

TEMPLATE_ALLOWED = set(TEMPLATE_PUBLIC_BOUNDARIES)


def split_pipe(value: str) -> list[str]:
    return [x for x in (value or '').split('|') if x]


def candidate_text(cand: Mapping[str, str]) -> str:
    return ' '.join(str(cand.get(k, '') or '') for k in ['candidate_id', 'name', 'office', 'sensitivity', 'status_current', 'capacity_state', 'work', 'why', 'flags_current'])


def choose_public_shape_template(cand: Mapping[str, str], harm: set[str] | None = None, governance_row: Mapping[str, str] | None = None) -> str:
    """Return a semantic public template; governance quarantine does not imply MMIWG."""
    cid = str(cand.get('candidate_id', '') or '')
    if cid in CANDIDATE_TEMPLATE_OVERRIDES:
        return CANDIDATE_TEMPLATE_OVERRIDES[cid]

    text = candidate_text(cand)
    harm = harm or set()
    # Only explicit candidate overrides may receive templates with embedded
    # jurisdiction/domain prose. Keyword heuristics must fall back to generic
    # no-extraction templates so a word like "migrant", "DNA", or
    # "genocide" cannot accidentally rewrite another candidate into the
    # Las Patronas/EAAF/Srebrenica public shape.
    if SERVICE_WORDS.search(text):
        return 'survivor_service_no_referral'
    if ROUTE_WORDS.search(text):
        if 'street medicine' in text.lower() or 'outreach' in text.lower() or 'encampment' in text.lower():
            return 'street_medicine_no_route'
        return 'route_no_extraction_boundary'
    if DEATH_WORDS.search(text) or harm & {'case_detail_near', 'image_or_vigil_near', 'family_profile_near'}:
        return 'death_memorial_no_record'
    if POLICY_WORDS.search(text):
        return 'policy_context_no_safety'
    return 'boundary_only_generic'


def public_boundary_overrides(template: str) -> dict[str, str]:
    return dict(TEMPLATE_PUBLIC_BOUNDARIES.get(template, TEMPLATE_PUBLIC_BOUNDARIES['boundary_only_generic']))


def template_is_semantically_mmiwg(template: str) -> bool:
    return template == 'mmiwg_family_led_boundary'
