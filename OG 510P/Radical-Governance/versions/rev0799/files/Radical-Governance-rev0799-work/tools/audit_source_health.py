#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

sys.dont_write_bytecode = True

from archive_meta import SOURCES_DIR


def fetch(url: str, *, timeout: float, use_head: bool) -> dict:
    method = "HEAD" if use_head else "GET"
    request = Request(url, method=method, headers={"User-Agent": "radical-governance-source-health-audit/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:
            return {
                "method": method,
                "ok": True,
                "status": getattr(response, "status", None),
                "final_url": response.geturl(),
                "content_type": response.headers.get("content-type"),
                "content_length": response.headers.get("content-length"),
            }
    except HTTPError as exc:
        return {"method": method, "ok": False, "status": exc.code, "error": str(exc), "final_url": getattr(exc, "url", url)}
    except URLError as exc:
        return {"method": method, "ok": False, "status": None, "error": str(exc.reason), "final_url": url}
    except TimeoutError as exc:
        return {"method": method, "ok": False, "status": None, "error": str(exc), "final_url": url}


def main() -> None:
    parser = argparse.ArgumentParser(description="Network-dependent source-key URL audit. Not used by offline make lint.")
    parser.add_argument("--source-key", action="append", default=[], help="Source key to audit; may be repeated.")
    parser.add_argument("--limit", type=int, default=25, help="Maximum number of source keys to audit when --source-key is omitted.")
    parser.add_argument("--timeout", type=float, default=10.0, help="Per-request timeout in seconds.")
    parser.add_argument("--get", action="store_true", help="Use GET instead of HEAD.")
    args = parser.parse_args()

    registry = json.loads((SOURCES_DIR / "source_keys.json").read_text(encoding="utf-8"))
    keys = registry.get("keys", {})
    selected = args.source_key or list(keys)[: max(args.limit, 0)]
    results = []
    for key in selected:
        entry = keys.get(key)
        if not entry:
            results.append({"source_key": key, "ok": False, "error": "unknown source_key"})
            continue
        result = fetch(entry.get("url", ""), timeout=args.timeout, use_head=not args.get)
        result.update({"source_key": key, "url": entry.get("url"), "title": entry.get("title"), "publisher": entry.get("publisher")})
        results.append(result)
    print(json.dumps({"audited_at_utc": datetime.now(timezone.utc).isoformat(), "count": len(results), "results": results}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
