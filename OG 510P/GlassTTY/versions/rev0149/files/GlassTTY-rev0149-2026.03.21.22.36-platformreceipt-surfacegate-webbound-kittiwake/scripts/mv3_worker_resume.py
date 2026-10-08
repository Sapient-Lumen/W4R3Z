from pathlib import Path
import importlib.util

_script = Path(__file__).with_name('mv3-worker-resume.py')
_spec = importlib.util.spec_from_file_location('glasstty_mv3_worker_resume_script', _script)
_module = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_module)

main = _module.main
