"""Build the rev0371 timeline-hardened Priority-0 responder/submission bundles."""
import hashlib, json, pathlib, zipfile
ROOT = pathlib.Path(__file__).resolve().parents[1]
RESPONDER = "assays/priority-zero-timeline-hardened-external-replay-responder-only-2026-06-16.json"
TEMPLATE = "assays/priority-zero-timeline-hardened-external-replay-response-template-2026-06-16.json"
README = "handoffs/priority-zero-timeline-hardened-external-replay-responder-readme-2026-06-16.md"
BUNDLE = "handoffs/priority-zero-timeline-hardened-external-replay-responder-bundle-2026-06-16.zip"
EVIDENCE_TEMPLATE = "assays/priority-zero-timeline-hardened-clean-external-response-evidence-record-template-2026-06-16.json"
CUSTODY_README = "handoffs/priority-zero-timeline-hardened-clean-response-custody-readme-2026-06-16.md"
SUBMISSION_KIT = "handoffs/priority-zero-timeline-hardened-external-replay-submission-kit-2026-06-16.zip"
MANIFEST = "handoffs/priority-zero-timeline-hardened-external-replay-handoff-manifest-2026-06-16.json"

def _sha(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()

def _write_zip(rel: str, members: list[str]) -> None:
    with zipfile.ZipFile(ROOT / rel, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for member in members:
            info = zipfile.ZipInfo(member)
            info.date_time = (1980, 1, 1, 0, 0, 0)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            zf.writestr(info, (ROOT / member).read_bytes())

def main() -> None:
    _write_zip(BUNDLE, [RESPONDER, TEMPLATE, README])
    _write_zip(SUBMISSION_KIT, [BUNDLE, EVIDENCE_TEMPLATE, CUSTODY_README])
    manifest = json.loads((ROOT / MANIFEST).read_text(encoding="utf-8"))
    manifest["responder_bundle_sha256"] = _sha(BUNDLE)
    manifest["submission_kit_sha256"] = _sha(SUBMISSION_KIT)
    manifest["responder_only_sha256"] = _sha(RESPONDER)
    manifest["response_template_sha256"] = _sha(TEMPLATE)
    manifest["evidence_record_template_sha256"] = _sha(EVIDENCE_TEMPLATE)
    manifest["scorer_intake_sha256"] = _sha("assays/priority-zero-timeline-hardened-external-replay-scorer-intake-2026-06-16.json")
    for row in manifest.get("excluded_from_responder_bundle", []):
        row["sha256"] = _sha(row["path"])
    (ROOT / MANIFEST).write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(BUNDLE, _sha(BUNDLE))
    print(SUBMISSION_KIT, _sha(SUBMISSION_KIT))

if __name__ == "__main__":
    main()
