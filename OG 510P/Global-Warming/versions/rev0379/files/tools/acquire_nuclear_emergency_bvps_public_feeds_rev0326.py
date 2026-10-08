#!/usr/bin/env python3
"""Dry-run or live acquisition harness for public NRC/FEMA feeds used by BVPS emergency-preparedness cube.

By default this runs in --dry-run mode and writes the exact URLs/filters that would be fetched.
Live network fetching is intentionally explicit and allowlisted. Public feed records are context only;
this tool never emits local readiness closure.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, time, urllib.parse, urllib.request
from pathlib import Path

ALLOWLIST = ('www.fema.gov','gis.fema.gov','www.nrc.gov')

def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def read_rows(path):
    with Path(path).open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def write_rows(path, rows, fields):
    with Path(path).open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); [w.writerow({k:r.get(k,'') for k in fields}) for r in rows]

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--contract', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--raw-dir', default='quarantine/public-feed-raw-rev0326')
    ap.add_argument('--live', action='store_true')
    ap.add_argument('--timeout', type=int, default=30)
    args = ap.parse_args(argv)
    rows=[]
    raw_dir=Path(args.raw_dir); raw_dir.mkdir(parents=True, exist_ok=True)
    for row in read_rows(args.contract):
        url=row['endpoint_url']
        host=urllib.parse.urlparse(url).netloc
        allowed=host in ALLOWLIST
        status='dry_run_not_fetched'
        http_status=''
        raw_path=''
        raw_sha=''
        err=''
        if args.live:
            if not allowed:
                status='blocked_non_allowlisted_host'
            else:
                try:
                    req=urllib.request.Request(url, headers={'User-Agent':'datacube-rev0326-feed-acquisition/1.0'})
                    with urllib.request.urlopen(req, timeout=args.timeout) as resp:
                        b=resp.read()
                        http_status=str(resp.status)
                    raw_sha=sha_bytes(b)
                    raw_path=str(raw_dir/(row['feed_id']+'-'+raw_sha[:12]+'.raw'))
                    Path(raw_path).write_bytes(b)
                    status='fetched_context_only'
                    time.sleep(0.2)
                except Exception as e:
                    status='fetch_failed_hold_no_upgrade'
                    err=str(e)
        rows.append({
            'feed_id':row['feed_id'],'feed_name':row['feed_name'],'endpoint_url':url,'host':host,
            'allowlisted':str(allowed).lower(),'run_mode':'live' if args.live else 'dry_run',
            'fetch_status':status,'http_status':http_status,'raw_artifact_path':raw_path,'raw_sha256':raw_sha,
            'closure_effect':'no_auto_closure','error':err
        })
    fields=['feed_id','feed_name','endpoint_url','host','allowlisted','run_mode','fetch_status','http_status','raw_artifact_path','raw_sha256','closure_effect','error']
    write_rows(args.output, rows, fields)
    return 0
if __name__=='__main__':
    raise SystemExit(main())
