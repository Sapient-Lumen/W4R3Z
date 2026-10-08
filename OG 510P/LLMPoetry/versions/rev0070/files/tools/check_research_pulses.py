#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path

def main(root='.'):
    root=Path(root)
    checks=[]
    try:
        state=json.loads((root/'STATE.json').read_text())
        rev=state.get('revision')
        turn=state.get('turn',{}).get('last_completed')
        checks.append(('state_parse', True))
    except Exception as e:
        print(json.dumps({'ok':False,'checks':[{'name':'state_parse','ok':False,'detail':str(e)}]}, indent=2)); return 1
    try:
        ledger=json.loads((root/'registries/research_entropy_ledger.json').read_text())
        pulses=ledger.get('pulses',[])
        checks.append(('ledger_parse', isinstance(pulses,list)))
        checks.append(('ledger_revision_matches_state', ledger.get('revision')==rev))
    except Exception as e:
        print(json.dumps({'ok':False,'checks':[{'name':'ledger_parse','ok':False,'detail':str(e)}]}, indent=2)); return 1
    current=[p for p in pulses if p.get('revision')==rev and p.get('turn')==turn]
    checks.append(('current_revision_turn_pulse_present', len(current)>=1))
    try:
        src=json.loads((root/'registries/source_registry.json').read_text())
        source_ids={s.get('source_id') for s in src.get('sources',[])}
        checks.append(('source_registry_parse', True))
        missing=[]
        for p in current:
            for sid in p.get('source_ids',[]):
                if sid not in source_ids:
                    missing.append(sid)
        checks.append(('current_pulse_source_ids_registered', not missing))
    except Exception:
        checks.append(('source_registry_parse', False))
        checks.append(('current_pulse_source_ids_registered', False))
    try:
        index=json.loads((root/'registries/research_pulse_index.json').read_text())
        idx_pulses=index.get('pulses',[])
        ledger_ids=[p.get('pulse_id') for p in pulses]
        idx_ids=[p.get('pulse_id') for p in idx_pulses]
        checks.append(('pulse_index_parse', isinstance(idx_pulses,list)))
        checks.append(('pulse_index_revision_matches_state', index.get('revision')==rev))
        checks.append(('pulse_index_synchronized_with_ledger', idx_ids==ledger_ids))
        checks.append(('pulse_index_current_pulse_present', any(p.get('revision')==rev and p.get('turn')==turn for p in idx_pulses)))
    except Exception:
        checks.append(('pulse_index_parse', False))
    blocked=[p for p in current if p.get('blocked') or p.get('status')=='WEB-PULSE-BLOCKED']
    if blocked:
        checks.append(('blocked_pulse_has_reason', all(p.get('blocked_reason') or p.get('reason') for p in blocked)))
    else:
        checks.append(('current_pulse_not_blocked', True))
    ok=all(v for _,v in checks)
    print(json.dumps({'ok':ok,'revision':rev,'turn':turn,'checks':[{'name':n,'ok':bool(v)} for n,v in checks]}, indent=2))
    return 0 if ok else 1
if __name__=='__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv)>1 else '.'))
