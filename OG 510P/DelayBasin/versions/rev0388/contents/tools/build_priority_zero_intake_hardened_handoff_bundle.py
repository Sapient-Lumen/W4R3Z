
"""Build the deterministic intake-hardened Priority-0 responder handoff bundle."""
import hashlib
import json
import pathlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESP = 'assays/priority-zero-intake-hardened-external-replay-responder-only-2026-06-15.json'
TEMPLATE = 'assays/priority-zero-intake-hardened-external-replay-response-template-2026-06-15.json'
SCORER = 'assays/priority-zero-intake-hardened-external-replay-scorer-intake-2026-06-15.json'
ZIP_REL = 'handoffs/priority-zero-intake-hardened-external-replay-responder-bundle-2026-06-15.zip'
MANIFEST = 'handoffs/priority-zero-intake-hardened-external-replay-handoff-manifest-2026-06-15.json'
FORBIDDEN = ["answer_key", "true_variant", "expected_score", "scorecard", SCORER, "priority-zero-intake-hardened-external-replay-scorer-intake"]


def sha(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def assert_no_forbidden() -> None:
    for rel in [RESP, TEMPLATE]:
        text = (ROOT / rel).read_text(encoding="utf-8")
        for token in FORBIDDEN:
            if token in text:
                raise SystemExit(f"responder bundle input {rel} leaked forbidden token: {token}")


def build() -> None:
    assert_no_forbidden()
    zpath = ROOT / ZIP_REL
    zpath.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zpath, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for rel in [RESP, TEMPLATE]:
            info = zipfile.ZipInfo(rel, date_time=(2026, 6, 15, 19, 50, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            zf.writestr(info, (ROOT / rel).read_bytes())
    scorer = json.loads((ROOT / SCORER).read_text(encoding="utf-8"))
    scorer["responder_bundle_sha256"] = sha(ZIP_REL)
    (ROOT / SCORER).write_text(json.dumps(scorer, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    manifest = json.loads((ROOT / MANIFEST).read_text(encoding="utf-8"))
    manifest["responder_bundle_sha256"] = sha(ZIP_REL)
    for row in manifest.get("contains", []):
        row["sha256"] = sha(row["path"])
    for row in manifest.get("excluded_from_bundle", []):
        row["sha256"] = sha(row["path"])
    (ROOT / MANIFEST).write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{sha(ZIP_REL)}  {ZIP_REL}")


if __name__ == "__main__":
    build()
