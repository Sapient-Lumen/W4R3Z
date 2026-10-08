#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from cdp_inspect import inspect_cdp


def main() -> None:
    parser = argparse.ArgumentParser(description='Inspect a Chromium remote-debugging port and report visible CDP targets.')
    parser.add_argument('--port', type=int, required=True)
    parser.add_argument('--extension-id')
    parser.add_argument('--timeout', type=float, default=1.0, help='Per-request HTTP timeout in seconds')
    parser.add_argument('--wait', type=float, default=5.0, help='How long to keep polling before giving up')
    parser.add_argument('--watch', type=float, default=0.0, help='After CDP becomes available, watch browser-level Target events for this many seconds')
    parser.add_argument('--attach', type=float, default=0.0, help='After CDP becomes available, auto-attach to browser-level page/service_worker targets for this many seconds')
    parser.add_argument('--pretty', action='store_true')
    args = parser.parse_args()

    report = inspect_cdp(port=args.port, extension_id=args.extension_id, timeout=args.timeout, wait=args.wait, watch=args.watch, attach=args.attach)
    print(json.dumps(report, indent=2 if args.pretty else None))
    raise SystemExit(0 if report.get('available') else 1)


if __name__ == '__main__':
    main()
