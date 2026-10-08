import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / 'examples' / 'dependency-graphs'
SCHEMA_PATH = ROOT / 'schemas' / 'artifact-dependency-graph.schema.json'
STATES = {'DG0','DG1','DG2','DG3','DG4','DGX'}
receipt = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8'))
ft_items = json.loads((ROOT / 'FOLLOWTHROUGH_QUEUE.json').read_text(encoding='utf-8'))['items']
ft_ids = {item['id'] for item in ft_items}
lint_tool_names = {Path(row['path']).name for row in json.loads((ROOT / 'CUBE_TOOLCHAIN_REGISTRY.json').read_text(encoding='utf-8'))['lint_order']}

def fail(errors, rel, msg): errors.append(f'{rel}: {msg}')
def parse_date(value, errors, rel, field):
    try: date.fromisoformat(value)
    except Exception: fail(errors, rel, f'{field} must be ISO date')

def validate(path: Path):
    rel=path.relative_to(ROOT).as_posix(); errors=[]
    data=json.loads(path.read_text(encoding='utf-8'))
    required=['graph_id','revision','graph_state','related_followthrough_ids','nodes','edges','required_terminal_paths','graph_limits','last_reviewed']
    for field in required:
        if field not in data or data[field] in ('', [], None): fail(errors, rel, f'missing or empty {field}')
    if errors: return errors
    if data['revision'] != receipt['revision']: fail(errors, rel, 'revision does not match receipt')
    if data['graph_state'] not in STATES: fail(errors, rel, 'graph_state invalid')
    if not data['graph_id'].startswith('DG-'): fail(errors, rel, 'graph_id must start DG-')
    parse_date(data['last_reviewed'], errors, rel, 'last_reviewed')
    for fid in data['related_followthrough_ids']:
        if fid not in ft_ids: fail(errors, rel, f'unknown followthrough id {fid}')
    ids=set(); validators=[]; records=[]
    for idx,node in enumerate(data['nodes']):
        for field in ['node_id','path','kind']:
            if field not in node: fail(errors, rel, f'nodes[{idx}].{field} missing')
        nid=node.get('node_id')
        if nid in ids: fail(errors, rel, f'duplicate node_id {nid}')
        ids.add(nid)
        npath=node.get('path','')
        if not (ROOT / npath).exists(): fail(errors, rel, f'node path missing {npath}')
        if node.get('kind') == 'validator':
            validators.append(nid)
            if Path(npath).name not in lint_tool_names: fail(errors, rel, f'validator not wired into lint {npath}')
        if node.get('kind') == 'record': records.append(nid)
    edge_targets=set(); edge_sources=set()
    for idx,edge in enumerate(data['edges']):
        for field in ['from','to','relationship']:
            if field not in edge: fail(errors, rel, f'edges[{idx}].{field} missing')
        if edge.get('from') not in ids: fail(errors, rel, f'edge from unknown {edge.get("from")}')
        if edge.get('to') not in ids: fail(errors, rel, f'edge to unknown {edge.get("to")}')
        edge_sources.add(edge.get('from')); edge_targets.add(edge.get('to'))
    for p in data['required_terminal_paths']:
        if not (ROOT / p).exists(): fail(errors, rel, f'required terminal path missing {p}')
    # Every record node except the graph itself should have a supporting incoming edge.
    for nid in records:
        if nid != 'dependency-graph' and nid not in edge_targets:
            fail(errors, rel, f'record node has no incoming dependency edge: {nid}')
    limits=' '.join(data.get('graph_limits', [])).lower()
    for phrase in ['not learning or service effectiveness evidence','does not close ft-0181','synthetic example']:
        if phrase not in limits: fail(errors, rel, f'graph_limits missing phrase: {phrase}')
    return errors

schema=json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
if schema.get('title') != 'AI-EDU artifact dependency graph': raise SystemExit('artifact dependency graph schema title mismatch')
paths=sorted(DIR.glob('*.json'))
if not paths: raise SystemExit('no artifact dependency graphs found')
all_errors=[]
for path in paths: all_errors.extend(validate(path))
if all_errors: raise SystemExit('artifact dependency graph validation errors:\n' + '\n'.join(all_errors))
print(f'check_artifact_dependency_graphs: OK ({len(paths)} graphs)')
