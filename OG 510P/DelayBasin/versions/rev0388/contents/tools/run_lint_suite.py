import os
import pathlib
import subprocess
import sys

sys.dont_write_bytecode = True

from validation_toolchain_lib import build_validation_toolchain

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT / "tools"

# Every checker is executed in a fresh subprocess. This costs a little more wall
# time, but it keeps admission validation from inheriting module globals,
# bytecode/cache state, open temporary directories, or runpy side effects from a
# prior checker. Generated-surface drift is still the heaviest check, but it is
# no longer a special case whose state can poison the rest of the suite.


def _checker_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env.pop("PYTHONPATH", None)
    return env


def _run_tool(tool: str) -> tuple[bool, int, str, str]:
    result = subprocess.run(
        [sys.executable, "-S", str(TOOLS_DIR / tool)],
        cwd=ROOT,
        env=_checker_env(),
        text=True,
        capture_output=True,
    )
    return result.returncode == 0, result.returncode, result.stdout, result.stderr


def main() -> int:
    tools = build_validation_toolchain(ROOT)
    total = len(tools)
    for index, tool in enumerate(tools, start=1):
        print(f"== lint step {index}/{total}: {tool} ==", flush=True)
        ok, code, stdout, stderr = _run_tool(tool)
        if not ok:
            print(f"failed lint step {index}/{total}: {tool}", flush=True)
            if stdout:
                print(stdout, end="")
            if stderr:
                print(stderr, end="", file=sys.stderr)
            return code or 1
        if index == total or index % 25 == 0:
            print(f"== lint progress {index}/{total} ==", flush=True)
    print("run_lint_suite: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
