#!/usr/bin/env python3
"""Local FT-0181 validator fixtures that preserve field-lane source chains.

These helpers are for check scripts only. They build minimized, non-evidence
source artifacts under the caller's scratch/field/ft0181/validation tree so
positive validator paths exercise the same provenance anchors as real field
intake without borrowing checker scratch.
"""
from __future__ import annotations

from pathlib import Path

from prepare_ft0181_owner_request_packet import build_packet
from record_ft0181_owner_contact_status import OPERATOR_CONFIRMATIONS, build_status
from record_ft0181_owner_send_log import OPERATOR_CONFIRMATION as SEND_LOG_CONFIRMATION, build_send_log

DEFAULT_SERVICE_LABEL = 'AIEDU-SR-003 draft reminder pilot'
DEFAULT_OWNER_ROLE = 'accountable service owner route'
DEFAULT_SOURCE_RECORD_SET = 'owner-maintained local service record set'
DEFAULT_DATE_RANGE = '2026-06-01 through 2026-06-07'


def rel_to_root(path: Path, *, root: Path) -> str:
    return path.relative_to(root).as_posix()


def build_valid_sent_contact_status(
    output_path: Path,
    *,
    root: Path,
    sent_date: str = '2026-06-16',
    response_due_date: str = '2026-06-23',
    status_date: str | None = None,
    attempt_count: int = 1,
    source_slug: str = 'source-send-log',
    service_label: str = DEFAULT_SERVICE_LABEL,
    owner_role: str = DEFAULT_OWNER_ROLE,
    source_record_set: str = DEFAULT_SOURCE_RECORD_SET,
    date_range: str = DEFAULT_DATE_RANGE,
) -> Path:
    """Build a valid SENT_AWAITING_REPLY status with an anchored send-log source."""
    status_date = status_date or sent_date
    source_root = output_path.parent.parent / 'source-artifacts'
    packet_dir = source_root / 'owner-request-packets' / source_slug
    packet = build_packet(
        output_dir=packet_dir,
        service_label=service_label,
        owner_role=owner_role,
        source_record_set=source_record_set,
        date_range=date_range,
        return_date=response_due_date,
        overwrite=True,
    )
    if not packet.get('ok'):
        raise RuntimeError(f'contact-status source packet did not build: {packet}')
    send_dir = source_root / 'owner-send-logs' / source_slug
    send_log = build_send_log(
        output_dir=send_dir,
        packet_manifest=packet_dir / 'packet-manifest.json',
        sent_date=sent_date,
        response_due_date=response_due_date,
        service_label=service_label,
        owner_role=owner_role,
        source_record_set=source_record_set,
        date_range=date_range,
        send_channel_class='email',
        owner_route_class='accountable-owner',
        operator_confirmation=SEND_LOG_CONFIRMATION,
        overwrite=True,
    )
    if not send_log.get('ok'):
        raise RuntimeError(f'contact-status source send-log did not build: {send_log}')
    status = build_status(
        output_dir=output_path.parent,
        status='sent-awaiting-reply',
        service_label=service_label,
        owner_role=owner_role,
        source_record_set=source_record_set,
        date_range=date_range,
        sent_date=sent_date,
        response_due_date=response_due_date,
        status_date=status_date,
        attempt_count=attempt_count,
        operator_confirmation=OPERATOR_CONFIRMATIONS['sent-awaiting-reply'],
        source_artifact=rel_to_root(send_dir / 'send-log.json', root=root),
        overwrite=True,
    )
    if not status.get('ok'):
        raise RuntimeError(f'contact-status fixture did not build: {status}')
    return output_path
