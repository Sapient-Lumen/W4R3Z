#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import socket
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

def check_tcp(host: str, port: int, timeout_seconds: float) -> dict:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout_seconds)
    try:
        sock.connect((host, port))
    except Exception as exc:  # pragma: no cover - environment dependent
        return {"ok": False, "error": str(exc)}
    finally:
        sock.close()
    return {"ok": True}

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    config_path = (ROOT / args.config).resolve()
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))

    report = {
        "config": str(config_path.relative_to(ROOT)),
        "results": [],
    }

    for service in config.get("services", []):
        kind = service["kind"]
        result = {"name": service["name"], "kind": kind}
        if kind == "tcp":
            result.update(
                check_tcp(
                    host=service["host"],
                    port=int(service["port"]),
                    timeout_seconds=float(service.get("timeout_seconds", 1.0)),
                )
            )
        else:
            result.update({"ok": False, "error": f"unsupported kind: {kind}"})
        report["results"].append(result)

    artifacts_dir = ROOT / "artifacts"
    artifacts_dir.mkdir(exist_ok=True)
    out = artifacts_dir / "discovery-service-check.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(report, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
