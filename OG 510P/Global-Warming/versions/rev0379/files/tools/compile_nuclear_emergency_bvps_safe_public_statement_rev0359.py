#!/usr/bin/env python3
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
segments=pd.read_csv(ROOT/'cube/nuclear-emergency-bvps-safe-statement-compiler-output-rev0359.csv')
out=ROOT/'field-kits/bvps-rev0359/public-status-draft.md'
lines=['# Public-safe status draft — rev0359','']
for _,r in segments.iterrows():
    if str(r.compiler_decision).startswith('approved'):
        lines += [str(r.statement_text),'']
out.write_text('\n'.join(lines),encoding='utf-8')
print(out)
