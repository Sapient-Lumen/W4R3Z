#!/usr/bin/env python3
"""Stage an outbound external-contact send trace into a public shell.

The tool is intentionally conservative: raw sent-message exports, SMTP logs,
provider receipts, and screenshots must remain outside the release tree. The
public output is a hash/size/MIME shell with header-presence booleans and no
raw transport bytes. It is not dispatch, not proof by itself, and not a
response-clock trigger.
"""
import argparse
import hashlib
import json
import mimetypes
from email import policy
from email.parser import BytesParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
DEFAULT_OUTPUT = ROOT / "examples" / f"external-contact-send-trace-shell-{REV}-no-transport.json"


def is_inside_root(path: Path) -> bool:
    try:
        path.resolve().relative_to(ROOT.resolve())
        return True
    except ValueError:
        return False


def load_current() -> dict:
    return json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8"))


def parse_headers(raw: bytes) -> dict:
    try:
        msg = BytesParser(policy=policy.default).parsebytes(raw)
    except Exception:
        return {
            "rfc5322_parse_attempted": True,
            "message_id_present": False,
            "date_header_present": False,
            "from_header_present": False,
            "to_header_present": False,
            "subject_present": False,
            "received_or_provider_trace_present": False,
            "authentication_results_present": False,
            "dkim_or_dmarc_result_present": False,
            "message_id_observed": None,
        }
    auth = bool(msg.get("Authentication-Results"))
    dkim_dmarc = bool(msg.get("DKIM-Signature") or (msg.get("Authentication-Results") and "dmarc" in str(msg.get("Authentication-Results")).lower()))
    return {
        "rfc5322_parse_attempted": True,
        "message_id_present": bool(msg.get("Message-ID")),
        "date_header_present": bool(msg.get("Date")),
        "from_header_present": bool(msg.get("From")),
        "to_header_present": bool(msg.get("To")),
        "subject_present": bool(msg.get("Subject")),
        "received_or_provider_trace_present": bool(msg.get_all("Received") or msg.get("X-Provider-Trace") or msg.get("X-Google-Smtp-Source")),
        "authentication_results_present": auth,
        "dkim_or_dmarc_result_present": dkim_dmarc,
        "message_id_observed": str(msg.get("Message-ID")).strip() if msg.get("Message-ID") else None,
    }


def build_shell(raw_path: Path, private_locator: str, trace_format: str, source_locator: str | None) -> dict:
    if is_inside_root(raw_path):
        raise SystemExit("raw send trace must be outside the public release tree")
    raw = raw_path.read_bytes()
    header_state = parse_headers(raw)
    mime = mimetypes.guess_type(raw_path.name)[0] or "application/octet-stream"
    shell = load_current()
    shell["send_trace_state"] = "transport-candidate-staged"
    shell["candidate_trace"].update({
        "raw_trace_present_now": True,
        "source_locator": source_locator,
        "private_trace_locator": private_locator,
        "raw_trace_sha256": hashlib.sha256(raw).hexdigest(),
        "size_bytes": len(raw),
        "mime_type": mime,
        "trace_format": trace_format,
        "message_id_observed": header_state.pop("message_id_observed"),
        "transport_proof_present_now": False
    })
    shell["message_header_checks"].update(header_state)
    shell["public_shell_policy"]["shell_created_now"] = True
    shell["public_summary"] = (
        "A candidate outbound send trace was staged into a public hash shell. "
        "This shell still does not by itself mark the request as sent, start a response clock, "
        "create custody, create a failed-gate shell, or move the live floor until the send-proof "
        "record and downstream audits verify authorization, sent_at, private trace retention, and deadline binding."
    )
    return shell


def check_current() -> None:
    shell = load_current()
    if shell.get("revision") != REV:
        raise SystemExit("send-trace shell revision mismatch")
    if shell.get("send_trace_state") != "pre-dispatch-no-transport":
        raise SystemExit("current send-trace shell must remain pre-dispatch/no-transport")
    if shell.get("candidate_trace", {}).get("raw_trace_present_now") is not False:
        raise SystemExit("current send-trace shell must not claim raw transport evidence")
    if shell.get("deadline_binding", {}).get("deadline_may_start_now") is not False:
        raise SystemExit("current send-trace shell must not start deadline/clock")
    if shell.get("downstream_locks", {}).get("may_treat_message_id_as_response_clock") is not False:
        raise SystemExit("current send-trace shell must reject Message-ID-as-clock")
    print("stage_external_contact_send_trace: OK")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-trace", help="Path to raw sent-message/provider trace outside release tree")
    parser.add_argument("--private-trace-locator", help="Private vault locator where raw trace is retained")
    parser.add_argument("--trace-format", choices=["raw-rfc822-sent-message", "provider-sent-export", "smtp-log-export", "signed-provider-receipt", "other"], default="raw-rfc822-sent-message")
    parser.add_argument("--source-locator")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--check-output", action="store_true")
    args = parser.parse_args()
    if args.check_output:
        check_current()
        return
    if not args.raw_trace or not args.private_trace_locator:
        raise SystemExit("--raw-trace and --private-trace-locator are required unless --check-output is used")
    out = Path(args.output)
    if not out.is_absolute():
        out = (ROOT / out).resolve()
    shell = build_shell(Path(args.raw_trace).resolve(), args.private_trace_locator, args.trace_format, args.source_locator)
    out.write_text(json.dumps(shell, indent=2) + "\n", encoding="utf-8")
    print(out.relative_to(ROOT) if is_inside_root(out) else out)


if __name__ == "__main__":
    main()
