"""Build the rev0369 custody-hardened Priority-0 external replay handoff bundles."""
from pathlib import Path
import zipfile

from priority_zero_handoff_bundle_lib import build_responder_bundle, file_sha256

ROOT = Path(__file__).resolve().parents[1]
RESPONDER_BUNDLE = "handoffs/priority-zero-custody-hardened-external-replay-responder-bundle-2026-06-16.zip"
SUBMISSION_KIT = "handoffs/priority-zero-custody-hardened-external-replay-submission-kit-2026-06-16.zip"
RESPONDER_MEMBERS = ["assays/priority-zero-custody-hardened-external-replay-responder-only-2026-06-16.json", "assays/priority-zero-custody-hardened-external-replay-response-template-2026-06-16.json", "handoffs/priority-zero-custody-hardened-external-replay-responder-readme-2026-06-16.md"]
SUBMISSION_MEMBERS = ["handoffs/priority-zero-custody-hardened-external-replay-responder-bundle-2026-06-16.zip", "assays/priority-zero-clean-external-response-evidence-record-template-2026-06-16.json", "handoffs/priority-zero-clean-response-custody-readme-2026-06-16.md"]
FORBIDDEN = ["answer_key", "scorer-intake", "assays/priority-zero-custody-hardened-external-replay-scorer-intake-2026-06-16.json"]


def build_submission_kit() -> str:
    kit_path = ROOT / SUBMISSION_KIT
    kit_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(kit_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for rel in SUBMISSION_MEMBERS:
            path = ROOT / rel
            if not path.exists():
                raise SystemExit(f"missing submission kit member: {rel}")
            info = zipfile.ZipInfo(rel, date_time=(2026, 6, 16, 4, 44, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            zf.writestr(info, path.read_bytes())
    return file_sha256(ROOT, SUBMISSION_KIT)


def main() -> None:
    responder_sha = build_responder_bundle(root=ROOT, bundle_rel=RESPONDER_BUNDLE, members=RESPONDER_MEMBERS, date_time=(2026, 6, 16, 4, 44, 0), forbidden_tokens=FORBIDDEN)
    kit_sha = build_submission_kit()
    print(f"{RESPONDER_BUNDLE} {responder_sha}")
    print(f"{SUBMISSION_KIT} {kit_sha}")


if __name__ == "__main__":
    main()
