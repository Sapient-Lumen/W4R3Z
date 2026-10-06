import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs/20-constitution/decay-watch-registry.md"
RECEIPT = ROOT / "REVISION-RECEIPT.json"
CONTEXT = ROOT / "context-pack.json"
ALLOWED_STATUSES = {"explicitly-overdue", "reviewed-current", "renewed", "demoted", "retired"}

def month_key(value: str) -> tuple[int, int]:
    m = re.match(r"(\d{4})-(\d{2})", value)
    if not m:
        raise SystemExit(f"invalid month horizon/date: {value}")
    return int(m.group(1)), int(m.group(2))


def month_ordinal(value: str) -> int:
    year, month = month_key(value)
    return year * 12 + month

receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
current_month = month_key(receipt["created_at"])
text = REGISTRY.read_text(encoding="utf-8")
blocks = re.split(r"(?=^- `DW-\d{4}`)", text, flags=re.M)
overdue = []
for block in blocks:
    m = re.match(r"- `(DW-\d{4})` — `([^`]+)`", block)
    if not m:
        continue
    dw_id = m.group(1)
    hm = re.search(r"^\s*- Review horizon:\s*(\d{4}-\d{2})", block, flags=re.M)
    if not hm:
        raise SystemExit(f"{dw_id} missing Review horizon")
    horizon = hm.group(1)
    sm = re.search(r"^\s*- Review status:\s*([^;\n]+)", block, flags=re.M)
    if month_key(horizon) < current_month:
        status = sm.group(1).strip() if sm else ""
        if status not in ALLOWED_STATUSES:
            raise SystemExit(f"{dw_id} horizon {horizon} is overdue relative to {receipt['created_at']} without allowed Review status")
        overdue_months = month_ordinal(receipt["created_at"]) - month_ordinal(horizon)
        if status == "explicitly-overdue" and overdue_months > 1:
            raise SystemExit(
                f"{dw_id} remained explicitly-overdue for {overdue_months} calendar months; "
                "review, renew, demote, or retire it instead of carrying an indefinite warning"
            )
        overdue.append(dw_id)
if CONTEXT.exists():
    context = json.loads(CONTEXT.read_text(encoding="utf-8"))
    surfaced = [entry.get("id") for entry in context.get("decay_watch_overdue", [])]
    missing = [dw_id for dw_id in overdue if dw_id not in surfaced]
    if missing:
        raise SystemExit("context-pack missing overdue decay-watch ids: " + ", ".join(missing))
print("check_decay_watch_horizon_freshness: OK")
