#!/usr/bin/env python3
"""UnreachabilityProof builder (skeleton).

Takes a JSON file containing:
{
  "target": {"type": "url", "identifier": "https://..."},
  "window": {"start": "...", "end": "..."},
  "probe_results": [...],
  "controls": [...]
}

Outputs a UnreachabilityProof object with placeholder hashes/signature.

Intentionally minimal: this tool does not fetch external platforms.
"""

import json
import sys
import uuid
from datetime import datetime, timezone


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def main(inp: str, outp: str) -> int:
    with open(inp, 'r', encoding='utf-8') as f:
        data = json.load(f)

    proof = {
        "schema_version": "1.0",
        "proof_id": str(uuid.uuid4()),
        "target": data["target"],
        "window": data["window"],
        "probe_results": data.get("probe_results", []),
        "controls": data.get("controls", []),
        "independence_claims": data.get("independence_claims"),
        "created_at": now_iso(),
        "created_by": data.get("created_by", "unknown"),
        "hashes": data.get("hashes", []),
        "notes": data.get("notes"),
        "signature": {
            "alg": "UNSIGNED",
            "sig": ""
        }
    }

    with open(outp, 'w', encoding='utf-8') as f:
        json.dump(proof, f, indent=2, sort_keys=True)
        f.write('\n')

    return 0


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: urp_builder_skeleton.py <input.json> <output_unreachability_proof.json>')
        sys.exit(1)
    sys.exit(main(sys.argv[1], sys.argv[2]))
