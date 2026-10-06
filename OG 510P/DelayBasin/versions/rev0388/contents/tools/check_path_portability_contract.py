import pathlib

from release_hygiene_lib import iter_release_paths

ROOT = pathlib.Path(__file__).resolve().parents[1]
MAX_RELATIVE_PATH = 180
MAX_COMPONENT = 170
WARN_RELATIVE_PATH = 160
WARN_COMPONENT = 150

failures = []
warnings = []
for path in iter_release_paths(ROOT):
    rel = path.relative_to(ROOT).as_posix()
    if len(rel) > MAX_RELATIVE_PATH:
        failures.append(f"relative path too long ({len(rel)}>{MAX_RELATIVE_PATH}): {rel}")
    elif len(rel) > WARN_RELATIVE_PATH:
        warnings.append(rel)
    for part in path.relative_to(ROOT).parts:
        if len(part) > MAX_COMPONENT:
            failures.append(f"component too long ({len(part)}>{MAX_COMPONENT}): {rel} :: {part}")
        elif len(part) > WARN_COMPONENT:
            warnings.append(rel)
if failures:
    raise SystemExit("path portability failures:\n" + "\n".join(failures[:20]))
print(f"check_path_portability_contract: OK ({len(set(warnings))} advisory long paths/components below fail threshold)")
