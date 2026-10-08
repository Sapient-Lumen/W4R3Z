#!/usr/bin/env python3
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
df=pd.read_csv(ROOT/'cube/nuclear-emergency-bvps-safe-statement-lint-result-rev0359.csv')
assert len(df)==54
assert (df.auto_closure=='no').all()
assert (df.validator_status=='pass').all()
print('validated',len(df))
