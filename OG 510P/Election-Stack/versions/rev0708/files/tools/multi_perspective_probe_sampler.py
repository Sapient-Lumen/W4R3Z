#!/usr/bin/env python3
"""multi_perspective_probe_sampler.py

Skeleton for selecting diverse network perspectives (ASN/country) for validation.
"""
import random
import json
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: multi_perspective_probe_sampler.py <probes.json> [k]", file=sys.stderr)
        sys.exit(2)

    k=int(sys.argv[2]) if len(sys.argv) > 2 else 10
    probes=json.load(open(sys.argv[1],'r',encoding='utf-8'))

    # naive: sample distinct ASNs if possible
    by_asn={}
    for p in probes:
        asn=p.get('asn')
        by_asn.setdefault(asn, []).append(p)

    asns=[a for a in by_asn.keys() if a is not None]
    random.shuffle(asns)
    chosen=[]
    for a in asns:
        chosen.append(random.choice(by_asn[a]))
        if len(chosen) >= k:
            break

    print(json.dumps({"k":k,"chosen":chosen}, indent=2))

if __name__ == '__main__':
    main()
