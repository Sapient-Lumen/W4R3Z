import pathlib
import runpy

from validation_toolchain_lib import build_validation_toolchain

ROOT = pathlib.Path(__file__).resolve().parents[1]
tools = build_validation_toolchain(ROOT)

for tool in tools:
    print(f"== {tool} ==", flush=True)
    try:
        runpy.run_path(str(ROOT / "tools" / tool), run_name="__main__")
    except SystemExit as e:
        code = e.code if isinstance(e.code, int) else 1
        if code != 0:
            raise

print("run_lint_suite: OK")
