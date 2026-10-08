#!/usr/bin/env python3
"""Normalize OpenFEMA/ArcGIS IPAWS CAP archive JSON into flat lineage-safe CSV.

This tool is intentionally conservative: it never marks an archive record as local readiness closure.
It accepts OpenFEMA JSON with an `IpawsArchivedAlerts` array, an ArcGIS FeatureServer JSON
with `features[].attributes`, or a plain list of records. It expects `originalMessage` CAP XML when
available and emits one normalized row per CAP alert message, not one row per info/area expansion.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, re, sys, xml.etree.ElementTree as ET
from pathlib import Path

NS = {'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}

def text(node, path):
    el = node.find(path, NS)
    return (el.text or '').strip() if el is not None and el.text else ''

def texts(node, path):
    return [((el.text or '').strip()) for el in node.findall(path, NS) if (el.text or '').strip()]

def sha(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

def iter_records(payload):
    if isinstance(payload, dict) and 'IpawsArchivedAlerts' in payload:
        yield from payload['IpawsArchivedAlerts']
    elif isinstance(payload, dict) and 'features' in payload:
        for feat in payload['features']:
            yield feat.get('attributes', feat)
    elif isinstance(payload, list):
        yield from payload
    else:
        raise ValueError('Unsupported IPAWS payload shape: expected IpawsArchivedAlerts, features, or list')

def parse_cap_xml(xml_text: str):
    root = ET.fromstring(xml_text.encode('utf-8'))
    info = root.find('cap:info', NS)
    area = info.find('cap:area', NS) if info is not None else None
    event_code_value = ''
    event_code_name = ''
    if info is not None:
        ec = info.find('cap:eventCode', NS)
        if ec is not None:
            event_code_name = text(ec, 'cap:valueName')
            event_code_value = text(ec, 'cap:value')
    geos = []
    polygon_present = 'false'
    circle_present = 'false'
    if area is not None:
        geos = texts(area, 'cap:geocode/cap:value')
        polygon_present = 'true' if area.find('cap:polygon', NS) is not None else 'false'
        circle_present = 'true' if area.find('cap:circle', NS) is not None else 'false'
    status = text(root, 'cap:status')
    msg_type = text(root, 'cap:msgType')
    references = text(root, 'cap:references')
    identifier = text(root, 'cap:identifier')
    sender = text(root, 'cap:sender')
    sent = text(root, 'cap:sent')
    original_hash = sha(xml_text)
    dedupe_fingerprint = sha('|'.join([sender, identifier, sent, original_hash]))
    lineage_root = identifier
    if references:
        # CAP references triples are sender,identifier,sent separated by commas; multiple triples may be space-separated.
        parts = [p.strip() for p in re.split(r'\s+', references) if p.strip()]
        first = parts[0] if parts else references
        ref_fields = [p.strip() for p in first.split(',')]
        if len(ref_fields) >= 2 and ref_fields[1]:
            lineage_root = ref_fields[1]
    if msg_type == 'Cancel':
        lineage_state = 'cancel_signal'
        closure_effect = 'accepted_reopen_signal'
    elif msg_type == 'Error':
        lineage_state = 'error_signal'
        closure_effect = 'accepted_reopen_signal'
    elif msg_type == 'Update':
        lineage_state = 'superseding_update_hold'
        closure_effect = 'hold_no_upgrade'
    elif not geos and not (polygon_present == 'true' or circle_present == 'true'):
        lineage_state = 'geocode_gap_hold'
        closure_effect = 'hold_no_upgrade'
    elif status in ('Exercise','Test'):
        lineage_state = 'exercise_or_test_context'
        closure_effect = 'candidate_for_adjudication_not_closure' if status == 'Exercise' else 'hold_no_upgrade'
    elif status == 'Actual':
        lineage_state = 'public_actual_context'
        closure_effect = 'context_no_upgrade'
    else:
        lineage_state = 'manual_review_hold'
        closure_effect = 'hold_no_upgrade'
    return {
        'identifier': identifier,
        'sender': sender,
        'sent': sent,
        'status': status,
        'msgType': msg_type,
        'scope': text(root, 'cap:scope'),
        'references': references,
        'incidents': text(root, 'cap:incidents'),
        'event': text(info, 'cap:event') if info is not None else '',
        'eventCode_valueName': event_code_name,
        'eventCode_value': event_code_value,
        'urgency': text(info, 'cap:urgency') if info is not None else '',
        'severity': text(info, 'cap:severity') if info is not None else '',
        'certainty': text(info, 'cap:certainty') if info is not None else '',
        'effective': text(info, 'cap:effective') if info is not None else '',
        'onset': text(info, 'cap:onset') if info is not None else '',
        'expires': text(info, 'cap:expires') if info is not None else '',
        'senderName': text(info, 'cap:senderName') if info is not None else '',
        'headline': text(info, 'cap:headline') if info is not None else '',
        'description': text(info, 'cap:description') if info is not None else '',
        'instruction': text(info, 'cap:instruction') if info is not None else '',
        'web': text(info, 'cap:web') if info is not None else '',
        'areaDesc': text(area, 'cap:areaDesc') if area is not None else '',
        'geocode_values': ';'.join(geos),
        'polygon_present': polygon_present,
        'circle_present': circle_present,
        'normalized_lineage_key': lineage_root,
        'dedupe_fingerprint': dedupe_fingerprint,
        'original_message_sha256': original_hash,
        'lineage_state': lineage_state,
        'closure_effect': closure_effect,
    }

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--source-feed-id', default='FEED-0326-001')
    args = ap.parse_args(argv)
    raw = Path(args.input).read_text(encoding='utf-8')
    raw_hash = hashlib.sha256(raw.encode('utf-8')).hexdigest()
    payload = json.loads(raw)
    rows = []
    seen = set()
    for i, rec in enumerate(iter_records(payload), 1):
        xml_text = rec.get('originalMessage') or rec.get('ORIGINALMESSAGE') or rec.get('capXml') or ''
        if not xml_text:
            rows.append({'archive_record_id': rec.get('recordId', f'row-{i}'), 'source_feed_id': args.source_feed_id, 'raw_artifact_sha256': raw_hash, 'parse_status':'missing_originalMessage', 'closure_effect':'hold_no_upgrade'})
            continue
        try:
            out = parse_cap_xml(xml_text)
            out['archive_record_id'] = rec.get('recordId', rec.get('OBJECTID', f'row-{i}'))
            out['source_feed_id'] = args.source_feed_id
            out['raw_artifact_sha256'] = raw_hash
            out['parse_status'] = 'ok'
            if out['dedupe_fingerprint'] in seen:
                out['lineage_state'] = 'deduplicated_archive_row'
                out['closure_effect'] = 'context_no_upgrade'
            seen.add(out['dedupe_fingerprint'])
            rows.append(out)
        except Exception as e:
            rows.append({'archive_record_id': rec.get('recordId', f'row-{i}'), 'source_feed_id': args.source_feed_id, 'raw_artifact_sha256': raw_hash, 'parse_status':'parse_error', 'parse_error':str(e), 'closure_effect':'hold_no_upgrade'})
    # stable field ordering
    fields = ['archive_record_id','source_feed_id','raw_artifact_sha256','original_message_sha256','identifier','sender','sent','status','msgType','scope','references','incidents','event','eventCode_valueName','eventCode_value','urgency','severity','certainty','effective','onset','expires','senderName','headline','description','instruction','web','areaDesc','geocode_values','polygon_present','circle_present','normalized_lineage_key','dedupe_fingerprint','lineage_state','closure_effect','parse_status','parse_error']
    with Path(args.output).open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k:r.get(k,'') for k in fields})
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
