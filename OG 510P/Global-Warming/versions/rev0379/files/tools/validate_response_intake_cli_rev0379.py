from pathlib import Path
import subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
script=ROOT/'tools/bvps_response_intake_rev0379.py'
if not script.exists():
    raise SystemExit('missing response intake CLI')
res=subprocess.run([sys.executable, str(script), '--self-test'], cwd=str(ROOT), text=True, capture_output=True)
if res.returncode:
    raise SystemExit(res.stderr or res.stdout)
print('PASS response intake CLI self-test')
