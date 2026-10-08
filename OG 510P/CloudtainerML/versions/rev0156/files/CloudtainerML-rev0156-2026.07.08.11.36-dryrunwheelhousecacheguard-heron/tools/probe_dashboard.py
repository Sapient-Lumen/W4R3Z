#!/usr/bin/env python3
from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

ROOT = Path(__file__).resolve().parents[1]
PROBE_DIR = ROOT / 'artifacts' / 'probe-results'
DASH_DIR = ROOT / 'artifacts' / 'dashboard'

def revision() -> str:
    try:
        return json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8')).get('revision', 'rev0007')
    except Exception:
        return 'rev0007'

REVISION = revision()


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return None


def count_rows(payload: dict[str, Any]) -> int | None:
    for key in ['rows']:
        v = payload.get(key)
        if isinstance(v, list):
            return len(v)
        if isinstance(v, int):
            return v
    for key in ['summary', 'aggregate']:
        v = payload.get(key)
        if isinstance(v, dict) and isinstance(v.get('row_count'), int):
            return v['row_count']
        if isinstance(v, list):
            return len(v)
    return None


def top_level_keys(payload: dict[str, Any]) -> list[str]:
    return sorted(k for k in payload.keys() if k not in {'rows'})


def compact_summary(payload: dict[str, Any]) -> dict[str, Any]:
    for key in ['summary', 'aggregate', 'by_method']:
        if key in payload:
            v = payload[key]
            if isinstance(v, dict):
                return {'type': key, 'keys': list(v.keys())[:12]}
            if isinstance(v, list):
                return {'type': key, 'items': len(v), 'first': v[0] if v else None}
    return {'type': 'none'}


def build_dashboard() -> dict[str, Any]:
    probes: list[dict[str, Any]] = []
    for path in sorted(PROBE_DIR.glob('*.json')):
        payload = load_json(path)
        if payload is None:
            probes.append({'file': str(path.relative_to(ROOT)), 'parse_error': True})
            continue
        probe_name = payload.get('probe') or path.stem
        probes.append({
            'file': str(path.relative_to(ROOT)),
            'probe': probe_name,
            'rows': count_rows(payload),
            'csv': payload.get('csv'),
            'purpose': payload.get('purpose') or payload.get('note') or payload.get('interpretation'),
            'top_level_keys': top_level_keys(payload),
            'summary_shape': compact_summary(payload),
        })
    return {
        'project': 'CloudtainerML',
        'revision': REVISION,
        'probe_json_count': len(probes),
        'probes': probes,
    }


def write_markdown(dash: dict[str, Any], path: Path) -> None:
    lines = [f'# Probe dashboard — {REVISION}', '', f"Probe JSON files: **{dash['probe_json_count']}**", '']
    lines.append('| Probe | Rows | File | What it is for |')
    lines.append('|---|---:|---|---|')
    for p in dash['probes']:
        purpose = str(p.get('purpose') or '').replace('\n', ' ')[:170]
        lines.append(f"| {p.get('probe')} | {p.get('rows', '')} | `{p.get('file')}` | {purpose} |")
    lines.append('')
    lines.append('## Notes')
    lines.append('')
    lines.append('- This dashboard is intentionally shallow: it verifies that probe outputs are discoverable and comparable before deeper plotting exists.')
    lines.append('- Next refactor target: normalize metric names across probes so cross-probe charts can be generated automatically.')
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def write_html(dash: dict[str, Any], path: Path) -> None:
    rows = []
    for p in dash['probes']:
        rows.append('<tr>' + ''.join([
            f"<td>{html.escape(str(p.get('probe')))}</td>",
            f"<td>{html.escape(str(p.get('rows', '')))}</td>",
            f"<td><code>{html.escape(str(p.get('file')))}</code></td>",
            f"<td>{html.escape(str(p.get('purpose') or ''))}</td>",
        ]) + '</tr>')
    doc = f"""<!doctype html>
<html><head><meta charset='utf-8'><title>CloudtainerML {REVISION} probe dashboard</title>
<style>body{{font-family:system-ui,sans-serif;max-width:1100px;margin:2rem auto;line-height:1.4}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #bbb;padding:.4rem;vertical-align:top}}code{{font-size:.9em}}</style>
</head><body><h1>CloudtainerML {REVISION} probe dashboard</h1><p>Probe JSON files: <b>{dash['probe_json_count']}</b></p><table><thead><tr><th>Probe</th><th>Rows</th><th>File</th><th>Purpose</th></tr></thead><tbody>{''.join(rows)}</tbody></table></body></html>"""
    path.write_text(doc, encoding='utf-8')


def main() -> int:
    DASH_DIR.mkdir(parents=True, exist_ok=True)
    dash = build_dashboard()
    (DASH_DIR / 'PROBE-DASHBOARD.json').write_text(json.dumps(dash, indent=2), encoding='utf-8')
    write_markdown(dash, DASH_DIR / 'PROBE-DASHBOARD.md')
    write_html(dash, DASH_DIR / 'PROBE-DASHBOARD.html')
    print(json.dumps({'probe_json_count': dash['probe_json_count'], 'outdir': str(DASH_DIR.relative_to(ROOT))}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
